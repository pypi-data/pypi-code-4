#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Line Interface for PyChanDownloader
"""
import os, hashlib, re
from random import choice
from urllib import urlretrieve
from urllib2 import urlopen, HTTPError, URLError, Request
from time import sleep
import sqlite3

from Sveetchies.cli.SveePyCLI import SveePyCLI, OPTPARSER_USAGE, LOGGING_DATE_FORMAT, \
                    LOGGING_FILEMODE, PRINT_OUTPUT_METHODS
from Sveetchies.logger import LoggingInterface
from Sveetchies.chan import __version__, __title__, ChanBackendError
from Sveetchies.chan.parser import DEFAULT_CHAN_BASE_URL, DEFAULT_DB_FILENAME, FourChanDownloader, IChanDownloader, ZeroChanDownloader

LOGGING_FILENAME = "chan_downloader.log"
OPTPARSER_PROMPT_VERSION = "%s (%%prog) %s" % (__title__, __version__)

class DownloadCLI(SveePyCLI):
    """
    Base Class to build a command line tool
    """
    def __init__( self, Apps_name=__title__, Apps_version=__version__,
            logging_prompt=None,
            optparser_prompt_version=OPTPARSER_PROMPT_VERSION,
            logging_filename=LOGGING_FILENAME,
            verbosity_choices=('0', '1', '2', '3')
        ):
        """
        :type Apps_name: string
        :param Apps_name: (optional) Tool desigation label.
        
        :type Apps_version: string
        :param Apps_version: (optional) Tool version label.
        
        :type logging_prompt: string
        :param logging_prompt: (optional) Specific prompt label (instead of the label automatically created using the tool version and designation ).
        
        :type logging_filename: string
        :param logging_filename: (optional) Logfile name. File to be created if option activated.
        
        :type verbosity_choices: list
        :param verbosity_choices: (optional) Available verbosity level list (from 0 to 1 by default.
        """
        # CLI init superclass
        super(DownloadCLI, self).__init__( 
            Apps_name=Apps_name,
            Apps_version=Apps_version,
            logging_filename=logging_filename,
            logging_prompt=logging_prompt,
            optparser_prompt_version=optparser_prompt_version,
            verbosity_choices=verbosity_choices
        )
        
    def get_commandline_options(self):
        """
        Command line arguments added. If all is correct, Django project initialised
        """
        self._CLI_Parser_.add_option("--add", dest="thread_list", nargs=2, action="append", help=u'Thread où chercher des fichiers. Le premier argument est le nom du canal (dans l\'url, pas son titre) et le second est l\'identifiant du thread', metavar="CANAL ID")
        self._CLI_Parser_.add_option("--target", dest="target_dir", default=None, help=u'Nom de répertoire relatif (au répertoire de base) à utiliser pour stocker les fichiers.', metavar="PATH")
        self._CLI_Parser_.add_option("--base_dir", dest="base_dir", default=None, help=u'Chemin absolu du répertoire de base ou le script va travailler. Par défaut c\'est le répertoire  courant du script.', metavar="PATH")
        self._CLI_Parser_.add_option("--base_url", dest="base_url", default=DEFAULT_CHAN_BASE_URL, help=u'Url de base du Chan à scanner, avec le http:// et le slash de fin (Default: %s)'%DEFAULT_CHAN_BASE_URL, metavar="PATH")
        self._CLI_Parser_.add_option("--refresh", dest="refresh_time", default=None, help=u'Temps en secondes à spécifier pour ré-effectuer le scan des éléments toute les X secondes. Vide par défaut, ce qui implique aucun refresh périodique, les éléments ne seront traités qu\'une seule fois.', metavar="SECONDS")
        self._CLI_Parser_.add_option("--db", dest="db_path", default=None, help=u'Chemin (absolu ou relatif) vers le fichier de bdd. Par défaut un fichier "%s" est créé dans le répertoire cible.'%DEFAULT_DB_FILENAME, metavar="PATH")
        self._CLI_Parser_.add_option("--parser", dest="parser_type", default=None, choices=('4chan', 'zerochan', 'ichan'), help=u'Type de parser de Chan parmi la liste: 4chan, zerochan, ichan. Par défaut le parser 4chan est utilisé.', metavar="STRING")
        
        # The superclass parses all arguments, after all additions have been made
        super(DownloadCLI, self).get_commandline_options()
        
    def launch(self):
        """
        Runs the commands
        """
        # Downloader parser type selection
        if self._CLI_Options_.parser_type == 'zerochan':
            ParserModule = ZeroChanDownloader
        if self._CLI_Options_.parser_type == 'ichan':
            ParserModule = IChanDownloader
        else:
            ParserModule = FourChanDownloader
        # Downloader init
        downloader = ParserModule(
            self._CLI_Logger_,
            root_dir=self._CLI_Options_.base_dir,
            target_dir=self._CLI_Options_.target_dir,
            base_url=self._CLI_Options_.base_url,
            db_filepath=self._CLI_Options_.db_path,
            debug=self._CLI_Debug_
        )
        if self._CLI_Options_.thread_list:
            i = 0
            tmp_save = []
            while len(self._CLI_Options_.thread_list)>0:
                self._CLI_Logger_.info( "THREAD ELEMENT:%s" % (i+1) )
                canal, thread_id = self._CLI_Options_.thread_list[0]
                # Protects the other thread from a single thread  http failure
                try:
                    downloader.process(canal, thread_id)
                except ChanBackendError:
                    # If it has failed, do not save the element so it is rescanned later
                    self._CLI_Options_.thread_list.pop(0)
                else:
                    # Save the element to rescan it later
                    tmp_save.append( self._CLI_Options_.thread_list.pop(0) )
                i += 1
                # If the end of the list is reached and a timer has been set, reset the list and restart the loop.
                if len(self._CLI_Options_.thread_list)==0 and self._CLI_Options_.refresh_time:
                    self._CLI_Logger_.title( "End of element list, restart from zero in %sseconds" % self._CLI_Options_.refresh_time )
                    sleep( float(self._CLI_Options_.refresh_time) )
                    self._CLI_Options_.thread_list = tmp_save[:]
                    i = 0
                    tmp_save = []
        
        # Superclass is in charge of managing the default commands (Test for instance) and to cleanly close the script
        super(DownloadCLI, self).launch()
    
#
if __name__ == "__main__":
    obj = DownloadCLI()
    obj.get_commandline_options()
    obj.launch()
