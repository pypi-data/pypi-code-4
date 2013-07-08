#!/usr/bin/python

'''
---------------------------------------------------------
common.ngseq.switchStrand.py
---------------------------------------------------------

This stand-alone script reads a bam file and switches the strand alignment of 
each read in the file. The reads in the bam file have the sequence of the read 
stored appropriate to the 5'-3' forwards strand of the reference DNA regardless
of whether the read maps to the forward or reverse strand. This is good, because
it means that all this script has to do to reverse the strandedness information
is change the flags saying whether a read maps on the forward or reverse strand.

.. moduleauthor:: Nick Schurch <nschurch@dundee.ac.uk>

:module_version: 1.1
:created_on: 2013-07-08

Command-line Arguments
======================

**usage\:** 
    switchStrand.py
    :param: <input bam file>
    :param: <output bam file> 
    :option:`-l|--log` *<file>* 
    [:option:`--tmpdir`] 
    [:option:`-v|--verbose`] 
    [:option:`--version`] 
    [:option:`--help`]

Required Parameters
-------------------

:para: <input bam file>

  The input bam file

:param: <output bam file>

  he output bam file

:option:`--logfile|-l`        

  The name (inc. path) of the log file from the wrapper.

Optional Parameter
-------------

:option:`--help|-h`

  Print a basic description of the tool and its options to STDOUT.

:option:`--version`    

  Show program's version number and exit.
    
:option:`--verbose|-v`     

  Turn on verbose logging (recommended).

Output
======

A bam file with the new read sequences and strand assignments.

'''

__version__ = "1.1"
__usage__ = "\n\t%s <input bam file> <output bam file> -l|--logfile <file> " \
            "\n\t[--version] [-v|--verbose] [--help]"
__progdesc__ = '''
This stand-alone script reads a bam file and switches the strand alignment of 
each read in the file. The reads in the bam file have the sequence of the read 
stored appropriate to the 5'-3' forwards strand of the reference DNA regardless
of whether the read maps to the forward or reverse strand. This is good, because
it means that all this script has to do to reverse the strandedness information
is change the flags saying whether a read maps on the forward or reverse strand.  
'''
__progepi__ = '''
----------------------------
common.ngseq.switchStrand.py
----------------------------
'''

import sys, os, logging, pysam
import script_options.standard_parsers as sp
import script_logging.standard_logging as sl

if __name__ == '__main__':
    
    # parse command line options
    # Set standard parser
    parser, pos_args, kw_args = sp.standard_parser(__version__,
                                                   prog = sys.argv[0], 
                                                   usage = __usage__,
                                                   description = __progdesc__,
                                                   epilog = __progepi__,
                                                   infile = True,
                                                   outfile = True,
                                                   tmpdir = False)
        
    # parse arguments
    args = parser.parse_args()
    
    # setup standard logging information
    root_logger = logging.getLogger(__name__)
    root_logger.setLevel(logging.INFO)
    if args.verbose:
        root_logger.setLevel(logging.DEBUG)
    logfile_handler = sl.get_logfile_handler(args)
    root_logger.addHandler(logfile_handler)
    sl.standard_logger(__version__, sys.argv, args, pos_args, 
                       kw_args, logbase=__name__)
    
    # check that the input file is infact a bam file
    root_logger.info("Reading input file...")
    bam_in = None
    try:
        bam_in = pysam.Samfile(args.infile, "rb" )
    except ValueError as e:
        msg = "Input file (%s) does not appear to be a bam file!" % args.infile 
        print msg
        root_logger.info(msg)
        raise e
    
    root_logger.info("Processing reads...")
    # stream from one bam to another
    log_mult=0
    log_grain=1E6
    printcounter = 0
    outfile = pysam.Samfile(args.outfile, "wb", template=bam_in)
    for read in bam_in:
        read.is_reverse = not read.is_reverse
        outfile.write(read)
        printcounter+=1
        if printcounter==log_grain:
            log_mult+=1
            printcounter = 0            
            root_logger.info("\t%i reads done" % (log_mult*log_grain))
    
    root_logger.info("\t%i reads done" % ((log_mult*log_grain)+printcounter))
    root_logger.info("Output saved to file: %s" % (args.outfile))
    root_logger.info("finished.")


