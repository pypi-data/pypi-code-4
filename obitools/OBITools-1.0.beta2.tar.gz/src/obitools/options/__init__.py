"""
    Module providing high level functions to manage command line options.
"""
import logging
import sys

from logging import debug

from optparse import OptionParser
from optparse import IndentedHelpFormatter                     

from obitools.utils import universalOpen
from obitools.utils import fileSize
from obitools.utils import universalTell
from obitools.utils import progressBar
from obitools.format.options import addInputFormatOption, addInOutputOption,\
    autoEntriesIterator
import time
    
from _options import fileWithProgressBar, \
                     currentInputFileName, \
                     currentInputFile, \
                     currentFileSize, \
                     currentFileTell, \
                     allEntryIterator

class ObiHelpFormatter (IndentedHelpFormatter):
    def __init__(self,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 short_first=1):
        IndentedHelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

    def format_heading(self, heading):
        return '\n'.join(("%*s%s" % (self.current_indent, "", '*'*(len(heading)+4)),
                          "%*s* %s *" % (self.current_indent, "", heading),
                          "%*s%s\n" % (self.current_indent, "", '*'*(len(heading)+4))))


def getOptionManager(optionDefinitions,entryIterator=None,progdoc=None,checkFormat=False):
    '''
    Build an option manager function. that is able to parse
    command line options of the script.
    
    @param optionDefinitions: list of function describing a set of 
                              options. Each function must allows as
                              unique parameter an instance of OptionParser.
    @type optionDefinitions:  list of functions.
    
    @param entryIterator:     an iterator generator function returning
                              entries from the data files. 
                              
    @type entryIterator:      an iterator generator function with only one
                              parameter of type file
    '''

    parser = OptionParser(usage=progdoc, formatter=ObiHelpFormatter())
    parser.add_option('--DEBUG',
                      action="store_true", dest="debug",
                      default=False,
                      help="Set logging in debug mode")

    parser.add_option('--without-progress-bar',
                      action="store_false", dest="progressbar",
                      default=True,
                      help="desactivate progress bar")

    for f in optionDefinitions:
        if f == addInputFormatOption or f == addInOutputOption:
            checkFormat=True 
        f(parser)
        
        
    def commandLineAnalyzer():
        options,files = parser.parse_args()
        if options.debug:
            logging.root.setLevel(logging.DEBUG)
            
        if checkFormat:
            if not hasattr(options, "skiperror"):
                options.skiperror=False
            ei=autoEntriesIterator(options)
        else:
            ei=entryIterator
        
            
        options.readerIterator=ei
        
        i = allEntryIterator(files,ei,with_progress=options.progressbar)
        return options,i
    
    return commandLineAnalyzer


        