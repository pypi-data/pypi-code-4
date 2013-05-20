#!/usr/local/bin/python
"""
:py:mod:`obicomplement`: Reverses complements sequences 
=======================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obicomplement` reverses complements the sequence records.


    .. TIP:: The identifiers of the sequence records are modified by appending
             to them the ``_CMP`` suffix.
             
    .. TIP:: a attribute with key ``complemented`` and value sets to ``True`` is added
             on each reversed complemented sequence record.
             
By using the selection option set, it is possible to reverse complement only a subset of the
sequence records included in the input file. The selected sequence are reversed complemented,
others are stored without modification 

    *Example 1:* 
    
    .. code-block:: bash
    
       > obicomplement seq.fasta > seqRC.fasta
       
    Reverses complements all sequence records from the ``seq.fasta`` file and stores the 
    result to the ``seqRC.fasta`` file.

    *Example 2:* 
    
    .. code-block:: bash
    
       > obicomplement -s 'A{10,}$' seq.fasta > seqRC.fasta
       
    Reverses complements sequence records from the ``seq.fasta`` file only if they finish
    by at least 10 ``A``. Others sequences are stored without modification.

"""

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.format.options import addInOutputOption, sequenceWriterGenerator


if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption], progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    goodFasta = filterGenerator(options)
    writer = sequenceWriterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            writer(seq.complement())
        else:
            writer(seq)

            