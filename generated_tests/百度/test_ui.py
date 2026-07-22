import pytest
from conftest import B

class Test_首页:
    def test_load(self, page):
        page.goto(B + '/')
        assert page.locator('body').is_visible()
        assert len(page.title()) > 0

class Test_搜索结果:
    def test_load(self, page):
        page.goto(B + '/s?wd=test')
        assert page.locator('body').is_visible()
        assert len(page.title()) > 0
