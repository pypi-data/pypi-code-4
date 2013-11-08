#/usr/bin/env python
# -*- coding: utf-8 -*-

from cif import read_cif, write_cif
from poscar import read_poscar, write_poscar
from ase_mapper import read_ase

class StructureFormatError(Exception):
    '''Problem reading an input file'''

class FormatNotSupportedError(Exception):
    '''The provided input format is not supported'''

def read(source_file, *args, **kwargs):
    if 'cif' in source_file:
        return read_cif(source_file, *args, **kwargs)
    elif ( 'POSCAR' in source_file or
            'CONTCAR' in source_file ):
        return read_poscar(source_file, *args, **kwargs)
    else:
        return read_ase(source_file, *args, **kwargs)
    raise FormatNotSupportedError('The file %s is in an unrecognized format\
            and cannot be read' % source_file)
