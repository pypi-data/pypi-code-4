import unittest

from collective.ploneseltest.testcase import SeleniumPloneLayer
from kreagroup.jsi18n.tests.base import KreaGroupJSi18nSeleniumTestCase

KREAGROUP_JSI18N_JS_DIGESTS = (# kreagroup.jsi18n 1.0.0
                               '6582c09723ded68d47615d44c2b825db937b0ed391020f6d4e2fd39f4ca011cdbc84b21bb5b330e15f216c8dae4f94c64068f7d859b405887d75c6fed7a72d63',)
JARN_JSI18N_JS_DIGESTS = (# jarn.jsi18n 1.0
                          '20f9cf3f5454743fadb4f2d0ec5f5def756550dc12aff4c58f41c3e46e229e7e46cef097dc1981a314cfa1e4fbaa473e4f6191e39e28ac65f55f1a6255558013',)

class Layer(SeleniumPloneLayer):
    pass

class TestDependencies(KreaGroupJSi18nSeleniumTestCase):

    layer = Layer

    def test_kreagroup_jsi18n_js(self):
        self.open("/++resource++jsi18n.js")
        self.wait()
        jsi18n_js_content = self.selenium.get_html_source()
        import hashlib
        m = hashlib.sha512()
        m.update(jsi18n_js_content)
        digest = m.hexdigest()
        self.assertTrue(digest in KREAGROUP_JSI18N_JS_DIGESTS,
                        digest + "\n" + jsi18n_js_content)


    # @remark
    # The following lines can be added to prefs.js of the selenium firefox
    # profile to ensure the cache is empty when we run these two tests...
    # Otherwise, the first test will pass, the second will take stuff from
    # the cache and fail...
    #
    # // @added
    # user_pref("browser.cache.disk.enable", false);
    # user_pref("browser.cache.memory.enable", false);
    # user_pref("browser.cache.offline.enable", false);
    # user_pref("network.http.use-cache", false);
    #    def test_uninstall_kreagroup_jsi18n_js(self):
    # 
    # but this also affects other tests, so we don't use the settings above, 
    # neither we run this test...
    #def test_uninstall_kreagroup_jsi18n_js(self):
    #    self.uninstall_package()
    #
    #    self.open("/++resource++jsi18n.js")
    #    self.wait()
    #    jsi18n_js_content = self.selenium.get_html_source()
    #    import hashlib
    #    m = hashlib.sha512()
    #    m.update(jsi18n_js_content)
    #    digest = m.hexdigest()
    #    self.assertTrue(digest in JARN_JSI18N_JS_DIGESTS,
    #                    digest + "\n" + jsi18n_js_content)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDependencies))
    return suite