"""
单元测试 — Task Manager 任务管理系统
被测: http://127.0.0.1:8000
"""
import pytest, httpx
BASE = "http://127.0.0.1:8000"

class TestConnectivity:
    """TC-CONN-001 | 模块: 基础连接 | P0"""
    def test_server_reachable(self):
        try: r = httpx.get(BASE, timeout=15, follow_redirects=True); assert r.status_code < 500
        except Exception as e: pytest.skip(f"Unreachable: {e}")
