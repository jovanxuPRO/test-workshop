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

    def test_mobile(self, c):
        """mobile: GET /"""
        r = c.get("/", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /"""
        r = c.get("/", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_首页HEAD:
    """ /"""

class Test_英文搜索:
    """GET /s?wd=hello"""

    def test_ok(self, c):
        """ok: GET /s?wd=hello"""
        r = c.get("/s?wd=hello")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=hello"""
        r = c.get("/s?wd=hello")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=hello"""
        r = c.get("/s?wd=hello")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=hello"""
        t0 = time.time(); r = c.get("/s?wd=hello"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=hello"""
        r = c.head("/s?wd=hello")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=hello"""
        r = c.get("/s?wd=hello?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET /s?wd=hello"""
        r = c.get("/s?wd=hello", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=hello"""
        r = c.get("/s?wd=hello", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_中文搜索:
    """GET /s?wd=测试"""

    def test_ok(self, c):
        """ok: GET /s?wd=测试"""
        r = c.get("/s?wd=测试")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=测试"""
        r = c.get("/s?wd=测试")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=测试"""
        r = c.get("/s?wd=测试")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=测试"""
        t0 = time.time(); r = c.get("/s?wd=测试"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=测试"""
        r = c.head("/s?wd=测试")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=测试"""
        r = c.get("/s?wd=测试?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET /s?wd=测试"""
        r = c.get("/s?wd=测试", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=测试"""
        r = c.get("/s?wd=测试", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_搜索第2页:
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

    def test_mobile(self, c):
        """mobile: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=test&pn=10"""
        r = c.get("/s?wd=test&pn=10", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_搜索第3页:
    """GET /s?wd=test&pn=20"""

    def test_ok(self, c):
        """ok: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=test&pn=20"""
        t0 = time.time(); r = c.get("/s?wd=test&pn=20"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=test&pn=20"""
        r = c.head("/s?wd=test&pn=20")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=test&pn=20"""
        r = c.get("/s?wd=test&pn=20", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_每页50条:
    """GET /s?wd=test&rn=50"""

    def test_ok(self, c):
        """ok: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET /s?wd=test&rn=50"""
        t0 = time.time(); r = c.get("/s?wd=test&rn=50"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET /s?wd=test&rn=50"""
        r = c.head("/s?wd=test&rn=50")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=test&rn=50"""
        r = c.get("/s?wd=test&rn=50", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_空关键词:
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

    def test_mobile(self, c):
        """mobile: GET /s?wd="""
        r = c.get("/s?wd=", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd="""
        r = c.get("/s?wd=", headers={"Accept":"application/json"})
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

    def test_mobile(self, c):
        """mobile: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET /s?wd=test&rsv_spt=1"""
        r = c.get("/s?wd=test&rsv_spt=1", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_POST搜索:
    """POST /s"""

    def test_ok(self, c):
        """ok: POST /s"""
        r = c.post("/s", json={"t":"test"})
        assert r.status_code < 500

    def test_empty(self, c):
        """empty: POST /s"""
        r = c.post("/s")
        assert r.status_code < 500

    def test_bad(self, c):
        """bad: POST /s"""
        r = c.post("/s", content="x", headers={"Content-Type":"application/json"})
        assert r.status_code < 500

    def test_form(self, c):
        """form: POST /s"""
        r = c.post("/s", data={"k":"v"})
        assert r.status_code < 500

class Test_Logo图片:
    """GET https://www.baidu.com/img/bd_logo1.png"""

    def test_ok(self, c):
        """ok: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET https://www.baidu.com/img/bd_logo1.png"""
        t0 = time.time(); r = c.get("https://www.baidu.com/img/bd_logo1.png"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.head("https://www.baidu.com/img/bd_logo1.png")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET https://www.baidu.com/img/bd_logo1.png"""
        r = c.get("https://www.baidu.com/img/bd_logo1.png", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_静态资源:
    """GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""

    def test_ok(self, c):
        """ok: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        t0 = time.time(); r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.head("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"""
        r = c.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png", headers={"Accept":"application/json"})
        assert r.status_code < 500

class Test_错误页面:
    """GET https://www.baidu.com/search/error.html"""

    def test_ok(self, c):
        """ok: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html")
        assert r.status_code in (200,301,302,304)

    def test_body(self, c):
        """body: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html")
        assert len(r.content) > 0 or r.status_code >= 300

    def test_type(self, c):
        """type: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html")
        assert "content-type" in str(r.headers).lower() or r.status_code >= 300

    def test_time(self, c):
        """time: GET https://www.baidu.com/search/error.html"""
        t0 = time.time(); r = c.get("https://www.baidu.com/search/error.html"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_head(self, c):
        """head: GET https://www.baidu.com/search/error.html"""
        r = c.head("https://www.baidu.com/search/error.html")
        assert r.status_code < 500

    def test_page(self, c):
        """page: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html?page=1")
        assert r.status_code < 500

    def test_mobile(self, c):
        """mobile: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html", headers={"User-Agent":"iPhone"})
        assert r.status_code < 500

    def test_json_accept(self, c):
        """json_accept: GET https://www.baidu.com/search/error.html"""
        r = c.get("https://www.baidu.com/search/error.html", headers={"Accept":"application/json"})
        assert r.status_code < 500
