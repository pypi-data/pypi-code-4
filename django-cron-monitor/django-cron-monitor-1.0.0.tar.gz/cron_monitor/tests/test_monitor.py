import unittest
import cron_monitor.monitor
import requests
import time
import datetime
import os
import subprocess
from mock import MagicMock, call, patch
from ConfigParser import ConfigParser
import tempfile
import json


class TestReadConfig(unittest.TestCase):

    def config_equal(self, cp1, cp2):
        b1 = (cp1.items('Server') == cp2.items('Server'))
        b2 = (cp1.getboolean('Logging', 'timestamp') ==
              cp2.getboolean('Logging', 'timestamp'))
        b3 = (cp1.items('Email') == cp2.items('Email'))
        return b1 and b2 and b3

    def test_no_name_given(self):
        """ Test that read_config gets the default values """
        cp = cron_monitor.monitor.read_config(None)
        # read_config should create the config file if it doesn't exist
        # So, don't need to check for file existing
        cp2 = ConfigParser()
        cp2.read(os.path.join(os.path.expanduser('~'), '.cronmonrc'))
        self.assertTrue(self.config_equal(cp, cp2))

    def test_invalid_name(self):
        """ If the given name could not be read, go to default """
        # Generate random unused filename
        f = tempfile.NamedTemporaryFile()
        f.close()
        cp = cron_monitor.monitor.read_config(f.name)
        default = ConfigParser()
        default.read(os.path.join(os.path.expanduser('~'), '.cronmonrc'))
        self.assertTrue(self.config_equal(cp, default))

    def test_valid_name(self):
        """ Test that reading from arbitrary file works """
        # Make sure it returns something different from the default
        cp = ConfigParser()
        cp.add_section('Server')
        cp.add_section('Logging')
        cp.add_section('Email')
        cp.set('Server', 'domain', 'http://www.noooooo.com')
        cp.set('Server', 'app_url', 'app')
        cp.set('Logging', 'timestamp', 'True')
        cp.set('Email', 'email_list', 'hello')
        cp.set('Email', 'email_on_bad_exit', 'False')
        cp.set('Email', 'email_on_stderr', 'True')
        # Generate and write to an unused file name
        new_config = tempfile.NamedTemporaryFile(delete=False)
        cp.write(new_config)
        new_config.close()

        cp2 = cron_monitor.monitor.read_config(new_config.name)
        self.assertTrue(self.config_equal(cp, cp2))
        # Clean up after
        os.remove(new_config.name)


class TestStartRecord(unittest.TestCase):
    """
    Tests the notify_of_start() method
    """

    def setUp(self):
        self.requests = patch('requests.post')
        self.poster = self.requests.start()
        self.response = self.poster.return_value

        self.date = patch('datetime.datetime')
        datetime_mock = self.date.start()
        datetime_mock.now.return_value = 'Start time here'
        datetime_mock.side_effect = \
            lambda *args, **kw: datetime.datetime(*args, **kw)

        self.args = MagicMock()
        self.args.script_args = ['echo', 'hello']
        self.args.name = None
        self.server = 'http://localhost:8000'
        self.emails = 'whatever'
        self.email_conditions = {'a': 'b'}

    def tearDown(self):
        self.date.stop()
        self.requests.stop()

    def test_no_name(self):
        """ Test that the name is defaulted to command """
        cron_monitor.monitor.notify_of_start(
            self.args, self.server, self.emails, self.email_conditions
        )
        expected_payload = {'start_time': 'Start time here',
                            'command': 'echo hello',
                            'name': 'echo hello',
                            'emails': 'whatever',
                            'conditions': json.dumps({'a': 'b'})}
        self.poster.assert_called_once_with(
            '%s/begin' % self.server,
            data=expected_payload)
        self.response.raise_for_status.assert_called_once_with()

    def test_with_name(self):
        """ Test that a customized name can be given """
        self.args.name = 'Test'
        cron_monitor.monitor.notify_of_start(
            self.args, self.server, self.emails, self.email_conditions
        )
        expected_payload = {'start_time': 'Start time here',
                            'command': 'echo hello',
                            'name': 'Test',
                            'emails': 'whatever',
                            'conditions': json.dumps({'a': 'b'})}
        self.poster.assert_called_once_with(
            '%s/begin' % self.server,
            data=expected_payload)
        self.response.raise_for_status.assert_called_once_with()

    def test_improper_id(self):
        """ Test that an exception is raised if the id given is not an int. """
        self.response.text = 'totally an integer'
        with self.assertRaises(ValueError):
            cron_monitor.monitor.notify_of_start(
                self.args, self.server, self.emails, self.email_conditions
            )

    def test_valid_id(self):
        """ Tests that the correct integer is returned. """
        self.response.text = '100'
        self.assertEqual(
            cron_monitor.monitor.notify_of_start(
                self.args, self.server, self.emails, self.email_conditions
            ),
            100
        )


class TestGetEmails(unittest.TestCase):
    """ Tests the get_emails function """
    def setUp(self):
        self.args = MagicMock()
        self.config = MagicMock()

    def test_email_parsing(self):
        """ Test that the parsing of emails works as expected. """
        self.args.emails = None
        self.config.get.return_value = 'a, b, c, d    ,e,  ,,f'
        self.assertEqual(
            ['a', 'b', 'c', 'd', 'e', 'f'],
            cron_monitor.monitor.get_emails(self.args, self.config))

    def test_args_override(self):
        """ Test that emails from args override the config """
        self.args.emails = 'a,b,c,d'
        self.config.get.return_value = 'e, f, g'
        self.assertEqual(
            ['a', 'b', 'c', 'd'],
            cron_monitor.monitor.get_emails(self.args, self.config))


class TestGetConditions(unittest.TestCase):
    """ Tests the get_conditions method. """
    def setUp(self):
        self.config = MagicMock()

    def test_attribute_assignment(self):
        self.config.getboolean.side_effect = False, True
        expected = {'email_on_bad_exit': False, 'email_on_stderr': True}
        self.assertEqual(expected,
                         cron_monitor.monitor.get_conditions(self.config))
        self.config.getboolean.side_effect = True, False
        expected = {'email_on_bad_exit': True, 'email_on_stderr': False}
        self.assertEqual(expected,
                         cron_monitor.monitor.get_conditions(self.config))


# Use a patch decorator instead of defining it in setUp
# This ensures that mocked time calls occur in the test methods
#   and regular time calls are used to time unit testing
@patch('time.time', MagicMock())
@patch('os.path.join', MagicMock())
class TestRunProcess(unittest.TestCase):
    """
    Test that run_process works correctly.

    This does not test stdbuf or timestamper.py.
    """

    def setUp(self):
        self.command = ['sleep', '10']
        self.p1 = MagicMock()
        self.p2 = MagicMock()
        self.p3 = MagicMock()
        self.patcher = patch('subprocess.Popen')
        mocked_popen = self.patcher.start()
        mocked_popen.side_effect = [self.p1, self.p2, self.p3]

    def tearDown(self):
        self.patcher.stop()

    def test_with_timestamp(self):
        """ Test that payload is modified correctly. """
        time.time.side_effect = [10, 15]
        os.path.join.return_value = 'path'
        # Check returned dictionary
        payload = cron_monitor.monitor.run_process(self.command, True)
        self.assertEqual(payload['exit_code'], self.p1.returncode)
        self.assertEqual(payload['run_time'], 5)
        self.assertEqual(payload['out_log'], self.p2.stdout.read())
        self.assertEqual(payload['err_log'], self.p3.stdout.read())
        self.assertEqual(payload['timestamp'], 'True')

        # Now check the calls to the various objects
        expected = []
        expected.append(call("stdbuf -oL -eL sleep 10".split(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE))
        expected.append(call(['python', 'path'],
                             stdin=self.p1.stdout,
                             stdout=subprocess.PIPE))
        expected.append(call(['python', 'path'],
                             stdin=self.p1.stderr,
                             stdout=subprocess.PIPE))

        self.assertEqual(os.path.join.call_count, 1)
        self.assertEqual(subprocess.Popen.call_args_list, expected)
        self.p1.stdout.close.assert_called_once_with()
        self.p1.stderr.close.assert_called_once_with()
        self.p1.wait.assert_called_once_with()
        self.p2.wait.assert_called_once_with()
        self.p3.wait.assert_called_once_with()
        self.p2.stdout.close.assert_called_once_with()
        self.p3.stdout.close.assert_called_once_with()

    def test_without_timestamp(self):
        """
        This should be almost exactly the same as the previous method.
        So, only the payload is checked (all other calls are checked by above.
        """
        time.time.side_effect = [20, 23]
        # Check returned dictionary
        payload = cron_monitor.monitor.run_process(self.command, False)
        self.assertEqual(payload['exit_code'], self.p1.returncode)
        self.assertEqual(payload['run_time'], 3)
        self.assertEqual(payload['out_log'], self.p2.stdout.read())
        self.assertEqual(payload['err_log'], self.p3.stdout.read())
        self.assertEqual(payload['timestamp'], 'False')


class TestNotifyEnd(unittest.TestCase):
    """
    Tests the notify_of_end() method
    """

    @patch('requests.post', MagicMock())
    def test_sent_request(self):
        response = MagicMock()
        requests.post.return_value = response
        server = 'whatever'
        payload = {1: 1, 2: 2}
        cron_monitor.monitor.notify_of_end(server, payload)
        requests.post.assert_called_once_with('whatever/finish',
                                              data=payload)
        response.raise_for_status.assert_called_once_with()


@patch.multiple('cron_monitor.monitor',
                read_config=MagicMock(),
                notify_of_start=MagicMock(),
                run_process=MagicMock(),
                notify_of_end=MagicMock(),
                get_emails=MagicMock(),
                get_conditions=MagicMock())
class TestWatch(unittest.TestCase):
    """
    Tests the watch method
    """

    def setUp(self):
        self.args = MagicMock()

    def test_no_command(self):
        self.args.script_args = None
        self.assertRaises(ValueError, cron_monitor.monitor.watch, self.args)

    def test_attribute_assignment(self):
        """ Test that attributes are assigned correctly. """
        self.config = cron_monitor.monitor.read_config.return_value
        cron_monitor.monitor.get_emails.return_value = 'emails'
        cron_monitor.monitor.get_conditions.return_value = {1: 2}

        def set_args(domain, timestamp, app_url):
            self.args.domain = domain
            self.args.time = timestamp
            self.args.appurl = app_url

        def set_config(domain, timestamp, app_url):
            self.config.get.side_effect = [domain, app_url]
            self.config.getboolean.return_value = timestamp

        # args None case
        set_args(None, None, None)
        set_config('http://localhost:8000', True, 'app')
        cron_monitor.monitor.watch(self.args)
        cron_monitor.monitor.notify_of_start.assert_called_with(
            self.args, 'http://localhost:8000/app', 'emails', {1: 2}
        )
        cron_monitor.monitor.run_process.assert_called_with(
            command=self.args.script_args,
            timestamp=True
        )

        # args valid case
        set_args('http://host:0', False, 'app2')
        set_config('http://localhost:8000', True, 'app')
        cron_monitor.monitor.watch(self.args)
        cron_monitor.monitor.notify_of_start.assert_called_with(
            self.args, 'http://host:0/app2', 'emails', {1: 2}
        )
        cron_monitor.monitor.run_process.assert_called_with(
            command=self.args.script_args,
            timestamp=False
        )

        # Test miscellaneous calls
        cron_monitor.monitor.get_emails.assert_called_with(
            self.args, self.config)
        cron_monitor.monitor.get_conditions.assert_called_with(self.config)

    def test_payload_modification(self):
        """ Test that the payload is modified correctly. """
        self.args.script_args = ['echo', 'asdf']
        cron_monitor.monitor.notify_of_start.return_value = 5  # The record id

        # No output
        payload = {'rec_id': 5, 'out_log': '', 'err_log': ''}
        cron_monitor.monitor.run_process.return_value = payload
        cron_monitor.monitor.watch(self.args)
        passed_dict = cron_monitor.monitor.notify_of_end.call_args[0][1]
        self.assertFalse('plain_log_name' in passed_dict)
        self.assertFalse('html_log_name' in passed_dict)

        # Only stdout
        payload['out_log'] = 'asdf'
        cron_monitor.monitor.watch(self.args)
        passed_dict = cron_monitor.monitor.notify_of_end.call_args[0][1]
        self.assertEqual(passed_dict['plain_log_name'], 'echo_asdf_5.log')
        self.assertEqual(passed_dict['html_log_name'], 'echo_asdf_5.html')

        # Both
        payload['err_log'] = 'oh noooooooo'
        cron_monitor.monitor.watch(self.args)
        passed_dict = cron_monitor.monitor.notify_of_end.call_args[0][1]
        self.assertEqual(passed_dict['plain_log_name'], 'echo_asdf_5.log')
        self.assertEqual(passed_dict['html_log_name'], 'echo_asdf_5.html')

        # Only stderr
        payload['out_log'] = ''
        cron_monitor.monitor.watch(self.args)
        passed_dict = cron_monitor.monitor.notify_of_end.call_args[0][1]
        self.assertEqual(passed_dict['plain_log_name'], 'echo_asdf_5.log')
        self.assertEqual(passed_dict['html_log_name'], 'echo_asdf_5.html')

# No tests for the main method
