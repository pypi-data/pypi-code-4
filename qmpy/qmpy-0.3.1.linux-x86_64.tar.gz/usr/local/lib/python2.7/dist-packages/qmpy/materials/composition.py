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
        formula             : Unique composition string
        meta_data           : MetaData objects, have a Type and Value.
        element_set         : QuerySet of Element objects
        ntypes              : Number of elements in the composition

        mass                : Mass/atom of the composition (assuming normal
                              isotopes)
        meidema             : Composition energy as computed by the Meidema
                              model
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

    def __str__(self):
        return self.formula

    def __eq__(self, other):
        if self.space != other.space:
            return False
        for k in self.space:
            if abs(self.unit_comp[k] - other.unit_comp[k]) > 1e-4:
                return False
        return True

    def save(self, *args, **kwargs):
        '''
        Overriden save function - assigns ntypes and the element_set.
        '''
        self.ntypes = len(self.comp)
        super(Composition, self).save(*args, **kwargs)
        self.element_set = [ Element.get(e) for e in self.comp.keys() ]

    @classmethod
    def get(cls, composition):
        '''
        Classmethod for getting Composition objects - if the Composition
        existsin the database, it is returned. If not, a new Composition is
        created.

        Example:
        >>> Composition.get('Fe2O3')
        <Composition: Fe2O3>
        '''
        if isinstance(composition, basestring):
            composition = parse_comp(composition)
        comp = reduce_comp(composition)
        comp, created = cls.objects.get_or_create(formula=format_comp(comp))
        if created:
            comp.ntypes = len(comp.comp)
            comp.elements = comp.comp.keys()
        return comp

    @classmethod
    def get_list(cls, bounds, calculated=False):
        '''
        Classmethod for finding all compositions within the space bounded by a
        sequence of compositions. 

        Example:
        >>> Composition.get_list(['Fe','O'])
        [<Composition: Fe>, <Composition: O>, <Composition: Fe2O3>,
        <Composition: Fe3O4>, <Composition: FeO>, <Composition: Fe107O125>,
        <Composition: Fe37O38>, <Composition: Fe49O52>, <Composition: Fe16O17>,
        <Composition: Fe9O10>, <Composition: Fe113O124>, <Composition:
        Fe11O12>, <Composition: Fe0.929O>, <Composition: Fe41O44>]
        >>> Composition.get_list('Fe-O', calculated=True)
        [<Composition: Fe>, <Composition: O>, <Composition: Fe2O3>,
        <Composition: Fe3O4>, <Composition: FeO>]
        '''
        space = set()
        if isinstance(bounds, basestring):
            bounds = bounds.split('-')
        if len(bounds) == 1:
            return [Composition.get(bounds[0])]
        for b in bounds:
            bound = parse_comp(b)
            space |= set(bound.keys())
        in_elts = Element.objects.filter(symbol__in=space)
        out_elts = Element.objects.exclude(symbol__in=space)
        comps = Composition.objects.filter(element_set__in=in_elts,
                ntypes__lt=len(space))
        comps = Composition.objects.exclude(element_set__in=out_elts)
        comps = comps.exclude(entry=None)
        if calculated:
            comps = comps.exclude(calculation=None)
            #comps = comps.filter(calculation__label__in=['static', 'standard'])
        return comps.distinct()

    @property
    def ground_state(self):
        '''Return the most stable entry at the composition.'''
        return self.sorted_distinct[0]

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
    def sorted_distinct(self):
        '''Return a list of entries, sorted by formation energy.'''
        return sorted(self.distinct.values(), key=lambda x: 
                100 if x.energy is None else x.energy )

    @property
    def delta_e(self):
        '''Return the lowest formation energy.'''
        calcs = self.calculation_set.exclude(delta_e=None)
        if not calcs.exists():
            return
        return min(calcs.values_list('delta_e', flat=True))

    @property
    def icsd_delta_e(self):
        '''
        Return the lowest formation energy calculated from experimentally
        measured structures - i.e. excluding prototypes.
        '''
        calcs = self.calculation_set.exclude(delta_e=None)
        calcs = calcs.filter(path__contains='icsd')
        if not calcs.exists():
            return
        return min(calcs.values_list('delta_e', flat=True))

    @property
    def ndistinct(self):
        '''Return the number of distinct entries.'''
        return len(self.distinct)

    @property
    def comp(self):
        '''Return an element:amount composition dictionary.'''
        return parse_comp(self.formula)

    @property
    def unit_comp(self):
        '''
        Return an element:amoutn composition dictionary normalized to a unit
        composition.
        '''
        return normalize_comp(self.comp)

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
        '''Return the set of element symbols'''
        return set(self.comp.keys())

    # methods
    def get_distinct_entries(self):
        '''
        Return a dictionary of (spacegroup, natoms):Entry pairs.

        Example:
        >>> comp = Composition.get('Fe2O3')
        >>> comp.get_distinct_entries()
        {(96L, 56L): <Entry: 81763 : Fe2O3>, (167L, 30L): <Entry: 43528 :
        Fe2O3>, (60L, 20L): <Entry: 56783 : Fe2O3>, (143L, 30L): <Entry: 47007
        : Fe2O3>, (167L, 10L): <Entry: 76705 : Fe2O3>}
        '''
        uniq = {}
        duplicates = defaultdict(list)
        entries = self.entry_set.all()
        for entry in entries:
            sg = entry.input.spacegroup.number
            natoms = entry.input.natoms
            key = (sg, natoms)
            duplicates[key].append(entry)
            if key not in uniq:
                uniq[key] = entry
            elif not entry.energy is None:
                if uniq[key].energy is None:
                    uniq[key] = entry
                elif uniq[key].energy > entry.energy:
                    uniq[key] = entry
        self._duplicates = duplicates
        self._unique = uniq
        return self._unique

    @property
    def experiment(self):
        '''Return the lowest experimantally measured formation energy at the
        compositoin.
        '''
        expts = self.experimentalformationenergy_set.filter(dft=False)
        if not expts.exists():
            return
        return min(expts.values_list('delta_e', flat=True))
