from flea import TestAgent

from fresco import flash, FrescoApp, GET, Response

app = FrescoApp()
@app.route('/messages', GET)
def flash_messages(request):
    return Response('%'.join(s for level, s in flash.messages()))

@app.route('/flash', GET)
def flash_custom(request):
    for item in request.query.getlist('m'):
        flash.info(item)
    if 'r' in request.query:
        return Response.redirect(
            request.query.get('r')
        )
    return Response('%'.join(s for level, s in flash.messages()))

app = TestAgent(app)

class TestFlash(object):

    def test_flash_with_redirect(self):
        r = app.get('/flash', data=[('r', '/messages'), ('m', 'hello')])
        assert r.request.request_path == '/messages'
        assert r.body == 'hello'

    def test_multi_flash_with_redirect(self):
        r = app.get('/flash', data=[('r', '/messages'), ('m', 'hello'), ('m', 'world')])
        assert r.request.request_path == '/messages'
        assert r.body == 'hello%world'

    def test_multi_flash_with_metachars_and_redirect(self):
        r = app.get('/flash', data=[('r', '/messages'), ('m', 'hel:lo'), ('m', 'wo,r;ld')])
        assert r.request.request_path == '/messages'
        assert r.body == 'hel:lo%wo,r;ld', r.body

    def test_flash(self):
        r = app.get('/flash', data=[('m', 'hello')])
        assert r.request.request_path == '/flash'
        assert r.body == 'hello'

    def test_multi_flash(self):
        r = app.get('/flash', data=[('m', 'hello'), ('m', 'world')])
        assert r.request.request_path == '/flash'
        assert r.body == 'hello%world'

    def test_multi_flash_with_metachars(self):
        r = app.get('/flash', data=[('m', 'hel:lo'), ('m', 'wo,r;ld')])
        assert r.request.request_path == '/flash'
        assert r.body == 'hel:lo%wo,r;ld'


