import json

from abc import ABCMeta, abstractmethod
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ftp_deploy.conf import *
from .core import commits_parser
from .curl import curl_connection


class notification():

    """Notification abstract class, take three arguments, host, service object and payload json string"""
    __metaclass__ = ABCMeta

    def __init__(self, host, service, payload):
        self.host = host
        self.service = service
        self.payload = json.loads(payload)
        self.commits = self.payload['commits']
        self.user = self.payload['user']
        self.from_email = 'noreply@ftpdeploy.com'
        self.send()

    @property
    def template_html(self):
        raise NotImplementedError

    @property
    def template_text(self):
        raise NotImplementedError

    @abstractmethod
    def subject(self):
        pass

    @abstractmethod
    def emails(self):
        pass

    @abstractmethod
    def context(self):
        pass

    def deploy_user(self):
        """Method return email of deploy user"""
        if self.payload['user'] == 'Restore':
            return []

        try:
            curl = curl_connection(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'])
            curl.authenticate()
            url = 'https://bitbucket.org/api/1.0/users/%s/emails' % self.payload['user']
            context = json.loads(curl.perform(url))
            return [context[0]['email']]
        except Exception, e:
            return []

    def send(self):
        """Sent method process emails from list returned by emails() method"""
        for recipient in self.emails():
            text_content = render_to_string(self.template_text, self.context())
            html_content = render_to_string(self.template_html, self.context())

            msg = EmailMultiAlternatives(self.subject(), text_content, self.from_email, [recipient])
            msg.attach_alternative(html_content, "text/html")
            msg.send()


class notification_success(notification):

    """Notification class for success"""

    template_html = 'ftp_deploy/email/email_success.html'
    template_text = 'ftp_deploy/email/email_success.txt'

    def subject(self):
        return '%s - Deploy Successfully' % self.service

    def emails(self):
        emails_list = list()
        emails_list += DEPLOY_NOTIFICATIONS['success']['emails']

        if DEPLOY_NOTIFICATIONS['success']['deploy_user']:
            emails_list += self.deploy_user()

        if DEPLOY_NOTIFICATIONS['success']['commit_user']:
            emails_list += commits_parser(self.commits).email_list()

        return list(set(emails_list))

    def context(self):
        context = dict()
        context['service'] = self.service
        context['host'] = self.host
        context['commits_info'] = commits_parser(self.commits).commits_info()
        context['files_added'], context['files_modified'], context['files_removed'] = commits_parser(self.commits).file_diff()
        return context


class notification_fail(notification):

    """Notification class for fail"""

    template_html = 'ftp_deploy/email/email_fail.html'
    template_text = 'ftp_deploy/email/email_fail.txt'

    def __init__(self, host, service, payload, error):
        self.error = error
        super(notification_fail, self).__init__(host, service, payload)

    def subject(self):
        return '%s - Deploy Fail' % self.service

    def emails(self):
        emails_list = list()
        emails_list += DEPLOY_NOTIFICATIONS['fail']['emails']

        if DEPLOY_NOTIFICATIONS['fail']['deploy_user']:
            emails_list += self.deploy_user()

        if DEPLOY_NOTIFICATIONS['fail']['commit_user']:
            emails_list += commits_parser(self.commits).email_list()

        return list(set(emails_list))

    def context(self):
        context = dict()
        context['host'] = self.host
        context['service'] = self.service
        context['error'] = self.error
        return context
