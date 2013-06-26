# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import unittest

import os
import shutil
import tempfile

from _connection import PPlusConnection, PPlusError

#------------------------------------------------------------------------------
def _count_file_lines(file_path):
    with open(file_path) as f:
        counter = len(f.readlines())
    return counter

def myjob(pc, arg):
    return arg

def mybadjob(pc):
    raise Exception()

#------------------------------------------------------------------------------
class PPlusConnectionTest(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write('Small file indeed it is\n')
            self.small_file = f.name
        self.pc = PPlusConnection(debug=True)

    def tearDown(self):
        shutil.rmtree('cache')
        shutil.rmtree('disk')
        os.remove(self.small_file)

    def test_settings(self):
        self.assertEquals(self.pc.cache_path,
                          os.path.abspath(os.path.join('cache/',
                                                       self.pc.id)))
        self.assertEquals(self.pc.disk_path,
                          os.path.abspath(os.path.join('disk/',
                                                       self.pc.id)))
        self.assertEquals(True, self.pc.is_debug)

    def test_ids(self):
        self.assertEquals(32, len(self.pc.id))
        self.assertEquals(32, len(self.pc.session_id))

        pc = PPlusConnection(5)
        self.assertEquals(1, len(pc.id))
        self.assertEquals('5', pc.id)

    def test_put(self):
        self.pc.put('MYFILE', self.small_file)
        path = os.path.join(self.pc.disk_path, 'MYFILE')
        self.assertTrue(os.path.exists(path))

        # Same key without overwrite
        self.assertRaises(PPlusError, self.pc.put,
                                            'MYFILE',
                                            self.small_file, overwrite=False)

        # Same file
        self.pc.put('MYFILE2', self.small_file)
        path = os.path.join(self.pc.disk_path, 'MYFILE2')
        self.assertTrue(os.path.exists(path))

    def test_put_overwrite(self):
        self.pc.put('MYFILE', self.small_file)
        self.pc.put('MYFILE', self.small_file, overwrite=True)

    def test_remove(self):
        self.pc.put('MYFILE', self.small_file)
        path = os.path.join(self.pc.disk_path, 'MYFILE')
        self.assertTrue(os.path.exists(path))

        self.pc.remove('MYFILE')
        self.assertFalse(os.path.exists(path))

        self.pc.remove('MYFILE')  # pass silently

    def test_get_path(self):
        self.pc.put('MYFILE', self.small_file)

        path = os.path.join(self.pc.cache_path, 'MYFILE')
        self.assertEqual(path, self.pc.get_path('MYFILE'))
        self.assertTrue(os.path.exists(path))

    def test_remove_after_get_path(self):
        self.pc.put('MYFILE', self.small_file)
        disk_path = os.path.join(self.pc.disk_path, 'MYFILE')
        local_path = self.pc.get_path('MYFILE')

        self.assertTrue(os.path.exists(disk_path))
        self.assertTrue(os.path.exists(local_path))

        self.pc.remove('MYFILE')
        self.assertFalse(os.path.exists(disk_path))
        self.assertFalse(os.path.exists(local_path))

    def test_cache_locking(self):
        pc2 = PPlusConnection(id=self.pc.id)
        pc2.put('MYFILE', self.small_file)

        import multiprocessing

        def lock_and_unlock(pc):
            import time
            time.sleep(2)
            pc.get_path('MYFILE')

        tp = multiprocessing.Process(target=lock_and_unlock, args=(pc2,))
        tp.start()

        self.assertTrue(os.path.exists(self.pc.get_path('MYFILE')))
        tp.join()

    def test_remote_remove(self):
        self.pc.put('MYFILE', self.small_file)
        disk_path = os.path.join(self.pc.disk_path, 'MYFILE')
        local_path = self.pc.get_path('MYFILE')

        self.assertTrue(os.path.exists(disk_path))
        self.assertTrue(os.path.exists(local_path))

        os.remove(disk_path)  # remove file manually
        self.assertTrue(os.path.exists(local_path))
        self.assertRaises(PPlusError, self.pc.get_path, 'MYFILE')
        self.assertFalse(os.path.exists(local_path))

    def test_collect_without_submit(self):
        self.assertRaises(PPlusError, self.pc.collect)

    def test_submit_and_collect(self):
        params = range(10)
        for i in params:
            self.pc.submit(myjob, args=(i,))

        self.assertEquals(params, sorted(self.pc.collect()))
        self.assertEquals(params, sorted(self.pc.collect(clean_executed=True)))
        self.assertEquals([], sorted(self.pc.collect()))

    def test_resubmissions(self):
        for i in xrange(10):
            self.pc.submit(mybadjob)
        self.assertEquals([], sorted(self.pc.collect()))  # default: 0 resubs

    def test_write_remotely(self):
        with open(self.small_file, 'r') as src:
            with self.pc.write_remotely('MYFILE') as dst:
                tmp_path = dst.name
                shutil.copyfileobj(src, dst)

        path = os.path.join(self.pc.disk_path, 'MYFILE')
        self.assertTrue(os.path.exists(path))
        self.assertFalse(os.path.exists(tmp_path))

        # Same key without overwrite
        fd = self.pc.write_remotely('MYFILE', overwrite=False)
        self.assertRaises(PPlusError, fd.close)

        # Same key with overwrite
        fd = self.pc.write_remotely('MYFILE')

        tmp_path = fd.name
        path = os.path.join(self.pc.disk_path, 'MYFILE')

        self.assertTrue(os.path.exists(tmp_path))
        self.assertTrue(os.path.exists(path))
        fd.close()
        self.assertFalse(os.path.exists(tmp_path))
        self.assertTrue(os.path.exists(path))

    def test_write_remotely_content(self):
        with open(self.small_file, 'r') as src:
            with self.pc.write_remotely('MYFILE') as dst:
                shutil.copyfileobj(src, dst)

        lines_local = open(self.small_file, 'r').readlines()
        lines_remote = open(self.pc.get_path('MYFILE')).readlines()

        self.assertEquals(lines_local, lines_remote)


#------------------------------------------------------------------------------
def _test(verbosity=1):
    suite1 = unittest.TestLoader().loadTestsFromTestCase(PPlusConnectionTest)
    alltests = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=verbosity).run(alltests)
