#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from CifFile import ReadCif, CifFile, CifBlock
import warnings
import itertools
import itertools

import qmpy.materials.structure as strx
import qmpy.materials.composition as comp
import qmpy.analysis.symmetry as sym
import qmpy.data.experiment as expt
from qmpy.utils import *

def get_value(number):
    '''Attempt to return a float from a cif number value.'''
    
    if number == '.':
        return 0.0
    try:
        return float(number)
    except ValueError:
        pass
    number = number.split('(')[0]
    return float(number)

def get_atom(cba):
    '''Convert a _atom loop to an Atom'''
    atom = strx.Atom()
    if hasattr(cba, '_atom_site_type_symbol'):
        atom.element_id = cba._atom_site_type_symbol.strip('0123456789+-')
    elif hasattr(cba, '_atom_site_label'):
        atom.element_id = cba._atom_site_label.strip('0123456789')
    else:
        raise Exception('No recognized element identifier')

    if atom.element_id == 'D' or atom.element_id == 'T':
        atom.element_id = 'H'
    atom.x = get_value(cba._atom_site_fract_x)
    atom.y = get_value(cba._atom_site_fract_y)
    atom.z = get_value(cba._atom_site_fract_z)
    atom.occupancy = get_value(cba._atom_site_occupancy)
    #atom.cif_label = cba._atom_site_type_symbol
    return atom

def get_spacegroup(cb):
    '''Create a Spacegroup from a CifBlock'''
    rots, trans = [], []
    for sym in cb.GetLoop('_symmetry_equiv_pos_as_xyz'):
        r, t = parse_sitesym(sym._symmetry_equiv_pos_as_xyz)
        rots.append(r)
        trans.append(t)
    return rots, trans

def get_lattice_parameters(cb):
    '''Return a tuple of lattice parameters from a CifBlock.'''
    return (get_value(cb.get('_cell_length_a')),
            get_value(cb.get('_cell_length_b')),
            get_value(cb.get('_cell_length_c')),
            get_value(cb.get('_cell_angle_alpha')),
            get_value(cb.get('_cell_angle_beta')),
            get_value(cb.get('_cell_angle_gamma')))

def read_cif_block(cb):
    s = strx.Structure()
    s.cell = latparams_to_basis(get_lattice_parameters(cb))
    sym_ops = zip(*get_spacegroup(cb))
    cl = cb.GetLoop('_atom_type_symbol')
    try:
        ox_data = set((l._atom_type_symbol , 
            get_value(l._atom_type_oxidation_number)) for l in cl )
        ox_data = dict(ox_data)
    except:
        ox_data = {}

    atoms = []
    for atom in cb.GetLoop('_atom_site_label'):
        na = get_atom(atom)
        na.ox = ox_data.get(na.element_id, None)
        for rot, trans in sym_ops:
            coord = np.dot(rot, na.coord) + trans
            coord %= 1.0
            a = na.copy()
            a.coord = coord
            if any([(a.element_id == a2.element_id and 
                     s.get_distance(a, a2) < 1e-1) for a2 in atoms]):
                continue
            atoms.append(a)
    s.atoms = atoms
    s.composition = comp.Composition.get(s.comp)
    
    ## meta data
    s.r_val = float(cb.get('_refine_ls_R_factor_all', 0.0))
    s.temperature = get_value(cb.get('_cell_measurement_temperature', 0.0))
    s.pressure = get_value(cb.get('_cell_measurement_pressure', 0.0))
    if cb.get('_chemical_name_structure_type'):
        s.prototype = strx.Prototype.get(cb.get('_chemical_name_structure_type'))
    s.reported_composition = strx.Composition.get(
                   parse_comp(cb.get('_chemical_formula_sum')))
    s.input_format = 'cif'
    return s

def read_cif(cif_file, grammar='1.1'):
    '''
    Takes a CIF format file, and returns a Structure object. Applies all
    symmetry operations in the CIF to the atoms supplied with the structure. If
    these are not correct, the structure will not be either. If the CIF
    contains more than one file, the return will be a list. If not, the return
    will be a single structure (not in a len-1 list).

    Example:
    >>> s = read_cif('test.cif')
    '''
    warnings.catch_warnings()
    warnings.simplefilter("ignore")
    warnings.warn("deprecated", DeprecationWarning)
    cf = ReadCif(cif_file, grammar=grammar)
    structures = []
    for key in cf.keys():
        structures.append(read_cif_block(cf[key]))
    if len(structures) == 1:
        return structures[0]
    else:
        return structures

def add_comp_loop(structure, cb):
    c_cols = [[ '_atom_type_symbol', '_atom_type_oxidation_number' ]]
    c_data = [[ [ str(s) for s in structure.species ],
                [ str(s.ox_format) for s in structure.species ] ]]
    cb.AddCifItem(( c_cols, c_data ))

def add_cell_loop(structure, cb):
    a, b, c, alpha, beta, gamma = structure.lat_params
    cb['_cell_length_a'] = '%08f' % a
    cb['_cell_length_b'] = '%08f' % b
    cb['_cell_length_c'] = '%08f' % c
    cb['_cell_angle_alpha'] = '%08f' % alpha
    cb['_cell_angle_beta'] = '%08f' % beta
    cb['_cell_angle_gamma'] =  '%08f' % gamma
    cb['_cell_volume'] = '%08f' % structure.volume

def add_symmetry_loop(structure, cb, wrap=False):
    structure.group_atoms_by_symmetry()
    data = sym.get_symmetry_dataset(structure)
    eqd = dict( (i, e) for i, e in enumerate(data['equivalent_atoms']) )
    cb['_symmetry_space_group_name_H-M'] = str(data['international'])
    cb['_symmetry_Int_Tables_number'] = str(data['number'])
    ss_cols = [[ '_symmetry_equiv_pos_site_id', '_symmetry_equiv_pos_as_xyz']]
    ss_data = [[ [ str(i+1) for i in range(len(data['rotations'])) ],
                 [ str(sym.Operation.get((r, t))) for r, t in 
                             zip(data['rotations'], data['translations']) ] ]]
    cb.AddCifItem(( ss_cols, ss_data ))
    a_rows = [[ '_atom_site_label', '_atom_site_type_symbol',
                '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z', 
                '_atom_site_Wyckoff_symbol',
                '_atom_site_occupancy' ]]
    a_data = [ [ str('%s%d' % (a.element_id, eqd[i])) 
                      for i, a in enumerate(structure)],
                [ str('%s%+d' % (a.element_id, 
                    a.ox if a.ox else 0 ))
                                 for a in structure ],
                [ '%08f' % a.x for a in structure ], 
                [ '%08f' % a.y for a in structure ], 
                [ '%08f' % a.z for a in structure ], 
                [ str(data['wyckoffs'][i]) for i in range(len(structure)) ],
                [ '%08f' % a.occupancy for a in structure ] ]

    if wrap:
        tmparr = np.array(a_data).T.tolist()
        for a in list(tmparr):
            for i, j, k in itertools.product([0, 1], [0, 1], [0, 1]):
                if i == 0 and j == 0 and k == 0:
                    continue
                if ( float(a[2])+i <= 1 and 
                     float(a[3])+j <= 1 and
                     float(a[4])+k <= 1):
                    tmparr.append([ a[0], a[1], 
                        '%08f' % (float(a[2])+i),
                        '%08f' % (float(a[3])+j),
                        '%08f' % (float(a[4])+k),
                        a[5], a[6]])
        tmparr = sorted(tmparr, key=lambda x: x[0])
        a_data = np.array(tmparr).T.tolist()
    cb.AddCifItem(( a_rows, [a_data] ))

def make_cif_block(structure, wrap=False):
    cb = CifBlock()
    add_cell_loop(structure, cb)
    add_symmetry_loop(structure, cb, wrap=wrap)
    add_comp_loop(structure, cb)
    return cb

def write_cif(structures, wrap=False):
    cif = CifFile()
    if not isinstance(structures, list):
        structures=[structures]
    for i, structure in enumerate(structures):
        cif['structure_%d' % i ] = make_cif_block(structure, wrap=wrap)
    return str(cif)
