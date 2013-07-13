import flask
import functools
import itertools
import unittest
import werkzeug.routing
from flaskext.ypaginate import Pagination

app = flask.Flask(__name__)

def ypaginate_request_context(fn):
    '''
    Decorator which wraps a test method around an app.request_context to enable testing
    '''
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with app.test_request_context('#', method='GET'):
            fn(*args, **kwargs)
    return wrapper

def url_context_wrapper(url):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            @app.route(url)
            def url_context_wrapper_view():
                pass
            fn(*args, **kwargs)
        return wrapper
    return deco

@app.route('/ep/page/<page>/sa/<someKey>')
def endpoint_args_page_var():
    pass

@app.route('/ep/noPage/<someKey>')
def endpoint_viewargs_page_var():
    pass

@app.route('/ep/page/<page>/perPage/<perPage>/<key>')
def endpoint_args_page_perPage():
    pass

@app.route('/ep/m/<mickey>/m/<mouse>/<key>')
def endpoint_args_mickey_mouse():
    pass

@app.route('/ep/<gun>/what/<ship>')
def endpoint_args_gun_ship():
    pass

class TestPagination(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @ypaginate_request_context
    def test_total_pages(self):
        p = Pagination(total=70, perPage=10, endpoint='#')
        self.assertEqual(7, p.total_pages)
        p = Pagination(total=80, perPage=7, endpoint='#')
        self.assertEqual(12, p.total_pages)

    @ypaginate_request_context
    def test_has_prev(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=2, endpoint='#')
        self.assertEqual(True, p.has_prev)
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=1, endpoint='#')
        self.assertEqual(False, p.has_prev)

    @ypaginate_request_context
    def test_has_next(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=3, total=70,
                perPage=10, endpoint='#')
        self.assertEqual(True, p.has_next)
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=3, total=30,
                perPage=10, endpoint='#')
        self.assertEqual(False, p.has_next)

    @ypaginate_request_context
    def test_pageUrl(self):
        # default page separators
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=4, total=100,
                perPage=10, endpoint='/static/players')
        self.assertEqual('/static/players/page/4/perPage/10', p.pageUrl(4))
        # url ends with '/'
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=4, total=100,
                perPage=10, endpoint='/static/players/')
        self.assertEqual('/static/players/page/4/perPage/10', p.pageUrl(4))
        # custom page separators
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=2, total=144,
                perPage=12, pageSep='ss',
                perPageSep='khhT', endpoint='http://www.google.com/smth')
        self.assertEqual('http://www.google.com/smth/ss/5/khhT/12',
            p.pageUrl(5))

    @url_context_wrapper('/test/args/<arg1>/stuff/<item>/vvv/xyz/<int:fbuid>')
    def test_args(self):
        with app.test_request_context('/test/args/arg1Val/stuff/bottle/vvv/xyz/8164?next=http://www.google.com&hi=bye'):
            p = Pagination()
            d = {
                'arg1': 'arg1Val',
                'item': 'bottle',
                'fbuid': 8164,
                'next': 'http://www.google.com',
                'hi': 'bye',
            }
            self.assertEqual(d, p.args)

        # 'page' key in request.view_args
        with app.test_request_context('/test/args/5/stuff/view/vvv/xyz/772?x=coursera&page=52&bat=tab'):
            p = Pagination()
            d = {
                'arg1': '5',
                'item': 'view',
                'fbuid': 772,
                'x': 'coursera',
                'bat': 'tab',
            }
            self.assertEqual(d, p.args)

        # 'page' key in request.args
        with app.test_request_context('/ep/page/64/sa/dfhhs?x=y&a=b'):
            p = Pagination()
            d = {
                'someKey': 'dfhhs',
                'x': 'y',
                'a': 'b',
            }
            self.assertEqual(d, p.args)

        # 'page' key in both request.args and request.view_args
        with app.test_request_context('/ep/page/32/sa/aaaa?car=star&page=56&cdr=cond&g=j'):
            p = Pagination()
            d = {
                'someKey': 'aaaa',
                'car': 'star',
                'cdr': 'cond',
                'g': 'j',
            }
            self.assertEqual(d, p.args)

    def test_args__mode_fixed(self):
        # default 'page' and 'perPage'
        with app.test_request_context('/ep/page/13/perPage/14/google?x=y&fail=good'):
            p = Pagination(mode=Pagination.MODE_FIXED)
            d = {
                'key': 'google',
                'x': 'y',
                'fail': 'good',
            }
            self.assertEqual(d, p.args)
        # pageSep = mickey
        # perPage = mouse
        with app.test_request_context('/ep/m/124/m/45/facebook?apple=orange&past=present'):
            p = Pagination(mode=Pagination.MODE_FIXED, pageSep='mickey',
                    perPageSep='mouse')
            d = {
                'key': 'facebook',
                'apple': 'orange',
                'past': 'present',
            }
            self.assertEqual(d, p.args)
        # pageSep = mouse, perPageSep = mickey; present in request.view_args too
        with app.test_request_context('/ep/m/13/m/5/yahoo?hi=fer&g=k&mickey=minney&mouse=mice&kid=do'):
            p = Pagination(mode=Pagination.MODE_FIXED, pageSep='mouse',
                    perPageSep='mickey')
            d = {
                'key': 'yahoo',
                'hi': 'fer',
                'g': 'k',
                'kid': 'do',
            }
            self.assertEqual(d, p.args)
        # endpoint kwarg supplied
        with app.test_request_context('/ep/page/34/perPage/50/car?batman=joker&yeoman=grunt'):
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_page_perPage')
            d = {
                'key': 'car',
                'batman': 'joker',
                'yeoman': 'grunt',
            }
            self.assertEqual(d, p.args)
        # endpoint kwarg supplied, pageSep = gun, perPageSep = ship
        with app.test_request_context('/ep/page/12/perPage/5/man?gun=fight&ship=race&whats=app'):
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun', perPageSep='ship')
            d = {
                'page': '12',
                'perPage': '5',
                'key': 'man',
                'whats': 'app',
            }
            self.assertEqual(d, p.args)

    @ypaginate_request_context
    def test_prev_page(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=3, total=80,
                perPage=20, endpoint='#')
        self.assertEqual(Pagination.prevPageHtml.format(
            p.pageUrl(2), Pagination.prevLabel), p.prev_page)
        # custom prevLabel
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=5, total=70, perPage=7,
                prevLabel='PREV', endpoint='#')
        self.assertEqual(Pagination.prevPageHtml.format(
            p.pageUrl(4), 'PREV'), p.prev_page)
        # no prev_page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=1, total=60, perPage=6,
                endpoint='#')
        self.assertEqual(Pagination.disabledPageHtml.format(
            Pagination.prevLabel), p.prev_page)
        # no prev_page, custom prevLabel
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=1, total=60, perPage=6,
                prevLabel='myPrevPage', endpoint='#')
        self.assertEqual(Pagination.disabledPageHtml.format(
            'myPrevPage'), p.prev_page)

    def test_classic_prev_page(self):
        with app.test_request_context('/ep/page/1/sa/first?bkey=fbxy'):
            # has previous page
            p = Pagination(page=5, total=90, perPage=18)
            self.assertEqual(
                Pagination.prevPageHtml.format(
                    '/ep/page/4/sa/first?bkey=fbxy',
                    Pagination.prevLabel),
                p.prev_page)
        with app.test_request_context('/ep/page/32/sa/alien?j=b'):
            # has previous page but on page 2, so in the Pagination.prev_page
            # property, the 'page' variable becomes None, and page=None
            # gets passed as a key-value pair to url_for, which causes a
            # werkzeug.routing.BuildError
            p = Pagination(page=2, total=75, perPage=5)
            with self.assertRaises(werkzeug.routing.BuildError) as cm:
                p.prev_page
        with app.test_request_context('/ep/noPage/gad?a=b'):
            # no previous page, but endpoint does not have 'page' variable
            p = Pagination(page=2, total=75, perPage=5)
            self.assertEqual(
                Pagination.prevPageHtml.format(
                    '/ep/noPage/gad?a=b',
                    Pagination.prevLabel
                ),
                p.prev_page
            )
        with app.test_request_context('/ep/noPage/sx?ast=123'):
            # Page 1, no previous page, endpoint does not have 'page' variable
            p = Pagination(page=1, total=85, perPage=5)
            self.assertEqual(
                Pagination.disabledPageHtml.format(Pagination.prevLabel),
                p.prev_page
            )

    def test_prev_page__fixed(self):
        with app.test_request_context('/ep/page/4/perPage/5/good?y=u'):
            # has previous page
            p = Pagination(mode=Pagination.MODE_FIXED, page=3, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.prevPageHtml.format(
                    '/ep/page/2/perPage/10/good?y=u',
                    p.prevLabel
                ),
                p.prev_page
            )
        with app.test_request_context('/ep/m/4/m/12/xyz?abba=baab'):
            # has previous page, pageSep = mouse, perPageSep = mickey
            p = Pagination(mode=Pagination.MODE_FIXED, page=4, total=200,
                    perPage=10, pageSep='mouse', perPageSep='mickey')
            self.assertEqual(
                Pagination.prevPageHtml.format(
                    '/ep/m/10/m/3/xyz?abba=baab',
                    p.prevLabel
                ),
                p.prev_page
            )
        with app.test_request_context('/ep/page/5/perPage/10/abc?xyz=123'):
            # no previous page
            p = Pagination(mode=Pagination.MODE_FIXED, page=1, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.disabledPageHtml.format(p.prevLabel),
                p.prev_page
            )
        # endpoint supplied; page = ship, perPage = gun
        with app.test_request_context('/ep/page/4/perPage/17/wave?gun=aa&ship=bb'):
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='ship',
                    perPageSep='gun', page=4, perPage=17, total=200)
            baseUrl = '/ep/17/what/3?'
            args = ['key=wave', 'page=4', 'perPage=17']
            possibleUrls = \
                map(lambda x: Pagination.prevPageHtml.format(
                                  baseUrl + '&'.join(x),
                                  p.prevLabel
                              ),
                    list(itertools.permutations(args)))
            self.assertTrue(p.prev_page in possibleUrls)
            # no previous page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun',
                    perPageSep='ship', page=1, perPage=17, total=200)
            self.assertEqual(
                Pagination.disabledPageHtml.format(p.prevLabel),
                p.prev_page
            )

    @ypaginate_request_context
    def test_next_page(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=10, total=300,
                perPage=10, endpoint='#')
        self.assertEqual(Pagination.nextPageHtml.format(
            p.pageUrl(11), Pagination.nextLabel), p.next_page)
        # custom nextLabel
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=10, total=300,
                perPage=10, nextLabel='nextPage', endpoint='#')
        self.assertEqual(Pagination.nextPageHtml.format(
            p.pageUrl(11), 'nextPage'), p.next_page)
        # no next_page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=15, total=300,
                perPage=20, endpoint='#')
        self.assertEqual(Pagination.disabledPageHtml.format(
            Pagination.nextLabel), p.next_page)
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=15, total=300,
                perPage=20, nextLabel='NNNPPP', endpoint='#')
        self.assertEqual(Pagination.disabledPageHtml.format(
            'NNNPPP'), p.next_page)

    def test_classic_next_page(self):
        '''Tests old behavior of Pagination.next_page'''
        with app.test_request_context('/ep/page/58/sa/blah?col=here'):
            # has next page
            p = Pagination(page=5, total=90, perPage=9)
            self.assertEqual(
                Pagination.nextPageHtml.format(
                    '/ep/page/6/sa/blah?col=here',
                    Pagination.nextLabel
                ),
                p.next_page
            )
            # custom nextPage label
            p = Pagination(page=5, total=90, perPage=9, nextLabel='NEXTP')
            self.assertEqual(
                Pagination.nextPageHtml.format(
                    '/ep/page/6/sa/blah?col=here',
                    'NEXTP'
                ),
                p.next_page
            )
            # no more next page
            p = Pagination(page=30, total=90, perPage=3)
            self.assertEqual(
                Pagination.disabledPageHtml.format(Pagination.nextLabel),
                p.next_page
            )
            # no more next page + custom label
            p = Pagination(page=30, total=90, perPage=3, nextLabel='GG412')
            self.assertEqual(
                Pagination.disabledPageHtml.format('GG412'),
                p.next_page
            )

    def test_next_page__fixed(self):
        with app.test_request_context('/ep/page/41/perPage/12/sdf?hat=cat'):
            p = Pagination(mode=Pagination.MODE_FIXED, page=10, total=80,
                    perPage=2)
            self.assertEqual(
                Pagination.nextPageHtml.format(
                    '/ep/page/11/perPage/2/sdf?hat=cat',
                    p.nextLabel
                ),
                p.next_page
            )
            # no next page
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=20)
            self.assertEqual(
                Pagination.disabledPageHtml.format(p.nextLabel),
                p.next_page
            )
        with app.test_request_context('/ep/m/40/m/5/yam?nyan=cat'):
            # pageSep = mickey, perPageSep = mouse
            p = Pagination(mode=Pagination.MODE_FIXED, page=13, total=500,
                    perPage=5, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                Pagination.nextPageHtml.format(
                    '/ep/m/14/m/5/yam?nyan=cat',
                    p.nextLabel
                ),
                p.next_page
            )
        # endpoint supplied; page = gun, perPage = ship
        with app.test_request_context('/ep/page/32/perPage/10/bower?ufo=false&gun=s&ship=z'):
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', page=14, total=500,
                    perPage=20, pageSep='gun', perPageSep='ship')
            args = [
                'page=32', 'perPage=10', 'key=bower', 'ufo=false'
            ]
            baseUrl = '/ep/15/what/20?'
            possibleUrls = \
                map(lambda x:
                        Pagination.prevPageHtml.format(
                            baseUrl + '&'.join(x),
                            p.nextLabel
                        ),
                    list(itertools.permutations(args)))
            self.assertTrue(p.next_page in possibleUrls)
            # no next page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', page=10, total=200,
                    perPage=20, pageSep='gun', perPageSep='ship')
            self.assertEqual(
                Pagination.disabledPageHtml.format(p.nextLabel),
                p.next_page
            )

    @ypaginate_request_context
    def test_active_page(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, perPage=15, endpoint='#')
        self.assertEqual(Pagination.activePageHtml.format('page', 3,
            'perPage', 15, 3), p.active_page(3))
        # custom separators
        p = Pagination(mode=Pagination.MODE_SIMPLE, perPage=20, pageSep='pgs',
                perPageSep='emghhS', endpoint='#')
        self.assertEqual(Pagination.activePageHtml.format('pgs', 10,
            'emghhS', 20, 10), p.active_page(10))

    @ypaginate_request_context
    def test_first_page(self):
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=1, endpoint='#')
        self.assertEqual(p.active_page(1), p.first_page)
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=2, endpoint='#')
        self.assertEqual(Pagination.linkHtml.format(p.pageUrl(1), 1),
            p.first_page)

    def test_first_page_classic(self):
        with app.test_request_context('/ep/noPage/myVal?war=craft'):
            # has previous page
            p = Pagination(page=13, total=140, perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format('/ep/noPage/myVal?war=craft', 1),
                p.first_page
            )
            # no previous page
            p = Pagination(page=1, total=100, perPage=10)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(1),
                p.first_page
            )

    def test_first_page__fixed(self):
        with app.test_request_context('/ep/page/5/perPage/10/humid?desert=storm'):
            # has previous
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/page/1/perPage/10/humid?desert=storm',
                    1
                ),
                p.first_page
            )
            # no previous page
            p = Pagination(mode=Pagination.MODE_FIXED, page=1, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(1),
                p.first_page
            )
        with app.test_request_context('/ep/m/32/m/5/food?chicken=rice'):
            # pageSep = mouse, perPageSep = mickey
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10, pageSep='mouse', perPageSep='mickey')
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/m/10/m/1/food?chicken=rice',
                    1
                ),
                p.first_page
            )
        with app.test_request_context('/ep/page/4/perPage/25/turn?high=heels&wear=socks'):
            # endpoint supplied, pageSep = gun, perPageSep = ship
            # has previous page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', page=2, perPage=50,
                    total=100, pageSep='gun', perPageSep='ship')
            args = [
                'page=4', 'perPage=25', 'key=turn', 'high=heels', 'wear=socks'
            ]
            baseUrl = '/ep/1/what/50?'
            possibleUrls = \
                map(lambda x:
                        Pagination.linkHtml.format(
                            baseUrl + '&'.join(x),
                            1
                        ),
                    list(itertools.permutations(args)))
            self.assertTrue(p.first_page in possibleUrls)
            # no previous page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', page=1, perPage=50,
                    total=100, pageSep='gun', perPageSep='ship')
            self.assertEqual(
                Pagination.classicActivePageHtml.format(1),
                p.first_page
            )

    @ypaginate_request_context
    def test_last_page(self):
        # has 8 pages, now on page 7
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=7, perPage=16,
                total=128, endpoint='#')
        self.assertEqual(Pagination.linkHtml.format(
                p.pageUrl(p.total_pages), p.total_pages),
            p.last_page)
        # on last page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=6, perPage=20,
                total=120, endpoint='#')
        self.assertEqual(p.active_page(6), p.last_page)
        # exceeds last page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=8, perPage=20,
                total=100, endpoint='#')
        self.assertEqual(p.active_page(5), p.last_page)

    def test_last_page_classic(self):
        with app.test_request_context('/ep/page/53/sa/cl?big=star'):
            # has next page
            p = Pagination(page=41, total=200, perPage=2)
            self.assertEqual(
                Pagination.linkHtml.format('/ep/page/100/sa/cl?big=star',
                    100
                ),
                p.last_page
            )
            # no next page
            p = Pagination(page=40, total=200, perPage=5)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(40),
                p.last_page
            )

    def test_last_page__fixed(self):
        with app.test_request_context('/ep/page/13/perPage/20/someK?alfred=nobel'):
            # has next page
            p = Pagination(mode=Pagination.MODE_FIXED, page=13, total=400,
                    perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/page/40/perPage/10/someK?alfred=nobel',
                    40
                ),
                p.last_page
            )
            # no next page
            p = Pagination(mode=Pagination.MODE_FIXED, page=13, total=260,
                    perPage=20)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(13),
                p.last_page
            )
            # page given exceeds last page
            p = Pagination(mode=Pagination.MODE_FIXED, page=13, total=238,
                    perPage=20)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(12),
                p.last_page
            )
        with app.test_request_context('/ep/m/5/m/22/magic?fun=place'):
            # pageSep = mickey, perPageSep = mouse
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=220,
                    perPage=22, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/m/10/m/22/magic?fun=place',
                    10
                ),
                p.last_page
            )
        with app.test_request_context('/ep/page/5/perPage/30/monster?yy=tt'):
            # endpoint given, pageSep = mickey, perPageSep = mouse
            # has next page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_mickey_mouse', pageSep='mickey',
                    perPageSep='mouse', page=52, perPage=4, total=1024)
            baseUrl = '/ep/m/256/m/4/monster?'
            args = ['page=5', 'perPage=30', 'yy=tt']
            possibleUrls = \
                map(lambda x:
                        Pagination.linkHtml.format(
                            baseUrl + '&'.join(x),
                            256
                        ),
                    list(itertools.permutations(args)))
            self.assertTrue(p.last_page in possibleUrls)
            # no next page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_mickey_mouse', pageSep='mickey',
                    perPageSep='mouse', page=52, perPage=4, total=207)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(52),
                p.last_page
            )

    @ypaginate_request_context
    def test_single_page(self):
        # page is < 0
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=5, total=100,
                perPage=10, endpoint='#')
        self.assertEqual(p.first_page, p.single_page(0))
        # page > total pages
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=10, total=90,
                perPage=10)
        self.assertEqual(p.last_page, p.single_page(10))
        # supplied page is current page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=5, total=100,
                perPage=10, endpoint='#')
        self.assertEqual(p.active_page(5), p.single_page(5))
        # supplied page = 1
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=3, total=100,
                perPage=10, endpoint='#')
        self.assertEqual(p.first_page, p.single_page(1))
        # supplied page = last page
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=3, perPage=20,
                total=80, endpoint='#')
        self.assertEqual(p.last_page, p.single_page(4))
        # none of the above
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=4, perPage=25,
                total=200, endpoint='#')
        self.assertEqual(Pagination.linkHtml.format(p.pageUrl(6), 6),
            p.single_page(6))

    def test_single_page_classic(self):
        # page supplied to single_page function is same as
        # page given to Pagination
        with app.test_request_context('/ep/page/30/sa/aaa'):
            # page supplied to pagination is same page passed to
            # p.single_page method
            p = Pagination(page=32, total=500, perPage=10)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(32),
                p.single_page(32)
            )
            # not first page, not last page, supplied page different from
            # pagination page
            p = Pagination(page=45, total=500, perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format('/ep/page/32/sa/aaa', 32),
                p.single_page(32)
            )
        with app.test_request_context('/ep/noPage/KSDf'):
            # page <= 0
            p = Pagination(page=2, total=100, perPage=10)
            self.assertEqual(p.first_page, p.single_page(0))
            # page > total pages
            p = Pagination(page=6, total=100, perPage=20)
            self.assertEqual(p.last_page, p.single_page(6))
            # single_page(1), has_prev = True
            p = Pagination(page=32, total=500, perPage=10)
            self.assertEqual(p.first_page, p.single_page(1))
            # single_page(1), has_prev = False
            p = Pagination(page=1, total=500, perPage=10)
            self.assertEqual(p.first_page, p.single_page(1))
            # last page
            p = Pagination(page=50, total=500, perPage=10)
            self.assertEqual(p.last_page, p.single_page(50))
            # otherwise
            p = Pagination(page=30, total=500, perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format('/ep/noPage/KSDf?page=32', 32),
                p.single_page(32)
            )

    def test_single_page__fixed(self):
        with app.test_request_context('/ep/page/4/perPage/10/football?beats=it'):
            # page <= 0
            p = Pagination(mode=Pagination.MODE_FIXED, page=4, total=100,
                    perPage=10)
            self.assertEqual(p.first_page, p.single_page(-1))
            # page > total pages
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(p.last_page, p.single_page(11))
            # page == self.page
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(5),
                p.single_page(5)
            )
            # page == 1
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(
                p.first_page,
                p.single_page(1)
            )
            # page == p.total_pages
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(
                p.last_page,
                p.single_page(10)
            )
            # otherwise
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10)
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/page/7/perPage/10/football?beats=it',
                    7
                ),
                p.single_page(7)
            )
        with app.test_request_context('/ep/m/4/m/10/strong?weak=strong'):
            # same tests as above, but
            # pageSep = mickey, perPageSep = mouse

            # page == self.page
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                Pagination.classicActivePageHtml.format(5),
                p.single_page(5)
            )
            # page == 1
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                p.first_page,
                p.single_page(1)
            )
            # page == p.total_pages
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                p.last_page,
                p.single_page(10)
            )
            # otherwise
            p = Pagination(mode=Pagination.MODE_FIXED, page=5, total=100,
                    perPage=10, pageSep='mickey', perPageSep='mouse')
            self.assertEqual(
                Pagination.linkHtml.format(
                    '/ep/m/7/m/10/strong?weak=strong',
                    7
                ),
                p.single_page(7)
            )
        with app.test_request_context('/ep/page/12/perPage/10/fb?uid=1234&mage=wars'):
            # endpoint specified, pageSep = gun, perPageSep = ship
            # page == self.page
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun',
                    perPageSep='ship', page=20, perPage=20, total=500)
            self.assertEqual(
                Pagination.classicActivePageHtml.format(20),
                p.single_page(20)
            )
            # page == 1
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun',
                    perPageSep='ship', page=20, perPage=20, total=500)
            self.assertEqual(p.first_page, p.single_page(1))
            # page == p.total_pages
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun',
                    perPageSep='ship', page=20, perPage=20, total=500)
            self.assertEqual(p.last_page, p.single_page(25))
            # otherwise
            p = Pagination(mode=Pagination.MODE_FIXED,
                    endpoint='endpoint_args_gun_ship', pageSep='gun',
                    perPageSep='ship', page=20, perPage=20, total=500)
            baseUrl = '/ep/23/what/20?'
            args = ['page=12', 'perPage=10', 'key=fb', 'uid=1234', 'mage=wars']
            possibleUrls = \
                map(lambda x:
                        Pagination.linkHtml.format(
                            baseUrl + '&'.join(x),
                            23
                        ),
                    list(itertools.permutations(args)))
            self.assertTrue(p.single_page(23) in possibleUrls)

    @ypaginate_request_context
    def test_pages__total_pages_lte_2_innerWindow_plus_1(self):
        # 7 pages, on page 3, innerWindow = 2
        p = Pagination(page=4, perPage=10, total=70, innerWindow=3, outerWindow=2)
        self.assertEqual(list(xrange(1,8)), p.pages)

    @ypaginate_request_context
    def test_pages__winTo_gt_total_pages__winFrom_lte_ow_plus_1__winTo_gte_total_pages_minus_ow(self):
        # 1. end of middle section exceeds total pages
        # 2. left section overlaps with middle section
        # 3. right section touches/overlaps with middle section (doesnt matter due to 1)
        #
        #
        #             -ow
        #   -----mid-----
        # ow-
        # 1 2 3 4 5 6 7 8
        p = Pagination(page=6, innerWindow=3, outerWindow=1, total=80,
                perPage=10)
        self.assertEqual(8, p.total_pages)
        self.assertEqual(list(xrange(1, 9)), p.pages)

    @ypaginate_request_context
    def test_pages__winTo_gt_total_pages__winFrom_gt_ow_plus_1__winTo_gte_total_pages_minus_ow(self):
        # 1. end of middle section exceeds total pages
        # 2. left section does NOT overlap with middle section
        # 3. right section overlaps with middle section (doesnt matter due to 1)
        #
        #                 v
        #         -----mid-----
        # ow-               -ow
        # 1 2 3 4 5 6 7 8 9 0 1
        p = Pagination(page=9, innerWindow=3, outerWindow=1, total=121,
                perPage=11)
        self.assertEqual([1,2,None,5,6,7,8,9,10,11], p.pages)

    @ypaginate_request_context
    def test_pages__winTo_lte_total_pages__winFrom_gt_ow_plus_1__winTo_lt_total_pages_minus_ow(self):
        # 1. end of middle section does NOT exceed total pages
        # 2. left section does NOT touch/border with middle section
        # 3. right section does NOT touch/border with middle section
        #
        # ow-   ---mid---     -ow
        # 1 2 3 4 5 6 7 8 9 0 1 2
        p = Pagination(page=6, innerWindow=2, outerWindow=1, total=120, perPage=10)
        self.assertEqual([1,2,None,4,5,6,7,8,None,11,12], p.pages)

    @ypaginate_request_context
    def test_pages__winTo_lte_total_pages__winFrom_gt_ow_plus_1__winTo_gte_total_pages_minus_ow(self):
        # 1. end of middle section does NOT exceed total pages
        # 2. left section does NOT touch/border with middle section
        # 3. right section touches(borders) with middle section
        #
        # ow---     ---mid--- ---ow
        # 1 2 3 4 5 6 7 8 9 0 1 2 3
        p = Pagination(page=8, innerWindow=2, outerWindow=2, total=130,
                perPage=10)
        self.assertEqual([1,2,3,None,6,7,8,9,10,11,12,13], p.pages)
        # 1. end of middle section does NOT exceed total pages
        # 2. left section does NOT touch/border with middle section
        # 3. right section overlaps with middle section
        #
        #           ---mid---
        # ow---             ---ow
        # 1 2 3 4 5 6 7 8 9 0 1 2
        p = Pagination(page=8, innerWindow=2, outerWindow=2, total=120,
                perPage=10)
        self.assertEqual([1,2,3,None,6,7,8,9,10,11,12], p.pages)

    @ypaginate_request_context
    def test_pages__winTo_lte_total_pages__winFrom_lte_ow_plus_1__winTo_lt_total_pages_minus_ow(self):
        # 1. end of middle section does NOT exceed total pages
        # 2. left section overlaps with middle section
        # 3. right section does NOT touch/overlap with middle section
        #
        #     v
        # ---------
        # ow-         -ow
        # 1 2 3 4 5 6 7 8
        p = Pagination(page=3, innerWindow=2, outerWindow=1, total=80,
                perPage=10)
        self.assertEqual(8, p.total_pages)
        self.assertEqual([1,2,3,4,5,None,7,8], p.pages)
        # 1. end of middle section does NOT exceed total pages
        # 2. left section touches(borders) middle section
        # 3. right section does NOT touch/overlap with middle section
        # ow--- -----   -----     ---ow
        #             V
        # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
        p = Pagination(page=7, innerWindow=3, outerWindow=2, total=150,
                perPage=10)
        self.assertEqual([1,2,3,4,5,6,7,8,9,10,None,13,14,15], p.pages)

    @ypaginate_request_context
    def test_pages__winTo_lte_total_pages__winFrom_lte_ow_plus_1__winTo_gte_total_pages_minus_ow(self):
        # 1. end of middle section does NOT exceed total pages
        # 2. left section touches(borders) with middle section
        # 3. right section touches(borders) with middle section
        #
        #           v
        # ow--- ---mid--- ---ow
        # 1 2 3 4 5 6 7 8 9 0 1
        p = Pagination(page=6, innerWindow=2, outerWindow=2, total=110,
                perPage=10)
        self.assertEqual(list(xrange(1, 12)), p.pages)
        # 1. end of middle section does NOT exceed total pages
        # 2. left section touches(borders) with middle section
        # 3. right section overlaps with middle section
        #
        #           v
        #       ---mid---
        # ow---         ---ow
        # 1 2 3 4 5 6 7 8 9 0
        p = Pagination(page=6, innerWindow=2, outerWindow=2, total=80,
                perPage=8)
        self.assertEqual(list(xrange(1, 11)), p.pages)
        # 1. end of middle section does NOT exceed total pages
        # 2. left section overlaps with middle section
        # 3. right section touches(borders) with middle section
        #
        #       v
        #   ---mid---
        # ow---       ---ow
        # 1 2 3 4 5 6 7 8 9
        p = Pagination(page=4, innerWindow=2, outerWindow=2, total=81,
                perPage=9)
        self.assertEqual(list(xrange(1, 10)), p.pages)
        # 1. end of middle section does NOT exceed total pages
        # 2. left section overlaps with middle section
        # 3. right section overlaps with middle section
        #
        #       v
        #   ---mid---
        # ow---     ---ow
        # 1 2 3 4 5 6 7 8
        p = Pagination(page=4, innerWindow=2, outerWindow=2, total=64,
                perPage=8)
        self.assertEqual(list(xrange(1, 9)), p.pages)

    @ypaginate_request_context
    def test_links(self):
        # total_pages <= 1
        p = Pagination(page=1, total=10, perPage=10)
        self.assertEqual('', p.links)
        # no linkSize, no alignment, has gap
        #
        # ow-     ---mid--- ow-
        # 1 2 3 4 5 6 7 8 9 0 1
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=7, innerWindow=2,
                outerWindow=1, total=110, perPage=10, endpoint='#')
        linkStr = Pagination.linkCss.format('', ' pagination-centered')
        linkStr += p.prev_page
        linkStr += p.single_page(1) + p.single_page(2) + Pagination.gapMarker
        for i in xrange(5, 12):
            linkStr += p.single_page(i)
        linkStr += p.next_page
        linkStr += '</ul></div>'
        self.assertEqual(linkStr, p.links)
        # has linkSize now, has alignment
        #
        # ow-     ---mid--- ow-
        # 1 2 3 4 5 6 7 8 9 0 1
        p = Pagination(mode=Pagination.MODE_SIMPLE, page=7, innerWindow=2,
                outerWindow=1, total=110, perPage=10, linkSize='large',
                alignment='right', endpoint='#')
        linkStr = Pagination.linkCss.format(' pagination-large', ' pagination-right')
        linkStr += p.prev_page
        linkStr += p.single_page(1) + p.single_page(2) + Pagination.gapMarker
        for i in xrange(5, 12):
            linkStr += p.single_page(i)
        linkStr += p.next_page
        linkStr += '</ul></div>'
        self.assertEqual(linkStr, p.links)

    @ypaginate_request_context
    def test_info(self):
        # bounds dont exceed, search = False
        p = Pagination(page=1, perPage=10, total=100)
        infoStr = '<div class="pagination-page-info">'
        infoStr += Pagination.displayMsg.format(start=1, end=10,
            recordName=Pagination.recordName, total=100)
        infoStr += '</div>'
        self.assertEqual(infoStr, p.info)
        # bounds dont exceed, search = True
        p = Pagination(page=1, perPage=10, total=100, search=True, found=50)
        infoStr = '<div class="pagination-page-info">'
        infoStr += Pagination.searchMsg.format(start=1, end=10,
            recordName=Pagination.recordName, total=100, found=50)
        infoStr += '</div>'
        self.assertEqual(infoStr, p.info)
        # end bound exceed, search = False, recordName='cats'
        p = Pagination(page=8, total=92, perPage=12, recordName='cats')
        infoStr = '<div class="pagination-page-info">'
        infoStr += Pagination.displayMsg.format(start=85, end=92,
            recordName='cats', total=92)
        infoStr += '</div>'
        # start and end bounds exceed, search = False
        p = Pagination(page=13, total=92, perPage=12)
        infoStr = '<div class="pagination-page-info">'
        infoStr += Pagination.displayMsg.format(start=92, end=92,
            recordName=Pagination.recordName, total=92)
        infoStr += '</div>'
        self.assertEqual(infoStr, p.info)
        # start and end bounds exceed, search = True, recordName='sponns'
        p = Pagination(page=13, total=92, perPage=12, recordName='spoons',
                search=True, found=15)
        infoStr = '<div class="pagination-page-info">'
        infoStr += Pagination.searchMsg.format(start=15, end=15,
            recordName='spoons', found=15, total=92)
        infoStr += '</div>'
        self.assertEqual(infoStr, p.info)
