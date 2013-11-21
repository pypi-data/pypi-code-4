
from hgsvn import base_version, full_version, ui
from hgsvn.common import change_to_rootdir, fixup_hgsvn_dir, get_hgsvn_lock, LockHeld, load_hgsvn_branches_map, save_hgsvn_branches_map
from hgsvn.common import hgsvn_branchmap_options, update_config_branchmap, use_branchmap
from hgsvn.errors import HgSVNError

import sys
import os
from optparse import SUPPRESS_HELP
import re


copyright_message = """\
Copyright (C) 2007 Antoine Pitrou.
Copyright (C) 2009 Andi Albrecht.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

Written by Antoine Pitrou and Andi Albrecht.
"""


def on_option_verbosity(option, opt, value, parser, *args, **kwargs):
    #if "verbosity" in parser.values:
    if args[0] >= ui.DEBUG:
        parser.values.terminalwidth = 250
    
    if value is not None:
        parser.values.verbosity = value
    else:
        parser.values.verbosity = args[0]
        if len(parser.rargs) > 0:
            levelstr = parser.rargs[0]
            if levelstr[:1] != '-' :
                try:
                    level = int(levelstr)
                    parser.values.verbosity = level
                    del parser.rargs[0]
                except:
                    raise OptionValueError("invalid verbolity level value")
    ui.update_config(parser.values)

def on_option_branchmap_add(option, opt, value, parser):
    print "option_branchmap_add:%s"%value
    [svnpath, hgbranch] = re.split("=",value)
    ui.status("maping svn:%s -> hg:%s"%(svnpath, hgbranch), level=ui.DEBUG)
    update_config_branchmap(parser.values)
    use_branchmap(hgbranch, svnpath)

def run_parser(parser, long_help=""):
    """
    Add common options to an OptionParser instance, and run parsing.

    A hidden option is added to ease man page production with the help2man tool.
    For example, the following produces a (rather terse) man page for hgpullsvn:
    $ help2man -N "hgpullsvn --help2man" -o man1/hgpullsvn.1
    """
    parser.add_option("-m", "--mapbranch", type="string", dest="branchmaping", default="uao",
        help=("use map of branches with options <[n][o][a]>"
                "n - (No), denotes to avoid using currently collected map of hg branch - svn path"
                "o - (Over) denotes to replace mapingof current svn path"
                "a - (Add) allows add to map current svnbranch"
            )
                )
    parser.add_option("--branch-add", type="string", action="callback", callback=on_option_branchmap_add,
                      help=("append svn-hg branch map. format:<svn-path>=<hg-branch>"
                            "   example: -ba /branches/branchofsvn=branchofhg"
                           )
                     )
    parser.add_option("-l", "--hg-follow", dest="prefere2hg", default=False,
                      action="store_true",
                      help="prefere current hg-branch to pull-in, if all clean and"
                           " branch known - svn switches to last sync revision of hg-branch"
                     )
    parser.add_option("", "--version", dest="show_version", action="store_true",
        help="show version and exit")
    parser.add_option("", "--help2man", dest="help2man", action="store_true",
        help=SUPPRESS_HELP)
    parser.remove_option("--help")
    parser.add_option("-h", "--help", dest="show_help", action="store_true",
        help="show this help message and exit")
    parser.add_option("-v", "--verbose", dest="verbosity", default=10
                      , action="callback", callback=on_option_verbosity
                      , callback_args=(ui.VERBOSE,),
                      help=" -v [level] enables additional output, optionaly accepts level value")
    parser.add_option("--debug", dest="verbosity",
                      action="callback", callback=on_option_verbosity
                      , callback_args=(ui.DEBUG,),
                      help="enable debugging output")
    parser.add_option("--terminal-width", dest="terminalwidth", type="int", default=0, 
                      help=("override terminal width for output"
                            ", by default determined from COLUMNS environment variable"
                            " or 80 columns if it cant be determined"
                           )
                     )
    options, args = parser.parse_args()
    if options.show_help:
        if options.help2man and long_help:
            print long_help
            print
        parser.print_help()
        sys.exit(0)
    if options.show_version:
        prog_name = os.path.basename(sys.argv[0])
        if options.help2man:
            print prog_name, base_version
            print
            print copyright_message
        else:
            print prog_name, full_version
        sys.exit(0)
    ui.update_config(options)
    update_config_branchmap(options)
    return options, args

def display_parser_error(parser, message):
    """
    Display an options error, and terminate.
    """
    print "error:", message
    print
    parser.print_help()
    sys.exit(1)


def locked_main(real_main, *args, **kwds):
    """Wrapper for main() functions, that takes care of .hgsvn/lock."""
    # Make sure that we work in the checkout's top-level directory (issue3).
    try:
        change_to_rootdir()
    except HgSVNError, err:
        sys.stderr.write("%s\n" % err)
        return 1
    # We must do this before trying to take the lock file
    fixup_hgsvn_dir('.')
    try:
        l = get_hgsvn_lock()
    except LockHeld, e:
        print "Aborting:", e
        return 1
    try:
        res = real_main(*args, **kwds)
        save_hgsvn_branches_map()
        return res 
    finally:
        l.release()
