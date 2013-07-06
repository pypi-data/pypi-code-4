import argparse

from csat.acquisition import get_factories
from csat.acquisition.runner import get_runner_class


class ListAction(argparse.Action):
    def __init__(self, option_strings, dest, const, default=None,
                 required=False, help=None, metavar=None):
        super(ListAction, self).__init__(option_strings=option_strings,
                                         dest=dest, nargs=0, const=const,
                                         default=default, required=required,
                                         help=help)

    def __call__(self, parser, namespace, values, option_string):
        for collector in self.const:
            print collector
        parser.exit()


def main():
    parser = argparse.ArgumentParser('csat-collect')
    runner_class = get_runner_class()
    subparsers = parser.add_subparsers()
    collectors = []

    for factory in get_factories():
        subparser = subparsers.add_parser(factory.key)
        runner = runner_class(factory)
        subparser = runner.build_parser(subparser)
        subparser.set_defaults(runner=runner)
        collectors.append(factory.key)

    parser.add_argument('-l', '--list', action=ListAction, const=collectors)

    args = parser.parse_args()
    return args.runner.run_as_subcommand(args)


if __name__ == '__main__':
    main()
