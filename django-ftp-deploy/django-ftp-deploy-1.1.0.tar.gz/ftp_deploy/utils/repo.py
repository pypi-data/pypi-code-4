import pycurl
import json
from .curl import curl_connection
from .decorators import check


class bitbucket_check(curl_connection):

    """Bitbucket check class contain all checking points for bitbucket repository, return True if fail"""

    def __init__(self, username, password, service):
        super(bitbucket_check, self).__init__(username, password)
        self.service = service

    @check('Bitbucket')
    def check_authentication(self):
        self.authenticate()
        self.perform('https://bitbucket.org/api/1.0/user/repositories')
        if self.curl.getinfo(pycurl.HTTP_CODE) != 200:
            raise Exception("Login Fail")

    @check('Bitbucket')
    def check_repo_exist(self):
        self.authenticate()
        repos = json.loads(self.perform('https://bitbucket.org/api/1.0/user/repositories'))
        for repo in repos:
            if repo['slug'] == self.service.repo_slug_name:
                return False, ''
        raise Exception("Repository %s doesn't exist" % self.service.repo_slug_name)

    @check('Bitbucket')
    def check_branch_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/branches' % (self.username, self.service.repo_slug_name)
        branches = json.loads(self.perform(url))
        try:
            branches[self.service.repo_branch]
        except KeyError, e:
            raise Exception("Branch %s doesn't exist" % self.service.repo_branch)

    @check('Bitbucket')
    def check_hook_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/services' % (self.username, self.service.repo_slug_name)
        hooks = json.loads(self.perform(url))

        if type(hooks) == list:
            for hook in hooks:
                if len(hook['service']['fields']) > 0:
                    value = hook['service']['fields'][0]['value']
                    if value.find(str(self.service.hook_url())) != -1 and hook['service']['type'] == 'POST':
                        return False, ''
        raise Exception("Hook is not set up")

    def check_all(self):
        status = self.check_authentication()
        if status[0] == True:
            return status

        status = self.check_repo_exist()
        if status[0] == True:
            return status

        status = self.check_branch_exist()
        if status[0] == True:
            return status

        return False, ''
