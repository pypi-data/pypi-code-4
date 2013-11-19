"""
usage: %prog bigwig_file.bw  < bed_file.bed 
"""

from bx.bbi.bigwig_file import BigWigFile
import sys
bw = BigWigFile( open( sys.argv[1] ) )
for s in xrange(1000):
	print  bw.summarize('chr1', 10000, 10001, 1)

