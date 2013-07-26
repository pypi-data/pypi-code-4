#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
__title__ = "Batch directories cover shell script"
__version__ = "1.0"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008-2009 sveetch.biz"
__license__ = "GPL"

LOGGING_FILENAME = "BatchDirCoversCLI.log"

import os, sys, traceback
from Sveetchies.SveePyCLI import SveePyCLI, \
                    OPTPARSER_USAGE, \
                    OPTPARSER_PROMPT_VERSION, \
                    LOGGING_DATE_FORMAT, \
                    LOGGING_FILEMODE, \
                    PRINT_OUTPUT_METHODS

from Sveetchies.BatchDirCovers import BatchDirCovers

class BatchDirCoversCLI(SveePyCLI):
    def __init__( self, Apps_name=__title__, Apps_version=__version__,
                    optparser_usage=OPTPARSER_USAGE,
                    logging_prompt=None,
                    optparser_prompt_version=OPTPARSER_PROMPT_VERSION,
                    logging_date_format=LOGGING_DATE_FORMAT,
                    logging_filename=LOGGING_FILENAME,
                    logging_filemode=LOGGING_FILEMODE,
                    print_output_methods=PRINT_OUTPUT_METHODS
                ):
        
        # ...
        
        # La superclasse d'init
        super(BatchDirCoversCLI, self).__init__( Apps_name=Apps_name, Apps_version=Apps_version,
                    optparser_usage=optparser_usage,
                    logging_prompt=logging_prompt,
                    optparser_prompt_version=optparser_prompt_version,
                    logging_date_format=logging_date_format,
                    logging_filename=logging_filename,
                    logging_filemode=logging_filemode,
                    print_output_methods=print_output_methods,
                )
    """
    Classe de base pour faire un outil de commande en ligne
    """
    def get_commandline_options(self):
        """
        Rajout des arguments de la ligne de commande et initialisation du 
        projet Django si tout est correct
        """
        self._CLI_Parser_.add_option("--django_installpath", dest="DJ_Installation_pathname", default=None, help="help", metavar="DIRECTORY")
        
        # La superclasse s'occupe de parser tout les arguments après que les 
        # ajouts sont finis
        super(BatchDirCoversCLI, self).get_commandline_options()
        
        # Rapport pour le debug et le mode verbeux
        self.print_output("Django Project Absolute pathname : %s" % self.DJ_Project_pathname)
        if self.DJ_Installation_pathname:
            self.print_output("Django custom installation pathname : %s" % self.DJ_Installation_pathname)
        
        # ...
        try:
            True
        except:
            # On apelle la superclasse de launch qui va couper proprement le script
            super(BatchDirCoversCLI, self).stop()
        
        
    def launch(self):
        """
        Lance les commandes.
        """
        if self._CLI_Options_.DJ_Project_test:
            self.DjangoTest()
        
        # La superclasse s'occupe de gérer les commandes par défaut (comme Test) 
        # et de clore le script
        super(BatchDirCoversCLI, self).launch()
    
    
    def DjangoTest(self):
        """
        ...
        """
        self.print_output("* Foo !")
        
    
#
#
if __name__ == "__main__":
    obj = BatchDirCoversCLI( Apps_name=__title__, Apps_version=__version__,
                    logging_filename=LOGGING_FILENAME )
    obj.get_commandline_options()
    obj.launch()

