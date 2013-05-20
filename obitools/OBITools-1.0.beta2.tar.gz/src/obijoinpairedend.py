#!/usr/local/bin/python
'''
:py:mod:`obijoinpairedend`: joins paired end reads
==================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obijoinpairedend` aims at joining the two reads of a paired-end library.

For this purpose, it concatenates sequence merging the forward read and the 
reversed-complemented reverse read. A stretch of N is added between both the reads.

The program uses as input one or two sequences reads files. 

    - If two files are used one of them must be specified using the ``-r`` option. 
      Sequence records corresponding to the same read pair must be in the same order 
      in the two files.
      
    - If just one file is provided, sequence records are supposed to be all of the same length.
      The first half of the sequence is used as forward read, the second half is used as the reverse
      read.

    *Example:*
    
    .. code-block:: bash
    
       > obijoinpairedend -r seq3P.fastq seq5P.fastq > seq.fastq
       
    The ``seq5P.fastq`` sequence file contains the forward sequence records.
    The ``seq3P.fastq`` sequence file contains the reverse sequence records.
    Pairs of reads are joined together and the resulting sequence is stored in the
    `` seq.fastq`` file.

'''

from obitools.options import getOptionManager

from itertools import chain
from obitools import NucSequence
from obitools.format.options import sequenceWriterGenerator, autoEntriesIterator,\
    addInOutputOption
from obitools.utils import universalOpen

def addPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )

    
def cutDirectReverse(entries):
    first = []
    
    for i in xrange(10):
        first.append(entries.next())
        
    lens = [len(x) for x in first]
    clen = {}
    for i in lens:
        clen[i]=clen.get(i,0)+1
    freq = max(clen.values())
    freq = [k for k in clen if clen[k]==freq]
    assert len(freq)==1,"To many sequence length"
    freq = freq[0]
    assert freq % 2 == 0, ""
    lread = freq/2
    
    seqs = chain(first,entries)
    
    for s in seqs:
        d = s[0:lread]
        r = s[lread:]
        yield(d,r)

    
def seqPairs(direct,reverse):
    for d in direct:
        r = reverse.next()
        yield(d,r)


        
def buildJoinedSequence(sequences,options):
    nqual = 10.**-(options.nqual/10.)
    junction = options.junction
    
    for d,r in sequences:
        r=r.complement()
        
        s = str(d) + str(r)
        
        seq = NucSequence(d.id + '_PairEnd',s,d.definition,**d)
        
        withqual = hasattr(d, 'quality') or hasattr(r, 'quality')
        
        if withqual:
            if hasattr(d, 'quality'):
                quality = d.quality
            else:
                quality = [10**-4] * len(d)
                
            quality.extend([nqual] * junction)
            
            if hasattr(r, 'quality'):
                quality.extend(r.quality)
            else:
                quality.extend([10**-4] * len(r))
                
            seq.quality=quality
            seq['pairend_limit']=len(d)

            
        yield seq
        
    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addPairEndOptions,addInOutputOption])
    
    (options, direct) = optionParser()
    
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reader = autoEntriesIterator(options)
        reverse = reader(universalOpen(options.reverse))
        sequences=seqPairs(direct,reverse)
    
    writer = sequenceWriterGenerator(options)

    for seq in buildJoinedSequence(sequences,options):
        writer(seq)
        
        

