"""
JIRA backend that connects to a JIRA installation using credentials provided in
the application config.
"""

from __future__ import absolute_import
import itertools

import iso8601
from jira.client import JIRA
from mongoengine import *

from githubsurvivor import config
from githubsurvivor.models import User, Issue

MAX_ISSUE_RESULTS = 99999

def create_user(jira_user):
    "Creates a `githubsurvivor.models.User` from a `jira.resources.User`."
    try:
        return User.objects.get(login=jira_user.name)
    except User.DoesNotExist:
        user = User(login=jira_user.name,
                    name=jira_user.displayName,
                    email=jira_user.emailAddress,
                    avatar_url=jira_user.avatarUrls.__dict__['48x48'],
                    # FIXME: is it possible to generate this?
                    #assigned_issues_url=
                    )
        return user.save()

def create_issue(jira_issue):
    "Creates a `githubsurvivor.models.Issue` from a `jira.resources.Issue`."
    fields = jira_issue.fields
    state = 'closed' if fields.resolution and fields.resolution.name in ('Finished', 'Fixed') else 'open'
    parse_date = lambda d: iso8601.parse_date(d) if d else None
    issue = Issue(key=jira_issue.key,
                  title=fields.summary,
                  state=state,
                  opened=parse_date(fields.created),
                  closed=parse_date(fields.resolutiondate),
                  # TODO: we need the HTML URL, not the API URL
                  url=jira_issue.self)

    if fields.assignee:
        issue.assignee = create_user(fields.assignee)

    return issue.save()

class Importer(object):

    def __init__(self):
        username = config.JIRA_USERNAME
        password = config.JIRA_PASSWORD
        server = config.JIRA_SERVER
        project = config.JIRA_PROJECT

        self.jira = JIRA(basic_auth=(username, password), options={'server': server})
        self.project = project

    def import_users(self, verbose=False):
        for jira_user in self._fetch_users():
            user = create_user(jira_user)
            if verbose: print 'created user: %s' % user.login

    def import_issues(self, verbose=False):
        for jira_issue in self._fetch_issues():
            issue = create_issue(jira_issue)
            if verbose: print 'created issue: %s' % issue.key

    def _fetch_users(self):
        return self.jira.search_assignable_users_for_projects('', self.project)

    def _fetch_issues(self):
        return self.jira.search_issues(
            'project=%s and (status=OPEN or status=CLOSED)' % self.project,
            maxResults=MAX_ISSUE_RESULTS)

def issue_importer():
    return Importer()
