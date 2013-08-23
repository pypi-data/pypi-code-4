import os
import sys
import re
from setuptools import Command

class EpydocCommand(Command):
    '''
    Setuptools command used to build an API documentation with epydoc.

    @author: jwienke
    '''

    user_options = [('format=', 'f',
                     'the output format to use (html and pdf)'),
                    ('config=', 'c',
                     'Epydoc configuration file'),
                    ('names=', None,
                     'Names of packages to document. Defaults to all '
                     'configured packages in the project. Comma-separated.'),
                    ('output-dir=', 'o',
                     'Folder for generated output. Default: docs'),
                    ('verbose', 'v', 'print verbose warnings')]
    description = 'Generates an API documentation using epydoc.'

    FORMAT_HTML = 'html'
    FORMAT_PDF = 'pdf'

    def initialize_options(self):
        self.format = None
        self.verbose = False
        self.config = None
        self.names = ''
        self.output_dir = 'docs'

    def finalize_options(self):
        if self.format is None:
            self.format = self.FORMAT_HTML
        if not self.format in [self.FORMAT_HTML, self.FORMAT_PDF]:
            self.format = self.FORMAT_HTML
        self.names = [module.strip()
                      for module in re.split('[\s,]+', self.names)
                      if len(module.strip()) > 0]

    def run(self):

        # ensure that everything that's needed is built
        self.run_command('build')

        outdir = os.path.join(self.output_dir, self.format)
        try:
            os.makedirs(outdir)
        except OSError:
            pass

        # build the argument string
        cmdline = ['foo']
        cmdline.append('--' + self.format)
        cmdline.append('-o')
        cmdline.append(outdir)
        if self.verbose:
            cmdline.append('-v')
        if self.config is not None:
            cmdline.append('--config')
            cmdline.append(self.config)
            
        base = self.get_finalized_command('build_py')
        if self.names is None or len(self.names) == 0:
            for package, _, _ in base.find_all_modules():
                cmdline.append(package)
        else:
            cmdline = cmdline + self.names
        
        import copy
        import epydoc.cli as ep

        argv = copy.copy(sys.argv)
        try:
            sys.argv = cmdline
            ep.cli()
        finally:
            sys.argv = argv
