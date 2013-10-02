import numpy as np

class Mol ():
    r"""
    Molecule.
    """
    __g6_string = ''
    # Adjacency matrix
    __A = []
    # Incidence matrix
    __B = []
    # Laplacian matrix
    __L = []
    # Normalized laplacian matrix
    __NL = []
    # Signless laplacian matrix
    __Q = []
    # Distance matrix
    __D = []
    # Resistance Distance matrix
    __RD = []

    __Order = 0
    __Edges = []
    
    __Sage_graph = None
    __NX_graph = None
    
    __Degrees = []
    
    
    __Spectrum = []
    __Laplacian_spectrum = []
    __Distance_spectrum = []
    __Norm_laplacian_spectrum = []
    __Signless_laplacian_spectrum = []
    __RD_spectrum = []
    
    __Is_connected = None
    # Switch it to False when we know that the graph is connected. Useful for big calculations
    __Check_connectedness = True
    
    def _reset_(self):
        """ Reset all attributes """
        self.__g6_string = ''
        # Adjacency matrix
        self.__A = []
        # Incidence matrix
        self.__B = []
        # Laplacian matrix
        self.__L = []
        # Normalized laplacian matrix
        self.__NL = []
        # Signless laplacian matrix
        self.__Q = []
        # Distance matrix
        self.__D = []
        # Resistance Distance matrix
        self.__RD = []
    
        self.__Order = 0
        self.__Edges = []
        
        self.__Sage_graph = None
        self.__NX_graph = None
        
        self.__Degrees = []
        
        
        self.__Spectrum = []
        self.__Laplacian_spectrum = []
        self.__Distance_spectrum = []
        self.__Norm_laplacian_spectrum = []
        self.__Signless_laplacian_spectrum = []
        self.__RD_spectrum = []
        
        self.__Is_connected = None
    
    # allow to set structure from somewhere
    # used in utilites
    
    def _set_A(self, A):
        self.__A = A
        
    def _set_Edges(self, edges):
        self.__Edges = edges
        
    def _set_Order(self, order):
        self.__Order = order
    
    # native method to initialize Mol class is to provide g6 string
    def __init__(self, string=None, check_connectedness=True):
        """ Molecular graph class """
        self.__Check_connectedness = check_connectedness
        if string != None:
            if string[0] == '>':
                if string.startswith('>>graph6<<'):
                    string = string[10:]
                elif string.startswith('>>sparse6<<'):
                    string = string[11:]
                            
            if string[0] == ':':
                print self.read_s6(string)
            else:
                self.read_g6(string)
        
          
    def __repr__(self):
        if self.__A != None: return  'Molecular graph on '+ str(self.__Order)+' vertices, g6: ' + self.__g6_string
        return 'Empty Molecular graph'
        
    def __len__(self):
        if self.__A != None: return len(self.__A)
        else: return 0
    
    def set_check_connectedness(self, c):
        """ Switch on/off of checking connectedness for the graph. Might be useful in batch calculations to economy time.
        args: c (True/False)
        """
        self.check_connectedness = c

    def g6_string(self):
        """ Return a graph6 string representation of the graph
        
        Alias: graph6_string """
        return self.__g6_string
    # alias like in Sage:    
    graph6_string = g6_string
    
    def order(self):
        """ Return number of vertices """
        return self.__Order
    # alias for order
    n = order
    
    def edges(self):
        """ Return list of edges """    
        return self.__Edges
    
    def size(self):
        """ Return number of edges"""
        return len(self.__Edges)
    # alias for size
    m = size
    
    def vertices(self):
        """ Return list of vertices """
        return range(self.__Order)
           
    def sage_graph(self):
        """ Return Sage Graph object """
        if self.__Sage_graph is None: self._init_sage_graph_()
        return self.__Sage_graph
         
            
    def NX_graph(self):
        """ Return NetworkX graph object """
        if self.__NX_graph is None:
            import networkx as nx
            self.__NX_graph = nx.Graph(self.__Edges)
        return self.__NX_graph
        
        
    def _init_sage_graph_(self):
        """ Initialize SAGE graph from Adjacency matrix"""
        from sage.graphs.graph import Graph
        self.__Sage_graph = Graph(self.__Edges)
            
            
    def read_g6(self, s):
        """ Initialize graph from graph6 string """
        
        def graph_bit(pos,off):
            return ( (ord(s[off + 1+ pos/6]) - 63) & (2**(5-pos%6)) ) != 0
        
        if s.startswith('>>graph6<<'):
            s = s[10:]
        # reset all the attributes before changing the structure    
        self._reset_()
        
                
        n = ord(s[0]) - 63
        off = 0
        if n==63:
            if ord(s[1]) - 63 != 63:
                n = ((ord(s[1])-63)<<12) + ((ord(s[2])-63)<<6) + ord(s[3])-63
                
                off = 3
            else:
                n = ((ord(s[2])-63)<<30) + ((ord(s[3])-63)<<24) + ((ord(s[4])-63)<<18) + ((ord(s[5])-63)<<12) + ((ord(s[6])-63)<<6) + ord(s[7])-63
                
                off = 7
                
        self.__Order = n     
    
        self.__A = [[0 for col in range(n)] for row in range(n)]
    
        i=0; j=1
        
        self.__Edges = [];
        for x in range(n*(n-1)/2):
            if graph_bit(x, off):
                self.__A[i][j] = 1
                self.__A[j][i] = 1
                self.__Edges.append((i,j))
            if j-i == 1:
                i=0
                j+=1
            else:
                i+=1
                
        self.__g6_string = s
    
    read_graph6 = read_g6
    
    def read_s6(self, s):
        """ Initialize graph from sparse6 string """
        def graph_bit(pos,off):
            return ( (ord(s[off + 1+ pos/6]) - 63) & (2**(5-pos%6)) ) != 0
        
        
        if s.startswith('>>sparse6<<'):
            s = s[11:]
        if not s[0] == ':':
            print 'This is not a sparse6 format!'
            return False

        # reset all the attributes before changing the structure    
        self._reset_()
                      
        s = s[1:]
        n = ord(s[0]) - 63
        off = 0
        if n==63:
            if ord(s[1]) - 63 != 63:
                n = ((ord(s[1])-63)<<12) + ((ord(s[2])-63)<<6) + ord(s[3])-63
                
                off = 3
            else:
                n = ((ord(s[2])-63)<<30) + ((ord(s[3])-63)<<24) + ((ord(s[4])-63)<<18) + ((ord(s[5])-63)<<12) + ((ord(s[6])-63)<<6) + ord(s[7])-63
                
                off = 7
                
        self.__Order = n     
        
        k = 1
        while 1<<k < n:
           k += 1
       
        data = s[off+1:]
        
        print n,k
        print data
        
        def parseData():
            """Return stream of pairs b[i], x[i] for sparse6 format."""
            chunks = iter(data)
            d = None # partial data word
            dLen = 0 # how many unparsed bits are left in d
        
            while 1:
                if dLen < 1:
                    d = ord(next(chunks))-63
                    dLen = 6
                dLen -= 1
                b = (d>>dLen) & 1 # grab top remaining bit
    			
                x = d & ((1<<dLen)-1) # partially built up value of x
                xLen = dLen		# how many bits included so far in x
                while xLen < k:	# now grab full chunks until we have enough
                    d = ord(next(chunks)) - 63
                    dLen = 6
                    x = (x<<6) + d
                    xLen += 6
                x = (x >> (xLen - k)) # shift back the extra bits
                dLen = xLen - k
                yield b,x

        self.__A = [[0 for col in range(n)] for row in range(n)]
    
        
        self.__Edges = [];
        
        v = 0
        
        for b,x in parseData():
            if b: v += 1
            if x >= n: break # padding with ones can cause overlarge number here
            elif x > v: v = x
            else:
                self.__A[x][v] = 1
                self.__A[v][x] = 1
                self.__Edges.append((x,v))
        
        self.__g6_string = ''

    read_sparse6 = read_s6
    
    def write_dot_file(self, filename):
    
        f_out = open(filename, 'w')
        f_out.writelines('graph Mol {\n')
        for (i,j) in self.edges():
            f_out.writelines( '    ' + str(i) + ' -- ' + str(j) +';\n')
        f_out.writelines('}')    
        f_out.close()
                    
    #
    #
    # matrices
    #
    #
    
    def adjacency_matrix(self):
        """ Return Adjacency matrix
        
        Alias : A
        """    
        return self.__A
        
    A = adjacency_matrix
    
    def incidence_matrix(self):
        """ Return Incidence matrix 
        
        Alias: B
        """
        if self.__B == []:
            def func((u,v)):
                col = [0] * self.__Order
                col[u] = 1
                col[v] = 1
                return col
            # apply func to each edge
            b = map(lambda e: func(e), self.edges())
            # transpose the result
            self.__B = map(list, zip(*b)) 
        return self.__B
        
    B = incidence_matrix


    def laplacian_matrix(self):
        """ Return Laplacian matrix
        
        L = D-A
        where  D - matrix whose diagonal elements are the degrees of the corresponding vertices
               A - adjacency matrix
                
        Alias : L
        """
        if self.__L == []:
            self.__L = np.diag(self.degrees()) - np.matrix(self.__A);
        return self.__L
        
    L = laplacian_matrix
    
    
    def signless_laplacian_matrix(self):
        """ Return Signless Laplacian matrix
        
        Q = D+A
        Alias : Q
        """
        if self.__Q == []:

            self.__Q = np.diag(self.degrees()) + np.matrix(self.__A);
        return self.__Q
        
    Q = signless_laplacian_matrix
    
    
    def normalized_laplacian_matrix(self):
        """ Return Normalized Laplacian matrix
        
        NL = deg^(-1/2) * L * deg(1/2)
        Alias : NL
        """
        ## TODO: check if we have zeros in degrees()
        if self.__NL  == []:
            d1 = np.diag( np.power( self.degrees(), -.5 ))
            d2 = np.diag( np.power( self.degrees(),  .5 ))
            self.__NL = d1 * self.laplacian_matrix() * d2
        return self.__NL
        
    NL = normalized_laplacian_matrix


    def distance_matrix(self):
        """ Return Distance matrix
        
        Alias : D
        """    
        if self.__Order == 0: return []
        
        if self.__D == [] :
            # use here float only for using np.inf - infinity
            A = np.matrix(self.__A, dtype=float)
            n,m = A.shape
            I=np.identity(n)
            A[A==0]=np.inf # set zero entries to inf
            A[I==1]=0 # except diagonal which should be zero
            for i in range(n):
                r = A[i,:]
                A = np.minimum(A, r + r.T)
            self.__D = np.matrix(A,dtype=int)
            
        return self.__D  
        
    D = distance_matrix
    
    def reciprocal_distance_matrix(self):
        """ Return Reciprocal Distance matrix """

        rd = np.matrix(self.distance_matrix(),dtype=float)
        # probably there exists more python way to apply a function to each element of matrix
        for i in range(self.__Order):
            for j in range(self.__Order):
                if not rd[i,j] == 0: rd[i,j] = 1 / rd[i,j]
        
        return rd

    
    def resistance_distance_matrix(self):
        """ Return Resistance Distance matrix """
        
        if not self.is_connected() or self.__Order == 0:
            return False
            
        if self.__RD == []:
            #from numpy import linalg as la
            n = self.__Order
            s = n*self.laplacian_matrix() + 1
            sn = n* np.linalg.inv(s)
            RD = np.ndarray((n,n))
            for i in range(n):
                for j in range(n):
                    RD[i,j] = np.float64( np.float128(sn[i,i]) + np.float128(sn[j,j]) - 2*np.float128(sn[i,j]) )
            self.__RD = RD
            
        return self.__RD
    #
    #
    # Graph invariants
    #
    #
    
    def diameter(self):
        """ Return diameter of the graph
        
        Diameter is the maximum value of distance matrix
        """
        return self.distance_matrix().max()
        
    
        
    def degrees(self):
        """ Return degree of the vertex
        
        Alias : deg
        """
        if self.__Degrees == []:
            self.__Degrees = map(lambda r: sum(r) , self.__A)
        ## calcuate degrees for all vertices
        return self.__Degrees
        
    deg = degrees
                
                
    def eccentricity(self):
        """ Eccentricity of the graph for all its vertices"""
        if self.__Order == 0: return None
        
        return self.distance_matrix().max(axis=0).tolist()[0]
        
        
        
    def distances_from_vertex(self, v):
        """ Return list of all distances from a given vertex to all others"""
        # used to test graph where it is connected or not
        seen={}  
        level=0  
        nextlevel=[v]
        while nextlevel:
            thislevel=nextlevel 
            nextlevel=[] 
            for v in thislevel:
                if v not in seen: 
                    seen[v]=level 
                    nb = [i for (i,j) in zip(range(len(self.__A[v])), self.__A[v]) if j!=0]
                    nextlevel.extend(nb)
            #if (cutoff is not None and cutoff <= level):  break
            level=level+1
        return seen
        
        
        
    def is_connected(self):
        """ Return True/False depends on the graph is connected or not """ 
        if self.__Order == 0: return False
        
        if not self.__Check_connectedness : return True
        
        if self.__Is_connected is None:
            # we take vertex 0 and check whether we can reach all other vertices 
            self.__Is_connected = len(self.distances_from_vertex(0)) == self.order()
        return self.__Is_connected
        
        
            
    #
    #
    # Graph spectra
    #
    #
    
    def spectrum(self, matrix="adjacency"):
        r""" Spectrum of the graph
    
        args:
            matrix (str or matrix)
                'adjacency'             or 'A' : default
                'laplacian'             or 'L'
                'distance'              or 'D'
                'signless_laplacian'    or 'Q'
                'normalized_laplacian'  or 'NL'
                'resistance_distance'   or 'RD'
                'reciprocal_distance'

                arbitrary matrix
                
        """
        
        from numpy import linalg as la
        
        if type(matrix) is str:
        
            if self.__Order == 0: return []

            if matrix == "adjacency" or matrix == "A":
                if self.__Spectrum == []:
                    s = la.eigvalsh(self.__A).tolist()
                    s.sort(reverse=True)
                    self.__Spectrum = s
                return self.__Spectrum
                    
            elif matrix == "laplacian" or matrix == "L":
                if self.__Laplacian_spectrum == []:
                    s = la.eigvalsh(self.laplacian_matrix()).tolist()
                    s.sort(reverse=True)
                    self.__Laplacian_spectrum = map(lambda x: x if x>0 else 0,s)
                return self.__Laplacian_spectrum
                
            elif matrix == "distance" or matrix == "D":
                if self.__Distance_spectrum == []:
                    s = la.eigvalsh(self.distance_matrix()).tolist()
                    s.sort(reverse=True)
                    self.__Distance_spectrum = s
                return self.__Distance_spectrum  
            
            elif matrix == "signless_laplacian" or matrix == "Q":
                if self.__Signless_laplacian_spectrum == []:
                    ## TODO: check if we have zeros in degrees()
                    s = la.eigvalsh(self.signless_laplacian_matrix()).tolist()
                    s.sort(reverse=True)
                    self.__Signless_laplacian_spectrum = map(lambda x: x if x>0 else 0,s)
                return self.__Signless_laplacian_spectrum  
    
            elif matrix == "normalized_laplacian" or matrix == "NL":
                if self.__Norm_laplacian_spectrum == []:
                    ## TODO: check if we have zeros in degrees()
                    s = la.eigvalsh(self.normalized_laplacian_matrix()).tolist()
                    s.sort(reverse=True)
                    self.__Norm_laplacian_spectrum = s
                return self.__Norm_laplacian_spectrum  
    
            elif matrix == "resistance_distance" or matrix == "RD":
                if self.__RD_spectrum == []:
                    s = la.eigvalsh(self.resistance_distance_matrix()).tolist()
                    s.sort(reverse=True)
                    self.__RD_spectrum = s
                return self.__RD_spectrum
            # NO CACHE
            elif matrix == "reciprocal_distance" :
                s = la.eigvalsh(self.reciprocal_distance_matrix()).tolist()
                s.sort(reverse=True)
                return s
            else:
                return False 
                
        # if the parameter is an arbitrary matrix            
        # DEPRECATED:
        # use mathchem.spectrum(matrix) for arbitrary matrices
        # 
        else:
            s = la.eigvalsh(matrix).tolist()
            s.sort(reverse=True)
            return s
    
    # for arbitrary matrices use:
    # mathchem.spectral_moment(matrix)
    def spectral_moment(self, k, matrix="adjacency"):
        """ Return k-th spectral moment
        
        parameters: matrix - see spectrum help
        """
        return np.power(self.spectrum(matrix),k).tolist()
        
    # for arbitrary matrices use:
    # mathchem.spectral_radius(matrix)        
    def spectral_radius(self, matrix="adjacency"):
        s = self.spectrum(matrix)
        return max(abs(s[0]), abs(s[len(s)-1]))
        
    
    # for arbitrary matrices use:
    # mathchem.energy(matrix)    
    def energy(self, matrix="adjacency"):
        """ Return energy of the graph 
        
        parameters: matrix - see spectrum help
        """
        return np.float64(np.sum( map( lambda x: abs(x) ,self.spectrum(matrix)), dtype=np.float128))
                
                
    def incidence_energy(self):
        """ Return incidence energy (IE)
            
        Incidence energy is the sum of singular values of incidence matrix
        """
        if self.__Order == 0: return []
        from numpy.linalg import svd
        return np.float64(np.sum(svd(self.incidence_matrix(), compute_uv=False), dtype=np.float128))

    #
    #
    # Chemical indices
    #
    #
    
    def zagreb_m1_index(self):
        """ Zagreb M1 Index """    
        return sum(map(lambda d: d**2, self.degrees()))
        
    
    def zagreb_m2_index(self):
        """ Zagreb M2 Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Zagreb M2 Index is a special case of Connectivity Index with power = 1"""
        return sum( map(lambda (e1, e2): self.degrees()[e1]*self.degrees()[e2] , self.edges()) )    

    
    def connectivity_index(self, power):
        """ Connectivity index (R)"""
        E = self.edges() # E - all edges
        if len(E) == 0: return 0
        return np.float64(np.sum( map(lambda (e1 ,e2): ( self.degrees()[e1]*self.degrees()[e2] ) ** power , E) , dtype=np.float128))

    augmented_zagreb_index = connectivity_index

    def sum_connectivity_index(self):
        """ Sum-Connectivity index"""
        E = self.edges() # E - all edges
        if len(E) == 0: return 0
        return np.float64(np.sum( map(lambda (e1 ,e2): ( self.degrees()[e1]+self.degrees()[e2] ) ** (-0.5) , E) , dtype=np.float128)) 
        
    def geometric_arithmetic_index(self):
        """ Geometric-Arithmetic index"""
        E = self.edges() # E - all edges
        if len(E) == 0: return 0
        return np.float64(np.sum( map(lambda (e1 ,e2): 2.0*np.sqrt(self.degrees()[e1]*self.degrees()[e2] ) / (self.degrees()[e1]+self.degrees()[e2])  , E) , dtype=np.float128)) 
           
    def eccentric_connectivity_index(self):
        """ Eccentric Connectivity Index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return sum( map( lambda a,b: a*b, self.degrees(), self.eccentricity() ) )
        
    
    def randic_index(self):
        """ Randic Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Randic Index is a special case of Connectivity Index with power = -1/2"""
        return self.connectivity_index(-0.5)
                        
    ### refactor it!
    def atom_bond_connectivity_index(self):
        """ Atom-Bond Connectivity Index (ABC) """
        s = np.float128(0) # summator
        for (u,v) in self.edges():
            d1 = np.float64(self.degrees()[u])
            d2 = np.float64(self.degrees()[v])
            s += np.float128( ( (d1 + d2 - 2 ) / (d1 * d2)) ** .5 )
        return np.float64(s)
    
    
    def estrada_index(self, matrix = "adjacency"):
        """ Estrada Index (EE)  
        
        args:
            matrix -- see spectrum for help, default value is 'adjacency'
            
        There is an alias 'distance_estrada_index' for distance matrix
        """
        return np.float64(np.sum( map( lambda x: np.exp( x.real ) , self.spectrum(matrix) ) ,dtype=np.float128 )) 
        
        
    def distance_estrada_index(self):
        """ Distance Estrada Index (DEE) 
        
        Special case of Estrada index with distance matrix
        """
        return self.estrada_index('distance')
    
    
    
    def degree_distance(self):
        """ Degree Distance (DD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False      
        dd = np.matrix(self.degrees()) * self.distance_matrix().sum(axis=1)
        return dd[0,0]
        
    def reverse_degree_distance(self):
        """ Reverse Distance Degree (rDD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return 2*( self.order()-1 ) * len(self.edges()) * self.diameter() - self.degree_distance()
    
    
    def molecular_topological_index(self):
        """ (Schultz) Molecular Topological Index (MTI)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        # (A+D)*d

        A = np.matrix(self.__A)
        d = np.matrix(self.degrees())
        return np.float64(( (A + self.distance_matrix()) * d.T ).sum(dtype=np.float128))
    
        
    def eccentric_distance_sum(self):
        """ Distance Sum
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return (self.eccentricity() * self.distance_matrix().sum(axis=1))[0,0]
    
    
    # strange - it is slow ((
    def balaban_j_index(self):
        """ Balaban J index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        ds = self.distance_matrix().sum(axis=1)
        m = len(self.edges())
        k = (m / ( m - self.__Order +2.0 ))
        return np.float64(k * np.sum( map(lambda (u ,v): 1 / np.sqrt((ds[u][0,0]*ds[v][0,0])), self.edges() ), dtype=np.float128))
        
    def sum_balaban_index(self):
        """ Sum Balaban index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        ds = self.distance_matrix().sum(axis=1)
        m = len(self.edges())
        k = (m / ( m - self.__Order +2.0 ))
        return np.float64(k * np.sum( map(lambda (u ,v): 1 / np.sqrt((ds[u][0,0]+ds[v][0,0])), self.edges() ), dtype=np.float128))
    
        
    def kirchhoff_index(self):
        """ Kirchhoff Index (Kf)
        
        Kf = 1/2 * sum_i sum_j RD[i,j]
        Based on resistance distance matrix RD
        
        Alias: resistance
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return np.float64(self.resistance_distance_matrix().sum(dtype=np.float128) / 2)
        
    resistance = kirchhoff_index
    
    def wiener_index(self):
        """ Wiener Index (W)
        
        W = 1/2 * sum_i sum_j D[i,j]
        where D is distance matrix
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return self.distance_matrix().sum(dtype=np.float64) / 2
        
    def terminal_wiener_index(self):
        """ Calculate Terminal Wiener Index (TW)
        
        TW = Sum of all distances between pendent vertices (with degree = 1)
        """
        if not self.is_connected(): return False
        s = 0
        for u in range(self.order()):
            if self.degrees()[u] != 1: continue
            for v in range(u+1, self.order()):
                if self.degrees()[v] == 1:
                    s = s + self.distance_matrix()[u,v]
        return s

    def reverse_wiener_index(self):
        """ Reverse Wiener Index (RW)
        
        RW = 1/2 * sum_i!=j ( d - D[i,j] )
        where D is distance matrix and d is diameter
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        # here we use formula: RW = 1/2 * n * (n-1) * d - W
        return  self.diameter() * (self.__Order * (self.__Order - 1)) / 2 - self.wiener_index()
        
    def hyper_wiener_index(self):
        """ Hyper-Wiener Index (WW)
        
        WW = 1/2 * ( sum_ij d(i,j)^2 + sum_i_j d(i,j) )
        where D is distance matrix

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        return ( np.power(self.distance_matrix(),2).sum() + self.distance_matrix().sum() ) / 4 # since we have symmetric matrix
        
        
    def harary_index(self):
        """ Harary Index (H)
        
        H = sum_i sum_j Rd[i,j]
        where Rd is reciprocal distance matrix 
        Rd[i,j] = 1 / D[i,j] for D[i,j] != 0
        Rd[i,j] = 0 otherwise

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        return np.float64(self.reciprocal_distance_matrix().sum(dtype=np.float128))
        
    def LEL(self):
        """ Return Laplacian-like energy (LEL) """
        return np.float64(np.sum( map( lambda x: np.sqrt(x) ,self.spectrum('laplacian')), dtype=np.float128))

    def multiplicative_sum_zagreb_index(self):
        """ Log( Multiplicative Sum Zagreb index )""" 
        d = self.degrees()
        return np.float64(np.sum( map( lambda (u,v): np.log(np.float64(d[u]+d[v])), self.edges()) , dtype=np.float128))
        
    def multiplicative_p2_zagreb_index(self):
        """Calculates Log( Multiplicative P2 Zagreb index )""" 
        d = self.degrees()
        return np.float64(np.sum( map( lambda (u,v): np.log(np.float64(d[u]*d[v])), self.edges()) , dtype=np.float128))
    
    def multiplicative_p1_zagreb_index(self):
        """Calculates Log( Multiplicative P1 Zagreb index )""" 
        d = self.degrees()
        return np.float64(np.sum( map( lambda v: np.log(np.float64(d[v]**2)), self.vertices()) , dtype=np.float128))
        
        
    # Adriatic indices

    
    # DEPRECATED
    # use mathchem.all_adriatic()
    
    def all_adriatic(self):
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
        
    def adriatic_name(self,p,i,j,a):
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
        
        
    def _adriatic_entry_(self,du,dv,i,j,a):
        """ Return an individual edge contribution for Adriatic indices and matrices"""
        # phi(x,a)
        phi = {1: lambda x,a: np.log(x)**a, 2: lambda x,a: x**a, 3: lambda x,a: a**x}
        # gamma (x,y)
        gamma = {\
        1: lambda x,y: x*y,\
        2: lambda x,y: x+y,\
        3: lambda x,y: 0 if x+y==0 else 1.0/(x+y),\
        4: lambda x,y: abs(x-y),\
        5: lambda x,y: 0 if x==y else 1.0/abs(x-y),\
        6: lambda x,y: 0 if max(x,y)==0 else min(x,y)/max(x,y),\
        7: lambda x,y: 0 if min(x,y)==0 else max(x,y)/min(x,y),\
        8: lambda x,y: 0 if x==0 or y==0 else x/y+y/x}
        
        return gamma[j](phi[i](du,a), phi[i](dv,a))
        
        
    def adriatic_matrix(self,p,i,j,a):
        """ Return the Adriatic matrix with given parameters"""
        
        if p==0: d = self.degrees()
        else: d = self.distance_matrix().sum(axis=0).tolist()[0]
        
        AM = [[0] * self.order() for k in range(self.order())]
        
        for (u,v) in self.edges():
            AM[u][v] = AM[v][u] = self._adriatic_entry_(np.float64(d[u]), np.float64(d[v]), i,j,a)
        
        return AM
    
    def adriatic_index(self,p,i,j,a):
        """ Return the Adriatic index with given parameters"""

        if p==0: d = self.degrees()
        else: d = self.distance_matrix().sum(axis=0).tolist()[0]
        
        func  = lambda (u, v) : self._adriatic_entry_(np.float64(d[u]), np.float64(d[v]), i,j,a)
        return np.float64(np.sum( map( func, self.edges()) , dtype=np.float128))
    
    # Adriatic indices by names
    
    def randic_type_lordeg_index(self):
        """ Adriatic index: Randic type lordeg index"""
        return self.adriatic_index(0, 1, 1, 0.5)

    def randic_type_lodeg_index(self):
        """ Adriatic index: Randic type lodeg index"""
        return self.adriatic_index(0, 1, 1, 1)

    def randic_type_losdeg_index(self):
        """ Adriatic index: Randic type losdeg index"""
        return self.adriatic_index(0, 1, 1, 2)

    def sum_lordeg_index(self):
        """ Adriatic index: sum lordeg index"""
        return self.adriatic_index(0, 1, 2, 0.5)

    def sum_lodeg_index(self):
        """ Adriatic index: sum lodeg index"""
        return self.adriatic_index(0, 1, 2, 1)

    def sum_losdeg_index(self):
        """ Adriatic index: sum losdeg index"""
        return self.adriatic_index(0, 1, 2, 2)

    def inverse_sum_lordeg_index(self):
        """ Adriatic index: inverse sum lordeg index"""
        return self.adriatic_index(0, 1, 3, 0.5)

    def inverse_sum_lodeg_index(self):
        """ Adriatic index: inverse sum lodeg index"""
        return self.adriatic_index(0, 1, 3, 1)

    def inverse_sum_losdeg_index(self):
        """ Adriatic index: inverse sum losdeg index"""
        return self.adriatic_index(0, 1, 3, 2)

    def misbalance_lordeg_index(self):
        """ Adriatic index: misbalance lordeg index"""
        return self.adriatic_index(0, 1, 4, 0.5)

    def misbalance_lodeg_index(self):
        """ Adriatic index: misbalance lodeg index"""
        return self.adriatic_index(0, 1, 4, 1)

    def misbalance_losdeg_index(self):
        """ Adriatic index: misbalance losdeg index"""
        return self.adriatic_index(0, 1, 4, 2)

    def inverse_misbalance_lordeg_index(self):
        """ Adriatic index: inverse misbalance lordeg index"""
        return self.adriatic_index(0, 1, 5, 0.5)

    def inverse_misbalance_lodeg_index(self):
        """ Adriatic index: inverse misbalance lodeg index"""
        return self.adriatic_index(0, 1, 5, 1)

    def inverse_misbalance_losdeg_index(self):
        """ Adriatic index: inverse misbalance losdeg index"""
        return self.adriatic_index(0, 1, 5, 2)

    def min_max_lordeg_index(self):
        """ Adriatic index: min-max lordeg index"""
        return self.adriatic_index(0, 1, 6, 0.5)

    def min_max_lodeg_index(self):
        """ Adriatic index: min-max lodeg index"""
        return self.adriatic_index(0, 1, 6, 1)

    def min_max_losdeg_index(self):
        """ Adriatic index: min-max losdeg index"""
        return self.adriatic_index(0, 1, 6, 2)

    def max_min_lordeg_index(self):
        """ Adriatic index: max-min lordeg index"""
        return self.adriatic_index(0, 1, 7, 0.5)

    def max_min_lodeg_index(self):
        """ Adriatic index: max-min lodeg index"""
        return self.adriatic_index(0, 1, 7, 1)

    def max_min_losdeg_index(self):
        """ Adriatic index: max-min losdeg index"""
        return self.adriatic_index(0, 1, 7, 2)

    def symmetric_division_lordeg_index(self):
        """ Adriatic index: symmetric division lordeg index"""
        return self.adriatic_index(0, 1, 8, 0.5)

    def symmetric_division_lodeg_index(self):
        """ Adriatic index: symmetric division lodeg index"""
        return self.adriatic_index(0, 1, 8, 1)

    def symmetric_division_losdeg_index(self):
        """ Adriatic index: symmetric division losdeg index"""
        return self.adriatic_index(0, 1, 8, 2)

    def randic_type_indeg_index(self):
        """ Adriatic index: Randic type indeg index"""
        return self.adriatic_index(0, 2, 1, -1)

    def randic_type_irdeg_index(self):
        """ Adriatic index: Randic type irdeg index"""
        return self.adriatic_index(0, 2, 1, -0.5)

    def randic_type_rodeg_index(self):
        """ Adriatic index: Randic type rodeg index"""
        return self.adriatic_index(0, 2, 1, 0.5)

    def randic_type_deg_index(self):
        """ Adriatic index: Randic type deg index"""
        return self.adriatic_index(0, 2, 1, 1)

    def randic_type_sdeg_index(self):
        """ Adriatic index: Randic type sdeg index"""
        return self.adriatic_index(0, 2, 1, 2)

    def sum_indeg_index(self):
        """ Adriatic index: sum indeg index"""
        return self.adriatic_index(0, 2, 2, -1)

    def sum_irdeg_index(self):
        """ Adriatic index: sum irdeg index"""
        return self.adriatic_index(0, 2, 2, -0.5)

    def sum_rodeg_index(self):
        """ Adriatic index: sum rodeg index"""
        return self.adriatic_index(0, 2, 2, 0.5)

    def sum_deg_index(self):
        """ Adriatic index: sum deg index"""
        return self.adriatic_index(0, 2, 2, 1)

    def sum_sdeg_index(self):
        """ Adriatic index: sum sdeg index"""
        return self.adriatic_index(0, 2, 2, 2)

    def inverse_sum_indeg_index(self):
        """ Adriatic index: inverse sum indeg index"""
        return self.adriatic_index(0, 2, 3, -1)

    def inverse_sum_irdeg_index(self):
        """ Adriatic index: inverse sum irdeg index"""
        return self.adriatic_index(0, 2, 3, -0.5)

    def inverse_sum_rodeg_index(self):
        """ Adriatic index: inverse sum rodeg index"""
        return self.adriatic_index(0, 2, 3, 0.5)

    def inverse_sum_deg_index(self):
        """ Adriatic index: inverse sum deg index"""
        return self.adriatic_index(0, 2, 3, 1)

    def inverse_sum_sdeg_index(self):
        """ Adriatic index: inverse sum sdeg index"""
        return self.adriatic_index(0, 2, 3, 2)

    def misbalance_indeg_index(self):
        """ Adriatic index: misbalance indeg index"""
        return self.adriatic_index(0, 2, 4, -1)

    def misbalance_irdeg_index(self):
        """ Adriatic index: misbalance irdeg index"""
        return self.adriatic_index(0, 2, 4, -0.5)

    def misbalance_rodeg_index(self):
        """ Adriatic index: misbalance rodeg index"""
        return self.adriatic_index(0, 2, 4, 0.5)

    def misbalance_deg_index(self):
        """ Adriatic index: misbalance deg index"""
        return self.adriatic_index(0, 2, 4, 1)

    def misbalance_sdeg_index(self):
        """ Adriatic index: misbalance sdeg index"""
        return self.adriatic_index(0, 2, 4, 2)

    def inverse_misbalance_indeg_index(self):
        """ Adriatic index: inverse misbalance indeg index"""
        return self.adriatic_index(0, 2, 5, -1)

    def inverse_misbalance_irdeg_index(self):
        """ Adriatic index: inverse misbalance irdeg index"""
        return self.adriatic_index(0, 2, 5, -0.5)

    def inverse_misbalance_rodeg_index(self):
        """ Adriatic index: inverse misbalance rodeg index"""
        return self.adriatic_index(0, 2, 5, 0.5)

    def inverse_misbalance_deg_index(self):
        """ Adriatic index: inverse misbalance deg index"""
        return self.adriatic_index(0, 2, 5, 1)

    def inverse_misbalance_sdeg_index(self):
        """ Adriatic index: inverse misbalance sdeg index"""
        return self.adriatic_index(0, 2, 5, 2)

    def min_max_rodeg_index(self):
        """ Adriatic index: min-max rodeg index"""
        return self.adriatic_index(0, 2, 6, 0.5)

    def min_max_deg_index(self):
        """ Adriatic index: min-max deg index"""
        return self.adriatic_index(0, 2, 6, 1)

    def min_max_sdeg_index(self):
        """ Adriatic index: min-max sdeg index"""
        return self.adriatic_index(0, 2, 6, 2)

    def max_min_rodeg_index(self):
        """ Adriatic index: max-min rodeg index"""
        return self.adriatic_index(0, 2, 7, 0.5)

    def max_min_deg_index(self):
        """ Adriatic index: max-min deg index"""
        return self.adriatic_index(0, 2, 7, 1)

    def max_min_sdeg_index(self):
        """ Adriatic index: max-min sdeg index"""
        return self.adriatic_index(0, 2, 7, 2)

    def symmetric_division_rodeg_index(self):
        """ Adriatic index: symmetric division rodeg index"""
        return self.adriatic_index(0, 2, 8, 0.5)

    def symmetric_division_deg_index(self):
        """ Adriatic index: symmetric division deg index"""
        return self.adriatic_index(0, 2, 8, 1)

    def symmetric_division_sdeg_index(self):
        """ Adriatic index: symmetric division sdeg index"""
        return self.adriatic_index(0, 2, 8, 2)

    def randic_type_hadeg_index(self):
        """ Adriatic index: Randic type hadeg index"""
        return self.adriatic_index(0, 3, 1, 0.5)

    def randic_type_twodeg_index(self):
        """ Adriatic index: Randic type twodeg index"""
        return self.adriatic_index(0, 3, 1, 2)

    def sum_hadeg_index(self):
        """ Adriatic index: sum hadeg index"""
        return self.adriatic_index(0, 3, 2, 0.5)

    def sum_twodeg_index(self):
        """ Adriatic index: sum twodeg index"""
        return self.adriatic_index(0, 3, 2, 2)

    def inverse_sum_hadeg_index(self):
        """ Adriatic index: inverse sum hadeg index"""
        return self.adriatic_index(0, 3, 3, 0.5)

    def inverse_sum_twodeg_index(self):
        """ Adriatic index: inverse sum twodeg index"""
        return self.adriatic_index(0, 3, 3, 2)

    def misbalance_hadeg_index(self):
        """ Adriatic index: misbalance hadeg index"""
        return self.adriatic_index(0, 3, 4, 0.5)

    def misbalance_twodeg_index(self):
        """ Adriatic index: misbalance twodeg index"""
        return self.adriatic_index(0, 3, 4, 2)

    def inverse_misbalance_hadeg_index(self):
        """ Adriatic index: inverse misbalance hadeg index"""
        return self.adriatic_index(0, 3, 5, 0.5)

    def inverse_misbalance_twodeg_index(self):
        """ Adriatic index: inverse misbalance twodeg index"""
        return self.adriatic_index(0, 3, 5, 2)

    def min_max_hadeg_index(self):
        """ Adriatic index: min-max hadeg index"""
        return self.adriatic_index(0, 3, 6, 0.5)

    def min_max_twodeg_index(self):
        """ Adriatic index: min-max twodeg index"""
        return self.adriatic_index(0, 3, 6, 2)

    def max_min_hadeg_index(self):
        """ Adriatic index: max-min hadeg index"""
        return self.adriatic_index(0, 3, 7, 0.5)

    def max_min_twodeg_index(self):
        """ Adriatic index: max-min twodeg index"""
        return self.adriatic_index(0, 3, 7, 2)

    def symmetric_division_hadeg_index(self):
        """ Adriatic index: symmetric division hadeg index"""
        return self.adriatic_index(0, 3, 8, 0.5)

    def symmetric_division_twodeg_index(self):
        """ Adriatic index: symmetric division twodeg index"""
        return self.adriatic_index(0, 3, 8, 2)

    def randic_type_lordi_index(self):
        """ Adriatic index: Randic type lordi index"""
        return self.adriatic_index(1, 1, 1, 0.5)

    def randic_type_lodi_index(self):
        """ Adriatic index: Randic type lodi index"""
        return self.adriatic_index(1, 1, 1, 1)

    def randic_type_losdi_index(self):
        """ Adriatic index: Randic type losdi index"""
        return self.adriatic_index(1, 1, 1, 2)

    def sum_lordi_index(self):
        """ Adriatic index: sum lordi index"""
        return self.adriatic_index(1, 1, 2, 0.5)

    def sum_lodi_index(self):
        """ Adriatic index: sum lodi index"""
        return self.adriatic_index(1, 1, 2, 1)

    def sum_losdi_index(self):
        """ Adriatic index: sum losdi index"""
        return self.adriatic_index(1, 1, 2, 2)

    def inverse_sum_lordi_index(self):
        """ Adriatic index: inverse sum lordi index"""
        return self.adriatic_index(1, 1, 3, 0.5)

    def inverse_sum_lodi_index(self):
        """ Adriatic index: inverse sum lodi index"""
        return self.adriatic_index(1, 1, 3, 1)

    def inverse_sum_losdi_index(self):
        """ Adriatic index: inverse sum losdi index"""
        return self.adriatic_index(1, 1, 3, 2)

    def misbalance_lordi_index(self):
        """ Adriatic index: misbalance lordi index"""
        return self.adriatic_index(1, 1, 4, 0.5)

    def misbalance_lodi_index(self):
        """ Adriatic index: misbalance lodi index"""
        return self.adriatic_index(1, 1, 4, 1)

    def misbalance_losdi_index(self):
        """ Adriatic index: misbalance losdi index"""
        return self.adriatic_index(1, 1, 4, 2)

    def inverse_misbalance_lordi_index(self):
        """ Adriatic index: inverse misbalance lordi index"""
        return self.adriatic_index(1, 1, 5, 0.5)

    def inverse_misbalance_lodi_index(self):
        """ Adriatic index: inverse misbalance lodi index"""
        return self.adriatic_index(1, 1, 5, 1)

    def inverse_misbalance_losdi_index(self):
        """ Adriatic index: inverse misbalance losdi index"""
        return self.adriatic_index(1, 1, 5, 2)

    def min_max_lordi_index(self):
        """ Adriatic index: min-max lordi index"""
        return self.adriatic_index(1, 1, 6, 0.5)

    def min_max_lodi_index(self):
        """ Adriatic index: min-max lodi index"""
        return self.adriatic_index(1, 1, 6, 1)

    def min_max_losdi_index(self):
        """ Adriatic index: min-max losdi index"""
        return self.adriatic_index(1, 1, 6, 2)

    def max_min_lordi_index(self):
        """ Adriatic index: max-min lordi index"""
        return self.adriatic_index(1, 1, 7, 0.5)

    def max_min_lodi_index(self):
        """ Adriatic index: max-min lodi index"""
        return self.adriatic_index(1, 1, 7, 1)

    def max_min_losdi_index(self):
        """ Adriatic index: max-min losdi index"""
        return self.adriatic_index(1, 1, 7, 2)

    def symmetric_division_lordi_index(self):
        """ Adriatic index: symmetric division lordi index"""
        return self.adriatic_index(1, 1, 8, 0.5)

    def symmetric_division_lodi_index(self):
        """ Adriatic index: symmetric division lodi index"""
        return self.adriatic_index(1, 1, 8, 1)

    def symmetric_division_losdi_index(self):
        """ Adriatic index: symmetric division losdi index"""
        return self.adriatic_index(1, 1, 8, 2)

    def randic_type_indi_index(self):
        """ Adriatic index: Randic type indi index"""
        return self.adriatic_index(1, 2, 1, -1)

    def randic_type_irdi_index(self):
        """ Adriatic index: Randic type irdi index"""
        return self.adriatic_index(1, 2, 1, -0.5)

    def randic_type_rodi_index(self):
        """ Adriatic index: Randic type rodi index"""
        return self.adriatic_index(1, 2, 1, 0.5)

    def randic_type_di_index(self):
        """ Adriatic index: Randic type di index"""
        return self.adriatic_index(1, 2, 1, 1)

    def randic_type_sdi_index(self):
        """ Adriatic index: Randic type sdi index"""
        return self.adriatic_index(1, 2, 1, 2)

    def sum_indi_index(self):
        """ Adriatic index: sum indi index"""
        return self.adriatic_index(1, 2, 2, -1)

    def sum_irdi_index(self):
        """ Adriatic index: sum irdi index"""
        return self.adriatic_index(1, 2, 2, -0.5)

    def sum_rodi_index(self):
        """ Adriatic index: sum rodi index"""
        return self.adriatic_index(1, 2, 2, 0.5)

    def sum_di_index(self):
        """ Adriatic index: sum di index"""
        return self.adriatic_index(1, 2, 2, 1)

    def sum_sdi_index(self):
        """ Adriatic index: sum sdi index"""
        return self.adriatic_index(1, 2, 2, 2)

    def inverse_sum_indi_index(self):
        """ Adriatic index: inverse sum indi index"""
        return self.adriatic_index(1, 2, 3, -1)

    def inverse_sum_irdi_index(self):
        """ Adriatic index: inverse sum irdi index"""
        return self.adriatic_index(1, 2, 3, -0.5)

    def inverse_sum_rodi_index(self):
        """ Adriatic index: inverse sum rodi index"""
        return self.adriatic_index(1, 2, 3, 0.5)

    def inverse_sum_di_index(self):
        """ Adriatic index: inverse sum di index"""
        return self.adriatic_index(1, 2, 3, 1)

    def inverse_sum_sdi_index(self):
        """ Adriatic index: inverse sum sdi index"""
        return self.adriatic_index(1, 2, 3, 2)

    def misbalance_indi_index(self):
        """ Adriatic index: misbalance indi index"""
        return self.adriatic_index(1, 2, 4, -1)

    def misbalance_irdi_index(self):
        """ Adriatic index: misbalance irdi index"""
        return self.adriatic_index(1, 2, 4, -0.5)

    def misbalance_rodi_index(self):
        """ Adriatic index: misbalance rodi index"""
        return self.adriatic_index(1, 2, 4, 0.5)

    def misbalance_di_index(self):
        """ Adriatic index: misbalance di index"""
        return self.adriatic_index(1, 2, 4, 1)

    def misbalance_sdi_index(self):
        """ Adriatic index: misbalance sdi index"""
        return self.adriatic_index(1, 2, 4, 2)

    def inverse_misbalance_indi_index(self):
        """ Adriatic index: inverse misbalance indi index"""
        return self.adriatic_index(1, 2, 5, -1)

    def inverse_misbalance_irdi_index(self):
        """ Adriatic index: inverse misbalance irdi index"""
        return self.adriatic_index(1, 2, 5, -0.5)

    def inverse_misbalance_rodi_index(self):
        """ Adriatic index: inverse misbalance rodi index"""
        return self.adriatic_index(1, 2, 5, 0.5)

    def inverse_misbalance_di_index(self):
        """ Adriatic index: inverse misbalance di index"""
        return self.adriatic_index(1, 2, 5, 1)

    def inverse_misbalance_sdi_index(self):
        """ Adriatic index: inverse misbalance sdi index"""
        return self.adriatic_index(1, 2, 5, 2)

    def min_max_rodi_index(self):
        """ Adriatic index: min-max rodi index"""
        return self.adriatic_index(1, 2, 6, 0.5)

    def min_max_di_index(self):
        """ Adriatic index: min-max di index"""
        return self.adriatic_index(1, 2, 6, 1)

    def min_max_sdi_index(self):
        """ Adriatic index: min-max sdi index"""
        return self.adriatic_index(1, 2, 6, 2)

    def max_min_rodi_index(self):
        """ Adriatic index: max-min rodi index"""
        return self.adriatic_index(1, 2, 7, 0.5)

    def max_min_di_index(self):
        """ Adriatic index: max-min di index"""
        return self.adriatic_index(1, 2, 7, 1)

    def max_min_sdi_index(self):
        """ Adriatic index: max-min sdi index"""
        return self.adriatic_index(1, 2, 7, 2)

    def symmetric_division_rodi_index(self):
        """ Adriatic index: symmetric division rodi index"""
        return self.adriatic_index(1, 2, 8, 0.5)

    def symmetric_division_di_index(self):
        """ Adriatic index: symmetric division di index"""
        return self.adriatic_index(1, 2, 8, 1)

    def symmetric_division_sdi_index(self):
        """ Adriatic index: symmetric division sdi index"""
        return self.adriatic_index(1, 2, 8, 2)

    def randic_type_hadi_index(self):
        """ Adriatic index: Randic type hadi index"""
        return self.adriatic_index(1, 3, 1, 0.5)

    def randic_type_twodi_index(self):
        """ Adriatic index: Randic type twodi index"""
        return self.adriatic_index(1, 3, 1, 2)

    def sum_hadi_index(self):
        """ Adriatic index: sum hadi index"""
        return self.adriatic_index(1, 3, 2, 0.5)

    def sum_twodi_index(self):
        """ Adriatic index: sum twodi index"""
        return self.adriatic_index(1, 3, 2, 2)

    def inverse_sum_hadi_index(self):
        """ Adriatic index: inverse sum hadi index"""
        return self.adriatic_index(1, 3, 3, 0.5)

    def inverse_sum_twodi_index(self):
        """ Adriatic index: inverse sum twodi index"""
        return self.adriatic_index(1, 3, 3, 2)

    def misbalance_hadi_index(self):
        """ Adriatic index: misbalance hadi index"""
        return self.adriatic_index(1, 3, 4, 0.5)

    def misbalance_twodi_index(self):
        """ Adriatic index: misbalance twodi index"""
        return self.adriatic_index(1, 3, 4, 2)

    def inverse_misbalance_hadi_index(self):
        """ Adriatic index: inverse misbalance hadi index"""
        return self.adriatic_index(1, 3, 5, 0.5)

    def inverse_misbalance_twodi_index(self):
        """ Adriatic index: inverse misbalance twodi index"""
        return self.adriatic_index(1, 3, 5, 2)

    def min_max_hadi_index(self):
        """ Adriatic index: min-max hadi index"""
        return self.adriatic_index(1, 3, 6, 0.5)

    def min_max_twodi_index(self):
        """ Adriatic index: min-max twodi index"""
        return self.adriatic_index(1, 3, 6, 2)

    def max_min_hadi_index(self):
        """ Adriatic index: max-min hadi index"""
        return self.adriatic_index(1, 3, 7, 0.5)

    def max_min_twodi_index(self):
        """ Adriatic index: max-min twodi index"""
        return self.adriatic_index(1, 3, 7, 2)

    def symmetric_division_hadi_index(self):
        """ Adriatic index: symmetric division hadi index"""
        return self.adriatic_index(1, 3, 8, 0.5)

    def symmetric_division_twodi_index(self):
        """ Adriatic index: symmetric division twodi index"""
        return self.adriatic_index(1, 3, 8, 2)

    
