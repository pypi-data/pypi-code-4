#!/usr/local/bin/python
'''
:py:mod:`obisort`: Sorts sequence records according to the value of a given attribute 
=====================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obisort` sorts sequence records according to the value of a given attribute, which can be either numeric or alphanumeric.

'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager

def addSortOptions(optionManager):
    group=optionManager.add_option_group('Obisort specific options')
    group.add_option('-k','--key',
                             action="append", dest="key",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="Attribute used to sort the sequence records.")
    
    group.add_option('-r','--reverse',
                             action="store_true", dest="reverse",
                             default=False,
                             help="Sorts in reverse order.")
    
def cmpGenerator(options):

    keys=options.key
    lk=len(keys)-1

    def cmpkeys(x,y,i=0):
        k=keys[i]
        c=cmp(x[k],y[k])
        if c==0 and i < lk:
            i+=1
            c=cmpkeys(x, y,i+1)
        if i==lk:
            i=0
        return c
    
    return cmpkeys

            

if __name__ == '__main__':

    optionParser = getOptionManager([addSortOptions,addInOutputOption])
    
    (options, entries) = optionParser()

    cmpk=cmpGenerator(options)
    
    seqs = [seq for seq in entries]
    seqs.sort(cmpk, reverse=options.reverse)

    writer = sequenceWriterGenerator(options)
    
    for seq in seqs:
        writer(seq)
