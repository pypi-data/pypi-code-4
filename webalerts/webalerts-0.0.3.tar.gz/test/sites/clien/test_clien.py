from datetime import datetime
import os
import re

from mock import Mock
import pytest
import yaml

from webalerts import LoginError
from webalerts.sites.clien import Clien, ClienAPI
from ...helpers import mock_function, MockRequest


__dir__ = os.path.abspath(os.path.dirname(__file__))


class TestClien(object):

    def setup(self):
        self.clien = Clien(config={
            'board_ids': ['foo', 'bar', 'puff'],
        })
        def get_post(board_id, post_id):
            return Mock(board_id=board_id, post_id=post_id, published=post_id)
        self.clien._api.get_post = Mock(side_effect=get_post)
        self.post_ids = {}
        self.clien._api.get_post_ids = mock_function(self.post_ids)

    def test_get_new_posts(self):
        self.post_ids.update({
            ('foo', 1): [5, 4, 3, 2, 1],
            ('bar', 1): [14, 13, 12, 11],
            ('puff', 1): [110, 109, 107],
            ('puff', 2): [106, 105, 104],
            ('puff', 3): [103, 102, 100],
        })
        assert self.clien.get_new_posts() == []
        self.post_ids.update({
            ('foo', 1): [7, 6, 4, 3, 2],
            ('bar', 1): [17, 16, 15, 14],
            ('puff', 1): [120, 119, 117],
            ('puff', 2): [116, 114, 112],
            ('puff', 3): [111, 110, 107],
        })
        assert [post.post_id for post in self.clien.get_new_posts()] == [
            6, 7, 15, 16, 17, 111, 112, 114, 116, 117, 119, 120
        ]


class TestClienAPIWithAuth(object):

    def setup(self):
        setup_api(self, 'user_foo', 'letmein')

    @pytest.mark.parametrize('board_id,page_no', [
        ('news', 3),
        ('lecture', 2),
        ('sold', 1),
        ('chehum', 56),
    ])
    def test_get_post_ids(self, board_id, page_no):
        assert (self.api.get_post_ids(board_id, page_no) ==
                self.pages[(board_id, page_no)]['post_ids'])

    @pytest.mark.parametrize('board_id,post_id', [
        ('news', 1713648),
        ('cm_mac', 727448),
        ('sold', 701508),
        ('cm_mac', 698162),
        ('sold', 705985),
    ])
    def test_get_post(self, board_id, post_id):
        rv = self.api.get_post(board_id, post_id)
        expected = self.posts[(board_id, post_id)]
        if not expected.get('deleted'):
            assert rv.url == expected['url']
            assert rv.title == expected['title']
            content_trimmed = re.sub(r'[\s\xa0]+', ' ', rv.content).strip()
            assert content_trimmed == expected['content_trimmed']
            assert rv.author == expected['author']
            assert rv.author_id == expected['author_id']
            published_timestamp = datetime.strftime(rv.published, '%Y-%m-%d %H:%M')
            assert published_timestamp == expected['published_timestamp']
        else:
            assert rv is None

    def test_get_post_invalid_markup(self):
        assert self.api.get_post('test', 1) is None


class TestClienAPIWithoutAuth(object):

    def setup(self):
        setup_api(self, 'abcd', '1234')

    def test_get_post(self):
        with pytest.raises(LoginError):
            self.api.get_post('sold', 701508)


def setup_api(self, username, password):
    self.api = ClienAPI(username, password)
    self.api._browser._request = MockRequest()
    self.api._browser._request.from_yaml(os.path.join(__dir__, 'pages.yaml'))
    self.pages = {}
    self.posts = {}
    for item in load_yaml('pages.yaml'):
        if 'post_ids' in item:
            key = (item['board_id'], item['page_no'])
            container = self.pages
        elif 'post_id' in item:
            key = (item['board_id'], item['post_id'])
            container = self.posts
        else:
            continue
        container[key] = item


def load_yaml(name):
    with open(os.path.join(__dir__, name)) as f:
        return yaml.load(f.read())
