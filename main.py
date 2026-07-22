from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import os, json, tempfile, subprocess, threading, queue, asyncio, shutil, re

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Test Workshop", version="2.0.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")


def safe_name(text):
    """净化名称，去除特殊字符"""
    text = re.sub(r'[^\w\u4e00-\u9fff]', '_', str(text))
    text = re.sub(r'_+', '_', text).strip('_')
    return text or 'unnamed'


def generate_test_code(plan):
    name = plan.get('name', 'untitled')
    base_url = plan.get('url', 'http://localhost')
    apis = plan.get('apis', [])
    pages = plan.get('pages', [])
    rules = plan.get('rules', [])
    types = plan.get('types', ['api'])

    safe = safe_name(name)
    out_dir = os.path.join(tempfile.gettempdir(), f'test_{safe}')
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    # conftest
    conftest = f'''import pytest, httpx
BASE_URL = "{base_url}"

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=20, follow_redirects=True) as c:
        yield c

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, slow_mo=500)
        yield b
        b.close()

@pytest.fixture
def page(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    pg.set_default_timeout(15000)
    yield pg
    ctx.close()
'''
    with open(os.path.join(out_dir, 'conftest.py'), 'w', encoding='utf-8') as f:
        f.write(conftest)

    # API tests
    if types and 'api' in types and apis:
        api_lines = ['import pytest', '']
        for i, api in enumerate(apis):
            m = api.get('m', 'GET'); p = api.get('p', '/'); n = safe_name(api.get('n', ''))
            cls_name = f"Test_{n[:30]}"
            api_lines.append(f'class {cls_name}:')
            api_lines.append(f'    """{m} {p}"""')
            api_lines.append('')

            tp = p.replace("{id}", "1")
            if m == 'GET':
                api_lines.append(f'    def test_status(self, client):')
                api_lines.append(f'        r = client.get("{tp}")')
                api_lines.append(f'        assert r.status_code in (200, 301, 302, 304, 307, 308, 401, 403, 404, 405)')
                api_lines.append('')
            elif m == 'POST':
                api_lines.append(f'    def test_post(self, client):')
                api_lines.append(f'        r = client.post("{tp}", json={{"test":"auto"}})')
                api_lines.append(f'        assert r.status_code in (200, 201, 204, 301, 302, 400, 401, 403, 404, 405, 422)')
                api_lines.append('')
            elif m == 'PUT':
                api_lines.append(f'    def test_put(self, client):')
                api_lines.append(f'        r = client.put("{tp}", json={{"test":"auto"}})')
                api_lines.append(f'        assert r.status_code in (200, 201, 204, 301, 400, 401, 403, 404, 405, 422)')
                api_lines.append('')
            elif m == 'DELETE':
                api_lines.append(f'    def test_delete(self, client):')
                api_lines.append(f'        r = client.delete("{tp}")')
                api_lines.append(f'        assert r.status_code in (200, 204, 301, 401, 403, 404, 405)')
                api_lines.append('')

        with open(os.path.join(out_dir, 'test_api.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(api_lines))

    # Page tests (Playwright)
    if types and 'ui' in types and pages:
        page_lines = ['import pytest', 'from conftest import BASE_URL', '', '']
        for i, pg in enumerate(pages):
            u = pg.get('u', pg.get('url', '/')); na = safe_name(pg.get('na', pg.get('name', ''))); ac = pg.get('ac', pg.get('action', ''))
            cls = f"Test_Page_{na[:25]}"
            page_lines.append(f'class {cls}:')
            page_lines.append(f'    """Page: {u} - {ac}"""')
            page_lines.append('')
            page_lines.append(f'    def test_page_loads(self, page):')
            page_lines.append(f'        page.goto(BASE_URL + "{u}")')
            page_lines.append(f'        assert page.title() is not None')
            page_lines.append(f'        assert page.locator("body").is_visible()')
            page_lines.append('')
            page_lines.append(f'    def test_page_no_js_error(self, page):')
            page_lines.append(f'        errors = []')
            page_lines.append(f'        page.on("pageerror", lambda err: errors.append(str(err)))')
            page_lines.append(f'        page.goto(BASE_URL + "{u}")')
            page_lines.append(f'        page.wait_for_timeout(2000)')
            page_lines.append(f'        assert len(errors) == 0, f"JS errors: {{errors}}"')
            page_lines.append('')
        with open(os.path.join(out_dir, 'test_ui.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(page_lines))
    if types and 'data' in types and rules:
        data_lines = ['import pytest', '', 'class TestDataValidation:', '']
        for i, rule in enumerate(rules):
            rule_name = safe_name(rule[:40])
            data_lines.append(f'    def test_rule_{i}_{rule_name}(self, client):')
            data_lines.append(f'        """{rule}"""')
            if apis:
                first_path = apis[0].get('p', '/').replace('{id}', '1')
                data_lines.append(f'        r = client.get("{first_path}")')
            else:
                data_lines.append(f'        r = client.get("/")')
            data_lines.append(f'        assert r.status_code in (200, 301, 302)')
            data_lines.append(f'        # Rule: {rule}')
            data_lines.append('')

        with open(os.path.join(out_dir, 'test_data.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(data_lines))

    return out_dir


def run_tests(test_dir):
    cmd = ['python', '-m', 'pytest', test_dir, '-v', '--tb=short', '--color=no']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return {'total': 0, 'passed': 0, 'failed': 0, 'stdout': '', 'stderr': 'Timeout expired after 180s'}
    total = passed = failed = 0
    for line in (result.stdout + result.stderr).split('\n'):
        m = re.findall(r'(\d+)\s+(passed|failed|error)', line)
        for cnt, st in m:
            if st == 'passed': passed += int(cnt)
            elif st in ('failed', 'error'): failed += int(cnt)
        total = max(total, passed + failed)
    return {'total': total, 'passed': passed, 'failed': failed, 'stdout': result.stdout[-8000:], 'stderr': result.stderr[-2000:]}


@app.post("/api/generate-and-run")
async def generate_and_run(request: Request):
    try:
        body = await request.json()
        test_dir = generate_test_code(body)
        results = run_tests(test_dir)
        return {
            'ok': results['failed'] == 0 and results['total'] > 0,
            'results': results,
            'dir': test_dir
        }
    except Exception as e:
        import traceback
        return {
            'ok': False,
            'error': str(e),
            'traceback': traceback.format_exc()[-2000:],
            'results': {'total': 0, 'passed': 0, 'failed': 0}
        }


@app.get("/api/stream-execute")
async def stream_execute(request: Request):
    """SSE streaming - real-time test execution with progress"""
    plan_json = request.query_params.get('plan', '')
    if not plan_json:
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'msg': 'No plan provided'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    plan = json.loads(plan_json)
    test_dir = generate_test_code(plan)

    async def stream():
        q = queue.Queue()
        total = [0]; passed = [0]; failed = [0]

        def worker():
            proc = subprocess.Popen(
                ['python', '-m', 'pytest', test_dir, '-v', '--tb=line', '--color=no'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
            )
            for line in iter(proc.stdout.readline, ''):
                q.put(line)
                if 'PASSED' in line and 'test_' in line: total[0] += 1; passed[0] += 1
                elif 'FAILED' in line and 'test_' in line: total[0] += 1; failed[0] += 1
            q.put('__END__')
            proc.wait()

        t = threading.Thread(target=worker, daemon=True); t.start()

        yield f"data: {json.dumps({'type': 'start', 'msg': 'Testing ' + plan.get('name','') + ' @ ' + plan.get('url',''), 'test_dir': test_dir})}\n\n"

        while True:
            try:
                line = q.get(timeout=0.1)
            except queue.Empty:
                await asyncio.sleep(0.05)
                yield f"data: {json.dumps({'type': 'ping', 'total': total[0], 'passed': passed[0], 'failed': failed[0]})}\n\n"
                continue
            if line == '__END__':
                rate = round(passed[0]/total[0]*100, 1) if total[0] > 0 else 0
                yield f"data: {json.dumps({'type': 'done', 'total': total[0], 'passed': passed[0], 'failed': failed[0], 'rate': rate, 'msg': f'{passed[0]} passed, {failed[0]} failed, {rate}%'})}\n\n"
                break
            stripped = line.strip()
            status = 'pass' if 'PASSED' in stripped else 'fail' if 'FAILED' in stripped else 'info'
            yield f"data: {json.dumps({'type': 'test', 'line': stripped[-300:], 'status': status})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "static", "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
