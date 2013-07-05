from csat.acquisition import base


__version__ = '0.1.0'


class GithubCommentsCollector(base.CollectorBase):

    name = 'Github comments analyzer'
    key = 'ghcomments'
    version = __version__

    def build_parser(self, base):
        parser = super(GithubCommentsCollector, self).build_parser(base)
        parser.add_argument('-s', '--state', default='all',
                            choices=('all', 'open', 'closed'),
                            help='Filter issues by their state.')
        parser.add_argument('-i', '--issues', action='store_true',
                            help='Include nodes for issues (defaults to '
                            'false).')

        auth = parser.add_mutually_exclusive_group()
        auth.add_argument('-t', '--token', help='A personal API access token.')
        auth.add_argument('-a', '--client', help='The client ID and the client '
                          'secret. Format: <id>:<secret>')

        parser.add_argument('repo_name')
        return parser

    def get_command(self, model):
        from django.conf import settings

        cmd = ['csat-collect', self.key, '--state', model.issues_state]
        if model.issue_nodes:
            cmd += ['--issues']
        if model.access_token:
            cmd += ['--token', model.access_token]
        else:
            try:
                id, secret = settings.GITHUB_OAUTH
            except (AttributeError, ValueError):
                pass
            else:
                cmd += ['--client', '{}:{}'.format(id, secret)]

        cmd += [model.repo_name]
        return cmd

    def get_model(self):
        from . import models
        return models.GithubCommentsConfig

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def build_collector(self, task_manager, logger, args):
        from .collector import GithubCommentsCollector

        if args.token:
            auth = [args.token]
        elif args.client:
            auth = args.client.split(':')
        else:
            auth = []

        return GithubCommentsCollector(task_manager, logger, args.repo_name,
                                       args.issues, args.state, auth)


github_comments_collector = GithubCommentsCollector()
