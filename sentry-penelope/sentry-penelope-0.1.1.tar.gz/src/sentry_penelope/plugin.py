"""
sentry_penelope.plugin
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from sentry.plugins.bases.issue import IssuePlugin
from sentry_penelope.api import TracXmlProxy

import sentry_penelope


class PenelopeOptionsForm(forms.Form):
    penelope = forms.CharField(label=_('Trac base URL'),
            widget=forms.TextInput(attrs={'placeholder': 'e.g. https://penelope.com/trac'}),
        help_text=_('Enter your trac base URL (without project name)'))


class NewIssueForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span9'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'span9'}),
                                  help_text=_('You can use wiki syntax.'))
    trac = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'span9'}))


class PenelopePlugin(IssuePlugin):
    new_issue_form = NewIssueForm
    author = 'Penelope Team'
    author_url = 'http://getpenelope.github.io'
    version = sentry_penelope.VERSION
    description = "Integrate Penelope issues by linking a repository to a project."
    resource_links = [
        ('Bug Tracker', 'https://github.com/getpenelope/sentry-penelope/issues'),
        ('Source', 'https://github.com/getpenelope/sentry-penelope'),
    ]

    slug = 'penelope'
    title = _('Penelope')
    conf_title = title
    conf_key = 'penelope'
    project_conf_form = PenelopeOptionsForm

    def get_trac(self, group):
        penelope = self.get_option('penelope', group.project)
        site = dict(group.get_latest_event().data['tags']).get('site')
        return '%s/trac/%s' % (penelope, site)

    def get_initial_form_data(self, request, group, event, **kwargs):
        return {
            'description': "{{{\n%s\n}}}" % self._get_group_description(request, group, event),
            'title': self._get_group_title(request, group, event),
            'trac': self.get_trac(group)
        }

    def is_configured(self, request, project, **kwargs):
        return bool(self.get_option('trac_base', project))

    def get_new_issue_title(self, **kwargs):
        return 'Create Penelope Issue'

    def create_issue(self, request, group, form_data, **kwargs):
        proxy = TracXmlProxy(form_data['trac'], request=request)
        try:
            opts = {'type': 'defect',
                    'issuetype': 'sistemistica',
                    'customerrequest': '',
                    'owner': ''}
            ticket = proxy.ticket.create(form_data['title'],
                                         form_data['description'],
                                         opts)
        except Exception, e:
            msg = unicode(e)
            raise forms.ValidationError(_('Error communicating with Penelope: %s') % (msg,))

        try:
            data = int(ticket)
        except Exception, e:
            raise forms.ValidationError(_('Error decoding response from Penelope: %s') % (e,))

        return data

    def get_issue_label(self, group, issue_id, **kwargs):
        return 'PENELOPE-%s' % issue_id

    def get_issue_url(self, group, issue_id, **kwargs):
        return '%s/ticket/%s' % (self.get_trac(group), issue_id)
