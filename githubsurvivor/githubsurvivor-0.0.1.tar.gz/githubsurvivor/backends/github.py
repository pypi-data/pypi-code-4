"""
A GitHub-backed issue backend that connects to the GitHub API using credentials
provided in the application config.

GitHub issues don't provide a very rich API for figuring out who resolved an
issue. We assume that the assignee of a closed issue is the person responsible
for fixing it.
"""

from __future__ import absolute_import
import itertools

from github import Github
from mongoengine import *

from githubsurvivor import config
from githubsurvivor.models import User, Issue

def create_user(gh_user):
    "Create a User from a `github.NamedUser`."
    try:
        return User.objects.get(login=gh_user.login)
    except User.DoesNotExist:
        user = User(login=gh_user.login,
                    name=gh_user.name,
                    avatar_url='//www.gravatar.com/avatar/%s?s=52' % gh_user.gravatar_id,
                    assigned_issues_url='https://github.com/%s/issues/assigned/%s' % \
                        (config.GITHUB_REPO, gh_user.login))
        return user.save()

def create_issue(gh_issue):
    "Create an Issue from a `github.Issue`."
    issue = Issue(key=str(gh_issue.number),
                  title=gh_issue.title,
                  state=gh_issue.state,
                  opened=gh_issue.created_at,
                  closed=gh_issue.closed_at,
                  url=gh_issue.html_url)
    if gh_issue.assignee:
        issue.assignee = create_user(gh_issue.assignee)
    return issue.save()

class Importer(object):

    def __init__(self):
        auth_token = config.GITHUB_OAUTH_TOKEN
        account_name, repo_name = config.GITHUB_REPO.split('/')
        account = Github(auth_token).get_user(account_name)
        self.repo = account.get_repo(repo_name)

    def import_users(self, verbose=False):
        for gh_user in self._fetch_users():
            user = create_user(gh_user)
            if verbose: print 'created user: %s' % user.login

    def import_issues(self, verbose=False):
        for gh_issue in self._fetch_issues():
            issue = create_issue(gh_issue)
            if verbose: print 'created issue: %s' % issue.title

    def _fetch_users(self):
        return self.repo.get_collaborators()

    def _fetch_issues(self):
        return itertools.chain(self.repo.get_issues(state='open'),
                               self.repo.get_issues(state='closed'))

def issue_importer():
    return Importer()
