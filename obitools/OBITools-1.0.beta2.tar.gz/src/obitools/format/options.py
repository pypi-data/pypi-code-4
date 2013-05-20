'''
Created on 13 oct. 2009

@author: coissac
'''

from obitools.format.sequence.embl import emblIterator
from obitools.format.sequence.genbank import genbankIterator
from obitools.format.sequence.fnaqual import fnaFastaIterator
from obitools.format.sequence.fasta import fastaAAIterator, fastaNucIterator, fastFastaIterator
from obitools.format.sequence.fastq import fastFastqIlluminaIterator,fastFastqSolexaIterator

from obitools.fastq import fastFastqSangerIterator
from obitools.fnaqual.quality import qualityIterator
from obitools.ecopcr.sequence import EcoPCRDBSequenceIterator
from obitools.fasta import formatFasta, rawFastaIterator,\
                           formatSAPFastaGenerator
from obitools.fastq import formatFastq

from obitools.ecopcr.sequence import EcoPCRDBSequenceWriter
from obitools.ecopcr.options  import loadTaxonomyDatabase

from cPickle import dump,load,UnpicklingError

#from obitools.format._format import printOutput

from array import array
from itertools import chain
import sys

import re
from obitools.ecopcr import EcoPCRFile
from obitools.format.sequence import skipOnErrorIterator
from obitools import BioSequence
from obitools.utils import FakeFile




def binarySequenceIterator(lineiterator):    
            
    f = FakeFile(lineiterator)
            
    try:
        while(1):
            try:
                s = load(f)
                yield s
            except UnpicklingError:
                pass
    except EOFError:
        raise StopIteration

def addInputFormatOption(optionManager):

    group = optionManager.add_option_group("Input format options",
                    "If not specified, a test is done to determine the file format")

    group.add_option('--genbank',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='genbank',
                     help="Input file is in genbank format")
    
    group.add_option('--embl',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='embl',
                     help="Input file is in embl format")
    
    group.add_option('--skip-on-error',
                     action="store_true", dest="skiperror",
                     default=False,
                     help="Skip sequence entries with parse error")
    
    group.add_option('--fasta',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='fasta',
                     help="Input file is in fasta nucleic format (including obitools fasta extentions)")

    group.add_option('--ecopcr',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='ecopcr',
                     help="Input file is in ecopcr format")
    
    group.add_option('--raw-fasta',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='rawfasta',
                     help="Input file is in fasta format (but more tolerant to format variant)")

#    group.add_option('--fna',
#                     action="store_const", dest="seqinformat",
#                     default=None,
#                     const='fna',
#                     help="input file is in fasta nucleic format produced by 454 sequencer pipeline")
#
#    group.add_option('--qual',
#                     action="store", dest="withqualfile",
#                     type='str',
#                     default=None,
#                     help="Specify the name of a quality file produced by 454 sequencer pipeline")

    group.add_option('--sanger',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='sanger',
                     help="Input file is in sanger fastq nucleic format (standard fastq)")

    group.add_option('--solexa',
                     action="store_const", dest="seqinformat",
                     default=None,
                     const='solexa',
                     help="Input file is in fastq nucleic format produced by solexa sequencer")

    #===========================================================================
    # group.add_option('--illumina',
    #                         action="store_const", dest="seqinformat",
    #                         default=None,
    #                         const='illumina',
    #                         help="input file is in fastq nucleic format produced by old solexa sequencer")
    #===========================================================================

    group.add_option('--ecopcrdb',
                      action="store_const", dest="seqinformat",
                      default=None,
                      const='ecopcrdb',
                      help="Input file is an ecopcr database")

    group.add_option('--nuc',
                     action="store_const", dest="moltype",
                     default=None,
                     const='nuc',
                     help="Input file contains nucleic sequences")
    
    group.add_option('--prot',
                     action="store_const", dest="moltype",
                     default=None,
                     const='pep',
                     help="Input file contains protein sequences")

def addOutputFormatOption(optionManager):

    group = optionManager.add_option_group("Output format options")


#    optionManager.add_option('-B','--bin-output',
#                             action="store_const", dest="output",
#                             default=None,
#                             const=dump,
#                             help="output sequences in binary format")
    group.add_option('--fasta-output',
                             action="store_const", dest="output",
                             default=None,
                             const=formatFasta,
                             help="Output sequences in obitools fasta format")
    group.add_option('--fastq-output',
                             action="store_const", dest="output",
                             default=None,
                             const=formatFastq,
                             help="Output sequences in sanger fastq format")
#    group.add_option('--sap-output',
#                             action="store_const", dest="output",
#                             default=None,
#                             const=formatSAPFastaGenerator,
#                             help="Output sequences in sap fasta format "
#                                  "(Sequence must have a taxid and a taxonomy has to be loaded)")
    
    group.add_option('--ecopcrDB-output',
                             action="store", dest="ecopcroutput",
                             default=None,
                             help="Output sequences in ecopcr database format "
                                  "(sequence records are not printed on standard output)")
    group.add_option('--uppercase',
                             action='store_true',dest='uppercase',
                             default=False,
                             help="Print sequences in upper case (default is lower case)")



def addInOutputOption(optionManager):
    addInputFormatOption(optionManager)
    addOutputFormatOption(optionManager)


def autoEntriesIterator(options):
    options.outputFormater=formatFasta
    options.outputFormat="fasta"
    
    ecopcr_pattern = re.compile('^[^ ]+ +| +[0-9]+ +| + [0-9]+ + | +')
    
    def annotatedIterator(formatIterator):
        options.outputFormater=formatFasta
        options.outputFormat="fasta"
        def iterator(lineiterator):
            for s in formatIterator(lineiterator):
                s.extractTaxon()
                yield s

        return iterator

    def withQualIterator(qualityfile):
        options.outputFormater=formatFastq
        options.outputFormat="fastq"
        def iterator(lineiterator):
            for s in fnaFastaIterator(lineiterator):
                q = qualityfile.next()
                quality = array('d',(10.**(-x/10.) for x in q))
                s.quality=quality
                yield s
                
        return iterator

    def autoSequenceIterator(lineiterator):
        options.outputFormater=formatFasta
        options.outputFormat="fasta"
        first = lineiterator.next()

        if first[0]==">":
#            if options.withqualfile is not None:
#                qualfile=qualityIterator(options.withqualfile)
#                reader=withQualIterator(qualfile)
#                options.outputFormater=formatFastq
#                options.outputFormat="fastq"
            if options.moltype=='nuc':
                reader=fastaNucIterator
            elif options.moltype=='pep':
                reader=fastaAAIterator
            else:
                reader=fastFastaIterator
        elif first[0]=='@':
            reader=fastFastqSangerIterator
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
        elif first[0:3]=='ID ':
            reader=emblIterator
        elif first[0:6]=='LOCUS ':
            reader=genbankIterator
        elif first[0:8]=="#!Pickle":
            reader=binarySequenceIterator
        elif first[0]=="#" or ecopcr_pattern.search(first):
            reader=EcoPCRFile 
        else:
            raise AssertionError,'file is not in fasta, fasta, embl, genbank or ecoPCR format'
        
        if reader==binarySequenceIterator:
            input = binarySequenceIterator(lineiterator)
        else:
            input = reader(chain([first],lineiterator))
    
        return input
                
    if options.seqinformat is None:
        reader = autoSequenceIterator
    else:
        if options.seqinformat=='fasta':
            if options.moltype=='nuc':
                reader=fastaNucIterator
            elif options.moltype=='pep':
                reader=fastaAAIterator
            else:
                reader=fastFastaIterator
        elif options.seqinformat=='rawfasta':
            reader=annotatedIterator(rawFastaIterator)
        elif options.seqinformat=='genbank':
            reader=annotatedIterator(genbankIterator)
        elif options.seqinformat=='embl':
            reader=annotatedIterator(emblIterator)
        elif options.seqinformat=='fna':
            reader=fnaFastaIterator
        elif options.seqinformat=='sanger':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastFastqSangerIterator
        elif options.seqinformat=='solexa':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastFastqSolexaIterator
        elif options.seqinformat=='illumina':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastFastqIlluminaIterator
        elif options.seqinformat=='ecopcr':
            reader=EcoPCRFile
        elif options.seqinformat=='ecopcrdb':
            reader=EcoPCRDBSequenceIterator
            
        if options.seqinformat=='fna' and options.withqualfile is not None:
            qualfile=qualityIterator(options.withqualfile)
            reader=withQualIterator(qualfile)
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            
    if options.skiperror:
        reader = skipOnErrorIterator(reader)

    return reader

def sequenceWriterGenerator(options,output=sys.stdout):
    class SequenceWriter:
        def __init__(self,options,file=sys.stdout):
            self._format=None
            self._file=file
            self._upper=options.uppercase
        def put(self,seq):
            if self._format is None:
                self._format=formatFasta
                if options.output is not None:
                    self._format=options.output
                    if self._format is formatSAPFastaGenerator:
                        self._format=formatSAPFastaGenerator(options)
                elif options.outputFormater is not None:
                    self._format=options.outputFormater
            s = self._format(seq,upper=self._upper)
            try:
                self._file.write(s)
                self._file.write("\n")
            except IOError:
                sys.exit(0)
                
    class BinaryWriter:
        def __init__(self,options,file=sys.stdout):
            self._file=file
            self._file.write("#!Pickle\n")
        def put(self,seq):
            try:
                if isinstance(seq, BioSequence):
                        dump(seq,self._file,protocol=2)
                else:
                    for s in seq:
                        dump(s,self._file,protocol=2)
            except IOError:
                sys.exit(0)
           
                
    if options.ecopcroutput is not None:
        taxo = loadTaxonomyDatabase(options)
        writer=EcoPCRDBSequenceWriter(options.ecopcroutput,taxonomy=taxo)
    elif options.output==dump:
        writer=BinaryWriter(options,output)
    else:
        writer=SequenceWriter(options,output)
        
    def sequenceWriter(sequence):
        writer.put(sequence)

    return sequenceWriter
    
    