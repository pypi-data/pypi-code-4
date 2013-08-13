
__version__ = '0.1a'


class Argument(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class CommandRunner(object):
    
    description = ""
    args = []
    subcommands = {}
    
    def __init__(self):
        subcommands = getattr(self.__class__, 'subcommands', {})
        self._subcommands = subcommands.copy()
    
    
    def add_subcommand(self, name, cls):
        if not issubclass(cls, CommandRunner):
            m = "not a CommandRunner subclass"
            raise Exception(m)
        
        self._subcommands[name] = cls
    
    def init_subcommand(self, name, cls):
        return cls()
    
    
    def create_parser(self):
        import argparse
        return argparse.ArgumentParser(description = self.description)
    
    def init_parser(self, parser=None):
        if not parser:
            parser = self.create_parser()
        
        for arg in self.args:
            if not isinstance(arg, Argument):
                raise Exception("Not an Argument instance")
            parser.add_argument(*arg.args, **arg.kwargs)
        
        if len(self._subcommands) == 0:
            parser.set_defaults(func=self.execute)
            return parser
        
        subparsers = parser.add_subparsers()
        for k in self._subcommands:
            if not issubclass(self._subcommands[k], CommandRunner):
                raise Exception("Not a CommandRunner subclass")
            cmd = self.init_subcommand(k, self._subcommands[k])
            
            subparser = subparsers.add_parser(k, help=cmd.description)
            cmd.init_parser(subparser)
        
        return parser
    
    
    def parse_args(self, args=None):
        parser = self.init_parser()
        if args == None:
            return parser, parser.parse_args()
        else:
            return parser, parser.parse_args(args)
    
    
    def run(self, args=None):
        parser, args = self.parse_args(args)
        try:
            args.func(parser, args)
        except AttributeError:
            parser.error("missing command. Launch with -h option for more information")
    
    def execute(self, parser, args):
        m = "Undefined abstract method 'execute()'"
        raise NotImplementedError(m)
