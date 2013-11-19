#!/usr/bin/python

import array
import gzip
import struct
import numpy as np
import multiprocessing as mp


class BinaryGenoWriter(object):
    """
    Class for creating and writing to a gemini
    binary genotype file (gzipped).
    """
    def __init__(self, filestub, num_variants, num_samples):
        self.num_variants = num_variants
        self.num_samples = num_samples
        self.filestub = filestub
        self.filename = self.filestub + ".gbin.gz"
        self.filehandle = gzip.open(self.filename, 'wb')
        self.write_header()

    def write_header(self):
        """Add a magic number and the number of vars/samples
           as a header.  This allows subsequent reads to check
           the provenance of the file and now exactly the size
           of each block of genotyes (i.e., num_samples)
        """
        # magic number
        self.filehandle.write('%s' % 'gemini')
        # need to pack so that integers < 4 bytes are padded to fill 4 bytes.
        self.filehandle.write(struct.pack('ii', self.num_variants, self.num_samples))
        
    def write(self, gt_types_buffer):
        """
        Write a buffer's worth of genotypes to the file.
        gt_types_buffer is a list or array
        """
        data = np.array(gt_types_buffer, dtype='uint8')
        self.filehandle.write(data)

    def get_filename(self):
        return self.filename

    def close(self):
        self.filehandle.close()

class BinaryGenoReader(object):
    """
    Class for opening and reading bytes from a gemini
    binary genotype file (gzipped).
    """
    def __init__(self, filename):
        self.filename = filename
        # 100Mb buffer
        self.read_buff_size = 100*1024*1024
        self.filehandle = gzip.open(self.filename, 'rb')
        # make sure the file is in the right format
        self.read_header()
        
    def read_header(self):
        """
        Make sure we have the right format and extract
        the number of variants and number of samples.
        This tells us how to "stride" through the bytes.
        That is, which ind/sample does the byte belong to?
        """
        magic = self.filehandle.read(6)
        if magic != 'gemini':
            sys.exit('incorrect file format')
        # note: struct.unopack returns a tuple
        self.num_variants = struct.unpack("i", self.filehandle.read(4))[0]
        self.num_samples = struct.unpack("i", self.filehandle.read(4))[0]

    def __iter__(self):
        return self

    def next(self):
        """
        Return the next buffer of bytes from the file.
        """
        bytes = self.filehandle.read(self.read_buff_size)
        return bytes

class GenotypeTypeCounter(object):
    """
    Example class for counting the number of each
    type of genotype (het, hom_alt, etc.) for each
    sample.
    """
    def __init__(self, filename):
        self.filename = filename
        self.byte_num = 0
        self.reader = BinaryGenoReader(self.filename)
        self.num_variants = self.reader.num_variants
        self.num_samples = self.reader.num_samples
        
        self.num_hom_ref = np.zeros(self.num_samples, dtype=np.int)
        self.num_het     = np.zeros(self.num_samples, dtype=np.int)
        self.num_hom_alt = np.zeros(self.num_samples, dtype=np.int)
        self.num_unknown = np.zeros(self.num_samples, dtype=np.int)

    def _count(self, raw_byte):
        byte = ord(raw_byte)
        ind = self.byte_num % self.num_samples
        var = int(self.byte_num / self.num_samples)
        # 0 / 00000000 hom ref
        # 1 / 00000001 het
        # 2 / 00000010 missing
        # 3 / 00000011 hom alt
        if not byte & 1 and not byte & 2:
            self.num_hom_ref[ind] += 1
        elif byte & 1 and not byte & 2:
            self.num_het[ind] += 1
        elif byte & 1 and byte & 2:
            self.num_hom_alt[ind] += 1
        elif not byte & 1 and byte & 2:
            self.num_unknown[ind] += 1
        self.byte_num += 1

    def count_gts(self):
        while 1:
            bytes = self.reader.next()
            if len(bytes) == 0:
                break
            map(self._count, bytes)

    def total_gts(self, i):
        return self.num_hom_ref[i] + \
               self.num_het[i] + \
               self.num_hom_alt[i] + \
               self.num_unknown[i]

    def report_counts(self):
        for i in xrange(self.num_samples):
            print i, \
                  self.num_hom_ref[i], \
                  self.num_het[i], \
                  self.num_hom_alt[i], \
                  self.num_unknown[i], \
                  self.total_gts(i)

num_vars = 1000
num_inds = 100
# simulate genotypes and write to file
gt_writer = BinaryGenoWriter("foo", num_vars, num_inds)

# simulate gemini building a buffer of genotypes from the VCF file
# and then writing the buffer to the binary file.
num_bufs = 10
for i in xrange(0,num_bufs):
    print i
    gts = np.random.randint(low=0, high=4, size=(num_vars*num_inds)/num_bufs)
    gt_writer.write(gts)

gt_writer.close()
filename = gt_writer.get_filename()

#count genotypes
gt_counter = GenotypeTypeCounter(filename)
gt_counter.count_gts()
gt_counter.report_counts()


