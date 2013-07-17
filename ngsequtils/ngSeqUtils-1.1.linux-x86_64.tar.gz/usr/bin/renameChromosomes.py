#!/usr/bin/python

'''
---------------------------------
common.ngseq.renameChromosomes.py
---------------------------------

This stand-alone script reads a simple tab-delimited conversion file that 
describes the conversion from a current chromosome naming convention to the
desired naming convention, and then converts the header of an existing bamfile 
from the one, to the other. Optionally, the .bai index file is also generated 
for the resulting output bam file.

.. moduleauthor:: Nick Schurch <nschurch@dundee.ac.uk>

:module_version: 1.2
:created_on: 2013-07-16

Command-line Arguments
======================

**usage\:** 
    renameChromosomes.py
    :param: <input bam file>
    :param: <output bam file> 
    :param: <input text file>
    :option:`-l|--log` *<file>* 
    [:option:`--index`]
    [:option:`-v|--verbose`] 
    [:option:`--version`] 
    [:option:`--help`]

Required Parameters
-------------------

:para: <input bam file>

  The input bam file

:param: <output bam file>

  The output bam file

:para: <input text file>

   A simple tab-delimited conversion file that describes the conversion from the 
   current chromosome naming convention to the desired naming convention.
   
   For example (A.thaliana):
       Chr1    1
       Chr2    2
       Chr3    3
       Chr4    4
       Chr5    5
       mitochondria   Mt
       chloroplast    Pt

:option:`--logfile|-l`        

  The name (inc. path) of the log file from the wrapper.

Optional Parameter
------------------

:option:`--index|-i`

  Create the index file for the output bam file

:option:`--help|-h`

  Print a basic description of the tool and its options to STDOUT.

:option:`--version`    

  Show program's version number and exit.
    
:option:`--verbose|-v`     

  Turn on verbose logging (recommended).

Output
======

A bam file with the new chromosome labels in the header.

'''

__version__ = "1.0"
__usage__ = "\n\t%s <input bam file> <input text file> <output bam file> " \
            "-l|--logfile <file> \n\t[--version] [-v|--verbose] [--help]"
__progdesc__ = '''
TThis stand-alone script reads a simple tab-delimited conversion file that 
describes the conversion from a current chromosome naming convention to the
desired naming convention, and then converts the header of an existing bamfile 
from the one, to the other. Optionally, the .bai index file is also generated 
for the resulting output bam file.  
'''

import sys, os, logging, pysam, re
import script_options.custom_callables as cc
import script_options.standard_parsers as sp
import script_logging.standard_logging as sl

if __name__ == '__main__':
    
    # parse command line options
    # Set standard parser
    parser, pos_args, kw_args = sp.standard_parser(__version__,
                                                   prog = sys.argv[0], 
                                                   usage = __usage__,
                                                   description = __progdesc__,
                                                   infile = True,
                                                   outfile = True,
                                                   tmpdir = False)
    
    add_reqarggroup = parser.add_argument_group('Additional Options (required)')
    
    infilehelp = "Specify a tab-delimited conversion file that describes the " \
                 "conversion from the current chromosome naming convention " \
                 "to the desired naming convention. For example " \
                 "(A.thaliana):\n\tChr1\t1\n\tChr2\t2\netc."

    add_reqarggroup.add_argument('convfile',
                                 action = 'store',
                                 type = cc.input_file,
                                 help = infilehelp 
                                 )
    pos_args.append(('convfile', None))
    
    add_optarggroup = parser.add_argument_group('Additional Options (optional)')
    
    indexhelp = "If specified, generate the index for the output bam file"

    add_optarggroup.add_argument('-i', '--index',
                                 action = 'store_true',
                                 default = False,
                                 help = indexhelp 
                                 )
    kw_args.append(('index', False))

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
    root_logger.info("Reading input bam file...")
    bam_in = None
    try:
        bam_in = pysam.Samfile(args.infile, "rb" )
    except ValueError as e:
        msg = "Input file (%s) does not appear to be a bam file!" % args.infile 
        print msg
        root_logger.info(msg)
        raise e
    
    root_logger.info("Reading input tab-delimited text file...")
    conv_in = {}
    try:
        f = open(args.convfile, "r" )
        conv_data = f.readlines()
        f.close()
        for line in conv_data:
            if line.strip()!="":
                line_data = re.split("\t",line.strip())
                conv_in[line_data[0]] = line_data[1]

        root_logger.info("Input conversion file contained %i values." \
                         "" % len(conv_in.keys()))
    except ValueError as e:
        msg = "Input file (%s) does not appear to be a readable file!" \
              "" % args.infile 
        print msg
        root_logger.info(msg)
        raise e
    except IndexError as e:
        msg = "Input file (%s) does not appear to contain two " \
              "tab-separated columns!" % args.convfile 
        print msg
        root_logger.info(msg)
        raise e

    root_logger.info("Processing header conversion details...")
    # stream from one bam to another
    header_in = bam_in.header
    replaced_values=0
    for entry in header_in["SQ"]:
        if entry["SN"] in conv_in.keys():
            entry["SN"] = conv_in[entry["SN"]]
            replaced_values+=1
    
    root_logger.info("Found and replaced %i chromosome values in %s." \
                     "" % (replaced_values, args.infile))
    
    root_logger.info("Writing new bam file: %s ..." % args.outfile)
    log_mult=0
    log_grain=1E6
    printcounter = 0
    outfile = pysam.Samfile(args.outfile, "wb", header=header_in)
    for read in bam_in:
        outfile.write(read)
        printcounter+=1
        if printcounter==log_grain:
            log_mult+=1
            printcounter = 0            
            root_logger.info("\t%i reads done" % (log_mult*log_grain))
    
    if args.index:
        root_logger.info("Writing index for new bam file: %s.bai ..." \
                         "" % args.outfile)
        pysam.index(args.outfile)
    
    root_logger.info("\t%i reads done" % ((log_mult*log_grain)+printcounter))
    root_logger.info("Output saved to file: %s" % (args.outfile))
    root_logger.info("finished.")

