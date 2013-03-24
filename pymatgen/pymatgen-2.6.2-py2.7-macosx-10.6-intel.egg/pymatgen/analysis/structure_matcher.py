#!/usr/bin/env python

"""
This module provides classes to perform fitting of structures.
"""

from __future__ import division

__author__ = "Stephen Dacek, William Davidson Richards, Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Stephen Dacek"
__email__ = "sdacek@mit.edu"
__status__ = "Beta"
__date__ = "Dec 3, 2012"

import numpy as np
import itertools
import abc

from pymatgen.serializers.json_coders import MSONable
from pymatgen.core.structure import Structure
from pymatgen.core.structure_modifier import StructureEditor
from pymatgen.core.lattice import Lattice
from pymatgen.core.composition import Composition
from pymatgen.optimization.linear_assignment import LinearAssignment
from pymatgen.util.coord_utils import get_points_in_sphere_pbc


class AbstractComparator(MSONable):
    """
    Abstract Comparator class. A Comparator defines how sites are compared in
    a structure.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def are_equal(self, sp1, sp2):
        """
        Defines how the species of two sites are considered equal. For
        example, one can consider sites to have the same species only when
        the species are exactly the same, i.e., Fe2+ matches Fe2+ but not
        Fe3+. Or one can define that only the element matters,
        and all oxidation state information are ignored.

        Args:
            sp1:
                First species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.
            sp2:
                Second species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.

        Returns:
            Boolean indicating whether species are considered equal.
        """
        return

    @abc.abstractmethod
    def get_structure_hash(self, structure):
        """
        Defines a hash for structures. This allows structures to be grouped
        efficiently for comparison. For example, in exact matching,
        you should only try to perform matching if structures have the same
        reduced formula (structures with different formulas can't possibly
        match). So the reduced_formula is a good hash. The hash function
        should be relatively fast to compute relative to the actual matching.

        Args:
            structure:
                A structure

        Returns:
            A hashable object. Examples can be string formulas, etc.
        """
        return

    @staticmethod
    def from_dict(d):
        for trans_modules in ['structure_matcher']:
            mod = __import__('pymatgen.analysis.' + trans_modules,
                             globals(), locals(), [d['@class']], -1)
            if hasattr(mod, d['@class']):
                trans = getattr(mod, d['@class'])
                return trans()
        raise ValueError("Invalid Comparator dict")

    @property
    def to_dict(self):
        return {"version": __version__, "@module": self.__class__.__module__,
                "@class": self.__class__.__name__}


class SpeciesComparator(AbstractComparator):
    """
    A Comparator that matches species exactly. The default used in
    StructureMatcher.
    """

    def are_equal(self, sp1, sp2):
        """
        True if species are exactly the same, i.e., Fe2+ == Fe2+ but not Fe3+.

        Args:
            sp1:
                First species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.
            sp2:
                Second species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.

        Returns:
            Boolean indicating whether species are equal.
        """
        return sp1 == sp2

    def get_structure_hash(self, structure):
        """
        Hash for structure.

        Args:
            structure:
                A structure

        Returns:
            Reduced formula for the structure is used as a hash for the
            SpeciesComparator.
        """
        return structure.composition.reduced_formula


class ElementComparator(AbstractComparator):
    """
    A Comparator that matches elements. i.e. oxidation states are
    ignored.
    """

    def are_equal(self, sp1, sp2):
        """
        True if element:amounts are exactly the same, i.e.,
        oxidation state is not considered.

        Args:
            sp1:
                First species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.
            sp2:
                Second species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.

        Returns:
            Boolean indicating whether species are the same based on element
            and amounts.
        """
        comp1 = Composition(sp1)
        comp2 = Composition(sp2)
        return comp1.get_el_amt_dict() == comp2.get_el_amt_dict()

    def get_structure_hash(self, structure):
        """
        Hash for structure.

        Args:
            structure:
                A structure

        Returns:
            Reduced formula for the structure is used as a hash for the
            SpeciesComparator.
        """
        return structure.composition.reduced_formula


class FrameworkComparator(AbstractComparator):
    """
    A Comparator that matches sites, regardless of species.
    """

    def are_equal(self, sp1, sp2):
        """
        True if there are atoms on both sites.

        Args:
            sp1:
                First species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.
            sp2:
                Second species. A dict of {specie/element: amt} as per the
                definition in Site and PeriodicSite.

        Returns:
            True always
        """
        return True

    def get_structure_hash(self, structure):
        """
        Hash for structure.

        Args:
            structure:
                A structure

        Returns:
            Number of atoms is a good hash for simple framework matching.
        """
        return len(structure)


class StructureMatcher(MSONable):
    """
    Class to match structures by similarity.

    Algorithm:

    1. Given two structures: s1 and s2
    2. Optional: Reduce to primitive cells.
    3. If the number of sites do not match, return False
    4. Reduce to s1 and s2 to Niggli Cells
    5. Optional: Scale s1 and s2 to same volume.
    6. Optional: Remove oxidation states associated with sites
    7. Find all possible lattice vectors for s2 within shell of ltol.
    8. For s1, translate an atom in the smallest set to the origin
    9. For s2: find all valid lattices from permutations of the list
       of lattice vectors (invalid if: det(Lattice Matrix) < half
       volume of original s2 lattice)
    10. For each valid lattice:

        a. If the lattice angles of are within tolerance of s1,
           basis change s2 into new lattice.
        b. For each atom in the smallest set of s2:

            i. Translate to origin and compare sites in structure within
               stol.
            ii. If true: break and return true
    """

    def __init__(self, ltol=0.2, stol=0.6, angle_tol=5, primitive_cell=True,
                 scale=True, comparator=SpeciesComparator()):
        """
        Args:
            ltol:
                Fractional length tolerance. Default is 0.2.
            stol:
                Site tolerance in Angstrom. Default is 0.5 Angstrom.
            angle_tol:
                Angle tolerance in degrees. Default is 5 degrees.
            primitive_cell:
                If true: input structures will be reduced to primitive
                cells prior to matching. Default to True.
            scale:
                Input structures are scaled to equivalent volume if true;
                For exact matching, set to False.
            comparator:
                A comparator object implementing an equals method that declares
                declaring equivalency of sites. Default is
                SpeciesComparator, which implies rigid species
                mapping, i.e., Fe2+ only matches Fe2+ and not Fe3+.

                Other comparators are provided, e.g., ElementComparator which
                matches only the elements and not the species.

                The reason why a comparator object is used instead of
                supplying a comparison function is that it is not possible to
                pickle a function, which makes it otherwise difficult to use
                StructureMatcher with Python's multiprocessing.
        """
        self.ltol = ltol
        self.stol = stol
        self.angle_tol = angle_tol
        self._comparator = comparator
        self._primitive_cell = primitive_cell
        self._scale = scale

    def _get_lattices(self, s1, s2, vol_tol):
        s1_lengths, s1_angles = s1.lattice.lengths_and_angles
        all_nn = get_points_in_sphere_pbc(
            s2.lattice, [[0, 0, 0]], [0, 0, 0],
            (1 + self.ltol) * max(s1_lengths))[:, [0, 1]]
        nv = []
        for l in s1_lengths:
            nvi = all_nn[np.where((all_nn[:, 1] < (1 + self.ltol) * l)
                                  & (all_nn[:, 1] > (1 - self.ltol) * l))][:, 0]
            if not len(nvi):
                return
            nvi = [np.array(site) for site in nvi]
            nvi = np.dot(nvi, s2.lattice.matrix)
            nv.append(nvi)

        #The vectors are broadcast into a 5-D array containing
        #all permutations of the entries in nv[0], nv[1], nv[2]
        #produces the same result as three nested loops over the
        #same variables and calculating determinants individually
        bfl = (np.array(nv[0])[None, None, :, None, :] *
               np.array([1, 0, 0])[None, None, None, :, None] +
               np.array(nv[1])[None, :, None, None, :] *
               np.array([0, 1, 0])[None, None, None, :, None] +
               np.array(nv[2])[:, None, None, None, :] *
               np.array([0, 0, 1])[None, None, None, :, None])

        #Compute volume of each array
        vol = np.sum(bfl[:, :, :, 0, :] * np.cross(bfl[:, :, :, 1, :],
                                                   bfl[:, :, :, 2, :]), 3)
        #Find valid lattices
        valid = np.where(abs(vol) >= vol_tol)
        if not len(valid[0]):
            return
        #loop over valid lattices to compute the angles for each
        lengths = np.sum(bfl[valid] ** 2, axis=2) ** 0.5
        angles = np.zeros((len(bfl[valid]), 3), float)
        for i in xrange(3):
            j = (i + 1) % 3
            k = (i + 2) % 3
            angles[:, i] = \
                np.sum(bfl[valid][:, j, :] * bfl[valid][:, k, :], 1)\
                / (lengths[:, j] * lengths[:, k])
        angles = np.arccos(angles) * 180. / np.pi
        #Check angles are within tolerance
        valid_angles = np.where(np.all(np.abs(angles - s1_angles) <
                                       self.angle_tol, axis=1))
        if not len(valid_angles[0]):
            return
        #yield valid lattices
        for lat in bfl[valid][valid_angles]:
            nl = Lattice(lat)
            yield nl

    def _cmp_struct(self, s1, s2, frac_tol):
        #compares the fractional coordinates
        for s1_coords, s2_coords in zip(s1, s2):
            dist = s1_coords[:, None] - s2_coords[None, :]
            dist = abs(dist - np.round(dist))
            dist[np.where(dist > frac_tol[None, None, :])] = 3 * len(dist)
            cost = np.sum(dist, axis=-1)
            if np.max(np.min(cost, axis=0)) >= 3 * len(dist):
                return False
            lin = LinearAssignment(cost)
            if lin.min_cost >= 3 * len(dist):
                return False
        return True

    def fit(self, struct1, struct2):
        """
        Fit two structures.

        Args:
            struct1:
                1st structure
            struct2:
                2nd structure

        Returns:
            True if the structures are the equivalent, else False.
        """
        stol = self.stol
        comparator = self._comparator

        if comparator.get_structure_hash(struct1) !=\
                comparator.get_structure_hash(struct2):
            return False

        #primitive cell transformation
        if self._primitive_cell and struct1.num_sites != struct2.num_sites:
            struct1 = struct1.get_primitive_structure()
            struct2 = struct2.get_primitive_structure()

        # Same number of sites
        if struct1.num_sites != struct2.num_sites:
            return False

        # Get niggli reduced cells. Though technically not necessary, this
        # minimizes cell lengths and speeds up the matching of skewed
        # cells considerably.
        struct1 = struct1.get_reduced_structure(reduction_algo="niggli")
        struct2 = struct2.get_reduced_structure(reduction_algo="niggli")

        nl1 = struct1.lattice
        nl2 = struct2.lattice

        #rescale lattice to same volume
        if self._scale:
            scale_vol = (nl2.volume / nl1.volume) ** (1 / 6)
            se1 = StructureEditor(struct1)
            nl1 = Lattice(nl1.matrix * scale_vol)
            se1.modify_lattice(nl1)
            struct1 = se1.modified_structure
            se2 = StructureEditor(struct2)
            nl2 = Lattice(nl2.matrix / scale_vol)
            se2.modify_lattice(nl2)
            struct2 = se2.modified_structure

        #Volume to determine invalid lattices
        vol_tol = nl2.volume / 2

        #fractional tolerance of atomic positions
        frac_tol = np.array([stol / i for i in struct1.lattice.abc])

        #generate structure coordinate lists
        species_list = []
        s1 = []
        for site in struct1:
            found = False
            for i, species in enumerate(species_list):
                if comparator.are_equal(site.species_and_occu, species):
                    found = True
                    s1[i].append(site.frac_coords)
                    break
            if not found:
                s1.append([site.frac_coords])
                species_list.append(site.species_and_occu)

        zipped = sorted(zip(s1, species_list), key=lambda x: len(x[0]))

        s1 = [x[0] for x in zipped]
        species_list = [x[1] for x in zipped]
        s2_cart = [[] for i in s1]

        for site in struct2:
            found = False
            for i, species in enumerate(species_list):
                if comparator.are_equal(site.species_and_occu, species):
                    found = True
                    s2_cart[i].append(site.coords)
                    break
            #if no site match found return false
            if not found:
                return False

        #check that sizes of the site groups are identical
        for f1, c2 in zip(s1, s2_cart):
            if len(f1) != len(c2):
                return False

        #translate s1
        s1_translation = s1[0][0]
        for i in range(len(species_list)):
            s1[i] = np.mod(s1[i] - s1_translation, 1)

        #do permutations of vectors, check for equality
        for nl in self._get_lattices(struct1, struct2, vol_tol):
            s2 = [nl.get_fractional_coords(c) for c in s2_cart]
            for coord in s2[0]:
                t_s2 = [np.mod(coords - coord, 1) for coords in s2]
                if self._cmp_struct(s1, t_s2, frac_tol):
                    return True
        return False

    def find_indexes(self, s_list, group_list):
        """
        Given a list of structures, return list of indices where each
        structure appears in group_list.

        Args:
            s_list:
                list of structures to check
            group_list:
                list to find structures in
        """
        inds = [-1] * len(s_list)
        for j in range(len(s_list)):
            for i in range(len(group_list)):
                if len(np.where(s_list[j] in group_list[i])[0]):
                    inds[j] = i
                    break
        return inds

    def group_structures(self, s_list):
        """
        Given a list of structures, use fit to group
        them by structural equality.

        Args:
            s_list:
                List of structures to be grouped

        Returns:
            A list of lists of matched structures
            Assumption: if s1=s2 and s2=s3, then s1=s3
            This may not be true for small tolerances.
        """
        #Use structure hash to pre-group structures.
        sorted_s_list = sorted(s_list, key=self._comparator.get_structure_hash)
        all_groups = []

        #For each pre-grouped list of structures, perform actual matching.
        for k, g in itertools.groupby(sorted_s_list,
                                      key=self._comparator.get_structure_hash):
            g = list(g)
            group_list = [[g[0]]]
            for i, j in itertools.combinations(range(len(g)), 2):
                s1_ind, s2_ind = self.find_indexes([g[i], g[j]], group_list)
                if s2_ind == -1 and self.fit(g[i], g[j]):
                    group_list[s1_ind].append(g[j])
                elif (j - i) == 1 and s2_ind == -1:
                    group_list.append([g[j]])
            all_groups.extend(group_list)
        return all_groups

    @property
    def to_dict(self):
        return {"version": __version__, "@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "comparator": self._comparator.to_dict,
                "stol": self.stol,
                "ltol": self.ltol,
                "angle_tol": self.angle_tol,
                "primitive_cell": self._primitive_cell,
                "scale": self._scale}

    @staticmethod
    def from_dict(d):
        return StructureMatcher(
            ltol=d["ltol"], stol=d["stol"], angle_tol=d["angle_tol"],
            primitive_cell=d["primitive_cell"], scale=d["scale"],
            comparator=AbstractComparator.from_dict(d["comparator"]))

    def fit_anonymous(self, struct1, struct2):
        """
        Performs an anonymous fitting, which allows distinct species in one
        structure to map to another. E.g., to compare if the Li2O and Na2O
        structures are similar.

        Args:
            struct1:
                1st structure
            struct2:
                2nd structure

        Returns:
            A minimal species mapping that would map struct1 to struct2 in
            terms of structure similarity, or None if no fit is found. For
            example, to map the cubic Li2O to cubic Na2O,
            we need a Li->Na mapping. This method will return
            [({Element("Li"): 1}, {Element("Na"): 1})]. Since O is the same
            in both structures, there is no O to O mapping required.
            Note that the return form is a list of pairs of species and
            occupancy dicts. This complicated return for is necessary because
            species and occupancy dicts are non-hashable.
        """
        sp1 = list(set(struct1.species_and_occu))
        sp2 = list(set(struct2.species_and_occu))

        if len(sp1) != len(sp2):
            return None

        for perm in itertools.permutations(sp2):
            perm = list(perm)
            mapped_sp = []
            for site in struct1:
                ind = sp1.index(site.species_and_occu)
                mapped_sp.append(perm[ind])

            transformed_structure = Structure(struct1.lattice, mapped_sp,
                                              struct1.frac_coords)
            if self.fit(transformed_structure, struct2):
                return {sp1[i]: perm[i] for i in xrange(len(sp1))
                        if sp1[i] != perm[i]}

        return None