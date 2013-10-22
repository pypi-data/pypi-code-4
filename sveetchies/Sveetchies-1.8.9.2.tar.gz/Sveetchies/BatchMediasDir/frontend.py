#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from manager import BatchDirectory
from modules import *

if __name__ == "__main__":
    from optparse import OptionParser
    
    starttime = datetime.datetime.now()
    
    commandline_parser = OptionParser()
    commandline_parser.add_option("-p", "--path", dest="path", help=u"Path of the directory to scan to detect directories where valuable media can be found(ogg, mp3, flac, etc..).", metavar="PATH")
    commandline_parser.add_option("-c", "--cover", dest="cover_mode", default=False, action="store_true", help=u"Record sleeve. Unimplemented")
    commandline_parser.add_option("-r", "--rename", dest="rename_mode", default=False, action="store_true", help=u"Rename all detected elements(lower case, whitespaces become underscores, cleanup of special chars, aso.). In case of a name collision during a renaming, raises a blocking error.")
    commandline_parser.add_option("-s", "--stats", dest="stats_mode", default=False, action="store_true", help=u"List of the elements that have been modified")
    commandline_parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help=u"ACtivates a mode that does not write anything. the process runs entirely, but no writing on the disk is done.")
    #
    (commandline_options, commandline_args) = commandline_parser.parse_args()
    if not commandline_options.path:
        commandline_parser.error("Command need at least the 'path' option")
    #
    path = commandline_options.path
    debug = commandline_options.debug
    callables = []
    if commandline_options.rename_mode:
        callables.append(Renamer)
    if commandline_options.cover_mode:
        callables.append(Cover)
    if commandline_options.stats_mode:
        callables.append(Stats)
    #
    obj = BatchDirectory(callables=callables, debug=debug)
    obj.scan(path)
    obj.proceed()
    
    endtime = datetime.datetime.now()
    print "~~~ Lenght : %s" % str(endtime-starttime)
