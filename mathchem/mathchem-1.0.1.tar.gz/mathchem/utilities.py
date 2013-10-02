from mathchem import *

          
def batch_process(infile, file_format, outfile, function, hydrogens=False) :
    """ Read file molecule-by-molecule and apply a <function> to each molecule
    Good for large files containing thousands of molecules
    """
    
    f_out = open(outfile, 'w')
    f_in = open(infile, 'r')
    
    if file_format == 'g6':
        for line in f_in:
            #line = f_in.readline()
            m = Mol(line)
            f_out.write(str(function(m))+"\n")
            
    elif file_format =='sdf':
        while True:
            m = _read_sdf_molecule(f_in, hydrogens)
            if m == False: break
            f_out.write(str(function(m))+"\n")
    
    elif file_format =='mol2':
        while True:
            m = _read_mol2_molecule(f_in, hydrogens)
            if m == False: break
            f_out.write(str(function(m))+"\n")
            
    # TODO: read the directory because mol file contain only one molecule
    elif file_format =='mol':
        m = read_from_mol(f_in, hydrogens)
        if m != False:
            f_out.write(str(function(m))+"\n")
        
    f_in.close()
    f_out.close()
    
    return
    

#
#    Functions that read all the file and return list of Mol instances
#

def read_from_sdf(fname, hydrogens = False):
    """
    Read the whole .sdf file and return list of Mol instances
    """

    f_in = open(fname, 'r')
    mols = []

    while True:
        m = _read_sdf_molecule(f_in, hydrogens)
        if m == False: break
        mols.append(m)
    
    f_in.close()
    return mols



def read_from_mol(fname, hydrogens = False):
    """
    Read the whole .mol file and return Mol instance
    """

    f_in = open(fname, 'r')

    m = _read_sdf_molecule(f_in, hydrogens)
    
    f_in.close()
    return m



def read_from_mol2(fname, hydrogens = False):
    """
    Read the whole .mol2 file and return list of Mol instances
    """
    
    f_in = open(fname, 'r')
    mols = []

    while True:
        m = _read_mol2_molecule(f_in, hydrogens)
        if m == False: break
        mols.append(m)
    
    f_in.close()
    return mols
 
 
    
def read_from_g6(fname):
    """
    Read the whole .g6 file (graph6 fromat) and return list of Mol instances
    """
    
    f_in = open(fname, 'r')
    mols = []

    for line in f_in:
        mols.append(Mol(line))

    f_in.close()
    return mols   

def read_from_s6(fname):
    """
    Read the whole .s6 file (sparse6 format) and return list of Mol instances
    """
    f_in = open(fname, 'r')
    mols = []

    for line in f_in:
        mols.append(Mol(line))

    f_in.close()
    return mols  

def read_from_planar_code(fname):
    """
    Read the whole file (planar code fromat) and return list of Mol instances
    """
    
    f_in = open(fname, 'rb')
    mols = []

    # read header >>planar_code<<
    f_in.read(15)
    # TODO: check for correct header
    
    byte = f_in.read(1)
    # read byte by byte

    while byte != "":
        n = ord(byte)
        
        m = Mol()
        A = [[0 for col in range(n)] for row in range(n)]
        E = [] # here we will collect edges
        k = 1 # current vertex
        while byte != "":    
            byte = f_in.read(1)
            b = ord(byte)
            if b == 0: # go to the next vertex
                k += 1
                if k == n+1: # go to the next graph
                    break
            elif A[k-1][b-1] == 0: # if we don't have already added the edge
                E.append((k-1,b-1))
                A[k-1][b-1] = 1
                A[b-1][k-1] = 1
        
        m._set_Order(n)
        m._set_A(A)
        m._set_Edges(E)
        
        mols.append(m)
        byte = f_in.read(1)

    f_in.close()
    return mols 

#
#    NCI functions
#


def read_from_NCI_by_NSC(num, hydrogens = False):

    url = 'http://cactus.nci.nih.gov/ncidb2.2/nci2.2.tcl?op1=nsc&data1='+num+'&output=sdf&nomsg=1&maxhits=1000000'
    
    return _read_from_NCI(url, hydrogens)


def read_from_NCI_by_name(name, hydrogens = False, fields = []):

    fields_string = ''
    for f in fields: fields_string = fields_string + '&fields=' + urllib.quote_plus(f)
    
    url = 'http://cactus.nci.nih.gov/ncidb2.2/nci2.2.tcl?op1=name&data1='+name+'&method1=substring&output=sdf&nomsg=1&maxhits=1000000'+ fields_string

    return _read_from_NCI(url, hydrogens)


def read_from_NCI_by_CAS(num, hydrogens = False):

    url = 'http://cactus.nci.nih.gov/ncidb2.2/nci2.2.tcl?op1=cas&data1='+num+'&output=sdf&nomsg=1&maxhits=1000000'

    return _read_from_NCI(url, hydrogens)

    

# helpers

def spectrum(matrix):
    r""" Calculates spectrum of the matrix"""
    from numpy import linalg as la
    s = la.eigvalsh(matrix).tolist()
    s.sort(reverse=True)
    return s


def all_adriatic():
    """ Generate all possible parameters sets for adriatic indices"""
    r = []
    for p in [0,1]:
        for i in [1,2,3]:
            for j in range(1,9):
                if i == 3:
                    for a in [0.5, 2]:
                        r.append((p,i,j,a))
                elif i == 2 and j in range(1,6):
                    for a in [-1, -0.5, 0.5, 1, 2]:
                        r.append((p,i,j,a))
                elif i == 2 or i == 1:
                    for a in [0.5, 1, 2]:
                        r.append((p,i,j,a))
    return r    
    
def adriatic_name(p,i,j,a):
    """ Return the name for given parameters of Adriatic indices"""
    #(j)
    name1 = {1:'Randic type ',\
             2:'sum ',\
             3:'inverse sum ', \
             4:'misbalance ', \
             5:'inverse misbalance ', \
             6:'min-max ', \
             7:'max-min ', \
             8:'symmetric division '}
    # (i,a)         
    name2 = {(1, 0.5):'lor',\
             (1,1):'lo', \
             (1,2):'los', \
             (2,-1):'in', \
             (2, -0.5):'ir', \
             (2, 0.5):'ro', \
             (2,1):'', \
             (2,2):'s', \
             (3, 0.5):'ha', \
             (3,2):'two'}
    #(p)         
    name3 = {0:'deg', 1:'di'}
    
    return(name1[j]+name2[(i,a)]+name3[p])
    
def spectral_moment( k, matrix):
    """ Return k-th spectral moment of a matrix
    
    parameters: matrix
    """
    return np.power(spectrum(matrix),k).tolist()
        
def spectral_radius(matrix):
    s = spectrum(matrix)
    return max(abs(s[0]), abs(s[len(s)-1]))
    

    
def energy(matrix):
    """ Return energy of a matrix 
    
    parameters: matrix
    """
    return np.float64(np.sum( map( lambda x: abs(x) , spectrum(matrix)), dtype=np.float128))
    
    
###
###
###   Private functions
###
###
    
# make a request to the NCI and retreive data in form of SDF-file
def _read_from_NCI(url, hydrogens = False):
    import urllib2, tempfile
    
    resp = urllib2.urlopen(url)
    
    if resp.code != 200:
        print 'Server returned error code ', resp.code
        return False
    
    f = tempfile.TemporaryFile()
    f.write(resp.read())
    f.seek(0)
    mols = []
    while True:
        m = _read_sdf_molecule(f, hydrogens)
        if m == False: break
        mols.append(m)
    f.close()
        
    return mols



# functions which parse a fragment of file and initialize Mol instance

# read a single molecule from file
def _read_sdf_molecule(file, hydrogens = False):
    # read the header 3 lines
    for i in range(3):
        file.readline()
    line = file.readline()
    
    if line == '': return False
    
    # this does not work for 123456 which must be 123 and 456
    #(atoms, bonds) = [t(s) for t,s in zip((int,int),line.split())]
    atoms = int(line[:3])
    bonds = int(line[3:6])
    
    order = atoms
    
    v = [];
    
    for i in range( atoms ):
        line = file.readline()
        symbol = line.split()[3]
        
        if hydrogens == False and (symbol == 'H' or symbol == 'h'):
            order = order - 1
        else:
            v.append(i+1);
            
    
    # fill the matrix A zeros
    A = [[0 for col in range(order)] for row in range(order)]
    edges = []
    
    for i in range( bonds ):
        line = file.readline()
        #(a1, a2) = [t(s) for t,s in zip((int,int),line.split())]
        a1 = int(line[:3])
        a2 = int(line[3:6])

        if a1 in v and a2 in v:
            # add edge here!
            k = v.index(a1)
            j = v.index(a2)
            A[k][j] = 1
            A[j][k] = 1
            edges.append((k,j))
    
    
    while line !='':
        line = file.readline()
        if line[:4] == "$$$$": break
        
    m = Mol()
    m._set_A(A)
    m._set_Order(order)
    m._set_Edges(edges)
    
    return m
    
    
# read a single molecule from file
def _read_mol2_molecule(file, hydrogens = False):

    # seek for MOLECULE tag
    line = file.readline()
    
    while line != '':
        if line.strip() == '@<TRIPOS>MOLECULE': break
        line = file.readline()


    if line == '': return False
    #skip molecule name
    file.readline()

    # read
    line = file.readline()

    
    atoms = int(line.split()[0])
    # TODO: number of bonds may not be present
    bonds = int(line.split()[1])
    
    #print atoms, bonds
        
    order = atoms
    
    v = [];
    
    # seek for ATOM tag
    line = file.readline()
    while line != '':
        if line.strip() == '@<TRIPOS>ATOM': break
        line = file.readline()
       
    for i in range( atoms ):
        line = file.readline()
        arr = line.split()
        id = int(arr[0])
        symbol = arr[4]
        
        if hydrogens == False and (symbol == 'H' or symbol == 'h'):
            order = order - 1
        else:
            v.append(id);
            
    
    # fill the matrix A zeros
    A = [[0 for col in range(order)] for row in range(order)]
    edges = []
    
    #seek for bonds tag @<TRIPOS>BOND
    line = file.readline()
    while line !='':
        if line.strip() == '@<TRIPOS>BOND': break
        line = file.readline()
        
    if line == '': return False
    
    
    for i in range( bonds ):
        line = file.readline()
        (bid, a1, a2) = [t(s) for t,s in zip((int, int,int),line.split())]


        if a1 in v and a2 in v:
            # add edge here!
            k = v.index(a1)
            j = v.index(a2)
            A[k][j] = 1
            A[j][k] = 1
            edges.append((k,j))
        
    m = Mol()
    m._set_A(A)
    m._set_Order(order)
    m._set_Edges(edges)
    
    return m

