#!/usr/bin/env python

from numpy import *
from collections import defaultdict
import os.path
import time
import qmpy
import StringIO

from qmpy.utils import *

THERMOPY_LIB_PATH = qmpy.INSTALL_PATH+'/data/thermodynamic/'

class PhaseError(Exception):
    pass

class PhaseDataError(Exception):
    pass

class PhaseData(object):
    def __init__(self):
        self._phases = []
        self._phase_dict = {}

    def __eq__(self, other):
        if self.space != other.space:
            return False
        if any( abs(self.unit_comp[k] - other.unit_comp[k]) > 1e-6 for k in
                self.unit_comp.keys() ):
            return False
        if abs( self.energy - other.energy ) > 1e-6:
            return False

    @property
    def phases(self):
        '''
        Return all phases.
        '''
        return self._phases

    @phases.setter
    def phases(self, phases):
        self._phases = phases
        self._phase_dict = None

    @property
    def phase_dict(self):
        if not self._phase_dict:
            self.get_phase_dict()
        return self._phase_dict

    @phase_dict.setter
    def phase_dict(self, phase_dict):
        self._phase_dict = phase_dict

    @property
    def space(self):
        space = set()
        for p in self.phases:
            space |= p.space
        return space

    ### Methods

    def get_phase_dict(self):
        '''
        Dictionary of phase.name:phase, such that each composition is mapped to
        the lowest energy phase at that composition.

        Example:
        >>> pd = PhaseData()
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-3))
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-4))
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-5))
        >>> pd.phase_dict
        {'Fe2O3': <Phase Fe2O3 : -5}
        '''
        phase_dict = {}
        for p in self.phases:
            if not p.name in phase_dict:
                phase_dict[p.name] = p
            else:
                if p.energy < phase_dict[p.name].energy:
                    phase_dict[p.name] = p
        self.phase_dict = phase_dict

    def add_phase(self, phase):
        '''
        Add a phase, updated the phase dictionary appropriately.
        '''
        self.phases.append(phase)
        if not phase.name in self.phase_dict:
            self.phase_dict[phase.name] = phase
        else:
            if phase.energy < self.phase_dict[phase.name].energy:
                self.phase_dict[phase.name] = phase

    def add_phases(self, phases):
        for phase in phases:
            self.add_phase(phase)

    def load_library(self, library):
        '''
        Load a library file, containing self-consistent thermochemical data.
        
        '''
        self.read_file(qmpy.INSTALL_PATH+'/data/thermodata/'+library)

    def load_oqmd(self, space=None, search={}, stable=False):
        from qmpy.analysis.vasp.calculation import Calculation
        from qmpy.materials.element import Element
        data = Calculation.objects.exclude(delta_e=None)
        #if stable:
        #    data = data.exclude(stability__lte=0)
        if search:
            data = data.filter(**search)
        if space:
            space_qs = Element.objects.exclude(symbol__in=space)
            data = data.filter(composition__element_set__in=space)
            data = data.exclude(composition__element_set__in=space_qs)

        for p in data:
            self.add_phase(p.phase)

    def read_file(self, filename, per_atom=True):
        '''
        Read in a thermodata file (named filename), formatted as 
        "composition energy [description]"

        E.g.

        composition energy
        Fe 0.0
        O 0.0
        Li 0.0
        Fe3O4 -0.21331204979
        FeO -0.589343204057
        Fe3O4 -0.21331204979
        FeLiO2 -0.446739168889
        FeLi5O4 -0.198830531099
        '''
        if isinstance(filename, basestring):
            fileobj = open(filename)
        elif isinstance(filename, file):
            fileobj = filename
        elif isinstance(filename, type(StringIO.StringIO())):
            fileobj = filename
            fileobj.name = None
        thermodata = fileobj.readlines()
        headers = [ h.lower() for h in thermodata.pop(0).strip().split() ]
        if 'composition' not in headers:
            raise PhaseDataError("Found columns: %s. Must provide composition in\
                                  a column labelled composition." % 
                                  (', '.join(headers)))
        if ('energy' not in headers and 'delta_e' not in headers):
            raise PhaseDataError("Found columns: %s. Must provide energies in\
                                  a column labelled delta_e or energy." % 
                                  (', '.join(headers)))

        keywords = {'energy':'energy', 'composition':'composition', 
                'delta_e':'energy', 'delta_h':'energy', 'delta_g':'energy',
                'comp':'composition', 'name':'composition', 
                'desc':'description', 'description':'description'}

        headers = [ keywords[h] for h in headers if h in keywords ]

        for i, line in enumerate(thermodata):
            line = line.strip().split()
            if not line:
                continue
            ddict = dict(zip(headers, line))
            phase = Phase(composition=ddict['composition'],
                          energy=float(ddict['energy']),
                          description=ddict.get('description', 
                              '{file}:{line}'.format(file=fileobj.name, line=i)),
                          per_atom=per_atom)
            self.add_phase(phase)

class Phase(object):
    '''
    A Phase represents a computed formation energy, and its corresponding
    composition. Phases will also have description which indicates something
    about its source. If loaded from OQMD the Formation object imported can be
    accessed by Phase._formation and the formation id can be accessed
    by Phase.id.
    '''

    def __init__(self, 
            composition=None, 
            energy=None, 
            description='',
            per_atom=True,
            name=''):

        if composition is None or energy is None:
            raise IncompletePhaseError
        if isinstance(composition, basestring):
            composition = parse_comp(composition)

        self._unit_comp = None
        self._nom_comp = None
        self._space = None
        self._latex = None
        self._meta_stability = None
        self._name = name
        self._description = description
        self._comp = defaultdict(float, composition)
        self._formation = None
        self._phase_dict = None
        self._gap = None
        self.id = None

        if not per_atom:
            self._total_energy = energy
            self._energy = energy/sum(composition.values())
            self._energy_pfu = energy / sum(self.nom_comp.values())
        else:
            self._energy = energy
            self._total_energy = energy * sum(composition.values())
            self._energy_pfu = energy / sum(self.nom_comp.values())

        if len(composition) == 1:
            self._energy = 0
            self._total_energy = 0
            self._energy_pfu = 0

    @staticmethod
    def from_phases(phase_dict):
        '''
        Generate a Phase object from a dictionary of Phase objects. Returns a
        composite phase of unit composition.
        '''
        if len(phase_dict) == 1:
            return phase_dict.keys()[0]

        pkeys = sorted(phase_dict.keys(), key=lambda x: x.name)
        energy = sum([ amt*p.energy for p, amt in phase_dict.items() ])
        name = ''
        latex = ''
        for p in pkeys:
            amt = phase_dict[p]
            if amt < 1e-3:
                continue
            if amt == 1:
                name += p.name
                latex += p.latex
            else:
                name += '%s %s' % (round(amt,3), p.name)
                latex += '%s %s' % (round(amt,3), p.latex)
            name += ' + '
            latex += ' + '
        name = name.rstrip(' + ')
        latex = latex.rstrip(' + ')

        comp = defaultdict(float)
        for p, factor in phase_dict.items():
            for e, amt in p.unit_comp.items():
                comp[e] += amt*factor

        phase = Phase(
                composition=comp,
                energy=energy,
                per_atom=False)
        phase._name = name
        phase._latex = latex
        phase._phase_dict = phase_dict
        return phase

    def __repr__(self):
        if self._description:
            return '<Phase {name} ({description}): {energy}>'.format(
                    name=self.name, energy=self.energy, description=self._description)
        else:
            return '<Phase {name} : {energy}>'.format(
                    name=self.name, energy=self.energy)

    def __eq__(self,other):
        '''
        Phases are defined to be equal if they have the same composition and an
        energy within 1e-6 eV/atom.
        '''
        if set(self.comp) != set(other.comp):
            return False
        if abs(self.energy - other.energy) > 1e-6:
            return False
        for key in self.comp:
            if abs(self.unit_comp[key]-other.unit_comp[key]) > 1e-6:
                return False
        return True

    #### Attributes

    @property
    def name(self):
        '''
        Alphabetical ordering of composition.
        '''
        if not self._name:
            self._name = format_comp(self.comp, special='reduce')
        return self._name

    @property
    def volume(self):
        if self._phase_dict is not None:
            return sum( phase.formation.entry.volume*amt for phase, amt in
                    self._phase_dict.items() )
        else:
            return self.formation.entry.volume

    @property
    def mass(self):
        if self._phase_dict is not None:
            return sum( phase.formation.composition.mass*amt for phase, amt in
                    self._phase_dict.items() )
        else:
            return self.formation.composition.mass

    @property
    def space(self):
        '''
        Set of elements in the phase.
        '''
        return set([ k for k, v in self.unit_comp.items() 
            if abs(v) > 1e-6 ])

    @property
    def n(self):
        '''
        Number of atoms in the total composition.
        '''
        return sum(self._comp.values())

    @property
    def name(self):
        return format_comp(self.comp)

    @property
    def comp(self):
        '''
        Total composition.
        '''
        return self._comp

    @property
    def unit_comp(self):
        '''
        Unit composition.
        '''
        return unit_comp(self.comp)

    @property
    def nom_comp(self):
        '''
        Composition divided by the GCD. e.g. Fe4O6 becomes Fe2O3.
        '''
        return reduce_comp(self.comp)

    @property
    def latex(self):
        '''
        LaTeX friendly format of name.
        '''
        return latex_comp(self.nom_comp)

    @property
    def name(self):
        return format_comp(reduce_comp(self.comp))

    @property
    def description(self):
        '''
        Some description of the phase origin.
        '''
        return self._description

    @property
    def energy(self):
        '''
        Energy per atom in eV.
        '''
        return self._energy

    @property
    def total_energy(self):
        '''
        Total energy for the composition as supplied (in eV).
        '''
        return self._total_energy

    @property
    def energy_pfu(self):
        '''
        Energy per nominal composition. i.e. energy per Fe2O3, not Fe4O6.
        '''
        return self._energy_pfu

    @property
    def formation(self):
        '''
        OQMD Formation object, if it exists.
        '''
        if self._formation is None:
            self.get_formation()
        return self._formation

    @property
    def band_gap(self):
        if not self._gap:
            self.get_gap()
        return self._gap

    def get_gap(self):
        if not self._phase_dict:
            self._gap = self.formation.calculation.band_gap
        else:
            self._gap = min([ p.formation.calculation.band_gap for p in
                self._phase_dict ])

    #### Methods

    @property
    def calculation(self):
        '''
        Get the oqmd Formation object for this Phase, if it exists.
        '''
        if self.id is None:
            return
        from qmpy.analysis.vasp.calculation import Calculation
        return Calculation.objects.get(id=self.id)

    def free_energy(self, T=0, P=0, mus={}):
        '''
        Free energy function for the phase, can be defined to be anything, by
        default it just returns the phase's ground state energy.
        '''
        #global environment
        return self._energy

    def fraction(self, comp):
        '''
        Returns a composition dictionary with the specified composition pulled
        out as 'var'. 

        Example:
        >>> phase = Phase(composition={'Fe':1, 'Li':5, 'O'8'}, energy=-1)
        >>> phase.fraction('Li2O')
        defaultdict(<type 'float'>, {'var': 2.5, 'Fe': 1, 'O': 5.5, 'Li': 0.0})
        '''
        if isinstance(comp, Phase):
            comp = comp.unit_comp
        elif isinstance(comp, basestring):
            comp = parse_comp(comp, special='unit')
        residual = defaultdict(float, self.unit_comp)
        tot = sum(residual.values())
        for c, amt in dict(comp).items():
            pres = residual[c]/amt
            for c2, amt2 in comp.items():
                residual[c2] -= pres*amt2
        residual['var'] = (tot - sum(residual.values()))
        residual['var'] /= float(sum(comp.values()))
        return residual
