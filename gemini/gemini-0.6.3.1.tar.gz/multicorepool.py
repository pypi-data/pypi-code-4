#! /usr/bin/env python
import random
import readline
import mmap
import multiprocessing as mp
import Queue
import time
import vcf as vcf
import cyvcf as cyvcf

import sys
import os

filemap = None

def getchunks(file, size=4*1024*1024):
    
    prev_offset = 0
    while 1:
        s = f.readline()
        offset = f.tell()
        if not s.startswith("#"):
            break
        prev_offset = offset

    f.seek(prev_offset, 0)
    chunks = []
    while 1:
        start = f.tell()
        f.seek(size, 1)
        s = f.readline()
        chunks.append((start, f.tell() - start))
        if not s:
            break
    return chunks


def process(file, chunk):
    file.seek(chunk[0])
    buffer = []
    while True:
        try:
            line = file.readline()
        except StopIteration:
            break
        offset = file.tell()      
        if offset >= chunk[0]+chunk[1] or not line: break
        buffer.append(line)  
    return buffer
                
def printrec(rec):
    global vcffile
    print vcf.VCFReader.parse(vcffile, rec)

if __name__ == '__main__':

    if sys.argv[1] == "m":
        filename = sys.argv[2] 
        f = open(filename)
        chunks = getchunks(f)
        f.close()
        
        vcffile = vcf.VCFReader(open(sys.argv[2]), 'rb')
        file = open(sys.argv[2])
        
        pool = mp.Pool(processes=4)
        for chunk in chunks:
            buffer = process(file, chunk)
            pool.map(printrec, buffer)
    elif sys.argv[1] == "s":
        vcf_reader = vcf.VCFReader(open(sys.argv[2]), 'rb')
        for rec in vcf_reader:
            print rec
