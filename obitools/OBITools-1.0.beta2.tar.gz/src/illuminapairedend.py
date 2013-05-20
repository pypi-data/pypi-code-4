#!/usr/local/bin/python
'''
:py:mod:`illuminapairedend`: aligns paired end Illumina reads
=============================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

.. IMPORTANT:: :py:mod:`illuminapairedend` replaces ``solexapairend``.

:py:mod:`illuminapairedend` aims at aligning the two reads of a pair-end library sequenced 
using an Illumina platform. 

    - If the two reads overlap, it returns the consensus sequence together with its quality 
    
    - Otherwise, it concatenates sequence merging the forward read and 
      the reversed-complemented reverse read.

The program uses as input one or two :doc:`fastq <../fastq>` sequences reads files. 

    - If two files are used one of them must be specified using the ``-r`` option. 
      Sequence records corresponding to the same read pair must be in the same order 
      in the two files.
      
    - If just one file is provided, sequence records are supposed to be all of the same length.
      The first half of the sequence is used as forward read, the second half is used as the reverse
      read.

:py:mod:`illuminapairedend` align the forward sequence record with the reverse complement of the 
reverse sequence record. The alignment algorithm takes into account the base qualities.

    *Example:*
    
    .. code-block:: bash
    
       > illuminapairedend -r seq3P.fastq seq5P.fastq > seq.fastq
       
    The ``seq5P.fastq`` sequence file contains the forward sequence records.
    The ``seq3P.fastq`` sequence file contains the reverse sequence records.
    Pairs of reads are aligned together and the consensus sequence is stored in the
    `` seq.fastq`` file.

'''

from obitools import NucSequence
from obitools.options import getOptionManager, allEntryIterator
from obitools.align import QSolexaReverseAssemble
from obitools.align import QSolexaRightReverseAssemble
from obitools.tools._solexapairend import buildConsensus
from obitools.format.options import addInputFormatOption,addOutputFormatOption,\
    sequenceWriterGenerator

from itertools import chain
import cPickle
import math

def addSolexaPairEndOptions(optionManager):
    optionManager.add_option('-r','--reverse-reads',
                             action="store", dest="reverse",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="Filename containing reverse solexa reads "
                            )
    optionManager.add_option('--sanger',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='sanger',
                             help="input file is in sanger fastq nucleic format (standard fastq)")

    optionManager.add_option('--solexa',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='solexa',
                             help="input file is in fastq nucleic format produced by solexa sequencer")

    optionManager.add_option('--illumina',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='illumina',
                             help="input file is in fastq nucleic format produced by old solexa sequencer")

#    optionManager.add_option('--proba',
#                             action="store", dest="proba",
#                             metavar="<FILENAME>",
#                             type="str",
#                             default=None,
#                             help="null ditribution data file")
    

    optionManager.add_option('--score-min',
                             action="store", dest="smin",
                             metavar="#.###",
                             type="float",
                             default=None,
                             help="minimum score for keeping aligment")

#    optionManager.add_option('--pvalue',
#                             action="store", dest="pvalue",
#                             metavar="#.###",
#                             type="float",
#                             default=None,
#                             help="maximum pvalue for keeping aligment")
    


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

def checkAlignOk(ali):
    #print not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    return not (ali[0][0]=='-' or ali[1][len(ali[1])-1]=='-')
    
la = QSolexaReverseAssemble()
ra = QSolexaRightReverseAssemble()

def buildAlignment(direct,reverse):
    
    if len(direct)==0 or len(reverse)==0:
        return None
        
    la.seqA=direct 
    la.seqB=reverse 
    ali=la()
    ali.direction='left'
    
    ra.seqA=direct
    ra.seqB=reverse
    rali=ra()
    rali.direction='right'
    
    if ali.score < rali.score:
        ali=rali

    return ali
        
def alignmentIterator(sequences):
    
    for d,r in sequences:
        ali = buildAlignment(d,r)
        if ali is None:
            continue
        yield ali
        
      
def buildJoinedSequence(ali,options):
    d = ali[0].getRoot()
    r = ali[1].getRoot()

    
    r=r.complement()
    
    s = str(d) + str(r)
    
    seq = NucSequence(d.id + '_PairEnd',s,d.definition,**d)
    
    withqual = hasattr(d, 'quality') or hasattr(r, 'quality')
    
    if withqual:
        if hasattr(d, 'quality'):
            quality = d.quality
        else:
            quality = [10**-4] * len(d)
                    
        if hasattr(r, 'quality'):
            quality.extend(r.quality)
        else:
            quality.extend([10**-4] * len(r))
            
        seq.quality=quality
        
    seq['score']=ali.score
    seq['direction']=ali.direction
    seq['mode']='joined'
    seq['pairend_limit']=len(d)
    
    return seq

    
    
if __name__ == '__main__':
    optionParser = getOptionManager([addSolexaPairEndOptions,addOutputFormatOption],checkFormat=True
                                    )
    
    (options, direct) = optionParser()
    
    #WARNING TO REMOVE : DIRTY PATCH !
    options.proba = None


    options.sminL = None
    options.sminR = None

    
    if options.proba is not None and options.smin is None:
        p = open(options.proba)
        options.nullLeft  = cPickle.load(p)
        options.nullRight = cPickle.load(p)
        
        assert options.pvalue is not None, "You have to indicate a pvalue or an score min"
        
        i = int(math.floor((1.0 - options.pvalue) * len(options.nullLeft)))
                           
        if i == len(options.nullLeft):
            i-=1
        options.sminL = options.nullLeft[i]
        
        i = int(math.floor((1.0 - options.pvalue) * len(options.nullRight)))
        if i == len(options.nullRight):
            i-=1
        options.sminR = options.nullRight[i]
        
    if options.smin is not None:
        options.sminL = options.smin
        options.sminR = options.smin
        
        
    if options.reverse is None:
        sequences=cutDirectReverse(direct)
    else:
        reverse = allEntryIterator([options.reverse],options.readerIterator)
        sequences=seqPairs(direct,reverse)
        
    writer = sequenceWriterGenerator(options)
    
    ba = alignmentIterator(sequences)
                
    for ali in ba:
        
        if options.sminL is not None:
            if (   (ali.direction=='left' and ali.score > options.sminL) 
                or (ali.score > options.sminR)):
                consensus = buildConsensus(ali)
            else:
                consensus = buildJoinedSequence(ali, options)
                
            consensus['sminL']=options.sminL
            consensus['sminR']=options.sminR
        else:
            consensus = buildConsensus(ali)
                        
        writer(consensus)
        
        
        
        

