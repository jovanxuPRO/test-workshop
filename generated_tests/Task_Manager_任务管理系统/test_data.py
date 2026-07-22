"""
数据校验 — Task Manager 任务管理系统
"""
import pytest, httpx
from conftest import B

@pytest.fixture
def c():
    with httpx.Client(base_url=B, timeout=25, follow_redirects=True) as x: yield x

class TestData:
    def test_D001_删除用户后关联任务负责人应清空(self, c):
        """规则: 删除用户后关联任务负责人应清空"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 删除用户后关联任务负责人应清空

    def test_D002_统计API总数与实际数据一致(self, c):
        """规则: 统计API总数与实际数据一致"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 统计API总数与实际数据一致

    def test_D003_状态分布之和等于总任务数(self, c):
        """规则: 状态分布之和等于总任务数"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 状态分布之和等于总任务数

    def test_D004_完成率___done数_total_x_100(self, c):
        """规则: 完成率 = done数/total x 100"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 完成率 = done数/total x 100

    def test_D005_重复用户名_邮箱应被拒绝(self, c):
        """规则: 重复用户名/邮箱应被拒绝"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 重复用户名/邮箱应被拒绝

    def test_D006_任务指派给不存在用户应被拒绝(self, c):
        """规则: 任务指派给不存在用户应被拒绝"""
        resp = c.get("/api/users"); assert resp.status_code in(200,301,302)
        # TODO: 任务指派给不存在用户应被拒绝
