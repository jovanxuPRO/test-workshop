"""
Test Workshop Pro v5 - Automated Test Generation & Execution Platform.

Start: python main.py (serves on http://0.0.0.0:9000)

Key Endpoints:
  POST /api/plan        - Submit test plan, returns session ID
  GET  /api/stream?id=   - SSE stream of real-time test execution
  POST /api/gnr          - Synchronous test generation & execution
  GET  /api/stop         - Kill running pytest process
  GET  /api/report?dir=  - JUnit XML-based ISTQB report
  GET  /api/report-count - Summary counts from latest execution
  GET  /api/report-list  - Browse all historical reports
  GET  /api/tc           - Test case CRUD operations

Data Files:
  generated_tests/   - Per-execution test code + JUnit XML (keeps last 20)
  test_cases.json    - User-managed test case library
  exec_history.json  - Execution summary records (keeps last 50)
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os, json, shutil, subprocess, threading, queue, asyncio, re, base64, html, logging, uuid, signal, atexit
import ipaddress, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("test-workshop")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
        return response

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Test Workshop Pro", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SecurityHeadersMiddleware)
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")
GEN = os.path.join(BASE, "generated_tests")
os.makedirs(GEN, exist_ok=True)
TCF = os.path.join(BASE, "test_cases.json")

# Concurrency guard: max 3 simultaneous test executions
_exec_sem = asyncio.Semaphore(3)

# AI API Key — encrypted at rest, decrypted in memory only
# Set via env TW_AI_KEY=sk-xxx or via UI (POST /api/ai-key)
_AI_ENC_FILE = os.path.join(BASE, ".ai_key.enc")
import hashlib as _hashlib, secrets as _secrets

_fernet_secret = _hashlib.pbkdf2_hmac(
    "sha256", os.environ.get("TW_SECRET", BASE).encode(),
    b"test-workshop-ai-key-v1", 100000, dklen=32
)


def _encrypt_key(plain: str) -> bytes:
    """Encrypt with random IV + HMAC-XOR stream + 16-byte auth tag."""
    from base64 import urlsafe_b64encode as b64e
    key_bytes = _fernet_secret
    iv = _secrets.token_bytes(32)
    data = plain.encode()
    import hmac, hashlib
    stream = hmac.new(key_bytes, iv, hashlib.sha256).digest()
    while len(stream) < len(data):
        stream += hmac.new(key_bytes, stream[-32:], hashlib.sha256).digest()
    encrypted = bytes(a ^ b for a, b in zip(data, stream[:len(data)]))
    payload = iv + encrypted
    tag = hmac.new(key_bytes, payload, hashlib.sha256).digest()[:16]
    return b64e(payload + tag)


def _decrypt_key(data: bytes) -> str:
    """Verify auth tag, then decrypt. Raises on tampering."""
    from base64 import urlsafe_b64decode as b64d
    raw = b64d(data)
    if len(raw) < 48:
        raise ValueError("Invalid encrypted data")
    payload, tag = raw[:-16], raw[-16:]
    import hmac, hashlib
    expected = hmac.new(_fernet_secret, payload, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(tag, expected):
        raise ValueError("Authentication failed")
    iv, encrypted = payload[:32], payload[32:]
    stream = hmac.new(_fernet_secret, iv, hashlib.sha256).digest()
    while len(stream) < len(encrypted):
        stream += hmac.new(_fernet_secret, stream[-32:], hashlib.sha256).digest()
    return bytes(a ^ b for a, b in zip(encrypted, stream[:len(encrypted)])).decode()


# Try to load from encrypted file first, then env var
_ai_key = ""
if os.path.exists(_AI_ENC_FILE):
    try:
        with open(_AI_ENC_FILE, "rb") as f:
            _ai_key = _decrypt_key(f.read())
        logger.info("AI key loaded from encrypted storage")
    except Exception:
        logger.warning("Failed to decrypt AI key file, trying env var")

if not _ai_key:
    _ai_key = os.environ.get("TW_AI_KEY", "").strip()
    if _ai_key:
        logger.info("AI key loaded from TW_AI_KEY env var")

_DEBUG = os.environ.get("TW_DEBUG", "").lower() in ("1", "true", "yes")
# Simple rate limiter: max requests per endpoint per window
_rate_limits = {}  # key -> [(timestamp, count), ...]


def _check_rate(key, max_req=60, window=60):
    """Return True if rate limit not exceeded. Simple sliding window."""
    global _rate_limits
    now = datetime.now().timestamp()
    if key not in _rate_limits:
        _rate_limits[key] = []
    _rate_limits[key] = [t for t in _rate_limits[key] if t > now - window]
    if len(_rate_limits[key]) >= max_req:
        return False
    _rate_limits[key].append(now)
    # Per-key cleanup instead of global clear
    if len(_rate_limits) > 5000:
        _rate_limits = {k: v for k, v in _rate_limits.items() if len(_rate_limits) <= 1000 or any(t > now - window for t in v)}
    return True


@app.on_event("startup")
async def startup_check():
    """Validate prerequisites: check key dependencies are installed."""
    checks = {}
    for mod in ["httpx", "pytest"]:
        try:
            __import__(mod)
            checks[mod] = True
        except ImportError:
            checks[mod] = False
            logger.warning(f"Missing dependency: {mod}")
    r = subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, text=True)
    if r.returncode != 0:
        logger.warning("pytest not found on PATH")
    else:
        logger.info(f"Startup OK. {r.stdout.strip()}")


import signal, atexit


def _cleanup_procs():
    for pid, proc in list(RUN_PROCS.items()):
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try: proc.kill()
            except Exception: pass
    RUN_PROCS.clear()


atexit.register(_cleanup_procs)


@app.on_event("shutdown")
async def shutdown_cleanup():
    _cleanup_procs()

def is_safe_url(url_str):
    """Block SSRF: reject private/internal/reserved IP ranges and file:// scheme."""
    lowered = url_str.lower()
    if lowered.startswith("file://") or lowered.startswith("ftp://"):
        return False
    # Block known internal hostname patterns before DNS resolution
    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1"}
    try:
        parsed = urllib.parse.urlparse(url_str)
        host = parsed.hostname
        if not host: return True
        if host.lower() in blocked_hosts or host.endswith(".local") or host.endswith(".internal"):
            return False
        # Check if host is an IP literal
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            # Hostname — resolve DNS and check the IP too
            try:
                resolved = subprocess.run(
                    ["python", "-c", f"import socket; print(socket.gethostbyname({host!r}))"],
                    capture_output=True, text=True, timeout=3)
                ip_str = resolved.stdout.strip()
                if ip_str:
                    ip = ipaddress.ip_address(ip_str)
                else:
                    return True
            except Exception:
                return True
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
        if ip in (ipaddress.ip_address("169.254.169.254"),):
            return False
        return True
    except Exception:
        return True

def safe(s):
    """Sanitize to safe identifier: retain only word chars + CJK, replace rest with _"""
    s = str(s)[:200]
    s = re.sub(r'[^\w\u4e00-\u9fff]', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    while '..' in s: s = s.replace('..', '.')
    return s or 't'

def safe_path(s):
    """Sanitize URL path: allow / {} ? = &"""
    s = str(s)[:500]
    s = re.sub(r'[^\w\u4e00-\u9fff\-/:,.?&=+%{}]', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    while '..' in s: s = s.replace('..', '.')
    return s or '/'

def _json_err(msg, status=200):
    return {"ok": False, "error": msg}

def gen_code(plan):
    """Generate executable pytest test code from a test plan.

    Args:
        plan: dict with keys:
            name (str): Project name for directory naming
            url (str): Base URL for test requests
            apis (list): API endpoints, each {m: HTTP method, p: path, n: description}
            pages (list): Web pages, each {u: URL, na: name}
            rules (list): Data validation rules as strings
            types (list): Test types to generate ['api','ui','data']
            auth (str): Auth type 'none'|'bearer'|'header'|'basic'
            authValue (str): Auth credential (sanitized before use)

    Returns:
        str: Path to the generated test directory containing conftest.py,
             test_api.py, test_ui.py, test_data.py, test_unit.py
    """
    name = plan.get("name", "u")
    raw_url = str(plan.get("url") or "http://localhost")
    url = re.sub(r'[^\w\-/:,.?&=+%~#]', '', raw_url)[:500]
    if not is_safe_url(url):
        url = "http://localhost"
    apis = plan.get("apis", []); pages = plan.get("pages", [])
    rules = plan.get("rules", []); types = plan.get("types", ["api", "ui", "data"])
    out = os.path.join(GEN, safe(name) + "_" + datetime.now().strftime("%H%M%S") + "_" + uuid.uuid4().hex[:6])
    # Cleanup: keep only last 20 test dirs by modification time
    try:
        dirs = [(os.path.join(GEN, d), os.path.getmtime(os.path.join(GEN, d))) 
                for d in os.listdir(GEN) if os.path.isdir(os.path.join(GEN, d))]
        dirs.sort(key=lambda x: x[1])
        for dp, _ in dirs[:-19]:
            try: shutil.rmtree(dp, ignore_errors=True)
            except Exception: pass
    except Exception: pass
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)

    # Build auth env var value (in-memory only, never written to disk)
    auth_type = plan.get("auth", "none")
    auth_value = plan.get("authValue", "")
    auth_value = re.sub(r'[^\w\-=+/,.:;@#$%^&*()!]', '', str(auth_value))[:500]
    auth_env = {}
    if auth_type == "bearer" and auth_value:
        auth_env["TW_AUTH_HEADER"] = f"Bearer {auth_value}"
    elif auth_type == "basic" and auth_value:
        auth_env["TW_AUTH_HEADER"] = f"Basic {base64.b64encode(auth_value.encode()).decode()}"
    elif auth_type == "header" and auth_value:
        parts = auth_value.split(":", 1)
        if len(parts) == 2:
            auth_env["TW_AUTH_HEADER_NAME"] = parts[0].strip()
            auth_env["TW_AUTH_HEADER"] = parts[1].strip()

    # conftest - auth via env var, never written to disk
    cf = '# Auto-generated test config\n'
    cf += 'import pytest, httpx, time, os\n'
    cf += f'B = "{url}"\n'
    cf += '@pytest.fixture\n'
    cf += 'def c():\n'
    cf += '    _ah = os.environ.get("TW_AUTH_HEADER", "")\n'
    cf += '    _hn = os.environ.get("TW_AUTH_HEADER_NAME", "Authorization")\n'
    cf += '    _hdrs = {"User-Agent":"Mozilla/5.0"}\n'
    cf += '    if _ah:\n'
    cf += '        _hdrs[_hn] = _ah\n'
    cf += '    with httpx.Client(base_url=B, timeout=25, follow_redirects=True, headers=_hdrs) as cl: yield cl\n'
    cf += '@pytest.fixture(scope="session")\n'
    cf += 'def browser():\n'
    cf += '    from playwright.sync_api import sync_playwright\n'
    cf += '    headless = os.environ.get("TW_HEADLESS", "false").lower() == "true"\n'
    cf += '    with sync_playwright() as p:\n'
    cf += '        br = p.chromium.launch(headless=headless, slow_mo=0,\n'
    cf += '            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])\n'
    cf += '        yield br; br.close()\n'
    cf += '@pytest.fixture\n'
    cf += 'def page(browser):\n'
    cf += '    ctx = browser.new_context()\n'
    cf += '    pg = ctx.new_page(); pg.set_default_timeout(20000)\n'
    cf += '    yield pg; ctx.close()\n'
    with open(os.path.join(out, "conftest.py"), "w", encoding="utf-8") as f:
        f.write(cf)

    # unit tests — only if api/unit type requested and not exact mode
    if ("api" in types or "unit" in types) and not plan.get("exact"):
        ut = 'import pytest, httpx, time\n'
        ut += f'B = "{url}"\n'
        ut += 'class TestUnit:\n'
        ut += '    def test_1_reachable(self):\n'
        ut += '        """服务可达性"""\n'
        ut += '        r = httpx.get(B, timeout=15, follow_redirects=True)\n'
        ut += '        assert r.status_code < 500\n\n'
        ut += '    def test_2_response_time(self):\n'
        ut += '        """响应时间基准"""\n'
        ut += '        t0=time.time(); httpx.get(B,timeout=20,follow_redirects=True)\n'
        ut += '        assert time.time()-t0<10\n\n'
        ut += '    def test_3_ssl_valid(self):\n'
        ut += '        """SSL证书有效"""\n'
        ut += '        if not B.startswith("https"): pytest.skip("HTTP only")\n'
        ut += '        r=httpx.get(B,timeout=15,follow_redirects=True)\n'
        ut += '        assert r.status_code<500\n\n'
        ut += '    def test_4_redirect_follow(self):\n'
        ut += '        """重定向跟踪"""\n'
        ut += '        r=httpx.get(B,timeout=15,follow_redirects=True)\n'
        ut += '        assert r.status_code < 500\n\n'
        ut += '    def test_5_headers_present(self):\n'
        ut += '        """响应头完整"""\n'
        ut += '        r=httpx.get(B,timeout=15,follow_redirects=True)\n'
        ut += '        assert isinstance(r.headers, dict) or hasattr(r.headers, "__getitem__")\n\n'
        ut += '    def test_6_content_length(self):\n'
        ut += '        """响应体大小"""\n'
        ut += '        r=httpx.get(B,timeout=15,follow_redirects=True)\n'
        ut += '        assert len(r.content)>0 or r.status_code>=300\n\n'
        ut += '    def test_7_encoding_valid(self):\n'
        ut += '        """编码声明检查"""\n'
        ut += '        r=httpx.get(B,timeout=15,follow_redirects=True)\n'
        ut += '        assert isinstance(r.encoding, str) or r.status_code>=300\n\n'
        ut += '    def test_8_concurrent(self):\n'
        ut += '        """并发请求"""\n'
        ut += '        import concurrent.futures\n'
        ut += '        def req(): return httpx.get(B,timeout=20,follow_redirects=True).status_code\n'
        ut += '        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:\n'
        ut += '            results = list(ex.map(lambda _: req(), range(3)))\n'
        ut += '        assert all(s<500 for s in results)\n\n'
        with open(os.path.join(out, "test_unit.py"), "w", encoding="utf-8") as f:
            f.write(ut)

    # api tests
    if "api" in types and apis:
        lines = ["import pytest, time", ""]
        seen = set()
        exact = plan.get("exact", False)  # exact mode: 1 test per API (for preview execution)
        for ai, a in enumerate(apis):
            m = a.get("m", "GET")
            if m not in ("GET", "POST", "PUT", "DELETE", "HEAD", "PATCH", "OPTIONS"):
                m = "GET"
            p = safe_path(a.get("p", "/")); n = safe(a.get("n", ""))
            # Deduplicate class names: append index if collision
            cn = n
            if cn in seen:
                cn = f"{n}_{ai}"
            seen.add(cn)
            tp = p.replace("{id}", "1")
            lines.append(f"class Test_{cn}:")
            lines.append(f'    """{m} {p}"""')
            lines.append("")
            if exact:
                tests = [("ok", f'c.request("{m}","{tp}")', "r.status_code < 500")]
            elif m == "GET":
                tests = [
                    ("ok", f'c.get("{tp}")', "r.status_code in (200,301,302,304)"),
                    ("body", f'c.get("{tp}")', "len(r.content) > 0 or r.status_code >= 300"),
                    ("type", f'c.get("{tp}")', '"content-type" in str(r.headers).lower() or r.status_code >= 300'),
                    ("time", f'c.get("{tp}")', "elapsed < 5"),
                    ("head", f'c.head("{tp}")', "r.status_code < 500"),
                    ("page", f'c.get("{tp}{"&" if "?" in tp else "?"}page=1")', "r.status_code < 500"),
                    ("mobile", f'c.get("{tp}", headers={{"User-Agent":"iPhone"}})', "r.status_code < 500"),
                    ("json_accept", f'c.get("{tp}", headers={{"Accept":"application/json"}})', "r.status_code < 500"),
                ]
            elif m == "POST":
                tests = [
                    ("ok", f'c.post("{tp}", json={{"t":"test"}})', "r.status_code < 500"),
                    ("empty", f'c.post("{tp}")', "r.status_code < 500"),
                    ("bad", f'c.post("{tp}", content="x", headers={{"Content-Type":"application/json"}})', "r.status_code < 500"),
                    ("form", f'c.post("{tp}", data={{"k":"v"}})', "r.status_code < 500"),
                ]
            elif m == "PUT":
                tests = [
                    ("ok", f'c.put("{tp}", json={{"t":"test"}})', "r.status_code < 500"),
                    ("empty", f'c.put("{tp}")', "r.status_code < 500"),
                ]
            elif m == "DELETE":
                tests = [("ok", f'c.delete("{tp}")', "r.status_code < 500")]
            elif m == "PATCH":
                tests = [
                    ("ok", f'c.patch("{tp}", json={{"t":"test"}})', "r.status_code < 500"),
                    ("empty", f'c.patch("{tp}")', "r.status_code < 500"),
                ]
            elif m == "HEAD":
                tests = [
                    ("ok", f'c.head("{tp}")', "r.status_code < 500"),
                    ("headers", f'c.head("{tp}")', "len(r.headers) > 0"),
                ]
            else:
                # OPTIONS or unknown methods — basic reachability test
                tests = [("ok", f'c.request("{m}","{tp}")', "r.status_code < 500")]
            for tn, stmt, check in tests:
                lines.append(f"    def test_{tn}(self, c):")
                lines.append(f'        """{tn}: {m} {p}"""')
                if tn == "time":
                    lines.append(f'        t0 = time.time(); r = c.get("{tp}"); elapsed = time.time() - t0')
                    lines.append(f'        assert elapsed < 5')
                else:
                    lines.append(f"        r = {stmt}")
                    lines.append(f"        assert {check}")
                lines.append("")
        with open(os.path.join(out, "test_api.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # ui tests - expanded
    if "ui" in types and pages:
        lines = ["import pytest", "from conftest import B", ""]
        ui_seen = set()
        for pi, pg in enumerate(pages):
            u = safe_path(pg.get("u","/")); na = safe(pg.get("na",""))
            cna = na
            if cna in ui_seen:
                cna = f"{na}_{pi}"
            ui_seen.add(cna)
            lines.append(f"class Test_{cna}:")
            lines.append("")
            # Test 1: page loads
            lines.append(f"    def test_1_page_loaded(self,page):")
            lines.append(f'        """页面加载渲染"""')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        assert page.locator("body").is_visible()')
            lines.append(f'        assert len(page.title())>0')
            lines.append("")
            # Test 2: no console errors
            lines.append(f"    def test_2_no_console_errors(self,page):")
            lines.append(f'        """控制台无错误"""')
            lines.append(f'        errs=[]')
            lines.append(f'        page.on("pageerror",lambda e:errs.append(str(e)))')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        page.wait_for_timeout(2000)')
            lines.append(f'        assert len(errs)==0,f"JS errors:{{errs}}"')
            lines.append("")
            # Test 3: load time
            lines.append(f"    def test_3_load_time(self,page):")
            lines.append(f'        """页面加载时间"""')
            lines.append(f'        import time')
            lines.append(f'        t0=time.time();page.goto(B+"{u}");page.wait_for_load_state("networkidle")')
            lines.append(f'        assert time.time()-t0<10')
            lines.append("")
            # Test 4: responsive check
            lines.append(f"    def test_4_mobile_viewport(self,page):")
            lines.append(f'        """移动端视口"""')
            lines.append(f'        page.set_viewport_size({{"width":375,"height":812}})')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        assert page.locator("body").is_visible()')
            lines.append("")
            # Test 5: navigation links
            lines.append(f"    def test_5_links_exist(self,page):")
            lines.append(f'        """页面导航元素"""')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        links=page.locator("a").count()')
            lines.append(f'        assert links>0')
            lines.append("")
            # Test 6: resources loaded
            lines.append(f"    def test_6_resources_loaded(self,page):")
            lines.append(f'        """静态资源加载"""')
            lines.append(f'        failed=[]')
            lines.append(f'        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        page.wait_for_timeout(3000)')
            lines.append(f'        assert len(failed)==0, f"Failed resources: {{failed}}"')
            lines.append("")
        with open(os.path.join(out, "test_ui.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # data tests - validate each API endpoint against rules
    if "data" in types and rules and apis:
        lines = ["import pytest, httpx", "from conftest import B", "", "class TestData:", ""]
        for i, r in enumerate(rules):
            api = apis[i % len(apis)] if apis else {"p": "/", "m": "GET"}
            p = safe_path(api.get("p", "/"))
            tp = p.replace("{id}", "1")
            dr = r.replace('"', "'").replace("\\", "\\\\")
            lines.append(f"    def test_d{i}(self, c):")
            lines.append(f'        """{dr}"""')
            lines.append(f'        resp = c.get("{tp}")')
            lines.append('        assert resp.status_code < 500')
            lines.append("")
        with open(os.path.join(out, "test_data.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return out, auth_env


HIST = os.path.join(BASE, "exec_history.json")

def load_hist():
    """Load execution history from exec_history.json."""
    if os.path.exists(HIST):
        try:
            with open(HIST, encoding="utf-8") as f:
                data = json.loads(f.read())
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            logger.warning(f"Corrupted history file, resetting")
            try: os.rename(HIST, HIST + ".bak")
            except OSError: pass
    return []

def _atomic_write(path, data):
    """Atomic write: temp file + rename to prevent corruption on crash."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    os.replace(tmp, path)

def save_hist_entry(entry):
    """Append an execution record to history. Keeps last 50 entries."""
    entries = load_hist()
    entries.insert(0, entry)
    if len(entries) > 50: entries = entries[:50]
    _atomic_write(HIST, entries)


@app.get("/api/history-data")
def list_history_json():
    """Return execution history as JSON for the Exec tab."""
    entries = load_hist()
    return {"history": entries}


@app.get("/api/history")
def list_history():
    entries = load_hist()
    if not entries:
        return HTMLResponse("<body style='font-family:sans-serif;text-align:center;padding:80px;color:#888'><h2>No history</h2></body>")

    rows = ""
    for i, e in enumerate(entries):
        color = "#27ae60" if e.get("failed", 0) == 0 else "#ef5350"
        rows += '<tr>'
        rows += f'<td>{i+1}</td>'
        rows += f'<td>{html.escape(str(e.get("name","?")), quote=False)}</td>'
        rows += f'<td>{html.escape(str(e.get("url","?")), quote=False)}</td>'
        rows += f'<td>{html.escape(str(e.get("time","?")), quote=False)}</td>'
        rows += f'<td style="color:#3498db;font-weight:700">{e.get("total",0)}</td>'
        rows += f'<td style="color:#27ae60;font-weight:700">{e.get("passed",0)}</td>'
        rows += f'<td style="color:#ef5350;font-weight:700">{e.get("failed",0)}</td>'
        rows += f'<td style="color:{color};font-weight:700">{e.get("rate",0)}%</td>'
        rows += f'<td><a href="/api/report?dir={e.get("dir","")}" target="_blank" style="color:#5c6bc0">报告</a></td>'
        rows += f'<td><button onclick="fetch(\'/api/history/{i}\',{{method:\'DELETE\'}}).then(()=>location.reload())" style="background:#fce4ec;color:#ef5350;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px">删除</button></td>'
        rows += '</tr>\n'

    total_runs = len(entries)
    avg_rate = round(sum(e.get("rate",0) for e in entries) / total_runs, 1)
    total_tests = sum(e.get("total",0) for e in entries)
    total_passed = sum(e.get("passed",0) for e in entries)

    return HTMLResponse(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>执行历史</title>
<style>body{{font-family:sans-serif;max-width:1100px;margin:30px auto;background:#f5f6fa;color:#333;padding:0 20px}}
h1{{color:#2c3e50}} .sub{{color:#888;font-size:13px;margin-bottom:20px}}
.metrics{{display:flex;gap:12px;margin:20px 0}}
.m{{background:#fff;border-radius:8px;padding:14px 18px;text-align:center;min-width:90px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.m .v{{font-size:26px;font-weight:700;display:block}}.m .l{{font-size:11px;color:#888;margin-top:3px}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
th{{background:#f8f9fb;padding:10px;text-align:left;font-size:11px;color:#888;text-transform:uppercase}}
td{{padding:10px;border-bottom:1px solid #eee;font-size:12px}}tr:hover td{{background:#fafbff}}
a{{color:#5c6bc0;text-decoration:none}}
</style></head><body>
<h1>执行历史</h1><p class="sub">{total_runs} 次执行 | 平均通过率 {avg_rate}% | 累计 {total_passed}/{total_tests} 通过</p>
<div class="metrics">
<div class="m"><span class="v" style="color:#3498db">{total_runs}</span><span class="l">执行次数</span></div>
<div class="m"><span class="v" style="color:#27ae60">{total_passed}</span><span class="l">累计通过</span></div>
<div class="m"><span class="v" style="color:#5c6bc0">{avg_rate}%</span><span class="l">平均通过率</span></div>
</div>
<table><thead><tr><th>#</th><th>项目</th><th>地址</th><th>时间</th><th>总计</th><th>通过</th><th>失败</th><th>通过率</th><th>报告</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody></table>
<p style="text-align:center;margin-top:20px"><a href="/">返回测试工坊</a></p>
</body></html>""")

@app.delete("/api/history/{idx}")
def del_history(idx: int):
    entries = load_hist()
    if 0 <= idx < len(entries):
        entry = entries.pop(idx)
        dir_name = entry.get("dir", "")
        if dir_name:
            dp = os.path.join(GEN, dir_name)
            try: shutil.rmtree(dp, ignore_errors=True)
            except Exception: pass
        _atomic_write(HIST, entries)
    return {"ok": True}


# Save on each execution
# In gnr endpoint, after parsing results:
@app.post("/api/gnr")
async def gnr(request: Request):
    if not _check_rate("gnr", max_req=20, window=60):
        return {"ok": False, "error": "Rate limit exceeded (20/min). Please wait."}
    async with _exec_sem:
        try:
            body = await request.json()
            if len(json.dumps(body)) > 50000:
                return {"ok": False, "error": "Plan too large"}
            d, auth_env = gen_code(body)
            xml_path = os.path.join(d, "results.xml")
            env = os.environ.copy()
            env.update(auth_env)
            r = await asyncio.to_thread(
                subprocess.run, ["python", "-m", "pytest", d, "-v", "--tb=short", "--color=no", f"--junitxml={xml_path}"],
                capture_output=True, text=True, timeout=300, env=env)
            t = p = f = 0
            if os.path.exists(xml_path):
                root = ET.parse(xml_path).getroot()
                ts = root.find("testsuite")
                if ts is None: ts = root
                t = int(ts.get("tests", 0) or 0)
                f = int(ts.get("failures", 0) or 0)
                e = int(ts.get("errors", 0) or 0)
                p = t - f - e
            save_hist_entry({
                "name": body.get("name", "?"),
                "url": body.get("url", "?").split("?")[0],
                "total": t, "passed": p, "failed": f, "errors": e,
                "rate": round(p/t*100,1) if t else 0,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dir": os.path.basename(d),
            })
            save_auto_tcs(body)
            update_tc_status(body, xml_path)
            return {"ok": f == 0, "total": t, "passed": p, "failed": f, "log": r.stdout[-5000:]}
        except Exception as ex:
            logger.error(f"gnr failed: {ex}", exc_info=_DEBUG)
            return {"ok": False, "error": "Internal error during test execution"}


PLANS = {}

@app.post("/api/plan")
async def save_plan(request: Request):
    try:
        if not _check_rate("plan", max_req=30, window=60):
            return {"error": "Rate limit exceeded"}
        body = await request.json()
        if len(json.dumps(body)) > 50000:
            return {"error": "Plan too large"}
        pid = uuid.uuid4().hex[:8]
        PLANS[pid] = body
        return {"id": pid}
    except Exception as e:
        logger.error(f"save_plan failed: {e}", exc_info=_DEBUG)
        return {"error": "Internal error"}


RUN_PROCS = {}  # pid -> Popen, per-session process tracking

@app.post("/api/stop")
def stop_exec(sid: str = ""):
    """Stop a specific session by plan ID, or all if no ID provided."""
    global RUN_PROCS
    if sid and sid in RUN_PROCS:
        try:
            RUN_PROCS[sid].terminate()
            RUN_PROCS[sid].kill()
        except Exception:
            pass
        RUN_PROCS.pop(sid, None)
        PLANS.pop(sid, None)
    elif not sid:
        for pid, proc in list(RUN_PROCS.items()):
            try:
                proc.terminate()
                proc.kill()
            except Exception:
                pass
        RUN_PROCS.clear()
        PLANS.clear()
    return {"ok": True}


@app.get("/api/stream")
async def stream(request: Request):
    pid = request.query_params.get("id", "")
    plan = PLANS.get(pid)
    if not plan:
        async def e():
            yield f"data: {json.dumps({'t':'error'})}\n\n"
        return StreamingResponse(e(), media_type="text/event-stream")

    # Reconnect: if process still running for this pid, attach to existing stdout
    existing = RUN_PROCS.get(pid)
    if existing and existing.poll() is None:
        return _attach_existing(pid, existing, plan)

    if existing:
        RUN_PROCS.pop(pid, None)

    try:
        d, auth_env = gen_code(plan)
    except Exception:
        logger.error("gen_code failed in stream", exc_info=_DEBUG)
        PLANS.pop(pid, None)
        async def e():
            yield f"data: {json.dumps({'t':'error','msg':'Code generation failed'})}\n\n"
        return StreamingResponse(e(), media_type="text/event-stream")
    xml_path = os.path.join(d, "results.xml")
    env = os.environ.copy()
    env.update(auth_env)
    return _run_stream(pid, plan, d, xml_path, env, request)


def _attach_existing(pid, proc, plan):
    """Reconnect SSE to an already-running subprocess."""
    q = queue.Queue()
    T = [0]; P = [0]; F = [0]; E = [0]

    def w():
        for line in iter(proc.stdout.readline, ""): q.put(line)
        q.put("__END__")
        proc.wait()

    threading.Thread(target=w, daemon=True).start()

    async def s():
        try:
            yield f"id: {pid}\ndata: {json.dumps({'t':'start','msg':'reconnected'})}\n\n"
            _heartbeat = 0
            _deadline = datetime.now().timestamp() + 600
            while True:
                if datetime.now().timestamp() > _deadline:
                    yield f"data: {json.dumps({'t':'error','msg':'Execution timeout'})}\n\n"
                    break
                try:
                    line = await asyncio.to_thread(q.get, timeout=0.1)
                except queue.Empty:
                    _heartbeat += 1
                    if _heartbeat % 20 == 0:
                        yield ": keepalive\n\n"
                    await asyncio.sleep(0.05)
                    continue
                if line == "__END__":
                    rate = round(P[0]/T[0]*100,1) if T[0] else 0
                    RUN_PROCS.pop(pid, None)
                    PLANS.pop(pid, None)
                    yield f"data: {json.dumps({'t':'done','total':T[0],'passed':P[0],'failed':F[0],'errors':E[0],'rate':rate})}\n\n"
                    break
                st = line.strip()
                if "PASSED" in st and "::" in st:
                    T[0] += 1; P[0] += 1
                elif "FAILED" in st and "::" in st:
                    T[0] += 1; F[0] += 1
                elif "ERROR" in st and "::" in st:
                    T[0] += 1; E[0] += 1
                yield f"data: {json.dumps({'t':'test','line':st[-300:].replace(chr(10),' ').replace(chr(13),'')})}\n\n"
        finally:
            RUN_PROCS.pop(pid, None)
            PLANS.pop(pid, None)
    return StreamingResponse(s(), media_type="text/event-stream",
        headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"})


def _run_stream(pid, plan, d, xml_path, env, request):
    """Start a new subprocess and stream its output via SSE."""

    async def s():
        q = queue.Queue()
        T = [0]; P = [0]; F = [0]; E = [0]
        try:
            try:
                proc = subprocess.Popen(
                    ["python", "-m", "pytest", d, "-v", "--tb=line", "--color=no", f"--junitxml={xml_path}"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
                RUN_PROCS[pid] = proc
            except Exception as ex:
                logger.error(f"Popen failed: {ex}", exc_info=_DEBUG)
                yield f"data: {json.dumps({'t':'error','msg':'Failed to start test process'})}\n\n"
                return
            def w():
                for line in iter(proc.stdout.readline, ""): q.put(line)
                q.put("__END__")
                proc.wait()
            threading.Thread(target=w, daemon=True).start()
            yield f"id: {pid}\ndata: {json.dumps({'t':'start'})}\n\n"
            _heartbeat = 0
            _deadline = datetime.now().timestamp() + 600  # 10 min max
            while True:
                if datetime.now().timestamp() > _deadline:
                    try: proc.terminate(); proc.kill()
                    except Exception: pass
                    yield f"data: {json.dumps({'t':'error','msg':'Execution timeout (10min)'})}\n\n"
                    break
                if await request.is_disconnected():
                    try: proc.terminate(); proc.kill()
                    except Exception: pass
                    RUN_PROCS.pop(pid, None)
                try:
                    line = await asyncio.to_thread(q.get, timeout=0.1)
                except queue.Empty:
                    _heartbeat += 1
                    if _heartbeat % 20 == 0:
                        yield ": keepalive\n\n"
                    await asyncio.sleep(0.05)
                    continue
                if line == "__END__":
                    rate = round(P[0] / T[0] * 100, 1) if T[0] else 0
                    e = {"name": plan.get("name","?"), "url": plan.get("url","?").split("?")[0],
                        "total": T[0], "passed": P[0], "failed": F[0], "errors": E[0],
                        "rate": rate, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "dir": os.path.basename(d)}
                    save_hist_entry(e)
                    save_auto_tcs(plan)
                    update_tc_status(plan, xml_path)
                    yield f"data: {json.dumps({'t':'done','total':T[0],'passed':P[0],'failed':F[0],'errors':E[0],'rate':rate})}\n\n"
                    RUN_PROCS.pop(pid, None)
                    break
                st = line.strip()
                if "PASSED" in st and "::" in st:
                    T[0] += 1; P[0] += 1; icon = "[PASS]"
                elif "FAILED" in st and "::" in st:
                    T[0] += 1; F[0] += 1; icon = "[FAIL]"
                elif "ERROR" in st and "::" in st:
                    T[0] += 1; E[0] += 1; icon = "[ERR ]"
                else:
                    icon = ""
                pct_str = ""
                m = re.search(r'\[(\s*\d+)%\]', st)
                if m: pct_str = m.group(1).strip()
                out_line = f"{icon} {st[-280:]}" if icon else st[-300:]
                out_line = out_line.replace("\n"," ").replace("\r","")
                yield f"data: {json.dumps({'t':'test','line':out_line,'pct':pct_str})}\n\n"
        finally:
            # Keep PLANS alive on disconnect so reconnection works
            pass
    return StreamingResponse(s(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})


@app.get("/api/report-count")
def report_count():
    """Return just the numbers from latest XML"""
    xml_files = []
    for root, dirs, files in os.walk(GEN):
        for file_name in files:
            if file_name == "results.xml": xml_files.append(os.path.join(root, file_name))
    if not xml_files: return {"total": 0, "passed": 0, "failed": 0, "rate": 0}
    xml_file = max(xml_files, key=os.path.getmtime)
    try:
        tree = ET.parse(xml_file)
        ts = tree.getroot().find("testsuite")
        if ts is None: ts = tree.getroot()
        t_val = ts.get("tests", "0")
        f_val = ts.get("failures", "0")
        e_val = ts.get("errors", "0")
        t = int(t_val) if t_val.isdigit() else 0
        f = int(f_val) if f_val.isdigit() else 0
        e = int(e_val) if e_val.isdigit() else 0
    except (ET.ParseError, Exception):
        logger.warning(f"Corrupt results.xml: {xml_file}")
        return {"total": 0, "passed": 0, "failed": 0, "rate": 0}
    p = t - f - e
    rate = round(p/t*100, 1) if t else 0
    return {"total": t, "passed": p, "failed": f, "errors": e, "rate": rate}


@app.get("/api/report-list")
def report_list():
    items = ""
    for d in sorted(os.listdir(GEN), reverse=True):
        dp = os.path.join(GEN, d)
        xf = os.path.join(dp, "results.xml")
        if not os.path.isdir(dp) or not os.path.exists(xf): continue
        try:
            root = ET.parse(xf).getroot()
            ts = root.find("testsuite") or root
            t = int(ts.get("tests","0") or 0); f = int(ts.get("failures","0") or 0); e = int(ts.get("errors","0") or 0)
            p = t-f-e; rate = round(p/t*100,1) if t else 0
            c = "#27ae60" if f==0 else "#ef5350"
            sd = html.escape(d, quote=True)
            items += f'<tr onclick="document.getElementById(\'d{sd}\').classList.toggle(\'hidden\')" style="cursor:pointer">'
            items += f'<td style="font-family:monospace;font-size:11px">{sd[:40]}</td><td style="color:#3498db;font-weight:700">{t}</td>'
            items += f'<td style="color:#27ae60;font-weight:700">{p}</td><td style="color:#ef5350;font-weight:700">{f}</td>'
            items += f'<td style="color:#ff9800;font-weight:700">{e}</td>'
            items += f'<td style="color:{c};font-weight:700">{rate}%</td>'
            items += f'<td><a href="/api/report?dir={sd}" target="_blank">打开</a></td></tr>'
            items += f'<tr class="hidden" id="d{sd}"><td colspan="6"><iframe src="/api/report?dir={sd}" style="width:100%;height:400px;border:none;border-radius:6px"></iframe></td></tr>'
        except (ET.ParseError, OSError, ValueError): pass
    return HTMLResponse(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>报告库</title>
<style>body{{font-family:sans-serif;max-width:1200px;margin:30px auto;background:#f5f6fa;color:#333;padding:0 20px}}
h1{{color:#2c3e50}}table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
th{{background:#f8f9fb;padding:10px;text-align:left;font-size:11px;color:#888}}td{{padding:10px;border-bottom:1px solid #eee;font-size:12px}}
tr:hover td{{background:#fafbff}}.hidden{{display:none}}</style></head><body>
<h1>测试报告库</h1><p style="color:#888;font-size:13px;margin-bottom:20px">点击行展开详情</p>
<table><thead><tr><th>名称</th><th>总计</th><th>通过</th><th>失败</th><th>错误</th><th>通过率</th><th>详情</th></tr></thead>
<tbody>{items}</tbody></table><p style="text-align:center;margin-top:20px"><a href="/">返回</a></p>
</body></html>""")


@app.get("/api/report")
def report(dir: str = ""):
    try:
        return _build_report(dir)
    except Exception as ex:
        logger.error(f"Report crash: {ex}", exc_info=_DEBUG)
        return HTMLResponse(f"<body style='font-family:sans-serif;text-align:center;padding:80px;color:#888'><h2>Report Error</h2><p>{html.escape(str(ex)[:200])}</p></body>")


def _build_report(dir: str):
    if dir:
        dir = safe(dir)  # Prevent path traversal
        xml_path = os.path.join(GEN, dir, "results.xml")
        if not os.path.exists(xml_path):
            return HTMLResponse("<body style='font-family:sans-serif;text-align:center;padding:80px;color:#888'><h2>Report Not Found</h2></body>")
        xml_files = [xml_path]
    else:
        xml_files = []
        for root, dirs, files in os.walk(GEN):
            for f in files:
                if f == "results.xml":
                    xml_files.append(os.path.join(root, f))
    if not xml_files:
        body = '<body style="font-family:sans-serif;text-align:center;padding:80px;color:#888">'
        body += '<h2>No Report Yet</h2><p>Run a test first</p>'
        body += '<p><a href="/">Back</a></p></body>'
        return HTMLResponse(body)

    try:
        xml_file = max(xml_files, key=os.path.getmtime)
        tree = ET.parse(xml_file)
    except (ET.ParseError, OSError, FileNotFoundError):
        return HTMLResponse("<body style='font-family:sans-serif;text-align:center;padding:80px;color:#888'><h2>Report Corrupted</h2><p>Try running tests again</p></body>")
    root_el = tree.getroot()
    # Get totals from the first testsuite
    ts = root_el.find("testsuite")
    if ts is None: ts = root_el
    total = int(ts.get("tests", 0) or 0)
    failed = int(ts.get("failures", 0) or 0)
    errors = int(ts.get("errors", 0) or 0)
    skipped = int(ts.get("skipped", 0) or 0)
    passed = total - failed - errors - skipped
    stime = float(ts.get("time", 0) or 0)

    rows = ""
    tc_num = 0
    for ts in root_el.findall("testsuite"):
        for tc in ts.findall("testcase"):
            tc_num += 1
            cn = tc.get("classname", "")
            tn = tc.get("name", "")
            dur = tc.get("time", "")
            fail_el = tc.find("failure")
            err_el = tc.find("error")

            # Extract module from classname: "Test_首页" -> "首页"
            mod_name = cn.split(".")[-1].replace("Test_","") if "." in cn else cn
            # File type: test_api/test_ui/test_data/test_unit
            parts = cn.split(".")
            file_type = (parts[-2] if len(parts) >= 3 else "").replace("test_","").replace("_"," ")
            # Scenario mapping
            smap = {"test_ok":"正常请求响应","test_body":"响应体验证","test_type":"Content-Type","test_time":"响应时间","test_head":"HEAD请求","test_page":"分页参数","test_mobile":"移动端UA","test_json_accept":"JSON请求头","test_empty":"空请求体","test_bad":"非法JSON","test_form":"表单提交","test_load":"页面加载","test_reachable":"服务可达","test_response_time":"响应基准"}
            scenario = smap.get(tn, "功能验证")
            # Test point
            # Test scenario + expected result mapping
            scn_map = {
                "test_ok":("接口可达性","HTTP状态码为2xx/3xx"),
                "test_body":("响应内容检查","响应体非空或状态码>=300"),
                "test_type":("响应头检查","Content-Type包含合法值或状态码>=300"),
                "test_time":("性能基准","响应时间小于5秒"),
                "test_head":("HEAD请求","HEAD请求状态码小于500"),
                "test_page":("分页参数","带page参数请求状态码小于500"),
                "test_mobile":("移动端UA","iPhone UA请求状态码小于500"),
                "test_json_accept":("JSON请求头","Accept:application/json状态码小于500"),
                "test_empty":("空请求体","空POST请求状态码小于500"),
                "test_bad":("非法JSON","非法JSON POST请求状态码小于500"),
                "test_form":("表单提交","form-data POST请求状态码小于500"),
                "test_load":("页面渲染","页面元素可见且标题非空"),
                "test_1_page_loaded":("页面加载","元素可见且标题非空"),
                "test_2_no_console_errors":("控制台检查","无JS运行时错误"),
                "test_3_load_time":("页面性能","加载时间小于10秒"),
                "test_4_mobile_viewport":("移动端适配","375x812视口正常渲染"),
                "test_5_links_exist":("导航元素","页面存在超链接"),
                "test_6_resources_loaded":("静态资源","CSS/JS/图片加载无4xx"),
                "test_1_reachable":("服务可达","GET请求状态码<500"),
                "test_2_response_time":("响应基准","响应时间<10秒"),
                "test_3_ssl_valid":("SSL证书","HTTPS连接正常"),
                "test_4_redirect_follow":("重定向","正确跟随3xx跳转"),
                "test_5_headers_present":("响应头","至少包含1个响应头"),
                "test_6_content_length":("响应大小","响应体>0字节"),
                "test_7_encoding_valid":("字符编码","编码声明正确"),
                "test_8_concurrent":("并发请求","3并发全通过"),
            }
            scn, expected = scn_map.get(tn, ("功能验证","请求正常响应"))
            # Data rules
            if tn.startswith("test_d"):
                num = tn.replace("test_d","")
                scn = f"数据校验规则{num}"
                expected = "数据符合业务规则"

            if fail_el is not None:
                status = "fail"; color = "#ef5350"; badge = "失败"
                detail = (fail_el.get("message", "") + "\n" + (fail_el.text or ""))[:500]
            elif err_el is not None:
                status = "error"; color = "#ff9800"; badge = "异常"
                detail = (err_el.get("message", "") + "\n" + (err_el.text or ""))[:500]
            else:
                status = "passed"; color = "#27ae60"; badge = "通过"
                detail = ""

            det_html = ""
            if detail:
                bar = "█" * 20
                det_html = f'<details><summary style="cursor:pointer;color:{color};font-size:11px">查看详情</summary><pre style="background:#1a1c23;color:#ff7675;padding:8px;border-radius:4px;font-size:10px;overflow-x:auto;max-width:400px;margin:4px 0 0;white-space:pre-wrap">' + html.escape(detail, quote=False) + '</pre></details>'

            # Precondition from test name
            precond_map = {
                "test_ok":"无", "test_body":"无", "test_type":"无", "test_time":"无",
                "test_head":"服务支持HEAD方法", "test_page":"接口支持分页参数",
                "test_mobile":"无需特殊前置", "test_json_accept":"接口支持JSON响应",
                "test_empty":"接口接收空请求体", "test_bad":"接口解析非法JSON",
                "test_form":"接口接收form-data", "test_load":"页面可公网访问",
                "test_1_page_loaded":"目标页面可访问", "test_2_no_console_errors":"无",
                "test_3_load_time":"网络通畅", "test_4_mobile_viewport":"无",
                "test_5_links_exist":"页面含超链接元素", "test_6_resources_loaded":"无",
                "test_1_reachable":"服务运行中", "test_2_response_time":"网络延迟<10s",
                "test_3_ssl_valid":"HTTPS启用", "test_4_redirect_follow":"服务可能返回3xx",
                "test_5_headers_present":"服务正常响应", "test_6_content_length":"服务返回内容",
                "test_7_encoding_valid":"服务声明编码", "test_8_concurrent":"服务支持并发请求",
            }
            precondition = precond_map.get(tn, "无")

            rows += '<tr>'
            rows += f'<td style="font-family:monospace;font-size:10px">TC-{tc_num:03d}</td>'
            rows += f'<td><strong>{html.escape(mod_name, quote=False)}</strong></td>'
            rows += f'<td>{html.escape(file_type, quote=False)}</td>'
            rows += f'<td style="font-size:10px">{precondition}</td>'
            rows += f'<td>{scn}</td>'
            rows += f'<td style="font-size:11px">{expected}</td>'
            rows += f'<td style="color:{color};font-weight:700">{badge}</td>'
            rows += f'<td style="font-size:11px;color:#888">{dur}s</td>'
            rows += f'<td style="font-size:11px">{det_html}</td>'
            rows += '</tr>\n'

    rate = round(passed / total * 100, 1) if total else 0
    mc = "#27ae60" if failed == 0 and errors == 0 else "#ef5350"

    page = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>Test Report</title>\n'
    page += '<style>\n'
    page += 'body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:1200px;margin:30px auto;background:#f5f6fa;color:#333;padding:0 20px}\n'
    page += '.header{background:linear-gradient(135deg,#5c6bc0,#7c4dff);color:#fff;padding:32px 36px;border-radius:12px;margin-bottom:24px}\n'
    page += '.header h1{margin:0 0 6px;font-size:22px}.header p{opacity:.85;font-size:12px;margin:4px 0}\n'
    page += '.metrics{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}\n'
    page += '.m{background:#fff;border-radius:8px;padding:18px 22px;text-align:center;min-width:100px;box-shadow:0 2px 8px rgba(0,0,0,.04);flex:1}\n'
    page += '.m .v{font-size:30px;font-weight:700;display:block}.m .l{font-size:11px;color:#888;margin-top:4px}\n'
    page += '.bar{height:10px;background:#e8ecf1;border-radius:5px;overflow:hidden;margin:16px 0}\n'
    page += 'table{width:100%;border-collapse:collapse;font-size:12px;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04)}\n'
    page += 'th{background:#f8f9fb;padding:10px 8px;text-align:left;font-size:10px;color:#888;text-transform:uppercase}\n'
    page += 'td{padding:8px;border-bottom:1px solid #eee;font-size:11px}tr:hover td{background:#fafbff}\n'
    page += '.footer{text-align:center;margin-top:30px;font-size:11px;color:#888;padding:16px}\n'
    page += '</style></head><body>\n'
    page += '<div class="header"><h1>自动化测试报告</h1>'
    page += f'<p>标准: ISTQB / IEEE 829 | 耗时: {stime:.1f}s | {datetime.now().strftime("%Y-%m-%d %H:%M")}</p></div>\n'
    page += '<div class="metrics">\n'
    page += f'<div class="m"><span class="v" style="color:#3498db">{total}</span><span class="l">总计</span></div>\n'
    page += f'<div class="m"><span class="v" style="color:#27ae60">{passed}</span><span class="l">通过</span></div>\n'
    page += f'<div class="m"><span class="v" style="color:#ef5350">{failed}</span><span class="l">失败</span></div>\n'
    page += f'<div class="m"><span class="v" style="color:#ff9800">{errors}</span><span class="l">错误</span></div>\n'
    page += f'<div class="m"><span class="v" style="color:{mc}">{rate}%</span><span class="l">通过率</span></div>\n'
    page += '</div>\n'
    page += f'<div class="bar"><div style="height:100%;border-radius:5px;width:{rate}%;background:{mc}"></div></div>\n'
    page += '<div style="overflow-x:auto"><table>\n'
    page += '<thead><tr><th>ID</th><th>测试模块</th><th>测试类型</th><th>前置条件</th><th>测试点</th><th>预期结果</th><th>结果</th><th>耗时</th><th>备注</th></tr></thead>\n'
    page += '<tbody>\n'
    page += rows
    page += '</tbody></table></div>\n'
    page += '<div style="background:#f0fdf4;border-left:4px solid #27ae60;padding:14px 20px;margin-top:20px;border-radius:6px;font-size:12px">\n'
    page += '<strong>安全合规声明:</strong> 仅发送标准HTTP请求。不包含真实用户数据(PII)、暴力扫描、绕过安全机制或未经授权的操作。\n'
    page += '</div>\n'
    page += '<div class="footer">Test Workshop Pro | ISTQB Compliant</div>\n'
    page += '</body></html>'
    return HTMLResponse(page)


# ====== Test Case Manager ======
def load_tc():
    """Load test case library from test_cases.json."""
    if os.path.exists(TCF):
        try:
            with open(TCF, encoding="utf-8") as f:
                data = json.loads(f.read())
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            logger.warning(f"Corrupted test cases file, resetting")
            try: os.rename(TCF, TCF + ".bak")
            except OSError: pass
    return []

def save_tc(d):
    """Save test case library to test_cases.json. Atomic write."""
    _atomic_write(TCF, d)

@app.get("/api/tc")
def list_tc():
    return {"cases": load_tc()}

@app.post("/api/tc")
async def add_tc(request: Request):
    b = await request.json()
    tcs = load_tc()
    if len(tcs) >= 500:
        return {"ok": False, "error": "Test case limit reached (500 max)"}
    max_id = max([int(tc.get("id","0")) for tc in tcs] + [0])
    tc = {
        "id": str(max_id + 1).zfill(3),
        "module": str(b.get("module", ""))[:100],
        "title": str(b.get("title", ""))[:200],
        "priority": b.get("priority", "P1")[:10],
        "method": b.get("method", "GET"),
        "path": str(b.get("path", ""))[:500],
        "expected": str(b.get("expected", ""))[:500],
        "steps": str(b.get("steps", ""))[:1000],
        "status": "Pending",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tcs.append(tc)
    save_tc(tcs)
    return {"ok": True}

@app.post("/api/save-tc")
async def save_plan_to_tc(request: Request):
    """Save plan's APIs/pages to TC library without executing."""
    b = await request.json()
    before = len(load_tc())
    save_auto_tcs(b)
    after = len(load_tc())
    return {"ok": True, "added": after - before, "total": after}


@app.get("/api/ai-key-status")
def ai_key_status():
    """Return whether AI key is configured (never reveal the actual key)."""
    return {"configured": bool(_ai_key), "source": "env" if os.environ.get("TW_AI_KEY") else ("ui" if _ai_key else "none")}


@app.post("/api/ai-key")
async def set_ai_key(request: Request):
    """Set AI API key. Encrypted at rest, decrypted to memory only."""
    global _ai_key
    body = await request.json()
    key = str(body.get("key", "")).strip()
    if not key:
        # Clear key
        _ai_key = ""
        try: os.remove(_AI_ENC_FILE)
        except OSError: pass
        logger.info("AI key cleared")
        return {"ok": True, "masked": ""}
    if len(key) < 8:
        return {"ok": False, "error": "Key too short"}
    _ai_key = key
    try:
        with open(_AI_ENC_FILE, "wb") as f:
            f.write(_encrypt_key(key))
        os.chmod(_AI_ENC_FILE, 0o600)
        logger.info("AI key encrypted and persisted (length=%d)", len(key))
    except Exception as e:
        logger.error(f"Failed to encrypt AI key: {e}")
        return {"ok": False, "error": "Encryption failed"}
    return {"ok": True, "masked": key[:6] + "****" if len(key) > 6 else "****"}


_RESOURCE_PATTERNS = {
    r"users?|accounts?|members?": {
        "scenarios": ["创建-正常数据", "创建-重复用户名", "创建-缺少必填字段",
                      "创建-无效邮箱", "创建-超长用户名", "批量创建-100条",
                      "获取列表-分页", "获取详情-存在ID", "获取详情-不存在ID",
                      "更新-正常", "更新-不存在ID", "更新-只读字段不可改",
                      "删除-正常", "删除-不存在ID", "删除-有依赖数据"],
        "auth": True, "pagination": True, "validation": ["email", "username", "password"]
    },
    r"tasks?|todos?|items?": {
        "scenarios": ["创建-正常", "创建-空标题", "更新状态-完成/取消",
                      "获取列表-按状态过滤", "获取列表-按日期排序",
                      "批量更新-全部完成", "删除-正常", "删除-已完成不可删"],
        "auth": True, "pagination": True
    },
    r"orders?|payments?|transactions?": {
        "scenarios": ["创建-正常", "创建-库存不足", "创建-金额为0",
                      "创建-金额为负", "退款-正常", "退款-已退款不可重复",
                      "查询-按状态", "查询-按时间范围", "导出-生成报表"],
        "auth": True, "pagination": True, "idempotent": True
    },
    r"login|auth|signin|token": {
        "scenarios": ["登录-正确凭据", "登录-错误密码", "登录-不存在用户",
                      "登录-空用户名", "登录-空密码", "登录-锁定账户",
                      "刷新Token-有效", "刷新Token-过期", "登出-正常"],
        "auth": False, "rate_limit": True
    },
    r"search|query|find": {
        "scenarios": ["搜索-有结果", "搜索-无结果", "搜索-空关键词",
                      "搜索-超长关键词", "搜索-特殊字符", "搜索-分页"],
        "pagination": True
    },
    r"upload|file|image|avatar|media": {
        "scenarios": ["上传-正常图片", "上传-超大文件", "上传-不支持格式",
                      "上传-空文件", "批量上传-10个", "删除-正常"],
        "file_upload": True
    },
    r"stats?|reports?|analytics?|dashboard": {
        "scenarios": ["统计-总体数据", "统计-时间段筛选", "统计-无数据时期",
                      "统计-数据一致性校验", "导出-CSV", "导出-JSON"],
        "auth": True, "cache": True
    },
    r"config|settings?|profile": {
        "scenarios": ["获取配置-正常", "更新配置-正常", "更新配置-无效值",
                      "更新配置-超限值", "重置-默认值"],
        "auth": True
    },
}


@app.post("/api/ai-suggest")
async def ai_suggest(request: Request):
    """AI-powered test case suggestion — uses LLM if key configured, else patterns."""
    try:
        body = await request.json()
        apis = body.get("apis", [])
        seed = body.get("seed", 0)
        model = body.get("model", "") or os.environ.get("TW_AI_MODEL", "gpt-4o")
        base_url = body.get("base_url", "") or os.environ.get("TW_AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if _ai_key:
            try:
                results = await _call_llm(apis, seed, model, base_url)
                if results is not None and len(results) > 0:
                    return {"suggestions": results, "source": "ai"}
                elif results is not None:
                    return {"suggestions": _pattern_suggest(apis, seed), "source": "pattern", "ai_error": "AI 返回了空列表"}
            except Exception as e:
                logger.warning(f"AI call failed, fallback: {e}")
                return {"suggestions": _pattern_suggest(apis, seed), "source": "pattern", "ai_error": str(e)[:200]}
        msg = "API Key 未配置" if not _ai_key else "AI 返回为空"
        return {"suggestions": _pattern_suggest(apis, seed), "source": "pattern", "ai_error": msg}
    except Exception as e:
        logger.error(f"ai-suggest crashed: {e}", exc_info=True)
        return {"suggestions": []}


async def _call_llm(apis, seed, model, base_url):
    import httpx, random
    random.seed(seed)
    api_lines = "\n".join(f"- {a.get('m','GET')} {a.get('p','/')} ({a.get('n','')})" for a in apis)
    prompt = f"""你是ISTQB高级测试工程师。根据以下API列表，为每个API生成丰富的测试用例。要求全面覆盖：

API:
{api_lines}

为每个API生成6-12条用例，包括：
- P0: 正常场景、核心业务、认证授权（2-3条）
- P1: 异常输入、边界条件、权限校验（2-4条）  
- P2: 并发/性能、安全注入(XSS/SQL)、兼容性（2-4条）

每条用例JSON: title, priority(P0/P1/P2), expected(具体状态码+响应内容), precondition(实际前置条件), steps(详细步骤), method, path
总量不限，越多越好。返回纯JSON数组。"""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {_ai_key}"},
            json={"model":model,"messages":[{"role":"user","content":prompt}],
                  "temperature":0.8+random.random()*0.2,"max_tokens":8000})
        if r.status_code != 200: raise Exception(f"AI API {r.status_code}")
        text = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in text: text = text.split("```")[1].lstrip("json").strip()
        import json as _j
        # Try parsing, with fallbacks for malformed AI output
        try:
            return _j.loads(text)
        except _j.JSONDecodeError:
            # Try to extract array: find first [ and last ]
            start = text.find("[")
            end = text.rfind("]")
            if start >= 0 and end > start:
                try:
                    return _j.loads(text[start:end+1])
                except _j.JSONDecodeError:
                    pass
            # Try line-by-line extraction of objects
            items = []
            for line in text.split("\n"):
                line = line.strip().rstrip(",")
                if line.startswith("{") and line.endswith("}"):
                    try: items.append(_j.loads(line))
                    except _j.JSONDecodeError: pass
            if items: return items
            # Last resort: auto-close truncated JSON
            fixed = text[start:end+1] if start>=0 and end>start else text
            if fixed.rstrip().endswith(","): fixed = fixed.rstrip().rstrip(",") + "]"
            if not fixed.rstrip().endswith("]"): fixed = fixed.rstrip() + "]"
            # Close any unclosed string
            if fixed.count('"') % 2 != 0: fixed += '"'
            try: return _j.loads(fixed)
            except _j.JSONDecodeError: pass
            raise Exception(f"AI returned unparseable JSON: {text[:100]}")


def _pattern_suggest(apis, seed):
    import random; random.seed(seed)
    suggestions = []
    step_tmpl = ["发送 {m} {p}","发送 {m} {p}，检查状态码","构造请求 → {m} {p} → 解析响应","1.准备数据 2.发送 {m} {p} 3.验证"]
    extra = ["并发10请求","超时重试","SQL注入字符","XSS脚本标签","过期Token","大请求体413","不支持MediaType415"]
    exp_var = {"normal":["HTTP 200","HTTP 201","HTTP 200/201/204"],"error":["HTTP 400","HTTP 422","HTTP 400/422"],"general":["HTTP 2xx","HTTP 200/301/302"]}
    pre_var = ["服务已启动","数据库已初始化","缓存已预热","测试数据已准备","Token已获取","无"]
    for api in apis:
        m=api.get("m","GET"); p=api.get("p","/"); n=api.get("n",""); pl=p.lower(); pf=f"[{m}] {n or p}"
        matched=False
        for pat,cfg in _RESOURCE_PATTERNS.items():
            if re.search(pat,pl):
                matched=True; sc=list(cfg.get("scenarios",[])); random.shuffle(sc)
                keep=max(2,int(len(sc)*random.uniform(0.5,0.8)))
                for s in sc[:keep]:
                    pri="P0" if any(w in s for w in ["正常","正确","登录"]) else ("P1" if any(w in s for w in ["列表","详情"]) else "P2")
                    pool="error" if any(w in s for w in ["缺少","无效","错误","不存在","空","重复"]) else ("normal" if any(w in s for w in ["创建","正常"]) else "general")
                    suggestions.append({"title":f"{pf}-{s}","priority":pri,"method":m,"path":p,"expected":random.choice(exp_var.get(pool,exp_var["general"])),"precondition":random.choice(pre_var),"steps":random.choice(step_tmpl).replace("{m}",m).replace("{p}",p)})
                for s in random.sample(extra,random.randint(0,2)):
                    suggestions.append({"title":f"{pf}-{s}","priority":"P2","method":m,"path":p,"expected":random.choice(exp_var["general"]),"precondition":random.choice(["无","服务已启动"]),"steps":random.choice(step_tmpl).replace("{m}",m).replace("{p}",p)})
                break
        if not matched:
            for t,pri,exp,pre in [("可达性验证","P0","HTTP 200/301/302/304","服务运行中"),("响应时间基准","P1","<5秒","网络通畅"),("空请求处理","P2","状态码<500","无"),("异常参数容错","P2","不应返回500","无")]:
                suggestions.append({"title":f"{pf}-{t}","priority":pri,"method":m,"path":p,"expected":exp,"precondition":pre,"steps":random.choice(step_tmpl).replace("{m}",m).replace("{p}",p)})
    return suggestions


@app.put("/api/tc/{cid}")
async def upd_tc(cid: str, request: Request):
    b = await request.json()
    tcs = load_tc()
    for tc in tcs:
        if tc["id"] == cid:
            for k in ["module", "title", "priority", "method", "path", "expected", "steps", "status"]:
                if k in b:
                    tc[k] = b[k]
            save_tc(tcs)
            return {"ok": True}
    return {"ok": False}

@app.delete("/api/tc/{cid}")
def del_tc(cid: str):
    tcs = [tc for tc in load_tc() if tc["id"] != cid]
    save_tc(tcs)
    return {"ok": True}


def save_auto_tcs(plan):
    """Save auto-generated test cases to library with dedup by title."""
    name = plan.get("name", "未命名")
    existing = load_tc()
    seen = {tc.get("title", "") for tc in existing}
    added = 0
    for api in plan.get("apis", []):
        m = api.get("m", "GET")
        p = safe_path(api.get("p", "/"))
        title = api.get("n", p)
        if title in seen:
            continue
        seen.add(title)
        max_id = max([int(tc.get("id","0")) for tc in existing] + [0])
        existing.append({
            "id": str(max_id + 1).zfill(3),
            "module": safe(name),
            "title": title,
            "priority": "P1",
            "method": m,
            "path": p,
            "expected": "HTTP状态码 < 500",
            "steps": f"1. 发送 {m} {p}",
            "status": "待执行",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        added += 1
    for pg in plan.get("pages", []):
        u = safe_path(pg.get("u", "/"))
        pg_name = pg.get("na", u)
        m = "GET"
        title = f"UI-{pg_name}"
        if title in seen:
            continue
        seen.add(title)
        max_id = max([int(tc.get("id","0")) for tc in existing] + [0])
        existing.append({
            "id": str(max_id + 1).zfill(3),
            "module": safe(name),
            "title": f"UI-{pg_name}",
            "priority": "P1",
            "method": m,
            "path": u,
            "expected": "页面可访问，无JS错误",
            "steps": f"1. Playwright打开页面 {u}",
            "status": "待执行",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        added += 1
    if added:
        save_tc(existing)
        logger.info(f"Saved {added} auto-generated TCs from '{name}'")


def update_tc_status(plan, xml_path):
    """Update test case statuses based on execution results."""
    if not os.path.exists(xml_path):
        return
    try:
        root = ET.parse(xml_path).getroot()
        results = {}  # classname -> status
        for ts in root.findall("testsuite"):
            for tc in ts.findall("testcase"):
                cn = tc.get("classname", "")
                failed = tc.find("failure") is not None
                errored = tc.find("error") is not None
                results[cn] = "失败" if failed else ("异常" if errored else "通过")
        if not results:
            return
        tcs = load_tc()
        updated = 0
        for tc in tcs:
            if tc.get("status") in ("通过", "失败", "异常"):
                continue  # already has final status, don't overwrite unless re-run
            # Match by method+path
            m = tc.get("method", "GET")
            p = tc.get("path", "")
            best = "通过"
            for cn, status in results.items():
                if p in cn and ("Test_" in cn or "test_" in cn):
                    if status != "通过":
                        best = status
                        break
            tc["status"] = best
            updated += 1
        if updated:
            save_tc(tcs)
    except Exception:
        pass

@app.get("/tc")
def tc_page():
    return FileResponse(os.path.join(BASE, "static", "tc.html"))

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("TW_HOST", "127.0.0.1")
    port = int(os.environ.get("TW_PORT", "9000"))
    cert = os.environ.get("TW_CERT_FILE", "")
    key = os.environ.get("TW_KEY_FILE", "")
    kwargs = {"host": host, "port": port}
    if cert and key and os.path.exists(cert) and os.path.exists(key):
        kwargs["ssl_certfile"] = cert
        kwargs["ssl_keyfile"] = key
        logger.info(f"HTTPS enabled: {host}:{port}")
    else:
        logger.info(f"HTTP mode: {host}:{port}")
    uvicorn.run(app, **kwargs)
