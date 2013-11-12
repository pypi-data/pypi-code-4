import os
from subprocess import CalledProcessError

from mock import patch, MagicMock

from .base import Base
from deployer.utils import (
    _check_call,
    dict_merge,
    ErrorExit,
    mkdir,
)


class UtilTests(Base):

    def test_relation_list_merge(self):
        self.assertEqual(
            dict_merge(
                {'relations': [['m1', 'x1']]},
                {'relations': [['m2', 'x2']]}),
            {'relations': [['m1', 'x1'], ['m2', 'x2']]})

    def test_no_rels_in_target(self):
        self.assertEqual(
            dict_merge(
                {'a': 1},
                {'relations': [['m1', 'x1'], ['m2', 'x2']]}),
            {'a': 1, 'relations': [['m1', 'x1'], ['m2', 'x2']]})

    @patch('subprocess.check_output')
    def test_check_call_fail_no_retry(self, check_output):
        _e = CalledProcessError(returncode=1, cmd=['fail'])
        check_output.side_effect = _e
        self.assertRaises(
            ErrorExit, _check_call, params=['fail'], log=MagicMock())

    @patch('time.sleep')
    @patch('subprocess.check_output')
    def test_check_call_fail_retry(self, check_output, sleep):
        _e = CalledProcessError(returncode=1, cmd=['fail'])
        check_output.side_effect = _e
        self.assertRaises(
            ErrorExit, _check_call, params=['fail'], log=MagicMock(), max_retry=3)
        # 1 failure + 3 retries
        self.assertEquals(len(check_output.call_args_list), 4)

    @patch('time.sleep')
    @patch('subprocess.check_output')
    def test_check_call_succeed_after_retry(self, check_output, sleep):
        # call succeeds after the 3rd try
        _e = CalledProcessError(returncode=1, cmd=['maybe_fail'])
        check_output.side_effect = [
            _e, _e, 'good', _e]
        output = _check_call(
            params=['magybe_fail'], log=MagicMock(), max_retry=3)
        self.assertEquals(output, 'good')
        # 1 failure + 3 retries
        self.assertEquals(len(check_output.call_args_list), 3)


class TestMkdir(Base):

    def setUp(self):
        self.playground = self.mkdir()

    def test_create_dir(self):
        # A directory is correctly created.
        path = os.path.join(self.playground, 'foo')
        mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_intermediate_dirs(self):
        # All intermediate directories are created.
        path = os.path.join(self.playground, 'foo', 'bar', 'leaf')
        mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_expand_user(self):
        # The ~ construction is expanded.
        with patch('os.environ', {'HOME': self.playground}):
            mkdir('~/in/my/home')
        path = os.path.join(self.playground, 'in', 'my', 'home')
        self.assertTrue(os.path.isdir(path))

    def test_existing_dir(self):
        # The function exits without errors if the target directory exists.
        path = os.path.join(self.playground, 'foo')
        os.mkdir(path)
        mkdir(path)

    def test_existing_file(self):
        # An OSError is raised if a file already exists in the target path.
        path = os.path.join(self.playground, 'foo')
        with open(path, 'w'):
            with self.assertRaises(OSError):
                mkdir(path)

    def test_failure(self):
        # Errors are correctly re-raised.
        path = os.path.join(self.playground, 'foo')
        os.chmod(self.playground, 0000)
        self.addCleanup(os.chmod, self.playground, 0700)
        with self.assertRaises(OSError):
            mkdir(os.path.join(path))
        self.assertFalse(os.path.exists(path))
