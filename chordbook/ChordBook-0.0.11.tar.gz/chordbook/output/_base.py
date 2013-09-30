# _base.py

# Base class for ChordBook outputters

import os
import chordbook.libcbk


class CbkOutputter(object):

    def __init__(self):
        """Subclasses should call this then set their own file suffix"""
        self.outputdir = self.__class__.__name__
        self.output = ""
        self.stdout = False
        self.outputfilesuffix = "repr.txt"

    def make_book(self, b):
        """Store internal representation of Book object"""

        # Just do a repr() on the book object
        self.output = repr(b);

        # Subclasses need to call this at the end of their make_book() 
        self.output_book(b.filename)

    def output_book(self, filename):
        """ Either print output to stdout or save it as file.
            Filename of json data file given as argument - is used to derive output filename"""

        if self.stdout == True:
            print self.output
        else:
            # create output file name from given filename
            root, suffix = os.path.splitext(os.path.basename(filename))
            outputfile = ".".join([root, self.outputfilesuffix])

            # check outputdir exists, create it if not
            if os.path.isdir(self.outputdir) == False:
                # FIXME - what if the following fails?
                os.mkdir(self.outputdir)
            
            # write the file
            outfile = os.path.join(self.outputdir, outputfile)

            # FIXME - what if any of the following fail?
            f = open(outfile, "w")
            f.write(self.output)
            f.close()
