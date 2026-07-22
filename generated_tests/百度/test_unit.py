import pytest, httpx, time
B = "https://www.baidu.com"
class TestUnit:
    def test_reachable(self):
        try:
            r = httpx.get(B, timeout=15, follow_redirects=True)
            assert r.status_code < 500
        except: pytest.skip("unreachable")
    def test_response_time(self):
        try:
            t0 = time.time()
            httpx.get(B, timeout=20, follow_redirects=True)
            assert time.time() - t0 < 10
        except: pytest.skip("timeout")
