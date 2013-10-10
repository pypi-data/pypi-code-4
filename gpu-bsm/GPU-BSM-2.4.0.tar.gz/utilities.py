
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
# rel. 2.4.0 2013-10-03
#
# contact andrea.manconi@itb.cnr.it


import os
import logging
from optparse import OptionParser
from subprocess import Popen
from pycuda import driver

class DirectoryError(Exception): pass
class BSProtocolError(Exception): pass
class MismatchesError(Exception): pass
class QueryFormatException(Exception): pass
class QueryException(Exception): pass
class MultiQueryFormatException(Exception): pass
class InsertSizeException(Exception): pass
class GPUOptionTypeException(Exception): pass
class InvalidGPUidException(Exception): pass
class HitsOptionTypeException(Exception): pass
class InvalidHitsOptionException(Exception): pass
class MismatchesOptionTypeException(Exception): pass
class MismatchesOptionException(Exception): pass
class EDLimitOptionTypeException(Exception): pass
class EDLimitOptionException(Exception): pass
class MappingStrategyException(Exception): pass
class REDSizeOptionTypeException(Exception): pass
class ADPErrorRateTypeException(Exception): pass
class ADPOverlapTypeException(Exception): pass
class AdaptersOptionException(Exception): pass



# service files
FRAGMENTS_FNAME_F = 'fragments.fwd' # (for serialization) FWD file name to store RRBS fragments
FRAGMENTS_FNAME_R = 'fragments.rev' # (for serialization) REV file name to store RRBS fragments
FRAGMENTS_FNAME = 'fragments.info' # to store valid fragments info
REF_NAMES_CONVERSION_FNAME = 'ref_name.map'
REFERENCE_FNAME = 'ref.ser' # used for serialization
ALIGNMENTS_FNAME = 'alignments.sam'
TRIMMED_FILE_PREFIX = 'trimmed_' # prefix used to store trimmed files
UTILS_PATH='utils/' 

def check_file(filename):
    with open(filename) as f: pass
    
def check_dir(f):
    f = os.path.expanduser(f)
    d = os.path.dirname(f)
    if (os.path.exists(d)==False):
        raise DirectoryError('%s directory does not exist'%(f))

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

def check_BS_protocol(protocol):
    if protocol not in [1 , 2]:
        raise BSProtocolError()

def check_mismatches(mismatches):
    if (mismatches > 4 or mismatches<0):
        raise MismatchesError()

def detect_query_format(reads_fname):
    '''
    Detect the format of the reads. Only FASTA and FASTQ format are supported.
    '''
    query_file=open(reads_fname,'r')
    header=query_file.readline()
    query_file.close()

    if header[0] not in ['@', '>']: raise QueryFormatException
    return header[0]=='@' and 'Illumina GAII FastQ' or 'fasta'

def get_logger(log_file):
    '''
    A log manager
    '''
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger = logging.getLogger('GPU-BSM')
    logger.addHandler(console)
    hdlr = logging.FileHandler(log_file)

    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    return logger

def count_devices():
    '''
    Return the number of installed GPU cards
    '''
    driver.init()
    return driver.Device.count()

def check_gpu_id(dev_id, n_dev):
    '''
    Check if the selected gpu is valid
    '''
    try:
        dev_id = int(dev_id)
    except ValueError: raise GPUOptionTypeException()
    if (dev_id not in range(n_dev) and (dev_id!=-1)):
        raise InvalidGPUidException()
    return [dev_id]

def check_type_of_hits(type_of_hits):
    '''
    Check if the set H option is valid
    '''
    try:
        type_of_hits = int(type_of_hits)
    except ValueError: raise HitsOptionTypeException()
    if type_of_hits not in range(4)[1:]:
        raise InvalidHitsOptionException()
    return type_of_hits

def check_mismatches(mismatches):
    '''
    Check if the set m option is valid
    '''
    try:
        mismatches = int(mismatches)
    except ValueError: raise MismatchesOptionTypeException()
    if mismatches not in range(5) and mismatches!=-1:
        raise MismatchesOptionException()
    return mismatches


def check_ed_limit(ed_distance):
    '''
    Check if the set I option is valid
    '''
    try:
        ed_distance = int(ed_distance)
    except ValueError: raise EDLimitOptionTypeException()
    if ed_distance < 0:
        raise EDLimitOptionException()
    return ed_distance

def get_devices(n_dev, library):
    '''
    Return devices (ids) that will be exploited by GPU-BSM according to the user specified options, installed GPUs, and bs library
    '''
    if n_dev==1: return 0 # a single gpu card installed
    else: # multiple GPUs installed (at least 2)
        if library==1: return range(2) # Lister library
        else: # Cockus library
            if n_dev>=4: return range(4)
            else: return range(2)

def is_single_end(s, p1, p2):
    '''
    Detect errors in the type (single/pair - end) of the required alignment
    '''
    if s!=None:
        if (p1!=None or p2!=None): raise QueryException()
        return True
    elif (p1!=None):
        if (s!=None): raise QueryException()
        if (p2==None): raise QueryException()
        return False
    elif (p2!=None):
        if (s!=None): raise QueryException()
        if (p1==None): raise QueryException()
        return False
    elif (s==None and p1==None and p2==None): raise QueryException()


def check_red_site_length(length):
    '''
    Check if the lengths for the DNA fragments (RRBS) are valid 
    '''
    try:
        length = int(length)
    except ValueError: raise REDSizeOptionTypeException()
    return length
    

def change_soap3_ini_file(soap_path, max_mismatches, dp):


    #if max_mismatches==-1 or max_mismatches==4: max_mismatches=3 # 
    #if max_mismatches==-1: max_mismatches=4 
    
    fin = open(soap_path+"soap3-dp.ini")
    fout = open(soap_path+"soap3-dp.ini~", "wt")

    for line in fin:
        if line.startswith('Soap3MisMatchAllow'):
	    newline = 'Soap3MisMatchAllow='+str(max_mismatches)+'\n'
            fout.write(line.replace(line, newline))  # replace and write
        elif line.startswith('SkipSOAP3Alignment'):
	    if dp==False: newline = 'SkipSOAP3Alignment=0\n'
	    else: newline = 'SkipSOAP3Alignment=1\n'
            fout.write(line.replace(line, newline))  # replace and write
        else: fout.write(line)

    fin.close()
    fout.close()
    os.rename(soap_path+'soap3-dp.ini~',soap_path+'soap3-dp.ini')
    
    
def IUPAC(n):
  return {
    'A':('A'), 
    'C':('C'), 
    'G':('G'), 
    'T':('T'),
    'R':('A','G'), 
    'Y':('C','T'), 
    'S':('G','C'),
    'W':('A','T'), 
    'K':('G','T'), 
    'M':('A','C'), 
    'B':('C','G','T'), 
    'D':('A','G','T'), 
    'H':('A','C','T'),
    'V':('A','C','G'), 
    'N':('A','C','G','T')
  }[n]
  
  
def remove_adapters(adapters, in_fname, out_fname, info_file, overlap=3, error_rate=0.1):
  '''
  Use cutadapt to remove adapters
  '''
  remove=Popen('nohup cutadapt --info-file=%s -e %s -O %s -o %s -a %s %s'%(info_file, str(error_rate), str(overlap), out_fname, adapters, in_fname),shell=True)
  remove.wait()
  