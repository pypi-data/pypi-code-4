from django.db import models
from numpy.linalg import solve
import time
import copy
from pyspglib import spglib
from collections import defaultdict

from dev_qmpy.models.composition import Composition
from dev_qmpy.models.element import Element
from dev_qmpy.utils import *


class Atom(models.Model):
    structure = models.ForeignKey('Structure', related_name='atom_set')
    element = models.ForeignKey('Element', related_name='atoms')

    x = models.FloatField(blank=False)
    y = models.FloatField(blank=False)
    z = models.FloatField(blank=False)
    direct = models.BooleanField(default=True)

    fx = models.FloatField(default=0)
    fy = models.FloatField(default=0)
    fz = models.FloatField(default=0)

    magmom = models.FloatField(default=0)
    occupancy = models.FloatField(default=1)

    charge = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'atoms'

    def __str__(self):
        return '%s: %8f %8f %8f' % (self.element.symbol, 
                self.x, self.y, self.z)

    @property
    def symbol(self):
        return self.element.symbol

    @symbol.setter
    def symbol(self, symbol):
        self.element = Element.get(symbol)

    @property
    def force(self):
        return np.array([self.fx , self.fy, self.fz])

    @force.setter
    def force(self, values):
        self.fx, self.fy, self.fz = values

    @property
    def coord(self):
        return np.array([self.x , self.y, self.z])

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = values

class Structure(models.Model, object):
    id = models.AutoField(primary_key=True)
    entry = models.ForeignKey('Entry', null=True)
    label = models.CharField(blank=True, max_length=20)
    log = models.TextField()

    ## representations
    composition = models.ForeignKey(Composition, null=True)
    name = models.CharField(max_length=255, db_index=True, null=True)
    formula = models.CharField(max_length=255, db_index=True, null=True)
    natoms = models.IntegerField(null=True)

    x1 = models.FloatField()
    x2 = models.FloatField()
    x3 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    y3 = models.FloatField()
    z1 = models.FloatField()
    z2 = models.FloatField()
    z3 = models.FloatField()

    ## stresses
    sxx = models.FloatField(default=0)
    syy = models.FloatField(default=0)
    szz = models.FloatField(default=0)
    sxy = models.FloatField(default=0)
    syz = models.FloatField(default=0)
    szx = models.FloatField(default=0)

    ## symmetry
    spacegroup = models.IntegerField(null=True)

    class Meta:
        db_table = 'structures'

    def __eq__(self, other):
        if self.comp != other.comp:
            return False
        if not np.allclose(self.cell, other.cell):
            return False
        if not np.allclose(self.scaled_coords, other.scaled_coords):
            return False
        return True

    def __str__(self):
        return comp_to_name(self.comp, special='reduce')

    def like(self, other):
        if self.spacegroup is None:
            self.find_symmetry()
            self.save()
        if other.spacegroup is None:
            other.find_symmetry()
            other.save()

    def save(self,*args, **kwargs):
        self.formula = comp_to_formula(self.comp)
        self.name = comp_to_name(self.comp, special='reduce')
        self.composition = Composition.get(self.comp)
        if hasattr(self, 'new_atoms'):
            self.natoms = len(self.atoms)
        else:
            self.natoms = self.atom_set.count()
        super(Structure, self).save(*args, **kwargs)
        if hasattr(self, 'new_atoms'):
            for atom in self.new_atoms:
                self.atom_set.add(atom)
            del self.new_atoms

    @property
    def volume(self):
        b1, b2, b3 = self.cell
        return abs(np.dot(np.cross(b1, b2), b3))

    @volume.setter
    def volume(self, value):
        scale = value/self.volume
        self.cell = self.cell * scale**(1/3.)

    @property
    def lat_params(self):
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
        return np.array([
                [self.x1, self.x2, self.x3],
                [self.y1, self.y2, self.y3],
                [self.z1, self.z2, self.z3]])

    @cell.setter
    def cell(self, cell):
        self.x1, self.x2, self.x3 = cell[0]
        self.y1, self.y2, self.y3 = cell[1]
        self.z1, self.z2, self.z3 = cell[2]


    @property
    def atomic_numbers(self):
        return np.array([ atom.element.z for atom in self.atoms ])

    @property
    def stresses(self):
        return np.array([self.sxx, self.syy, self.szz, 
            self.sxy, self.syz, self.szx ])

    @stresses.setter
    def stresses(self, vector):
        self.sxx, self.syy, self.szz = vector[0:3]
        self.sxy, self.syx, self.szx = vector[3:6]

    @property
    def atoms(self):
        atoms = []
        if hasattr(self, 'new_atoms'):
            for a in self.new_atoms:
                atoms.append(a)
            return sorted(atoms, key=lambda x: x.symbol)
        return sorted(self.atom_set.all(), key=lambda x: x.symbol)

    def add_atom(self, atom):
        if not hasattr(self, 'new_atoms'):
            self.new_atoms = []
        self.new_atoms.append(atom)

    def set_magnetism(self, type, scheme='primitive'):
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

    @property
    def ntypes(self):
        return len(self.elements)

    @property
    def mrp(self):
        v1,v2,v3 = self.cell
        return  min(
                norm(v1),norm(v2),norm(v3),
                norm(v1+v2),norm(v2+v3),norm(v3+v1),
                norm(v1+v2+v3))

    @property
    def magmom(self):
        return sum(a.magmom for a in self.atoms)

    @property
    def elements(self):
        elts = set( atom.element for atom in self.atoms )
        return elts

    @property
    def comp(self):
        comp = defaultdict(int)
        for atom in self.atoms:
            comp[atom.symbol] += 1
        return comp

    @property
    def unit_comp(self):
        return defaultdict(float,
                name_to_comp(self.formula, special='unit'))

    @property
    def coords(self):
        return np.array([ atom.coord for atom in self.atoms ])

    @property
    def magmoms(self):
        return np.array([ atom.magmom for atom in self.atoms ])

    @property
    def scaled_coords(self):
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
    def cartesian_coords(self):
        coords = []
        for atom in self.atoms:
            if atom.direct:
                coords.append(np.dot(atom.coord, self.cell))
            else:
                coords.append(atom.coord)
        return np.array(coords)

    @property
    def forces(self):
        forces = []
        for atom in self.atoms:
            forces.append(atom.force)
        return np.array(forces)

    @forces.setter
    def forces(self, forces):
        for force, atom in zip(forces, self.atoms):
            atom.force = force

    @property
    def reciprocal_lattice(self):
        return np.linalg.inv(self.cell).T

    @property
    def inv(self):
        return np.linalg.inv(self.cell)

    @property
    def relative_rec_lat(self):
        rec_lat = self.reciprocal_lattice
        rec_mags = [ norm(rec_lat[0]), norm(rec_lat[1]), norm(rec_lat[2])]
        r0 = min(rec_mags)
        return np.array([ np.round(r/r0, 4) for r in rec_mags ])

    @property
    def sg(self):
        if not self.spacegroup:
            self.find_symmetry(keep=True)
        return self.spacegroup

    def find_symmetry(self, keep=False):
        sg = spglib.get_spacegroup(self.ase, symprec=1e-2)
        sg = sg.strip(' ()')
        self.spacegroup = int(sg)
        if keep:
            self.save()
        return int(sg)

    def get_distance(self, atom1, atom2):
        if isinstance(atom1, int):
            atom1 = self.atoms[atom1]
        if isinstance(atom2, int):
            atom2 = self.atoms[atom2]
        if atom1.direct:
            v1 = np.dot(atom1.coord, self.cell)
        else:
            v1 = atom1.coord
        if atom2.direct:
            v2 = np.dot(atom2.coord, self.cell)
        else:
            v2 = atom2.coord
        vec = v1 - v2
        Dr = solve(self.cell.T, vec)
        D = np.dot(Dr - np.round(Dr), self.cell)
        return norm(D)


    def find_neighbors(self):
        ''' Based on the following algorithm defines a list of pairs of atoms,
        sotred as a tuple, of the form (atom1,atom2,dist_1_2). For all triplets
        of atoms A, B and C, the atoms A and B are neighbors if and only if:
            AB is shorter than AC
            and
            AB is shorter than BC'''
        self.neighbors = []
        self.neigh_dict = defaultdict(list)
        atoms = self.atoms
        mrp = self.mrp
        for atom1, atom2 in itertools.combinations(atoms, 2):
            _12 = self.get_distance(atom1, atom2)
            if _12 == 0:
                _12 = mrp
            for atom3 in atoms:
                _23 = self.get_distance(atom2, atom3)
                _31 = self.get_distance(atom3, atom1)
                if _23 == 0: _23 = mrp
                if _31 == 0: _31 = mrp
                if _23 < _12 and _31 < _12:
                    break
            else:
                self.neighbors.append((atom1,atom2,_12))
                self.neigh_dict[atom1].append(atom2)
                self.neigh_dict[atom2].append(atom1)

    def substitute(self, replace, rescale=True):
        '''Replace atoms, as specified in a dict of pairs. 
        Optionally, can rescale the new volume to the total volume of the
        elemental phases of the new composition.

        Example:
        >>> s = Structure.create('POSCAR-Fe2O3')
        >>> s.substitute({'Fe':'Ni', 'O':'F'} rescale=True)
        '''

        struct = Structure()
        struct.cell = self.cell
        volume = 0.0
        for a, coord in zip(self.atoms, self.scaled_coords):
            a2 = Atom()
            a2.force = a.force
            a2.coord = coord
            a2.direct = True
            if a.symbol in replace:
                a2.symbol = replace[a.symbol]
            else:
                a2.symbol = a.symbol
            struct.add_atom(a2) 
            volume += a2.element.volume
        if rescale:
            struct.volume = volume
        return struct

    def copy(self):
        new = copy.deepcopy(self)
        new.id = None
        new.label = ''
        new.log = ''
        new.atom_set = []
        new.new_atoms = []
        for atom in self.atoms:
            new_atom = copy.deepcopy(atom)
            new_atom.id = None
            new.add_atom(new_atom)
        return new

    @property
    def similar(self):
        return Structure.objects.filter(natoms=self.natoms,
                composition=self.composition, 
                spacegroup=self.spacegroup,
                label=self.label)
