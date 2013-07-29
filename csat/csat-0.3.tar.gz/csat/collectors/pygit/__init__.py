try:
    import git
except ImportError:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('always')
        warnings.warn('No git module found, the pygit collector will not be '
                      'available', ImportWarning)
    git = None

from csat.acquisition import base


__version__ = '0.1.0'


class GitPythonCollector(base.CollectorBase):

    name = 'Git + Python dependencies analyzer'
    key = 'pygit'
    version = __version__

    def build_parser(self, base):
        parser = super(GitPythonCollector, self).build_parser(base)
        parser.add_argument('--revspec', '-r', default='master')
        parser.add_argument('--history', '-k', action='store_true',
                            help=(
                                'Keep history. Do not remove nodes/edges when '
                                'modules/dependencies are removed but register'
                                ' the action in an attribute.'
                            ))
        parser.add_argument('repo_url')
        parser.add_argument('package_name')
        return parser

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def get_model(self):
        from . import models
        return models.Config

    def get_command(self, model):
        cmd = ['csat-collect', self.key, '-r', model.revspec]

        if model.keep_history:
            cmd += ['-h']

        cmd += [model.repo_url, model.package]

        return cmd

    def build_collector(self, task_manager, logger, args):
        from .collector import GitPythonCollector
        return GitPythonCollector(task_manager, logger, args.repo_url,
                                  args.revspec, args.package_name,
                                  args.history)


if git is not None:
    git_python_collector = GitPythonCollector()

    if __name__ == '__main__':
        from csat.acquisition.runner import get_runner
        get_runner(git_python_collector).run()
