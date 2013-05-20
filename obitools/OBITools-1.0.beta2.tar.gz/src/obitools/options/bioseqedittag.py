import sys
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
import math

def addSequenceEditTagOptions(optionManager):
    
    group = optionManager.add_option_group('Sequences and attributes editing options')
    
    group.add_option('--rank',
                             action="store_true", dest='addrank',
                             default=False,
                             help="add a rank attribute to the sequence "
                                  "indicating the sequence position in the input data")

    group.add_option('-R','--rename-tag',
                             action="append", 
                             dest='renameTags',
                             metavar="<OLD_NAME:NEW_NAME>",
                             type="string",
                             default=[],
                             help="change tag name from OLD_NAME to NEW_NAME")

    group.add_option('--delete-tag',
                             action="append", 
                             dest='deleteTags',
                             metavar="<TAG_NAME>",
                             type="string",
                             default=[],
                             help="delete tag TAG_NAME")

    group.add_option('-S','--set-tag',
                             action="append", 
                             dest='setTags',
                             metavar="<TAG_NAME:PYTHON_EXPRESSION>",
                             type="string",
                             default=[],
                             help="Add a new tag named TAG_NAME with "
                                  "a value computed from PYTHON_EXPRESSION")

    group.add_option('--tag-list',
                             action="store", 
                             dest='taglist',
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="Indicate a file containing tag and values "
                                  "to modify on specified sequences")

    group.add_option('--set-identifier',
                             action="store", 
                             dest='setIdentifier',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence identifier with "
                                  "a value computed from PYTHON_EXPRESSION")

    group.add_option('--run',
                             action="store", 
                             dest='run',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Run a python expression on each selected sequence")

    group.add_option('--set-sequence',
                             action="store", 
                             dest='setSequence',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Change the sequence itself with "
                                  "a value computed from PYTHON_EXPRESSION")

    group.add_option('-T','--set-definition',
                             action="store", 
                             dest='setDefinition',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence definition with "
                                  "a value computed from PYTHON_EXPRESSION")
    
    group.add_option('-O','--only-valid-python',
                             action="store_true", 
                             dest='onlyValid',
                             default=False,
                             help="only valid python expressions are allowed")
    
    group.add_option('-C','--clear',
                             action="store_true", 
                             dest='clear',
                             default=False,
                             help="clear all tags associated to the sequences")
    
    group.add_option('-k','--keep',
                             action='append',
                             dest='keep',
                             default=[],
                             type="string",
                             help="only keep this tag")
    
    group.add_option('--length',
                             action="store_true", 
                             dest='length',
                             default=False,
                             help="add seqLength tag with sequence length")
    
    group.add_option('--with-taxon-at-rank',
                             action='append',
                             dest='taxonrank',
                             default=[],
                             type="string",
                             help="add taxonomy annotation at a speciefied rank level")
    
    group.add_option('-m','--mcl',
                             action="store", dest="mcl",
                             metavar="<mclfile>",
                             type="string",
                             default=None,
                             help="split following mcl graph clustering partition")
    
    group.add_option('--uniq-id',
                             action="store_true", dest="uniqids",
                             default=False,
                             help="force sequence ids to be uniq")
    

def readMCLFile(file):
    partition=1
    parts = {}
    for l in file:
        for seq in l.strip().split():
            parts[seq]=partition
        partition+=1
    return parts
        
def readTagFile(f):
    tags = {}
    
    for l in f:
        ident,tag,value = l.split(None,2)
        value=value.strip()
        d = tags.get(ident,[])
        try:
            value = eval(value)
        except Exception:
            pass
        d.append((tag,value))
        tags[ident]=d
        
    return tags


def sequenceTaggerGenerator(options):
    toDelete = options.deleteTags[:]
    toRename = [x.split(':',1) for x in options.renameTags if len(x.split(':',1))==2]
    toSet    = [x.split(':',1) for x in options.setTags if len(x.split(':',1))==2]
    newId    = options.setIdentifier
    newDef   = options.setDefinition
    newSeq   = options.setSequence
    clear    = options.clear
    keep     = set(options.keep)
    length   = options.length
    run      = options.run
    uniqids  = options.uniqids
    counter  = [0]
    loadTaxonomyDatabase(options)
    if options.taxonomy is not None:
        annoteRank=options.taxonrank
    else:
        annoteRank=[]

    if options.mcl is not None:
        parts = readMCLFile(open(options.mcl))
    else:
        parts = False
    
    if options.taglist is not None:
        tags = readTagFile(open(options.taglist))
    else:
        tags = False
        
    if uniqids:
        idlist = {}
    
    def sequenceTagger(seq):
        
        if counter[0]>=0:
            counter[0]+=1
        
        if clear or keep:
            ks = seq.keys()
            for k in ks:
                if k not in keep:
                    del seq[k]
        else:
            for i in toDelete:
                if i in seq:
                    del seq[i]                
            for o,n in toRename:
                if o in seq:
                    seq[n]=seq[o]
                    del seq[o]
                    
        for rank in annoteRank:
            if 'taxid' in seq:
                taxid = seq['taxid']
                if taxid is not None:
                    rtaxid = options.taxonomy.getTaxonAtRank(taxid,rank)
                    if rtaxid is not None:
                        scn = options.taxonomy.getScientificName(rtaxid)
                    else:
                        scn=None
                    seq[rank]=rtaxid
                    seq["%s_name"%rank]=scn 
                    
        if parts and seq.id in parts:   
            seq['cluster']=parts[seq.id]
            
        if tags and seq.id in tags: 
            for t,v in tags[seq.id]:
                seq[t]=v
            
        if options.addrank:
            seq['seq_rank']=counter[0]

        for i,v in toSet:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(v,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = v
            seq[i]=val
            
        if length:
            seq['seq_length']=len(seq)
            
        if newId is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newId,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newId
            seq.id=val
        if newDef is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newDef,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newDef
            seq.definition=val
            
        if newSeq is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newSeq,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newSeq
            if hasattr(seq, '_seq'):
                seq._seq=str(val).lower()
                if 'seq_length' in seq:
                    seq['seq_length']=len(seq)
                    
        if run is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(run,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
            
        if uniqids:
            n = idlist.get(seq.id,0)
            if (n > 0):
                newid = seq.id
                while (n > 0):
                    old = newid
                    newid = "%s.%d" % (old,n)
                    n = idlist.get(newid,0)
                idlist[old]+=1
                seq.id=newid
            idlist[seq.id]=1
                
                
            
        return seq
    
    return sequenceTagger