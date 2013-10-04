#:coding=utf8:

import re
from unittest import TestCase

from beproud.utils.html import (
    LOOSE_DOMAIN_RE,
    DOMAIN_RE,
    IP_ADDRESS_RE,
    URL_RE,
    DEFAULT_VALID_TAGS,
    DEFAULT_VALID_STYLES,
    urlize,
    sanitize_html,
)

class UrlReTest(TestCase):
    def test_loose_domain_re(self):
        domain_re = re.compile(LOOSE_DOMAIN_RE)
        self.assertEqual(domain_re.match("localhost").group(), 'localhost')
        self.assertTrue(domain_re.match("blah") is None)
        self.assertEqual(domain_re.match("beproud.jp").group(), 'beproud.jp')
        self.assertEqual(domain_re.match("dev-xxx.beproud.jp").group(), 'dev-xxx.beproud.jp')
        self.assertEqual(domain_re.match("dev_xxx.beproud.jp").group(), 'dev_xxx.beproud.jp')
        self.assertEqual(domain_re.match("dev_xxx.be_proud.j_p").group(), 'dev_xxx.be_proud.j_p')
        self.assertEqual(domain_re.match("www2.beproud.jp").group(), 'www2.beproud.jp')
        self.assertEqual(domain_re.match("www2.static.beproud.jp").group(), 'www2.static.beproud.jp')
        self.assertEqual(domain_re.match("www2.static.beproud.zcode").group(), 'www2.static.beproud.zcode')

    def test_domain_re(self):
        domain_re = re.compile(DOMAIN_RE)
        self.assertTrue(domain_re.match("localhost") is None)
        self.assertTrue(domain_re.match("blah") is None)
        self.assertEqual(domain_re.match("zcode.jp").group(), 'zcode.jp')
        self.assertEqual(domain_re.match("www2.zcode.jp").group(), 'www2.zcode.jp')
        self.assertEqual(domain_re.match("www2.static.zcode.jp").group(), 'www2.static.zcode.jp')
        self.assertEqual(domain_re.match("dev-xxx.beproud.jp").group(), 'dev-xxx.beproud.jp')
        self.assertTrue(domain_re.match("dev_xxx.beproud.jp") is None)
        self.assertEqual(domain_re.match("devxxx.bep_roud.jp").group(), 'devxxx.be')
        self.assertEqual(domain_re.match("devxxx.beproud.j_p").group(), 'devxxx.be')
        self.assertTrue(domain_re.match("www2.zcode") is None)

    def test_ip_address_re(self):
        ip_address_re = re.compile(IP_ADDRESS_RE)
        self.assertTrue(ip_address_re.match("localhost") is None)
        self.assertTrue(ip_address_re.match("blah") is None)
        self.assertTrue(ip_address_re.match("123.beproud.jp") is None)
        self.assertTrue(ip_address_re.match("123.148.224.249") is not None)
        self.assertTrue(ip_address_re.match("255.255.255.255") is not None)
        self.assertTrue(ip_address_re.match("123.148.294.226") is None)
        self.assertTrue(ip_address_re.match("123.999.224.249") is None)

    def test_url_re(self):
        url_re = re.compile(URL_RE)
        self.assertEquals(
            url_re.match("http://www.beproud.jp/company/?param=test#fragment").groups(),
            ('http', 'www.beproud.jp', 'www.beproud.jp', None, None, '/company/', 'param=test', 'fragment'),
        )

        self.assertEquals(
            url_re.match("http://www.beproud.jp:8000/company/").groups(),
            ('http', 'www.beproud.jp:8000', 'www.beproud.jp', None, '8000', '/company/', None, None),
        )

        self.assertEquals(
            url_re.match("http://www.beproud.jp:8000/company/?quer*?y=str#frag?m#ent").groups(),
            ('http', 'www.beproud.jp:8000', 'www.beproud.jp', None, '8000', '/company/', 'quer*?y=str', 'frag?m#ent'),
        )

        self.assertEquals(
            url_re.match("http://123.123.123.123:8000/company/?quer*?y=str#frag?m#ent").groups(),
            ('http', '123.123.123.123:8000', None, '123.123.123.123', '8000', '/company/', 'quer*?y=str', 'frag?m#ent'),
        )

        self.assertTrue(url_re.match("http://www.テスト.jp:8000/company/") is None)

class UrlizeTest(TestCase):

    def test_urlize(self):
        self.assertEqual(
            urlize(u'ペキペキ12月はカップル割り15％OFFです http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656'),
            u'ペキペキ12月はカップル割り15％OFFです <a href="http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656">http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656</a>',
        )

    def test_domain_check(self):
        self.assertEqual(
            urlize(u'このURL、http://beproud.jpビープラウドホームページ'),
            u'このURL、<a href="http://beproud.jp">http://beproud.jp</a>ビープラウドホームページ',
        )

    def test_attrs(self):
        self.assertEqual(
            urlize(u'ペキペキ12月はカップル割り15％OFFです http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656', attrs={'rel': 'nofollow'}),
            u'ペキペキ12月はカップル割り15％OFFです <a href="http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656" rel="nofollow">http://twitter.com/#!/PEKI_SHIBUYA/status/142081523179462656</a>',
        )

    def test_url_trim(self):
        self.assertEqual(
            urlize(u'このURL、http://beproud.jp/?query=strビープラウドホームページ', trim_url_limit=23),
            u'このURL、<a href="http://beproud.jp/?query=str">http://beproud.jp/?q...</a>ビープラウドホームページ',
        )


class HTMLSanitizationTest(TestCase):
    valid_tags = DEFAULT_VALID_TAGS
    valid_styles = DEFAULT_VALID_STYLES
    test_html = () 

    def test_html_sanitization(self):
        for html in self.test_html:
            sanitized_html = sanitize_html(
                html[0],
                valid_tags=self.valid_tags,
                valid_styles=self.valid_styles,
            )
            self.assertEqual(sanitized_html, html[1])

class TagStrippingTest(HTMLSanitizationTest):
    test_html = (
        (
            u'<b>This is a test</b>', 
            u'<b>This is a test</b>',
        ),
        (
            u'<script type="text/javascript">alert("DANGER!!");</script> Will Robinson',
            u'alert(&quot;DANGER!!&quot;); Will Robinson',
        ),
        (
            u'<a href="http://www.ianlewis.org/" rel="me" onclick="alert(\'woah!!\')">This is a test</a>',
            u'<a href="http://www.ianlewis.org/" rel="me">This is a test</a>',
        ),
        (
            u'<CRazY>Crazy Text</crazy>',
            u'Crazy Text',
        )
    )

class EntitiesTest(HTMLSanitizationTest):
    test_html = (
        (
            u'<b>Ian\'s Homepage</b>', 
            u'<b>Ian&apos;s Homepage</b>',
        ),
        (
            u'"I CaN HaZ SoMe < TeXt?"',
            u'&quot;I CaN HaZ SoMe &lt; TeXt?&quot;',
        ),
        (
            u'"I CaN HaZ SoMe <TeXt>?"',
            u'&quot;I CaN HaZ SoMe ?&quot;',
        ),
        (
            u'Ice Cream & &quot;Chocolate&quot;',
            u'Ice Cream &amp; &quot;Chocolate&quot;',
        )
    )

class CSSSanitizationTest(HTMLSanitizationTest):
    valid_tags = {
        'div': ('style',),
        'span': ('style',),
    }
    valid_styles = (
        "color",
        "font-weight",
        "width",
        "background-image",
    )
    test_html = (
        (
            u'<span style="color:#FFF;position:absolute;">My Homepage</span>', 
            u'<span style="color:#FFF;">My Homepage</span>', 
        ),
        (
            u'<span style="color:#FFF;position:absolute;font-weight:bold;">My Homepage</span>', 
            u'<span style="color:#FFF;font-weight:bold;">My Homepage</span>', 
        ),
        (
            u'<span style="color:#FFF;position:absolute   ">My Homepage</span>', 
            u'<span style="color:#FFF;">My Homepage</span>', 
        ),
        (
            u'<span style="  color:#FFF;  position:absolute;\tfont-weight:bold  ">My Homepage</span>', 
            u'<span style="color:#FFF;font-weight:bold;">My Homepage</span>', 
        ),
        (
            u'<span style="  color:#FFF;  position:absolute;\tfont-weight:bold;  aaaaa">My Homepage</span>', 
            u'<span style="color:#FFF;font-weight:bold;">My Homepage</span>', 
        ),
        (
            u'<span style="  color  : #FFF;  position:absolute;\tfont-weight:bold;  aaaaa">My Homepage</span>', 
            u'<span style="color:#FFF;font-weight:bold;">My Homepage</span>', 
        ),
        (
            u'<span style="border-width:5px;width:6px;border-left-width:10px">My Homepage</span>', 
            u'<span style="width:6px;">My Homepage</span>', 
        ),
        # CSS では、最後に出るスタイルが有効なので
        (
            u'<span style="width:5px;width:6px;">My Homepage</span>', 
            u'<span style="width:6px;">My Homepage</span>', 
        ),
        (
            u'<span style="WIDTH:5px;color:#FFF;">My Homepage</span>', 
            u'<span style="width:5px;color:#FFF;">My Homepage</span>', 
        ),
        (
            u'<span style="position:absolute">My Homepage</span>', 
            u'<span>My Homepage</span>', 
        ),
        (
            u'<span style="background-image:url(http://example.com/example.jpg);">My Homepage</span>', 
            u'<span style="background-image:url(http://example.com/example.jpg);">My Homepage</span>', 
        ),
    )

class ExtraHTMLTest(HTMLSanitizationTest):
    test_html = (
        (
            u'<input name=submit type=submit value=検索><span>Test</span>',
            u'<span>Test</span>',
        ),
    )

class NoFollowTest(TestCase):
    valid_tags = DEFAULT_VALID_TAGS
    valid_styles = DEFAULT_VALID_STYLES
    test_html = () 

    def test_nofollow(self):
        html = u'<a href="http://www.ianlewis.org/">This is a test</a>'
        sanitized_html = sanitize_html(html, valid_tags=self.valid_tags, add_nofollow=True)
        self.assertEqual(sanitized_html,
            u'<a href="http://www.ianlewis.org/" rel="nofollow">This is a test</a>')

        html = u'<a href="http://www.ianlewis.org/" rel="me">This is a test</a>'
        sanitized_html = sanitize_html(html, valid_tags=self.valid_tags, add_nofollow=True)
        self.assertEqual(sanitized_html,
            u'<a href="http://www.ianlewis.org/" rel="me nofollow">This is a test</a>')

    def test_nofollow_existing(self):
        html = u'<a href="http://www.ianlewis.org/" rel="me nofollow">This is a test</a>'
        sanitized_html = sanitize_html(html, valid_tags=self.valid_tags, add_nofollow=True)
        self.assertEqual(sanitized_html,
            u'<a href="http://www.ianlewis.org/" rel="me nofollow">This is a test</a>')

class SanitizeHtmlEncodingTest(TestCase):
    valid_tags = DEFAULT_VALID_TAGS

    def test_sanitize_html_encoding(self):
        html = u'<a href="http://www.ianlewis.org/">テストテスト</a>'.encode("cp932")
        sanitized_html = sanitize_html(html, valid_tags=self.valid_tags, encoding="cp932")
        self.assertEqual(sanitized_html,
            u'<a href="http://www.ianlewis.org/">テストテスト</a>')
