import argparse

from csat.acquisition import base


__version__ = '0.1.0'


class ListAction(argparse.Action):
    def __init__(self, option_strings, dest, const, default=None,
                 required=False, help=None, metavar=None):
        super(ListAction, self).__init__(option_strings=option_strings,
                                         dest=dest, nargs=0, const=const,
                                         default=default, required=required,
                                         help=help)

    def __call__(self, parser, namespace, values, option_string):
        for graph in self.const():
            print '  * {}'.format(graph.key)
            print '    ' + graph.description.strip()
            print ''
        parser.exit()


class ExampleGraphsCollector(base.CollectorBase):

    name = 'Example Graphs Collection'
    key = 'examples'
    version = __version__

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def get_model(self):
        from . import models
        return models.ExamplesConfig

    def get_command(self, model):
        return ['csat-collect', self.key, model.example, ]

    def build_parser(self, base):
        from . import graphs
        parser = super(ExampleGraphsCollector, self).build_parser(base)
        parser.add_argument('graph_name')
        parser.add_argument('-l', '--list', action=ListAction,
                            const=graphs.get_graphs, help='List all available '
                            'graphs and exit.')
        return parser

    def build_collector(self, task_manager, logger, args):
        from . import graphs
        return graphs.get_graph(args.graph_name)


examples_collector = ExampleGraphsCollector()


if __name__ == '__main__':
    from csat.acquisition.runner import get_runner
    get_runner(examples_collector).run()
