#!/usr/bin/env python
#encoding: utf-8
"""
@author: Liam Deacon

@contact: liam.m.deacon@gmail.com

@copyright: Copyright (C) 2013 Liam Deacon

@license: MIT License (see LICENSE file for details)

@summary: Provides convenience functions for generating input and calculating 
          atomic charge densities for use with the Barbieri/Van Hove phase 
          shift calculation package.

@see: http://www.icts.hkbu.edu.hk/surfstructinfo/SurfStrucInfo_files/leed/leedpack.html

@requires: f2py (for libphsh fortran wrapper generation) 

@note: to generate libphsh fortran wrappers (libphsh.pyd) for your platform
       then use 'python setup.py' in the lib directory of this package   
"""

import elements

class Atom(object):
    '''
    Atom class for input into cluster model for muffin-tin potential
    calculations.
    '''
    def __init__(self, element, coordinates, **kwargs):
        '''
        Constructor for Atom class.
        
        Parameters
        ----------
        element : str or int
            This is either the elemental symbol, name or atomic number.
        coordinates : list[float, float, float] or ndarray
            The fractional coordinates within the unitcell in terms of the
            basis vector a.
        tag : str, optional
            Add a name tag to this element (useful if dealing with multiple
            atoms of the same element in a given model). Default is the
            symbol for that element - numeric ids may be appended in the model
            class.
        radius : float, optional
            The muffin-tin radius of the atom in Angstroms (default is to 
            lookup 'atmrad' in the element dictionary).
        valence : int, optional
            The valency of the atom (default is to assume neutral atom).
        
        
        '''
        self.element = elements.ELEMENTS[element]
        self.set_coordinates(coordinates)
        self.name = self.element.name.title()
        self.tag = self.element.symbol.upper()
        self.Z = self.element.protons
        self.radius = self.element.atmrad
        self.valence = 0
        self.__dict__.update(kwargs)
 
            
    # set coordinates of atom within unitcell in terms of a
    def set_coordinates(self, coordinates):
        try:
            self.coordinates = coordinates
            self._coordinates = [r/0.529 for r in coordinates]
        except any as e:
            raise e
    
    # set valence of atom
    def set_valence(self, valency):
        self.valence = int(valency)
        
    # set muffin-tin radius of atom 
    def set_mufftin_radius(self, radius):
        """
        Description
        -----------
        Set the muffin-tin radius of the atom in Angstroms.
        """
        try:
            self.radius = float(radius)
            self._radius = self.radius/0.529 #in Bohr radii
        except:
            pass
        

class Unitcell(object):
    '''
    Unitcell class        
    '''
    def __init__(self, a, c, matrix_3x3, **kwargs):
        '''
        Constructor for the Unitcell class
        
        Parameters
        ----------
        a : float
            The in-plane lattice vector in Angstroms
        c : float
            The out-of-plane lattice vector in Angstroms. For cubic systems this
            will be equal to a.
        matrix_3x3: ndarray
            A 3x3 matrix describing the x,y,z construction of a,b,c basis vectors
            of the unitcell. Units for x, y & z should be in terms of fractional
            coordinates. 
        alpha : float, optional
            Angle alpha in degrees.
        beta : float, optional
            Angle beta in degrees.
        gamma : float, optional
            Angle gamma in degrees.

        '''
        # Convert Angstrom input to Bohr radii
        self.set_a(a)
        self.set_c(c)
        
        # Set basis vectors
        self.set_vectors(matrix_3x3)
        
        # Set xstal system
        self.alpha = 90.0
        self.beta = 90.0
        self.gamma = 90.0
        
        # Update additional information
        self.__dict__.update(kwargs)
        

    # set basis vectors from (3x3) matrix in fractional coordinates
    def set_vectors(self, m3x3):
        self.basis = m3x3
    
    # set a lattice parameter
    def set_a(self, a):
        """
        Description
        -----------
        Set the magnitude of the in-plane lattice vector a in Angstroms.
        
        Parameters
        ----------
        a: float
            The magnitude of the in-plane lattice vector in Angstroms  
        
        Notes
        -----
        To retrieve a in terms of Angstroms use 'unitcell.a', whereas the
        internal parameter 'unitcell._a' converts a into Bohr radii 
        (1 Bohr = 0.529Å), which is used for the muffin-tin potential
        calculations in libphsh (CAVPOT subroutine)  
        
        """
        self.a = float(a)
        self._a = self.a/0.529 #(1 Bohr = 0.529Å)    
        
    
    # set c lattice parameter
    def set_c(self, c):
        """
        Description
        -----------
        Set the magnitude of the out-of-plane lattice vector a. 
        
        Arguments
        ---------
        c : float
            The magnitude of the in-plane lattice vector in Angstroms 
        
        Notes
        -----
        To retrieve c in terms of Angstroms use 'unitcell.c', whereas the
        internal parameter 'unitcell._c' converts c into Bohr radii 
        (1 Bohr = 0.529Å), which is used for the muffin-tin potential
        calculations in libphsh (CAVPOT subroutine)   
        """
        self.c = float(c)
        self._c = self.c/0.529 #(1 Bohr = 0.529Å)   

        
    # set angle alpha in degrees 
    def set_alpha(self, alpha):
        self.alpha = float(alpha) % 360.0


    # set angle beta in degrees
    def set_beta(self, beta):
        self.beta = float(beta) % 360.0
    
    
    # set angle gamma in degrees
    def set_gamma(self, gamma):
        self.gamma = float(gamma) % 360.0
        
        
class Model(object):
    '''
    Generic model class.
    '''
    def __init__(self, unitcell, atoms, **kwargs):
        '''
        Constructor for Model class.
        
        Parameters
        ----------
        unitcell : Unitcell
            An instance of the Unitcell class.
        atoms : list
            Array of Atom class instances which constitute the model. 
            
        '''
        self.atoms = []
        self.set_atoms(atoms)
        self.set_unitcell(unitcell)
        self.__dict__.update(kwargs)
        
        
    def add_atom(self, element, position):
        """
        Append an Atom instance to the model
        
        Parameters
        ----------
        element : str or int
            Either an element name, symbol or atomic number.
        position : list(float) or ndarray
            (1x3) array of the fractional coordinates of the atom
            within the unitcell in terms of the lattice vector a.
        """
        self.atoms.append(Atom(element, position))
                
    
    def set_atoms(self, atoms):
        """
        Set the atoms for the model.
        
        Parameters
        ----------
        atoms : list(Atoms)
            Array of Atom instances. Entries in the list which are
            not of type Atom will be ignored.
              
        Raises
        ------
        TypeError if atoms parameter is not a list.
        """
        if isinstance(atoms, list):
            self.atoms = [atom for atom in atoms if isinstance(atom, Atom)]
        else:
            raise TypeError
    
    def set_unitcell(self, unitcell):
        """
        Set the unitcell for the model
        
        Parameters
        ----------
        unitcell : Unitcell
            Instance of Unitcell class to set to model.
            
        Raises
        ------
        TypeError if unitcell parameter is not a Unitcell.
        
        """
        if isinstance(unitcell, Unitcell):
            self.unitcell = unitcell
        else:
            raise TypeError
    
   
class MTZ_model(Model):
    '''
    Muffin-tin potential Model subclass for producing input file 
    for muffin-tin calculations in the Barbieri/Van Hove phase 
    shift calculation package.
    '''
    def __init__(self, unitcell, atoms, **kwargs):
        '''
        Constructor for Model class.
        
        Parameters
        ----------
        unitcell : Unitcell
            An instance of the Unitcell class.
        atoms : list
            Array of Atom class instances which constitute the model.
        nh : int, optional
            Parameter for estimating the muffin-tin zero (default: 10).
        exchange : float, optional
            Hartree type exchange term alpha (default: 0.7200). 
        c : float, optional
            The height of the slab in Angstroms - if this is much larger 
            than the bulk c distance then there will be a large vacuum 
            and therefore should be used when calculating a thin slab 
            rather than a bulk muffin-tin potential. Default is to lookup
            the out-of-plane basis vector bulk value.  
        nform : int or str, optional
            The phase shift calculation type, which can be 0 or 'cav' for
            using the cavpot subroutine, 1 or 'wil' for using the William's
            method, and 2 or 'rel' for using relativistic calculations suitable
            for the CLEED package.    
            
        '''
        self.atoms = []
        self.set_atoms(atoms)
        self.set_unitcell(unitcell)
        self.set_exchange(0.72)
        self.set_nh(10)
        self.__dict__.update(kwargs)
        

    # set the nh muffin-tin zero estimation parameter
    def set_nh(self, nh):
        self.nh = int(nh) #check this is not float 
    
    
    # set the alpha exchange term for muffin-tin calculation
    def set_exchange(self, alpha):
        try:
            self.exchange = float(alpha)
        except:
            pass
    
    
    # set form of muffin-tin calculation: 0=cav, 1=wil, 2=rel
    def set_nform(self, nform):
        if isinstance(int, nform):
            if nform >=0 and nform <= 2:
                self.nform = nform
        elif isinstance(str, nform):
            if nform == 'cav':
                self.nform = 0
            elif nform == 'wil':
                self.nform = 1
            elif nform == 'rel':
                self.nform = 2
        else:
            raise TypeError
        
        
    def set_slab_c(self, c):
        """
        Description
        -----------
        Set the maximum height of the slab in Angstroms - if this is 
        much larger than the bulk c distance then there will be a large 
        vacuum and therefore should be used when calculating a thin slab 
        rather than a bulk muffin-tin potential.
        
        Examples
        --------
        For Re the bulk c distance is 2.76Å, whereas a possible slab c distance
        could be ~10Å.
        
        """
        try:
            self.c = float(c)
            self._c = self.c/0.529
        except:
            pass
        
        
    def gen_input(self, **kwargs):
        """
        Description
        -----------
        Generate input file for use in the Barbieri/Van Hove phase shift 
        calculation package (phsh1 or libphsh)
        
        Arguments
        ---------
        bulk : bool
            If True the c value is set to the bulk value...
        filename : str
            The path of the generated file.
        header : str
            A file header string. 
        """
        
        # get file header - should be single line (force if not)
        if 'header' in kwargs:
            header = kwargs.pop('header').replace('\n',' ').replace('\r', '')
        else:
            header = "MTZ cluster input file"
        
        if 'bulk' in kwargs:
            if kwargs.get('bulk'):
                id = '_bulk'
            else:
                id = '_slab'
        else:
            id = ''
            
        if 'nform' in kwargs:
            self.set_nform(kwargs.get('nform'))
        else:
            self.nform = 2 #rel 
    
        if 'exchange' in kwargs:
            self.set_exchange(kwargs.get('exchange'))
        elif not isinstance(self.exchange, float):
            self.set_exchange(0.72)
    
        if 'nh' in kwargs:
            self.set_nh(kwargs.get('nh'))
        elif not isinstance(self.nh, int):
            self.set_nh(10)
    
        # get filename or make educated guess
        if 'filename' in kwargs:
            filename = kwargs.get('filename')
        else:
            filename = 'cluster{0}.i'.format(id)
        
        # auto-generate file
        with open(filename, 'w') as f:
            f.write(header+'\n')
            f.write(str(" %7.4f" % self.unitcell._a).ljust(33) + 
                    '# a lattice parameter distance in Bohr radii\n')
            f.write(str(" %7.4f %7.4f %7.4f" %(self.unitcell.basis[0][0],
                                                self.unitcell.basis[0][1],
                                                self.unitcell.basis[0][2])
                        ).ljust(33) + '# SPA coordinates of unit cell\n')
            f.write(str(" %7.4f %7.4f %7.4f" %(self.unitcell.basis[1][0],
                                                self.unitcell.basis[1][1],
                                                self.unitcell.basis[1][2])
                        ).ljust(33) + '\n')
            f.write(str(" %7.4f %7.4f %7.4f" %(self.unitcell.basis[2][0],
                                                self.unitcell.basis[2][1],
                                                self.unitcell.basis[2][2])
                        ).ljust(33) + 
                        '# Notice the value %.2f (%s calculation)\n' %(
                            self.unitcell.basis[2][2], 
                            id.replace('_', '')))
            nineq_atoms = 3
            f.write(str("%4i" %nineq_atoms).ljust(33) 
                    + '# number of ineq. atoms in this file (NINEQ)\n')
            tags = []
            for atom in self.atoms:
                while atom.tag in tags:
                    number = "".join([ch for ch in atom.tag if ch.isdigit()])
                    try:
                        number = int(number)
                        number += 1
                    except ValueError:
                        number = 1
                    atom.tag = ("".join([ch for ch in atom.tag if ch.isalpha()])
                             + str(number))
                    
                tags.append(atom.tag)
                f.write("{0} {1}".format(atom.element.name.capitalize(), 
                        atom.tag).ljust(33) + '# element, name tag\n')
                f.write(str("%4i %7.4f %7.4f %7.4f" %(1, atom.Z,
                        atom.valence, atom.radius/0.529)).ljust(33) + 
                        '# atoms in unit cell, Z, valence, '
                        'Muffin-tin radius (Bohr radii)\n')
                f.write(str(" %7.4f %7.4f %7.4f" %(atom.coordinates[0],
                                                   atom.coordinates[1],
                                                   atom.coordinates[2])
                        ).ljust(33) + '# coordinates in SPA units\n')
            f.write(str("%4i" %self.nform).ljust(33) + 
                    '# nform=2|1|0 (for rel will or cav)\n')
            f.write(str(" %7.4f" %self.exchange).ljust(33) + 
                    '# alpha (for Hartree type exchange term)\n')
            f.write(str("%4i" %self.nh).ljust(33) + 
                    '# nh (for estimating muffin-tin zero\n')


       
at = Atom('C', [0, 0, 0])
uc = Unitcell(1, 2, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
mtz = MTZ_model(uc, [at])
mtz.gen_input(filename='C:\\Users\\Liam\\Desktop\\cluster1.i')
