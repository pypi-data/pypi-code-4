from numpy.linalg import solve, norm
import time
import copy
from collections import defaultdict

from django.db import models

from element import *
from qmpy.utils import *
from qmpy.analysis.symmetry import WyckoffSite

class AtomError(Exception):
    '''Atom related problem'''

class SiteError(Exception):
    '''Site related problem'''

class Site(models.Model):
    '''
    Model for a lattice site. 

    Database Attributes:
        structure   : Structure object the site is associated with
        x, y, z     : fractional coordinates of the site (float)
        wyckoff     : WyckoffSite the site is on
        atom_set    : QuerySet of atoms on the site

    Convenience Attributes:
        coord       : equivalent to [x, y, z]
        atoms       : list of Atoms on the site
    '''
    structure = models.ForeignKey('Structure', blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'sites'

    # builtins
    def __str__(self):
        if len(self.atoms) == 1:
            return self.atoms[0].element_id
        elif len(self.atoms) > 1:
            elts = [ str(a.element) for a in self.atoms ]
            specs = [ str(a.species) for a in self.atoms ]
            if len(set(elts)) == len(set(specs)):
                return '('+','.join(elts)+')'
            else:
                return '('+','.join(specs)+')'
        else:
            return 'No atom found'

    # django overrides
    def save(self, *args, **kwargs):
        self.structure = self.structure
        for a in self.atoms:
            a.structure = self.structure
            a.site = self
        super(Site, self).save(*args, **kwargs)
        self.atom_set = self.atoms

    _atoms = None
    @property
    def atoms(self):
        if self._atoms is None:
            if self.id is None:
                self._atoms = []
            else:
                self._atoms = list(self.atom_set.all())
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        if isinstance(atoms, Atom):
            self._atoms = [atoms]
        elif all([ isinstance(a, Atom) for a in atoms ]):
            self._atoms = atoms
        else:
            raise TypeError('atoms must be a sequence of Atoms')

    @property
    def coord(self):
        return np.array([self.x , self.y, self.z])

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = values

    @property
    def cart_coord(self):
        #if self.direct and self.structure is None:
        #    raise SiteError("No associated structure")
        #elif self.direct:
        if self.structure is None:
            raise SiteError("No associated structure")
        return np.dot(self.coord, self.structure.cell)
        #else:
        #    return self.coord

    @property
    def label(self):
        if len(self.atoms) == 1:
            return self.atoms[0].element_id

class Atom(models.Model):
    '''
    Model for an Atom. An atom is defined principally by an element and a
    coordinate, but can also have additional properties like: magnetic moment,
    volume, charge or forces.

    Database Attributes:
        structure
        site
        element
        ox

        x, y, z
        direct
        fx, fy, fz

        magmom
        charge
        volume

    Convenience Attributes:

    Methods:
    '''
    structure = models.ForeignKey('Structure', related_name='atom_set',
                                               null=True)
    site = models.ForeignKey('Site', related_name='atom_set', null=True)

    # species
    element = models.ForeignKey('Element', blank=True, null=True)
    ox = models.IntegerField(default=None, blank=True, null=True)

    # position
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    direct = models.BooleanField(default=True)

    # forces
    fx = models.FloatField(blank=True, null=True)
    fy = models.FloatField(blank=True, null=True)
    fz = models.FloatField(blank=True, null=True)

    # properties
    magmom = models.FloatField(blank=True, null=True)
    charge = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)

    # symmetry
    occupancy = models.FloatField(default=1)
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'atoms'

    # builtins
    def __str__(self):
        return '%s: %8f %8f %8f' % (self.element, 
                self.x, self.y, self.z)

    def __eq__(self, other):
        if self.element_id != other.element_id:
            return False
        if any( abs(x - y) > 1e-3 for x, y in zip(self.coord, other.coord)):
            return False
        return True

    def __cmp__(self, other):
        comp_arr = [[ self.z, other.z ],
                    [ self.y, other.y ],
                    [ self.x, other.x ],
                    [ self.ox, other.ox ],
                    [ self.element_id, other.element_id ]]
        comp_arr = np.array([ row for row in comp_arr if 
                                  all( not x is None for x in row ) ]).T
        if len(comp_arr) == 0:
            return 0
        ind = np.lexsort(comp_arr)
        return ind[0]

    # convenience attributes
    @property
    def forces(self):
        return np.array([self.fx , self.fy, self.fz])

    @forces.setter
    def forces(self, values):
        self.fx, self.fy, self.fz = values

    @property
    def coord(self):
        return np.array([self.x , self.y, self.z])

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = values

    @property
    def cart_coord(self):
        if self.direct and self.structure is None:
            raise AtomError("No associated structure")
        elif self.direct:
            return np.dot(self.coord, self.structure.cell)
        else:
            return self.coord

    @property
    def species(self):
        return format_species(self.element_id, self.ox)

    # accessor
    @classmethod
    def get(cls, element, coord, **kwargs):
        '''
        Create a new Atom object. Requires element and coordinate arguments,
        with all other attributes being optional arguments.

        Example:
        >>> Atom.get('Fe', [0,0,0])
        >>> Atom.get('Ni', [0.5, 0.5, 0.5], ox=2, magmom=5, 
        >>>                                 forces=[0.2, 0.2, 0.2],
        >>>                                 volume=101, charge=1.8,
        >>>                                 occupancy=1)
        '''
        atom = Atom()
        atom.element = element
        atom.coord = coord
        valid_keys = ['ox', 'occupancy', 'wyckoff', 'charge', 
                'magmom', 'volume', 'forces']
        for key in valid_keys:
            if key in kwargs:
                setattr(atom, key, kwargs[key])
        return atom

    def copy(self):
        '''
        Creates an exact copy of the atom, only without the matching primary
        key.

        Example:
        >>> a = Atom.get('Fe', [0,0,0])
        >>> a.save()
        >>> a.id
        1
        >>> a.copy()
        >>> a
        <Atom: Fe @ [0.000, 0.000, 0.000]>
        >>> a.id
        None
        
        '''
        atom = Atom()
        atom.element_id = self.element_id
        atom.coord = self.coord
        valid_keys = ['ox', 'occupancy', 'charge', 
                'magmom', 'volume', 'forces']
        for key in valid_keys:
            setattr(atom, key, getattr(self, key))
        return atom

    def as_site(self):
        s = Site()
        s.coord = self.coord
        s.atoms = [self]
        return s

    def is_on(self, site, tol=1e-5):
        vec = self.coord - site.coord
        dist = norm(np.dot(vec - np.round(vec), self.structure.cell))
        return dist < tol
