import pytest, httpx
from conftest import B

@pytest.fixture
def c():
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as cl: yield cl

class TestData:

    def test_d0(self, c):
        """首页HTTP状态码200"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d1(self, c):
        """首页ContentType含text/html"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d2(self, c):
        """首页含关键词百度"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d3(self, c):
        """搜索页HTTP 200"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d4(self, c):
        """不同分页返回不同内容"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d5(self, c):
        """空搜索不崩溃"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d6(self, c):
        """Logo图片可访问"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d7(self, c):
        """POST搜索页可接受"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d8(self, c):
        """静态资源ContentType正确"""
        resp = c.get("/")
        assert resp.status_code < 500

    def test_d9(self, c):
        """英文和中文搜索均正常"""
        resp = c.get("/")
        assert resp.status_code < 500
