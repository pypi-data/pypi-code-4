import rw.www


def test_concatenation():
    obj = rw.www.StaticObject('test', 'file', '123456')
    url = obj + '&foo=bar'
    assert 'test' in url
    assert 'file' in url
    assert url.endswith('&foo=bar')


def test_kwargs():
    obj = rw.www.StaticObject(fname='file', md5sum='123456', module='test')
    url = obj + '&foo=bar'
    assert 'test' in url
    assert 'file' in url
    assert url.endswith('&foo=bar')
