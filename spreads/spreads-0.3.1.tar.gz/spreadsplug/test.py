from spreads.plugin import HookPlugin

def my_func(args):
    print "Woohoo"


class TestCommand(HookPlugin):
    @classmethod
    def add_command_parser(cls, rootparser):
        my_parser = rootparser.add_parser(
            'test', help='Just some testing')
        my_parser.set_defaults(func=my_func)
