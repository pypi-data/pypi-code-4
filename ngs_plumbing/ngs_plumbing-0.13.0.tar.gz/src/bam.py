import pysam
from . import fastq

SeqQualEntry = fastq.SeqQualEntry


class BamFile(pysam.Samfile):

    def iter_seqqual(self):
        """ Iterate through reads in a BAM stream, providing an interface similar
        to the one in the modules fastq and fasta """
        for read in self:
            yield SeqQualEntry('', read.seq, read.qual)
