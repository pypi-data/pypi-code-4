import re
import pycurl
import certifi
import StringIO

from .ftp import ftp_check
from .repo import bitbucket_check
from ftp_deploy.conf import *


class service_check(object):
    """Service check class, what group together all checking points. Return 'fails' and 'message' lists"""
    def __init__(self, service):
        self.service = service
        self.message = list()
        self.fails = [False, False, False, False]

    def check_log(self):
        """Check logs"""
        if self.service.pk is not None:
            log_fail = self.service.log_set.all().filter(status=False).filter(skip=False).count()
            if log_fail:
                self.message.append('<b>Log</b>: Deploy Fails(%d)' % log_fail)
                self.fails[0] = True

    def check_repo(self):
        """Check repositories connection, along with POST Hook"""
        if self.service.repo_source == 'bb':
            bb = bitbucket_check(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'], self.service)
            bb_fail, bb_fail_message = bb.check_all()

            if bb_fail:
                self.message.append(bb_fail_message)
                self.fails[1] = True

            hook_fail, hook_fail_message = bb.check_hook_exist()
            if hook_fail:
                self.message.append(hook_fail_message)
                self.fails[2] = True

    def check_ftp(self):
        """Check FTP connection"""
        ftp = ftp_check(self.service.ftp_host, self.service.ftp_username, self.service.ftp_password, self.service.ftp_path)
        ftp_fail, ftp_fail_message = ftp.check_all()
        ftp.quit()

        if ftp_fail:
            self.message.append(ftp_fail_message)
            self.fails[3] = True

    def check_all(self):
        self.check_log()
        self.check_repo()
        self.check_ftp()

        return self.fails, self.message


class commits_parser(object):

    """Commit parser for list of commits. Take commits dictionary captured from payload"""

    def __init__(self, commits):
        self.commits = commits

    def commits_info(self):
        """Return commits details list in format [message,author,raw_node]"""
        output = list()
        [output.append([commit['message'], commit['author'], commit['raw_node']]) for commit in reversed(self.commits)]
        return output

    def email_list(self):
        """Return email list from raw_author, limited to unique emails"""
        output = list()
        for commit in self.commits:
            email = re.search('%s(.*)%s' % ('<', '>'), commit['raw_author']).group(1)
            output.append(email) if email not in output else False
        return output

    def file_diff(self):
        """Return files list grouped by added, modified and removed. Respect order of commits"""
        added, removed, modified = list(), list(), list()

        for commit in self.commits:
            for file in commit['files']:
                if file['type'] == 'added':
                    added.append(file['file']) if file['file'] not in added else False
                    removed.remove(file['file']) if file['file'] in removed else False
                elif file['type'] == 'modified':
                    modified.append(file['file']) if file['file'] not in modified and file['file'] not in added else False
                elif file['type'] == 'removed':
                    removed.append(file['file']) if file['file'] not in removed else False
                    added.remove(file['file']) if file['file'] in added else False
                    modified.remove(file['file']) if file['file'] in modified else False

        return added,  modified, removed


class absolute_url(object):

    """Build absolute url to root url whthout trailing slash"""

    def __init__(self, request):
        self.request = request

    def build(self):
        return self.request.build_absolute_uri('/')[:-1]
