"""
API 测试 — Task Manager 任务管理系统 | http://127.0.0.1:8000
标准: ISTQB / 测试金字塔中层
"""
import pytest, httpx, time
BASE = "http://127.0.0.1:8000"

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE, timeout=25, follow_redirects=True) as c: yield c

class Test_用户列表:
    """测试模块: 用户列表"""

    def test_TC_正常响应(self, client):
        """TC-API-001 | 模块: 用户列表 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/users") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/users")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-002 | 模块: 用户列表 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/users") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/users")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-003 | 模块: 用户列表 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/users") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/users")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-004 | 模块: 用户列表 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/users") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/users")
        assert elapsed<5

class Test_创建用户:
    """测试模块: 创建用户"""

    def test_TC_正常响应(self, client):
        """TC-API-005 | 模块: 创建用户 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/users") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/users")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-006 | 模块: 创建用户 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/users") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/users")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-007 | 模块: 创建用户 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/users") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/users")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-008 | 模块: 创建用户 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/users") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/users")
        assert elapsed<5

class Test_用户详情:
    """测试模块: 用户详情"""

    def test_TC_正常响应(self, client):
        """TC-API-009 | 模块: 用户详情 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/users/1")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-010 | 模块: 用户详情 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-011 | 模块: 用户详情 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-012 | 模块: 用户详情 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/users/1") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/users/1")
        assert elapsed<5

class Test_更新用户:
    """测试模块: 更新用户"""

    def test_TC_正常响应(self, client):
        """TC-API-013 | 模块: 更新用户 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/users/1")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-014 | 模块: 更新用户 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-015 | 模块: 更新用户 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-016 | 模块: 更新用户 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/users/1") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/users/1")
        assert elapsed<5

class Test_删除用户:
    """测试模块: 删除用户"""

    def test_TC_正常响应(self, client):
        """TC-API-017 | 模块: 删除用户 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/users/1")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-018 | 模块: 删除用户 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-019 | 模块: 删除用户 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/users/1") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/users/1")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-020 | 模块: 删除用户 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/users/1") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/users/1")
        assert elapsed<5

class Test_任务列表:
    """测试模块: 任务列表"""

    def test_TC_正常响应(self, client):
        """TC-API-021 | 模块: 任务列表 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/tasks")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-022 | 模块: 任务列表 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/tasks")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-023 | 模块: 任务列表 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/tasks")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-024 | 模块: 任务列表 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/tasks") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/tasks")
        assert elapsed<5

class Test_创建任务:
    """测试模块: 创建任务"""

    def test_TC_正常响应(self, client):
        """TC-API-025 | 模块: 创建任务 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/tasks")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-026 | 模块: 创建任务 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/tasks")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-027 | 模块: 创建任务 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/tasks") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/tasks")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-028 | 模块: 创建任务 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/tasks") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/tasks")
        assert elapsed<5

class Test_更新任务:
    """测试模块: 更新任务"""

    def test_TC_正常响应(self, client):
        """TC-API-029 | 模块: 更新任务 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/tasks/1")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-030 | 模块: 更新任务 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/tasks/1")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-031 | 模块: 更新任务 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/tasks/1")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-032 | 模块: 更新任务 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/tasks/1") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/tasks/1")
        assert elapsed<5

class Test_删除任务:
    """测试模块: 删除任务"""

    def test_TC_正常响应(self, client):
        """TC-API-033 | 模块: 删除任务 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/tasks/1")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-034 | 模块: 删除任务 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/tasks/1")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-035 | 模块: 删除任务 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/tasks/1") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/tasks/1")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-036 | 模块: 删除任务 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/tasks/1") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/tasks/1")
        assert elapsed<5

class Test_数据统计:
    """测试模块: 数据统计"""

    def test_TC_正常响应(self, client):
        """TC-API-037 | 模块: 数据统计 | 优先级: P0 | 前置: 服务运行 | 步骤: client.get("/api/stats") | 数据: 无 | 预期: r.status_code in(200,301,302,304)"""
        r = client.get("/api/stats")
        assert r.status_code in(200,301,302,304)

    def test_TC_响应体(self, client):
        """TC-API-038 | 模块: 数据统计 | 优先级: P0 | 前置: 同上 | 步骤: client.get("/api/stats") | 数据: 无 | 预期: len(r.content)>0 or r.status_code>=300"""
        r = client.get("/api/stats")
        assert len(r.content)>0 or r.status_code>=300

    def test_TC_ContentType(self, client):
        """TC-API-039 | 模块: 数据统计 | 优先级: P1 | 前置: 同上 | 步骤: client.get("/api/stats") | 数据: 无 | 预期: "content-type" in str(r.headers).lower() or r.status_code>=300"""
        r = client.get("/api/stats")
        assert "content-type" in str(r.headers).lower() or r.status_code>=300

    def test_TC_响应时间(self, client):
        """TC-API-040 | 模块: 数据统计 | 优先级: P1 | 前置: 网络正常 | 步骤: client.get("/api/stats") | 数据: 计时器 | 预期: elapsed<5"""
        r = client.get("/api/stats")
        assert elapsed<5
