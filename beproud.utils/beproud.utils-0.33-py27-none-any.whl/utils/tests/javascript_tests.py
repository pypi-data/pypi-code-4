# vim:fileencoding=utf-8
from datetime import datetime,date,time
from unittest import TestCase

from beproud.utils.javascript import (
    json,
    escapejs_json,
    force_js,
    SafeJSONEncoder,
)

class JavascriptUtilsTestCase(TestCase):

    def test_escapejs_json(self):
        self.assertEqual(escapejs_json(u"<テスト>"), u'\\u003cテスト\\u003e')
        self.assertEqual(escapejs_json(u"Q&A"), u"Q\\u0026A")
        self.assertEqual(escapejs_json(u"データ"), u"データ")
        self.assertEqual(escapejs_json("<test>"), u"\\u003ctest\\u003e")
        self.assertEqual(escapejs_json(u"テスト & エスケープ"), u"テスト \\u0026 エスケープ")

    def test_force_js(self):
        self.assertEqual(force_js({"msg": u"メッセージ"}), '{"msg": "\\u30e1\\u30c3\\u30bb\\u30fc\\u30b8"}')
        self.assertEqual(force_js(datetime(2009, 12, 22, 16, 35, 02)), '"2009-12-22 16:35:02"') 
        self.assertEqual(force_js(date(2009, 12, 22)), '"2009-12-22"') 
        self.assertEqual(force_js(time(16, 35, 02)), '"16:35:02"')

        self.assertEqual(force_js(u"<title>"), u'"\\u003ctitle\\u003e"')

    def test_datetime(self):
        from datetime import datetime,date,time
        self.assertEqual(force_js({"msg": u"メッセージ"}), '{"msg": "\\u30e1\\u30c3\\u30bb\\u30fc\\u30b8"}')
        self.assertEqual(force_js(datetime(2009, 12, 22, 16, 35, 02)), '"2009-12-22 16:35:02"') 
        self.assertEqual(force_js(date(2009, 12, 22)), '"2009-12-22"') 
        self.assertEqual(force_js(time(16, 35, 02)), '"16:35:02"')

    def test_decimal(self):
        from decimal import Decimal
        self.assertEqual(force_js(Decimal("5")), '5')
        self.assertEqual(force_js({"dec": Decimal("1.5")}), '{"dec": 1.5}')

    def test_force_js_type(self):
        self.assertEqual(force_js("", "bool"), "false")
        self.assertEqual(force_js("5", "int"), '5')
        self.assertEqual(force_js("test", "array"), '["t", "e", "s", "t"]')
        self.assertEqual(force_js(5, "string"), '"5"')

    def test_safe_json_encoder(self):
        data = {
            "title": "<title>",
            "datetime": datetime(2009, 2, 19, 10, 22),
        }
        self.assertEqual(
            json.dumps(data, cls=SafeJSONEncoder),
            u'{"datetime": "2009-02-19 10:22:00", "title": "\\u003ctitle\\u003e"}',
        )
