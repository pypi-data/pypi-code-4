from django.db import models
from csat.acquisition.models import DataCollectorConfig
from django.utils.translation import ugettext_lazy as _


class GithubCommentsConfig(DataCollectorConfig):
    ISSUE_ALL, ISSUE_OPEN, ISSUE_CLOSED = 'all', 'open', 'closed'

    ISSUES_STATE_CHOICES = (
        (ISSUE_ALL, _('All')),
        (ISSUE_OPEN, _('Open')),
        (ISSUE_CLOSED, _('Closed')),
    )

    repo_name = models.CharField(_('Repository name'), max_length=255)
    issue_nodes = models.BooleanField(_('Add issues as nodes'), default=False)
    issues_state = models.CharField(_('Include issues'), max_length=63,
                                    choices=ISSUES_STATE_CHOICES,
                                    default=ISSUE_ALL)
    access_token = models.CharField(
        _('Access token'), max_length=50, blank=True, null=True,
        help_text=('A personal access token to use to authenticate to GitHub.'
                   ' You can omit this, but you will be limited to 60 '
                   'requests/hour.'))
