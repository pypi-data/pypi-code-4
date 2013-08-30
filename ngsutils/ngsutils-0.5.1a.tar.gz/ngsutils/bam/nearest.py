#!/usr/bin/env python
## category General
## desc Find the nearest annotated region for each read (from tabix-indexed file)
## experimental
'''
For each read, find the nearest annotated region from a tabix-indexed BED
file.

For example, if you have a BED file with the transcription starting site (TSS)
for all genes in the genome, this will find the nearest TSS for each read, and
report the distance to the site.
'''

import sys
import os


def usage(msg=None):
    if msg:
        sys.stderr.write('%s\n\n' % msg)
    sys.stderr.write(__doc__)
    sys.stderr.write('''\
Usage: bamutils nearest filename.bam tabix.bed

Note: tabix.bed.bgz and tabix.bed.bgz.tbi files must exist. You can create
these with "ngsutils tabixindex".
''')

    sys.exit(1)

if __name__ == '__main__':
    bam_fname = None
    bed_fname = None

    for arg in sys.argv[1:]:
        if not bam_fname and os.path.exists(arg):
            bam_fname = arg
        elif not bed_fname and os.path.exists(arg):
            bed_fname = arg

    if not bam_fname or not bed_fname:
        usage()