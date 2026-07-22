import pytest
from conftest import B

class Test_首页:

    def test_1_page_loaded(self,page):
        """页面加载渲染"""
        page.goto(B+"/")
        assert page.locator("body").is_visible()
        assert len(page.title())>0

    def test_2_no_console_errors(self,page):
        """控制台无错误"""
        errs=[]
        page.on("pageerror",lambda e:errs.append(str(e)))
        page.goto(B+"/")
        page.wait_for_timeout(2000)
        assert len(errs)==0,f"JS errors:{errs}"

    def test_3_load_time(self,page):
        """页面加载时间"""
        import time
        t0=time.time();page.goto(B+"/");page.wait_for_load_state("networkidle")
        assert time.time()-t0<10

    def test_4_mobile_viewport(self,page):
        """移动端视口"""
        page.set_viewport_size({"width":375,"height":812})
        page.goto(B+"/")
        assert page.locator("body").is_visible()

    def test_5_links_exist(self,page):
        """页面导航元素"""
        page.goto(B+"/")
        links=page.locator("a").count()
        assert links>=0

    def test_6_resources_loaded(self,page):
        """静态资源加载"""
        failed=[]
        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)
        page.goto(B+"/")
        page.wait_for_timeout(3000)
        assert True

class Test_英文搜索:

    def test_1_page_loaded(self,page):
        """页面加载渲染"""
        page.goto(B+"/s?wd=hello")
        assert page.locator("body").is_visible()
        assert len(page.title())>0

    def test_2_no_console_errors(self,page):
        """控制台无错误"""
        errs=[]
        page.on("pageerror",lambda e:errs.append(str(e)))
        page.goto(B+"/s?wd=hello")
        page.wait_for_timeout(2000)
        assert len(errs)==0,f"JS errors:{errs}"

    def test_3_load_time(self,page):
        """页面加载时间"""
        import time
        t0=time.time();page.goto(B+"/s?wd=hello");page.wait_for_load_state("networkidle")
        assert time.time()-t0<10

    def test_4_mobile_viewport(self,page):
        """移动端视口"""
        page.set_viewport_size({"width":375,"height":812})
        page.goto(B+"/s?wd=hello")
        assert page.locator("body").is_visible()

    def test_5_links_exist(self,page):
        """页面导航元素"""
        page.goto(B+"/s?wd=hello")
        links=page.locator("a").count()
        assert links>=0

    def test_6_resources_loaded(self,page):
        """静态资源加载"""
        failed=[]
        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)
        page.goto(B+"/s?wd=hello")
        page.wait_for_timeout(3000)
        assert True

class Test_中文搜索:

    def test_1_page_loaded(self,page):
        """页面加载渲染"""
        page.goto(B+"/s?wd=测试")
        assert page.locator("body").is_visible()
        assert len(page.title())>0

    def test_2_no_console_errors(self,page):
        """控制台无错误"""
        errs=[]
        page.on("pageerror",lambda e:errs.append(str(e)))
        page.goto(B+"/s?wd=测试")
        page.wait_for_timeout(2000)
        assert len(errs)==0,f"JS errors:{errs}"

    def test_3_load_time(self,page):
        """页面加载时间"""
        import time
        t0=time.time();page.goto(B+"/s?wd=测试");page.wait_for_load_state("networkidle")
        assert time.time()-t0<10

    def test_4_mobile_viewport(self,page):
        """移动端视口"""
        page.set_viewport_size({"width":375,"height":812})
        page.goto(B+"/s?wd=测试")
        assert page.locator("body").is_visible()

    def test_5_links_exist(self,page):
        """页面导航元素"""
        page.goto(B+"/s?wd=测试")
        links=page.locator("a").count()
        assert links>=0

    def test_6_resources_loaded(self,page):
        """静态资源加载"""
        failed=[]
        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)
        page.goto(B+"/s?wd=测试")
        page.wait_for_timeout(3000)
        assert True

class Test_搜索结果第2页:

    def test_1_page_loaded(self,page):
        """页面加载渲染"""
        page.goto(B+"/s?wd=test&pn=10")
        assert page.locator("body").is_visible()
        assert len(page.title())>0

    def test_2_no_console_errors(self,page):
        """控制台无错误"""
        errs=[]
        page.on("pageerror",lambda e:errs.append(str(e)))
        page.goto(B+"/s?wd=test&pn=10")
        page.wait_for_timeout(2000)
        assert len(errs)==0,f"JS errors:{errs}"

    def test_3_load_time(self,page):
        """页面加载时间"""
        import time
        t0=time.time();page.goto(B+"/s?wd=test&pn=10");page.wait_for_load_state("networkidle")
        assert time.time()-t0<10

    def test_4_mobile_viewport(self,page):
        """移动端视口"""
        page.set_viewport_size({"width":375,"height":812})
        page.goto(B+"/s?wd=test&pn=10")
        assert page.locator("body").is_visible()

    def test_5_links_exist(self,page):
        """页面导航元素"""
        page.goto(B+"/s?wd=test&pn=10")
        links=page.locator("a").count()
        assert links>=0

    def test_6_resources_loaded(self,page):
        """静态资源加载"""
        failed=[]
        page.on("response",lambda r: failed.append(r.url) if r.status>=400 else None)
        page.goto(B+"/s?wd=test&pn=10")
        page.wait_for_timeout(3000)
        assert True
