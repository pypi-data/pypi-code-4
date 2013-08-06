#!/usr/bin/python

import subprocess
import tempfile
import os
from collections import defaultdict
from ase.io.cif import parse_cif
from numpy import argsort,array,dot
from numpy.linalg import inv

ochoice=[48,50,59,68,70,85,86,88,125,126,129,130,133,134,
        137,138,141,142,201,203,222,224,227,228]
uchoice=[3,4,5,6,7,8,9,10,11,12,13,14,15]
hchoice=[146,148,155,160,161,166,167]

def cif_to_poscar(cif):
    cif_data = parse_cif(cif)[0][1]
    a=cif_data['_cell_length_a']
    b=cif_data['_cell_length_b']
    c=cif_data['_cell_length_c']
    alpha = cif_data['_cell_angle_alpha']
    beta = cif_data['_cell_angle_beta']
    gamma = cif_data['_cell_angle_gamma']
    sg = cif_data['_symmetry_int_tables_number']
    sg_name = cif_data['_symmetry_space_group_name_h-m']

    origin=False
    if int(sg) in ochoice and sg_name.endswith('Z'):
        origin=2

    wyksites={}
    for i in range(len(cif_data['_atom_site_label'])):
        label = cif_data['_atom_site_label'][i]
        elt = ''.join(c for c in label if c.isalpha)
        wyksites[label] = {'elt':elt}
        wyksites[label]['multiple'] =\
                cif_data['_atom_site_symmetry_multiplicity'][i]

        wyksites[label]['pos'] = [
                cif_data['_atom_site_fract_x'][i],
                cif_data['_atom_site_fract_y'][i],
                cif_data['_atom_site_fract_z'][i]]

    tmp = tempfile.mkdtemp(dir='/dev/shm')
    cwd = os.getcwd()
    os.chdir(tmp)

    # Create gulp.in
    gulp_instr = 'single\ntitle\n'
    gulp_instr += 'filler\n'
    gulp_instr += 'end\ncell\n'
    gulp_instr += '%.8f %.8f %.8f &\n %.8f %.8f %.8f\n' % (
            a, b, c, alpha, beta, gamma)
    gulp_instr += 'frac\n'
    for site in wyksites.values():
        sstr = ' '.join([ str(coord) for coord in site['pos'] ])
        gulp_instr += '%s %s\n' % (site['elt'], sstr)
    gulp_instr += 'space\n'
    gulp_instr += '%s\n' % sg_name.rstrip('HSZR')
    if origin:
        gulp_instr += 'origin 2\n'
    target = tempfile.mktemp(dir=tmp, suffix='.xyz')
    gulp_instr += 'output xyz '+target

    # Run GULP
    p1 = subprocess.Popen(['echo',gulp_instr],
            stdout=subprocess.PIPE)
    p2 = subprocess.Popen('gulp40',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=p1.stdout)
    p2.wait()
    out, err = p2.communicate()

    if err:
        gulp_instr = 'single\ntitle\n'
        gulp_instr += 'filler\n'
        gulp_instr += 'end\ncell\n'
        gulp_instr += '%.8f %.8f %.8f &\n %.8f %.8f %.8f\n' % (
                a, b, c, alpha, beta, gamma)
        gulp_instr += 'frac\n'
        for site in wyksites.values():
            sstr = ' '.join([ str(coord) for coord in site['pos'] ])
            gulp_instr += '%s %s\n' % (site['elt'], sstr)
        gulp_instr += 'space\n'
        gulp_instr += '%s\n' % sg
        if origin:
            gulp_instr += 'origin 2\n'
        target = tempfile.mktemp(dir=tmp, suffix='.xyz')
        gulp_instr += 'output xyz '+target
        # Run GULP
        p1 = subprocess.Popen(['echo',gulp_instr],
                stdout=subprocess.PIPE)
        p2 = subprocess.Popen('gulp40',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=p1.stdout)
        p2.wait()
        out, err = p2.communicate()

    if err:
        raise Exception

    stdout = out.split('\n')
    for n, line in enumerate(stdout):
        if 'Cartesian' in line:
            latvecs = '\n'.join(stdout[n+2:n+5])

    os.chdir(cwd)
    coords = defaultdict(list)
    atom_data = open(target)
    for line in atom_data:
        line = line.split()
        if len(line) != 4:
            continue
        atom = [float(x) for x in line[1:]]
        elt = line[0]
        if elt in ['D', 'T']:
            elt = 'H'
        dup = False
        for coord in coords[elt]:
            if all([ abs(x1-x2) < 0.1 for x1, x2 in zip(coord, atom)]):
                dup = True
        if not dup:
            coords[elt].append(atom)

    ordered_keys = sorted(coords)

    outstr = ' '.join(ordered_keys)+"\n"
    outstr += "1.0\n"
    outstr += latvecs+"\n"
    outstr += ' '.join(ordered_keys)+'\n'
    outstr += ' '.join(str(len(coords[k])) for k in ordered_keys)+'\n'
    outstr += "Cartesian\n"
    for k in ordered_keys:
        for atom in coords[k]:
            outstr += '%.8f %.8f %.8f\n' % (atom[0], atom[1], atom[2])
    outstr.rstrip('\n')
    return outstr
