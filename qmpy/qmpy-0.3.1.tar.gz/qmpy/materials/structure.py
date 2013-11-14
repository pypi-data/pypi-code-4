from numpy.linalg import solve, norm
import time
import copy
from collections import defaultdict

from django.db import models

from element import Element, Species
from atom import Atom, Site
from composition import Composition
from qmpy.utils import *
from qmpy.data.meta_data import *
from qmpy.analysis.symmetry import Spacegroup
from qmpy.analysis.symmetry import *
from qmpy.analysis.pdf import get_pdf_uri
from transforms import *

class StructureError(Exception):
    '''Structure related problem'''

@add_meta_data('comment')
@add_meta_data('keyword')
class Structure(models.Model, object):
    '''
    Structure model. Principal attributes are a lattice and basis set.

    Database Attributes:
        entry               : Entry which the structure belongs to.
        composition         : Composition of the structure.
        element_set         : django QuerySet of Element objects present in
                              the structure.
        species_set         : django QuerySet of Species objects present in the
                              structure. Species are Elements with a given
                              charge state. 
        reference           : Reference object, containing the author, journal,
                              title, etc...
        label               : Description of the structure
        prototype           :
        natoms              :
        ntypes              :
        nsites              : 
        
        x1, x2, x3
        y1, y2, y3
        z1, z2, z3 - elements of 3x3 lattice vector matrix

        sxx, syy, szz
        sxy, syz, szx - Stress elements

        volume              : total volume, in A^3/UC (float)
        volume_pa           : volume per atom, in A^3/atom (float)

        energy              : total energy, in eV/UC (float)
        energy_pa           : energy/atom, in eV/atom (float)
        delta_e    : formation energy in eV/atom (float)
        meta_stability      : Distance relative to the hull, in the absence of
                              this phase. Negative values indicate stability,
                              positive values, instability. Deeply negative
                              values indicate a strong preference to competing
                              phases, very positive values indicate it is far
                              less stable than competing phases. (float)

        spacegroup          : Spacegroup object

    '''
    # model relationships
    entry = models.ForeignKey('Entry', null=True)
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    meta_data = models.ManyToManyField('MetaData')
    reference = models.ForeignKey('Reference', blank=True, null=True)
    label = models.CharField(blank=True, max_length=20)
    prototype = models.ForeignKey('Prototype', null=True, blank=True,
                                               related_name='+')
    step = models.IntegerField(blank=True, null=True)
    measured = models.BooleanField(default=False)

    composition = models.ForeignKey('Composition', null=True, 
                                    related_name='structure_set')
    natoms = models.IntegerField(null=True, blank=True)
    nsites = models.IntegerField(null=True, blank=True)
    ntypes = models.IntegerField(null=True, blank=True)

    ## lattice
    x1 = models.FloatField()
    x2 = models.FloatField()
    x3 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    y3 = models.FloatField()
    z1 = models.FloatField()
    z2 = models.FloatField()
    z3 = models.FloatField()

    volume = models.FloatField(blank=True, null=True)
    volume_pa = models.FloatField(blank=True, null=True)

    sxx = models.FloatField(default=0)
    syy = models.FloatField(default=0)
    szz = models.FloatField(default=0)
    sxy = models.FloatField(default=0)
    syz = models.FloatField(default=0)
    szx = models.FloatField(default=0)

    ## symmetry
    spacegroup = models.ForeignKey('Spacegroup', blank=True,
            null=True)

    ## computed quantities
    energy = models.FloatField(blank=True, null=True)
    energy_pa = models.FloatField(blank=True, null=True)
    magmom = models.FloatField(blank=True, null=True)
    magmom_pa = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(blank=True, null=True)
    meta_stability = models.FloatField(blank=True, null=True)

    # cache
    _reciprocal_lattice = None
    _distinct_atoms = []
    _magmoms = []

    class Meta:
        app_label = 'qmpy'
        db_table = 'structures'

    # builtins
    def __eq__(self, other):
        if self.comp != other.comp:
            return False
        if not np.allclose(self.cell, other.cell):
            return False
        if not np.allclose(self.scaled_coords, other.scaled_coords):
            return False
        return True

    def __str__(self):
        if not self.composition_id is None:
            return self.composition_id
        else:
            return format_comp(reduce_comp(self.comp))

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)

    # django overrides
    def save(self,*args, **kwargs):
        if not self.composition:
            self.composition = Composition.get(self.comp)

        self.symmetrize()
        self.natoms = len(self.atoms)
        self.ntypes = len(self.comp.keys())
        super(Structure, self).save(*args, **kwargs)
        #for a in self.atoms:
        #    a.structure = self
        self.atom_set = self.atoms
        #for s in self.sites:
        #    s.structure = self
        self.site_set = self.sites
        self.element_set = self.elements
        self.species_set = self.species
        self.meta_data = self.comment_objects

    # django accessors/aggregators
    _atoms = None
    @property
    def atoms(self):
        if self._atoms is None:
            if not self.id:
                self._atoms = []
            else:
                self._atoms = self.atom_set.all()
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        self._atoms = sorted(atoms)
        self.natoms = len(atoms)
        self.ntypes = len(self.comp)
        for a in atoms:
            a.structure = self

    _sites = None
    @property
    def sites(self):
        if self._sites is None:
            self._sites = self.get_sites()
        return self._sites

    @sites.setter
    def sites(self, sites):
        self._sites = sites
        for s in sites:
            s.structure = self
        self.nsites = len(sites)

    @property
    def elements(self):
        '''List of Elements'''
        return [ Element.get(e) for e in self.comp.keys() ]

    @property
    def species(self):
        '''List of species'''
        return [ Species.get(s) for s in self.spec_comp.keys() ]

    @property
    def stresses(self):
        '''Calculated stresses, a numpy.ndarray of shape (6,)'''
        return np.array([self.sxx, self.syy, self.szz,
            self.sxy, self.syz, self.szx ])
        
    @stresses.setter
    def stresses(self, vector):
        self.sxx, self.syy, self.szz = vector[0:3]
        self.sxy, self.syx, self.szx = vector[3:6]

    # calculated properties
    @property
    def volume(self):
        '''Volume, calculated from the triple product of self.cell'''
        b1, b2, b3 = self.cell
        return abs(np.dot(np.cross(b1, b2), b3))

    @volume.setter
    def volume(self, value):
        scale = value/self.volume
        self.cell = self.cell * scale**(1/3.)

    @property
    def volume_pa(self):
        '''Volume, normalized per atom.'''
        return self.volume/self.natoms

    @property
    def lat_param_dict(self):
        '''Dictionary of lattice parameters.'''
        v1, v2, v3 = self.cell
        a = norm(v1)
        b = norm(v2)
        c = norm(v3)
        alpha = np.arccos(np.dot(v2, v3)/(b*c))*180/np.pi
        beta = np.arccos(np.dot(v1, v3)/(a*c))*180/np.pi
        gamma = np.arccos(np.dot(v1, v2)/(a*b))*180/np.pi
        return { 'a': a, 'b':b, 'c':c,
                'alpha': alpha, 'beta':beta, 'gamma':gamma }

    @property
    def lat_params(self):
        '''Tuple of lattice parameters (a, b, c, alpha, beta, gamma).'''
        v1, v2, v3 = self.cell
        a = norm(v1)
        b = norm(v2)
        c = norm(v3)
        alpha = np.arccos(np.dot(v2, v3)/(b*c))*180/np.pi
        beta = np.arccos(np.dot(v1, v3)/(a*c))*180/np.pi
        gamma = np.arccos(np.dot(v1, v2)/(a*b))*180/np.pi
        return a, b, c, alpha, beta, gamma

    @property
    def cell(self):
        '''Lattice vectors, 3x3 numpy.ndarray.'''
        return np.array([
                [self.x1, self.x2, self.x3],
                [self.y1, self.y2, self.y3],
                [self.z1, self.z2, self.z3]])

    @cell.setter
    def cell(self, cell):
        self.x1, self.x2, self.x3 = cell[0]
        self.y1, self.y2, self.y3 = cell[1]
        self.z1, self.z2, self.z3 = cell[2]
        self._inv = None

    @property
    def atomic_numbers(self):
        '''List of atomic numbers, length equal to number of atoms.'''
        return np.array([ atom.element.z for atom in self.atoms ])

    @property
    def atom_types(self):
        '''List of atomic symbols, length equal to number of atoms.'''
        return np.array([ atom.element_id for atom in self.atoms ])

    @property
    def species_types(self):
        '''List of species, length equal to number of atoms.'''
        return np.array([ atom.species_id for atom in self.atoms ])

    # methods
    def symmetrize(self):
        '''
        Analyze the symmetry of the structure. Uses spglib to find the
        symmetry. 

        Sets:
            self.spacegroup -> Spacegroup
            self.uniq_sites -> list of unique Sites
            
            for each atom:
                atom.wyckoff -> WyckoffSite
            for each site:
                site.multiplicity -> int

        '''
        dataset = get_symmetry_dataset(self)
        self.spacegroup = Spacegroup.objects.get(pk=dataset['number'])
        for i, site in enumerate(self.sites):    
            site.wyckoff = self.spacegroup.get_site(dataset['wyckoffs'][i])
            site.structure = self
        counts = defaultdict(int)
        for e in dataset['equivalent_atoms']:
            counts[e] += 1
        self.uniq_sites = []
        for ind, mult in counts.items():
            site = self.sites[ind]
            site.multiplicity = mult
            self.uniq_sites.append(site)

    def desymmetrize(self):
        '''
        Using self.spacegroup and self.uniq_sites, creates additional sites and
        atoms as indicated by the symmetry of the spacegroup.
        
        '''
        self.atoms = self.spacegroup.equivalent_sites(self)

    def add_atom(self, atom):
        for a in self.atoms:
            if (np.allclose(a.coord, atom.coord) and 
                    a.element_id == atom.element_id ):
                return
        self._atoms.append(atom)
        self.spacegroup = None

    def set_magnetism(self, type, scheme='primitive'):
        '''
        Assigns magnetic moments to all atoms in accordance with the specified
        magnetism scheme.

        Allowed schemes:
            none    - all magnetic moments are set to None
            "ferro" - all magnetic moments with partial d or f shells are
                      assigned an initial magnetic moment of 5 or 7
                      respectively
            "anti"  - raises NotImplementedError

        '''
        if type == 'none':
            for atom in self.atoms:
                atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        if type == 'ferro':
            for atom in self.atoms:
                if atom.element.d_elec > 0 and atom.element.d_elec < 10:
                    atom.magmom = 5
                elif atom.element.f_elec > 0 and atom.element.f_elec < 14:
                    atom.magmom = 7
                else:
                    atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        elif type == 'anti-ferro':
            raise NotImplementedError
        self.spacegroup = None

    @property
    def comp(self):
        '''Composition dictionary.'''
        comp = {}
        for atom in self.atoms:
            elt = atom.element_id
            comp[elt] = comp.get(elt, 0) + atom.occupancy
        return comp

    @property
    def spec_comp(self):
        '''Species composition dictionary.'''
        spec_comp = {}
        for atom in self.atoms:
            spec = atom.species
            spec_comp[spec] = spec_comp.get(spec, 0) + atom.occupancy
        return spec_comp

    @property
    def name(self):
        '''Unformatted name.'''
        return format_comp(self.comp)

    @property
    def unit_comp(self):
        return dict(name_to_comp(self.composition_id, special='unit'))

    @property
    def coords(self):
        '''numpy.ndarray of atom coordinates of shape (3, natoms).'''
        return np.array([ atom.coord for atom in self.atoms ])

    @property
    def magmoms(self):
        '''numpy.ndarray of magnetic moments of shape (natoms,).'''
        return np.array([ atom.magmom for atom in self.atoms ])

    @property
    def site_coords(self):
        '''numpy.ndarray of site coordinates of shape (3, nsites).'''
        return np.vstack([ s.coord for s in self.sites ])

    @property
    def site_labels(self):
        '''
        Labels for all sites. For sites with single occupancy returns the
        atomic symbol, for sites with multiple occupancies returns "(A,B)".

        '''
        return np.array([ str(s) for s in self.sites ])

    @property
    def scaled_coords(self):
        '''Return atomic positions in DIRECT coordinates.'''
        inv = self.inv.T
        coords = []
        for atom in self.atoms:
            if not atom.direct:
                coords.append(np.dot(inv, atom.coord))
            else:
                coords.append(atom.coord)
        coords = np.array(coords)
        coords %= 1.0
        coords %= 1.0
        return coords

    @property
    def direct_coords(self):
        '''Return atomic positions in DIRECT coordinates.'''
        return self.scaled_coords

    @property
    def cartesian_coords(self):
        '''Return atomic positions in cartesian coordinates.'''
        coords = []
        for atom in self.atoms:
            if atom.direct:
                #coords.append(atom.coord*s.cell)
                coords.append(np.dot(atom.coord, self.cell))
            else:
                coords.append(atom.coord)
        return np.array(coords)

    @property
    def forces(self):
        '''numpy.ndarray of forces on atoms.'''
        forces = []
        for atom in self.atoms:
            forces.append(atom.forces)
        return np.array(forces)

    @forces.setter
    def forces(self, forces):
        for forces, atom in zip(forces, self.atoms):
            atom.forces = force

    @property
    def reciprocal_lattice(self):
        '''Reciprocal lattice of the structure.'''
        if self._reciprocal_lattice is None:
            self._reciprocal_lattice = np.linalg.inv(self.cell).T
        return self._reciprocal_lattice

    _inv = None
    @property
    def inv(self):
        '''
        Precalculates the inverse of the lattice, for faster conversion
        between cartesian and direct coordinates.
        
        '''
        if self._inv is None:
            self._inv = np.linalg.inv(self.cell)
        return self._inv

    @property
    def relative_rec_lat(self):
        rec_lat = self.reciprocal_lattice
        rec_mags = [ norm(rec_lat[0]), norm(rec_lat[1]), norm(rec_lat[2])]
        r0 = min(rec_mags)
        return np.array([ np.round(r/r0, 4) for r in rec_mags ])

    @property
    def pdf_uri(self):
        return get_pdf_uri(self)

    def get_distance(self, atom1, atom2):
        '''Return the shorted distance between two atoms in the structure.'''
        if isinstance(atom1, int):
            atom1 = self.atoms[atom1]
        if isinstance(atom2, int):
            atom2 = self.atoms[atom2]

        vec = atom1.coord - atom2.coord
        #Dr = solve(self.cell.T, vec)
        D = np.dot(vec - np.round(vec), self.cell)
        return norm(D)

    def copy(self):
        '''
        Create a complete copy of the structure, with any primary keys
        removed, so it is not associated with the original.

        '''
        new = copy.deepcopy(self)
        new.id = None
        new.label = ''
        atom_set = []
        for atom in self.atoms:
            new_atom = atom.copy()
            new_atom.id = None
            atom_set.append(new_atom)
        new.atoms = atom_set
        return new

    @property
    def similar(self):
        return Structure.objects.filter(natoms=self.natoms,
                composition=self.composition, 
                label=self.label)

    def set_natoms(self, n):
        '''Set self.atoms to n blank Atoms.'''
        self.atoms = [ Atom() for i in range(n) ]

    def make_conventional(self):
        '''Uses spglib to convert to the conventional cell.'''
        refine_cell(self)

    def make_primitive(self):
        '''Uses spglib to convert to the primitive cell.'''
        find_primitive(self)

    def get_sites(self, tol=1e-3):
        '''
        From self.atoms, creates a list of Sites. Atoms which are closer
        than tol from one another are considered on the same site.

        '''
        if not any([ a.occupancy < 1 for a in self.atoms ]):
            self._sites = [ a.as_site() for a in self.atoms ]
            return self._sites
        d_sites = []
        for atom in self:
            for site in d_sites:
                if atom.is_on(site):
                    site.atoms.append(atom)
                    break
            else:
                site = atom.as_site()
                site.structure = self
                d_sites.append(site)
        self._sites = d_sites
        return self._sites

    def group_atoms_by_symmetry(self):
        '''Sort self.atoms according to the site they occupy.'''
        eq = get_symmetry_dataset(self)['equivalent_atoms']
        resort = np.argsort(eq)
        self._atoms = list(np.array(self._atoms)[resort])

    def substitute(self, replace):
        return substitute(self, replace)

class Prototype(models.Model):
    name = models.CharField(max_length=63, primary_key=True)
    structure = models.ForeignKey(Structure, related_name='+', 
                                  blank=True, null=True)
    composition = models.ForeignKey('Composition', blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'prototypes'

    @classmethod
    def get(cls, name):
        obj, new = cls.objects.get_or_create(name=name)
        if new:
            obj.save()
        return obj
