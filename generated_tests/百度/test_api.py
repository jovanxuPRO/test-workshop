import pytest, time

class Test_首页:
    """GET /"""

    def test_ok(self, c):
        """ok: GET /"""
        r = c.get("/")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /"""
        r = c.get("/")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /"""
        r = c.get("/")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /"""
        t0 = time.time(); r = c.get("/"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /"""
        r = c.head("/")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /"""
        r = c.get("/?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /"""
        r = c.get("/", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /"""
        r = c.get("/", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /"""
        r = c.get("/", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_搜索:
    """GET /s?wd=test"""

    def test_ok(self, c):
        """ok: GET /s?wd=test"""
        r = c.get("/s?wd=test")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=test"""
        r = c.get("/s?wd=test")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=test"""
        r = c.get("/s?wd=test")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=test"""
        t0 = time.time(); r = c.get("/s?wd=test"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=test"""
        r = c.head("/s?wd=test")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=test"""
        r = c.get("/s?wd=test?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /s?wd=test"""
        r = c.get("/s?wd=test", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /s?wd=test"""
        r = c.get("/s?wd=test", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /s?wd=test"""
        r = c.get("/s?wd=test", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_搜索分页:
    """GET /s?wd=test&pn=10"""

    def test_ok(self, c):
        """ok: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=test&pn=10"""
        t0 = time.time(); r = c.get("/s?wd=test&pn=10"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=test&pn=10"""
        r = c.head("/s?wd=test&pn=10")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_HEAD:
    """ /"""

class Test_POST测试:
    """POST /"""

    def test_ok(self, c):
        """ok: POST /"""
        r = c.post("/", json={"t":"test"})
        assert r.status_code < 500

    def test_empty(self, c):
        """empty: POST /"""
        r = c.post("/")
        assert r.status_code < 500

    def test_bad_json(self, c):
        """bad_json: POST /"""
        r = c.post("/", content="x", headers={"Content-Type":"application/json"})
        assert r.status_code < 500

    def test_form(self, c):
        """form: POST /"""
        r = c.post("/", data={"k":"v"})
        assert r.status_code < 500

    def test_xml(self, c):
        """xml: POST /"""
        r = c.post("/", content="<x/>", headers={"Content-Type":"application/xml"})
        assert r.status_code < 500

class Test_robots:
    """GET /robots.txt"""

    def test_ok(self, c):
        """ok: GET /robots.txt"""
        r = c.get("/robots.txt")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /robots.txt"""
        r = c.get("/robots.txt")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /robots.txt"""
        r = c.get("/robots.txt")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /robots.txt"""
        t0 = time.time(); r = c.get("/robots.txt"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /robots.txt"""
        r = c.head("/robots.txt")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /robots.txt"""
        r = c.get("/robots.txt?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /robots.txt"""
        r = c.get("/robots.txt", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /robots.txt"""
        r = c.get("/robots.txt", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /robots.txt"""
        r = c.get("/robots.txt", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_favicon:
    """GET /favicon.ico"""

    def test_ok(self, c):
        """ok: GET /favicon.ico"""
        r = c.get("/favicon.ico")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /favicon.ico"""
        r = c.get("/favicon.ico")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /favicon.ico"""
        r = c.get("/favicon.ico")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /favicon.ico"""
        t0 = time.time(); r = c.get("/favicon.ico"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /favicon.ico"""
        r = c.head("/favicon.ico")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /favicon.ico"""
        r = c.get("/favicon.ico?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /favicon.ico"""
        r = c.get("/favicon.ico", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /favicon.ico"""
        r = c.get("/favicon.ico", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /favicon.ico"""
        r = c.get("/favicon.ico", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_搜索建议:
    """GET /s?wd=test&rsv_spt=1"""

    def test_ok(self, c):
        """ok: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=test&rsv_spt=1"""
        t0 = time.time(); r = c.get("/s?wd=test&rsv_spt=1"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=test&rsv_spt=1"""
        r = c.head("/s?wd=test&rsv_spt=1")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500

class Test_空搜索:
    """GET /s?wd="""

    def test_ok(self, c):
        """ok: GET /s?wd="""
        r = c.get("/s?wd=")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd="""
        r = c.get("/s?wd=")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd="""
        r = c.get("/s?wd=")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd="""
        t0 = time.time(); r = c.get("/s?wd="); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd="""
        r = c.head("/s?wd=")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd="""
        r = c.get("/s?wd=?page=1")
        assert r.status_code < 500

    def test_mobile_ua(self, c):
        """mobile_ua: GET /s?wd="""
        r = c.get("/s?wd=", headers={"User-Agent":"Mozilla/5.0 (iPhone)"})
        assert r.status_code < 500

    def test_accept_json(self, c):
        """accept_json: GET /s?wd="""
        r = c.get("/s?wd=", headers={"Accept":"application/json"})
        assert r.status_code < 500

    def test_gzip(self, c):
        """gzip: GET /s?wd="""
        r = c.get("/s?wd=", headers={"Accept-Encoding":"gzip, deflate"})
        assert r.status_code < 500
