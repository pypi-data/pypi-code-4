#!/usr/bin/python
###############################################################################
#                                                                             #
#    remotemoose                                                              #
#                                                                             #
#    Wraps coarse workflows                                                   #
#                                                                             #
#    Copyright (C) Michael Imelfort                                           #
#                                                                             #
###############################################################################
#                                                                             #
#             8888888b.          888b     d888                                #                   
#             888   Y88b         8888b   d8888                                #                   
#             888    888         88888b.d88888                                #
#             888   d88P .d88b.  888Y88888P888  .d88b.   .d88b.               #
#             8888888P" d8P  Y8b 888 Y888P 888 d88""88b d88""88b              #
#             888 T88b  88888888 888  Y8P  888 888  888 888  888              #             
#             888  T88b Y8b.     888   "   888 Y88..88P Y88..88P              #
#             888   T88b "Y8888  888       888  "Y88P"   "Y88P"               #
#                                                                             #
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__author__ = "Michael Imelfort"
__copyright__ = "Copyright 2012"
__credits__ = ["Michael Imelfort"]
__license__ = "GPL3"
__version__ = "0.1.0"
__maintainer__ = "Michael Imelfort"
__email__ = "mike@mikeimelfort.com"
__status__ = "Alpha"

###############################################################################

# system imports
import argparse
import sys
import os 

# reMoo imports
from reMooUtils import PassClass

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class RMOptionsParser():
    def __init__(self): pass
    
    def parseOptions(self, options ):
        """Direct program flow"""
        PC = PassClass(options.complexity)
        PC.buildCard(keyPhrase=options.keyphrase,
                     accounts=options.accounts,
                     fileName=options.filename)
        

###############################################################################
###############################################################################
###############################################################################
###############################################################################
