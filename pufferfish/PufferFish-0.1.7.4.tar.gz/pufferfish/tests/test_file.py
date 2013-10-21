
import elixir
import logging
import os
import shutil
import stat
import tempfile

from elixir import create_all, setup_all, drop_all, cleanup_all
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from nose.tools import raises, assert_raises

from pufferfish import FileSystemEntity, add_session_hooks
from pufferfish.session import HookableSession
from pufferfish.file import File
from pufferfish.tests.model.image import Image
from pufferfish.tests.model.exc import RenameThumbnailExc, CreateThumbnailExc

class TestFile(object):
    
    def setup(self):
        engine = create_engine("sqlite:///")
        elixir.metadata.bind = engine
        self.session = HookableSession()
        elixir.session = self.session
        setup_all()
        create_all()

        self.tempdir = tempfile.mkdtemp()
        filesdir = os.path.join(self.tempdir, "files")
        os.mkdir(filesdir)
        # we use base_path instead of set_paths as set_paths sets the private
        # path too, and we need to test it being missing.
        
        File.base_path=self.tempdir
        File.tmp_objects = {"added": [], "removed": [], "updated": {}, "failed": [] }
        Image.base_path=self.tempdir
        Image.tmp_objects = {"added": [], "removed": [], "updated": {}, "failed": [] }

        # create test files.
        self.testfile1 = os.path.join(self.tempdir, "test1.xyz")
        self.testfile2 = os.path.join(self.tempdir, "test2.xyz")

        with open(self.testfile1, "w") as d1:
            with open(self.testfile2, "w") as d2:
               d1.write("1")
               d2.write("2")

        self.log = logging.getLogger(__name__)

    def teardown(self):
        self.restore_permissions(self.tempdir)
        drop_all()
        self.session.close()
        File.tmp_objects = {"added": [], "removed": [], "updated": [], "failed": [] }
        Image.tmp_objects = {"added": [], "removed": [], "updated": [], "failed": [] }
        shutil.rmtree(self.tempdir)

    def remove_permissions(self, dir_):
        os.chmod(dir_, stat.S_IRUSR|stat.S_IXUSR) 

    def restore_permissions(self, dir_):
        os.chmod(dir_, stat.S_IRWXU | stat.S_IRWXG)

    def run_without_permission_on(self, dir_, func, *args, **kwargs):
        self.remove_permissions(dir_)
        func(*args, **kwargs)
        self.restore_permissions(dir_)

    def test_create_commit(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        assert os.path.exists(f.dir)
        assert os.path.exists(f.path)

    def test_create_noname(self):
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()
        assert os.path.exists(f.dir)
        assert os.path.exists(f.path)

    @raises(TypeError)
    def test_create_nosource(self):
        f = File(session=self.session)

    def test_create_conflict(self):
        os.mkdir(os.path.join(self.tempdir, "1"))
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()

    def test_create_double_conflict(self):
        os.mkdir(os.path.join(self.tempdir, "1"))
        os.mkdir(os.path.join(self.tempdir, "1_conflict"))
        f = File(source=self.testfile1, session=self.session)
        self.session.commit()

    @raises(OSError)
    def test_create_oserror(self):
        self.remove_permissions(self.tempdir)
        f = File(source=self.testfile1, session=self.session)
        self.restore_permissions(self.tempdir)

    def test_update_commit(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        f.update_file(self.testfile2)
        self.session.commit()
        assert os.path.exists(f.dir)
        assert open(f.path).read().strip() == "2"

    def test_update_commit_fail(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        f.update_file(self.testfile2)
        self.run_without_permission_on(self.tempdir, self.session.commit)
        assert len(File.tmp_objects['failed']) > 0

    def test_delete_commit(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        d = f.dir
        fid = f.id
        f.delete()
        self.run_without_permission_on(self.tempdir, self.session.commit)

    def test_delete_commit_fail(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        d = f.dir
        fid = f.id
        f.delete()
        self.run_without_permission_on(self.tempdir, self.session.commit)
        
    def test_create_rollback(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        self.run_without_permission_on(self.tempdir, self.session.rollback)

    def test_create_rollback_fail(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        self.session.rollback()
        assert not os.path.exists(f.dir)

    def test_delete_rollback(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        assert os.path.exists(f.dir)
        f.delete()
        d = f.dir
        self.session.rollback()
        assert os.path.exists(d)

    def test_update_rollback(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        assert open(f.path).read().strip() == "1"
        self.session.commit()
        f.update_file(self.testfile2)
        self.session.rollback()
        assert os.path.exists(f.dir)
        assert open(f.path).read().strip() == "1"

    def test_update_name(self):
        f = File(name=u"test_update_name.obj", source=self.testfile1, session=self.session)
        original_path = f.path
        self.session.commit()
        self.session.close()

        g = elixir.session.query(File).first()
        assert g is not f
        assert g.path == f.path
        g.name = u'UPDATED.obj'
        self.session.commit()
        self.session.close()

        g1 = elixir.session.query(File).first()
        assert g1.path != original_path
        assert os.path.exists(g1.path) == True

    def test_update_name_and_source(self):
        f = File(name=u"test_update_name.obj", source=self.testfile1, session=self.session)
        original_path = f.path
        original_content = f.source.read()
        self.session.commit()
        self.session.close()

        g = elixir.session.query(File).first()
        g.name = u'UPDATED.obj'
        g.source = self.testfile2
        self.session.commit()
        self.session.close()

        g1 = elixir.session.query(File).first()
        assert g1.path != original_path
        assert os.path.exists(g1.path) == True
        assert g1.source.read() != original_content
    
    def test_update_rollback_fail(self):
        f = File(name=u"test", source=self.testfile1, session=self.session)
        self.session.commit()
        f.update_file(self.testfile2)
        self.run_without_permission_on(self.tempdir, self.session.rollback)
    
    @raises(ValueError)
    def test_path(self):
        File.set_paths("/tmp")
        File.set_paths("relative_path")

    def test_source(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        content = f.source.read()
        f.source = self.testfile2
        assert f.source.read() != content

    def test_to_dict(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        d = f.to_dict()
        assert f.name == d['name']
        assert f.url == d['url']
        assert f.path == d['path']
        assert f.size == d['size']
        assert f.content_type == d['content_type']

    def test_getattr(self):
        f = File(name=u'test', source=self.testfile1, session=self.session)
        self.session.commit()
        self.session.close()

        g = elixir.session.query(File).first()
        assert f is not g
        assert hasattr(g, "url")
        assert hasattr(g, "path")

    def test_thumb_create(self):
        
        assert_raises(CreateThumbnailExc, 
                      Image,
                      name=u'my_image.jpg',
                      source=self.testfile1, 
                      session=self.session)

    def test_thumb_rename(self):

        del Image.create_thumbnail

        f = Image(name=u'image.jpg',
                  source=self.testfile1,
                  session=self.session)

        assert_raises(RenameThumbnailExc,
                      f.set_name,
                      "UPDATED.jpg")
                      
                    



        
