import datetime
import os.path
import unittest
from urllib import pathname2url

import pytest

from upyun import const, UpYun


class UpYunTestCase(unittest.TestCase):
    #: File type bucket
    BUCKET_FILE = ''

    #: Image type bucket
    BUCKET_IMAGE = ''

    #: Username
    USERNAME = ''

    #: Password
    PASSWD = ''

    #: Predefined thumbnail version
    THUMB_VERSION = ''

    ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asset')
    LOCAL_PATH_TXT_FILE = os.path.join(ASSET, 'upyun-test.txt')
    LOCAL_PATH_IMG_FILE = os.path.join(ASSET, 'upyun-test.gif')
    REMOTE_DIR = '/tmp/upyun-test'
    REMOTE_PATH_TXT_FILE = pathname2url(
            os.path.join(REMOTE_DIR, 'upyun-test.txt'))
    REMOTE_PATH_IMG_FILE = pathname2url(
            os.path.join(REMOTE_DIR, 'upyun-test.gif'))

    def setUp(self):
        self.client_file = UpYun(self.BUCKET_FILE,
                (self.USERNAME, self.PASSWD), const.SPACE_TYPE_FILE)
        self.client_image = UpYun(self.BUCKET_IMAGE,
                (self.USERNAME, self.PASSWD), const.SPACE_TYPE_IMAGE)
        self.test_file_txt = open(self.LOCAL_PATH_TXT_FILE)
        self.test_file_img = open(self.LOCAL_PATH_IMG_FILE, 'rb')

    def tearDown(self):
        self.test_file_txt.close()
        self.test_file_img.close()
        self._delete(self.REMOTE_PATH_TXT_FILE, self.client_file)
        self._delete(self.REMOTE_PATH_IMG_FILE, self.client_file)
        self._delete(self.REMOTE_PATH_IMG_FILE, self.client_image)
        self._delete(self.REMOTE_DIR, self.client_image)
        self._delete(self.REMOTE_DIR, self.client_file)

    def _put_file(self):
        return self.client_file.put(
                self.REMOTE_PATH_TXT_FILE, self.test_file_txt)

    def _put_image(self, client=None):
        client = client or self.client_image
        return client.put(self.REMOTE_PATH_IMG_FILE, self.test_file_img)

    def _mkdir(self, mk_parent=True, client=None):
        client = client or self.client_file
        return client.mkdir(self.REMOTE_DIR, mk_parent)

    def _delete(self, path, client):
        return client.delete(path)

    def test_put_file_space_file(self):
        resp = self._put_file()
        assert resp.success, resp.error

    def test_put_file_space_image(self):
        resp = self._put_image(self.client_file)
        assert resp.success, resp.error

    def test_put_image_space_image(self):
        resp = self._put_image(self.client_image)
        assert resp.success, resp.error
        assert isinstance(resp.frames, int)
        assert isinstance(resp.height, int)
        assert resp.height > 0
        assert isinstance(resp.width, int)
        assert resp.width > 0

    def test_put_thumbnail_version(self):
        resp = self.client_image.put_thumbnail(self.REMOTE_PATH_IMG_FILE,
                self.test_file_img, self.THUMB_VERSION)
        assert resp.success, resp.error

    def test_put_thumbnail_version_modified(self):
        resp = self.client_image.put_thumbnail(self.REMOTE_PATH_IMG_FILE,
                self.test_file_img, self.THUMB_VERSION,
                const.THUMB_TYPE_FIX_MAX, (10,), 100, True)
        assert resp.success, resp.error

    def test_put_thumbnail_custom(self):
        resp = self.client_image.put_thumbnail(self.REMOTE_PATH_IMG_FILE,
                self.test_file_img, ttype=const.THUMB_TYPE_FIX_MAX, res=(10,),
                quality=100, sharpen=True)
        assert resp.success, resp.error

    def test_get_text_file(self):
        self._put_file()
        resp = self.client_file.get(self.REMOTE_PATH_TXT_FILE)
        assert resp.success, resp.error
        self.test_file_txt.seek(0)
        assert resp.data == self.test_file_txt.read()

    def test_get_binary_file(self):
        client = self.client_image
        self._put_image(client)
        resp = client.get(self.REMOTE_PATH_IMG_FILE)
        assert resp.success, resp.error
        self.test_file_img.seek(0)
        assert resp.data == self.test_file_img.read()

    def test_ls(self):
        client = self.client_file
        self._put_file()
        self._put_image(client)
        resp = client.ls(self.REMOTE_DIR)
        assert resp.success, resp.error
        remote_file_paths = map(lambda f: f.path, resp.files.itervalues())
        assert self.REMOTE_PATH_TXT_FILE in remote_file_paths
        assert self.REMOTE_PATH_IMG_FILE in remote_file_paths

    def test_mkdir(self):
        resp = self._mkdir()
        assert resp.success, resp.error

    def test_usage(self):
        resp = self.client_file.usage()
        assert resp.success, resp.error
        assert isinstance(resp.usage, int)
        resp = self.client_image.usage()
        assert resp.success, resp.error
        assert isinstance(resp.usage, int)

    def test_info(self):
        def _assert(resp):
            assert resp.success, resp.error
            assert isinstance(resp.size, int)
            assert isinstance(resp.date, datetime.datetime)
            assert resp.type == const.FILE_TYPE_FILE

        self._put_file()
        resp = self.client_file.info(self.REMOTE_PATH_TXT_FILE)
        _assert(resp)
        self._put_image()
        resp = self.client_image.info(self.REMOTE_PATH_IMG_FILE)
        _assert(resp)

    def test_delete(self):
        self._put_file()
        resp = self.client_file.delete(self.REMOTE_PATH_TXT_FILE)
        assert resp.success, resp.error
        self._put_image()
        resp = self.client_image.delete(self.REMOTE_PATH_IMG_FILE)
        assert resp.success, resp.error

if __name__ == '__main__':
    unittest.main()
