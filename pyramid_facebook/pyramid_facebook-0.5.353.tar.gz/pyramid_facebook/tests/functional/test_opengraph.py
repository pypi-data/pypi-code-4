from zope.interface import implementer

from pyramid_facebook.tests.functional import TestView


class TestOpenGraph(TestView):

    def setUp(self):
        self.define_virtual_goods()

    def define_virtual_goods(self):
        from pyramid_facebook import opengraph

        class PackCollection(object):

            __name__ = None
            __parent__ = None

            def __init__(self, request):
                self.children = {
                    'rainbows_pack': RainbowsCurrencyPack(self),
                }

            def __getitem__(self, key):
                return self.children[key]

        @implementer(opengraph.IResource)
        class RainbowsCurrencyPack(object):

            def __init__(self, parent):
                self.__name__ = 'rainbows_pack'
                self.__parent__ = parent

                self.prefixes = {
                    'product': 'http://ogp.me/ns/product#',
                }
                self.properties = {
                    'og:type': 'og:product',
                    'og:title': 'Rainbows Pack',
                    'og:description': 'Use Rainbows to play more',
                    'product:price': [
                        {'amount': '0.10', 'currency': 'CAD'},
                        {'amount': '0.15', 'currency': 'USD'},
                    ],
                }

        self.config.add_opengraph_collection(PackCollection, 'store/packs')

    def test_basic(self):
        resp = self.app.get('/test_canvas/store/packs/rainbows_pack',
                            status=200)

        lines = resp.body.splitlines()
        self.assertEqual(
            ['<head prefix="og: http://ogp.me/ns#',
             'fb: http://ogp.me/ns/fb#',
             'product: http://ogp.me/ns/product#',
             '">'],
            [line.strip() for line in lines[:4]])
        self.assertEqual('</head>', lines[-1])

        og_url = 'http://localhost/test_canvas/store/packs/rainbows_pack'

        for prop, expected in [
            ('fb:app_id', '1234567890'),
            ('og:type', 'og:product'),
            ('og:url', og_url),
            ('og:title', 'Rainbows Pack'),
            ('og:description', 'Use Rainbows to play more'),
          ]:
            value = resp.html.head.find('meta', property=prop)['content']
            self.assertEqual(expected, value)

    def test_url_with_query_string(self):
        resp = self.app.get(
            '/test_canvas/store/packs/rainbows_pack?promo=labor_day',
            status=200)

        self.assertEqual(
            resp.html.head.find('meta', property='og:url')['content'],
            'http://localhost/test_canvas/store/packs/rainbows_pack'
            '?promo=labor_day')

    def test_unknown_pack(self):
        self.app.get('/test_canvas/store/packs/unicorns_pack', status=404)

    def test_default_view(self):
        self.app.put('/test_canvas/store/packs/rainbows_pack', status=405)
