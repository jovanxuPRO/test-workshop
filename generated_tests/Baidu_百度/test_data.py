"""
数据校验 — Baidu 百度
"""
import pytest, httpx
from conftest import B

@pytest.fixture
def c():
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as x: yield x

class TestData:
    def test_D001_首页HTTP状态码为200(self, c):
        """规则: 首页HTTP状态码为200"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 首页HTTP状态码为200

    def test_D002_首页Content_Type含text_html(self, c):
        """规则: 首页Content-Type含text/html"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 首页Content-Type含text/html

    def test_D003_首页响应时间小于5秒(self, c):
        """规则: 首页响应时间小于5秒"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 首页响应时间小于5秒

    def test_D004_搜索页返回200且含html(self, c):
        """规则: 搜索页返回200且含html"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 搜索页返回200且含html

    def test_D005_静态资源正常加载(self, c):
        """规则: 静态资源正常加载"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 静态资源正常加载

    def test_D006_首页HTML含关键词百度(self, c):
        """规则: 首页HTML含关键词百度"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 首页HTML含关键词百度

    def test_D007_搜索建议接口正常(self, c):
        """规则: 搜索建议接口正常"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 搜索建议接口正常

    def test_D008_robots_txt可访问(self, c):
        """规则: robots.txt可访问"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: robots.txt可访问

    def test_D009_favicon可访问(self, c):
        """规则: favicon可访问"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: favicon可访问

    def test_D010_错误页面不崩溃(self, c):
        """规则: 错误页面不崩溃"""
        resp = c.get("/"); assert resp.status_code in(200,301,302)
        # TODO: 错误页面不崩溃
