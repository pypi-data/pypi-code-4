import os
import sys
sys.path.insert(0, '/usr/local/google_appengine')
import dev_appserver
dev_appserver.fix_sys_path()

from google.appengine.api import memcache
from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb
from views import app
from models import *
import unittest
import webtest
import logging

logger = logging.getLogger(__name__)


class T(unittest.TestCase):

    def setUp(self):

        self.app = webtest.TestApp(app)

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

        self.user1 = User(
            email=users.User('1@gmail.com')
        )
        self.user1.put()
        self.user2 = User(
            email=users.User('2@gmail.com')
        )
        self.user2.put()
        self.post1 = Post(
            title='a',
            content='a',
            user=self.user1.key
        )
        self.post1.put()
        self.post2 = Post(
            title='b',
            content='b',
            user=self.user1.key
        )
        self.post2.put()
        self.post3 = Post(
            title='c',
            content='c',
            user=self.user2.key
        )
        self.post3.put()
        self.comment1 = Comment(
            content='d',
            post=self.post3.key,
            user=self.user2.key
        )
        self.comment1.put()
        self.comment2 = Comment(
            content='e',
            post=self.post3.key,
            user=self.user2.key
        )
        self.comment2.put()
        self.tag1 = Tag(
            name='f',
            post=self.post3.key,
            user=self.user2.key
        )
        self.tag1.put()
        self.tag2 = Tag(
            name='g',
            post=self.post3.key,
            user=self.user2.key
        )
        self.tag2.put()

        assert len(User.query().fetch(5)) == 2
        assert len(Post.query().fetch(5)) == 3
        assert len(Comment.query().fetch(5)) == 2
        assert len(Tag.query().fetch(5)) == 2

    def tearDown(self):
        self.testbed.deactivate()


class PersmissionT(T):

    def test_create(self):

        self.testbed.setup_env(
            USER_EMAIL = '2@gmail.com',
            USER_ID = '123',
            USER_IS_ADMIN = '-1',
            overwrite = True
        )
        uri = '/posts/'
        data = {'post': {
            'title': 'New Book',
            'content': ' ',
            'user_id': unicode(self.user1.key.id())
        }}
        res = self.app.post_json(uri, data, expect_errors=True)
        self.assertEqual(res.status_int, 403)
        posts = Post.query().fetch(10)
        # assert no new post was created
        self.assertEqual(len(posts), 3)


class FieldT(T):

    def setUp(self):
        super(FieldT, self).setUp()
        self.testbed.setup_env(
            USER_EMAIL = '1@gmail.com',
            USER_ID = '123',
            USER_IS_ADMIN = '1',
            overwrite = True
        )

    def test_key(self):
        post = self.post1
        uri = '/posts/%s/' % post.key.id()
        res = self.app.get(uri)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        data = res.json
        post_data = data['post']
        self.assertEqual(post_data['id'], unicode(post.key.id()))
        self.assertEqual(post_data['user_id'], unicode(post.user.id()))

    @unittest.skip('')
    def test_blob(self):
        pass


class ApiT(T):

    def setUp(self):
        super(ApiT, self).setUp()
        self.testbed.setup_env(
            USER_EMAIL = '1@gmail.com',
            USER_ID = '123',
            USER_IS_ADMIN = '1',
            overwrite = True
        )

    def test_get_all(self):
        uri = '/posts/'
        res = self.app.get(uri)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        data = res.json
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data.keys()[0], 'posts')
        self.assertEqual(len(data['posts']), 3)

    def test_create(self):
        data = {'post': {
            'title': 'New Book',
            'content': 'My New Book',
            'user_id': unicode(self.user1.key.id())
        }}
        uri = '/posts/'
        res = self.app.post_json(uri, data)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        data = res.json
        post = Post.get_by_id(int(data['post']['id']))
        # self.assertEqual(unicode(post.key.id()), data['post']['id'])
        self.assertEqual(post.title, data['post']['title'])
        self.assertEqual(post.content, data['post']['content'])
        self.assertEqual(unicode(post.user.id()), data['post']['user_id'])

    def test_get_one(self):
        post = self.post1
        uri = '/posts/%d/' % post.key.id()
        res = self.app.get(uri)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        data = res.json
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data.keys()[0], 'post')
        post_data = data['post']
        self.assertEqual(post_data['id'], unicode(post.key.id()))
        self.assertEqual(post_data['title'], post.title)
        self.assertEqual(post_data['content'], post.content)
        self.assertEqual(post_data['user_id'], unicode(post.user.id()))

    def test_update(self):
        post = self.post1
        uri = '/posts/%d/' % post.key.id()
        data = {'post': {
            'title': 'New Book',
            'content': 'My New Book',
            'user_id': unicode(self.user1.key.id())
        }}
        res = self.app.put_json(uri, data)
        self.assertEqual(res.headers['Content-Type'], 'application/json')
        data = res.json
        post = Post.get_by_id(int(data['post']['id']))
        # self.assertEqual(unicode(post.key.id()), data['post']['id'])
        self.assertEqual(post.title, data['post']['title'])
        self.assertEqual(post.content, data['post']['content'])
        self.assertEqual(unicode(post.user.id()), data['post']['user_id'])

    def test_remove(self):
        post = self.post1
        uri = '/posts/%d/' % post.key.id()
        res = self.app.delete(uri)
        # assert relations are deleted
        for key in [post.key, post.user]:
            if key.get():
                e = '%s still exists' % key
                raise Exception(e)


class QueryT(T):

    def test_query(self):

        uri = '/posts/'

        data = {
            'query': {
                'string': 'WHERE title=:1',
                'values': [
                    'a'
                ]
            }
        }
        res = self.app.post_json(uri, data)
        data = res.json
        # assert returns 1/3 matched posts
        self.assertEqual(len(data['posts']), 1)

        data = {
            'query': {
                'string': 'WHERE user=:1',
                'values': [
                    {
                        'kind': 'User',
                        'value': unicode(self.user1.key.id())
                    }
                ]
            }
        }
        res = self.app.post_json(uri, data)
        data = res.json
        # assert returns 2/3 matched posts
        self.assertEqual(len(data['posts']), 2)

        data = {
            'query': {
                'string': 'WHERE user=:1 LIMIT 1',
                'values': [
                    {
                        'kind': 'User',
                        'value': unicode(self.user1.key.id())
                    }
                ]
            }
        }
        res = self.app.post_json(uri, data)
        data = res.json
        # assert returns 1/3 matched posts
        self.assertEqual(len(data['posts']), 1)

        data = {
            'query': {
                'string': 'WHERE user=:2 AND title=:1',
                'values': [
                    'a',
                    {
                        'kind': 'User',
                        'value': unicode(self.user1.key.id())
                    }
                ]
            }
        }
        res = self.app.post_json(uri, data)
        data = res.json
        # assert returns 1/3 matched posts
        self.assertEqual(len(data['posts']), 1)

        data = {
            'query': {
                'string': 'WHERE user=:1 AND title=:2',
                'values': [
                    {
                        'kind': 'User',
                        'value': unicode(self.user1.key.id())
                    },
                    'a'
                ]
            }
        }
        res = self.app.post_json(uri, data)
        data = res.json
        # assert returns 1/3 matched posts
        self.assertEqual(len(data['posts']), 1)

    def test_count(self):
        data = {
            'query': 'count'
        }
        uri = '/posts/'
        res = self.app.post_json(uri, data)
        self.assertEqual(Post.query().count(100), int(res.body))

        data = {
            'query': 'count'
        }
        uri = '/tags/'
        res = self.app.post_json(uri, data)
        self.assertEqual(Comment.query().count(100), int(res.body))

unittest.main()