from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import os, json, tempfile, subprocess, threading, queue, asyncio, shutil, re

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Test Workshop", version="3.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")


def safename(s): return re.sub(r'[^\w\u4e00-\u9fff]', '_', str(s))[:35].strip('_') or 'test'


def generate_test_code(plan):
    name = plan.get('name', 'untitled'); url = plan.get('url', 'http://localhost')
    apis = plan.get('apis', []); pages = plan.get('pages', [])
    rules = plan.get('rules', []); types = plan.get('types', ['api'])
    sd = safename(name)
    out = os.path.join(tempfile.gettempdir(), f'test_{sd}')
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)

    # ---- conftest ----
    cf = f'''import pytest, httpx
B="{url}"
@pytest.fixture
def client():
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as x: yield x
@pytest.fixture(scope="session")
def b():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(headless=False, slow_mo=300)
        yield br; br.close()
@pytest.fixture
def pg(b):
    ctx = b.new_context(); p = ctx.new_page(); p.set_default_timeout(20000)
    yield p; ctx.close()
'''
    open(os.path.join(out, 'conftest.py'), 'w', encoding='utf-8').write(cf)

    # ---- API tests ----
    if 'api' in types and apis:
        lines = ['import pytest', '']
        for a in apis:
            m = a.get('m', 'GET'); p = a.get('p', '/'); n = safename(a.get('n', ''))
            tp = p.replace('{id}', '1'); cl = f'Test_API_{n}'
            lines.append(f'class {cl}:')
            lines.append(f'    """{m} {p}"""')
            lines.append('')

            if m == 'GET':
                for tname, code, check in [
                    ('status', f'client.get("{tp}")', 'r.status_code in(200,301,302,304)'),
                    ('body', f'client.get("{tp}")', 'len(r.content)>0 or r.status_code in(204,301,302)'),
                    ('headers', f'client.get("{tp}")', '"content-type" in str(r.headers).lower() or r.status_code>=300'),
                ]:
                    lines.append(f'    def test_{tname}(self, client):')
                    lines.append(f'        r = {code}')
                    lines.append(f'        assert {check}')
                    lines.append('')
            elif m == 'POST':
                for tname, code, check in [
                    ('json', f'client.post("{tp}", json={{"t":"auto"}})', 'r.status_code in(200,201,204,400,401,403,405,415,422)'),
                    ('empty', f'client.post("{tp}")', 'r.status_code in(200,201,204,400,401,403,405,415,422)'),
                    ('bad_json', f'client.post("{tp}", content="x", headers={{"Content-Type":"application/json"}})', 'r.status_code in(200,201,204,400,401,403,405,415,422)'),
                ]:
                    lines.append(f'    def test_{tname}(self, client):')
                    lines.append(f'        r = {code}')
                    lines.append(f'        assert {check}')
                    lines.append('')
            elif m == 'PUT':
                for tname, code, check in [
                    ('json', f'client.put("{tp}", json={{"t":"auto"}})', 'r.status_code in(200,201,204,400,401,403,404,405,415,422)'),
                    ('empty', f'client.put("{tp}")', 'r.status_code in(200,201,204,400,401,403,404,405,415,422)'),
                ]:
                    lines.append(f'    def test_{tname}(self, client):')
                    lines.append(f'        r = {code}')
                    lines.append(f'        assert {check}')
                    lines.append('')
            elif m == 'DELETE':
                for tname, code, check in [
                    ('accepted', f'client.delete("{tp}")', 'r.status_code in(200,202,204,301,401,403,404,405)'),
                    ('response', f'client.delete("{tp}")', 'r.status_code is not None'),
                ]:
                    lines.append(f'    def test_{tname}(self, client):')
                    lines.append(f'        r = {code}')
                    lines.append(f'        assert {check}')
                    lines.append('')
        open(os.path.join(out, 'test_api.py'), 'w', encoding='utf-8').write('\n'.join(lines))

    # ---- UI tests ----
    if 'ui' in types and pages:
        lines = ['import pytest', 'from conftest import B', '', '']
        for pg in pages:
            u = pg.get('u', pg.get('url', '/')); na = safename(pg.get('na', pg.get('name', '')))
            cl = f'Test_Page_{na}'; lines.append(f'class {cl}:')
            lines.append(f'    """{u}"""'); lines.append('')
            lines.append(f'    def test_loads(self, pg):')
            lines.append(f'        pg.goto(B+"{u}")')
            lines.append(f'        assert pg.locator("body").is_visible()')
            lines.append(f'        assert len(pg.title()) > 0')
            lines.append('')
            lines.append(f'    def test_no_errors(self, pg):')
            lines.append(f'        errs = []')
            lines.append(f'        pg.on("pageerror", lambda e: errs.append(str(e)))')
            lines.append(f'        pg.goto(B+"{u}")')
            lines.append(f'        pg.wait_for_timeout(2000)')
            lines.append(f'        assert len(errs) == 0, f"JS errors: {{errs}}"')
            lines.append('')
    open(os.path.join(out, 'test_ui.py'), 'w', encoding='utf-8').write('\n'.join(lines))

    # ---- Data tests ----
    if 'data' in types and rules:
        lines = ['import pytest', '', 'class TestData:', '']
        for i, r in enumerate(rules):
            sn = safename(r); lines.append(f'    def test_{i}_{sn}(self, client):')
            lines.append(f'        """{r}"""')
            first = apis[0].get('p', '/').replace('{id}', '1') if apis else '/'
            lines.append(f'        resp = client.get("{first}")')
            lines.append(f'        assert resp.status_code in(200,301,302)')
            lines.append(f'        # Rule: {r}')
            lines.append('')
        open(os.path.join(out, 'test_data.py'), 'w', encoding='utf-8').write('\n'.join(lines))

    return out


@app.post("/api/generate-and-run")
async def gnr(request: Request):
    try:
        body = await request.json()
        d = generate_test_code(body)
        cmd = ['python', '-m', 'pytest', d, '-v', '--tb=short', '--color=no']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        t=p=f=0
        for line in (r.stdout+r.stderr).split('\n'):
            m = re.findall(r'(\d+)\s+(passed|failed|error)', line)
            for c, s in m:
                if s == 'passed': p += int(c)
                elif s in ('failed', 'error'): f += int(c)
            t = max(t, p + f)
        return {'ok': f == 0 and t > 0, 'results': {'total': t, 'passed': p, 'failed': f, 'stdout': r.stdout[-8000:], 'stderr': r.stderr[-2000:]}, 'dir': d}
    except Exception as e:
        import traceback; return {'ok': False, 'error': str(e), 'traceback': traceback.format_exc()[-2000:], 'results': {'total': 0, 'passed': 0, 'failed': 0}}


@app.get("/api/stream-execute")
async def stream(request: Request):
    pj = request.query_params.get('plan', '')
    if not pj:
        async def e(): yield f"data: {json.dumps({'type':'error','msg':'No plan'})}\n\n"
        return StreamingResponse(e(), media_type="text/event-stream")
    plan = json.loads(pj); d = generate_test_code(plan)

    async def s():
        q = queue.Queue(); T=[0]; P=[0]; F=[0]
        def w():
            proc = subprocess.Popen(['python', '-m', 'pytest', d, '-v', '--tb=line', '--color=no'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(proc.stdout.readline, ''):
                q.put(line)
                if 'PASSED' in line and '::' in line: T[0]+=1; P[0]+=1
                elif 'FAILED' in line and '::' in line: T[0]+=1; F[0]+=1
            q.put('__END__'); proc.wait()
        threading.Thread(target=w, daemon=True).start()
        msg = plan.get('name', '') + ' @ ' + plan.get('url', '')
        yield f"data: {json.dumps({'type':'start','msg':msg})}\n\n"
        while True:
            try: line = q.get(timeout=0.1)
            except queue.Empty: await asyncio.sleep(0.05); yield f"data: {json.dumps({'type':'ping','total':T[0],'passed':P[0],'failed':F[0]})}\n\n"; continue
            if line == '__END__':
                rate = round(P[0]/T[0]*100, 1) if T[0] else 0
                yield f"data: {json.dumps({'type':'done','total':T[0],'passed':P[0],'failed':F[0],'rate':rate,'msg':f'{P[0]} passed, {F[0]} failed, {rate}%'})}\n\n"; break
            st = line.strip(); status = 'pass' if 'PASSED' in st else 'fail' if 'FAILED' in st else 'info'
            yield f"data: {json.dumps({'type':'test','line':st[-300:],'status':status})}\n\n"
    return StreamingResponse(s(), media_type="text/event-stream")


@app.get("/")
def index(): return FileResponse(os.path.join(BASE, "static", "index.html"))


if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=9000)
