"""\
Configuration class
===================

Process command line and (optionally) a configuration file.
(Command line overrides config file specificaitons.)


Nick Seidenman <seidenman@wehi.ed.au>

Walter and Eliza Hall Institute
Parkville VIC 3052
Australia

"""

import logging
log = logging.getLogger(__name__)

import optparse
import cfgparse

import re

class Configurator(dict):

    def __init__(self, default_cfg="[DEFAULT]\n", use_msg=None, config_files=None):

        super(dict, self).__init__()

        # Create the parsers (command line options and config file)
        self.opt_parser = optparse.OptionParser(usage=use_msg)
        self.config_parser = cfgparse.ConfigParser(allow_py=True)
        log.debug('option and command line parsers created')
        
        # Load the default config, if provided.
        if default_cfg:  self.config_parser.add_file(content=default_cfg)
            
        # Tell the config parser to look on the command line for cfg file names and keys
        log.debug('config_files: {0}'.format(config_files))
        if config_files is not None:
            self.config_parser.add_optparse_files_option(self.opt_parser, config_files)
        else:
            self.config_parser.add_optparse_files_option(self.opt_parser)
            
        self.config_parser.add_optparse_keys_option(self.opt_parser)
        self.config_parser.add_optparse_help_option(self.opt_parser)

    def __call__(self):
        return self.config_parser.parse(self.opt_parser)


    def add_file(self, *args, **kwargs):
        self.config_parser.add_file(*args, **kwargs)


    def add_option(self, option_name, *alt_names, **kwargs):
        """\
This is little more than a wrapper around the add_option methods
of optparse and cfgparse.  `option_name` is the name that will
be used for the cfgparse call and will also be used in the optparse
call, prepended with '--' if it isn't already.
"""
        log.debug('option_name: "{0}"  alt_names: {1}   args: {2}'.format(option_name, alt_names, kwargs))

        target = kwargs.get('dest')
        if target is None:
            target = option_name.replace('-', '_')
            target = re.sub(r'(^_+)|(_+$)', '', target)
            kwargs['dest'] = target

        if option_name[0] == '-':
            self.opt_parser.add_option(option_name, *alt_names, **kwargs)
        else:
            self.config_parser.add_option(option_name, **kwargs)

        self.update({target: self.config_parser.add_option(option_name, dest=target)})
        
        return target

    def print_help(self):
        """Wrapper for cfgparse and optparse `print_help` methods."""
        self.opt_parser.print_help()
        self.config_parser.print_help()
        
