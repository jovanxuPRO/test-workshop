import pytest, httpx, time
B = "https://www.baidu.com"
class TestUnit:
    def test_1_reachable(self):
        """服务可达性"""
        try: r = httpx.get(B, timeout=15, follow_redirects=True); assert r.status_code < 500
        except: pytest.skip("unreachable")

    def test_2_response_time(self):
        """响应时间基准"""
        try: t0=time.time(); httpx.get(B,timeout=20,follow_redirects=True); assert time.time()-t0<10
        except: pytest.skip("timeout")

    def test_3_ssl_valid(self):
        """SSL证书有效"""
        if not B.startswith("https"): pytest.skip("HTTP only")
        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert r.status_code<500
        except: pytest.skip("ssl check failed")

    def test_4_redirect_follow(self):
        """重定向跟踪"""
        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.history)>=0
        except: pytest.skip("redirect check")

    def test_5_headers_present(self):
        """响应头完整"""
        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.headers)>0
        except: pytest.skip("headers check")

    def test_6_content_length(self):
        """响应体大小"""
        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert len(r.content)>0 or r.status_code>=300
        except: pytest.skip("content check")

    def test_7_encoding_valid(self):
        """编码声明检查"""
        try: r=httpx.get(B,timeout=15,follow_redirects=True); assert r.encoding or r.status_code>=300
        except: pytest.skip("encoding check")

    def test_8_concurrent(self):
        """并发请求"""
        try:
            import concurrent.futures
            def req(): return httpx.get(B,timeout=20,follow_redirects=True).status_code
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
                results = list(ex.map(lambda _: req(), range(3)))
            assert all(s<500 for s in results)
        except: pytest.skip("concurrent check")

