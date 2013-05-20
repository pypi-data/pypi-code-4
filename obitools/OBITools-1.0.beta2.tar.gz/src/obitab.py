#!/usr/local/bin/python
'''
:py:mod:`obitab`: converts a sequence file to a tabular file
============================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obitab` command converts sequence file to a tabular file that
can be open by a spreadsheet program or R.

'''

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption

def addTableOptions(optionManager):
    optionManager.add_option('-n','--na-string',
                             action="append", dest="NA",
                             metavar="<NOT AVAILABLE STRING>",
                             type="string",
                             default="NA",
                             help="String write in the table for not available value"
                            )
    optionManager.add_option('','--output-field-separator',
                             action="store", dest="ofs",
                             metavar="STRING",
                             type="string",
                             default="\t",
                             help="Field separator for CSV file"
                            )
    optionManager.add_option('-o','--output-seq',
                             action="store_true", dest="sequence",
                             default=False,
                             help="Add an extra column for sequence"
                            )
    optionManager.add_option('-d','--no-definition',
                             action="store_false", dest="definition",
                             default=True,
                             help="Remove column for sequence definition"
                            )
    optionManager.add_option('-a','--omit-attribute',
                             action="append", dest="omit",
                             metavar="<KEY>",
                             default=[],
                             help="Add attribute name to omit in the output tab"
                            )


def headerCmp(h1,h2):
    if type(h1) is str and type(h2) is str:
        return cmp(h1, h2)
    if type(h1) is str and type(h2) is tuple:
        return cmp(h1, h2[0])
    if type(h1) is tuple and type(h2) is str:
        return cmp(h1[0], h2)
    if type(h1) is tuple and type(h2) is tuple:
        c = cmp(h1[0],h2[0])
        if c==0:
            c = cmp(h1[1],h2[1])
        return c
    raise AssertionError
            
    

    

if __name__=='__main__':

    optionParser = getOptionManager([addTableOptions,addInOutputOption])
    
    (options, entries) = optionParser()

    column = {}
    subcol = {}
    db = []
    for seq in entries: 
        db.append(seq)
        keys = seq.keys()      
        for k in keys:
            t=type(seq[k])
            if k in column:
                column[k].add(t)
            else:
                column[k]=set([t])
            if t is dict:
                if k not in subcol:
                    subcol[k]=set()
                subcol[k]|=set(seq[k].keys())
                
    headers = set()
    for c in column:
        if len(column[c])==1:
            column[c]=column[c].pop()
        else:
            column[c]=str
            
        if column[c] not in (str,int,float,dict,bool):
            column[c]=str

            
        if column[c] is not dict:
            headers.add(c)
        else:
            for sc in subcol[c]:
                headers.add((c,sc))
                
    omit = set(options.omit)
    headers=list(headers)
    headers.sort(headerCmp)
    
    
    OFS = options.ofs
    
    s = "id"
    if options.definition:
        s = '%s%sdefinition'%(s,OFS)

    for k in headers:
        if type(k) is str:
            if k not in omit:
                s = '%s%s%s'%(s,OFS,k)
        else:
            if k[0] not in omit:
                if type(k[1]) is tuple:
                    sk = ":".join([str(x) for x in k[1]])
                else:
                    sk = str(k[1])
                if k[0][0:7]=='merged_':
                    s = '%s%s%s:%s' % (s,OFS,k[0][7:],sk)
                else:
                    s = '%s%s%s:%s' % (s,OFS,k[0],sk)
            
    if options.sequence:
        s = "%s%ssequence"%(s,OFS)
    print s
    
    
    for seq in db:
        s = seq.id
        
        if options.definition:
            s = '%s%s%s'%(s,OFS,seq.definition)
            
        for k in headers:
            if type(k) is str:
                if k not in omit:
                    if k in seq:
                        v = seq[k]
                        if v is None:
                            v=options.NA
                        s = '%s%s%s'%(s,OFS,v)
                    else:
                        s = '%s%s%s'%(s,OFS,options.NA)
            else:
                if k[0] not in omit:
                    if k[0] in seq:
                        sk = seq[k[0]]
                    else:
                        sk={}
                    if k[1] in sk:
                        v = sk[k[1]]
                        if v is None:
                            v=options.NA
                        s = '%s%s%s'%(s,OFS,v)
                    else:
                        if k[0][0:7]=='merged_':
                            s = '%s%s0'%(s,OFS)
                        else:
                            s = '%s%s%s'%(s,OFS,options.NA)
        if options.sequence:
            s = '%s%s%s'%(s,OFS,str(seq))
        
        print s
        
    
            
        
            
