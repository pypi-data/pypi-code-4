# -*- coding: utf-8 -*-
"""
Façonnage d'un devis à partir d'un document ReStructuredText

Retrouve les directives ReST spécifiques au module (sb_*) dans le document et les 
traitent. Les données injectées proviennent du fichier de config utilisateur
``~/.sveebiz/config`` si il existe, sinon ``/etc/sveebiz.conf`` si il existe.

TODO: Utiliser une variable d'environnement pour permettre de spécifier un autre 
      emplacement du fichier de config (ou bien juste son répertoire pour permettre 
      d'y mettre d'autres trucs et pas utiliser une variable shell pour chaque item ?).
"""
import os, re, ConfigParser

from __init__ import *
from models import *

# Nom des directives supportées par défaut. 
DEFAULT_DIRECTIVE_NAMES = [
    'sb_coords',
    'sb_cost_section',
    'sb_delay_add',
    'sb_delay_total',
    'sb_softwares',
]

class DummyFile(str):
    """
    Dummy interface that adds a read() meethod to a string to simulate a file
    object interface
    """
    def read(self):
        return self

class EstimateDocument(object):
    # REGEX look-up motif to detect directives. Supports only the last line of the
    #directive, but not its options
    directive_pattern = r'(?:^(\.\.[ \t]+(?:%s)\:\:.*\n))'

    def __init__(self, source, actived_directive_names=DEFAULT_DIRECTIVE_NAMES):
        """
        :type source: string or file object
        :param source: Source file in ReST format to work on.
        
        :type actived_directive_names: list
        :param actived_directive_names: (optional) Each directive name must be
                                        a method ``EstimateDocument.handle_NAME`` where
                                        ``NAME`` is the directive name, this method will
                                        then process the data inside the directive if it
                                        is found in the document. Activated directives
                                        that do not haveprocessing methods are left
                                        as such in the document. Uses the list of
                                        ``DEFAULT_DIRECTIVE_NAMES`` by défault.
        """
        self.source = source
        self.actived_directives = actived_directive_names
        self.directive_expression = self.directive_pattern % '|'.join(self.actived_directives)
        self.directive_re = re.compile(self.directive_expression, re.MULTILINE)
        self.config = self.get_config()
        self.coords = Coords(self.config)
        self.delayer = Delayer(self.config)
        self.costs = Costs(self.config, self.delayer)
        self.softwares = Softwares(self.config)

    def get_config(self):
        """
        Retrieves the configuration

        Tries to get the configuration from an *.ini style file
        
        :rtype: object `ConfigParser.SafeConfigParser`
        :return: Object containing user's configuration.
        """
        cfdir = os.path.join(os.path.expanduser('~'), '.sveebiz')
        cfname = os.path.join(cfdir, 'config')
        
        conf = ConfigParser.SafeConfigParser(DEFAULT_CONFIG)
        conf.read(["/etc/sveebiz.conf", cfname])
        return conf

    def get_safe_source(self):
        """
        Returns  a ready to use content be it a file or a simple string
        
        :rtype: string
        :return: Document content.
        """
        src = self.source
        if not isinstance(src, basestring):
            src = src.read()
        return src.replace('\r\n', '\n').replace('\r', '\n')

    def render_output(self):
        """
        Do the substitution and the processing of detected directives.
        This methods is exposed as``EstimateDocument.output`` attribut .
        
        :rtype: string
        :return: Document processing output.
        """
        safe_source = self.get_safe_source()
        if len(self.directive_re.findall(safe_source)) > 0:
            new_source = self.directive_re.sub(self.directives_replacement_func, safe_source)
            f = DummyFile(new_source)
            f.name = self.source.name
            self.source.close()
            return f
        return self.source
    
    output = property(render_output)

    def directives_replacement_func(self, matchobj):
        """
        Selection of the processing method depending on the directive
        
        If it does not exist, returns the directive as is, with no modification.
        Otherwise, returns the output of the processing method
        
        :type matchobj: object `re.MatchObject`
        :param matchobj: regex match object  for the directives detection.
        
        :rtype: string
        :return: Directive processing output
        """
        hashrow = matchobj.group(0)[2:].strip()
        keyword = hashrow.split('::')[0].strip()
        args = hashrow.split('::')[1].strip().split()
        if hasattr(self, 'handle_%s' % keyword):
            return getattr(self, 'handle_%s' % keyword)(args)
        return matchobj.group(0)

    def handle_sb_coords(self, directive_args=[]):
        """
        Coordinates injection directive
        
        :type directive_args: list
        :param directive_args: List of arguments found in the directive
        
        :rtype: string
        :return: Processing output.
        """
        return self.coords.render()

    def handle_sb_delay_add(self, directive_args=[]):
        """
        Register delay adding directive
        
        :type directive_args: list
        :param directive_args: List of arguments found in the directive
        
        :rtype: string
        :return: Processing output
        """
        return self.delayer.add(*directive_args)

    def handle_sb_softwares(self, directive_args=[]):
        """
        Software bricks injection directive
        
        :type directive_args: list
        :param directive_args: List of arguments found in the directive
        
        :rtype: string
        :return: Processing output
        """
        return self.softwares.get_softs_render(directive_args)

    def handle_sb_cost_section(self, directive_args=[]):
        """
        Injection of a section containing fares, total costs and total deadline
        
        :type directive_args: list
        :param directive_args: List of arguments found in the directive
        
        :rtype: string
        :return: Processing output
        """
        return self.costs.get_fees(*directive_args)

# Interface CLI
if __name__ == "__main__":
    from optparse import OptionParser
    commandline_parser = OptionParser()
    commandline_parser.add_option("-i", "--input", dest="input_filename", help=u"Chemin de fichier du document entrant", metavar="FILE")
    commandline_parser.add_option("-o", "--output", dest="output_filename", default=False, help=u"Chemin de fichier du document sortant modifié. Optionnel, si non spécifié le document sera affiché sur la sortie standard.", metavar="FILE")

    (commandline_options, commandline_args) = commandline_parser.parse_args()
    if not commandline_options.input_filename:
        commandline_parser.error("Vous devez spécifier au moins un fichier entrant.")
    
    #Opens the specified file, and get its content
    f = open(commandline_options.input_filename)
    obj = EstimateDocument(f)
    output = obj.output
    f.close()
    
    #Returns processing output on standard output when no outfile is set.
    if not commandline_options.output_filename:
        print output
    #Creates out file and writes the processing output
    else:
        newf = open(commandline_options.output_filename, 'w')
        newf.write(output)
        newf.close()
