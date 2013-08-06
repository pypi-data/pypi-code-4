from django.db import models
import json

from utils import *
from element import Element, ElementSet
from thermodynamics import Formation
from thermopy import PhaseSpace

##TODO
## - define properties seperate from methods

class Composition(models.Model):
    '''
    A composition object represents a point in composition space - i.e. it has
    a defined elemental composition, but not a defined structure. As such it
    can correspond to many structures, many experiments, and has a single
    valued meidema energy and hull energy.
    '''

    formula = models.CharField(primary_key=True, max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    keywords = models.CharField(max_length=255, null=False)

    element = models.ManyToManyField('Element', null=True)
    ntypes = models.IntegerField(null=True)

    ### other stuff

    mass = models.FloatField(blank=True, null=True)

    ### thermodyanamic stuff

    meidema = models.FloatField(blank=True, null=True)
    matproj = models.FloatField(blank=True, null=True)
    oqmd = models.FloatField(blank=True, null=True)
    icsd = models.FloatField(blank=True, null=True)
    expt = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'compositions'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = comp_to_name(self.comp, special='reduce')
        self.ntypes = len(self.comp)
        self.meidema = get_energy(self.comp)
        super(Composition, self).save(*args, **kwargs)
        if not self.element.count():
            for elt in self.comp:
                self.element.add(Element.get(elt))

    @property
    def summary(self):
        summary = 'Summary of %s:\n' % self.name
        sums = {}
        for k, v in self.distinct.items():
            s = '   - %s (SG# %s, %s atoms): ' % (v.path, k[0], k[1])
            if not v.tasks:
                print 'Not queued for some reason'
            elif v.holds:
                s += 'held for %s' % ', '.join(v.holds.split())
                sums[s] = 30000
            elif v.tasks[0].state==1:
                s += 'running'
                sums[s] = 20000
            elif not v.oqmd:
                sums[s] = 10000
            else:
                s += '%s' % v.oqmd.energy_pa
                sums[s] = v.oqmd.energy_pa

        sums = sorted( sums.keys(), key=lambda x: sums[x])
        summary += '\n'.join(sums)
        return summary

    @staticmethod
    def get(composition):
        if isinstance(composition, basestring):
            composition = name_to_comp(composition)
        cs, created = Composition.objects.get_or_create(
                formula=comp_to_formula(composition, special='reduce'))
        return cs

    @staticmethod
    def get_space(bounds):
        if isinstance(bounds, list):
            bounds = '-'.join(bounds)
        space = PhaseSpace(bounds, load=None)
        phases = []
        comps = Composition.objects.none()
        elts = [ Element.get(elt) for elt in space.space ]
        for i in range(len(space.space)):
            for combi in itertools.combinations(elts, r=i+1):
                for elt in combi:
                    comps |= elt.composition_set.filter(ntypes=i+1)
        comps = comps.values_list('formula', flat=True)
        for comp in comps:
            cdict = name_to_comp(comp)
            if space.in_space(cdict):
                phases.append(Composition.objects.get(formula=comp))
        return phases

    @property
    def calculable(self):
        return list(self.entry_set.filter(holds=''))

    @property
    def distinct(self):
        if not hasattr(self, '_distinct'):
            self.get_distinct(icsd=False)
        return self._unique

    @property
    def icsd_distinct(self):
        if not hasattr(self, '_distinct'):
            self.get_distinct(icsd=True)
        return self._unique

    @property
    def duplicates(self):
        if not hasattr(self, '_duplicates'):
            self.get_distinct(icsd=True)
        return self._duplicates

    def get_distinct(self, icsd=False, calculable=True, high_pressure=True):
        unique = {}
        duplicates = defaultdict(list)
        entries = self.entry_set.filter(structure__label='source')
        if not high_pressure:
            entries = entries.exclude(keywords__contains='pressure')
        if icsd:
            entries = entries.filter(path__contains='icsd')
        if calculable:
            entries = entries.filter(holds='')
        for entry in entries:
            inp = entry.input
            if not inp.spacegroup:
                inp.find_symmetry()
                inp.save()
            if icsd:
                sg = entry.icsd.spacegroup
            else:
                sg = inp.spacegroup

            duplicates[(sg, inp.natoms)].append(entry)
            if not (sg, inp.natoms) in unique:
                unique[(sg, inp.natoms)] = entry
            if (entry.is_done('standard') and not
                    unique[(sg, inp.natoms)].is_done('standard')):
                unique[(sg, inp.natoms)] = entry

        for entry in unique.values():
            entry.unique = True
            entry.save()

        self._unique = unique
        self._duplicates = duplicates

    @property
    def comp(self):
        return defaultdict(float, 
                name_to_comp(self.formula))

    @property
    def nom_comp(self):
        return defaultdict(float, 
                name_to_comp(self.formula, special='reduce'))

    @property
    def unit_comp(self):
        return defaultdict(float,
                name_to_comp(self.formula, special='unit'))

    def set_thermo(self, fit='standard'):
        expt = self.experiment_set.filter(dft=True).order_by('delta_e')
        if expt.exists():
            self.matproj = expt[0].delta_e

        expt = self.experiment_set.filter(dft=False).order_by('delta_e')
        if expt.exists():
            self.expt = expt[0].delta_e
        if expt.filter(source='ssub').exists():
            self.expt = expt.filter(source='ssub')[0].delta_e
        if expt.filter(comment='correction').exists():
            self.expt = expt.filter(comment='correction')[0].delta_e

        forms = self.formation_set.filter(fit=fit).order_by('delta_e')
        if forms.exists():
            self.oqmd = forms[0].delta_e

        f1 = forms.filter(calculation__path__contains='icsd')
        f2 = f1.order_by('delta_e')
        if f2.exists():
            self.icsd = f2[0].delta_e

        self.meidema = get_energy(self.comp)

    @property
    def gs(self):
        calcs = self.calculation_set.filter(settings='standard', done=True)
        calcs = calcs.filter(path__contains='icsd')
        calcs = calcs.order_by('energy_pa')
        if calcs.exists():
            return calcs[0]
        else:
            return None

    @property
    def hubbard(self):
        return any( hub for hub in self.gs.hubbards )

    @property
    def volume(self):
        if self.gs is not None:
            return self.gs.volume_pa
        else:
            return None

    ## keywords
    def add_keyword(self, keyword):
        keywords = self.get_keywords()
        if keyword not in keywords:
            keywords.append(keyword)
        self.keywords = ' '.join(keywords)

    def get_keywords(self):
        return self.keywords.strip().split(' ')

    def remove_keyword(self, keyword):
        keywords = self.keywords
        keywords.remove(keyword)
        self.keywords = ' '.join(keywords)

    @property
    def latex(self):
        return comp_to_latex(self.comp)
