from csat.acquisition import base


__version__ = '0.1.0'


class PipermailCollector(base.CollectorBase):

    name = 'Pipermail Archives Scraper'
    key = 'pipermail'
    version = __version__

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def get_model(self):
        from . import models
        return models.PipermailConfig

    def get_command(self, model):
        return ['csat-collect', self.key, model.base_url, ]

    def build_parser(self, base):
        parser = super(PipermailCollector, self).build_parser(base)
        parser.add_argument('base_url')
        parser.add_argument('-c', '--concurrency', default=16, type=int,
                            help='Number of concurrent HTTP requests used '
                            'when collecting data (default: 16).')
        return parser

    def build_collector(self, task_manager, logger, args):
        from .collector import PipermailCollector
        return PipermailCollector(task_manager, logger, args.base_url,
                                  args.concurrency)


pipermail_collector = PipermailCollector()


if __name__ == '__main__':
    from csat.acquisition.runner import get_runner
    get_runner(pipermail_collector).run()
