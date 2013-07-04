""" 
Parsing NGS file. 

The guiding principle here is to abstract the file
format and extract sequencing reads and their
associated quality string (whenever available).

File formats are guessed from the extension names.

"""
from . import fasta
from . import fastq
import gzip,bz2
import os, sys

if sys.version_info[0] == 2:
    _is_python2 = True
else:
    _is_python2 = False

FASTA_SUFFIXES = set(('fa', 'fasta'))
FASTQ_SUFFIXES = set(('fq', 'fastq'))
BAM_SUFFIXES = set('bam')

class FileFormatError(ValueError):
    pass

def _stream_factory(ll_stream, extension):
    if extension in FASTA_SUFFIXES:
        stream = fasta.iter_entries(ll_stream)
    elif extension in FASTQ_SUFFIXES:
        stream = fastq.iter_entries(ll_stream)
    else:
        ValueError("stream without a known extension: %s" % extension)
    return stream

def open(filename, mode="rb", buffering=int(2**23)):
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
        #fh = __builtins__['open'](filename, mode=mode, 
        #                          buffering=buffering)
        fh = filename
        ll_stream  = gzip.open(fh, mode=mode)
        compression = tmp.pop()
        stream = _stream_factory(ll_stream, tmp[-1])
    elif len(tmp) > 1 and tmp[-1] == 'bz2':
        if _is_python2:
            ll_stream = bz2.BZ2File(filename, mode=mode)
        else:
            fh = __builtins__['open'](filename, mode=mode, 
                                      buffering=buffering)
            ll_stream = bz2.open(fh, mode=mode)
        compression = tmp.pop()
        stream = _stream_factory(ll_stream, tmp[-1])
    elif tmp[-1] in BAM_SUFFIXES:
        from . import bam
        stream = bam.BamFile(filename, "rb")
    else:
        ll_stream = __builtins__['open'](filename, mode=mode, 
                                         buffering=buffering)
        stream = _stream_factory(ll_stream, tmp[-1])
    
    return stream

