from fanery import service, static, is_date

@service(safe = False, ssl = False)
def echo(*args, **argd):
    if args and argd:
        return args, argd
    elif args:
        return args if len(args) > 1 else args[0]
    elif argd:
        return argd

@service('echo_two', safe = False, ssl = False, auto_parse = False)
def echo2(*args, **argd):
    if args and argd:
        return args, argd
    elif args:
        return args if len(args) > 1 else args[0]
    elif argd:
        return argd

@service(ssl = False)
def safe_call(**argd):
    return argd

def test_urlpath():
    assert echo.urlpath == 'echo'
    assert echo2.urlpath == 'echo_two'
    assert safe_call.urlpath == 'safe_call'

def test_safe_param():
    assert echo.safe is False
    assert echo2.safe is False
    assert safe_call.safe is True

def test_ssl_param():
    assert echo.ssl is False
    assert echo2.ssl is False
    assert safe_call.ssl is False

def test_auto_parse_param():
    assert echo.auto_parse is True
    assert echo2.auto_parse is False
    assert safe_call.auto_parse is True

def test_log_exc_param():
    assert echo.log_exc is True
    assert echo2.log_exc is True
    assert safe_call.log_exc is True

def test_auto_parse_on_call():
    assert echo('1') == 1
    assert echo('1.1') == 1.1
    assert is_date(echo('1990-01-01'))
    assert echo2('1') == '1'
    try:
        safe_call()
    except AssertionError, e:
        assert e.args[0][0] == 'bad-format', e.args

def test_lookup():
    from fanery._term import to_json, to_str
    from fanery._service import lookup

    assert lookup('prefix/echo/1/2/3.json') == (
            echo, ['1', '2', '3'], '.json', to_json)

    assert lookup('/echo.doc') == (echo, [], '.doc', False)
    assert lookup('/a/safe_call') == (safe_call, [], '', None)
    assert lookup('a/b/echo_two.raw') == (echo2, [], '.raw', repr)
    assert lookup('safe_call.txt') == (safe_call, [], '.txt', to_str)

def test_consume():
    from fanery._state import get_state
    from fanery._service import consume

    _state_ = get_state()
    assert consume(_state_, 'prefix/echo/1/2/3') == (echo, '', (1,2,3))
    assert consume(_state_, 'prefix/echo/1/2/3.json') == (echo, '.json', '[1, 2, 3]')

def store_setUp():
    from fanery._store import storage, add_model, add_storage
    from fanery._mddb import MemDictStore as Store, User
    from fanery._auth import hooks

    add_model(User)
    dbm = Store(hooks)
    add_storage(dbm, User)

    user = hooks.fetch_user('user')
    if not user:
        with storage() as db:
            user = db.insert(User, login = 'user', password = 'passwd')
            assert user.login == 'user'
            assert user.password == 'passwd'

        stored = hooks.fetch_user('user')
        assert user.__dict__ == stored.__dict__

    return User, user

def test_PyClient():
    from fanery._client import PyClient

    client = PyClient()
    User, user = store_setUp()

    assert client.login(user.login, user.password) is True
    assert client.call('echo', a = '1.0') == {'a': 1}
    assert client.safe_call('safe_call', a = 1) == {'a': 1}
    assert client.call('echo.json', a = '1.0') == {'a': 1}
    assert client.safe_call('safe_call.json', a = '1.0') == {'a': 1}
    assert client.logout() is True

def test_WsgiClient():
    from fanery._client import WsgiClient

    client = WsgiClient()
    User, user = store_setUp()

    assert client.login(user.login, user.password) is True
    assert client.call('echo', a = '1.0') == repr({'a': 1})
    assert client.safe_call('safe_call', a = 1) == {u'a': 1}
    assert client.call('echo.json', a = '1.0') == {u'a': 1}
    assert client.safe_call('safe_call.json', a = '1.0') == {u'a': 1}
    assert client.logout() is True

def test_HttpClient():
    from multiprocessing import Process
    from fanery._server import start_wsgi_server
    from fanery._client import HttpClient

    User, user = store_setUp()

    server_proc = Process(target = start_wsgi_server)
    server_proc.daemon = True
    server_proc.start()

    client = HttpClient()

    try:
        assert client.login(user.login, user.password) is True
        assert client.call('echo', a = '1.0') == repr({'a': 1})
        assert client.safe_call('safe_call', a = 1) == {u'a': 1}
        assert client.call('echo.json', a = '1.0') == {u'a': 1}
        assert client.safe_call('safe_call.json', a = '1.0') == {u'a': 1}
        assert client.logout() is True
        assert client.login(user.login, user.password) is True
        assert client.logout() is True
    finally:
        server_proc.terminate()

def main():
    from random import shuffle
    tests = [(k, v) for k, v in globals().iteritems()
             if k.startswith('test_') and callable(v)]
    shuffle(tests)

    from fanery import timecall, memory_profile, line_profile
    for _, test in tests:
        #memory_profile(test)()
        #line_profile(test)()
        timecall(test)()

if __name__ == '__main__':
    main()
