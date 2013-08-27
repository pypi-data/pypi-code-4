from mock import patch, MagicMock
from subprocess import CalledProcessError
from .base import Base
from deployer.utils import dict_merge, _check_call, ErrorExit


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
            _e, _e, 'good', _e ]
        output = _check_call(params=['magybe_fail'], log=MagicMock(), max_retry=3)
        self.assertEquals(output, 'good')
        # 1 failure + 3 retries
        self.assertEquals(len(check_output.call_args_list), 3)
