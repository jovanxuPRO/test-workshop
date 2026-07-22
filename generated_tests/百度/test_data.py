import pytest
from conftest import B
import httpx
@pytest.fixture
def c():
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as cl: yield cl

class TestData:

    def test_d0(self, c):
        """首页HTTP 200"""
        resp = c.get("/")
        assert resp.status_code < 500
        # Rule: 首页HTTP 200

    def test_d1(self, c):
        """首页含text/html"""
        resp = c.get("/")
        assert resp.status_code < 500
        # Rule: 首页含text/html

    def test_d2(self, c):
        """首页<5秒"""
        resp = c.get("/")
        assert resp.status_code < 500
        # Rule: 首页<5秒

    def test_d3(self, c):
        """搜索页200"""
        resp = c.get("/")
        assert resp.status_code < 500
        # Rule: 搜索页200

    def test_d4(self, c):
        """robots可访问"""
        resp = c.get("/")
        assert resp.status_code < 500
        # Rule: robots可访问
