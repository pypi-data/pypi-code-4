#!/usr/bin/env python

'''Author: Sourabh Bajaj'''


# Imports
from subprocess import call
import argparse
import traceback

def cppcompile():
    """
    Compile a Cplusplus file, execute it and remove the a.out
    """
    c_parser = argparse.ArgumentParser(description=__doc__)

    # File to compile
    c_parser.add_argument('filename', help='file name')

    # Keep the a.out file
    c_parser.add_argument('--keep', metavar="Keep the output file",
                          default=False, help= 'Format --keep',
                          action='store_const', const=True)
    
    c_parser.add_argument('-o', metavar="Rename the output file",
                          default='a.out', help='Format -o outputFile')

    args = c_parser.parse_args()
    
    filename = args.filename
    outputFile = args.o
    b_keep = args.keep

    try:
        call(["c++","-std=c++11","-stdlib=libc++", filename, "-o", outputFile])
    except:
        print "Compilation failed"
        traceback.print_exc()
        return

    try:
        call(["./" + outputFile])
    except:
        print "Output file failure"
        traceback.print_exc()
        return        
    
    if b_keep:
        return

    try:
        call(["rm", "-rf", outputFile])
    except:
        print "Could not remove the file"
        traceback.print_exc()
    
    return
    
if __name__ == '__main__':
    cppcompile()