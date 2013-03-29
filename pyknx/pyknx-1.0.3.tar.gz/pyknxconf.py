#!/usr/bin/python

# Copyright (C) 2012-2013 Cyrille Defranoux
#
# This file is part of Pyknx.
#
# Pyknx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyknx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyknx. If not, see <http://www.gnu.org/licenses/>.
#
# For any question, feature requests or bug reports, feel free to contact me at:
# knx at aminate dot net

"""
Modifies an XML config file for Linknx so that it allows for communication with an instance of pyknxcommunicator.py
This script adds an ioport and a rule for each object that holds a pyknxcallback attribute in the source XML.
It always starts by cleaning any autogenerated rule from the input file and generates new ones unless the --clean option is passed.

USAGE:
	pyknxconf.py [-c communicatoraddress] -i inputfile [-o outputfile]

OPTIONS:
    -c --comm-addr <host:port>   Address of the communicator. This argument must specify the hostname or the ip address followed by a colon and the port to listen on. Default is localhost:1029'
    -i --inputfile               Filename of the original linknx xml config file. This file is modified by this script if no output file is specified.'
    -o --outputfile              Filename of the modified linknx xml config file to write. If missing, this argument defaults to the same file than the one specified with --inputfile.'
    -p --rule-prefix             Prefix for the rules generated by this script. Default is "pyknxrule_"'
    -v,--verbose                 Level of verbosity. Value must be one of the logging module (error, warning, info, debug)
       --clean                   Clean rules that were generated by this script but do not generate new rules. Rules to delete are those whose id starts by the rule prefix'
       --help                    Display this help message and exit.'
"""

from pyknx.configurator import Configurator
import getopt
import sys
import logging
from pyknx import logger

def printUsage():
	print __doc__

def parseAddress(addrStr, option):
    ix = addrStr.find(':')
    if ix < 0:
        raise Exception('Malformed value for ' + option +'. Expecting a tuple (hostname:port)')
    return (addrStr[0:ix], addrStr[ix + 1:])

if __name__ == '__main__':
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'c:i:o:p:', ['comm-addr=', 'input-file=', 'output-file=', 'rule-prefix=', 'verbose', 'clean', 'help'])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    # Parse command line arguments.
    communicatorAddress = ('127.0.0.1',1029)
    inputFile = None
    outputFile = None
    rulePrefix = 'pyknxrule_'
    cleanOnly = False
    verbosity = logging.INFO
    for option, value in options:
        if option == '-c' or option == '--comm-addr':
            communicatorAddress = parseAddress(value, option)
        elif option == '-i' or option == '--input-file':
            inputFile = value
        elif option == '-o' or option == '--output-file':
            outputFile = value
        elif option == '-p' or option == '--rule-prefix':
            rulePrefix = value
        elif option == '--verbose':
            verbosity = logging.DEBUG
        elif option == '--clean':
            cleanOnly = True
        elif option == '--help':
            printUsage()
            sys.exit(1)
        else:
            print 'Unrecognized option ' + option
            sys.exit(2)

    if not inputFile:
        printUsage()
        sys.exit(1)

    if not outputFile:
        outputFile = inputFile

    # Configure logger.
    logger.initLogger(None, verbosity)

    # Start configurator.
    configurator = Configurator(inputFile, outputFile, communicatorAddress, rulePrefix)

    # Generate config.
    configurator.cleanConfig()
    if not cleanOnly:
        configurator.generateConfig()
    configurator.writeConfig()
