#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

from django.db import models

from qmpy.materials.element import Element
from qmpy.data.meta_data import *
from qmpy.utils import *

class Composition(models.Model):
    '''
    Database Attributes:

    Convenience Attributes:

    Methods:
    '''
    formula = models.CharField(primary_key=True, max_length=255, db_index=True)
    meta_data = models.ForeignKey('MetaData', null=True)

    element_set = models.ManyToManyField('Element', null=True)
    ntypes = models.IntegerField(null=True)

    ### other stuff
    mass = models.FloatField(blank=True, null=True)

    ### thermodyanamic stuff
    meidema = models.FloatField(blank=True, null=True)
    structure = models.ForeignKey('Structure', blank=True,
            null=True,
            related_name='+')

    _unique = None
    _duplicates = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'compositions'

    # builtins
    def __str__(self):
        return self.formula

    def __eq__(self, other):
        if self.space != other.space:
            return False
        for k in self.space:
            if abs(self.unit_comp[k] - other.unit_comp[k]) > 1e-4:
                return False
        return True

    # django overrides
    def save(self, *args, **kwargs):
        super(Composition, self).save(*args, **kwargs)
        self.element_set = [ Element.get(e) for e in self.comp.keys() ]

    # accessors
    @classmethod
    def get(cls, composition):
        if isinstance(composition, basestring):
            composition = parse_comp(composition)
        comp = reduce_comp(composition)
        comp, created = cls.objects.get_or_create(formula=format_comp(comp))
        if created:
            comp.ntypes = len(comp.comp)
            comp.elements = comp.comp.keys()
        return comp

    @classmethod
    def get_list(cls, bounds):
        space = set()
        if isinstance(bounds, basestring):
            bounds = bounds.split('-')
        if len(bounds) == 1:
            return [Composition.get(bounds[0])]
        for b in bounds:
            bound = parse_comp(b)
            space |= set(bound.keys())
        elts = Element.objects.exclude(symbol__in=space)
        comps = Composition.objects.exclude(element_set__in=elts)
        comps = comps.exclude(entry=None)
        return comps

    # django caching
    _elements = None

    @property
    def elements(self):
        if self._elements is None:
            self._elements = [ Element.get(e) for e in self.comp.keys() ]
        else:
            self._elements = list(self.element_set.all())
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = [ Element.get(e) for e in elements ]

    # calculated properties
    @property
    def distinct(self):
        if self._unique is None:
            self.get_distinct_entries()
        return self._unique

    @property
    def delta_e(self):
        calcs = self.calculation_set.exclude(delta_e=None)
        if not calcs.exists():
            return
        return min(calcs.values_list('delta_e', flat=True))

    @property
    def ndistinct(self):
        return len(self.distinct)

    @property
    def comp(self):
        return parse_comp(self.formula)

    @property
    def unit_comp(self):
        return normalize_comp(self.comp)

    @property
    def red_comp(self):
        return reduce_comp(self.comp)

    @property
    def name(self):
        return format_comp(reduce_comp(self.comp))

    @property
    def latex(self):
        return latex_comp(reduce_comp(self.comp))

    @property
    def html(self):
        return html_comp(reduce_comp(self.comp))

    @property
    def space(self):
        return set(self.comp.keys())

    # methods
    def get_distinct_entries(self):
        unique = {}
        duplicates = defaultdict(list)
        entries = self.entry_set.all()
        for entry in entries:
            sg = entry.input.spacegroup.number
            natoms = entry.input.natoms
            duplicates[(sg, natoms)].append(entry)
            if not (sg, natoms) in unique:
                unique[(sg, natoms)] = entry
            elif entry.delta_e < unique[(sg, natoms)].delta_e:
                unique[(sg, natoms)] = entry
        self._unique = unique
        self._duplicates = duplicates
