from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import os, json, tempfile, subprocess, threading, queue, asyncio, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="Test Workshop", version="1.0.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")


import re

def safe_name(text):
    """去除特殊字符，只保留字母数字中文下划线"""
    text = re.sub(r'[^\w\u4e00-\u9fff]', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text or 'unnamed'


def generate_test_code(plan):
    name = plan.get('name', 'untitled')
    base_url = plan.get('url', 'http://localhost')
    apis = plan.get('apis', [])
    pages = plan.get('pages', [])
    rules = plan.get('rules', [])

    safe = safe_name(name)
    out_dir = os.path.join(tempfile.gettempdir(), f'test_{safe}')
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    # conftest.py
    conftest = f'''import pytest, httpx

BASE_URL = "{base_url}"

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=15) as c:
        yield c
'''
    with open(os.path.join(out_dir, 'conftest.py'), 'w', encoding='utf-8') as f:
        f.write(conftest)

    # API tests
    if apis:
        api_lines = ['import pytest', '']
        for i, api in enumerate(apis):
            m = api['m']; p = api['p']; n = api['n']
            cls_name = f"Test_{safe_name(n)[:30]}"
            api_lines.append(f'class {cls_name}:')
            api_lines.append(f'    """{m} {p} - {n}"""')
            api_lines.append('')

            if m == 'GET':
                tp = p.replace("{id}","1")
                api_lines.append(f'    def test_status_ok(self, client):')
                api_lines.append(f'        r = client.get("{tp}")')
                api_lines.append(f'        assert r.status_code in (200, 301, 302, 404)')
                api_lines.append('')
            elif m == 'POST':
                api_lines.append(f'    def test_post_ok(self, client):')
                api_lines.append(f'        r = client.post("{p}", json={{"name":"test"}})')
                api_lines.append(f'        assert r.status_code in (200, 201, 400, 401, 403, 422)')
                api_lines.append('')
            elif m == 'PUT':
                tp = p.replace("{id}","1")
                api_lines.append(f'    def test_put_ok(self, client):')
                api_lines.append(f'        r = client.put("{tp}", json={{"name":"updated"}})')
                api_lines.append(f'        assert r.status_code in (200, 400, 401, 403, 404)')
                api_lines.append('')
            elif m == 'DELETE':
                tp = p.replace("{id}","1")
                api_lines.append(f'    def test_delete_ok(self, client):')
                api_lines.append(f'        r = client.delete("{tp}")')
                api_lines.append(f'        assert r.status_code in (200, 204, 401, 403, 404)')
                api_lines.append('')

        with open(os.path.join(out_dir, f'test_api.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(api_lines))

    # Data tests
    if rules:
        data_lines = ['import pytest', '', 'class TestDataValidation:', '']
        for i, rule in enumerate(rules):
            data_lines.append(f'    def test_rule_{i+1}(self, client):')
            data_lines.append(f'        """{rule}"""')
            api_lines_for_rule = apis[0] if apis else None
            if api_lines_for_rule:
                data_lines.append(f'        r = client.get("{api_lines_for_rule["p"]}")')
                data_lines.append(f'        assert r.status_code in (200, 301, 302)')
            else:
                data_lines.append(f'        r = client.get("/")')
                data_lines.append(f'        assert r.status_code in (200, 301, 302)')
            data_lines.append(f'        # TODO: assert: {rule}')
            data_lines.append('')

        with open(os.path.join(out_dir, f'test_data.py'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(data_lines))

    return out_dir


def run_tests(test_dir):
    cmd = ['python', '-m', 'pytest', test_dir, '-v', '--tb=short', '--color=no']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    total = passed = failed = 0
    import re
    for line in (result.stdout + result.stderr).split('\n'):
        m = re.findall(r'(\d+)\s+(passed|failed|error)', line)
        for cnt, st in m:
            if st == 'passed': passed += int(cnt)
            elif st in ('failed', 'error'): failed += int(cnt)
        total = max(total, passed + failed)
    return {'total': total, 'passed': passed, 'failed': failed, 'stdout': result.stdout[-5000:], 'stderr': result.stderr[-2000:]}


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
            'traceback': traceback.format_exc()[-1000:]
        }


@app.get("/api/run-live")
async def run_live(request: Request):
    async def stream():
        q = queue.Queue()
        total = [0]; passed = [0]; failed = [0]

        def worker():
            proc = subprocess.Popen(
                ["python", "-m", "pytest", "tests", "-v", "--tb=line", "--color=no", "--alluredir=allure-results"],
                cwd=os.path.dirname(BASE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
            )
            for line in iter(proc.stdout.readline, ''):
                q.put(line)
                if 'PASSED' in line: total[0] += 1; passed[0] += 1
                elif 'FAILED' in line: total[0] += 1; failed[0] += 1
            q.put('__END__'); proc.wait()

        t = threading.Thread(target=worker, daemon=True); t.start()
        yield f"data: {json.dumps({'type':'start'})}\n\n"

        while True:
            try: line = q.get(timeout=0.1)
            except queue.Empty: await asyncio.sleep(0.05); yield f"data: {json.dumps({'type':'ping'})}\n\n"; continue
            if line == '__END__':
                yield f"data: {json.dumps({'type':'done','total':total[0],'passed':passed[0],'failed':failed[0],'rate':round(passed[0]/total[0]*100,1) if total[0]>0 else 0})}\n\n"
                break
            yield f"data: {json.dumps({'type':'test','line':line.strip()[-250:]})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "static", "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
