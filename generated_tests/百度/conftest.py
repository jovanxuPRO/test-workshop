import pytest, httpx
B = "https://www.baidu.com"
@pytest.fixture
def c():
    h = {"User-Agent":"Mozilla/5.0"}
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True, headers=h) as cl:
        yield cl
@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(headless=False, slow_mo=300)
        yield br; br.close()
@pytest.fixture
def page(browser):
    ctx = browser.new_context()
    pg = ctx.new_page(); pg.set_default_timeout(20000)
    yield pg; ctx.close()
