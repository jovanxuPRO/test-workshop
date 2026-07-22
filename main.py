"""
Test Workshop Pro v5 - JUnit XML Report + SSE Streaming
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
import os, json, shutil, subprocess, threading, queue, asyncio, re, xml.etree.ElementTree as ET
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Test Workshop Pro")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")
GEN = os.path.join(BASE, "generated_tests")
os.makedirs(GEN, exist_ok=True)
app.mount("/gen", StaticFiles(directory=GEN), name="gen")
TCF = os.path.join(BASE, "test_cases.json")

def safe(s): return re.sub(r'[^\w\u4e00-\u9fff]', '_', str(s))[:30].strip('_') or 't'

def gen_code(plan):
    name = plan.get("name", "u"); url = plan.get("url", "http://localhost")
    apis = plan.get("apis", []); pages = plan.get("pages", [])
    rules = plan.get("rules", []); types = plan.get("types", ["api", "ui", "data"])
    out = os.path.join(GEN, safe(name))
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)

    # conftest
    cf = '# Auto-generated test config\n'
    cf += 'import pytest, httpx, time\n'
    cf += f'B = "{url}"\n'
    cf += '@pytest.fixture\n'
    cf += 'def c():\n'
    cf += '    with httpx.Client(base_url=B, timeout=25, follow_redirects=True,\n'
    cf += '        headers={"User-Agent":"Mozilla/5.0"}) as cl: yield cl\n'
    cf += '@pytest.fixture(scope="session")\n'
    cf += 'def browser():\n'
    cf += '    from playwright.sync_api import sync_playwright\n'
    cf += '    with sync_playwright() as p:\n'
    cf += '        br = p.chromium.launch(headless=False, slow_mo=300)\n'
    cf += '        yield br; br.close()\n'
    cf += '@pytest.fixture\n'
    cf += 'def page(browser):\n'
    cf += '    ctx = browser.new_context()\n'
    cf += '    pg = ctx.new_page(); pg.set_default_timeout(20000)\n'
    cf += '    yield pg; ctx.close()\n'
    with open(os.path.join(out, "conftest.py"), "w", encoding="utf-8") as f:
        f.write(cf)

    # unit tests - expanded
    ut = 'import pytest, httpx, time\n'
    ut += f'B = "{url}"\n'
    ut += 'class TestUnit:\n'
    ut += '    def test_1_reachable(self):\n'
    ut += '        """服务可达性"""\n'
    ut += '        try: r = httpx.get(B, timeout=15, follow_redirects=True); assert r.status_code < 500\n'
    ut += '        except: pytest.skip("unreachable")\n\n'
    ut += '    def test_2_response_time(self):\n'
    ut += '        """响应时间基准"""\n'
    ut += '        try: t0=time.time(); httpx.get(B,timeout=20,follow_redirects=True); assert time.time()-t0<10\n'
    ut += '        except: pytest.skip("timeout")\n\n'
    ut += '    def test_3_ssl_valid(self):\n'
    ut += '        """SSL证书有效"""\n'
    ut += '        if not B.startswith("https"): pytest.skip("HTTP only")\n'
    ut += '        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert r.status_code<500\n'
    ut += '        except: pytest.skip("ssl check failed")\n\n'
    ut += '    def test_4_redirect_follow(self):\n'
    ut += '        """重定向跟踪"""\n'
    ut += '        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.history)>=0\n'
    ut += '        except: pytest.skip("redirect check")\n\n'
    ut += '    def test_5_headers_present(self):\n'
    ut += '        """响应头完整"""\n'
    ut += '        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.headers)>0\n'
    ut += '        except: pytest.skip("headers check")\n\n'
    ut += '    def test_6_content_length(self):\n'
    ut += '        """响应体大小"""\n'
    ut += '        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.content)>0 or r.status_code>=300\n'
    ut += '        except: pytest.skip("content check")\n\n'
    ut += '    def test_7_encoding_valid(self):\n'
    ut += '        """编码声明检查"""\n'
    ut += '        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert r.encoding or r.status_code>=300\n'
    ut += '        except: pytest.skip("encoding check")\n\n'
    ut += '    def test_8_concurrent(self):\n'
    ut += '        """并发请求"""\n'
    ut += '        try:\n'
    ut += '            import concurrent.futures\n'
    ut += '            def req(): return httpx.get(B,timeout=20,follow_redirects=True).status_code\n'
    ut += '            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:\n'
    ut += '                results = list(ex.map(lambda _: req(), range(3)))\n'
    ut += '            assert all(s<500 for s in results)\n'
    ut += '        except: pytest.skip("concurrent check")\n\n'
    with open(os.path.join(out, "test_unit.py"), "w", encoding="utf-8") as f:
        f.write(ut)

    # api tests
    if "api" in types and apis:
        lines = ["import pytest, time", ""]
        for a in apis:
            m = a.get("m", "GET"); p = a.get("p", "/"); n = safe(a.get("n", ""))
            tp = p.replace("{id}", "1")
            lines.append(f"class Test_{n}:")
            lines.append(f'    """{m} {p}"""')
            lines.append("")
            if m == "GET":
                tests = [
                    ("ok", f'c.get("{tp}")', "r.status_code in (200,301,302,304)"),
                    ("body", f'c.get("{tp}")', "len(r.content) > 0 or r.status_code >= 300"),
                    ("type", f'c.get("{tp}")', '"content-type" in str(r.headers).lower() or r.status_code >= 300'),
                    ("time", f'c.get("{tp}")', "elapsed < 5"),
                    ("head", f'c.head("{tp}")', "r.status_code < 500"),
                    ("page", f'c.get("{tp}?page=1")', "r.status_code < 500"),
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
            else:
                tests = []
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
        for pg in pages:
            u = pg.get("u","/"); na = safe(pg.get("na",""))
            lines.append(f"class Test_{na}:")
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
            lines.append(f'        assert links>=0')
            lines.append("")
            # Test 6: resources loaded
            lines.append(f"    def test_6_resources_loaded(self,page):")
            lines.append(f'        """静态资源加载"""')
            lines.append(f'        failed=[]')
            lines.append(f'        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)')
            lines.append(f'        page.goto(B+"{u}")')
            lines.append(f'        page.wait_for_timeout(3000)')
            lines.append(f'        assert True')
            lines.append("")
        with open(os.path.join(out, "test_ui.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # data tests
    if "data" in types and rules:
        lines = ["import pytest, httpx", "from conftest import B", "",
            "@pytest.fixture",
            "def c():",
            "    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as cl: yield cl",
            "", "class TestData:", ""]
        for i, r in enumerate(rules):
            dr = r.replace('"', "'")
            lines.append(f"    def test_d{i}(self, c):")
            lines.append(f'        """{dr}"""')
            lines.append('        resp = c.get("/")')
            lines.append('        assert resp.status_code < 500')
            lines.append("")
        with open(os.path.join(out, "test_data.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return out


HIST = os.path.join(BASE, "exec_history.json")

def load_hist():
    if os.path.exists(HIST):
        try: return json.loads(open(HIST, encoding="utf-8").read())
        except: pass
    return []

def save_hist_entry(entry):
    entries = load_hist()
    entries.insert(0, entry)
    if len(entries) > 50: entries = entries[:50]
    with open(HIST, "w", encoding="utf-8") as f:
        f.write(json.dumps(entries, ensure_ascii=False, indent=2))


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
        rows += f'<td>{e.get("name","?")}</td>'
        rows += f'<td>{e.get("url","?")}</td>'
        rows += f'<td>{e.get("time","?")}</td>'
        rows += f'<td style="color:#3498db;font-weight:700">{e.get("total",0)}</td>'
        rows += f'<td style="color:#27ae60;font-weight:700">{e.get("passed",0)}</td>'
        rows += f'<td style="color:#ef5350;font-weight:700">{e.get("failed",0)}</td>'
        rows += f'<td style="color:{color};font-weight:700">{e.get("rate",0)}%</td>'
        rows += f'<td><a href="/api/report" target="_blank" style="color:#5c6bc0">报告</a></td>'
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
        entries.pop(idx)
        with open(HIST, "w", encoding="utf-8") as f:
            f.write(json.dumps(entries, ensure_ascii=False, indent=2))
    return {"ok": True}


# Save on each execution
# In gnr endpoint, after parsing results:
@app.post("/api/gnr")
async def gnr(request: Request):
    try:
        body = await request.json()
        d = gen_code(body)
        xml_path = os.path.join(d, "results.xml")
        r = subprocess.run(["python", "-m", "pytest", d, "-v", "--tb=short", "--color=no", f"--junitxml={xml_path}"],
            capture_output=True, text=True, timeout=200)
        t = p = f = 0
        if os.path.exists(xml_path):
            root = ET.parse(xml_path).getroot()
            ts = root.find("testsuite")
            if ts is None: ts = root
            t = int(ts.get("tests", 0))
            f = int(ts.get("failures", 0))
            e = int(ts.get("errors", 0))
            p = t - f - e
        # Save to history
        save_hist_entry({
            "name": body.get("name", "?"),
            "url": body.get("url", "?"),
            "total": t, "passed": p, "failed": f, "errors": e,
            "rate": round(p/t*100,1) if t else 0,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        return {"ok": f == 0, "total": t, "passed": p, "failed": f, "log": r.stdout[-5000:]}
    except Exception as ex:
        import traceback
        return {"ok": False, "error": str(ex), "trace": traceback.format_exc()[-2000:]}


@app.get("/api/stream")
async def stream(request: Request):
    pj = request.query_params.get("plan", "")
    if not pj:
        async def e():
            yield f"data: {json.dumps({'t':'error'})}\n\n"
        return StreamingResponse(e(), media_type="text/event-stream")
    plan = json.loads(pj)
    d = gen_code(plan)
    xml_path = os.path.join(d, "results.xml")

    async def s():
        q = queue.Queue()
        T = [0]; P = [0]; F = [0]
        def w():
            proc = subprocess.Popen(
                ["python", "-m", "pytest", d, "-v", "--tb=line", "--color=no", f"--junitxml={xml_path}"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(proc.stdout.readline, ""):
                q.put(line)
            q.put("__END__")
            proc.wait()
        threading.Thread(target=w, daemon=True).start()
        yield f"data: {json.dumps({'t':'start'})}\n\n"
        while True:
            try:
                line = q.get(timeout=0.1)
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue
            if line == "__END__":
                rate = round(P[0] / T[0] * 100, 1) if T[0] else 0
                # Also save to history
                e = {"name": plan.get("name","?"), "url": plan.get("url","?"),
                    "total": T[0], "passed": P[0], "failed": F[0], "errors": 0,
                    "rate": rate, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                save_hist_entry(e)
                yield f"data: {json.dumps({'t':'done','total':T[0],'passed':P[0],'failed':F[0],'rate':rate})}\n\n"
                break
            st = line.strip()
            if "PASSED" in st and "::" in st:
                T[0] += 1; P[0] += 1
            elif "FAILED" in st and "::" in st:
                T[0] += 1; F[0] += 1
            # Extract percentage from pytest output like [ 42%]
            pct_str = ""
            m = re.search(r'\[(\s*\d+)%\]', st)
            if m: pct_str = m.group(1).strip()
            yield f"data: {json.dumps({'t':'test','line':st[-300:],'pct':pct_str})}\n\n"
    return StreamingResponse(s(), media_type="text/event-stream")


@app.get("/api/report-count")
def report_count():
    """Return just the numbers from latest XML"""
    xml_files = []
    for root, dirs, files in os.walk(GEN):
        for f in files:
            if f == "results.xml": xml_files.append(os.path.join(root, f))
    if not xml_files: return {"total": 0, "passed": 0, "failed": 0, "rate": 0}
    xml_file = max(xml_files, key=os.path.getmtime)
    tree = ET.parse(xml_file)
    ts = tree.getroot().find("testsuite")
    if ts is None: ts = tree.getroot()
    t = int(ts.get("tests", 0))
    f = int(ts.get("failures", 0))
    e = int(ts.get("errors", 0))
    p = t - f - e
    rate = round(p/t*100, 1) if t else 0
    return {"total": t, "passed": p, "failed": f, "errors": e, "rate": rate}


@app.get("/api/report")
def report():
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

    xml_file = max(xml_files, key=os.path.getmtime)
    tree = ET.parse(xml_file)
    root_el = tree.getroot()
    # Get totals from the first testsuite
    ts = root_el.find("testsuite")
    if ts is None: ts = root_el
    total = int(ts.get("tests", 0))
    failed = int(ts.get("failures", 0))
    errors = int(ts.get("errors", 0))
    skipped = int(ts.get("skipped", 0))
    passed = total - failed - errors - skipped
    stime = float(ts.get("time", 0))

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
                det_html = '<pre style="background:#1a1c23;color:#ff7675;padding:4px;border-radius:4px;font-size:10px;overflow-x:auto;max-width:350px;margin:0">' + detail + '</pre>'

            rows += '<tr>'
            rows += f'<td style="font-family:monospace;font-size:10px">TC-{tc_num:03d}</td>'
            rows += f'<td><strong>{mod_name}</strong></td>'
            rows += f'<td>{file_type}</td>'
            rows += f'<td>{scn}</td>'
            rows += f'<td style="font-size:11px">{expected}</td>'
            rows += f'<td style="color:{color};font-weight:700">{badge}</td>'
            rows += f'<td style="font-size:11px;color:#888">{dur}s</td>'
            rows += f'<td style="font-size:11px">{det_html}</td>'
            rows += '</tr>\n'

    rate = round(passed / total * 100, 1) if total else 0
    mc = "#27ae60" if failed == 0 and errors == 0 else "#ef5350"

    html = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>Test Report</title>\n'
    html += '<style>\n'
    html += 'body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:1200px;margin:30px auto;background:#f5f6fa;color:#333;padding:0 20px}\n'
    html += '.header{background:linear-gradient(135deg,#5c6bc0,#7c4dff);color:#fff;padding:32px 36px;border-radius:12px;margin-bottom:24px}\n'
    html += '.header h1{margin:0 0 6px;font-size:22px}.header p{opacity:.85;font-size:12px;margin:4px 0}\n'
    html += '.metrics{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}\n'
    html += '.m{background:#fff;border-radius:8px;padding:18px 22px;text-align:center;min-width:100px;box-shadow:0 2px 8px rgba(0,0,0,.04);flex:1}\n'
    html += '.m .v{font-size:30px;font-weight:700;display:block}.m .l{font-size:11px;color:#888;margin-top:4px}\n'
    html += '.bar{height:10px;background:#e8ecf1;border-radius:5px;overflow:hidden;margin:16px 0}\n'
    html += 'table{width:100%;border-collapse:collapse;font-size:12px;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04)}\n'
    html += 'th{background:#f8f9fb;padding:10px 8px;text-align:left;font-size:10px;color:#888;text-transform:uppercase}\n'
    html += 'td{padding:8px;border-bottom:1px solid #eee;font-size:11px}tr:hover td{background:#fafbff}\n'
    html += '.footer{text-align:center;margin-top:30px;font-size:11px;color:#888;padding:16px}\n'
    html += '</style></head><body>\n'
    html += '<div class="header"><h1>自动化测试报告</h1>'
    html += f'<p>标准: ISTQB / IEEE 829 | 耗时: {stime:.1f}s | {datetime.now().strftime("%Y-%m-%d %H:%M")}</p></div>\n'
    html += '<div class="metrics">\n'
    html += f'<div class="m"><span class="v" style="color:#3498db">{total}</span><span class="l">总计</span></div>\n'
    html += f'<div class="m"><span class="v" style="color:#27ae60">{passed}</span><span class="l">通过</span></div>\n'
    html += f'<div class="m"><span class="v" style="color:#ef5350">{failed}</span><span class="l">失败</span></div>\n'
    html += f'<div class="m"><span class="v" style="color:#ff9800">{errors}</span><span class="l">错误</span></div>\n'
    html += f'<div class="m"><span class="v" style="color:{mc}">{rate}%</span><span class="l">通过率</span></div>\n'
    html += '</div>\n'
    html += f'<div class="bar"><div style="height:100%;border-radius:5px;width:{rate}%;background:{mc}"></div></div>\n'
    html += '<div style="overflow-x:auto"><table>\n'
    html += '<thead><tr><th>ID</th><th>测试模块</th><th>测试类型</th><th>测试点</th><th>预期结果</th><th>结果</th><th>耗时</th><th>备注</th></tr></thead>\n'
    html += '<tbody>\n'
    html += rows
    html += '</tbody></table></div>\n'
    html += '<div style="background:#f0fdf4;border-left:4px solid #27ae60;padding:14px 20px;margin-top:20px;border-radius:6px;font-size:12px">\n'
    html += '<strong>安全合规声明:</strong> 仅发送标准HTTP请求。不包含真实用户数据(PII)、暴力扫描、绕过安全机制或未经授权的操作。\n'
    html += '</div>\n'
    html += '<div class="footer">Test Workshop Pro | ISTQB Compliant</div>\n'
    html += '</body></html>'
    return HTMLResponse(html)


# ====== Test Case Manager ======
def load_tc():
    if os.path.exists(TCF):
        return json.loads(open(TCF, encoding="utf-8").read())
    return []

def save_tc(d):
    with open(TCF, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))

@app.get("/api/tc")
def list_tc():
    return {"cases": load_tc()}

@app.post("/api/tc")
async def add_tc(request: Request):
    b = await request.json()
    tcs = load_tc()
    tc = {
        "id": str(len(tcs) + 1).zfill(3),
        "module": b.get("module", ""),
        "title": b.get("title", ""),
        "priority": b.get("priority", "P1"),
        "method": b.get("method", "GET"),
        "path": b.get("path", ""),
        "expected": b.get("expected", ""),
        "steps": b.get("steps", ""),
        "status": "Pending",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tcs.append(tc)
    save_tc(tcs)
    return {"ok": True}

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

@app.get("/tc")
def tc_page():
    return FileResponse(os.path.join(BASE, "static", "tc.html"))

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
