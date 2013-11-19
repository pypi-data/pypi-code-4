#! /usr/bin/env python
import random
import multiprocessing
import Queue
import time
import vcf
import sys


if __name__ == '__main__':
    vcf_reader = vcf.VCFReader(open(sys.argv[1]), 'rb')
    buf = []
    for var in vcf_reader:
        buf.append(var)
        
    for v in buf:
        print v