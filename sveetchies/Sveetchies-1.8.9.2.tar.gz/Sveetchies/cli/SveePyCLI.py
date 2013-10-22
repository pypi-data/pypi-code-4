#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 'SveePyCLI' contenant tout le nécessaire pour faire un outils de commande en 
# ligne fonctionnel. Il est destiné à être hérité par l'outil final.
#
# Ceci est la nouvelle version comportant quelques améliorations, le comportement pouvant 
# être différent avec l'ancien, cette version est pour l'instant présente sous un nouveau 
# nom, la version historique étant laissée en place en attendant d'imposer une 
# modification aux projets qui l'utilisait.
#
__title__ = "Sveetch's Python Commande LIne"
__version__ = "0.2.0"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008-2010 Sveetch.Biz"

LOGGING_FILENAME = "SveePyCLI.log"
LOGGING_DATE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_FILEMODE = "a"

OPTPARSER_USAGE = "%prog [options]\nUse -h or --help for print help message."
OPTPARSER_PROMPT_VERSION = "%s (%%prog) %s" % (__title__, __version__)
OPTPARSER_LOG_MODE_HELP = "Enable messages logging. If True, by default the logs file is created in the script current directory. (Default=False)"
OPTPARSER_LOG_FILENAME_HELP = "Define an absolute path to a log filename. (Default=%s)"
OPTPARSER_DEBUG_HELP = "Enable debugging. This is totally optionnal for commands, the ones than implement debugging formerly will specify it. (Default=False)"
OPTPARSER_VERBOSE_HELP = "Enable verbose output. If True, logging output will be print on the standard terminal output. (Default=False)"
OPTPARSER_VERBOSITY_HELP = u'Verbosity level from 0 to 1, 0 is silent. (Default=0)'
OPTPARSER_PYTHONPATH_HELP = "Append the given path to the current pythonpath. Give all your path in one string, separate them with ':' like '/home/foo/bar:/home/foo/plop'. (Default=False)"
OPTPARSER_ENVIRONVAR_HELP = "Append environnement variable, with NAME as the name of the variable and CONTENT for his content. Use this option for each variable you want to add to the environnement script. Never forget to quote your CONTENT.(Default=Empty)"
OPTPARSER_TEST_HELP = "Simple testing option to check than the script is ok."
PRINT_OUTPUT_METHODS = ('verbose', 'logging')
OPTPARSER_VERBOSITY_CHOICES = ['0', '1']

import os, sys
from optparse import OptionParser
from Sveetchies.logger import LoggingInterface

class CommandError(Exception):
    """
    Exception to show specific problem when running a command
    """
    pass

class SveePyCLI(object):
    """
    Base class to create a command line tool
    """
    def __init__( self, Apps_name=__title__, Apps_version=__version__,
                    optparser_usage=OPTPARSER_USAGE,
                    logging_prompt=None,
                    logging_date_format=LOGGING_DATE_FORMAT,
                    logging_filename=LOGGING_FILENAME,
                    logging_filemode=LOGGING_FILEMODE,
                    optparser_prompt_version=OPTPARSER_PROMPT_VERSION,
                    print_output_methods=PRINT_OUTPUT_METHODS,
                    verbosity_choices=OPTPARSER_VERBOSITY_CHOICES
                ):
        """
        Attributes initialisation with default values, then command parser initialisation
        
        :type Apps_name: string
        :param Apps_name: (optional) Tool designation label .
        
        :type Apps_version: string
        :param Apps_version: (optional) Tool version label .
        
        :type optparser_usage: string
        :param optparser_usage: (optional) tool usage sum up label.
        
        :type logging_prompt: string
        :param logging_prompt: (optional) Specific prompt label (instead of the aumatic
                                    label made from tool designation and version).
        
        :type logging_date_format: string
        :param logging_date_format: (optional) Date output format for the logs
                                    according to the strftime() scheme).
        
        :type logging_filename: string
        :param logging_filename: (optional) Logfile name if activated.
        
        :type logging_filemode: string
        :param logging_filemode: (optional) Defaults write mode for the log: append by
                                    default.
        
        :type optparser_prompt_version: string
        :param optparser_prompt_version: (optional)Prompt version written by
                                    `optparse.OptionParser`.
        
        :type print_output_methods: list
        :param print_output_methods: (optional) Lists all available output methods :
                                    (logfile, STDOUT, aso).
        
        :type verbosity_choices: list
        :param verbosity_choices: (optional) Lists all possible verbose modes.
                                    From 0 to 1 by default.
        """
        self._CLI_Debug_ = False
        self._CLI_Verbosity_ = 0
        self._CLI_Logging_ = False
        self._CLI_Options_ = None
        
        self._CLI_Parser_ = None
        self._CLI_Logger_ = LoggingInterface(passive=True, logging_filename=logging_filename, logging_date_format=logging_date_format, logging_filemode=logging_filemode)
        
        #CLI configuration attibutes
        self.Apps_name = Apps_name
        self.Apps_version = Apps_version
        self.optparser_usage = optparser_usage
        self.verbosity_choices = verbosity_choices
        self.optparser_prompt_version = optparser_prompt_version
        if logging_prompt:
            self.logging_prompt = logging_prompt
        else:
            self.logging_prompt = "[%s] v%s - STARTED" % (self.Apps_name, self.Apps_version)
        self.optparser_log_filename_help = OPTPARSER_LOG_FILENAME_HELP % self._CLI_Logger_.logging_filename
        self.print_output_methods = print_output_methods
        
        # Command parser init
        self._CLI_Parser_ = OptionParser(self.optparser_usage, version=self.optparser_prompt_version)
        
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def get_commandline_options(self):
        """
        Command line argument management. To add your own commands, you need to subclass
        it and then call it as the last method as :
        
            super(SveePyCLI, self).get_commandline_options()
        
        """
        # Internal arguments
        self._CLI_Parser_.add_option("-d", "--debug", dest="debug_mode", default=False, action="store_true", help=OPTPARSER_DEBUG_HELP)
        self._CLI_Parser_.add_option("-e", "--environvar", action="append", nargs=2, type="string", dest="environvar_set", help=OPTPARSER_ENVIRONVAR_HELP, metavar="NAME \"CONTENT\"")
        self._CLI_Parser_.add_option("-f", "--log_filename", dest="log_file", default=os.path.join( os.getcwd(), self._CLI_Logger_.logging_filename ), help=self.optparser_log_filename_help, metavar="FILE")
        self._CLI_Parser_.add_option("-l", "--log_mode", dest="log_mode", default=False, action="store_true", help=OPTPARSER_LOG_MODE_HELP)
        self._CLI_Parser_.add_option("-p", "--pythonpath", dest="pythonpath_set", default=False, help=OPTPARSER_PYTHONPATH_HELP, metavar="PATHS")
        self._CLI_Parser_.add_option("-t", "--test", dest="test_mode", default=False, action="store_true", help=OPTPARSER_TEST_HELP)
        #self._CLI_Parser_.add_option("-v", "--verbose", dest="verbose_mode", default=False, action="store_true", help=OPTPARSER_VERBOSE_HELP)
        self._CLI_Parser_.add_option('-v', '--verbosity', action='store', dest='verbosity', default='0', type='choice', choices=self.verbosity_choices, help=OPTPARSER_VERBOSITY_HELP)
        (self._CLI_Options_, self.cli_Args) = self._CLI_Parser_.parse_args()
        
        # Make some attributes more accessible
        self._CLI_Debug_ = self._CLI_Options_.debug_mode
        #self._CLI_Verbose_ = self._CLI_Options_.verbose_mode
        self._CLI_Verbosity_ = int(self._CLI_Options_.verbosity)
        self._CLI_Logging_ = self._CLI_Options_.log_mode
        
        # Changes the pythonpath 
        if self._CLI_Options_.pythonpath_set:
            self.SetPythonpath(self._CLI_Options_.pythonpath_set)
        # Adds variable to the script environnement.
        if self._CLI_Options_.environvar_set:
            self.SetEnvironVar(self._CLI_Options_.environvar_set)
        # sets the Init and Prompt of the logging
        self._CLI_Logger_.connect_logger(
            passive=False,
            output_verbosity=self._CLI_Verbosity_,
            logging_verbosity=int(self._CLI_Logging_),
            logging_filename=self._CLI_Options_.log_file
        )
        self._CLI_Logger_.info("Logging Filename : %s" % self._CLI_Options_.log_file)
        #Prompt title
        self._CLI_Logger_.title(self.logging_prompt)
        
    def launch(self):
        """
        Starts the commands
        No automatism planned so far. So the object that will implement this method will
        have to add conditions on the command options he exposes.
        """
        if self._CLI_Options_.test_mode:
            self.Test()
        # End of the game
        self.stop()
    
    def stop(self):
        """
        Ends the script cleanly
        """
        self._CLI_Logger_.info("! END OF OPERATIONS !")
        sys.exit(0)
    
    def Test(self):
        """
        Fake test
        """
        self._CLI_Logger_.info("Test ! Lorem Ipsum !")
    
    def SetPythonpath(self, paths):
        """
        Adds given paths to the sys.path
        
        :type paths: string
        :param paths: List of paths to add, separated by a':'.
        """
        self._CLI_Logger_.info("Setting Pythonpath according to the given path.")
        
        for path in paths.split(':'):
            self._CLI_Logger_.info("* Adding '%s'"%path, indent="    ")
            sys.path.insert(0, path)
    
    def SetEnvironVar(self, varlist):
        """
        Adds given path to the sys.path. Path are then joined together with ':'
        the exact same way it is done in bash
        
        :type varlist: list
        :param varlist: list of variable to be added as a tuple.
        """
        self._CLI_Logger_.info("Setting variables in the environnement script.")
        
        for k,v in varlist:
            self._CLI_Logger_.info("* Adding '%s' = \"%s\""%(k,v), indent="    ")
            os.environ[k] = v
    
#
#
if __name__ == "__main__":
    obj = SveePyCLI()
    obj.get_commandline_options()
    obj.launch()

