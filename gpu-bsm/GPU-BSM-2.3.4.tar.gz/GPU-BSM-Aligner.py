
# This file is part of GPU-BSM.

# GPU-BSM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# GPU-BSM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GPU-BSM.  If not, see <http://www.gnu.org/licenses/>.


# GPU-BSM is a GPU based program to map bisulfite treated reads
# rel. 2.3.4 2013-09-09
#
# contact andrea.manconi@itb.cnr.it

import ntpath
import fileinput
import string
import os
import time 
import shelve
import subprocess
import random
import math
import logging
import sys
import pickle
from subprocess import Popen
from utilities import *



def parse_cigar(cigar):
    '''
    to calculate the overall indels
    '''
    cigar_op = 'MIDNSHP=X'
    p_cigar_op = dict([(j, cigar[j]) for j in range(len(cigar)) if cigar[j] in cigar_op])

    operators = {'M': list(), 'I': list(), 'D': list()}
    i = 0
    for j in sorted(p_cigar_op.iterkeys()):
        slice_size = int(cigar[i:j])
        i = j+1
        if p_cigar_op[j]=='I': operators['I'].append(slice_size)
        elif p_cigar_op[j]=='D': operators['D'].append(slice_size)
        else: operators['M'].append(slice_size)
    return operators

def alignment_score(cigar, edit_distance):
    '''
    Calculate the alignment score
    '''

    # MatchScore defines the score for match
    MatchScore=1
    # MismatchScore defines the score for mismatch
    MismatchScore=-2
    # GapOpenScore defines the score for opening a gap
    GapOpenScore=-3
    # GapExtendScore defines the score for extending a gap
    GapExtendScore=-1

    operators = parse_cigar(cigar)
    gaps_penalty = 0; mismatches_penalty = 0; matches_score = 0
    nb_of_gaps = 0; nb_of_mismatches = 0; nb_of_matches = 0

    seq_size = 0
    for op in ['I', 'D']:
        for gap in operators[op]:
            seq_size+=gap*(op=='I')
            nb_of_gaps+=gap
            gaps_penalty += GapOpenScore + (gap>1)*(gap-1)*GapExtendScore

    for item in operators['M']: seq_size+=item
    
    nb_of_mismatches = edit_distance - nb_of_gaps
    nb_of_matches = seq_size - edit_distance

    mismatches_penalty = nb_of_mismatches*MismatchScore
    matches_score = nb_of_matches*MatchScore

    return matches_score + mismatches_penalty + gaps_penalty



def get_alignments(fname, m, strand):
    '''
    Get alignments performed by SOAP3-dp
    '''

    edit_distances = {} # mismatches and indels
    positions = {}
    fname+='.out'
    started_alignments = False 
    for line in fileinput.input(fname):
        if not line.startswith('@'): started_alignments=True
        if started_alignments:
            data=line.split()
            if data[2]!='*': # the read has been aligned
		if not edit_distances.has_key(data[0]): edit_distances[data[0]]=dict(zip(range(m+1), (m+1)*[0]))
                ed = int(data[12].split(':')[-1]) # NM field in the SAM file: the edit distance (mismatches, indels and ambiguous bases)
                #ed = int(data[-7].split(':')[-1]) # NM field in the SAM file: the edit distance (mismatches, indels and ambiguous bases)
                if not edit_distances[data[0]].has_key(ed): edit_distances[data[0]][ed]=0
                edit_distances[data[0]][ed]+=1
                if not positions.has_key(data[0]): positions[data[0]]=list()
                cigar = data[5]
                score = alignment_score(cigar, ed)
                strand_fa = {'0':'+', '1':'-'}[bin(int(data[1]))[2]] # bit 0x10
                positions[data[0]].append({'seq_id': data[2], 'position': int(data[3]), 'strand_fa':strand_fa, 'ed':ed, 'strand': strand, 'cigar': cigar, 'score': score})
    fileinput.close()
    return edit_distances, positions

def remove_multi_best_score(edit_distances, alignments):
    '''
    Remove those reads with at least two best score alignments
    '''
    for read in alignments.keys():
        scores = [alignment['score'] for alignment in alignments[read]]
        best_score = max(scores)
        if scores.count(best_score)>1:
            del(edit_distances[read]); del(alignments[read])
        else: # no best alignments are discarded
            alignments[read]=[alignments[read][scores.index(best_score)]]
    return

def converted_reads_files(reads_file, reads_file1, reads_file2, library, single_end):
    '''
    Create the files where to store the converted reads
    '''
    if single_end: # single-end alignment
        head, tail = ntpath.split(reads_file)
        fileName, fileExtension = os.path.splitext(tail)

        FW_C2T_fname = out_path+'/'+'FW_C2T'+fileExtension+'.tmp'
        RC_G2A_fname = out_path+'/'+'RC_G2A'+fileExtension+'.tmp'
        reads_fnames = {'FW_C2T':FW_C2T_fname, 'RC_G2A':RC_G2A_fname}

        if library == 2: # for Cokus library
            FW_G2A_fname = out_path+'/'+'FW_G2A'+fileExtension+'.tmp'
            RC_C2T_fname = out_path+'/'+'RC_C2T'+fileExtension+'.tmp'
            reads_fnames['FW_G2A'] = FW_G2A_fname
            reads_fnames['RC_C2T'] = RC_C2T_fname
        return reads_fnames

    else: # pair-end alignment
        head1, tail1 = ntpath.split(reads_file1)
        fileName1, fileExtension1 = os.path.splitext(tail1)
        head2, tail2 = ntpath.split(reads_file2)
        fileName2, fileExtension2 = os.path.splitext(tail2)
        
        FW_C2T_fname_1 = out_path+'/'+'FW_C2T_1'+fileExtension1+'.tmp'
        FW_C2T_fname_2 = out_path+'/'+'FW_C2T_2'+fileExtension2+'.tmp'
        RC_G2A_fname_1 = out_path+'/'+'RC_G2A_1'+fileExtension1+'.tmp'
        RC_G2A_fname_2 = out_path+'/'+'RC_G2A_2'+fileExtension2+'.tmp'
        reads_fnames = {'FW_C2T_1':FW_C2T_fname_1, 'FW_C2T_2':FW_C2T_fname_2, 'RC_G2A_1':RC_G2A_fname_1, 'RC_G2A_2':RC_G2A_fname_2}

        if library == 2: # for Cokus library
            FW_G2A_fname_1 = out_path+'/'+'FW_G2A_1'+fileExtension1+'.tmp'
            FW_G2A_fname_2 = out_path+'/'+'FW_G2A_2'+fileExtension2+'.tmp'
            RC_C2T_fname_1 = out_path+'/'+'RC_C2T_1'+fileExtension1+'.tmp'
            RC_C2T_fname_2 = out_path+'/'+'RC_C2T_2'+fileExtension2+'.tmp'
            reads_fnames['FW_G2A_1'] = FW_G2A_fname_1
            reads_fnames['FW_G2A_2'] = FW_G2A_fname_2
            reads_fnames['RC_C2T_1'] = RC_C2T_fname_1
            reads_fnames['RC_C2T_2'] = RC_C2T_fname_2
        return reads_fnames


def reverse_compl(seq):
    '''
    Return the reverse complement of a nucleotide sequence
    '''
    seq=seq.upper()
    rc_seq=seq.translate(string.maketrans("ATCG", "TAGC"))[::-1]
    return rc_seq;

def reads_conversion(converted_reads_fnames, reads_file, query_format, out_path, bs_reads_fname, library, step=None):
    '''
    Convert the reads according to the library
    '''

    if step==None: idx=''
    else: idx='_'+str(step)

    FW_C2T = open(converted_reads_fnames['FW_C2T'+idx],'w')
    RC_G2A = open(converted_reads_fnames['RC_G2A'+idx],'w')
    if library == 2: # for Cokus library
        FW_G2A = open(converted_reads_fnames['FW_G2A'+idx],'w')
        RC_C2T = open(converted_reads_fnames['RC_C2T'+idx],'w')

    bs_reads = open(bs_reads_fname, 'w')

    c = 1
    inc=0
    for line in fileinput.input(reads_file):
        seq=None
        if query_format=="Illumina GAII FastQ":
            if (c==1):
                c+=1
                id = line[:-1]
                FW_C2T.write(id+"\n")
                RC_G2A.write(id+"\n")
                if library == 2:
                    FW_G2A.write(id+"\n")
                    RC_C2T.write(id+"\n")

            elif (c==2):
                c+=1
                seq = line[:-1]
                FW_C2T.write(seq.replace('C','T')+"\n")
                RC_G2A.write(reverse_compl(seq).replace('G','A')+"\n")
                if library == 2:
                    FW_G2A.write(seq.replace('G','A')+"\n")
                    RC_C2T.write(reverse_compl(seq).replace('C','T')+"\n")
            else:
                if c==4: c=1
                else: c+=1
                FW_C2T.write(line)
                RC_G2A.write(line)
                if library == 2:
                    FW_G2A.write(line)
                    RC_C2T.write(line)
            if seq!=None:
                inc+=1
                bs_reads.write(str(inc)+'\t')
                bs_reads.write(id+'\t')
                bs_reads.write(seq+'\n')

        elif query_format=="fasta":
            if line[0]=='>':
                id = line[:-1]
                FW_C2T.write(id+"\n")
                RC_G2A.write(id+"\n")
                if library == 2:
                    FW_G2A.write(id+"\n")
                    RC_C2T.write(id+"\n")
                else:
                    seq = line[:-1]
                    FW_C2T.write(seq.replace('C','T')+"\n")
                    RC_G2A.write(reverse_compl(seq).replace('G','A')+"\n") 
                    if library == 2:
                        FW_G2A.write(seq.replace('G','A')+"\n")
                        RC_C2T.write(reverse_compl(seq).replace('C','T')+"\n")

            bs_reads.write(str(inc)+'\t')
            bs_reads.write(id+'\t')
            bs_reads.write(seq+'\n')

    fileinput.close()

    FW_C2T.close()
    RC_G2A.close()
    if library == 2:
        FW_G2A.close()
        RC_C2T.close()
    bs_reads.close()
    return inc




def map_single_end_reads(soap3_path, index_path, reads_fnames, mismatches, logger, library, gpu_id, type_of_hits, ungapped):
    '''
    Invoke SOAP3-dp to map the reads
    '''

    n_dev = len(gpu_id)

    # a single GPU used
    if n_dev==1:
        #if mismatches==-1: 
        if ungapped==False: # indels support enabled
            FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, gpu_id[0], length),shell=True)
            FW_C2T_map.wait()
            logger.info('Forward reads with Cs converted to Ts mapped to the first index')
            RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, gpu_id[0], length),shell=True)
            RC_G2A_map.wait()
            logger.info('Reverse complement reads with Gs converted to As mapped to the first index')

        else: # indels support disabled
            FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, mismatches, gpu_id[0], length),shell=True)
            FW_C2T_map.wait()
            logger.info('Forward reads with Cs converted to Ts mapped to the first index')
            RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, mismatches, gpu_id[0], length),shell=True)
            RC_G2A_map.wait()
            logger.info('Reverse complement reads with Gs converted to As mapped to the first index')

        merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T']),shell=True)
        merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A']),shell=True)
        merge_FW_C2T.wait()
        merge_RC_G2A.wait()

        if library==2:
            #if mismatches==-1: 
            if ungapped==False: # indels support enabled
                FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], type_of_hits, gpu_id[0], length),shell=True)
                FW_G2A_map.wait()
                logger.info('Forward reads with Gs converted to As mapped to the second index')
                RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], type_of_hits, gpu_id[0], length),shell=True)
                RC_C2T_map.wait()
                logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')

            else: # indels support disabled
                FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], mismatches, type_of_hits, gpu_id[0], length),shell=True)
                FW_G2A_map.wait()
                logger.info('Forward reads with Gs converted to As mapped to the second index')
                RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], mismatches, type_of_hits, gpu_id[0], length),shell=True)
                RC_C2T_map.wait()
                logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')

            merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A']),shell=True)
            merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T']),shell=True)
            merge_FW_G2A.wait()
            merge_RC_C2T.wait()

    # multiple GPUs can be used
    else:
        # up to 2 cards can be used
        if n_dev==2:
            #if mismatches==-1: 
            if ungapped==False: # indels support enabled
                FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, gpu_id[0], length),shell=True)
                RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, gpu_id[1], length),shell=True)

            else: # indels support disabled
                FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, mismatches, gpu_id[0], length),shell=True)
                RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, mismatches, gpu_id[1], length),shell=True)

            FW_C2T_map.wait()
            RC_G2A_map.wait()
            logger.info('Forward reads with Cs converted to Ts mapped to the first index')
            logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
            merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T']),shell=True)
            merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A']),shell=True)
            merge_FW_C2T.wait()
            merge_RC_G2A.wait()

            if library==2:
                #if mismatches==-1:
                if ungapped==False: # indels support enabled
                    FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], type_of_hits, gpu_id[0], length),shell=True)
                    RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], type_of_hits, gpu_id[1], length),shell=True)
                else: # indels support disabled
                    FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], mismatches, type_of_hits, gpu_id[0], length),shell=True)
                    RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], mismatches, type_of_hits, gpu_id[1], length),shell=True)
                FW_G2A_map.wait()
                RC_C2T_map.wait()
                logger.info('Forward reads with Gs converted to As mapped to the second index')
                logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
                merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A']),shell=True)
                merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T']),shell=True)
                merge_FW_G2A.wait()
                merge_RC_C2T.wait()

        # up to 4 cards can be used
        elif n_dev==4:
            #if mismatches==-1: 
            if ungapped==False: # indels support enabled
                FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, gpu_id[0], length),shell=True)
                RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, gpu_id[1], length),shell=True)
            else: # indels support disabled
                FW_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T'], type_of_hits, mismatches, gpu_id[0], length),shell=True)
                RC_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -s %s -c %s -b 2 -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A'], type_of_hits, mismatches, gpu_id[1], length),shell=True)

            if library==2:
                #if mismatches==-1: 
                if ungapped==False: # indels support enabled
                    FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], type_of_hits, gpu_id[2], length),shell=True)
                    RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], type_of_hits, gpu_id[3], length),shell=True)
                else: # indels support disabled
                    FW_G2A_map=Popen('nohup %ssoap3-dp single %sFW_G2A.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A'], mismatches, type_of_hits, gpu_id[2], length),shell=True)
                    RC_C2T_map=Popen('nohup %ssoap3-dp single %sFW_C2T.fa.index %s -s %s -h %s -b 2 -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T'], mismatches, type_of_hits, gpu_id[3], length),shell=True)
                FW_G2A_map.wait()
                RC_C2T_map.wait()
                logger.info('Forward reads with Gs converted to As mapped to the second index')
                logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
                merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A']),shell=True)
                merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T']),shell=True)
                merge_FW_G2A.wait()
                merge_RC_C2T.wait()

            FW_C2T_map.wait()
            RC_G2A_map.wait()
            logger.info('Forward reads with Cs converted to Ts mapped to the first index')
            logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
            merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T']),shell=True)
            merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A']),shell=True)
            merge_FW_C2T.wait()
            merge_RC_G2A.wait()

def map_pair_end_reads(soap3_path, index_path, reads_fnames, mismatches, maxInsertSize, minInsertSize, logger, library, gpu_id, type_of_hits, ungapped):
    '''
    Invoke SOAP3-dp to map the reads
    '''

    n_dev = len(gpu_id)

    # a single GPU used
    if n_dev==1:
	if ungapped==False: # indels support enabled
	  FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'],
	  type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	  FW_C2T_map.wait() # wait to synchronize GPU threads
	  logger.info('Forward reads with Cs converted to Ts mapped to the first index')
	  RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'],  type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	  RC_G2A_map.wait()
	  logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
	  merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T_1']),shell=True)
	  merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A_1']),shell=True)
	  merge_FW_C2T.wait()
	  merge_RC_G2A.wait()
	else: # indels support disabled
	  FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	  FW_C2T_map.wait() # wait to synchronize GPU threads
	  logger.info('Forward reads with Cs converted to Ts mapped to the first index')
	  RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	  RC_G2A_map.wait()
	  logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
	  merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T_1']),shell=True)
	  merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A_1']),shell=True)
	  merge_FW_C2T.wait()
	  merge_RC_G2A.wait()

        if library==2:
	    if ungapped==False: # indels support enabled
	      FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	      FW_G2A_map.wait()
	      logger.info('Forward reads with Gs converted to As mapped to the second index')
	      RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	      RC_C2T_map.wait()
	      logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
	      merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
	      merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
	      merge_FW_G2A.wait()
	      merge_RC_C2T.wait()
	    else: # indel support disabled
	      FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	      FW_G2A_map.wait()
	      logger.info('Forward reads with Gs converted to As mapped to the second index')
	      RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
	      RC_C2T_map.wait()
	      logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
	      merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
	      merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
	      merge_FW_G2A.wait()
	      merge_RC_C2T.wait()

    # multiple GPUs can be used
    else:
        # up to 2 cards can be used
        if n_dev==2:
	    if ungapped==False: # indels support enabled
	      FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'], type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	      RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
	      FW_C2T_map.wait() # wait to synchronize GPU threads
	      logger.info('Forward reads with Cs converted to Ts mapped to the first index')
	      RC_G2A_map.wait()
	      logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
	      merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T_1']),shell=True)
	      merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A_1']),shell=True)
	      merge_FW_C2T.wait()
	      merge_RC_G2A.wait()
	    else: # indels support disabled
	      FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	      RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
	      FW_C2T_map.wait() # wait to synchronize GPU threads
	      logger.info('Forward reads with Cs converted to Ts mapped to the first index')
	      RC_G2A_map.wait()
	      logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
	      merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T_1']),shell=True)
	      merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A_1']),shell=True)
	      merge_FW_C2T.wait()
	      merge_RC_G2A.wait()

            if library==2:
		if ungapped==False: # indels support enabled
		  FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
		  RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
		  FW_G2A_map.wait()
		  logger.info('Forward reads with Gs converted to As mapped to the second index')
		  RC_C2T_map.wait()
		  logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
		  merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
		  merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
		  merge_FW_G2A.wait()
		  merge_RC_C2T.wait()
		else: # indels support disabled
		  FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[0], length),shell=True)
		  RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
		  FW_G2A_map.wait()
		  logger.info('Forward reads with Gs converted to As mapped to the second index')
		  RC_C2T_map.wait()
		  logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
		  merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
		  merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
		  merge_FW_G2A.wait()
		  merge_RC_C2T.wait()
        # up to 4 cards can be used
        elif n_dev==4:
	    if ungapped==False: # indels support enabled
	      FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'], type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	      RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
	    else: # indels support disabled
	      FW_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_C2T_1'], reads_fnames['FW_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize, gpu_id[0], length),shell=True)
	      RC_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h %s -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_G2A_1'], reads_fnames['RC_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[1], length),shell=True)
	    
            if library==2:
		if ungapped==False: # indels support enabled
		  FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -h 2 -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[2], length),shell=True)
		  RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -h 2 -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], type_of_hits, maxInsertSize, minInsertSize,  gpu_id[3], length),shell=True)
		  FW_G2A_map.wait()
		  logger.info('Forward reads with Gs converted to As mapped to the second index')
		  RC_C2T_map.wait()
		  logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
		  merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
		  merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
		  merge_FW_G2A.wait()
		  merge_RC_C2T.wait()
		else: # indels support disabled
		  FW_G2A_map=Popen('nohup %ssoap3-dp pair %sFW_G2A.fa.index %s %s -s %s -h 2 -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['FW_G2A_1'], reads_fnames['FW_G2A_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[2], length),shell=True)
		  RC_C2T_map=Popen('nohup %ssoap3-dp pair %sFW_C2T.fa.index %s %s -s %s -h 2 -b 2 -u %s -v %s -c %s -L %s'%(soap3_path, index_path, reads_fnames['RC_C2T_1'], reads_fnames['RC_C2T_2'], mismatches, type_of_hits, maxInsertSize, minInsertSize,  gpu_id[3], length),shell=True)
		  FW_G2A_map.wait()
		  logger.info('Forward reads with Gs converted to As mapped to the second index')
		  RC_C2T_map.wait()
		  logger.info('Reverse complement reads with Cs converted to Ts mapped to the first index\n')
		  merge_FW_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_G2A_1']),shell=True)
		  merge_RC_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_C2T_1']),shell=True)
		  merge_FW_G2A.wait()
		  merge_RC_C2T.wait()

            FW_C2T_map.wait() # wait to synchronize GPU threads
            logger.info('Forward reads with Cs converted to Ts mapped to the first index')
            RC_G2A_map.wait()
            logger.info('Reverse complement reads with Gs converted to As mapped to the first index')
            merge_FW_C2T=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['FW_C2T_1']),shell=True)
            merge_RC_G2A=Popen('nohup %smerge-sam.sh %s'%(soap3_path, reads_fnames['RC_G2A_1']),shell=True)
            merge_FW_C2T.wait()
            merge_RC_G2A.wait()
            

def remove_ambiguous(reads_fnames, library, edit_distance, w_ambiguous, single_end):
    '''
    Remove ambiguous mapped reads in two steps.

    First step: it removes those reads that match at least 2 times in all possible alignments (different strands)
    Second step: it removes those reads that provide at least two best score alignments
    '''
    
    if single_end: idx=''
    else: idx='_1'

    # first step
    FW_C2T_ALIGN, FW_C2T_POS = get_alignments(reads_fnames['FW_C2T'+idx], int(edit_distance), '+FW')
    RC_G2A_ALIGN, RC_G2A_POS = get_alignments(reads_fnames['RC_G2A'+idx], int(edit_distance), '-FW')
    if library == 2:
        FW_G2A_ALIGN, FW_G2A_POS = get_alignments(reads_fnames['FW_G2A'+idx], int(edit_distance), '-RC')
        RC_C2T_ALIGN, RC_C2T_POS = get_alignments(reads_fnames['RC_C2T'+idx], int(edit_distance), '+RC')

    # second step
        
    if library==1: mappings = [(FW_C2T_ALIGN, FW_C2T_POS), (RC_G2A_ALIGN, RC_G2A_POS)]
    else: mappings = [(FW_C2T_ALIGN, FW_C2T_POS), (RC_G2A_ALIGN, RC_G2A_POS), (FW_G2A_ALIGN, FW_G2A_POS), (RC_C2T_ALIGN, RC_C2T_POS)]

    try:
      for mapping in mappings:
	remove_multi_best_score(mapping[0], mapping[1])
    except: pass


    if w_ambiguous==False:

        if library == 1:
	    poss_ambiguous = set(FW_C2T_ALIGN.keys()).intersection(set(RC_G2A_ALIGN.keys()))
        else: #if library == 2:
            poss_ambiguous = set.intersection(set(FW_C2T_ALIGN.keys()), set(RC_G2A_ALIGN.keys()), set(FW_G2A_ALIGN.keys()), set(RC_C2T_ALIGN.keys()))

        ambiguous=set()
        for read_id in poss_ambiguous:
	    # ambiguous are those reads that present at least a mapping
	    # with the lower number of differences in at least two different alignments
	    for d in range(int(edit_distance)+1):
                if (library==1):
		    '''
		    if (FW_C2T_ALIGN[read_id][d]!=0 and RC_G2A_ALIGN[read_id][d]!=0):
                        ambiguous.add(read_id)
                        break #continue
		    elif (FW_C2T_ALIGN[read_id][d]!=0 and RC_G2A_ALIGN[read_id][d]==0):
			del(RC_G2A_ALIGN[read_id]); del(RC_G2A_POS[read_id])
			break
		    elif (FW_C2T_ALIGN[read_id][d]==0 and RC_G2A_ALIGN[read_id][d]!=0):
                        del(FW_C2T_ALIGN[read_id]); del(FW_C2T_POS[read_id])
			break
		    else: continue
		    '''
		    if (FW_C2T_ALIGN[read_id][d]!=0 and RC_G2A_ALIGN[read_id][d]!=0):
			if (FW_C2T_POS[read_id][0]['score']==RC_G2A_POS[read_id][0]['score']):
			  ambiguous.add(read_id)
			  break #continue
			elif (FW_C2T_POS[read_id][0]['score']>RC_G2A_POS[read_id][0]['score']):
			  del(RC_G2A_ALIGN[read_id]); del(RC_G2A_POS[read_id])
			  break
			elif (FW_C2T_POS[read_id][0]['score']<RC_G2A_POS[read_id][0]['score']):  
			  del(FW_C2T_ALIGN[read_id]); del(FW_C2T_POS[read_id])
			  break
		    elif (FW_C2T_ALIGN[read_id][d]!=0 and RC_G2A_ALIGN[read_id][d]==0):
			del(RC_G2A_ALIGN[read_id]); del(RC_G2A_POS[read_id])
			break
		    elif (FW_C2T_ALIGN[read_id][d]==0 and RC_G2A_ALIGN[read_id][d]!=0):
                        del(FW_C2T_ALIGN[read_id]); del(FW_C2T_POS[read_id])
			break
		    else: continue
                else:
                    if ((FW_C2T_ALIGN[read_id][d]!=0 and RC_G2A_ALIGN[read_id][d]!=0) or
                        (FW_C2T_ALIGN[read_id][d]!=0 and FW_G2A_ALIGN[read_id][d]!=0) or
                        (FW_C2T_ALIGN[read_id][d]!=0 and RC_C2T_ALIGN[read_id][d]!=0) or
                        (RC_G2A_ALIGN[read_id][d]!=0 and FW_G2A_ALIGN[read_id][d]!=0) or
                        (FW_C2T_ALIGN[read_id][d]!=0 and RC_C2T_ALIGN[read_id][d]!=0) or
                        (FW_G2A_ALIGN[read_id][d]!=0 and RC_C2T_ALIGN[read_id][d]!=0)):
                        ambiguous.add(read_id)
                        continue
            
	
	del poss_ambiguous
  
        for read in ambiguous:
            try:
                del(FW_C2T_ALIGN[read]); del(FW_C2T_POS[read])
                del(RC_G2A_ALIGN[read]); del(RC_G2A_POS[read])
                if library==2:
                    del(FW_G2A_ALIGN[read]); del(FW_G2A_POS[read])
                    del(RC_C2T_ALIGN[read]); del(RC_C2T_POS[read])
            except KeyError: pass

        # second step
        '''
        if library==1: mappings = [(FW_C2T_ALIGN, FW_C2T_POS), (RC_G2A_ALIGN, RC_G2A_POS)]
        else: mappings = [(FW_C2T_ALIGN, FW_C2T_POS), (RC_G2A_ALIGN, RC_G2A_POS), (FW_G2A_ALIGN, FW_G2A_POS), (RC_C2T_ALIGN, RC_C2T_POS)]

	try:
	  for mapping in mappings:
            remove_multi_best_score(mapping[0], mapping[1])
        except: pass
	'''
        
        # free the memory
        del(FW_C2T_ALIGN); del(RC_G2A_ALIGN)
        if library==2:
            del(FW_G2A_ALIGN); del(RC_C2T_ALIGN)


    if (library==1): return [FW_C2T_POS, RC_G2A_POS]
    return [FW_C2T_POS, RC_G2A_POS, FW_G2A_POS, RC_C2T_POS]


def get_valid_reads(valid_mappings, bs_reads_fname, library):
    '''
    Return only the not ambiguous reads
    '''
    valid_read_ids = set()
    valid_read_ids.update(set(valid_mappings[0].keys()))
    valid_read_ids.update(set(valid_mappings[1].keys()))
    if library==2:
        valid_read_ids.update(set(valid_mappings[2].keys()))
        valid_read_ids.update(set(valid_mappings[3].keys()))
    
    reads = {}
    for line in fileinput.input(bs_reads_fname):
        l = line.split()
        read_id = l[1][1:]
        if read_id in valid_read_ids:
            reads[read_id] = {}
            reads[read_id]['header'] = l[1]+' '+l[2]
            # reads[read_id]['read'] = l[3] # the original bisulfite-treated read
            reads[read_id]['read'] = l[-1] # the original bisulfite-treated read


    fileinput.close()
    return reads

def calc_mismatches(read, reference, rule='TC'):
    '''
    Calculate the number of mismatches.
    '''
    pairs = []
    
    pairs = [read[i]+reference[i] for i in range(min([len(read), len(reference)])) if read[i]!=reference[i] and read[i]!="N" and reference[i]!="N"]
    return len([paired for paired in pairs if paired != rule])

    
def methylation_level(read, reference):
    '''
    Calculate the methylation level
    
        - bases that not involving cytosines
        X   methylated C in CHG context
        x unmethylated C in CHG context
        H   methylated C in CHH context
        h unmethylated C in CHH context
        Z   methylated C in CpG context
        z unmethylated C in CpG context
    '''

    H = ['A','C','T']
    reference = reference.replace('_','')
    methylation = str()
    level = '-'
    for i in range(len(read)):
        if read[i] not in ['C','T']: level = '-'
	elif read[i]=='T' and reference[i+2]=='C': # unmethylated Cs
            if reference[i+3]=='G': level = 'x'
            elif reference[i+3] in H :
                if reference[i+4]=='G': level = 'y'
                elif reference[i+4] in H: level = 'z'
	elif read[i]=='C' and reference[i+2]=='C': # methylated Cs
            if reference[i+3]=='G': level = 'X'
            elif reference[i+3] in H:
                if reference[i+4]=="G": level = 'Y'
                elif reference[i+4] in H: level = 'Z'
	else: level = '-'
	methylation = methylation + level
    return methylation

def read_mapping_analysis(strand_alignments, reference_seqs, library, methylation, mismatches, bs_reads_fname, out_path, n, ed_limit, ungapped, ref_names_conv):
    
    XR={0:'CT', 1:'CT', 2:'GA', 3:'GA'}
    XG={0:'CT', 1:'GA', 2:'CT', 3:'GA'}
    FLAG={0:'0', 1:'16', 2:'16', 3:'0'} # consider only bit 0x10 
		  
    n_alignments = dict()
    # load into the memory the (successfully) mapped reads
    valid_mapped_reads = get_valid_reads(strand_alignments, bs_reads_fname, library)
    if methylation: out_methylation = open(out_path+'/methylation.out', 'w')
    out_alignments = open(out_path+'/'+ALIGNMENTS_FNAME, 'w')
    #if mismatches==-1: mismatches=ed_limit
    if ungapped==False: mismatches=ed_limit
    i=0
    for alignments in strand_alignments:
        i+=1
        if methylation: logger.info('Analyzing edit distance (4-letter nt alphabet) and methylation - strand %d of %d'%(i, len(valid_mappings)))
        else: logger.info('Analyzing edit distance (4-letter nt alphabet) - strand %d of %d'%(i, len(valid_mappings)))
	try:
	  for read_id in alignments.keys():
	      position = alignments[read_id][0]['position']
	      strand = alignments[read_id][0]['strand']
	      strand_fa = alignments[read_id][0]['strand_fa']
	      seq_id = alignments[read_id][0]['seq_id'].zfill(4) # note that only an alignment for a read can exists (ambiguous have been removed)
	      cigar = alignments[read_id][0]['cigar']

	      cigar_op = 'MIDNSHP=X'
	      p_cigar_op = dict([(j, cigar[j]) for j in range(len(cigar)) if cigar[j] in cigar_op])

	      indels = ('I' in cigar) or ('D' in cigar) or ('S' in cigar)
	      if (i%2==1): read_seq = valid_mapped_reads[read_id]['read'].upper()
	      else: read_seq = reverse_compl(valid_mapped_reads[read_id]['read'].upper())

	      reference_long = reference_seqs[seq_id][alignments[read_id][0]['position']-2-1:alignments[read_id][0]['position']+len(read_seq)+2-1].upper()
	      reference = reference_long[2:-2]

	      t=0
	      if indels:
		  tmp_read_seq=''
		  tmp_reference=''

		  k = 0 # cigar string shift index
		  idx_r = 0 # read sequence shift index
		  idx_R = 0 # reference sequence shift index
		  for j in sorted(p_cigar_op.iterkeys()):
		      step = int(cigar[k:j])
		      if (p_cigar_op[j]=='I' or p_cigar_op[j]=='S'):
			  tmp_reference+='-'*step
			  tmp_read_seq+=read_seq[idx_r:idx_r+step]
			  idx_r+=step
		      elif p_cigar_op[j]=='D':
			  tmp_read_seq+='-'*step
			  tmp_reference+=reference[idx_R:idx_R+step]
			  idx_R+=step
		      else:
			  tmp_read_seq+=read_seq[idx_r:idx_r+step]
			  tmp_reference+=reference[idx_R:idx_R+step]
			  idx_r+=step
			  idx_R+=step
		      k = j+1


		  read_seq=tmp_read_seq
		  reference=tmp_reference

	      if (i%2==1): n_mis = calc_mismatches(read_seq, reference) 
	      else: n_mis = calc_mismatches(read_seq, reference, 'AG')
	      
	      if (n_mis!=None and n_mis <= mismatches):
		  if not n_alignments.has_key(n_mis): n_alignments[n_mis]=0
		  n_alignments[n_mis]+=1
		  if methylation:
		      methylation_seq = methylation_level(read_seq, reference_long)
		      out_methylation.write(valid_mapped_reads[read_id]['header']+ '\t' + str(n_mis) + '\t' + read_seq + '\t' + reference + '\t' + str(position) + '\t' + methylation_seq + '\n')
		  else: methylation_seq = methylation_level(read_seq, reference_long)
		  #out_alignments.write(valid_mapped_reads[read_id]['header'] + ' ' + ref_names_conv[seq_id] + ' ' + str(position) + ' ' + strand + ' ' + str(n_mis) + '\n')
		  
		  
		  
		  out_alignments.write(valid_mapped_reads[read_id]['header'] + ' ' + FLAG[i]+' ' + ref_names_conv[seq_id] + ' ' + str(position) + ' ' + '255' + ' ' + cigar + ' ' + '*' + ' '+ '0' + ' ' + '0' + ' ' + reference + ' ' + '*' + ' ' + 'NM:i:'+str(n_mis) + ' ' + 'XM:Z:'+methylation_seq + ' ' + 'XR:Z:'+XR[i] + ' ' + 'XG:Z:'+XG[i] + '\n')
		  
		  
        except: pass    
    if methylation: out_methylation.close()
    out_alignments.close()
    return n_alignments

def optional_arg(arg_default):
    def func(option,opt_str,value,parser):
        if parser.rargs and not parser.rargs[0].startswith('-'):
            val=parser.rargs[0]
            parser.rargs.pop(0)
        else:
            val=arg_default
        setattr(parser.values,option.dest,val)
    return func



# main
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()

    #------------------------------------------#
    #            Set options                   #
    #------------------------------------------#
    parser.set_defaults(infilename=None)
    parser.add_option("-s", "--reads", dest="infilename",help="The query file (FASTA or FASTQ format) [For alignments of single-end reads]", metavar="FILE")

    parser.set_defaults(infilename1=None)
    parser.add_option("-1", "--reads1", dest="infilename1",help="A query file (FASTA or FASTQ format) [For alignments of pair-end reads]", metavar="FILE")

    parser.set_defaults(infilename2=None)
    parser.add_option("-2", "--reads2", dest="infilename2",help="A query file (FASTA or FASTQ format)[For alignments of pair-end reads]", metavar="FILE")

    parser.set_defaults(soap3path="~/soap3/")
    parser.add_option("-S", "--soap3", dest="soap3path",help="The path of SOAP3-dp [~/soap3-dp/]", metavar="PATH")

    parser.set_defaults(gpu=-1)
    parser.add_option("-g", "--gpu", dest="gpu", help="Use this option to specify the a gpu identifier. If not specified GPU-BSM uses up to four GPU cards.", metavar="INT")

    parser.add_option("-u", "--max_insert_size:", dest="maxInsertSize", help="Maximum value of insert size")

    parser.add_option("-v", "--min_insert_size:", dest="minInsertSize", help="Minimum value of insert size")

    parser.set_defaults(dbpath="indexes/")
    parser.add_option("-i", "--index_path", dest="index_path", help="The directory of the indexes (generated in preprocessing genome) [indexes/]", metavar="PATH")

    #parser.set_defaults(mismatches='-1')
    parser.set_defaults(mismatches='4')
    parser.add_option("-m", "--mismatches", dest="mismatches", help="Use this option to set the maximum number of mismatches allowed in the first step of SOAP3-dp [default 4]", metavar="INT") #. Do not use this option to take into account indels in the 

    parser.set_defaults(ed_limit='20')
    parser.add_option("-I", "--limit", dest="ed_limit", help="GPU-BSM discards those alignments obtained with more than I differences [default 20]", metavar="INT")

    parser.add_option("-M", "--methylation", dest="methylation", action='callback',callback=optional_arg('empty'), help="Use this option to calculate methylation levels")

    parser.set_defaults(type_of_hits='1')
    parser.add_option("-H", "--hits", dest="type_of_hits", help="All valid alignments: 1 (DEAULT) - All best alignments: 2 - Unique best alignments: 3")

    parser.set_defaults(library=1) 
    parser.add_option("-l", "--library", dest="library", help="BS read protocol: 1 for Lister and 2 for Cokus")

    parser.set_defaults(length=120)
    parser.add_option("-L", "--length", dest="length", help="Length of the longest read in the query file [120]")

    parser.add_option("-a", "--ambiguous", dest="w_ambiguous", action='callback', callback=optional_arg('empty'), help="Use this option to not remove ambiguous mapped reads")
    
    parser.add_option("--dp", dest="dp", action='callback', callback=optional_arg('empty'), help="Use only dynamic programming to look for both gapped and ungapped alignments")
    
    parser.add_option("--ungapped", dest="ungapped", action='callback', callback=optional_arg('empty'), help="Use this option to look only for ungapped alignments")
   
    #------------------------------------------#
    #            Check options                 #
    #------------------------------------------#
    (options, args) = parser.parse_args()
    parser.parse_args(args)
    try:
        # bs treated reads - for single-end alignments
        reads_file = options.infilename
        # bs treated reads - for pair-end alignments
        reads_file1 = options.infilename1
        reads_file2 = options.infilename2

        single_end = is_single_end(reads_file, reads_file1, reads_file2) #single_end is True for single-end alignment, it is False for pair-end alignments

        if single_end: check_file(reads_file)
        else:
            check_file(reads_file1)
            check_file(reads_file2)

        # bs read library (Lister or Cokus)  
        library = options.library
        library = int(library)
        check_BS_protocol(library)

        # looking for GPUs installed
        n_dev = count_devices()
        gpu_id = check_gpu_id(options.gpu, n_dev)
        if gpu_id==[-1]:
            gpu_id = get_devices(n_dev, library)


        if single_end==False:
            maxInsertSize = options.maxInsertSize
            minInsertSize = options.minInsertSize
            if (maxInsertSize==None or minInsertSize==None): raise InsertSizeException()
            maxInsertSize = int(maxInsertSize)
            minInsertSize = int(minInsertSize)

        # allowed mismatches
        mismatches = check_mismatches(options.mismatches)
        
        

        type_of_hits = check_type_of_hits(options.type_of_hits)

        methylation=False
        if options.methylation: methylation=True 

        length = options.length
        length = int(length)

        w_ambiguous=False
        if options.w_ambiguous: w_ambiguous=True
        
        dp=False
        if options.dp: dp=True
        
        ungapped=False
        if options.ungapped: ungapped=True
        
        if (ungapped and dp): raise MappingStrategyException()
  
	#if mismatches == -1: ed_limit = check_ed_limit(options.ed_limit)
        if ungapped == False: ed_limit = check_ed_limit(options.ed_limit)
        else: ed_limit=mismatches
	
	# the path of SOAP3-dp
        soap3_path = options.soap3path
        soap3_path = str(soap3_path)
        if soap3_path[-1] !="/": soap3_path = soap3_path+"/"
        check_dir(soap3_path) # check if the path exists

        #if (mismatches>2 and mismatches!=-1):
        change_soap3_ini_file(soap3_path, mismatches, dp) # change Soap3MisMatchAllow and SkipSOAP3Alignment settings in the soap3.ini file


        # the path of the indexes previously calcutated for the reference genome
        index_path = options.index_path
        index_path = str(index_path)
        if index_path[-1] !="/": index_path = index_path+"/"
        check_dir(index_path)
        
    except IOError:
        print '[ERROR] File %s does not exist'%(reads_file)
        exit()
    except BSProtocolError:
        print '[ERROR] BS treated reads protocol not supported: 1 for Lister - 2 for Cokus'
        parser.print_help()
        exit()
    except MismatchesError:
        print '[ERROR] GPU-BSM allows up to 4 mismatches'
        parser.print_help()
        exit()
    except DirectoryError, err:
        print '[ERROR] ', err
        exit()
    except InsertSizeException:
        print '[ERROR] Use option -u and -v for maxInsertSize and minInsertSize'
        parser.print_help()
        exit()
    except QueryException:
        print '[ERROR] Use option -s for single-end alignment or options -1 and -2 for pair-end alignment'
        parser.print_help()
        exit()
    except GPUOptionTypeException:
        print '[ERROR] Use an integer value for -g option'
        parser.print_help()
        exit()
    except InvalidGPUidException:
        print '[ERROR] Invalid GPU identifier for -g option'
        exit()
    except HitsOptionTypeException:
        print '[ERROR] Use an integer value for -H option'
        parser.print_help()
        exit()
    except InvalidHitsOptionException:
        print '[ERROR] Invalid value for -H option'
        parser.print_help()
        exit()
    except MismatchesOptionTypeException():
        print '[ERROR] Use an integer value for -m option'
        parser.print_help()
        exit()
    except MismatchesOptionException():
        print '[ERROR] Invalid value for -m option'
        parser.print_help()
        exit()
    except EDLimitOptionTypeException():
        print '[ERROR] Use an integer value for -I option'
        parser.print_help()
        exit()
    except EDLimitOptionException():
        print '[ERROR] Invalid value for -I option. Only positive values.'
        parser.print_help() 
        exit()
    except MappingStrategyException():
        print '[ERROR] Options --dp and --ungapped cannot be used together.'
        parser.print_help()
        exit()    
    except Exception, err:
        print '[ERROR] ', err
        parser.print_help()
        exit()

    #------------------------------------------#
    #            Set logger                    #
    #------------------------------------------#
    job_id = str(random.randint(1000000,9999999)) # a job identifier
    out_path ='output/'
    out_path = out_path + job_id
    os.mkdir(out_path) # the directory where results are stored
    log_path = out_path + '/' + 'log' + '.log' # log file
    
    logger = get_logger(log_path)
    logger.info('\n# ---------- Summarizing parameters ---------- #\n')
    logger.info('**************************************************\n')
    logger.info('BS reads filename: %s'%(reads_file))
    logger.info('%s protocol'%((library==1) and 'Lister' or 'Cokus'))
    logger.info('SOAP3-dp path: %s'%(soap3_path))
    logger.info('Reference genome indexes [path]: %s'%(index_path))
    logger.info('Maximum allowed mismatches: %s'%(mismatches))
    logger.info('SOAP3-dp alignments that will be analyzed: %s'%({1:'all valid alignments', 2:'all best alignments', 3:'unique best alignments'}[type_of_hits]))
    logger.info('%s devices installed'%(n_dev))
    logger.info('%s GPU(s) will be exploited for analysis'%(len(gpu_id)))
    logger.info('GPU(s) identified by the following ID(s) %s will be used'%(gpu_id))
    logger.info('Indels support: %s '%((ungapped==False and 'True' or 'False')))
    logger.info('Skip SOAP3 when look for gapped alignments: %s '%((dp==True and 'True' or 'False')))
    logger.info('**************************************************\n')
    
    #------------------------------------------#
    #            Start the job                 #
    #------------------------------------------#
    start_time = time.time()
    logger.info('Job # %s started\n'%(job_id))
    logger.info('Results will be stored in the %s directory'%(out_path))
    logger.info('**************************************************\n')

    # create temporary files to store the reads converted according to the adopted protocol
    reads_fnames = converted_reads_files(reads_file, reads_file1, reads_file2, library, single_end)
    logger.info('The following temporary files %s have been created'%(reads_fnames.values()))
    
    # detect the format of the query (FASTQ/FASTA)
    try:
        if single_end: query_format=detect_query_format(reads_file)
        else:
            query_format=detect_query_format(reads_file1)
            if query_format!=detect_query_format(reads_file2): raise MultiQueryFormatException()
    except QueryFormatException:
        logger.error('Query type not supported')
        sys.exit(0)
    except MultiQueryFormatException:
        logger.error('Query files of different type')
        sys.exit(0)

    logger.info('Reads file in %s format'%(query_format))
    logger.info('Starting to convert the reads')

    #------------------------------------------#
    #          Converting bs-reads             #
    #------------------------------------------#
    bs_reads_fname = out_path+'/'+'bs_reads'
    if single_end:
        nb_reads = reads_conversion(reads_fnames, reads_file, query_format, out_path, bs_reads_fname, library)
    else: # pair ends
        nb_reads = reads_conversion(reads_fnames, reads_file1, query_format, out_path, bs_reads_fname, library, 1)
        reads_conversion(reads_fnames, reads_file2, query_format, out_path, bs_reads_fname, library, 2)
    logger.info('%s Reads have been converted'%(nb_reads))
    logger.info('**************************************************\n')
    

    #------------------------------------------#
    #          Mapping reads                   #
    #------------------------------------------#
    logger.info('Mapping reads')
    mapping_time = time.time()
    if single_end: map_single_end_reads(soap3_path, index_path, reads_fnames, mismatches, logger, library, gpu_id, type_of_hits, ungapped)
    else: map_pair_end_reads(soap3_path, index_path, reads_fnames, mismatches, maxInsertSize, minInsertSize, logger, library, gpu_id, type_of_hits, ungapped)
    os.system('rm '+ out_path+'/*gout*')
    logger.info('Reads have been mapped in %s sec'%(time.time() - mapping_time))
    logger.info('**************************************************\n')
    
    #------------------------------------------#
    #         Avoiding ambiguous reads         #
    #------------------------------------------#
    #if mismatches==-1: valid_mappings=remove_ambiguous(reads_fnames, library, ed_limit, w_ambiguous, single_end)
    if ungapped==False: valid_mappings=remove_ambiguous(reads_fnames, library, ed_limit, w_ambiguous, single_end)
    else: valid_mappings=remove_ambiguous(reads_fnames, library, mismatches, w_ambiguous, single_end)
    logger.info('Ambiguous mappings have been removed')
    logger.info('**************************************************\n')

    #------------------------------------------#
    #          Post-processing                 #
    #------------------------------------------#
    logger.info('Post-processing phase started')
    reference_file='ref.shelve'
    reference_seqs={}
    reference = shelve.open(index_path+reference_file,'r')
    # load in memory the reference sequences
    n=0
    for seq_id in reference:
        n+=1
        reference_seqs[seq_id]=reference[seq_id]
        logger.info('Reference sequence: seq id: %s size: %d bp'%(seq_id, len(reference[seq_id])))
    reference.close()

    ref_names_f=open(index_path+REF_NAMES_CONVERSION, 'rb')
    ref_names_conv = pickle.load(ref_names_f)
    ref_names_f.close()
    
    #n_alignments = dict(zip(range(mismatches+1),[0]*(mismatches+1)))
    n_alignments=read_mapping_analysis(valid_mappings, reference_seqs, library, methylation, mismatches, bs_reads_fname, out_path, n, ed_limit, ungapped, ref_names_conv)
    
    logger.info('False positives removed')
    if methylation: logger.info('Methylation calculated')
    logger.info('**************************************************\n')
    
    logger.info('Resuming results')
    logger.info('BS-reads: \t %d'%(nb_reads))
    logger.info('Uniquely aligned reads: \t %d'%(reduce(lambda n,m:n+m,n_alignments.values())))
    for n_mis in n_alignments.keys():
        logger.info('Alignments with %d mismatches: %d \t'%(n_mis, n_alignments[n_mis]))

    logger.info('Elapsed time: %s sec'%(time.time() - start_time))

    
    # remove temporary files
    os.remove(bs_reads_fname)
    os.system('rm '+ out_path+'/*tmp*')



    
