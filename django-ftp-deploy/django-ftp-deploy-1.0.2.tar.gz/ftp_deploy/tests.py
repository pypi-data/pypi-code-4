"""
Unit Tests for ftp_deploy application
"""
import pycurl
import json
import StringIO
from ftplib import FTP
import certifi

from django.test import TestCase
from django.core.urlresolvers import reverse

from .conf import *
from models import Log


class ftpdeployTest(TestCase):

    def test_can_create_log_entry(self):
        """
        Can create Log entry
        """
        Log.objects.create(user='user', message='commit message', passed=True)

        log_entry = Log.objects.get(pk=1)

        self.assertEqual('user', log_entry.user)
        self.assertEqual('commit message', log_entry.message)
        self.assertTrue(log_entry.passed)

    def test_bitbucket_check_secret_key(self):
        """
        ftpdeploy bitbucket page response
        """

        if DEPLOY_SECRET_KEY == '':
            self.fail('DEPLOY_SECRET_KEY is not set')

        response = self.client.get(reverse('ftpdeploy_bitbucket', kwargs={'secret_key': DEPLOY_SECRET_KEY}))
        self.assertEqual(response.status_code, 200)


class FTPConnectionTest(TestCase):

    def setUp(self):
        self.ftp = FTP()

        self.ftp_host = FTP_SETTINGS['host']
        self.ftp_username = FTP_SETTINGS['username']
        self.ftp_password = FTP_SETTINGS['password']

    def tearDown(self):
        self.ftp.quit()

    def test_can_connetct_to_ftp(self):
        """
        Test FTP connection
        """
        self.ftp.connect(self.ftp_host)
        self.ftp.login(self.ftp_username, self.ftp_password)


class BitbucketConnectionTest(TestCase):

    def setUp(self):
        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.CAINFO, certifi.where())

    def tearDown(self):
        self.curl.close()

    def test_can_login_to_bitbucket(self):
        """
        Test login to Bitbucket
        """
        url = 'https://bitbucket.org/api/1.0/user/repositories'
        self.curl.setopt(pycurl.WRITEFUNCTION, lambda x: None)

        self.curl.setopt(self.curl.USERPWD, '%s:%s' % (self.bitbucket_username, self.bitbucket_password))
        self.curl.setopt(self.curl.URL, url)
        self.curl.perform()

        self.assertEqual(self.curl.getinfo(pycurl.HTTP_CODE), 200)

    def test_write_json_to_stringio(self):
        """
        Test write json response to StringIO and read json data
        """
        url = 'https://bitbucket.org/api/1.0/repositories/tutorials/tutorials.bitbucket.org'
        json_string = ''

        b = StringIO.StringIO()
        self.curl.setopt(pycurl.URL, url)

        self.curl.setopt(pycurl.WRITEFUNCTION, b.write)
        self.curl.perform()
        data = json.loads(b.getvalue())

        self.assertEqual('tutorials', data['owner'])
