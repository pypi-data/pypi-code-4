#!/usr/local/bin/python
'''
:py:mod:`obihead`: Extracts the first sequence records
=======================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obihead` command is in some way analog to the standard Unix `head` command.
It selects the head of  :ref:`a sequence file <../format>`. 
But instead of working text line by text line as the standard Unix tool, 
selection is done at the sequence record level. You can specify the number of sequence records 
to select.

  *Example:*

    
    .. code-block:: bash
    
         > obihead -n 150 seq1.fasta > seq2.fasta
    
    Selects the 150 first sequence records from the ``seq1.fasta`` file and stores
    them into the ``seq2.fasta`` file.


'''
import sys
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager


def addHeadOptions(optionManager):
    optionManager.add_option('-n','--sequence-count',
                             action="store", dest="count",
                             metavar="###",
                             type="int",
                             default=10,
                             help="Count of first sequences to print")
    

if __name__ == '__main__':
    optionParser = getOptionManager([addHeadOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    i=0

    writer = sequenceWriterGenerator(options)
    
    for s in entries:
        if i < options.count:
            writer(s)
            i+=1
        else:
            print >>sys.stderr,""
            sys.exit(0)
            
        

