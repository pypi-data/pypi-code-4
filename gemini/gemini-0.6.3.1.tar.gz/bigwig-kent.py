"""
usage: %prog bigwig_file.bw  < bed_file.bed 
"""
import sys
import subprocess
from subprocess import Popen, PIPE
from bx.intervals.io import GenomicIntervalReader

bigwig = sys.argv[1]
for interval in GenomicIntervalReader( sys.stdin ):
	c = interval.chrom
	s = str(interval.start)
	e = str(interval.start + 1)

	p = subprocess.Popen(['bigWigSummary', '-type=mean', bigwig, c, s, e, '1'], stdout=PIPE)
	output = p.stdout

	#bws = bw.get(interval.chrom, interval.start, interval.start+1)
	#print interval.chrom, interval.start, interval.start+1, bws.min_val, bws.max_val, bws.sum_data
	print interval.chrom, interval.start, interval.start+1