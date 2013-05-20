#!/usr/local/bin/python
'''
:py:mod:`obitail`: Extracts the last sequence records
======================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obitail` command is in some way analog to the standard Unix `tail` command.
It selects the tail of :ref:`a sequence file <../format>`. 
But instead of working text line by text line as the standard Unix tool, 
selection is done at the sequence record level. You can specify the number of 
sequence records to select.

  *Example:*
    
    .. code-block:: bash
        
          > obitail -n 150 seq1.fasta > seq2.fasta
    
    Selects the 150 last sequence records from the ``seq1.fasta`` file and stores
    them into the ``seq2.fasta`` file.


'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
import collections

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
    
    queue = collections.deque(entries,options.count)

    writer = sequenceWriterGenerator(options)
   
    while queue:
        writer(queue.popleft())
        
        
        

