#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sveetch's Django Commande LIne

This Module is an extention of  `Sveetchies.SveePyCLI_Old` designed to handle 
a Django project directly from the command line.

Usually, it is a better idea to use ``djang-admin`` adjustable commands system
through the Django project than using DjangoCLI.
"""
__title__ = "Sveetch's Django Commande LIne"
__version__ = "0.1.0"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008 Sveetch.Biz"

LOGGING_FILENAME = "DjangoCLI.log"
DJANGO_SETTINGS_FILENAME = "settings"
DJANGO_PROJECT_DIR_HELP = "Absolute path to the Django project to manipulate. By default this is the current directory. (DEFAULT=%s)"
DJANGO_SETTINGS_FILENAME_HELP = "Settings filename (without '.py') of the Django project to manipulate. (DEFAULT=%s)"
DJANGO_INSTALLPATH_HELP = "Specify a pathname to your Django installation. Use this only if you don't have Django installed in your Python installation."

import os, sys, traceback
from Sveetchies.cli.SveePyCLI_Old import SveePyCLI_Old, \
                    OPTPARSER_USAGE, \
                    OPTPARSER_PROMPT_VERSION, \
                    LOGGING_DATE_FORMAT, \
                    LOGGING_FILEMODE, \
                    PRINT_OUTPUT_METHODS

from Sveetchies.cli.ImportDjangoProject import ImportDjangoProject

class DjangoCLI(SveePyCLI_Old):
    def __init__( self, Apps_name=__title__, Apps_version=__version__,
                    optparser_usage=OPTPARSER_USAGE,
                    logging_prompt=None,
                    optparser_prompt_version=OPTPARSER_PROMPT_VERSION,
                    logging_date_format=LOGGING_DATE_FORMAT,
                    logging_filename=LOGGING_FILENAME,
                    logging_filemode=LOGGING_FILEMODE,
                    print_output_methods=PRINT_OUTPUT_METHODS,
                    default_project_directory=os.getcwd(),
                    default_project_settings=DJANGO_SETTINGS_FILENAME
                ):
        """
        :type Apps_name: string
        :param Apps_name: (optional) Tool designation label.
        
        :type Apps_version: string
        :param Apps_version: (optional) Tool version label.
        
        :type optparser_usage: string
        :param optparser_usage: (optional) Tool use summary label
        
        :type logging_prompt: string
        :param logging_prompt: (optional) Specific prompt label
        Used instead of one created from the designation and label
        
        :type logging_date_format: string
        :param logging_date_format: (optional) Date format used in the logs
        (from the ``strftime() scheme).
        
        :type logging_filename: string
        :param logging_filename: (optional) Logfile name to create if used
\        
        :type logging_filemode: string
        :param logging_filemode: (optional) File read mode, append by default
        
        :type optparser_prompt_version: string
        :param optparser_prompt_version: (optional) Prompt version displayed by
                                    `optparse.OptionParser`.
        
        :type print_output_methods: list
        :param print_output_methods: (optional) Output methods list (logs, stdout, aso.)
                                    available
        
        :type default_project_directory: string
        :param default_project_directory: (optional) Django project directory to be used.
                                    By default, current directory is used
        
        :type default_project_settings: string
        :param default_project_settings: (optional) Setting module name (filename without
.py) for the project. By default, uses "settings".
        """
        # Default directory where to look for the Django project
        self.default_project_directory = default_project_directory
        #Default settings filename for the Django project
        self.default_project_settings = default_project_settings
        
        # init superclass
        super(DjangoCLI, self).__init__( Apps_name=Apps_name, Apps_version=Apps_version,
                    optparser_usage=optparser_usage,
                    logging_prompt=logging_prompt,
                    optparser_prompt_version=optparser_prompt_version,
                    logging_date_format=logging_date_format,
                    logging_filename=logging_filename,
                    logging_filemode=logging_filemode,
                    print_output_methods=print_output_methods,
                )
    """
    Baseclass to create a command line tool
    """
    def get_commandline_options(self):
        """
        Add arguments to the command line and initialising of the Django project if
        everything is fine
        """
        self._CLI_Parser_.add_option("--django_installpath",
dest="DJ_Installation_pathname", default=None, help=DJANGO_INSTALLPATH_HELP,
metavar="DIRECTORY")
        self._CLI_Parser_.add_option("--django_project", dest="DJ_Project_pathname", default=self.default_project_directory, help=DJANGO_PROJECT_DIR_HELP%self.default_project_directory, metavar="DIRECTORY")
        self._CLI_Parser_.add_option("--django_settings", dest="DJ_Project_settings_name", default=self.default_project_settings, help=DJANGO_SETTINGS_FILENAME_HELP%self.default_project_settings, metavar="FILE")
        self._CLI_Parser_.add_option("--django_test", dest="DJ_Project_test", default=False, action="store_true", help="Simple Django test.")
        
        # The superclass parses all arguments after they have all been added
        super(DjangoCLI, self).get_commandline_options()
        
        #Makes some attributes more accessible
        self.DJ_Project_pathname = self._CLI_Options_.DJ_Project_pathname
        self.DJ_Project_settings_name = self._CLI_Options_.DJ_Project_settings_name
        self.DJ_Installation_pathname = self._CLI_Options_.DJ_Installation_pathname
        # Report for the debug and the verbose mode
        self.print_output("Django Project Absolute pathname : %s" % self.DJ_Project_pathname)
        self.print_output("Django Project Settings name : %s" % self.DJ_Project_settings_name)
        if self.DJ_Installation_pathname:
            self.print_output("Django custom installation pathname : %s" % self.DJ_Installation_pathname)
        
        # Tries to import all that is needed to reach the projet
        try:
            self.DJ_Project_settings = ImportDjangoProject(self.DJ_Project_pathname, self.DJ_Project_settings_name, self.DJ_Installation_pathname)
            if not self.DJ_Project_settings:
                raise ImportError, "Unable to import project with directory '%s'" % self.DJ_Project_pathname
        # import failed. We stop here silently but the error is logged
        except:
            self.print_output("! DJANGO OR PROJECT IMPORTATION FAILED !", indent_logging="")
            self.print_output("! TRACEBACK :", indent_logging="")
            self.print_output(traceback.format_exc(), indent_logging="")
            #Starting superclass is called to cleanly stop the script
            super(DjangoCLI, self).stop()
        
        
    def launch(self):
        """
        Starts the commands. Nothing automatic yet
        """
        if self._CLI_Options_.DJ_Project_test:
            self.DjangoTest()
        
        # The super class is in charge of managing the commands available by default
        # (like Test) and to stop the script
        super(DjangoCLI, self).launch()
    
    def DjangoTest(self):
        """
        Tests wether the Django project is accessible for the script
        """
        # Django project access test using its settings
        foo = self.DJ_Project_settings.DATABASE_ENGINE
        self.print_output("* Access test to the project is OK !")
        # Database access test using contrib.site installed almost everywhere
        from django.contrib.sites.models import Site
        site_current = Site.objects.get_current()
        self.print_output("* Access test to the database is OK !")
    
#
if __name__ == "__main__":
    obj = DjangoCLI( Apps_name=__title__, Apps_version=__version__,
                    logging_filename=LOGGING_FILENAME )
    obj.get_commandline_options()
    obj.launch()