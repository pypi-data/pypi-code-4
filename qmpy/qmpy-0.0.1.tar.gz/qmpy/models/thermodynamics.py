from django.db import models
import json

from utils import *
from thermopy import *

### things for efficiently indexing the master entries

class Fit(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    experiments = models.ManyToManyField('Experiment')
    dft = models.ManyToManyField('Calculation')
    fit_elements = models.ManyToManyField('Element')
    fit_hubbards = models.ManyToManyField('Hubbard')
    class Meta:
        db_table = 'fits'

    def __str__(self):
        return self.name

    def formation(self, calculation):
        adjust = 0.0
        for elt, amt in calculation.input.unit_comp.items():
            if self.mu_set.filter(element_id=elt).exists():
                adjust -= amt*self.mu_set.get(element_id=elt).energy
            else:
                adjust -= amt*Element.get(elt).base_mu

        for hub in calculation.hubbards:
            if hub in list(self.fit_hubbards.all()):
                if not self.hubbardmu_set.filter(hubbard=hub).exists():
                    continue
                amt = calculation.input.unit_comp[hub.element_id]
                adjust -= self.hubbardmu_set.get(hubbard=hub).energy*amt
        n = calculation.input.natoms
        form, created = Formation.objects.get_or_create(delta_e=calculation.energy_pa + adjust,
                calculation=calculation, fit=self)
        if created:
            form.save()
        return form

    def compute_new_formations(self):
        from calculation import Calculation
        print 'import successful'
        calcs = Calculation.objects.filter(settings='standard',
                done=True).exclude(formation__fit=self)
        for calc in calcs:
            print calc.entry.name
            form = self.formation(calc)
            form.composition = calc.composition
            form.entry = calc.entry
            form.description = calc.entry.label
            form.save()

    def compute_expt_formations(self):
        from calculation import Calculation
        print 'import successful'
        calcs = Calculation.objects.filter(settings='standard',
                done=True, composition__experiment__dft=False).\
                        exclude(formation__fit=self)
        for calc in calcs.distinct():
            print calc.entry.name
            form = self.formation(calc)
            form.composition = calc.composition
            form.entry = calc.entry
            form.description = calc.entry.label
            form.save()

    def compute_all_formations(self):
        from calculation import Calculation
        print 'import successful'
        calcs = Calculation.objects.filter(settings='standard', done=True)
        print 'Todo:', calcs.count()
        for calc in calcs:
            print calc.entry.name
            form = self.formation(calc)
            form.composition = calc.composition
            form.entry = calc.entry
            form.description = calc.entry.label
            form.save()

    @staticmethod
    def get(fitting):
        fit = Fit.objects.filter(name=fitting)
        if not fit.exists():
            print 'Fit by that name doesn\'t exist. Try one of:'
            for f in Fit.objects.all():
                print '   -', f.name
        return fit[0]

    @staticmethod
    def create(label=None, calculations=None, experiments=None, fit_for=[]):
        data = []
        hub_data = []
        fit, created = Fit.objects.get_or_create(name=label)
        if created:
            fit.save()
        fit.formation_set.all().delete()
        fit.mu_set.all().delete()
        fit.hubbardmu_set.all().delete() # fresh start on mus

        elements = set()  # list of all elements in any compound in fit
        hubbards = set() # list of all hubbards in any calc in fit
        fit_set = set(fit_for)
        expts = {}
        calcs = {}

        for expt in experiments:
            if expt.delta_e is None:
                continue
            #name = expt.composition.name
            if not set(expt.comp.keys()) & fit_set:
                continue

            if not expt.name in expts:
                expts[expt.name] = expt

            elif expt.delta_e < expts[expt.name].delta_e:
                expts[expt.name] = expt

        for calc in calculations:
            if calc.energy_pa is None:
                continue
            if not set(calc.composition.comp.keys()) & fit_set:
                print 'nothing from', calc.composition.comp.keys(), 'in', fit_set
                continue
            name = calc.composition.name
            if not name in calcs:
                calcs[name] = calc
            elif calc.energy_pa < calcs[name].energy_pa:
                calcs[name] = calc

        valid_pairs = set(calcs.keys()) & set(expts.keys())
        for name in valid_pairs:
            fit.experiments.add(expts[name])
            fit.dft.add(calcs[name])
            for elt in name_to_comp(name):
                elements.add(elt)
            if not calcs[name].hubbard:
                data.append(name)
            else:
                hub_data.append(name)
                for hub in calcs[name].hubbards:
                    if hub: 
                        hubbards.add(hub)

        elements = list(elements)
        hubbards = list(hubbards)
        hubbard_elements = [ hub.element.symbol for hub in hubbards ]

        A = []
        b = []
        base_mus = dict( (elt, Element.get(elt).mu) for elt in elements)
        pprint(base_mus)
        for elt, mu in base_mus.items():
            elt = Element.get(elt)
            elt.base_mu = mu
            elt.save()

        for name in data:
            unit_comp = name_to_comp(name, special='unit')
            # remove non-fitting elements
            print name, calcs[name].energy_pa, expts[name].delta_e
            b.append(calcs[name].energy_pa - expts[name].delta_e - sum( base_mus[elt]*amt 
                    for elt, amt in unit_comp.items() if elt not in fit_for ))
            A.append([ unit_comp[elt] for elt in fit_for ])

        A = np.array(A)
        b = np.array(b)
#        if len(A) == 0 and len(b) == 0:
#            print 'Nothing in fit set. What did you do wrong?'
#            exit()

        result = np.linalg.lstsq(A, b)
        element_mus = dict(zip(fit_for, result[0]))

        ### Second fit
        A = []
        b = []
        for name in hub_data:
            print 'hubbard:', name, calcs[name].energy_pa, expts[name].delta_e
            unit_comp = name_to_comp(name, special='unit')
            b.append(calcs[name].energy_pa - expts[name].delta_e -
                    sum( base_mus[elt]*amt
                        for elt, amt in unit_comp.items() 
                        if elt not in fit_for) - 
                    sum( element_mus[elt]*amt
                        for elt, amt in unit_comp.items()
                        if elt in fit_for))
            A.append([ unit_comp[elt] for elt in hubbard_elements ])

        A = np.array(A)
        b = np.array(b)
 #       if len(A) == 0 and len(b) == 0:
 #           print 'Nothing in fit set. What did you do wrong?'
 #           exit()
        result = np.linalg.lstsq(A, b)
        hubbard_mus = dict(zip(hubbards, result[0]))

        pprint(hubbard_mus)
        fit.save()

        for elt, val in element_mus.items():
            elt = Element.get(elt)
            print elt, val
            mu = Mu(element=elt, energy=val, fitting=fit)
            mu.save()
            fit.fit_elements.add(elt)

        for hub, val in hubbard_mus.items():
            print hub, val
            hubmu = HubbardMu(hubbard=hub, energy=val, fitting=fit)
            hubmu.save()
            fit.fit_hubbards.add(hub)

        fit.save()
        return fit

    @property
    def mu_dict(self):
        mdict = {}
        for mu in self.mu_set.all():
            mdict[mu.element.symbol] = mu.energy
        return mdict

    @property
    def hub_dict(self):
        hdict = defaultdict(float)
        for hub in self.hubbardmu_set.all():
            hdict[hub.element.symbol] = hub.energy
        return hdict
            
class HubbardMu(models.Model):
    hubbard = models.ForeignKey('Hubbard')
    energy = models.FloatField()
    fitting = models.ForeignKey(Fit)

    class Meta:
        db_table = 'hubbard_mus'

    def __str__(self):
        return '%s=%s' % (self.hubbard.element, self.energy)

class Mu(models.Model):
    element = models.ForeignKey('Element',
            related_name='mus')
    energy = models.FloatField()
    fitting = models.ForeignKey(Fit)

    class Meta:
        db_table = 'mus'

    def __str__(self):
        return '%s=%s' % (self.element, self.energy)


class Formation(models.Model):
    entry = models.ForeignKey('Entry', null=True, blank=True)
    composition = models.ForeignKey('Composition', null=True, blank=True)
    calculation = models.ForeignKey('Calculation', null=True, blank=True)
    description = models.CharField(max_length=20, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    fit = models.ForeignKey('Fit', null=True)
    hull_distance = models.FloatField(null=True)
    delta_e = models.FloatField(null=True)
    tielines = models.ManyToManyField('self')

    phase = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'formations'

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    @staticmethod
    def get(calculation, fit='standard'):
        fit = Fit.get(fit)
        form = fit.formation(calculation)
        form.composition = calculation.composition
        form.entry = calculation.entry
        form.description = form.entry.label
        form.save()
        return form.delta_e

    @property
    def phase(self):
        return Phase(energy=self.delta_e, 
                composition=self.composition.comp, 
                description=self.id,
                #description=self.calculation.entry.label,
                normalize_energy=False)

    @property
    def pop_string(self):
        template='''$structure: {comment}
CREATE_NEW_EQUILIBRIUM {id},1
SET-CONDITION P=101325,T=298.15,{composition}
EXPERIMENT H={energy}:1000'''
        comp = self.composition.comp
        composition = ', '.join([ 'N(%s)=%s' % (elt, amt) for 
            elt, amt in comp.items() ])
        energy = 96485.3*self.delta_e*sum(comp.values())
        return template.format(
                comment=self.entry.label,
                composition=composition, 
                energy=energy,
                id=self.id)


    def find_tie_lines(self):
        space = PhaseSpace()
        for formation in Formation.objects.get(fit=self.fit):
            break

class Equilibria(models.Model):
    fit = models.ForeignKey('Fit')
    members = models.ManyToManyField('Formation')
