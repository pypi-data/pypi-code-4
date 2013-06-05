#!/usr/bin/python
###############################################################################
#                                                                             #
#    reMooUtils                                                               #
#                                                                             #
#    Utilities for doing the work                                             #
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
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import font_manager as font_manager
import string

np.seterr(all='raise')

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class PassClass:
    """main workhorse"""
    def __init__(self, complexity):
        self.rand = None              # random numbr generator
        self.cardSize = (7.08, 2.165) # in inches, std business card for AUS
        
        # work out which chars we'll use
        self.complexity = complexity
        lc = [chr(I) for I in np.arange(97, 123)]
        uc = [chr(I) for I in np.arange(65, 91)]
        num = [chr(I) for I in np.arange(48, 58)]
        punc = [chr(I) for I in np.arange(33, 48)] + [chr(I) for I in np.arange(58, 65)] + [chr(I) for I in np.arange(94, 97)] + [chr(I) for I in np.arange(123, 127)]
        
        if self.complexity == 1:
            self.chars = lc
            self.punc = []
        elif self.complexity == 2:
            self.chars = lc + num
            self.punc = []
        elif self.complexity == 3:
            self.chars = lc + uc+ num
            self.punc = []
        elif self.complexity == 4:
            self.chars = lc + uc + num
            self.punc = punc
            self.puncAmnt = 1     # 10% punctuation
        else: # self.complexity == 5 or ???
            self.chars = lc + uc + num + punc
            self.punc = []

        # set the font
        # try to find source code pro
        self.fProps = [font_manager.FontProperties(), font_manager.FontProperties()] 
        sf = font_manager.findSystemFonts()
        bold = None
        reg = None
        
        for i in sf:
            if string.find(i, 'SourceCodePro-Bold.ttf') != -1:
                bold = font_manager.FontProperties(fname=i)
            if string.find(i, 'SourceCodePro-Regular.ttf') != -1:
                reg = font_manager.FontProperties(fname=i)

        if bold is not None:
            if reg is not None:
                self.fProps = [reg, bold]
            else:
                self.fProps = [bold, bold]
        else:
            if reg is not None:
                self.fProps = [reg, reg]
                
        # stick with 5 colors
        self.cols = ['#66A61E', '#E7298A', '#7570B3', '#D95F02', '#1B9E77']
        
    def buildCard(self, keyPhrase=None, accounts=[], fileName='card'):
        """Build the card and save to file
        
        keyPhrase is optional but recommended
        """
        # set up the random numbers
        if keyPhrase is None:
            # totally random!
            self.rand = np.random
        else:
             self.rand = np.random.RandomState([ord(A) for A in keyPhrase])
             
        # Make the card
        fig = plt.figure()
        ax = fig.gca()
        plt.subplots_adjust(left=.0001, bottom=.001, right=.9999, top=.9999, wspace=.0001, hspace=.0001)
        plt.xticks([], [])
        plt.yticks([], [])

        # these are set for Source code Pro YMMV
        x_start = 10
        y_start = 16
        y_jump = 45
        x_jump = 35

        # print back first if need be
        ax.set_ylim(0, 649)
        if len(accounts) == 0:
            ax.set_xlim(0, 1062)
            fig.set_size_inches(self.cardSize[0]/2, self.cardSize[1])
        else:
            ax.set_xlim(0, 2124)
            fig.set_size_inches(self.cardSize[0], self.cardSize[1])
            # we need to set the back of the card
            if len(accounts) > 14:
                print "WARNING: Can only fit 14 lines on the card, soz..."
            
            # print some numbers
            for y in range(14):
                ax.text(x_start + x_jump*31, 
                        y_start + y_jump*y, 
                        str(13-y),
                        color=self.randCol(),
                        fontproperties=self.randFont()
                        )

            # print the accounts on differenrt lines
            Ys = np.arange(14)
            self.rand.shuffle(Ys)
            
            for y in range(np.min([14, len(accounts)])):
                ax.text(x_start + x_jump*(33+self.rand.randint(27-len(accounts[y]))), 
                        y_start + y_jump*Ys[y], 
                        accounts[y],
                        color=self.randCol(),
                        fontproperties=self.randFont()
                        )

        # front of the card is always the same
        for x in range(30):
            for y in range(14):
                ax.text(x_start + x_jump*x, 
                        y_start + y_jump*y, 
                        self.randChar(),
                        color=self.randCol(),
                        fontproperties=self.randFont()
                        )


        # save and we're done
        plt.savefig(fileName ,dpi=300)
        plt.close()
        del fig

    def randFont(self):
        """Return a bolded or not bolded font"""
        return self.fProps[self.rand.randint(2)]

    def randChar(self):
        """Return a random char according to complexity"""
        if self.complexity != 4:
            return self.chars[self.rand.randint(len(self.chars))]
        else: # self.complexity == 4
            if self.rand.randint(10) < self.puncAmnt:
                return self.punc[self.rand.randint(len(self.punc))]
            else:
                return self.chars[self.rand.randint(len(self.chars))]

    def randCol(self):
        """Return a random color"""
        return self.cols[self.rand.randint(len(self.cols))]
        

###############################################################################
###############################################################################
###############################################################################
###############################################################################
