#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import warnings
import fractions as frac
import numpy as np

from django.db import models

from routines import *

class TranslationError(Exception):
    pass

class RotationError(Exception):
    pass

class OperationError(Exception):
    pass

class WyckoffSiteError(Exception):
    pass

class SpacegroupError(Exception):
    pass

class Translation(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'translations'

    @property
    def vector(self):
        return np.array([self.x, self.y, self.z])

    @vector.setter
    def vector(self, vector):
        self.x, self.y, self.z = vector

    @classmethod
    def get(cls, vector):
        fields = ['x', 'y', 'z']
        arr_dict = dict(zip(fields, vector))
        obj, new = cls.objects.get_or_create(**arr_dict)
        if new:
            obj.save()
        return obj

    def __str__(self):
        ops = []
        for t in self.vector:
            if t == 0:
                s = '0'
            elif t < 0:
                s = '-%s' % (frac.Fraction(str(t)))
            else:
                s = '+%s' % (frac.Fraction(str(t)))
            ops.append(s)
        return ','.join(ops)

class Rotation(models.Model):
    a11 = models.FloatField()
    a12 = models.FloatField()
    a13 = models.FloatField()
    a21 = models.FloatField()
    a22 = models.FloatField()
    a23 = models.FloatField()
    a31 = models.FloatField()
    a32 = models.FloatField()
    a33 = models.FloatField()

    class Meta:
        app_label = 'qmpy'
        db_table = 'rotations'

    @property 
    def matrix(self):
        return np.array([ 
            [ self.a11, self.a12, self.a13 ],
            [ self.a21, self.a22, self.a23 ],
            [ self.a31, self.a32, self.a33 ]])

    @matrix.setter
    def matrix(self, matrix):
        self.a11, self.a12, self.a13 = matrix[0]
        self.a21, self.a22, self.a23 = matrix[1]
        self.a31, self.a32, self.a33 = matrix[2]

    @classmethod
    def get(cls, matrix):
        fields = [ 'a11', 'a12', 'a13',
                   'a21', 'a22', 'a23',
                   'a31', 'a32', 'a33']
        matrix = np.ravel(matrix)
        mat_dict = dict(zip(fields, matrix))
        obj, new = cls.objects.get_or_create(**mat_dict)
        if new:
            obj.save()
        return obj

    def __str__(self):
        ops = []
        indict = {0:'x', 1:'y', 2:'z'}
        for r in self.matrix:
            s = ''
            for i, x in enumerate(r):
                if x == 0:
                    continue
                elif x == 1:
                    s += indict[i]
                elif x == -1:
                    s += '-'+indict[i]
                else:
                    f = frac.Fraction(str(x))
                    s += '%s%s' % (f, indict[i])
            ops.append(s)
        return ','.join(ops)

class Operation(models.Model):
    rotation = models.ForeignKey(Rotation)
    translation = models.ForeignKey(Translation)

    class Meta:
        app_label = 'qmpy'
        db_table = 'operations'

    @classmethod
    def get(cls, value):
        '''
        Accepts symmetry operation strings, i.e. "+x, x+1/2, x+y-z" or a tuple
        of rotation matrix and translation vector. 

        Example:
        >>> Operation.get("x,y,-y")
        >>> Operation.get(( rot, trans ))
        '''
        if isinstance(value, basestring):
            rot, trans = parse_sitesym(value)
        elif isinstance(value, tuple):
            rot, trans = value
        rot = Rotation.get(rot)
        trans = Translation.get(trans)
        op, new = cls.objects.get_or_create(rotation=rot, translation=trans)
        if new:
            op.save()
        return op

    def __str__(self):
        ops = []
        indict = {0:'x', 1:'y', 2:'z'}
        for r,t in zip(self.rotation.matrix, 
                       self.translation.vector):

            s = ''
            for i, x in enumerate(r):
                if x == 0:
                    continue
                elif x == 1:
                    s += indict[i]
                elif x == -1:
                    s += '-'+indict[i]
                else:
                    f = frac.Fraction(str(x)).limit_denominator(1000)
                    s += '%s%s' % (f, indict[i])

            if t == 0:
                pass
            elif t < 0:
                s += '-%s' % (frac.Fraction('%08f' % t))
            else:
                s += '+%s' % (frac.Fraction('%08f' % t))
            ops.append(s)
        return ','.join(ops)


class WyckoffSite(models.Model):
    spacegroup = models.ForeignKey('Spacegroup', related_name='site_set')
    symbol = models.CharField(max_length=1)
    multiplicity = models.IntegerField(blank=True, null=True)
    x = models.CharField(max_length=8)
    y = models.CharField(max_length=8)
    z = models.CharField(max_length=8)
    
    class Meta:
        app_label = 'qmpy'
        db_table = 'wyckoffsites'

    def __str__(self):
        return '%s%d' % (self.symbol, self.multiplicity)

    @classmethod
    def get(cls, symbol, spacegroup):
        site, new = cls.objects.get_or_create(spacegroup=spacegroup, 
                symbol=symbol)
        if new:
            site.save()
        return site

class Spacegroup(models.Model):
    number = models.IntegerField(primary_key=True)
    hm = models.CharField(max_length=30, blank=True, null=True)
    hall = models.CharField(max_length=30, blank=True, null=True)
    pearson = models.CharField(max_length=30)
    schoenflies = models.CharField(max_length=30)
    operations = models.ManyToManyField(Operation, null=True)
    centering_vectors = models.ManyToManyField(Translation)
    lattice_system = models.CharField(max_length=20)
    centrosymmetric = models.BooleanField()

    _sym_ops = None
    _rots = None
    _trans = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'spacegroups'

    def save(self, *args, **kwargs):
        super(Spacegroup, self).save(*args, **kwargs)
        for op in self.sym_ops:
            op.save()
        self.operations = self.sym_ops

    @property
    def sym_ops(self):
        if self._sym_ops is None:
            self._sym_ops = [ op for op in self.operations.all() ]
        return self._sym_ops

    @sym_ops.setter
    def sym_ops(self, sym_ops):
        self._sym_ops = sym_ops

    @property
    def rotations(self):
        if self._rots is None:
            self._rots = np.array([ op.rotation.matrix for op in self.sym_ops ])
        return self._rots

    @rotations.setter
    def rotations(self, rotations):
        self._rots = rotations

    @property
    def translations(self):
        if self._trans is None:
            self._trans = np.array([ op.translation.array for op in self.sym_ops ])
        return self._trans

    @translations.setter
    def translations(self, translations):
        self._trans = translations

    def __str__(self):
        return str(self.number)

    @property
    def wyckoff_sites(self):
        return self.site_set.all().order_by('symbol')

    @property
    def symbol(self):
        return self.hm

    def equivalent_sites(self, structure, symprec=1e-3):
        sites = []
        for atom in structure.uniq_atoms:
            for rot, trans in zip(self.rotations, self.translations):
                site = np.dot(rot, atom.coord) + trans
                site %= 1.0
                a = atom.copy()
                a.coord = site
                if not any( s == a for s in sites ):
                    sites.append(a)
        return sites

    def symmetry_normalised_sites(self, scaled_positions):
        """Returns an array of same size as *scaled_positions*,
        containing the corresponding symmetry-equivalent sites within
        the unit cell of lowest indices.

        Example:

        >>> from ase.lattice.spacegroup import Spacegroup
        >>> sg = Spacegroup(225)  # fcc
        >>> sg.symmetry_normalised_sites([[0.0, 0.5, 0.5], [1.0, 1.0, 0.0]])
        array([[ 0.,  0.,  0.],
               [ 0.,  0.,  0.]])
        """
        scaled = np.array(scaled_positions, ndmin=2)
        normalised = np.empty(scaled.shape, np.float)
        for i, pos in enumerate(scaled):
            sympos = np.dot(self.rotations, pos) + self.translations
            sympos %= 1.0
            sympos %= 1.0
            j = np.lexsort(sympos.T)[0]
            normalised[i,:] = sympos[j]
        return normalised

    def unique_sites(self, structure, symprec=1e-3, output_mask=False):
        scaled = np.array(structure.scaled_coords, ndmin=2)
        symnorm = self.symmetry_normalised_sites(scaled)
        perm = np.lexsort(symnorm.T)
        iperm = perm.argsort()
        xmask = np.abs(np.diff(symnorm[perm], axis=0)).max(axis=1) > symprec
        mask = np.concatenate(([True], xmask))
        imask = mask[iperm]
        if output_mask:
            return [ a for a, i in zip(structure.atoms, imask) if i ], imask
        else:
            return [ a for a, i in zip(structure.atoms, imask) if i ]

    @property
    def n_sym_ops(self):
        return self.operations.count()

    @property
    def n_wyckoff_sites(self):
        return self.site_set.count()

    def get_site(self, symbol):
        symol = symbol.strip('0123456789')
        return self.site_set.get(symbol__exact=symbol)
