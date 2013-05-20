#!/usr/local/bin/python

'''
:py:mod:`obiannotate`: Adds/Edits sequence record annotations
=============================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiannotate` is the command that allows adding/modifying/removing 
annotation attributes attached to sequence records.

Once such attributes are added, they can be used by the other OBITools commands for 
filtering purposes or for statistics computing.

*Example:*

    .. code-block:: bash
        
        > obiannotate -S short:'len(sequence)<100' seq1.fasta > seq2.fasta

    The above command adds an attribute named *short* which has a boolean value indicating whether the sequence length is less than 100bp.

*Example:*

    .. code-block:: bash
        
        > obiannotate --rank seq1.fasta | obiannotate -C --set-identifier '"'FungA'_%05d" % seq_rank' > seq2.fasta

    The above command adds a new attribute whose value is the sequence record 
    entry number in the file. Then it clears all the sequence record attributes 
    and sets the identifier to a string beginning with *FungA_* followed by a 
    suffix with 5 digits containing the sequence entry number.

*Example:*

    .. code-block:: bash
        
        > obiannotate -d my_ecopcr_database --with-taxon-at-rank=genus seq1.fasta > se2.fasta

    The above command adds taxonomic information at the *genus* rank to the 
    sequence records. 

*Example:*

    .. code-block:: bash
        
        > obiannotate -S 'new_seq:str(sequence).replace("a","t")' seq1.fasta | obiannotate --set-sequence new_seq > seq2.fasta

    The overall aim of the above command is to edit the *sequence* object itself, 
    by replacing all nucleotides *a* by nucleotides *t*. First, a new attribute 
    named *new_seq* is created, which contains the modified sequence, and then 
    the former sequence is replaced by the modified one.
    
'''

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.options.bioseqedittag import addSequenceEditTagOptions
from obitools.options.bioseqedittag import sequenceTaggerGenerator
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
        
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,
                                     addSequenceEditTagOptions,
                                     addInOutputOption], progdoc=__doc__)

    (options, entries) = optionParser()
    
    writer = sequenceWriterGenerator(options)
    
    sequenceTagger = sequenceTaggerGenerator(options)
    goodFasta = filterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            sequenceTagger(seq)
        writer(seq)
            
