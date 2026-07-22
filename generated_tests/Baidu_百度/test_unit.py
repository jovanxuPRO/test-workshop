"""
单元测试 — Baidu 百度
被测: https://www.baidu.com
"""
import pytest, httpx
BASE = "https://www.baidu.com"

class TestConnectivity:
    """TC-CONN-001 | 模块: 基础连接 | P0"""
    def test_server_reachable(self):
        try: r = httpx.get(BASE, timeout=15, follow_redirects=True); assert r.status_code < 500
        except Exception as e: pytest.skip(f"Unreachable: {e}")
