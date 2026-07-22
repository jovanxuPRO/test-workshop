"""
UI 测试 — Task Manager 任务管理系统
"""
import pytest
from conftest import B

class Test_Page_test:
    def test_页面可访问(self, pg):
        """场景: 页面可访问"""
        pg.goto(B+"/"); assert pg.locator("body").is_visible()

    def test_无JS错误(self, pg):
        """场景: 无JS错误"""
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.goto(B+"/"); pg.wait_for_timeout(2000); assert len(errs)==0, f"JS:{errs}"

    def test_标题非空(self, pg):
        """场景: 标题非空"""
        pg.goto(B+"/"); assert len(pg.title())>0

class Test_Page_test:
    def test_页面可访问(self, pg):
        """场景: 页面可访问"""
        pg.goto(B+"/users-page"); assert pg.locator("body").is_visible()

    def test_无JS错误(self, pg):
        """场景: 无JS错误"""
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.goto(B+"/users-page"); pg.wait_for_timeout(2000); assert len(errs)==0, f"JS:{errs}"

    def test_标题非空(self, pg):
        """场景: 标题非空"""
        pg.goto(B+"/users-page"); assert len(pg.title())>0

class Test_Page_test:
    def test_页面可访问(self, pg):
        """场景: 页面可访问"""
        pg.goto(B+"/tasks-page"); assert pg.locator("body").is_visible()

    def test_无JS错误(self, pg):
        """场景: 无JS错误"""
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.goto(B+"/tasks-page"); pg.wait_for_timeout(2000); assert len(errs)==0, f"JS:{errs}"

    def test_标题非空(self, pg):
        """场景: 标题非空"""
        pg.goto(B+"/tasks-page"); assert len(pg.title())>0
