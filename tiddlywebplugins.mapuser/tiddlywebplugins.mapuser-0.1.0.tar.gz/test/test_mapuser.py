"""
Test POSTs to the local TiddlyWeb instance
"""


from json import dumps

import os

import shutil

import httplib2

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.store import Store
from tiddlyweb.config import config

from test.fixtures import initialize_app, get_auth


def setup_module(module):
    initialize_app()

    module.store = Store(config['server_store'][0], config['server_store'][1], {'tiddlyweb.config': config})
    bag = Bag('MAPUSER')
    module.store.put(bag)

    user = User('ben')
    user.set_password('mocha')
    module.store.put(user)
    user = User('chris')
    user.set_password('piccolo')
    module.store.put(user)


def teardown_module():
    if os.path.exists('store'):
        shutil.rmtree('store')


def test_handler_valid_post_responds_with_201():
    cookie = get_auth('ben', 'mocha')
    data = {'mapped_user': 'pads'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/ben',
                                     method='POST',
                                     headers={
                                         'content-type': 'application/json; charset=UTF-8',
                                         'Cookie': 'tiddlyweb_user="%s"' % cookie
                                     },
                                     body=dumps(data))

    assert response['status'] == '201'


def test_handler_valid_post_creates_mapuser_tiddler():
    cookie = get_auth('chris', 'piccolo')
    data = {'mapped_user': 'cdent'}

    http = httplib2.Http()
    http.request('http://0.0.0.0:8080/map_user/chris',
                 method='POST',
                 headers={
                     'content-type': 'application/json; charset=UTF-8',
                     'Cookie': 'tiddlyweb_user="%s"' % cookie
                 },
                 body=dumps(data))

    tiddler = Tiddler('chris', 'MAPUSER')
    tiddler = store.get(tiddler)

    assert tiddler.modifier == 'chris'
    assert tiddler.text == ''
    assert 'mapped_user' in tiddler.fields
    assert tiddler.fields['mapped_user'] == 'cdent'


def test_handler_responds_with_400_when_content_type_not_present():
    cookie = get_auth('ben', 'mocha')
    data = {'mapped_user': 'pads'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/ben',
                                     method='POST',
                                     headers={'Cookie': 'tiddlyweb_user="%s"' % cookie},
                                     body=dumps(data))

    assert response['status'] == '400'


def test_handler_responds_with_415_when_content_type_is_invalid():
    cookie = get_auth('chris', 'piccolo')
    data = {'mapped_user': 'cdent'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/chris',
                                     method='POST',
                                     headers={
                                         'content-type': 'text/html; charset=UTF-8',
                                         'Cookie': 'tiddlyweb_user="%s"' % cookie
                                     },
                                     body=dumps(data))

    assert response['status'] == '415'


def test_handler_responds_with_400_when_content_is_invalid():
    cookie = get_auth('ben', 'mocha')
    data = {'mapped_user': 'pads'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/ben',
                                     method='POST',
                                     headers={'Cookie': 'tiddlyweb_user="%s"' % cookie},
                                     body=dumps(data))

    assert response['status'] == '400'


def test_handler_responds_with_400_when_cookie_is_not_sent():
    data = {'mapped_user': 'cdent'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/chris',
                                     method='POST',
                                     headers={'content-type': 'application/json; charset=UTF-8'},
                                     body=dumps(data))

    assert response['status'] == '400'


def test_handler_responds_with_401_when_cookie_is_invalid():
    cookie = 'ben:starbucks'
    data = {'mapped_user': 'pads'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/ben',
                                     method='POST',
                                     headers={
                                         'content-type': 'application/json; charset=UTF-8',
                                         'Cookie': 'tiddlyweb_user="%s"' % cookie
                                     },
                                     body=dumps(data))

    assert response['status'] == '401'


def test_handler_responds_with_401_when_user_is_invalid():
    cookie = get_auth('chris', 'piccolo')
    data = {'mapped_user': 'pads'}

    http = httplib2.Http()
    response, content = http.request('http://0.0.0.0:8080/map_user/ben',
                                     method='POST',
                                     headers={
                                         'content-type': 'application/json; charset=UTF-8',
                                         'Cookie': 'tiddlyweb_user="%s"' % cookie
                                     },
                                     body=dumps(data))

    assert response['status'] == '401'
