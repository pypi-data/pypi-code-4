from . import fasta
from . import fastq
import gzip,bz2
import os

FASTA_SUFFIXES = set(('.fa', '.fasta'))
FASTQ_SUFFIXES = set(('.fq', '.fastq'))
BAM_SUFFIXES = set('bam')

class FileFormatError(ValueError):
    pass

def _stream_factory(stream, extension):
    if extension in FASTA_SUFFIXES:
        stream = fasta.FastaFile(fileobj=ll_stream)
    elif extension in FASTQ_SUFFIXES:
        stream = fastq.FastqFile(fileobj=ll_stream)
    else:
        ValueError("stream without a know extension: %s" % extension)
    return stream

def open(filename, mode="rb"):
    """ Factory guessing the format from the file extension. """
    fn = filename.lower()
    tmp = fn.split(os.path.sep)[-1]
    tmp = tmp.split(os.path.extsep)
    if len(tmp) == 0:
        ValueError("File without an extension")
    # FIXME: BAM files chould be considered like BGZF streams.
    # AFAIK, the only Python interface to BGZF is in biopython.
    compression = None
    if len(tmp) > 1 and tmp[-1] == 'gz':
        ll_stream  = gzip.open(filename, mode=mode)
        compression = tmp.pop()
        stream = _stream_factory(ll_stream, tmp[-1])
    elif len(tmp) > 1 and tmp[-1] == 'bz2':
        ll_stream = bz2.open(filename, mode=mode)
        compression = tmp.pop()
        stream = _stream_factory(ll_stream, tmp[-1])
    elif tmp[-1] in BAM_SUFFIXES:
        from . import bam
        stream = bam.BamFile(filename, "rb")
    else:
        ll_stream = __builtins__['open'](filename, mode=mode)
        stream = _stream_factory(ll_stream, tmp[-1])
    
    return stream

