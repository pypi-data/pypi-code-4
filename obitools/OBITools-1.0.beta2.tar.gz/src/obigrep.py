#!/usr/local/bin/python
'''
:py:mod:`obigrep`: Filters sequence file 
=========================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`obigrep` command is in some way analog to the standard Unix ``grep`` 
command.
It selects a subset of sequence records from a :ref:`sequence file <../format>`. 

A sequence record is a :doc:`complex object <../fasta>` composed of an identifier, 
a set of attributes (``key=value``), a definition, and the sequence itself. 

Instead of working text line by text line as the standard Unix tool, selection is 
done sequence record by sequence record. 
A large set of options allows refining selection on any of the sequence record 
elements.

Moreover :py:mod:`obigrep` allows specifying simultaneously several conditions (that 
take the value ``TRUE`` or ``FALSE``) and only the sequence records that fulfill all 
the conditions (all conditions are ``TRUE``) are selected.

'''


from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator

if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption],progdoc=__doc__)
    
    (options, entries) = optionParser()
    goodSeq   = sequenceFilterIteratorGenerator(options)

    writer = sequenceWriterGenerator(options)
    
    for seq in goodSeq(entries):
        writer(seq)
            
            
