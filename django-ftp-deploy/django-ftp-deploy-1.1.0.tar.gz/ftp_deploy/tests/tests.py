"""
Unit Tests for ftp_deploy application
"""
import random
import string
import json
import os

from django.test import TestCase,  TransactionTestCase, SimpleTestCase, Client
from django.core.urlresolvers import reverse

from ftp_deploy.conf import *
from ftp_deploy.utils.curl import curl_connection
from ftp_deploy.utils.core import commits_parser
from ftp_deploy.models import Log, Service


class FTPDeployTest(SimpleTestCase):

    def setUp(self):
        self.client = Client()

        service = Service.objects.create(
            ftp_host='ftp.host',
            ftp_username='username',
            ftp_password='password',
            ftp_path='',
            repo_source='bb',
            repo_name='Repo Name',
            repo_slug_name='repo_name',
            repo_branch='master',
            repo_hook=False,
            secret_key=''.join(random.choice(string.letters + string.digits) for x in range(30)),
            status=True,
            status_message='',
        )

        
        with open('%s/payload.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
            
        Log.objects.create(service=service, payload=payload, user='username', status=True, status_message='', skip=False)
        Log.objects.create(service=service, payload=payload, user='username', status=False, status_message='', skip=False)
        Log.objects.create(service=service, payload=payload, user='username', status=False, status_message='', skip=True)

    def test_secret_key(self):
        service_entry = Service.objects.get(pk=1)
        secret_key = service_entry.secret_key

        response = self.client.get(reverse('ftpdeploy_deploy', kwargs={'secret_key': secret_key}))
        self.assertEqual(response.status_code, 405)

    def test_service_methods(self):

        service = Service.objects.get(pk=1)

        self.assertEqual(service.deploys(), 1)
        self.assertEqual(service.fail_deploys(), 1)
        self.assertEqual(service.skipped_deploys(), 1)
        self.assertEqual(service.latest_log_user(), 'username')
        self.assertEqual(service.hook_url(), reverse('ftpdeploy_deploy', kwargs={'secret_key': service.secret_key}))

    def test_log_methods(self):

        log = Log.objects.get(pk=1)

        self.assertEqual(log.commits_info(), [[u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871'], [
                         u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876']])

    def test_commit_parser(self):
        logs = Log.objects.all()

        commits = list()
        for log in logs:
            payload = json.loads(log.payload)
            commits += payload['commits']

        files_added, files_modified, files_removed = commits_parser(commits).file_diff()
        commits_info = commits_parser(commits).commits_info()

        self.assertEqual(files_added[0], 'example/file2.txt')
        self.assertEqual(files_modified[0], 'example/file1.txt')
        self.assertEqual(files_removed[0], 'example/file3.txt')

        self.assertEqual(commits_info, [[u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871'], [u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871'], [
                         u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871'], [u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876']])


class BitbucketConnectionTest(TestCase):

    def setUp(self):
        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']

        self.curl = curl_connection(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'])
        self.curl.authenticate()

    def test_can_login_to_bitbucket(self):
        """
        Test login to Bitbucket
        """
        url = 'https://bitbucket.org/api/1.0/user/repositories'
        self.curl.perform(url)
        self.assertEqual(self.curl.get_http_code(), 200)

    def tearDown(self):
        self.curl.close()
