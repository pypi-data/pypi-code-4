#!/usr/bin/env python
# -*- coding: utf-8 -*-


import itertools
import networkx as nx
import operator
import random

from copy import copy
from textwrap import dedent
from collections import defaultdict
from collections import namedtuple

from Bio.SeqFeature import ExactPosition
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import SeqFeature

from pydna import Dseq
from pydna import Dseqrecord
from pydna._simple_paths7 import all_circular_paths_edges
from pydna._simple_paths8 import all_simple_paths_edges
from findsubstrings_suffix_arrays_python import common_sub_strings
from findterminaloverlap_indexof_python import terminal_overlap


class Fragment(Dseqrecord):
    
    def __init__(self, record, start1    = 0,
                               end1      = 0,
                               start2    = 0,
                               end2      = 0,
                               alignment = 0, **kwargs):
        
        super(Fragment, self).__init__(record)
        
        self.start1             = start1
        self.end1               = end1
        self.left_overlap_size  = end1-start1
        self.start2             = start2
        self.end2               = end2
        self.right_overlap_size = end2-start2
        self.alignment          = alignment

    def __str__(self):
        return ("Fragment alignment {}\n").format(self.alignment)+super(Fragment,self).__str__()

class Contig(Dseqrecord):
    
    def __init__(self, record, source_fragments=[], processed_fragments=[], *args, **kwargs):        
        super(Contig, self).__init__(record)                
        self.source_fragments    = source_fragments        
        self.processed_fragments = processed_fragments        
        
    def detailed_fig(self):
        fig=""       
        for s in b.source_fragments:
            fig +="{}{}\n".format(" "*s.alignment, s.seq.tostring())        
        return fig
    
    def small_fig(self):

        if self.linear:
            '''
            frag20| 6
                   \/
                   /\
                    6|frag23| 6
                             \/
                             /\
                              6|frag14
            '''
            f = self.source_fragments[0]
            space2 = len(f.name)
            
            
            fig = ("{name}|{o2:>2}\n"
                   "{space2} \/\n"
                   "{space2} /\\\n").format(name = f.name,
                                            o2 = f.right_overlap_size,
                                            space2 = " "*space2)
            space = len(f.name)

            for f in self.source_fragments[1:-1]:        
                name= "{o1:>2}|{name}|".format(o1   = f.left_overlap_size,
                                               name = f.name)
                space2 = len(name)
                fig +=("{space} {name}{o2:>2}\n"
                       "{space} {space2}\/\n"
                       "{space} {space2}/\\\n").format( name = name,
                                                        o2 = f.right_overlap_size,
                                                        space = " "*space,
                                                        space2 = " "*space2)
                space +=space2 
            f = self.source_fragments[-1]
            fig += ("{space} {o1:>2}|{name}").format(name = f.name,
                                                    o1 = f.left_overlap_size,
                                                    space = " "*(space))
                
                
             
        else:
            '''
             -|2577|61
            |       \/
            |       /\
            |       61|5681|98
            |               \/
            |               /\
            |               98|2389|557
            |                       \/
            |                       /\
            |                       557-
            |                          |
             --------------------------
            '''
            f = self.source_fragments[0]        
            space = len(f.name)+3        
            fig =(" -|{name}|{o2:>2}\n"
                  "|{space}\/\n"
                  "|{space}/\\\n").format(name = f.name,
                                           o2 = f.right_overlap_size,
                                           space = " "*space)             
            for f in self.source_fragments[1:]:               
                name= "{o1:>2}|{name}|".format(o1 = f.left_overlap_size,
                                                      name = f.name)
                space2 = len(name)
                fig +=("|{space}{name}{o2:>2}\n"
                       "|{space}{space2}\/\n"
                       "|{space}{space2}/\\\n").format(o2 = f.right_overlap_size,
                                                       name = name,
                                                       space = " "*space,
                                                       space2 = " "*space2)
                space +=space2 
                                           
            fig +="|{space}{o1:>2}-\n".format(space=" "*(space), o1=self.source_fragments[0].left_overlap_size)    
            fig +="|{space}   |\n".format(space=" "*(space))    
            fig +=" {space}".format(space="-"*(space+3))             
        return dedent(fig)
    
    

    
    
    

class Assembly(object):
    '''Accepts a list of Dseqrecords and tries to assemble them into
    linear and circular assemblies based on shared regions of homology 
    with a minimum length given by limit.

    Parameters
    ----------

    dsrecs : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 25 nucleotides by default.

    Returns
    -------
    linear, circular: tuple
        Linear and circular are two lists containing linear 
        and circular assemblies.

        Each object in linear or circular is a named tuple with the following
        fields        

        +------------------+---------------------+----------------------------+ 
        | Field            | Type                | Contains                   | 
        +==================+=====================+============================+ 
        | result           | Dseqrecord          | Assembeled sequence        |
        +------------------+---------------------+----------------------------+ 
        | source_fragments | list of Dseqrecords | list of fragments          | 
        +------------------+---------------------+----------------------------+ 
        | sticky_fragments | list of Dseqrecords | list of processed fragments|
        |                  |                     | with a single stranded 5'  | 
        |                  |                     | cohesive end               |
        +------------------+---------------------+----------------------------+
        | source_alignments   | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each source       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+
        | sticky_alignments   | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each sticky       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+       
        | overlap_sizes    | list of integers    | list of the length of each |
        |                  |                     | overlap joining the        |   
        |                  |                     | sequences                  |
        +------------------+---------------------+----------------------------+        


        Source fragments are the double stranded blunt DNA fragments 
        originally added as the dsrecs argument. The parwise overlaps 
        found are added ar features to the source fragments.
        
        Sticky fragments are source fragments that have been processed 
        so that they can be ligated together by the homologous repair DNA
        machinery (single-strand annealing pathway). This involves trimming 
        DNA fragments so that the fragments are flanked by a 5' single stranded
        overhang.   
        
        Source_alignments is a list with the cumulative stagger between 
        each source fragment. Source alignments are different from sticky 
        alignments when the overlapping sequences are located in the interior
        of the fragments.

        ::
            
            Source fragments         
            ----------------
            
            
            cggcggcgggccTGCCTCtc                    \\
            gccgccgcccggACGGAGag                    | 
                                                    |
                      taTGCCTCaccattgcAAAAAAtt      |  source_fragments
            <-------->atACGGAGtggtaacgTTTTTTaa      |
                                                    | 
                                   aatAAAAAAcatcata | 
            <--------------------->ttaTTTTTTgtagtat /
            
            source_alignments = [10,23]
            
            
            Processed fragments         
            -------------------
            
                        <--6->        <--6->        overlap_sizes = [6,6]
                     
            cggcggcgggccTGCCTC                      \\
            gccgccgcccgg                             | 
                                                     |
                              accattgcAAAAAA         | sticky_fragments = [12,26]
            <---------->ACGGAGtggtaacg               |
                                                     | 
                                            catcata  | 
            <------------------------>TTTTTTgtagtat  /
                   sticky_alignments
                           
        

    '''

    def __init__(self, dsrecs):
        self.dsrecs    = dsrecs
        self.max_nodes = len(self.dsrecs)
        
        for dr in self.dsrecs:
            if dr.name in ("",".", "<unknown name>",None):
                dr.name = "frag{}".format(len(dr))
                
        self.analyzed_dsrecs   = []
        self.limit             = None
        self.no_of_olaps       = None
        self.protocol          = None
        self.circular_products = []
        self.linear_products   = []
                
    def __repr__(self):
        try:
            nodes = self.G.order()
        except AttributeError:
            nodes = "No graph"
        
        r = ( "Assembly object:\n"
              "Sequences........................: {number_of_seqs}\n"
              "Sequences with shared homologies.: {analyzed_dsrecs}\n"
              "Homology limit (bp)..............: {limit}\n"
              "Number of overlaps...............: {no_of_olaps}\n"
              "Nodes in graph...................: {nodes}\n"
              "Assembly protocol................: {pr}\n"
              "Circular products................: {cp}\n"
              "Linear product...................: {lp}" ).format(number_of_seqs  = len(self.dsrecs),
                                                                 analyzed_dsrecs = len(self.analyzed_dsrecs),
                                                                 limit           = self.limit,
                                                                 no_of_olaps     = self.no_of_olaps,
                                                                 nodes           = nodes,
                                                                 pr              = self.protocol,
                                                                 cp              = len(self.circular_products),
                                                                 lp              = len(self.linear_products))
        return r

    def _analyze_overlaps(self, algorithm):    
        cols = {}
        for dsrec in self.dsrecs:
            dsrec.features = [f for f in dsrec.features if f.type!="overlap"]
            dsrec.seq = dsrec.seq.fill_in()
        rcs = {dsrec:dsrec.rc() for dsrec in self.dsrecs}
        matches=[]
        dsset=set()

        for a, b in itertools.combinations(self.dsrecs, 2):
            match = algorithm( str(a.seq).upper(),
                               str(b.seq).upper(),
                               self.limit)
            if match:
                matches.append((a, b, match))
                dsset.add(a)
                dsset.add(b)                
            match = algorithm( str(a.seq).upper(),
                               str(rcs[b].seq).upper(),
                               self.limit)
            if match:
                matches.append((a, rcs[b], match))
                dsset.add(a)
                dsset.add(rcs[b])
                matches.append((rcs[a], b, [(len(a)-sa-le,len(b)-sb-le,le) for sa,sb,le in match]))
                dsset.add(b)
                dsset.add(rcs[a])
                
        self.no_of_olaps=0            
        
        for a, b, match in matches:
            for start_in_a, start_in_b, length in match:
                self.no_of_olaps+=1
                chksum = a[start_in_a:start_in_a+length].seguid()
                assert chksum == b[start_in_b:start_in_b+length].seguid()
                
                try:
                    fcol, revcol = cols[chksum]
                except KeyError:
                    fcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                    rcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                    cols[chksum] = fcol,rcol
                
                qual      = {"note"             : ["olp_{}".format(chksum)],
                             "chksum"           : [chksum],
                             "ApEinfo_fwdcolor" : [fcol],
                             "ApEinfo_revcolor" : [rcol]}
                
                if not chksum in [f.qualifiers["chksum"][0] for f in a.features if f.type == "overlap"]:            
                    a.features.append( SeqFeature( FeatureLocation(start_in_a,
                                                                   start_in_a + length),
                                                                   type = "overlap",
                                                                   qualifiers = qual))
                if not chksum in [f.qualifiers["chksum"][0] for f in b.features if f.type == "overlap"]:
                    b.features.append( SeqFeature( FeatureLocation(start_in_b,
                                                                   start_in_b + length),
                                                                   type = "overlap",
                                                                   qualifiers = qual))
        for ds in dsset:
            ds.features = sorted([f for f in ds.features], key = operator.attrgetter("location.start"))
            
        self.analyzed_dsrecs = list(dsset)
        return ( "{number_of_seqs} sequences analyzed\n"
                 "of which {analyzed_dsrecs} have shared homologies\n"
                 "with totally {no_of_olaps} overlaps" ).format( number_of_seqs  = len(self.dsrecs)*2,
                                                                 analyzed_dsrecs = len(self.analyzed_dsrecs),
                                                                 no_of_olaps = self.no_of_olaps)
    
    def create_graph(self):
        
        self.G=nx.MultiDiGraph(multiedges=True, name ="original graph" , selfloops=False)
        self.G.add_node( '5' )
        self.G.add_node( '3' )
        
        for dsrec in self.analyzed_dsrecs:
            overlaps = sorted( {f.qualifiers['chksum'][0]:f for f in dsrec.features 
                                if f.type=='overlap'}.values(),
                               key = operator.attrgetter('location.start'))          

            if overlaps:
                overlaps = ([SeqFeature(FeatureLocation(0,0),
                             type = 'overlap',
                             qualifiers = {'chksum':['5']})]+
                             overlaps+
                            [SeqFeature(FeatureLocation(len(dsrec),len(dsrec)),
                                        type = 'overlap',
                                        qualifiers = {'chksum':['3']})])
                
                for olp1, olp2 in itertools.combinations(overlaps, 2):
                    
                    n1 = olp1.qualifiers['chksum'][0]
                    n2 = olp2.qualifiers['chksum'][0]
                    
                    if n1 == '5' and n2=='3':
                        continue   
                    
                    s1,e1,s2,e2 = (olp1.location.start.position,
                                   olp1.location.end.position,
                                   olp2.location.start.position,
                                   olp2.location.end.position,)
                    
                    source_fragment = Fragment(dsrec,s1,e1,s2,e2)
                
                    processed_sek = dsrec[s1:e2]
                
                    processed_sek = Dseqrecord(Dseq(
                                    watson = processed_sek.seq.watson[e1-s1:],
                                    crick  = processed_sek.seq.crick[e2-s2:],
                                    ovhg   = e1-s1))
                    
                    processed_sek.name = "processedfrag"
                    
                    processed_fragment = Fragment(processed_sek,0,e1-s1,len(processed_sek)-(e2-s2), len(processed_sek))
                    
                    self.G.add_edge( n1, n2, 
                                     frag=source_fragment,
                                     proc_frag=processed_fragment,
                                     weight = s1-e1)
        return "A graph with 5', 3' and {nodes} internal nodes was created".format(nodes = self.G.order()-2)

    def analyze_overlaps(self, limit=25):
        self.limit = limit
        return self._analyze_overlaps(common_sub_strings)

    def analyze_terminal_overlaps(self, limit=25):
        self.limit = limit
        return self._analyze_overlaps(terminal_overlap)

    def _circ(self):        
        self.cG = self.G.copy()    
        self.cG.remove_nodes_from(('5','3'))
        circular_products=defaultdict(list)
        
        for path in all_circular_paths_edges(self.cG):
            
            pred_frag = copy(path[0][2]['frag'])
            pred_proc_frag = copy(path[0][2]['proc_frag'])  
            source_fragments = [pred_frag, ]
            processed_fragments = [pred_proc_frag, ]
                 
            if pred_frag.start2<pred_frag.end1:
                result=pred_frag[pred_frag.start2+(pred_frag.end1-pred_frag.start2):pred_frag.end2]
            else:
                result=pred_frag[pred_frag.end1:pred_frag.end2]            
            
            for first_node, second_node, edgedict in path[1:]:
                
                f  = copy(edgedict['frag'])
                pf = copy(edgedict['proc_frag'])
                
                f.alignment =  pred_frag.alignment + pred_frag.start2- f.start1
                source_fragments.append(f)
                
                pf.alignment = pred_proc_frag.alignment + pred_proc_frag.start2
                processed_fragments.append(pf)                

                if f.start2>f.end1:
                    result+=f[f.end1:f.end2]                    
                else:
                    result+=f[f.start2+(f.end1-f.start2):f.end2]
                
                pred_frag      = f
                pred_proc_frag = pf
                
            add=True
            
            for cp in circular_products[len(result)]:
                if (str(result.seq).lower() in str(cp.seq).lower()*2
                    or
                    str(result.seq).lower() == str(cp.seq.reverse_complement()).lower()*2):
                    add=False                
            if add:
                circular_products[len(result)].append( Contig( Dseqrecord(result,circular=True), source_fragments, processed_fragments) )

        return list(itertools.chain.from_iterable(circular_products[size] for size in sorted(circular_products, reverse=True)))
        
    def _lin(self):
        
        linear_products=defaultdict(list)    

        for path in all_simple_paths_edges(self.G, '5', '3', data=True, cutoff=self.max_nodes):
            
            pred_frag = copy(path[0][2].values().pop()['frag'])
            pred_proc_frag = copy(path[0][2].values().pop()['proc_frag'])         
            source_fragments = [pred_frag, ]
            processed_fragments = [pred_proc_frag, ]
            
            if pred_frag.start2<pred_frag.end1:
                result=pred_frag[pred_frag.start2+(pred_frag.end1-pred_frag.start2):pred_frag.end2]
            else:
                result=pred_frag[pred_frag.end1:pred_frag.end2]
            
            for first_node, second_node, edgedict in path[1:]:

                edgedict = edgedict.values().pop()
                
                f  = copy(edgedict['frag'])
                pf = copy(edgedict['proc_frag'])
                
                f.alignment =  pred_frag.alignment + pred_frag.start2- f.start1
                source_fragments.append(f)
                
                pf.alignment = pred_proc_frag.alignment + pred_proc_frag.start2
                processed_fragments.append(pf)
                
                if f.start2>f.end1:
                    result+=f[f.end1:f.end2]                    
                else:
                    result+=f[f.start2+(f.end1-f.start2):f.end2]
                
                pred_frag = f
                pred_proc_frag = pf

            add=True
            for lp in linear_products[len(result)]:
                if (str(result.seq).lower() == str(lp.seq).lower()
                    or
                    str(result.seq).lower() == str(lp.seq.reverse_complement()).lower()):
                    add=False
            for dsrec in self.dsrecs:
                if (str(result.seq).lower() == str(dsrec.seq).lower()
                    or
                    str(result.seq).lower() == str(dsrec.seq.reverse_complement()).lower()):
                    add=False
            if add:
                linear_products[len(result)].append(Contig( result, source_fragments, processed_fragments))
    
        return list(itertools.chain.from_iterable(linear_products[size] for size in sorted(linear_products, reverse=True)))
        

    def assemble_hr_circular(self):
        self.circular_products = self._circ()
        self.protocol = "homologous recombination, circular"
        return "{} circular products were formed".format(len(self.circular_products))
        
    def assemble_hr_linear(self):
        self.linear_products = self._lin()
        self.protocol = "homologous recombination, linear"
        return "{} linear products were formed".format(len(self.linear_products))
        
    def assemble_gibson_circular(self):
        self.circular_products = self._circ()
        self.protocol = "gibson assembly, circular"
        return "{} circular products were formed".format(len(self.circular_products))

    def assemble_gibson_linear(self):
        self.linear_products = self._lin()
        self.protocol = "gibson assembly, linear"
        return "{} linear products were formed".format(len(self.linear_products))

    def assemble_fusion_pcr_linear(self):
        self.linear_products = self._lin()
        self.protocol = "fusion PCR, linear"
        return "{} linear products were formed".format(len(self.linear_products))
        
    def assemble_slic(self):
        self.protocol = "slic, linear"
        pass
         
    def assemble_golden_gate(self):
        self.protocol = "golden_gate"
        pass
    


if __name__=="__main__":
    from pydna_helper import ape
    from pydna import Dseqrecord   
    from pydna import parse
    from pydna import eq    
    
    text5 = '''

    >2577
    tcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgacagagtcttttgtaacgaccccgtctccaccaacttggtatgcttgaaatctcaaggccattacacattcagttatgtgaacgaaaggtctttatttaacgtagcataaactaaataatacaggttccggttagcctgcaatgtgttaaatctaaaggagcatacccaaaatgaactgaagacaaggaaatttgcttgtccagatgtgattgagcatttgaacgttaataacataacatttttatacttaactatagaaagacttgtataaaaactggcaaacgagatattctgaatattggtgcatatttcaggtagaaaagcttacaaaacaatctaatcataatattgagatgaagagaaagataaaagaaaaaacgataagtcagatgagattatgattgtactttgaaatcgaggaacaaagtatatacggtagtagttccccgagttataacgggagatcatgtaaattgagaaaccagataaagatttggtatgcactctagcaagaaaataaaatgatgaatctatgatatagatcacttttgttccagcgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacgatcagatctttcaggaaagtttcggaggagatagtgttcggcagtttgtacatcatctgcgggatcaggtacggtttgatcaggttgtagaagatcaggtaagacatagaatcgatgtagatgatcggtttgtttttgttgatttttacgtaacagttcagttggaatttgttacgcagacccttaaccaggtattctacttcttcgaaagtgaaagactgggtgttcagtacgatcgatttgttggtagagtttttgttgtaatcccatttaccaccatcatccatgaaccagtatgccagagacatcggggtcaggtagttttcaaccaggttgttcgggatggtttttttgttgttaacgatgaacaggttagccagtttgttgaaagcttggtgtttgaaagtctgggcgccccaggtgattaccaggttacccaggtggttaacacgttcttttttgtgcggcggggacagtacccactgatcgtacagcagacatacgtggtccatgtatgctttgtttttccactcgaactgcatacagtaggttttaccttcatcacgagaacggatgtaagcatcacccaggatcagaccgatacctgcttcgaactgttcgatgttcagttcgatcagctgggatttgtattctttcagcagtttagagttcggacccaggttcattacctggttttttttgatgtttttcatatgcatggatccggggttttttctccttgacgttaaagtatagaggtatattaacaattttttgttgatacttttattacatttgaataagaagtaatacaaaccgaaaatgttgaaagtattagttaaagtggttatgcagtttttgcatttatatatctgttaatagatcaaaaatcatcgcttcgctgattaattaccccagaaataaggctaaaaaactaatcgcattatcatcctatggttgttaatttgattcgttcatttgaaggtttgtggggccaggttactgccaatttttcctcttcataaccataaaagctagtattgtagaatctttattgttcggagcagtgcggcgcgaggcacatctgcgtttcaggaacgcgaccggtgaagacgaggacgcacggaggagagtcttccttcggagggctgtcacccgctcggcggcttctaatccgtacttcaatatagcaatgagcagttaagcgtattactgaaagttccaaagagaaggtttttttaggctaagataatggggctctttacatttccacaacatataagtaagattagatatggatatgtatatggatatgtatatggtggtaatgccatgtaatatgattattaaacttctttgcgtccatccaacgagatctggcgcgccttaattaacccaacctgcattaatgaatcggccaacgcgcggattaccctgttatccctacatattgttgtgccatctgtgcagacaaacgcatcaggattcagtactgacaataaaaagattcttgttttcaagaacttgtcatttgtatagtttttttatattgtagttgttctattttaatcaaatgttagcgtgatttatattttttttcgcctcgacatcatctgcccagatgcgaagttaagtgcgcagaaagtaatatcatgcgtcaatcgtatgtgaatgctggtcgctatactgctgtcgattcgatactaacgccgccatccagtgtcgaaaacgagctcgaattcatcgatgatatcagatccactagtggcctatgcggccgcggatctgccggtctccctatagtgagtcgatccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacag

    >2389
    ctgtgaagtggctgaaatttcgtacaaaaaatttcgccaattgattcaggtaaatccggatgctggaacaaaagtgatctatatcatagattcatcattttattttcttgctagagtgcataccaaatctttatctggtttctcaatttacatgatctcccgttataactcggggaactactaccgtatatactttgttcctcgatttcaaagtacaatcataatctcatctgacttatcgttttttcttttatctttctcttcatctcaatattatgattagattgttttgtaagcttttctacctgaaatatgcaccaatattcagaatatctcgtttgccagtttttatacaagtctttctatagttaagtataaaaatgttatgttattaacgttcaaatgctcaatcacatctggacaagcaaatttccttgtcttcagttcattttgggtatgctcctttagatttaacacattgcaggctaaccggaacctgtattatttagtttatgctacgttaaataaagacctttcgttcacataactgaatgtgtaatggccttgagatttcaagcataccaagttggtggagacggggtcgttacaaaagactctatcctgatgcgtttgtctgcacagatggcactccgattaccctgttatccctacaagaatctttttattgtcagtactgattattcctttgccctcggacgagtgctggggcgtcggtttccactatcggcgagtacttctacacagccatcggtccagacggccgcgcttctgcgggcgatttgtgtacgcccgacagtcccggctccggatcggacgattgcgtcgcatcgaccctgcgcccaagctgcatcatcgaaattgccgtcaaccaagctctgatagagttggtcaagaccaatgcggagcatatacgcccggagccgcggcgatcctgcaagctccggatgcctccgctcgaagtagcgcgtctgctgctccatacaagccaaccacggcctccagaagaagatgttggcgacctcgtattgggaatccccgaacatcgcctcgctccagtcaatgaccgctgttatgcggccattgtccgtcaggacattgttggagccgaaatccgcgtgcacgaggtgccggacttcggggcagtcctcggcccaaagcatcagctcatcgagagcctgcgcgacggacgcactgacggtgtcgtccatcacagtttgccagtgatacacatggggatcagcaatcgcgcatatgaaatcacgccatgtagtgtattgaccgattccttgcggtccgaatgggccgaacccgctcgtctggctaagatcggccgcagcgatcgcatccatggcctccgcgaccggctgcagaacagcgggcagttcggtttcaggcaggtcttgcaacgtgacaccctgtgcacggcgggagatgcaataggtcaggctctcgctgaattccccaatgtcaagcacttccggaatcgggagcgcggccgatgcaaagtgccgataaacataacgatctttgtagaaaccatcggcgcagctatttacccgcaggacatatccacgccctcctacatcgaagctgaaagcacgagattcttcgccctccgagagctgcatcaggtcggagacgctgtcgaacttttcgatcagaaacttctcgacagacgtcgcggtgagttcaggctttttacccatggttgtttatgttcggatgtgatgtgattgggtcggctgcaggtcactagtgagaaagtgggcaacctggcgttcctcgacggttgtttatgttcggatgtgatgtgagaactgtatcctagcaagattttaaaaggaagtatatgaaagaagaacctcagtggcaaatcctaaccttttatatttctctacaggggcgcggcgtggggacaattcaacgcgtctgtgaggggagcgtttccctgctcgcaggtctgcagcgaggagccgtaatttttgcttcgcgccgtgcggccatcaaaatgtatggatgcaaatgattatacatggggatgtatgggctaaatgtacgggcgacagtcacatcatgcccctgagctgcgcacgtcaagactgtcaaggagggtattctgggcctccatgtcgctggccgggtgacccggcggggacaaggcaagctaaacagatctggcgcgccttaattaacccggggatccgtcgacctgcagcgtacgaagcttcagctggcggccgcgttctatagtgtcacctaaatcgtatgtggtcagcggccgcattgcacagactctgctgaatctggcaaaacaaccagacgctatgactcacccggacggcatgcaaatcaaaattacccgtcagga
    
    >5681
    atccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacaggcggttttcgcacgtacccatgcgctacgttcctggccctcttcaaacaggcccagttcgccaataaaatcaccctgattcagataggagaggatcatttctttaccctcttcgtctttgatcagcactgccacagagcctttaacgatgtagtacagcgtttccgctttttcaccctggtgaataagcgtgctcttggatgggtacttatgaatgtggcaatgagacaagaaccattcgagagtaggatccgtttgaggtttaccaagtaccataagatccttaaatttttattatctagctagatgataatattatatcaagaattgtacctgaaagcaaataaattttttatctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatatgcggtgtgaaataccgcacagatgcgtaaggagaaaataccgcatcaggcgctcttccgcttcctcgctcactgactcgctgcgctcggtcgttcggctgcggcgagcggtatcagctcactcaaaggcggtaatacggttatccacagaatcaggggataacgcaggaaagaacatgtgagcaaaaggccagcaaaagcccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctccgcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggtggcgaaacccgacaggactataaagataccaggcgtttccccctggaagctccctcgtgcgctctcctgttccgaccctgccgcttaccggatacctgtccgcctttctcccttcgggaagcgtggcgctttctcatagctcacgctgtaggtatctcagttcggtgtaggtcgttcgctccaagctgggctgtgtgcacgaaccccccgttcagcccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggtaagacacgacttatcgccactggcagcagccactggtaacaggattagcagagcgaggtatgtaggcggtgctacagagttcttgaagtggtggcctaactacggctacactagaaggacagtatttggtatctgcgctctgctgaagccagttaccttcggaaaaagagttggtagctcttgatccggcaaacaaaccaccgctggtagcggtggtttttttgtttgcaagcagcagattacgcgcagaaaaaaaggatctcaagaagatcctttgatcttttctacggggtctgacgctcagtggaacgaaaactcacgttaagggattttggtcatgaggggtaataactgatataattaaattgaagctctaatttgtgagtttagtatacatgcatttacttataatacagttttttagttttgctggccgcatcttctcaaatatgcttcccagcctgcttttctgtaacgttcaccctctaccttagcatcccttccctttgcaaatagtcctcttccaacaataataatgtcagatcctgtagagaccacatcatccacggttctatactgttgacccaatgcgtctcccttgtcatctaaacccacaccgggtgtcataatcaaccaatcgtaaccttcatctcttccacccatgtctctttgagcaataaagccgataacaaaatctttgtcgctcttcgcaatgtcaacagtacccttagtatattctccagtagatagggagcccttgcatgacaattctgctaacatcaaaaggcctctaggttcctttgttacttcttctgccgcctgcttcaaaccgctaacaatacctgggcccaccacaccgtgtgcattcgtaatgtctgcccattctgctattctgtatacacccgcagagtactgcaatttgactgtattaccaatgtcagcaaattttctgtcttcgaagagtaaaaaattgtacttggcggataatgcctttagcggcttaactgtgccctccatggaaaaatcagtcaaaatatccacatgtgtttttagtaaacaaattttgggacctaatgcttcaactaactccagtaattccttggtggtacgaacatccaatgaagcacacaagtttgtttgcttttcgtgcatgatattaaatagcttggcagcaacaggactaggatgagtagcagcacgttccttatatgtagctttcgacatgatttatcttcgtttcctgcaggtttttgttctgtgcagttgggttaagaatactgggcaatttcatgtttcttcaacactacatatgcgtatatataccaatctaagtctgtgctccttccttcgttcttccttctgttcggagattaccgaatcaaaaaaatttcaaagaaaccgaaatcaaaaaaaagaataaaaaaaaaatgatgaattgaattgaaaagctagcttatcgatgataagctgtcaaagatgagaattaattccacggactatagactatactagatactccgtctactgtacgatacacttccgctcaggtccttgtcctttaacgaggccttaccactcttttgttactctattgatccagctcagcaaaggcagtgtgatctaagattctatcttcgcgatgtagtaaaactagctagaccgagaaagagactagaaatgcaaaaggcacttctacaatggctgccatcattattatccgatgtgacgctgcagcttctcaatgatattcgaatacgctttgaggagatacagcctaatatccgacaaactgttttacagatttacgatcgtacttgttacccatcattgaattttgaacatccgaacctgggagttttccctgaaacagatagtatatttgaacctgtataataatatatagtctagcgctttacggaagacaatgtatgtatttcggttcctggagaaactattgcatctattgcataggtaatcttgcacgtcgcatccccggttcattttctgcgtttccatcttgcacttcaatagcatatctttgttaacgaagcatctgtgcttcattttgtagaacaaaaatgcaacgcgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgaaagcgctattttaccaacgaagaatctgtgcttcatttttgtaaaacaaaaatgcaacgcgacgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgagagcgctattttaccaacaaagaatctatacttcttttttgttctacaaaaatgcatcccgagagcgctatttttctaacaaagcatcttagattactttttttctcctttgtgcgctctataatgcagtctcttgataactttttgcactgtaggtccgttaaggttagaagaaggctactttggtgtctattttctcttccataaaaaaagcctgactccacttcccgcgtttactgattactagcgaagctgcgggtgcattttttcaagataaaggcatccccgattatattctataccgatgtggattgcgcatactttgtgaacagaaagtgatagcgttgatgattcttcattggtcagaaaattatgaacggtttcttctattttgtctctatatactacgtataggaaatgtttacattttcgtattgttttcgattcactctatgaatagttcttactacaatttttttgtctaaagagtaatactagagataaacataaaaaatgtagaggtcgagtttagatgcaagttcaaggagcgaaaggtggatgggtaggttatatagggatatagcacagagatatatagcaaagagatacttttgagcaatgtttgtggaagcggtattcgcaatgggaagctccaccccggttgataatcagaaaagccccaaaaacaggaagattattatcaaaaaggatcttcacctagatccttttaaattaaaaatgaagttttaaatcaatctaaagtatatatgagtaaacttggtctgacagttaccaatgcttaatcagtgaggcacctatctcagcgatctgtctatttcgttcatccatagttgcctgactccccgtcgtgtagataactacgatacgggagcgcttaccatctggccccagtgctgcaatgataccgcgagacccacgctcaccggctccagatttatcagcaataaaccagccagccggaagggccgagcgcagaagtggtcctgcaactttatccgcctccatccagtctattaattgttgccgggaagctagagtaagtagttcgccagttaatagtttgcgcaacgttgttggcattgctacaggcatcgtggtgtcactctcgtcgtttggtatggcttcattcagctccggttcccaacgatcaaggcgagttacatgatcccccatgttgtgcaaaaaagcggttagctccttcggtcctccgatcgttgtcagaagtaagttggccgcagtgttatcactcatggttatggcagcactgcataattctcttactgtcatgccatccgtaagatgcttttctgtgactggtgagtactcaaccaagtcattctgagaatagtgtatgcggcgaccgagttgctcttgcccggcgtcaatacgggataatagtgtatcacatagcagaactttaaaagtgctcatcattggaaaacgttcttcggggcgaaaactctcaaggatcttaccgctgttgagatccagttcgatgtaacccactcgtgcacccaactgatcttcagcatcttttactttcaccagcgtttctgggtgagcaaaaacaggaaggcaaaatgccgcaaaaaagggaataagggcgacacggaaatgttgaatactcatactcttcctttttcaatattattgaagcatttatcagggttattgtctcatgagcggatacatatttgaatgtatttagaaaaataaacaaataggggttccgcgcacatttccccgaaaagtgccacctgctaagaaaccattattatcatgacattaacctataaaaataggcgtatcacgaggccctttcgtctcgcgcgtttcggtgatgacggtgaaaacctctgacacatgcagctcccggagacggtcacagcttgtctgtaagcggatgccgggagcagacaagcccgtcagggcgcgtcagcgggtgttggcgggtgtcggggctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatagatcctgaggatcggggtgataaatcagtctgcgccacatcgggggaaacaaaatggcgcgagatctaaaaaaaaaggctccaaaaggagcctttcgcgctaccaggtaacgcgccactccgacgggattaacgagtgccgtaaacgacgatggttttaccgtgtgcggagatcaggttctgatcctcgagcatcttaagaattcgtcccacggtttgtctagagcagccgacaatctggccaatttcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgac
    
    '''
    
    x,y,z = parse(text5)
    print len(x),len(y),len(z) 
    a = Assembly([z,y,x])
    #a = Assembly([x,y,z])
    print a.analyze_overlaps(limit=60)
    print a.create_graph()
    print a.assemble_hr_circular()    
    
    
    
#    for sk in a.analyzed_dsrecs:
#        ape(sk)
#        import time;time.sleep(0.5)
    
    
    correct = 'tcgcgcgtttcggtgatgacggtgaaaacctctgacacatgcagctcccggagacggtcacagcttgtctgtaagcggatgccgggagcagacaagcccgtcagggcgcgtcagcgggtgttggcgggtgtcggggctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatagatcctgaggatcggggtgataaatcagtctgcgccacatcgggggaaacaaaatggcgcgagatctaaaaaaaaaggctccaaaaggagcctttcgcgctaccaggtaacgcgccactccgacgggattaacgagtgccgtaaacgacgatggttttaccgtgtgcggagatcaggttctgatcctcgagcatcttaagaattcgtcccacggtttgtctagagcagccgacaatctggccaatttcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgaccacatacgatttaggtgacactatagaacgcggccgccagctgaagcttcgtacgctgcaggtcgacggatccccgggttaattaaggcgcgccagatctgtttagcttgccttgtccccgccgggtcacccggccagcgacatggaggcccagaataccctccttgacagtcttgacgtgcgcagctcaggggcatgatgtgactgtcgcccgtacatttagcccatacatccccatgtataatcatttgcatccatacattttgatggccgcacggcgcgaagcaaaaattacggctcctcgctgcagacctgcgagcagggaaacgctcccctcacagacgcgttgaattgtccccacgccgcgcccctgtagagaaatataaaaggttaggatttgccactgaggttcttctttcatatacttccttttaaaatcttgctaggatacagttctcacatcacatccgaacataaacaaccgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacccaatcacatcacatccgaacataaacaaccatgggtaaaaagcctgaactcaccgcgacgtctgtcgagaagtttctgatcgaaaagttcgacagcgtctccgacctgatgcagctctcggagggcgaagaatctcgtgctttcagcttcgatgtaggagggcgtggatatgtcctgcgggtaaatagctgcgccgatggtttctacaaagatcgttatgtttatcggcactttgcatcggccgcgctcccgattccggaagtgcttgacattggggaattcagcgagagcctgacctattgcatctcccgccgtgcacagggtgtcacgttgcaagacctgcctgaaaccgaactgcccgctgttctgcagccggtcgcggaggccatggatgcgatcgctgcggccgatcttagccagacgagcgggttcggcccattcggaccgcaaggaatcggtcaatacactacatggcgtgatttcatatgcgcgattgctgatccccatgtgtatcactggcaaactgtgatggacgacaccgtcagtgcgtccgtcgcgcaggctctcgatgagctgatgctttgggccgaggactgccccgaagtccggcacctcgtgcacgcggatttcggctccaacaatgtcctgacggacaatggccgcataacagcggtcattgactggagcgaggcgatgttcggggattcccaatacgaggtcgccaacatcttcttctggaggccgtggttggcttgtatggagcagcagacgcgctacttcgagcggaggcatccggagcttgcaggatcgccgcggctccgggcgtatatgctccgcattggtcttgaccaactctatcagagcttggttgacggcaatttcgatgatgcagcttgggcgcagggtcgatgcgacgcaatcgtccgatccggagccgggactgtcgggcgtacacaaatcgcccgcagaagcgcggccgtctggaccgatggctgtgtagaagtactcgccgatagtggaaaccgacgccccagcactcgtccgagggcaaaggaataatcagtactgacaataaaaagattcttgtagggataacagggtaatcggagtgccatctgtgcagacaaacgcatcaggatagagtcttttgtaacgaccccgtctccaccaacttggtatgcttgaaatctcaaggccattacacattcagttatgtgaacgaaaggtctttatttaacgtagcataaactaaataatacaggttccggttagcctgcaatgtgttaaatctaaaggagcatacccaaaatgaactgaagacaaggaaatttgcttgtccagatgtgattgagcatttgaacgttaataacataacatttttatacttaactatagaaagacttgtataaaaactggcaaacgagatattctgaatattggtgcatatttcaggtagaaaagcttacaaaacaatctaatcataatattgagatgaagagaaagataaaagaaaaaacgataagtcagatgagattatgattgtactttgaaatcgaggaacaaagtatatacggtagtagttccccgagttataacgggagatcatgtaaattgagaaaccagataaagatttggtatgcactctagcaagaaaataaaatgatgaatctatgatatagatcacttttgttccagcgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacgatcagatctttcaggaaagtttcggaggagatagtgttcggcagtttgtacatcatctgcgggatcaggtacggtttgatcaggttgtagaagatcaggtaagacatagaatcgatgtagatgatcggtttgtttttgttgatttttacgtaacagttcagttggaatttgttacgcagacccttaaccaggtattctacttcttcgaaagtgaaagactgggtgttcagtacgatcgatttgttggtagagtttttgttgtaatcccatttaccaccatcatccatgaaccagtatgccagagacatcggggtcaggtagttttcaaccaggttgttcgggatggtttttttgttgttaacgatgaacaggttagccagtttgttgaaagcttggtgtttgaaagtctgggcgccccaggtgattaccaggttacccaggtggttaacacgttcttttttgtgcggcggggacagtacccactgatcgtacagcagacatacgtggtccatgtatgctttgtttttccactcgaactgcatacagtaggttttaccttcatcacgagaacggatgtaagcatcacccaggatcagaccgatacctgcttcgaactgttcgatgttcagttcgatcagctgggatttgtattctttcagcagtttagagttcggacccaggttcattacctggttttttttgatgtttttcatatgcatggatccggggttttttctccttgacgttaaagtatagaggtatattaacaattttttgttgatacttttattacatttgaataagaagtaatacaaaccgaaaatgttgaaagtattagttaaagtggttatgcagtttttgcatttatatatctgttaatagatcaaaaatcatcgcttcgctgattaattaccccagaaataaggctaaaaaactaatcgcattatcatcctatggttgttaatttgattcgttcatttgaaggtttgtggggccaggttactgccaatttttcctcttcataaccataaaagctagtattgtagaatctttattgttcggagcagtgcggcgcgaggcacatctgcgtttcaggaacgcgaccggtgaagacgaggacgcacggaggagagtcttccttcggagggctgtcacccgctcggcggcttctaatccgtacttcaatatagcaatgagcagttaagcgtattactgaaagttccaaagagaaggtttttttaggctaagataatggggctctttacatttccacaacatataagtaagattagatatggatatgtatatggatatgtatatggtggtaatgccatgtaatatgattattaaacttctttgcgtccatccaacgagatctggcgcgccttaattaacccaacctgcattaatgaatcggccaacgcgcggattaccctgttatccctacatattgttgtgccatctgtgcagacaaacgcatcaggattcagtactgacaataaaaagattcttgttttcaagaacttgtcatttgtatagtttttttatattgtagttgttctattttaatcaaatgttagcgtgatttatattttttttcgcctcgacatcatctgcccagatgcgaagttaagtgcgcagaaagtaatatcatgcgtcaatcgtatgtgaatgctggtcgctatactgctgtcgattcgatactaacgccgccatccagtgtcgaaaacgagctcgaattcatcgatgatatcagatccactagtggcctatgcggccgcggatctgccggtctccctatagtgagtcgatccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacaggcggttttcgcacgtacccatgcgctacgttcctggccctcttcaaacaggcccagttcgccaataaaatcaccctgattcagataggagaggatcatttctttaccctcttcgtctttgatcagcactgccacagagcctttaacgatgtagtacagcgtttccgctttttcaccctggtgaataagcgtgctcttggatgggtacttatgaatgtggcaatgagacaagaaccattcgagagtaggatccgtttgaggtttaccaagtaccataagatccttaaatttttattatctagctagatgataatattatatcaagaattgtacctgaaagcaaataaattttttatctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatatgcggtgtgaaataccgcacagatgcgtaaggagaaaataccgcatcaggcgctcttccgcttcctcgctcactgactcgctgcgctcggtcgttcggctgcggcgagcggtatcagctcactcaaaggcggtaatacggttatccacagaatcaggggataacgcaggaaagaacatgtgagcaaaaggccagcaaaagcccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctccgcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggtggcgaaacccgacaggactataaagataccaggcgtttccccctggaagctccctcgtgcgctctcctgttccgaccctgccgcttaccggatacctgtccgcctttctcccttcgggaagcgtggcgctttctcatagctcacgctgtaggtatctcagttcggtgtaggtcgttcgctccaagctgggctgtgtgcacgaaccccccgttcagcccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggtaagacacgacttatcgccactggcagcagccactggtaacaggattagcagagcgaggtatgtaggcggtgctacagagttcttgaagtggtggcctaactacggctacactagaaggacagtatttggtatctgcgctctgctgaagccagttaccttcggaaaaagagttggtagctcttgatccggcaaacaaaccaccgctggtagcggtggtttttttgtttgcaagcagcagattacgcgcagaaaaaaaggatctcaagaagatcctttgatcttttctacggggtctgacgctcagtggaacgaaaactcacgttaagggattttggtcatgaggggtaataactgatataattaaattgaagctctaatttgtgagtttagtatacatgcatttacttataatacagttttttagttttgctggccgcatcttctcaaatatgcttcccagcctgcttttctgtaacgttcaccctctaccttagcatcccttccctttgcaaatagtcctcttccaacaataataatgtcagatcctgtagagaccacatcatccacggttctatactgttgacccaatgcgtctcccttgtcatctaaacccacaccgggtgtcataatcaaccaatcgtaaccttcatctcttccacccatgtctctttgagcaataaagccgataacaaaatctttgtcgctcttcgcaatgtcaacagtacccttagtatattctccagtagatagggagcccttgcatgacaattctgctaacatcaaaaggcctctaggttcctttgttacttcttctgccgcctgcttcaaaccgctaacaatacctgggcccaccacaccgtgtgcattcgtaatgtctgcccattctgctattctgtatacacccgcagagtactgcaatttgactgtattaccaatgtcagcaaattttctgtcttcgaagagtaaaaaattgtacttggcggataatgcctttagcggcttaactgtgccctccatggaaaaatcagtcaaaatatccacatgtgtttttagtaaacaaattttgggacctaatgcttcaactaactccagtaattccttggtggtacgaacatccaatgaagcacacaagtttgtttgcttttcgtgcatgatattaaatagcttggcagcaacaggactaggatgagtagcagcacgttccttatatgtagctttcgacatgatttatcttcgtttcctgcaggtttttgttctgtgcagttgggttaagaatactgggcaatttcatgtttcttcaacactacatatgcgtatatataccaatctaagtctgtgctccttccttcgttcttccttctgttcggagattaccgaatcaaaaaaatttcaaagaaaccgaaatcaaaaaaaagaataaaaaaaaaatgatgaattgaattgaaaagctagcttatcgatgataagctgtcaaagatgagaattaattccacggactatagactatactagatactccgtctactgtacgatacacttccgctcaggtccttgtcctttaacgaggccttaccactcttttgttactctattgatccagctcagcaaaggcagtgtgatctaagattctatcttcgcgatgtagtaaaactagctagaccgagaaagagactagaaatgcaaaaggcacttctacaatggctgccatcattattatccgatgtgacgctgcagcttctcaatgatattcgaatacgctttgaggagatacagcctaatatccgacaaactgttttacagatttacgatcgtacttgttacccatcattgaattttgaacatccgaacctgggagttttccctgaaacagatagtatatttgaacctgtataataatatatagtctagcgctttacggaagacaatgtatgtatttcggttcctggagaaactattgcatctattgcataggtaatcttgcacgtcgcatccccggttcattttctgcgtttccatcttgcacttcaatagcatatctttgttaacgaagcatctgtgcttcattttgtagaacaaaaatgcaacgcgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgaaagcgctattttaccaacgaagaatctgtgcttcatttttgtaaaacaaaaatgcaacgcgacgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgagagcgctattttaccaacaaagaatctatacttcttttttgttctacaaaaatgcatcccgagagcgctatttttctaacaaagcatcttagattactttttttctcctttgtgcgctctataatgcagtctcttgataactttttgcactgtaggtccgttaaggttagaagaaggctactttggtgtctattttctcttccataaaaaaagcctgactccacttcccgcgtttactgattactagcgaagctgcgggtgcattttttcaagataaaggcatccccgattatattctataccgatgtggattgcgcatactttgtgaacagaaagtgatagcgttgatgattcttcattggtcagaaaattatgaacggtttcttctattttgtctctatatactacgtataggaaatgtttacattttcgtattgttttcgattcactctatgaatagttcttactacaatttttttgtctaaagagtaatactagagataaacataaaaaatgtagaggtcgagtttagatgcaagttcaaggagcgaaaggtggatgggtaggttatatagggatatagcacagagatatatagcaaagagatacttttgagcaatgtttgtggaagcggtattcgcaatgggaagctccaccccggttgataatcagaaaagccccaaaaacaggaagattattatcaaaaaggatcttcacctagatccttttaaattaaaaatgaagttttaaatcaatctaaagtatatatgagtaaacttggtctgacagttaccaatgcttaatcagtgaggcacctatctcagcgatctgtctatttcgttcatccatagttgcctgactccccgtcgtgtagataactacgatacgggagcgcttaccatctggccccagtgctgcaatgataccgcgagacccacgctcaccggctccagatttatcagcaataaaccagccagccggaagggccgagcgcagaagtggtcctgcaactttatccgcctccatccagtctattaattgttgccgggaagctagagtaagtagttcgccagttaatagtttgcgcaacgttgttggcattgctacaggcatcgtggtgtcactctcgtcgtttggtatggcttcattcagctccggttcccaacgatcaaggcgagttacatgatcccccatgttgtgcaaaaaagcggttagctccttcggtcctccgatcgttgtcagaagtaagttggccgcagtgttatcactcatggttatggcagcactgcataattctcttactgtcatgccatccgtaagatgcttttctgtgactggtgagtactcaaccaagtcattctgagaatagtgtatgcggcgaccgagttgctcttgcccggcgtcaatacgggataatagtgtatcacatagcagaactttaaaagtgctcatcattggaaaacgttcttcggggcgaaaactctcaaggatcttaccgctgttgagatccagttcgatgtaacccactcgtgcacccaactgatcttcagcatcttttactttcaccagcgtttctgggtgagcaaaaacaggaaggcaaaatgccgcaaaaaagggaataagggcgacacggaaatgttgaatactcatactcttcctttttcaatattattgaagcatttatcagggttattgtctcatgagcggatacatatttgaatgtatttagaaaaataaacaaataggggttccgcgcacatttccccgaaaagtgccacctgctaagaaaccattattatcatgacattaacctataaaaataggcgtatcacgaggccctttcgtc'

    print eq(correct,a.circular_products[0], circular=True)
    
