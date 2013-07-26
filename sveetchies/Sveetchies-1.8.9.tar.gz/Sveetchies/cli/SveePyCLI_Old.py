#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sveetch's Python Commande LIne

Il contient tout le nécessaire pour faire un outils de commande en ligne fonctionnel. 
Il est destiné à être hérité par l'outil final.

DEPRECATED: Utilisez plutot SveePyCLI qui est la nouvelle version en cours dont la 
signature a changé.
"""
__title__ = "Sveetch's Python Commande LIne"
__version__ = "0.1.1"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008 Sveetch.Biz"

LOGGING_FILENAME = "SveePyCLI_Old.log"
LOGGING_DATE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_FILEMODE = "a"

OPTPARSER_USAGE = "%prog [options]\nUse -h or --help for print help message."
OPTPARSER_PROMPT_VERSION = "%s (%%prog) %s" % (__title__, __version__)
OPTPARSER_LOG_MODE_HELP = "Enable messages logging. If True, by default the logs file is created in the script current directory. (Default=False)"
OPTPARSER_LOG_FILENAME_HELP = "Define an absolute path to a log filename. (Default=%s)"
OPTPARSER_DEBUG_HELP = "Enable debugging. This is totally optionnal for commands, the ones than implement debugging formerly will specify it. (Default=False)"
OPTPARSER_VERBOSE_HELP = "Enable verbose output. If True, logging output will be print on the standard terminal output. (Default=False)"
OPTPARSER_PYTHONPATH_HELP = "Append the given path to the current pythonpath. Give all your path in one string, separate them with ':' like '/home/foo/bar:/home/foo/plop'. (Default=False)"
OPTPARSER_ENVIRONVAR_HELP = "Append environnement variable, with NAME as the name of the variable and CONTENT for his content. Use this option for each variable you want to add to the environnement script. Never forget to quote your CONTENT.(Default=Empty)"
OPTPARSER_TEST_HELP = "Simple testing option to check than the script is ok."
PRINT_OUTPUT_METHODS = ('verbose', 'logging')

import logging, os, re, sys, traceback
from optparse import OptionParser

class CommandError(Exception):
    """
    Exception pour indiquer un problème spécifique à l'éxécution d'une commande
    """
    pass

class SveePyCLI_Old(object):
    """
    Classe de base pour faire un outil de commande en ligne
    """
    def __init__( self, Apps_name=__title__, Apps_version=__version__,
                    optparser_usage=OPTPARSER_USAGE,
                    logging_prompt=None,
                    optparser_prompt_version=OPTPARSER_PROMPT_VERSION,
                    logging_date_format=LOGGING_DATE_FORMAT,
                    logging_filename=LOGGING_FILENAME,
                    logging_filemode=LOGGING_FILEMODE,
                    print_output_methods=PRINT_OUTPUT_METHODS
                ):
        """
        Initialisation des attributs par défaut puis du parser de commandes
        """
        self._CLI_Debug_ = False
        self._CLI_Verbose_ = False
        self._CLI_Logging_ = False
        self._CLI_Options_ = None
        self.is_python2_5 = True
        
        self._CLI_Parser_ = None
        self._CLI_Logger_ = None
        
        # Attributs de configuration de la CLI
        self.Apps_name = Apps_name
        self.Apps_version = Apps_version
        self.optparser_usage = optparser_usage
        self.optparser_prompt_version = optparser_prompt_version
        if logging_prompt:
            self.logging_prompt = logging_prompt
        else:
            self.logging_prompt = "[%s] v%s - STARTED" % (self.Apps_name, self.Apps_version)
        self.logging_date_format = logging_date_format
        self.logging_filename = logging_filename
        self.logging_filemode = logging_filemode
        self.optparser_log_filename_help = OPTPARSER_LOG_FILENAME_HELP % self.logging_filename
        self.print_output_methods = print_output_methods
        
        # Init du parser de commande
        self._CLI_Parser_ = OptionParser(self.optparser_usage, version=self.optparser_prompt_version)
        
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def ustr(self, s):
        """
        Renvoi une chaine en byte unicode ou brut de pomme selon la version 
        de python pour pallier aux vielles installes (DEPRECATED)
        """
        defname = "_is_python2_5"
        if self.is_python2_5:
            return unicode(s,'utf8')
        else:
            return s
    
    def get_commandline_options(self):
        """
        Gestion des arguments de la ligne de commande. Pour rajouter ses propres 
        commandes, il faut le surclasser par son héritier et à appeler en fin 
        de méthode avec :
          super(SveePyCLI_Old, self).get_commandline_options()
        """
        # Arguments internes
        self._CLI_Parser_.add_option("-d", "--debug", dest="debug_mode", default=False, action="store_true", help=OPTPARSER_DEBUG_HELP)
        self._CLI_Parser_.add_option("-e", "--environvar", action="append", nargs=2, type="string", dest="environvar_set", help=OPTPARSER_ENVIRONVAR_HELP, metavar="NAME \"CONTENT\"")
        self._CLI_Parser_.add_option("-f", "--log_filename", dest="log_file", default=os.path.join( os.getcwd(), self.logging_filename ), help=self.optparser_log_filename_help, metavar="FILE")
        self._CLI_Parser_.add_option("-l", "--log_mode", dest="log_mode", default=False, action="store_true", help=OPTPARSER_LOG_MODE_HELP)
        self._CLI_Parser_.add_option("-p", "--pythonpath", dest="pythonpath_set", default=False, help=OPTPARSER_PYTHONPATH_HELP, metavar="PATHS")
        self._CLI_Parser_.add_option("-t", "--test", dest="test_mode", default=False, action="store_true", help=OPTPARSER_TEST_HELP)
        self._CLI_Parser_.add_option("-v", "--verbose", dest="verbose_mode", default=False, action="store_true", help=OPTPARSER_VERBOSE_HELP)
        (self._CLI_Options_, self.cli_Args) = self._CLI_Parser_.parse_args()
        
        # Rends certains attributs plus accessibles
        self._CLI_Debug_ = self._CLI_Options_.debug_mode
        self._CLI_Verbose_ = self._CLI_Options_.verbose_mode
        self._CLI_Logging_ = self._CLI_Options_.log_mode
        
        # Prompt en mode verbeux
        if self._CLI_Verbose_:
            print self.logging_prompt
        # Modifie le python path
        if self._CLI_Options_.pythonpath_set:
            self.SetPythonpath(self._CLI_Options_.pythonpath_set)
        # Ajout des variables à l'environnement du script
        if self._CLI_Options_.environvar_set:
            self.SetEnvironVar(self._CLI_Options_.environvar_set)
        # Init et Prompt du logging
        if not self._CLI_Logger_ and self._CLI_Options_.log_mode is True:
            logging.basicConfig(level=logging.DEBUG, format=self.logging_date_format, filename=self._CLI_Options_.log_file, filemode=self.logging_filemode)
            logging.info(self.logging_prompt)
            self._CLI_Logger_ = logging
            self.print_output("Logging Filename : %s" % self._CLI_Options_.log_file)
        
    def print_output(self, msg, indent_logging=" "):
        """
        Gestion des informations à renvoyer à la sortie standard et l'objet 
        de logging.
        """
        if self._CLI_Verbose_ and 'verbose' in self.print_output_methods:
            print msg
        if self._CLI_Options_.log_mode is True and 'logging' in self.print_output_methods:
            self._CLI_Logger_.info(indent_logging+msg)
    
    def launch(self):
        """
        Lance les commandes. Pas d'automatisme prévu pour l'instant donc il 
        faut conditionner tout les arguments de commande possibles (sauf les 
        internes)
        """
        if self._CLI_Options_.test_mode:
            self.Test()
        # Fin des opérations
        self.stop()
    
    def stop(self):
        """
        Stop le script proprement
        """
        self.print_output("! END OF OPERATIONS !", indent_logging="")
        sys.exit(0)
    
    def Test(self):
        """
        Test bidon
        """
        self.print_output("Test ! Lorem Ipsum !")
    
    def SetPythonpath(self, paths):
        """
        Ajout les chemins donnés dans le sys.path. Les chemins sont joints 
        ensemble par le caractère ':' , de la meme facon qu'on indique un 
        ensemble de chemin en Bash.
        """
        self.print_output("Setting Pythonpath according to the given path.")
        
        for path in paths.split(':'):
            self.print_output("* Adding '%s'"%path)
            sys.path.insert(0, path)
    
    def SetEnvironVar(self, varlist):
        """
        Ajout les chemins donnés dans le sys.path. Les chemins sont joints 
        ensemble par le caractère ':' , de la meme facon qu'on indique un 
        ensemble de chemin en Bash.
        """
        self.print_output("Setting variables in the environnement script.")
        
        for k,v in varlist:
            self.print_output("* Adding '%s' = \"%s\""%(k,v))
            os.environ[k] = v
    
#
if __name__ == "__main__":
    obj = SveePyCLI_Old()
    obj.get_commandline_options()
    obj.launch()