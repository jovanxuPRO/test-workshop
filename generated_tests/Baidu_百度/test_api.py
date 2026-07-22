"""
API 测试 — Baidu 百度 | https://www.baidu.com
标准: ISTQB / 测试金字塔中层
"""
import pytest, httpx, time
BASE = "https://www.baidu.com"

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE, timeout=25, follow_redirects=True) as c: yield c

class Test_百度首页:
    """测试模块: 百度首页"""

    def test_正常响应(self, client):
        """TC-API-001 | 模块: 百度首页 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-002 | 模块: 百度首页 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-003 | 模块: 百度首页 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-004 | 模块: 百度首页 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-005 | 模块: 百度首页 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-006 | 模块: 百度首页 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-007 | 模块: 百度首页 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-008 | 模块: 百度首页 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_搜索测试:
    """测试模块: 搜索测试"""

    def test_正常响应(self, client):
        """TC-API-009 | 模块: 搜索测试 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-010 | 模块: 搜索测试 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-011 | 模块: 搜索测试 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-012 | 模块: 搜索测试 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/s?wd=test"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-013 | 模块: 搜索测试 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-014 | 模块: 搜索测试 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-015 | 模块: 搜索测试 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-016 | 模块: 搜索测试 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_搜索分页:
    """测试模块: 搜索分页"""

    def test_正常响应(self, client):
        """TC-API-017 | 模块: 搜索分页 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-018 | 模块: 搜索分页 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-019 | 模块: 搜索分页 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-020 | 模块: 搜索分页 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/s?wd=test&pn=10"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-021 | 模块: 搜索分页 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-022 | 模块: 搜索分页 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-023 | 模块: 搜索分页 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-024 | 模块: 搜索分页 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_HEAD请求:
    """测试模块: HEAD请求"""

    def test_正常响应(self, client):
        """TC-API-025 | 模块: HEAD请求 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-026 | 模块: HEAD请求 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-027 | 模块: HEAD请求 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-028 | 模块: HEAD请求 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-029 | 模块: HEAD请求 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-030 | 模块: HEAD请求 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-031 | 模块: HEAD请求 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-032 | 模块: HEAD请求 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_POST首页:
    """测试模块: POST首页"""

    def test_正常响应(self, client):
        """TC-API-033 | 模块: POST首页 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-034 | 模块: POST首页 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-035 | 模块: POST首页 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-036 | 模块: POST首页 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-037 | 模块: POST首页 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-038 | 模块: POST首页 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-039 | 模块: POST首页 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-040 | 模块: POST首页 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_robots_txt:
    """测试模块: robots.txt"""

    def test_正常响应(self, client):
        """TC-API-041 | 模块: robots.txt | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-042 | 模块: robots.txt | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-043 | 模块: robots.txt | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-044 | 模块: robots.txt | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/robots.txt"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-045 | 模块: robots.txt | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-046 | 模块: robots.txt | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-047 | 模块: robots.txt | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-048 | 模块: robots.txt | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_favicon:
    """测试模块: favicon"""

    def test_正常响应(self, client):
        """TC-API-049 | 模块: favicon | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-050 | 模块: favicon | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-051 | 模块: favicon | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-052 | 模块: favicon | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/favicon.ico"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-053 | 模块: favicon | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-054 | 模块: favicon | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-055 | 模块: favicon | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-056 | 模块: favicon | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_搜索建议:
    """测试模块: 搜索建议"""

    def test_正常响应(self, client):
        """TC-API-057 | 模块: 搜索建议 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-058 | 模块: 搜索建议 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-059 | 模块: 搜索建议 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-060 | 模块: 搜索建议 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/s?wd=test&rsv_spt=1"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-061 | 模块: 搜索建议 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-062 | 模块: 搜索建议 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-063 | 模块: 搜索建议 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-064 | 模块: 搜索建议 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_错误页面:
    """测试模块: 错误页面"""

    def test_正常响应(self, client):
        """TC-API-065 | 模块: 错误页面 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-066 | 模块: 错误页面 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-067 | 模块: 错误页面 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-068 | 模块: 错误页面 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/error"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-069 | 模块: 错误页面 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-070 | 模块: 错误页面 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-071 | 模块: 错误页面 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-072 | 模块: 错误页面 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_静态资源:
    """测试模块: 静态资源"""

    def test_正常响应(self, client):
        """TC-API-073 | 模块: 静态资源 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-074 | 模块: 静态资源 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-075 | 模块: 静态资源 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-076 | 模块: 静态资源 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-077 | 模块: 静态资源 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-078 | 模块: 静态资源 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-079 | 模块: 静态资源 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-080 | 模块: 静态资源 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500

class Test_空搜索:
    """测试模块: 空搜索"""

    def test_正常响应(self, client):
        """TC-API-081 | 模块: 空搜索 | 优先级: P0 | 前置: 服务运行 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("{tp}")
        assert r.status_code in(200,301,302,304)

    def test_响应体非空(self, client):
        """TC-API-082 | 模块: 空搜索 | 优先级: P0 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("{tp}")
        assert len(r.content)>0 or r.status_code>=300

    def test_ContentType(self, client):
        """TC-API-083 | 模块: 空搜索 | 优先级: P1 | 前置: 同上 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("{tp}")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_响应时间_5s(self, client):
        """TC-API-084 | 模块: 空搜索 | 优先级: P1 | 前置: 网络正常 | 步骤:  | 数据: 计时器 | 预期: elapsed<5"""
        t0 = time.time(); r = client.get("/s?wd="); elapsed = time.time() - t0
        assert elapsed < 5

    def test_跟随重定向(self, client):
        """TC-API-085 | 模块: 空搜索 | 优先级: P2 | 前置: 可能有重定向 | 步骤: r = client.get("{tp}") | 数据: 无 | 预期: len(r.history)>=0"""
        r = client.get("{tp}")
        assert len(r.history)>=0

    def test_HEAD兼容(self, client):
        """TC-API-086 | 模块: 空搜索 | 优先级: P2 | 前置: 服务运行 | 步骤: r = client.head("{tp}") | 数据: 无 | 预期: r.status_code<500"""
        r = client.head("{tp}")
        assert r.status_code<500

    def test_分页参数(self, client):
        """TC-API-087 | 模块: 空搜索 | 优先级: P2 | 前置: 接口可能支持分页 | 步骤: r = client.get("{tp}?page=1&size=10") | 数据: page=1&size=10 | 预期: r.status_code<500"""
        r = client.get("{tp}?page=1&size=10")
        assert r.status_code<500

    def test_搜索参数(self, client):
        """TC-API-088 | 模块: 空搜索 | 优先级: P2 | 前置: 接口可能支持搜索 | 步骤: r = client.get("{tp}?q=test") | 数据: q=test | 预期: r.status_code<500"""
        r = client.get("{tp}?q=test")
        assert r.status_code<500
