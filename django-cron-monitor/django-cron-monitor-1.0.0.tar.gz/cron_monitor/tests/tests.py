"""
These will pass when you run "manage.py test".
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from cron_monitor.models import (Job, Log, Record,
                                 EmailConditions, EmailSettings)
from cron_monitor.models import GlobalEmailAddress
import datetime
import cron_monitor.views
from tempfile import TemporaryFile
from cStringIO import StringIO
from mock import MagicMock, patch, call
from Crypto import Random
from Crypto.Cipher import AES
import json
import smtplib
import base64


class LogMethodTests(TestCase):
    """ Test that the custom methods for Log work. """

    def setUp(self):
        job = Job.objects.create(name='q')
        start = datetime.datetime(2000, 10, 10)
        self.record = Record.objects.create(command='d',
                                            start_time=start,
                                            job=job)
        self.log = Log(log_name='hello.txt', log_text='hi', record=self.record)

    def test_invalid_log(self):
        """ Test that this log causes clean() to raise an exception """
        self.log.log_type = Log.NULL_LOG_TYPE
        self.assertEqual(unicode(self.log), u'hello.txt, invalid log')
        with self.assertRaises(ValidationError):
            self.log.clean()

    def test_plain_log(self):
        """ Test that plain logs are valid """
        self.log.log_type = Log.PLAIN_LOG_TYPE
        self.assertEqual(unicode(self.log), u'hello.txt, text log')
        self.log.clean()

    def test_html_log(self):
        """ Test that html logs are valid """
        self.log.log_type = Log.HTML_LOG_TYPE
        self.assertEqual(unicode(self.log), u'hello.txt, html log')
        self.log.clean()

    def test_absolute_url(self):
        self.log.log_type = Log.HTML_LOG_TYPE
        self.log.save()
        self.assertEqual(self.log.get_absolute_url(),
                         reverse('html_log', args=[self.record.pk]))
        self.log.log_type = Log.PLAIN_LOG_TYPE
        self.log.save()
        self.assertEqual(self.log.get_absolute_url(),
                         reverse('plain_log', args=[self.log.pk]))
        self.log.log_type = Log.NULL_LOG_TYPE
        self.assertRaises(ValueError, self.log.get_absolute_url)


class RecordMethodTests(TestCase):
    def setUp(self):
        start = datetime.datetime(2000, 10, 10)
        # Need a dummy job for the record to attach to
        # which is needed to give the record a valid id
        # which is needed to assign logs to the record for testing
        self.job = Job.objects.create(name='d')
        self.record = self.job.record_set.create(command='sleep 1',
                                                 start_time=start)
        self.log_plain = Log(log_name='plain',
                             log_text='asdf',
                             log_type=Log.PLAIN_LOG_TYPE)
        self.log_html = Log(log_name='html',
                            log_text='jkl;',
                            log_type=Log.HTML_LOG_TYPE)

    def test_record_unicode(self):
        """ Get that coverage """
        self.assertEqual(unicode(self.record),
                         u'sleep 1, %s' % str(self.record.start_time))

    def test_record_sort_order(self):
        """
        Records by default are sorted by start time
        Most recent come first
        """
        # Default record start_time is 2000-10-10
        start2 = datetime.datetime(1999, 12, 10)
        start3 = datetime.datetime(2000, 1, 1)
        rec2 = self.job.record_set.create(command='d', start_time=start2)
        rec3 = self.job.record_set.create(command='d', start_time=start3)
        records = Record.objects.all()
        self.assertEqual(records[0], self.record)
        self.assertEqual(records[1], rec3)
        self.assertEqual(records[2], rec2)

    def test_plain_log(self):
        """ Test that plain_log() gives the right log """
        self.assertIsNone(self.record.plain_log())
        self.record.log_set.add(self.log_plain)
        self.assertEqual(self.record.plain_log(), self.log_plain)
        self.record.log_set.add(self.log_html)
        self.assertEqual(self.record.plain_log(), self.log_plain)

    def test_html_log(self):
        """ Test that html_log() gives the right log """
        self.assertIsNone(self.record.html_log())
        self.record.log_set.add(self.log_plain)
        self.assertIsNone(self.record.html_log())
        self.record.log_set.add(self.log_html)
        self.assertEqual(self.record.html_log(), self.log_html)

    def test_record_clean(self):
        """ Test that the clean() method behaves as expected. """
        # Neither (also tests 0 logs)
        self.record.clean()
        # Exit code only
        self.record.exit_code = 0
        self.assertRaises(ValidationError, self.record.clean)
        # Both
        self.record.run_time = 1
        self.record.clean()
        # Run time only
        self.record.exit_code = None
        self.assertRaises(ValidationError, self.record.clean)
        # Reset for next part
        self.record.exit_code = 1

        # Now test for log validation
        # One log
        self.record.log_set.add(self.log_plain)
        self.assertRaises(ValidationError, self.record.clean)
        # Two logs, plain and html
        self.record.log_set.add(self.log_html)
        self.record.clean()
        # Two html
        self.log_plain.log_type = Log.HTML_LOG_TYPE
        self.log_plain.save()
        self.assertRaises(ValidationError, self.record.clean)
        # Two plain
        self.log_plain.log_type = Log.PLAIN_LOG_TYPE
        self.log_html.log_type = Log.PLAIN_LOG_TYPE
        self.log_plain.save()
        self.log_html.save()
        self.assertRaises(ValidationError, self.record.clean)
        # Three logs
        log_3 = Log(log_name='3', log_text='3', log_type=Log.PLAIN_LOG_TYPE)
        self.record.log_set.add(log_3)
        self.assertRaises(ValidationError, self.record.clean)


class JobMethodTests(TestCase):
    def setUp(self):
        self.job = Job.objects.create(name='testjob')

    def test_job_unicode(self):
        self.assertEqual(unicode(self.job), u'testjob')

    def test_fail_job_clean(self):
        """ Test that a job needs a record. """
        self.assertRaises(ValidationError, self.job.clean)

    def test_pass_job_clean(self):
        """ Test that a job passes if it has a record. """
        self.job.record_set.create(command='echo asdf',
                                   start_time=datetime.datetime(2000, 10, 10))
        self.job.clean()

    def test_set_addresses(self):
        self.job.emailaddress_set.create(address='removed_later')
        address_list = ['a@a.com', 'b@b.com', 'c@c.com']
        self.assertEqual(self.job.emailaddress_set.count(), 1)
        self.job.set_addresses(address_list)
        self.assertEqual(self.job.emailaddress_set.count(), 3)

    def test_set_conditions(self):
        self.job.emailconditions = EmailConditions(job=self.job)
        cond = {'email_on_bad_exit': False, 'email_on_stderr': True}
        self.assertTrue(self.job.emailconditions.email_on_bad_exit)
        self.assertFalse(self.job.emailconditions.email_on_stderr)
        self.job.set_conditions(cond)
        self.assertFalse(self.job.emailconditions.email_on_bad_exit)
        self.assertTrue(self.job.emailconditions.email_on_stderr)


class EmailSettingsMethodTests(TestCase):
    """ Tests the custom methods in EmailSettings """

    def setUp(self):
        self.e_settings = EmailSettings.objects.create()

    def test_padding_unpadding(self):
        """
        Test that padding creates a message of the right size,
        and unpadding a padded message returns the original.
        """
        # This should work for any string
        # Randomly generate strings of different lengths
        bs = AES.block_size
        gen = Random.new()
        for i in range(bs, 2 * bs):
            s = gen.read(i)
            pad_s = self.e_settings.pad(s)
            self.assertEqual(len(pad_s) % bs, 0)
            self.assertEqual(s, self.e_settings.unpad(pad_s))
        gen.close()

    def test_encrypt_decrypt(self):
        """
        Tests that encrypting and decrypting a password gives the original back
        """
        bs = AES.block_size
        gen = Random.new()
        for i in range(bs, 2 * bs):
            s = gen.read(i)
            enc_s = self.e_settings.encrypt(s)
            self.assertEqual(s, self.e_settings.decrypt(enc_s))
        gen.close()

    def test_save(self):
        """
        Test that when the password is saved, it is encrypted.
        """
        # To ensure the plaintext and encrypted text are different,
        # the password is deliberately something that must be padded
        # If this isn't done, there's a small chance that a password
        # is encrypted to itself
        bs = AES.block_size
        gen = Random.new()
        self.e_settings.email_host_password = ''
        self.e_settings.save()
        self.assertEqual(self.e_settings.email_host_password, '')

        pw = gen.read(bs - 1)
        self.e_settings.email_host_password = pw
        self.e_settings.save()
        # Compare the Base64 representations
        # (the assert tries to convert pw to unicode, which fails
        #   due to encoding problems. Converting to base 64 fixes this.)
        self.assertNotEqual(
            base64.b64encode(self.e_settings.email_host_password),
            base64.b64encode(pw)
        )
        gen.close()

    def test_get_password(self):
        self.e_settings.email_host_password = ''
        self.e_settings.save()
        self.assertEqual(self.e_settings.get_password(), '')

        self.e_settings.email_host_password = 'asdfjkl;'
        self.e_settings.save()
        self.assertEqual(self.e_settings.get_password(), 'asdfjkl;')

    def test_absolute_url(self):
        self.assertEqual(self.e_settings.get_absolute_url(),
                         reverse('settings_update', args=[self.e_settings.pk]))


class DisplayIndexViewTests(TestCase):
    def setUp(self):
        start = datetime.datetime(2000, 10, 10)
        self.job = Job.objects.create(name="sleep 10")
        self.record = self.job.record_set.create(command=self.job.name,
                                                 start_time=start)
        self.user = User.objects.create_user(
            username='testuser', password='hello'
        )

    def test_index_no_jobs(self):
        """
        Test content when no jobs are tracked
        """
        self.job.delete()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 0)

    def test_index_running_job(self):
        """
        Test that a job that hasn't finished is displayed correctly
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context['jobs']))
        self.assertEqual(self.job, response.context['jobs'][0])
        self.assertContains(response, 'Running')
        self.assertIsNone(self.record.exit_code)
        self.assertIsNone(self.record.run_time)

    def test_index_passed_job(self):
        """
        Test a job that has finished with exit code 0 is displayed right
        """
        self.record.exit_code = 0
        self.record.run_time = 10
        self.record.save()
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Done (exit code 0)')
        self.assertEqual(1, len(response.context['jobs']))

    def test_index_failed_job(self):
        """
        Test a job that has failed (finished with non-zero exit code)
        """
        self.record.exit_code = 1
        self.record.run_time = 10
        self.record.save()
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Failed')

    def test_not_logged_in(self):
        """
        Test that when not logged in, there is a link to a login page
        """
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Log In')
        self.assertContains(response, reverse('login'))

    def test_logged_in_no_settings(self):
        """
        Test that there are links for when the user is logged in
        """
        self.client.login(username='testuser', password='hello')
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Currently logged in as testuser')
        self.assertContains(response, reverse('logout'))
        self.assertContains(response, reverse('global'))
        self.assertContains(response, reverse('settings_add'))

    def test_logged_in_with_settings(self):
        # There's a default for everything
        settings = EmailSettings.objects.create()
        self.client.login(username='testuser', password='hello')
        response = self.client.get(reverse('index'))
        self.assertContains(response, settings.get_absolute_url())


class DisplayLogoutTests(TestCase):
    """ Tests the logout view. """

    def setUp(self):
        User.objects.create_user(username='b', password='b')

    def test_redirect(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))

    def test_logout(self):
        # Testing if the client is logged in is surprisingly odd to do
        self.client.login(username='b', password='b')
        self.assertIn('_auth_user_id', self.client.session)
        self.client.get(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)


@patch.multiple('cron_monitor.models.Job',
                set_conditions=MagicMock(),
                set_addresses=MagicMock())
class DisplayBeginRunTests(TestCase):
    def test_begin_missing_information(self):
        """
        It should error if the POST request does not have the right fields
        Tests for existence of 'command' and 'start_time'
        """
        payload = {'best_fruit': 'banana',
                   'tomayto': 'tomahto'}
        with self.assertRaises(KeyError):
            self.client.post(reverse('begin'), data=payload)

    def test_added_job(self):
        """
        Test that a job is created if the name given is unknown.
        And that the correct id is returned
        """
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(EmailConditions.objects.count(), 0)

        start = datetime.datetime(1990, 1, 1)
        payload = {'command': 'echo asf',
                   'start_time': str(start),
                   'name': 'echo asf',
                   'emails': ['email1', 'email2'],
                   'conditions': json.dumps({'a': 1})}
        response = self.client.post(reverse('begin'), data=payload)

        cron_monitor.models.Job.set_conditions.assert_called_with({'a': 1})
        cron_monitor.models.Job.set_addresses.assert_called_with(
            ['email1', 'email2']
        )
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(EmailConditions.objects.count(), 1)

        job = Job.objects.all()[0]
        record = job.record_set.all()[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, str(record.pk))
        self.assertEqual(record.command, 'echo asf')
        self.assertEqual(record.start_time, start)

    def test_job_already_there(self):
        """
        Test that if there is a job with the given name, no new job is made
        """
        job = Job.objects.create(name='sleep')
        EmailConditions.objects.create(job=job)
        start = datetime.datetime(1990, 1, 1)
        payload = {'command': 'sleep 3',
                   'name': 'sleep',
                   'start_time': str(start),
                   'emails': ['email1', 'email2'],
                   'conditions': json.dumps({'a': 1})}
        response = self.client.post(reverse('begin'), data=payload)
        # Other calls should be checked by above
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(EmailConditions.objects.count(), 1)
        record = job.record_set.all()[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, str(record.pk))
        self.assertEqual(record.command, 'sleep 3')
        self.assertEqual(record.start_time, start)

    def test_missing_start_time(self):
        """
        Test that if the start time is missing, it is filled in automatically
        """
        job = Job.objects.create(name='sleep')
        EmailConditions.objects.create(job=job)
        payload = {'command': 'sleep 3',
                   'name': 'sleep',
                   'emails': ['email1', 'email2'],
                   'conditions': json.dumps({'a': 1})}
        self.client.post(reverse('begin'), data=payload)
        record = job.record_set.all()[0]
        self.assertIsNotNone(record.start_time)

    def test_begin_non_post(self):
        """
        Should error if a non POST request is sent
        """
        response = self.client.get(reverse('begin'))
        self.assertEqual(response.status_code, 405)


class MergeTests(TestCase):
    """
    Test the methods that are used when merging stdout and stderr together.
    """
    def test_html_escape(self):
        from string import ascii_letters
        text = u"%s\'\"/<>&" % ascii_letters
        self.assertEqual(cron_monitor.views.html_escape(text),
                         u"%s&#x27;&quot;&#x2F;&lt;&gt;&amp;" % ascii_letters)

    def test_get_time_and_text(self):
        # Test no space
        self.assertRaises(ValueError,
                          cron_monitor.views.get_time_and_text, 'asdf')
        # Test valid line
        time = 1234567
        line = '%d Hello world.\n' % time
        time2, line2 = cron_monitor.views.get_time_and_text(line)
        self.assertEqual(time, time2)
        self.assertEqual(line2, 'Hello world.\n')

    def add_time(self, time, line):
        return "%d %s" % (time, line)

    def set_up_files(self):
        out = TemporaryFile()
        err = TemporaryFile()
        times = range(4)
        print >> out, self.add_time(times[0], "Line 0")
        print >> err, self.add_time(times[1], "Line 1")
        print >> out, self.add_time(times[2], "Line 2")
        print >> err, self.add_time(times[3], "Line 3")
        out.seek(0)
        err.seek(0)
        return out, err

    def set_up_files2(self):
        """ Catch more edge cases """
        out = TemporaryFile()
        err = TemporaryFile()
        times = range(4)
        print >> out, self.add_time(times[0], "Line 0")
        print >> out, self.add_time(times[1], "Line 1")
        print >> err, self.add_time(times[2], "Line 2")
        print >> out, self.add_time(times[3], "Line 3")
        out.seek(0)
        err.seek(0)
        return out, err

    def test_merge_timestamp_true(self):
        """
        Tests that the lines of output are merged into the correct order
        """
        out, err = self.set_up_files()
        expected_plain = "%s %s%s %s%s %s%s %s" \
            % (cron_monitor.views.local_time_string(0), 'Line 0\n',
               cron_monitor.views.local_time_string(1), 'Line 1\n',
               cron_monitor.views.local_time_string(2), 'Line 2\n',
               cron_monitor.views.local_time_string(3), 'Line 3\n')
        expected_html = '<span class="stdout">%s %s</span>' \
                        '<span class="stderr">%s %s</span>' \
                        '<span class="stdout">%s %s</span>' \
                        '<span class="stderr">%s %s</span>' \
                        % (cron_monitor.views.local_time_string(0), 'Line 0\n',
                           cron_monitor.views.local_time_string(1), 'Line 1\n',
                           cron_monitor.views.local_time_string(2), 'Line 2\n',
                           cron_monitor.views.local_time_string(3), 'Line 3\n')
        plain, html = StringIO(), StringIO()
        cron_monitor.views.merge(True, out, err, plain, html)
        self.assertTrue(out.closed)
        self.assertTrue(err.closed)
        self.assertEqual(plain.getvalue(), expected_plain)
        self.assertEqual(html.getvalue(), expected_html)
        plain.close()
        html.close()

    def test_merge_timestamp_false(self):
        """ Almost the same as previous test """
        out, err = self.set_up_files2()
        expected_plain = "%s%s%s%s" % ('Line 0\n',
                                       'Line 1\n',
                                       'Line 2\n',
                                       'Line 3\n')
        expected_html = '<span class="stdout">%s</span>' \
                        '<span class="stdout">%s</span>' \
                        '<span class="stderr">%s</span>' \
                        '<span class="stdout">%s</span>' \
                        % ('Line 0\n', 'Line 1\n',
                           'Line 2\n', 'Line 3\n')
        plain, html = StringIO(), StringIO()
        cron_monitor.views.merge(False, out, err, plain, html)
        self.assertTrue(out.closed)
        self.assertTrue(err.closed)
        self.assertEqual(plain.getvalue(), expected_plain)
        self.assertEqual(html.getvalue(), expected_html)
        plain.close()
        html.close()


@patch('cron_monitor.views.check_send_emails', MagicMock())
class DisplayFinishRunTests(TestCase):
    def setUp(self):
        # Make a dummy job for the record to attach to
        job = Job.objects.create(name='hello')
        EmailConditions.objects.create(job=job)
        start = datetime.datetime(1990, 10, 10)
        self.record = job.record_set.create(command='sleep 2',
                                            start_time=start)

    def test_finish_missing_information(self):
        """
        It should error if the POST request does not have the right fields
        """
        payload = {'best_fruit': 'banana',
                   'tomayto': 'tomahto'}
        with self.assertRaises(KeyError):
            self.client.post(reverse('finish'), data=payload)

    def test_invalid_record_id(self):
        """
        Giving an id that is not an integer should cause a ValidationError
        """
        with self.assertRaises(ValidationError):
            self.client.post(reverse('finish'), data={'rec_id': 'f'})

    def test_wrong_record_id(self):
        """
        Giving an id that does not correspond to any Record should raise a 404
        """
        payload = {'rec_id': self.record.pk+1,
                   'exit_code': 0,
                   'run_time': 5}
        response = self.client.post(reverse('finish'), data=payload)
        self.assertEqual(response.status_code, 404)

    def test_closed_run_no_output(self):
        """
        Sending a valid POST request should update the record in the database
        """
        payload = {'rec_id': self.record.pk,
                   'exit_code': 0,
                   'run_time': 2.05,
                   'out_log': '',
                   'err_log': ''}
        self.client.post(reverse('finish'), data=payload)
        self.assertEqual(Record.objects.count(), 1)
        record = Record.objects.all()[0]
        self.assertEqual(record.exit_code, 0)
        self.assertEqual(str(record.run_time), '2.05')
        self.assertEqual(record.log_set.count(), 0)
        self.assertFalse(record.has_err)
        cron_monitor.views.check_send_emails.assert_called_with(record)

    def test_closed_run_with_timestamp(self):
        """
        Test a run which displays the timestamps
        """
        payload = {'rec_id': self.record.pk,
                   'exit_code': 0,
                   'run_time': 2.05,
                   'plain_log_name': 'this_does_not_matter',
                   'out_log': '1000 Completed successfully\n',
                   'html_log_name': 'also_does_not_matter',
                   'err_log': '1034 Stuff\n',
                   'timestamp': 'True'}
        self.client.post(reverse('finish'), data=payload)
        self.assertEqual(Record.objects.count(), 1)
        rec = Record.objects.all()[0]
        self.assertEqual(rec.log_set.count(), 2)
        self.assertTrue(rec.has_err)
        cron_monitor.views.check_send_emails.assert_called_with(rec)

        log_plain = rec.log_set.get(log_type=Log.PLAIN_LOG_TYPE)
        log_html = rec.log_set.get(log_type=Log.HTML_LOG_TYPE)

        out_line = '%s %s' % (cron_monitor.views.local_time_string(1000),
                              'Completed successfully\n')
        err_line = '%s %s' % (cron_monitor.views.local_time_string(1034),
                              'Stuff\n')
        self.assertEqual(log_plain.log_text, '%s%s' % (out_line, err_line))
        self.assertEqual(log_plain.log_name, payload['plain_log_name'])
        self.assertEqual(log_html.log_name, payload['html_log_name'])

    def test_closed_run_no_timestamp(self):
        """
        Test a run which displays the timestamps
        """
        payload = {'rec_id': self.record.pk,
                   'exit_code': 0,
                   'run_time': 2.05,
                   'plain_log_name': 'this_does_not_matter',
                   'out_log': '1000 Completed successfully\n',
                   'html_log_name': 'also_does_not_matter',
                   'err_log': '1001 Stuff\n',
                   'timestamp': 'False'}
        self.client.post(reverse('finish'), data=payload)
        self.assertEqual(Record.objects.count(), 1)
        rec = Record.objects.all()[0]
        self.assertEqual(rec.log_set.count(), 2)
        self.assertTrue(rec.has_err)
        cron_monitor.views.check_send_emails.assert_called_with(rec)

        log_plain = rec.log_set.get(log_type=Log.PLAIN_LOG_TYPE)
        log_html = rec.log_set.get(log_type=Log.HTML_LOG_TYPE)
        self.assertEqual(log_plain.log_text,
                         "Completed successfully\nStuff\n")
        self.assertEqual(log_plain.log_name, payload['plain_log_name'])
        self.assertEqual(log_html.log_name, payload['html_log_name'])

    def test_closed_run_bad_post(self):
        """
        If the POST request has only an out log or only an err log,
        it should cause an error
        """
        payload = {'rec_id': self.record.pk,
                   'exit_code': 1,
                   'run_time': 2.05,
                   'plain_log_name': 'whatever',
                   'html_log_name': 'this_does_not_matter',
                   'err_log': 'I swallowed a bug'}
        with self.assertRaises(KeyError):
            self.client.post(reverse('finish'), data=payload)
        del payload['err_log']
        payload['out_log'] = 'test'
        with self.assertRaises(KeyError):
            self.client.post(reverse('finish'), data=payload)

    def test_missing_run_time(self):
        """
        If the run time is missing, it should be filled in automatically
        """
        payload = {'rec_id': self.record.pk,
                   'exit_code': 0,
                   'out_log': '',
                   'err_log': ''}
        self.client.post(reverse('finish'), data=payload)
        record = Record.objects.get(pk=self.record.pk)
        self.assertIsNotNone(record.run_time)

    def test_finish_non_post(self):
        """
        Should error if a non POST request is sent
        """
        response = self.client.get(reverse('finish'))
        self.assertEqual(response.status_code, 405)


@patch('cron_monitor.views.send_email', MagicMock())
class CheckSendEmailTests(TestCase):
    """ Tests the conditions under which emails are sent. """
    def setUp(self):
        # Make a dummy job for the record and conditions to attach to
        self.job = Job.objects.create(name='hello')
        self.conditions = EmailConditions.objects.create(job=self.job)
        self.start = datetime.datetime(1990, 10, 10)
        self.record = self.job.record_set.create(command='sleep 2',
                                                 start_time=self.start,
                                                 exit_code=1,
                                                 run_time=10)
        # Add one email to ensure there is always an address to send to
        self.job.emailaddress_set.create(address='hi@hi.com')

    def test_send_on_bad_exit(self):
        # When patch is used as class decorator, that mock is used for all
        # tests. So, method calls to the mock persist across tests.
        # Reset the mock to deal with this
        # mock isn't defined when setUp runs, have to run in every test method
        cron_monitor.views.send_email.reset_mock()
        self.conditions.email_on_bad_exit = True
        self.conditions.email_on_stderr = False
        self.conditions.save()
        self.record.exit_code = 0
        self.record.save()

        cron_monitor.views.check_send_emails(self.record)
        self.assertEqual(cron_monitor.views.send_email.call_count, 0)
        self.record.exit_code = 1
        self.record.save()
        cron_monitor.views.check_send_emails(self.record)
        self.assertEqual(cron_monitor.views.send_email.call_count, 1)

    def test_send_on_stderr(self):
        cron_monitor.views.send_email.reset_mock()
        self.conditions.email_on_bad_exit = False
        self.conditions.email_on_stderr = True
        self.conditions.save()
        self.record.has_err = False
        self.record.save()

        cron_monitor.views.check_send_emails(self.record)
        self.assertEqual(cron_monitor.views.send_email.call_count, 0)
        self.record.has_err = True
        self.record.save()
        cron_monitor.views.check_send_emails(self.record)
        self.assertEqual(cron_monitor.views.send_email.call_count, 1)

    def test_email_construction(self):
        cron_monitor.views.send_email.reset_mock()
        cron_monitor.views.check_send_emails(self.record)
        # get *args and unpack
        subject, message, address_list = \
            cron_monitor.views.send_email.call_args[0]
        self.assertEqual(subject, 'Failed sleep 2 at %s' % str(self.start))
        expected_msg = 'The command "sleep 2" that ran at %s has failed.\n\n' \
                       'Exit code: 1\n\nLog:\n' \
                       % str(self.start)
        self.assertEqual(message, expected_msg)
        self.assertEqual(address_list, ['hi@hi.com'])

    def test_address_list_construction(self):
        cron_monitor.views.send_email.reset_mock()
        self.job.emailaddress_set.create(address='b@b.com')
        GlobalEmailAddress.objects.create(address='a@a.com')
        GlobalEmailAddress.objects.create(address='c@c.com')

        cron_monitor.views.check_send_emails(self.record)
        address_list = cron_monitor.views.send_email.call_args[0][2]
        self.assertEqual(address_list,
                         ['hi@hi.com', 'b@b.com', 'a@a.com', 'c@c.com'])

    def test_no_addresses(self):
        cron_monitor.views.send_email.reset_mock()
        self.job.emailaddress_set.all().delete()
        cron_monitor.views.check_send_emails(self.record)
        self.assertEqual(cron_monitor.views.send_email.call_count, 0)


@patch('smtplib.SMTP', MagicMock())
class SendEmailTests(TestCase):
    """ Tests the send_email method. """
    def setUp(self):
        self.settings = EmailSettings.objects.create()

    def test_no_settings(self):
        smtplib.SMTP.reset_mock()
        self.settings.delete()
        cron_monitor.views.send_email('hi', 'bye', ['a@a.com'])
        self.assertEqual(smtplib.SMTP.call_count, 0)

    # None of the email sending tests will test the message content
    # These methods test the addresses sent to and from
    def test_basic_email(self):
        """ Test sending an email with no authentication. """
        session = smtplib.SMTP.return_value
        cron_monitor.views.send_email('hi', 'bye', ['a@a.com'])
        from_email, to_emails, msg = session.sendmail.call_args[0]
        self.assertEqual(from_email, 'monitor@localhost')
        self.assertEqual(to_emails, ['a@a.com'])
        session.quit.assert_called_with()

    def test_use_tls(self):
        session = smtplib.SMTP.return_value
        session.reset_mock()
        self.settings.use_tls = True
        self.settings.save()
        cron_monitor.views.send_email('hi', 'bye', ['a@a.com'])
        expected = [call.ehlo(), call.starttls(), call.ehlo()]
        self.assertEqual(expected, session.method_calls[:3])

    def test_authentication(self):
        session = smtplib.SMTP.return_value
        self.settings.email_host_user = 'harry'
        self.settings.email_host_password = 'potter'
        self.settings.save()
        cron_monitor.views.send_email('hi', 'bye', ['a@a.com'])
        session.login.assert_called_with('harry', 'potter')
        from_email, to_emails, msg = session.sendmail.call_args[0]
        self.assertEqual(from_email, 'harry')
        self.assertEqual(to_emails, ['a@a.com'])


class DisplayDeleteTests(TestCase):
    def test_invalid_id(self):
        """
        Giving an invalid id should return a bad request
        """
        response = self.client.post(reverse('delete'), data={'rec_id': 's'})
        self.assertEqual(response.status_code, 400)

    def test_wrong_id(self):
        """
        Giving a wrong id should raise a 404
        """
        # No records
        response = self.client.post(reverse('delete'), data={'rec_id': 1})
        self.assertEqual(response.status_code, 404)

    def test_record_deletion(self):
        """
        Test that if a valid id is given, the record is deleted
        """
        # Dummy job
        job = Job.objects.create(name='test')
        records = [Record(command='hi',
                          start_time=datetime.datetime(2000, 10, 10),
                          job=job)
                   for _ in range(4)]
        for rec in records:
            rec.save()
        keys = [records[i].pk for i in range(4)]

        payload = {'rec_id': keys[1]}
        response = self.client.post(reverse('delete'), data=payload)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Record.objects.count(), 3)
        for rec in Record.objects.all():
            self.assertNotEqual(rec.pk, keys[1])

        payload['rec_id'] = keys[0]
        response = self.client.post(reverse('delete'), data=payload)
        self.assertEqual(Record.objects.count(), 2)
        for rec in Record.objects.all():
            self.assertNotEqual(rec.pk, keys[0])

    def test_job_deletion(self):
        """ Test that if the last record is deleted, the job is deleted """
        job = Job.objects.create(name='test')
        start = datetime.datetime(2000, 10, 10)
        record = job.record_set.create(command='hi',
                                       start_time=start)
        self.client.post(reverse('delete'), data={'rec_id': record.pk})
        self.assertEqual(Record.objects.count(), 0)
        self.assertEqual(Job.objects.count(), 0)

    def test_delete_non_post(self):
        """ Giving a non-POST request should error. """
        response = self.client.get(reverse('delete'))
        self.assertEqual(response.status_code, 405)


class DisplayDeleteJobTests(TestCase):

    def test_invalid_id(self):
        """
        Giving an invalid id should return a bad request
        """
        response = self.client.post(reverse('delete_job'),
                                    data={'job_id': 's'})
        self.assertEqual(response.status_code, 400)

    def test_wrong_id(self):
        """
        Giving a wrong id should raise a 404
        """
        # No jobs
        response = self.client.post(reverse('delete_job'),
                                    data={'job_id': 1})
        self.assertEqual(response.status_code, 404)

    def test_job_deletion(self):
        """
        Test that if a valid id is given, the job is deleted
        And that all records associate with it are removed as well
        """
        # Dummy job
        job = Job.objects.create(name='test')
        for _ in range(3):
            job.record_set.create(command='hi',
                                  start_time=datetime.datetime(2000, 10, 10))
        self.assertEqual(Record.objects.count(), 3)
        payload = {'job_id': job.pk}
        response = self.client.post(reverse('delete_job'), data=payload)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Job.objects.count(), 0)
        self.assertEqual(Record.objects.count(), 0)

    def test_delete_job_non_post(self):
        """ Sending a non-POST request should error. """
        response = self.client.get(reverse('delete_job'))
        self.assertEqual(response.status_code, 405)


class DisplayLogTests(TestCase):
    def setUp(self):
        job = Job.objects.create(name='sleep')
        self.record = job.record_set.create(
            command='sleep 2',
            start_time=datetime.datetime(1990, 10, 10)
        )
        self.plain_log = self.record.log_set.create(
            log_name='out.log',
            log_text='Hello world',
            log_type=Log.PLAIN_LOG_TYPE
        )
        self.html_log = self.record.log_set.create(
            log_name='err.log',
            log_text='Hello oh wait what',
            log_type=Log.HTML_LOG_TYPE
        )

    def test_html_log(self):
        # Test html printing
        keywords = {'rec_id': self.record.pk}
        response = self.client.get(reverse('html_log',
                                           kwargs=keywords))
        self.assertEqual(response['Content-Disposition'],
                         'filename=%s' % self.html_log.log_name)
        self.assertContains(response, self.html_log.log_text)

    def test_html_404(self):
        keywords = {'rec_id': 0}
        response = self.client.get(reverse('html_log',
                                           kwargs=keywords))
        self.assertEqual(response.status_code, 404)

    def test_plain_log(self):
        # Test plain printing.
        keywords = {'log_id': self.plain_log.pk}
        response = self.client.get(reverse('plain_log',
                                           kwargs=keywords))
        self.assertEqual(response['Content-Disposition'],
                         'filename=%s' % self.plain_log.log_name)
        self.assertEqual(response.content, self.plain_log.log_text)

    def test_plain_404(self):
        keywords = {'log_id': 0}
        response = self.client.get(reverse('plain_log',
                                           kwargs=keywords))
        self.assertEqual(response.status_code, 404)


class DisplaySettingsCreateTests(TestCase):
    """ Test the creation of email settings. """
    def setUp(self):
        content_type = ContentType.objects.get_for_model(
            EmailSettings
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename='add_emailsettings'
        )
        self.user = User.objects.create_user(username='a', password='a')
        self.user.user_permissions.add(permission)
        self.user.save()
        self.client.login(username='a', password='a')

    def test_not_logged_in(self):
        # If not logged in, should get redirected to a login page
        self.client.logout()
        response = self.client.get(reverse('settings_add'))
        self.assertRedirects(
            response,
            '%s?next=%s' % (reverse('login'), reverse('settings_add'))
        )

    def test_no_permission(self):
        self.user.user_permissions.clear()
        self.user.save()
        response = self.client.get(reverse('settings_add'))
        self.assertEqual(response.status_code, 403)

    def test_displayed_form(self):
        """
        Not much to test here, because most of the code is Django-generated,
        and Django code is assumed to work correctly
        """
        response = self.client.get(reverse('settings_add'))
        self.assertEqual(response.status_code, 200)
        # Check for a password field and that's it
        self.assertContains(response, 'type="password"')

    def test_invalid(self):
        response = self.client.post(reverse('settings_add'), data={})
        # If invalid, should be redirected to the form
        self.assertContains(response, 'type="password"')

    def test_creation(self):
        payload = {'email_host': 'host',
                   'email_port': 25,
                   'email_host_user': '',
                   'email_host_password': '',
                   'use_tls': 'on'}
        self.client.post(reverse('settings_add'), data=payload)
        self.assertEqual(EmailSettings.objects.count(), 1)

        settings = EmailSettings.objects.all()[0]
        self.assertEqual(settings.email_host, 'host')
        self.assertEqual(settings.email_port, 25)
        self.assertEqual(settings.email_host_user, '')
        self.assertEqual(settings.email_host_password, '')
        self.assertEqual(settings.use_tls, True)


class DisplaySettingsUpdateTests(TestCase):
    """ Tests the change of settings. """

    def setUp(self):
        self.settings = EmailSettings.objects.create()
        self.kw = {'pk': self.settings.pk}
        content_type = ContentType.objects.get_for_model(
            EmailSettings
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename='change_emailsettings'
        )
        self.user = User.objects.create_user(username='a', password='a')
        self.user.user_permissions.add(permission)
        self.user.save()
        self.client.login(username='a', password='a')

    def test_not_logged_in(self):
        # If not logged in, should get redirected to a login page
        self.client.logout()
        response = self.client.get(reverse('settings_update',
                                           kwargs=self.kw))
        self.assertRedirects(
            response,
            '%s?next=%s' %
            (reverse('login'), reverse('settings_update', kwargs=self.kw))
        )

    def test_no_permission(self):
        self.user.user_permissions.clear()
        self.user.save()
        response = self.client.get(reverse('settings_update',
                                           kwargs=self.kw))
        self.assertEqual(response.status_code, 403)

    def test_update(self):
        self.assertEqual(EmailSettings.objects.count(), 1)
        payload = {'email_host': 'host',
                   'email_port': 25,
                   'email_host_user': '',
                   'email_host_password': ''}
        self.client.post(reverse('settings_update', kwargs=self.kw),
                         data=payload)
        self.assertEqual(EmailSettings.objects.count(), 1)
        settings = EmailSettings.objects.all()[0]
        self.assertEqual(settings.email_host, 'host')
        self.assertEqual(settings.email_port, 25)
        self.assertEqual(settings.email_host_user, '')
        self.assertEqual(settings.email_host_password, '')
        self.assertEqual(settings.use_tls, False)


class DisplayGlobalEmailListTests(TestCase):
    """ Test the display of emails. """

    def setUp(self):
        """ Populate with some GlobalEmailAddresses """
        for letter in 'abcdefgh':
            GlobalEmailAddress.objects.create(
                address='%c@%c.com' % (letter, letter)
            )

    def test_displayed_form(self):
        response = self.client.get(reverse('global'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "checkbox", count=8)
        self.assertContains(response, 'action="%s"' %
                                      reverse('global_delete'))
        self.assertContains(response, 'href="%s"' % reverse('global_add'))

    def test_displayed_form_no_emails(self):
        GlobalEmailAddress.objects.all().delete()
        response = self.client.get(reverse('global'))
        self.assertNotContains(response, '<input type="submit"')


class DisplayGlobalEmailCreateTests(TestCase):
    """ Test the creation of emails. """

    def setUp(self):
        content_type = ContentType.objects.get_for_model(
            GlobalEmailAddress
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename='add_globalemailaddress'
        )
        self.user = User.objects.create_user(username='a', password='a')
        self.user.user_permissions.add(permission)
        self.user.save()
        self.client.login(username='a', password='a')

    def test_not_logged_in(self):
        # If not logged in, should get redirected to a login page
        self.client.logout()
        response = self.client.get(reverse('global_add'))
        self.assertRedirects(
            response,
            '%s?next=%s' % (reverse('login'), reverse('global_add'))
        )

    def test_no_permission(self):
        # If the user does not have permission, should get a 403
        self.user.user_permissions.clear()
        self.user.save()
        response = self.client.get(reverse('global_add'))
        self.assertEqual(response.status_code, 403)

    def test_displayed_form(self):
        response = self.client.get(reverse('global_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input type="submit" value="Done" />')
        self.assertContains(response, '<form action="" method="post">')

    def test_creation(self):
        payload = {'address': 'a@a.com'}
        response = self.client.post(reverse('global_add'), data=payload)
        self.assertEqual(GlobalEmailAddress.objects.count(), 1)

        gea = GlobalEmailAddress.objects.all()[0]
        self.assertEqual(gea.address, 'a@a.com')
        self.assertRedirects(response, reverse('global'))


class DisplayGlobalEmailDeleteTests(TestCase):
    """ Test the deletion of emails. """

    def setUp(self):
        """ Populate with some GlobalEmailAddresses """
        for letter in 'abcdefgh':
            GlobalEmailAddress.objects.create(
                address='%c@%c.com' % (letter, letter)
            )
        content_type = ContentType.objects.get_for_model(
            GlobalEmailAddress
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename='delete_globalemailaddress'
        )
        self.user = User.objects.create_user(username='a', password='a')
        self.user.user_permissions.add(permission)
        self.user.save()
        self.client.login(username='a', password='a')

    def test_not_logged_in(self):
        # If not logged in, should get redirected to a login page
        self.client.logout()
        response = self.client.get(reverse('global_delete'))
        self.assertRedirects(
            response,
            '%s?next=%s' % (reverse('login'), reverse('global_delete'))
        )

    def test_no_permission(self):
        # If the user does not have permission, should get a 403
        self.user.user_permissions.clear()
        self.user.save()
        response = self.client.get(reverse('global_delete'))
        self.assertEqual(response.status_code, 403)

    def test_non_post(self):
        # If the user has permission, but does a get request, should 405
        response = self.client.get(reverse('global_delete'))
        self.assertEqual(response.status_code, 405)

    def test_deletion(self):
        keys = [gea.pk for gea in GlobalEmailAddress.objects.all()]
        keys = keys[:4]
        payload = dict((str(key), 'on') for key in keys)
        payload['a'] = 'b'
        payload['-1'] = 'invalid_id'
        response = self.client.post(reverse('global_delete'), data=payload)
        self.assertRedirects(response, reverse('global'))
        self.assertEqual(GlobalEmailAddress.objects.all().count(), 4)
        for gea in GlobalEmailAddress.objects.all():
            self.assertNotIn(gea.pk, keys)
