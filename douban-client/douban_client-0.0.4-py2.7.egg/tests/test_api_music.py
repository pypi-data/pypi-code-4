# -*- coding: utf-8 -*-

from uuid import uuid4
from framework import DoubanClientTestBase, main

class TestApiMusic(DoubanClientTestBase):
    def setUp(self):
        super(TestApiMusic, self).setUp()
        self.user_id = '40774605'
        self.music_id = '1419262'
        self.review_id = '5572975'

    def test_get_music(self):
        ret = self.client.music.get(self.music_id)

        self.assertTrue(isinstance(ret, dict))
        self.assertTrue(ret.has_key('author'))
        self.assertTrue(ret.has_key('title'))
        self.assertTrue(ret.has_key('summary'))

    def test_search_music(self):
        ret = self.client.music.search('坦白')

        self.assertTrue(isinstance(ret, dict))
        self.assertTrue(isinstance(ret['musics'], list))
        self.assertTrue(ret.has_key('start'))
        self.assertTrue(ret.has_key('count'))
        self.assertTrue(ret.has_key('total'))

    # def test_music_reviews(self):
    #     ret = self.client.music.reviews(self.music_id)

    #     self.assertTrue(isinstance(ret, dict))
    #     self.assertTrue(isinstance(ret['reviews'], list))
    #     self.assertTrue(ret.has_key('start'))
    #     self.assertTrue(ret.has_key('count'))
    #     self.assertTrue(ret.has_key('total'))

    def test_music_tags(self):
        ret = self.client.music.tags(self.music_id)

        self.assertTrue(isinstance(ret, dict))
        self.assertTrue(isinstance(ret['tags'], list))
        self.assertTrue(ret.has_key('start'))
        self.assertTrue(ret.has_key('count'))
        self.assertTrue(ret.has_key('total'))

    def test_get_music_tagged_list(self):
        ret = self.client.music.tagged_list('40774605')

        self.assertTrue(isinstance(ret, dict))
        self.assertTrue(isinstance(ret['tags'], list))
        self.assertTrue(ret.has_key('start'))
        self.assertTrue(ret.has_key('count'))
        self.assertTrue(ret.has_key('total'))

    def test_new_update_delete_review(self):

        # new
        title = content = uuid4().hex
        content = content * 10
        ret = self.client.music.review.new(self.music_id, title, content)

        self.assertTrue(isinstance(ret, dict))
        self.assertEqual(content, ret['content'])
        self.assertTrue(ret.has_key('author'))

        review_id = ret['id']

        # update
        content = content * 2
        ret = self.client.music.review.update(review_id, title, content)
        self.assertEqual(content, ret['content'])

        # delete
        ret = self.client.music.review.delete(review_id)
        self.assertEqual('OK', ret)


    # def test_get_music_review(self):
    #     ret = self.client.music.review.get(self.review_id)

    #     self.assertTrue(isinstance(ret, dict))
    #     self.assertEqual(ret['id'], self.review_id)
    #     self.assertTrue(ret.has_key('rating'))
    #     self.assertTrue(ret.has_key('author'))


if __name__ == '__main__':
    main()
