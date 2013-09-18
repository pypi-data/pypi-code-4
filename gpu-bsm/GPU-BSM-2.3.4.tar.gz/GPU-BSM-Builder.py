
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


import fileinput
import string
import os
import operator
import shelve
import time
import pickle
import subprocess
from utilities import *
from subprocess import Popen
from optparse import OptionParser



def get_reference(fasta_file, ref_path, indexes_path, logger):
    '''
    Load the reference sequence into the memory
    '''

    reference = {}
    sequence = ''
    header = ''
    nb_of_seqs = 0
    refd = shelve.open(ref_path+"refname.shelve",'n')
    ref_name_conversions = dict()
    
    
    for line in fileinput.input(fasta_file):
        l=line.split()
        if line[0]!=">":
                sequence=sequence+line[:-1]
        elif line[0]==">":
                if header=='':
                    nb_of_seqs+=1
                    header=l[0][1:]
                    short_header=str(nb_of_seqs).zfill(4)
                    ref_name_conversions[short_header]=header
                else:
                    sequence=sequence.upper()
                    reference[short_header]=sequence
                    #logger.info("Reference sequence: %s (renamed as %s ) %d bp"%(header,short_header,len(sequence))+"\n")
                    logger.info("Read reference sequence: %s %d bp"%(header,len(sequence))+"\n")
                    refd[short_header]=[header,len(sequence)]
                    sequence=''
                    header=l[0][1:]
                    nb_of_seqs+=1
                    short_header=str(nb_of_seqs).zfill(4)
                    ref_name_conversions[short_header]=header
                    

    output = open(indexes_path+REF_NAMES_CONVERSION, 'wb')
    pickle.dump(ref_name_conversions, output)
    output.close()
    #logger.info("Reference sequence: %s (renamed as %s ) %d bp"%(header,short_header,len(sequence))+"\n")
    logger.info("Read reference sequence: %s %d bp"%(header,len(sequence))+"\n")
    sequence=sequence.upper()
    reference[short_header]=sequence
    refd.close()
    
    return reference


def conversion(fname, reference, f, t):
    '''
    Convert Cs to Ts or Gs to As in the reference sequences
    f: from
    t: to
    '''

    outf=open(fname,'w')
    for sequence_id in reference.keys():
            outf.write('>%s'%(sequence_id)+"\n")
            sequence=reference[sequence_id]
            sequence=sequence.replace(f, t)
            outf.write('%s'%(sequence)+'\n')
    outf.close()


# main
if __name__ == "__main__":

    #------------------------------------------#
    #            Set options                   #
    #------------------------------------------#
    parser = OptionParser()
    parser.add_option("-r", "--reference", dest="filename",help="The reference fasta file", metavar="FILE")

    parser.set_defaults(indexes_path="indexes/")
    parser.add_option("-i", "--index_path", dest="indexes_path",help="The directory of the indexes [indexes/]", metavar="PATH")

    parser.set_defaults(soap3path="~/soap3-dp")
    parser.add_option("-S", "--soap3", dest="soap3path",help="The path of SOAP3-dp [~/soap3-dp/]", metavar="PATH")


    #------------------------------------------#
    #            Check options                 #
    #------------------------------------------#
    (options, args) = parser.parse_args()
    if options.filename==None:
        print '[ERROR] Use -f/--file option to specify a reference sequence file.'
        parser.print_help()
        exit()
    try:
        fasta_file=options.filename
        fasta_file=str(fasta_file)
        check_file(fasta_file) # check if the file exists

        indexes_path = options.indexes_path
        indexes_path = str(indexes_path)
        if indexes_path[-1] !="/": indexes_path=indexes_path+"/"
        ensure_dir(indexes_path) # if the directory does not exist it will be created

        soap3_path=options.soap3path
        soap3_path=str(soap3_path)
        if soap3_path[-1] !="/": soap3_path=soap3_path+"/"
        check_dir(soap3_path) # check if the path exists

    except IOError:
        print '[ERROR] File %s does not exist'%(fasta_file)
        exit()
    except DirectoryError, err:
        print '[ERROR] ', err
        exit()

    #------------------------------------------#
    #            Set logger                    #
    #------------------------------------------#

    log_file = indexes_path + 'log' + '.log' # log file
    logger = get_logger(log_file)
    
    #------------------------------------------#
    #            Start the job                 #
    #------------------------------------------#

    logger.info('Job started\n')
    logger.info('Reference genome file: %s'%(fasta_file))
    logger.info('SOAP3-dp path: %s'%(soap3_path))
    logger.info('Index file will be stored in the %s directory\n'%(indexes_path))


    start_time = time.time()
    reference = get_reference(fasta_file, indexes_path, indexes_path, logger)

    #------------------------------------------#
    #            Python shleve                 #
    #------------------------------------------#
    d = shelve.open(indexes_path+"ref.shelve",'n')
    for sequence_id in reference:
            d[sequence_id]=reference[sequence_id]
    d.close()

    #------------------------------------------#
    #       C-to-T and G-to-A conversions      #
    #------------------------------------------#
    logger.info('Cs to Ts conversion')
    conversion(indexes_path+'FW_C2T.fa', reference, 'C', 'T')
    logger.info('Gs to As conversion')
    conversion(indexes_path+'FW_G2A.fa', reference, 'G', 'A')

    #------------------------------------------#
    #       SOAP3-builder to build indexes     #
    #------------------------------------------#
    logger.info('Build the 2BWT indexes')
    index_1_C2T=Popen('nohup %ssoap3-dp-builder %sFW_C2T.fa > %sFW_C2T.log'%(soap3_path, indexes_path, indexes_path),shell=True)
    logger.info('The 2BWT index for the reference sequences with Cs converted to Ts has been built')

    index_2_G2A=Popen('nohup %ssoap3-dp-builder %sFW_G2A.fa > %sFW_G2A.log'%(soap3_path, indexes_path, indexes_path),shell=True)
    index_1_C2T.wait()
    
    index_2_G2A.wait()
    logger.info('The 2BWT index for the reference sequences with Gs converted to As has been built')
    
    logger.info('Converting the 2BWT index to the GPU2-BWT indexes')

    GPU2_BWT_index1_C2T = Popen('nohup %sBGS-Build  %sFW_C2T.fa.index'%(soap3_path, indexes_path), shell=True)
    GPU2_BWT_index1_C2T.wait()
    logger.info('First index converted')
    GPU2_BWT_index2_G2A = Popen('nohup %sBGS-Build  %sFW_G2A.fa.index'%(soap3_path, indexes_path), shell=True)
    GPU2_BWT_index2_G2A.wait()
    logger.info('Second index converted')

    #os.system('rm reference_genome/W_C2T./W_G2A.fa reference_genome/C_C2T.fa reference_genome/C_G2A.fa')
    elapsed_time = (time.time() - start_time)
    logger.info('Job finished')
    logger.info('Elapsed Time: %s sec'%(elapsed_time));
    
