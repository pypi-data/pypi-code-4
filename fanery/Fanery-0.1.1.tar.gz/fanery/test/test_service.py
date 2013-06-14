from fanery import service

def html(term):
    return '<p>%s</p>' % term

def xml(term):
    return '<%(tag)s>%(value)s</%(tag)s>' % \
        dict(value = term, tag = type(term).__name__)

@service(html = html, xml = xml)
def safe_echo(term = None):
    return term

@service(safe = False, ssl = False, html = html, xml = xml)
def echo(term = None):
    return term

def _state():
    return service.state

@service(safe = False, ssl = False)
def state1():
    return service.state, _state()

@service(safe = False, ssl = False)
def state2():
    return service.state, _state()

def test_service_meta():
    assert safe_echo.service.safe == True
    assert safe_echo.service.ssl == True
    assert echo.service.route == echo.__name__
    assert echo.service.cache == False
    assert echo.service.safe == False
    assert echo.service.ssl == False
    assert callable(echo.service.output.xml)
    assert callable(echo.service.output.html)
    assert echo.service.output.xml is xml
    assert echo.service.output.html is html
    assert echo.service.output == safe_echo.service.output

def test_lookup():
    func, args, exc, output = service.lookup('echo.xls')
    assert func is echo and not args and exc == '.xls' and output is None
    try:
        service.lookup('not-registered')
        raise Exception('should raise service.NotFound')
    except service.NotFound:
        pass

def test_consume():
    assert service.consume('echo') is None
    assert service.consume('echo/1') is 1
    assert service.consume('echo/1.0') is 1
    assert service.consume('echo', 1) is 1
    assert service.consume('echo', '1') is 1
    assert service.consume('echo', 1.0) is 1
    assert service.consume('echo', '1.0') is 1
    assert service.consume('echo', term = 1) is 1
    assert service.consume('echo', term = '1') is 1
    assert service.consume('echo', term = 1.0) is 1
    assert service.consume('echo', term = '1.0') is 1

def test_output():
    html = '<p>1</p>'
    assert service.consume('echo/1.html') == html
    assert service.consume('echo/1.0.html') == html
    assert service.consume('echo.html', 1) == html
    assert service.consume('echo.html', '1') == html
    assert service.consume('echo.html', 1.0) == html
    assert service.consume('echo.html', '1.0') == html
    assert service.consume('echo.html', term = 1) == html
    assert service.consume('echo.html', term = '1') == html
    assert service.consume('echo.html', term = 1.0) == html
    assert service.consume('echo.html', term = '1.0') == html

    xml = '<int>1</int>'
    assert service.consume('echo/1.xml') == xml
    assert service.consume('echo/1.0.xml') == xml
    assert service.consume('echo.xml', 1) == xml
    assert service.consume('echo.xml', '1') == xml
    assert service.consume('echo.xml', 1.0) == xml
    assert service.consume('echo.xml', '1.0') == xml
    assert service.consume('echo.xml', term = 1) == xml
    assert service.consume('echo.xml', term = '1') == xml
    assert service.consume('echo.xml', term = 1.0) == xml
    assert service.consume('echo.xml', term = '1.0') == xml

    xml = '<date>2012-01-30</date>'
    assert service.consume('echo/2012-1-30.xml') == xml
    assert service.consume('echo.xml', '30 Jan 2012') == xml
    assert service.consume('echo.xml', term = '01/30/2012') == xml

def test_state():
    session1_1, session1_2 = state1()
    session2_1, session2_2 = state2()
    assert session1_1 is session1_2
    assert session2_1 is session2_2
    assert session1_1 is not session2_1
