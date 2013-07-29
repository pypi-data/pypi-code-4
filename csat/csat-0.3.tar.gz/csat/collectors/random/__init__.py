from csat.acquisition import base


__version__ = '0.1.0'


class RandomGraphGenerator(base.CollectorBase):

    name = 'Random Graphs Generator'
    key = 'random'
    version = __version__

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def get_model(self):
        from . import models
        return models.RandomConfig

    def get_command(self, model):
        cmd = ['csat-collect', self.key, ]

        if model.ratio is not None:
            cmd += ['--ratio', str(model.ratio)]

        if model.seed is not None:
            cmd += ['--seed', str(model.seed)]

        cmd += [str(model.domains), str(model.nodes), str(model.edges)]
        return cmd

    def build_parser(self, base):
        parser = super(RandomGraphGenerator, self).build_parser(base)
        parser.add_argument('--seed', '-s', type=int)
        parser.add_argument('--ratio', '-r', type=float, default=0.8)
        parser.add_argument('domains', type=int)
        parser.add_argument('nodes', type=int)
        parser.add_argument('edges', type=int)
        return parser

    def build_collector(self, task_manager, logger, args):
        from . import generator
        return generator.GraphGenerator(args.domains, args.nodes, args.edges,
                                        args.ratio, args.seed)


random_generator = RandomGraphGenerator()


if __name__ == '__main__':
    from csat.acquisition.runner import get_runner
    get_runner(random_generator).run()
