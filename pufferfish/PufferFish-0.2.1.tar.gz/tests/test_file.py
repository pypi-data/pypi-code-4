#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2011 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import os
import shutil
import stat
import tempfile
import unittest

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from nose.tools import raises

from . model.base import Base
from . model.image import Image
from . model.file import File
from . model.exc import RenameThumbnailExc, CreateThumbnailExc
from pufferfish.exc import UninitializedError

class TestFile(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.log = logging.getLogger(__name__)
        Base.metadata.create_all(self.engine)

        self.tempdir = tempfile.mkdtemp()
        filesdir = os.path.join(self.tempdir, "files")
        os.mkdir(filesdir)
        self.init_classes()

        # create test files.
        self.testfile1 = os.path.join(self.tempdir, "test1.xyz")
        self.testfile2 = os.path.join(self.tempdir, "test2.xyz")

        with open(self.testfile1, "w") as d1:
            with open(self.testfile2, "w") as d2:
               d1.write("1")
               d2.write("2")

    def tearDown(self):
        self.restore_permissions(self.tempdir)
        Base.metadata.drop_all(self.engine)
        File._state['failed'] = []
        Image._state['failed'] = []
        self.session.close()
        shutil.rmtree(self.tempdir)

    def init_classes(self):
        File.initialize(self.tempdir)
        Image.initialize(self.tempdir)

    def remove_permissions(self, dir_):
        os.chmod(dir_, stat.S_IRUSR|stat.S_IXUSR)

    def restore_permissions(self, dir_):
        os.chmod(dir_, stat.S_IRWXU | stat.S_IRWXG)

    def run_without_permission_on(self, dir_, func, *args, **kwargs):
        self.remove_permissions(dir_)
        func(*args, **kwargs)
        self.restore_permissions(dir_)

#    def test_0000_uninit(self):
#        """ This test must be executed first """
#        with self.assertRaises(UninitializedError):
#            File(name=u"test", source=self.testfile1, session=self.session)
#            self.session.commit()
#        shutil.rmtree(self.tempdir)
#        self.init_classes()

    def test_explicit_id(self):
        f = File(id=53, name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        self.assertEqual(f.id, 53)
        g = self.session.query(File).first()
        self.assertEqual(g.id, 53)

    def test_create_commit(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        self.assertTrue(os.path.exists(f.dir))
        self.assertTrue(os.path.exists(f.path))

    def test_create_noname(self):
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()
        self.assertTrue(os.path.exists(f.dir))
        self.assertTrue(os.path.exists(f.path))

    @raises(TypeError)
    def test_create_nosource(self):
        f = File(session=self.session)

    def test_create_conflict(self):
        os.mkdir(os.path.join(self.tempdir, "1"))
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()
        self.assertTrue(os.path.exists(os.path.join(self.tempdir,
                                                    "1_conflict")))

    def test_create_double_conflict(self):
        os.mkdir(os.path.join(self.tempdir, "1"))
        os.mkdir(os.path.join(self.tempdir, "1_conflict"))
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()
        self.assertTrue(os.path.exists(os.path.join(self.tempdir,
                                                    "1_conflict_")))

    @raises(OSError)
    def test_create_oserror(self):
        self.remove_permissions(self.tempdir)
        f = File(source=self.testfile1, session=self.session)
        self.restore_permissions(self.tempdir)

    def test_update_commit(self):
        f = File(name=u"test_update_commit", source=self.testfile1,
                 session=self.session)
        self.session.commit()
        f.update_file(self.testfile2)
        self.session.commit()
        self.assertTrue(os.path.exists(f.dir))
        self.assertEqual(open(f.path).read().strip(), "2")

    def test_update_commit_fail(self):
        f = File(name=u"test_update_commit_fail", source=self.testfile1,
                 session=self.session)
        f.update_file(self.testfile2)
        self.run_without_permission_on(self.tempdir, self.session.commit)
        self.assertEqual(len(File._state['failed']), 1)

    def test_delete_commit(self):
        f = File(name=u"test_delete_commit", source=self.testfile1,
                 session=self.session)
        d = f.dir
        fid = f.id
        self.session.delete(f)
        self.assertTrue(os.path.exists(d))
        self.session.commit()
        self.assertFalse(os.path.exists(d))

    def test_delete_commit_fail(self):
        f = File(name=u"test_delete_commit_fail", source=self.testfile1,
                 session=self.session)
        d = f.dir
        fid = f.id
        self.session.delete(f)
        self.assertTrue(os.path.exists(d))
        self.run_without_permission_on(self.tempdir, self.session.commit)
        self.assertTrue(os.path.exists(d))

    def test_create_rollback_fail(self):
        f = File(name=u'test_create_rollback', source=self.testfile1,
                 session=self.session)
        self.run_without_permission_on(self.tempdir, self.session.rollback)
        self.assertIn(f, File._state['failed'])
        self.assertTrue(not self.session.query(File).all())
        self.assertTrue(os.path.exists(f.dir))

    def test_create_rollback(self):
        f = File(name=u'test_create_rollback', source=self.testfile1,
                 session=self.session)
        self.session.rollback()
        self.assertTrue(not self.session.query(File).all())
        self.assertFalse(os.path.exists(f.dir))

    def test_delete_rollback(self):
        f = File(name=u"test_delete_rollback", source=self.testfile1,
                 session=self.session)
        self.session.commit()
        self.assertTrue(os.path.exists(f.dir))
        d = f.dir
        self.session.delete(f)
        self.session.rollback()
        self.assertTrue(os.path.exists(d))

    def test_update_rollback(self):
        f = File(name=u"test_update_rollback", source=self.testfile1,
                 session=self.session)
        self.assertEqual(open(f.path).read().strip(), "1")
        self.session.commit()
        f.update_file(self.testfile2)
        self.session.rollback()
        self.assertTrue(os.path.exists(f.dir))
        self.assertEqual(open(f.path).read().strip(), "1")

    def test_update_name(self):
        f = File(name=u"test_update_name.obj", source=self.testfile1,
                 session=self.session)
        original_path = f.path
        self.session.commit()
        self.session.close()

        g = self.session.query(File).first()
        self.assertIsNot(g, f)
        self.assertEqual(g.path, f.path)
        g.name = u'UPDATED.obj'
        self.session.commit()
        self.session.close()

        g1 = self.session.query(File).first()
        self.assertNotEqual(g1.path, original_path)
        self.assertTrue(os.path.exists(g1.path))

    def test_filename(self):
        f = File(name=u'Testing invalid_name$.jpg', source=self.testfile1,
                 session=self.session)
        self.session.commit()
        self.assertNotIn("$", f.plain_name)
        self.assertEqual("Testing_invalid_name", f.plain_name)

    def test_update_name_and_source(self):
        f = File(name=u"test_update_name.obj", source=self.testfile1,
                 session=self.session)
        original_path = f.path
        original_content = f.source.read()
        self.session.commit()
        self.session.close()

        g = self.session.query(File).first()
        g.name = u'UPDATED.obj'
        g.source = self.testfile2
        self.session.commit()
        self.session.close()

        g1 = self.session.query(File).first()
        self.assertNotEqual(g1.path, original_path)
        self.assertTrue(os.path.exists(g1.path))
        self.assertNotEqual(g1.source.read(), original_content)

    def test_update_rollback_fail(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        f.update_file(self.testfile2)
        self.run_without_permission_on(self.tempdir, self.session.rollback)
        # FIXME add assert

    @raises(ValueError)
    def test_path(self):
        File.set_paths("relative_path")

    def test_case(self):
        f = File(name=u'pRova.XXX', source=self.testfile1,
                 session=self.session)
        self.session.commit()
        self.assertEqual(f.plain_name, 'pRova')
        self.assertEqual(f.extension, '.xxx')

    def test_source(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        content = f.source.read()
        f.source = self.testfile2
        self.assertNotEqual(f.source.read(), content)

    def test_to_dict(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        d = f.to_dict()
        self.assertEqual(f.id, d['id'])
        self.assertEqual(f.name, d['name'])
        self.assertEqual(f.url, d['url'])
        self.assertEqual(f.path, d['path'])
        self.assertEqual(f.size, d['size'])
        self.assertEqual(f.content_type, d['content_type'])

    def test_has_session(self):
        f = File(name=u'test_has_session', source=self.testfile1,
                 session=self.session)
        self.assertTrue(hasattr(f, 'session'))
        self.session.commit()
        self.session.close()

        g = self.session.query(File).first()
        self.assertTrue(f.session is g.session)

    def test_multiple_session_added(self):
        f1 = File(name=u'test_has_session', source=self.testfile1,
                 session=self.session)
        session2 = self.Session()
        f2 = File(name=u'test_has_session2', source=self.testfile2,
                 session=session2)

        self.assertFalse(f1.session is f2.session)
        self.assertTrue(f1.session is self.session)
        self.assertTrue(f2.session is session2)

        self.session.commit()
        self.assertIn(f2.id, File._state['File']['added'])
        self.assertNotIn(f1.id, File._state['File']['added'])

        session2.commit()
        self.assertNotIn(f2.id, File._state['File']['added'])


    def test_getattr(self):
        f = File(name=u'test_getattr', source=self.testfile1,
                 session=self.session)
        self.session.commit()
        self.session.close()

        g = self.session.query(File).first()
        self.assertIsNot(f, g)
        self.assertTrue(hasattr(g, "url"))
        self.assertTrue(hasattr(g, "path"))

    def test_thumb_create(self):

        self.assertRaises(CreateThumbnailExc,
                          Image,
                          name=u'my_image.jpg',
                          source=self.testfile1,
                          session=self.session)

    def test_thumb_rename(self):

        del Image.create_thumbnail

        f = Image(name=u'original.jpg',
                  source=self.testfile1,
                  session=self.session)

        self.assertRaises(RenameThumbnailExc,
                          f.set_name,
                          "UPDATED.jpg")
