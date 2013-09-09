
from __init__ import *

import sys
import csv
import json
import cPickle

from StringIO import StringIO

from os.path import splitext

from pprint import pprint

from config import Configurator

log_levels = {'DEB': logging.DEBUG,
              'INF': logging.INFO,
              'WAR': logging.WARN,
              'ERR': logging.ERROR,
              'CRI': logging.CRITICAL,
              'FAT': logging.FATAL,
              }

def prettyPrint(obj, fmt='pretty'):

    if fmt not in ['pretty', 'json', 'html']:
        raise ValueError('invalid prettyPrint format: "{0}"'.format(fmt))

    if fmt == 'pretty':
        pprint(obj)

    elif fmt == 'json':
        print json.dumps(obj, indent=4)

    elif fmt == 'html':
        result = """\
<div>
<div>
<span>Series Metadata</Span>
<table style="border-collapse: collapse; border-width: 1px; border-color: black; border-stype: solid;">
<thead><th>Series Metadata Descriptor</th><th>Value</th></thead>
<tbody>"""

        for ser_md in obj:
            if ser_md == 'samples' or ser_md[0] == '_': continue

            result += '<tr><td>{0}</td><td>{1}</td>\n'.format(ser_md, obj[ser_md])
            
        result += '</tbody>\n</table>\n</div>\n'

        #for smp_md in obj['samples']:

        result += """\
<hr/>
<div>
<span>Sample Medata</span>
<ul>
"""
        for smp_md in obj['samples']:
            result += "<li>"+smp_md['sample_id']+"</li>\n<ul>\n"
            for att in smp_md:
                result += "<li>"+att+": "
                if isinstance(smp_md[att], dict):
                    result += "</li>\n<ul>\n"
                    for ch in smp_md[att]:
                        result += "<li>"+ch+": "+smp_md[att][ch]+"</li>\n"
                    result += "</ul>\n"

                else:
                    result += `smp_md[att]`+"</li>\n"
            result += "</ul>\n"

        result += "</ul>\n</div>\n</div>"

        print result
            
    

def main():
    
    # Build a configuration parser and get the operating params for processing
    # this dataset.
    config = Configurator(use_msg="usage: %prog [options] [dataset]")

    config.add_option('--url', '-U', action='store', type='string', default=':memory:',
                       help='URL of the databse to be created and loaded')

    config.add_option('--separator', '-s', action='store', default='\t',
                      help="Column SEPARATOR string")

    config.add_option("--input", "-i", action='store', type='string', default='',
                      help="Input file in GEO format.")

    config.add_option("--output", "-o", action='store', type='string', default='',
                      help="Output file in TSV format.")

    config.add_option("--group-by", "-g", action='store', type='string', default='0',
                      help="group columns at the specified index level")

    config.add_option("--log2", "-2", action='store_true', default=False,
                      help="expression values will be converted to log2")

    config.add_option("--show-levels", action='store_true', default=False,
                      help="Output an enumerated list of column group levels.")

    config.add_option("--show-metadata", action='store_true', default=False,
                      help="Outpiut metadata.")

    config.add_option("--metadata-format", action='store', type='string', default='pretty',
                      help="Output format for metadata.  Default is 'pretty' print.  Othere format(s): json, html")

    config.add_option('--verbose', '-v', action='store_true', help='turn on verbose logging', default=False)
    config.add_option('--debug', '-d', default='WARN', help='debug level (DEBUG, INFO, [WARN], ERROR, CRITICAL, FATAL)')

    opts, args = config()

    log.setLevel(log_levels.get(opts.debug[:3].upper(), logging.WARN))

    log.debug('configuration processed:  opts={0}, args={1}'.format(opts, args))


    # Open and read in the series matrix file
    # Pickle and save the resulting object.
    if opts.input != '':
        infile = open(opts.input)
        # First try to load it as though it were a pickled instance of GEOSeries
        try:
            gmd = cPickle.load(infile)
        except:
            infile.seek(0)
            gmd = GEOSeries(infile, sep=opts.separator, log2=opts.log2)
            pickleFilename = splitext(opts.input)[0] + '.P'
            cPickle.dump(gmd, open(pickleFilename, 'w'), -1)

    elif len(args) == 0 :
        config.print_help()
        sys.exit(1)

    elif args[0] == '-':
        inbuf = StringIO(stdin.read())
        try:
            gmd = cPickle.load(inbuf)
        except:
            inbuf.seek(0)
            gmd = GEOSeries(inbuf, sep=opts.separator, log2=opts.log2)
            cPickle.dump(gmd, open(pickleFilename, 'w'), -1)

    else:
        infile = open(args[0])
        try:
            gmd = cPickle.load(infile)
        except:
            infile.seek(0)
            gmd = GEOSeries(infile, sep=opts.separator, log2=opts.log2)
            pickleFilename = splitext(args[0])[0] + '.P'
            cPickle.dump(gmd, open(pickleFilename, 'w'), -1)


    # Output column grouping levels
    if opts.show_levels:
        print 'Column Grouping Levels:'
        print 'Level\tName'
        levs = dict(sample_id=set())
        for samp in gmd.metadata.samples:
            levs['sample_id'].add(samp.sample_id)
            for ch in samp.characteristics.items():
                if not levs.has_key(ch[0]): levs[ch[0]] = set()
                levs[ch[0]].add(ch[1])
                
        for lev in enumerate(gmd.column_index_levels):
            print '{0[0]}:\t{0[1]}'.format(lev)
            if lev[1] != 'sample_id':
                for val in levs[lev[1]]: 
                    print '\t\t{0}'.format(val)
            print

    # Dump out the dataset metadata
    if opts.show_metadata:
        prettyPrint(gmd.metadata.toJSON(), fmt=opts.metadata_format)

    # Dump out dataset proper?
    if opts.output != '':

        # Group the columns?
        lev = None
        if opts.group_by != '':
            try:
                lev = int(opts.group_by)
            except:
                lev = opts.group_by

            if lev not in gmd.column_index_levels and lev not in range(len(gmd.column_index_levels)):
                raise ValueError('Invalid column index level specified: "{0}"'.format(lev))

        gmd.to_tsv(sys.stdout if opts.output == '-' else open(opts.output, 'w'), 
                   level=lev,
                   sep=opts.separator)
        


if __name__ == '__main__': 
    main()
