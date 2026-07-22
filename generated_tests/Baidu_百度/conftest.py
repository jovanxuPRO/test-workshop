"""测试配置"""
import pytest, httpx
B = "https://www.baidu.com"

@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p: br = p.chromium.launch(headless=False, slow_mo=300); yield br; br.close()

@pytest.fixture
def pg(browser):
    ctx = browser.new_context(); p = ctx.new_page(); p.set_default_timeout(20000); yield p; ctx.close()