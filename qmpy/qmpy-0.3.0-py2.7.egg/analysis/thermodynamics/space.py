import numpy as np
import numpy.linalg
import itertools
import os
from collections import defaultdict
import networkx as nx
from scipy.spatial import ConvexHull
from pulp import *

from qmpy.utils import *
from phase import Phase, PhaseData
from reaction import Reaction

class PhaseSpaceError(Exception):
    pass

class PhaseSpace(object):
    '''
    A PhaseSpace object represents, naturally, a region of phase space. 
    
    The most fundamental property of a PhaseSpace is its bounds,
    which are given as a hyphen-delimited list of compositions. These represent
    the extent of the phase space, and determine which phases are within the
    space.

    Next, a PhaseSpace has an attribute, _data, which is a PhaseData object,
    and is a container for Phase objects, which are used when performing
    thermodynamic analysis on this space.

    The majority of attributes are lazy, that is, they are only computed when
    they are requested, and how to get them (of which there are often several
    ways) is decided based on the size and shape of the phase space.
    '''
    
    def __init__(self, definition=None, pdata=PhaseData(), load=False):
        self._data = pdata
        self._phases = None # phases within the space
        self._phase_dict = None # phase dict
        self._space = None # set of elements present
        self._hull = None # list of facets on hull; facets are lists of phases
        self._stable = None # list of phases that are stable
        self._tie_lines = None # list of pairs connected by tie lines
        self._spaces = None # the biggest spaces containing phases
        self._dual_spaces = None # the biggest spaces containing tie lines
        self._cliques = None # maximal k-cliques in space 
        self._graph = None # networkx graph of phase space

        if definition is None:
            self.bounds = None
            return

        if isinstance(definition, basestring):
            if '-' in definition:
                definition = [ parse_comp(b) for b in definition.split('-')]
            elif ' ' in definition:
                definition = [ parse_comp(b) for b in definition.split(' ')]
            else:
                definition = [ parse_comp(definition) ]
        self.bounds = definition

        if load is None:
            pass
        elif not pdata._phases and not load:
            self.load('oqmd')
        elif load:
            self.load(*load)

        self.get_phases()
        self.get_phase_dict()

    ####
    #### Builtins
    ####

    def __repr__(self):
        if self._bounds is None:
            return '<unbounded PhaseSpace>'
        names = [ format_comp(reduce_comp(b)) for b in self._raw_bounds ]
        return '<PhaseSpace bound by %s>' % '-'.join(names)

    ###
    ### Data access and management
    ###

    def clear_data(self):
        '''
        Clears all phase data:
            PhaseSpace._data = PhaseData()
            PhasesSpace._phases = None
            PhaseSpace._phase_dict = None
        '''
        self._data._phases = []
        self._data._phase_dict = None
        self._phases = None
        self._phase_dict = None

    def clear_analysis(self):
        '''
        Clears all analyzed results.
            PhaseSpace._space = None
            PhaseSpace._stable = None
            PhaseSpace._tie_lines = None
            PhaseSpace._hull = None
            PhaseSpace._graph = None
        '''
        self._stable = None
        self._tie_lines = None
        self._hull = None
        self._spaces = None
        self._dual_spaces = None
        self._cliques = None
        self._graph = None

    def clear_all(self):
        '''
        Clears input data and analyzed results. 
        Same as:
        >>> PhaseData.clear_data() 
        >>> PhaseData.clear_analysis()
        '''
        self.clear_data()
        self.clear_analysis()

    def load(self, *args, **kwargs):
        '''
        Load OQMD data into PhaseData. Takes unordered arguments; 
            if 'legacy' in args: will import older data
            if 'stable' in args: will only import stable structures
            if 'prototypes' in args: will import prototype structures
            if 'icsd' in args: will import icsd structures
            if 'oqmd' in args: will import all oqmd structures
            if 'get=[string]' in args: will import structures with [string] in
            their path.
        '''
        stable = ( 'stable' in args )
        fit = kwargs.get('fit', 'standard')
        for arg in args:
            if arg == 'legacy':
                self._data.load('legacy.dat')
            if arg == 'oqmd':
                self._data.load_oqmd(self.space)
            if arg == 'icsd':
                self._data.load_oqmd(self.space,
                        search={'path__contains':'icsd'},
                        stable=stable)
            if arg == 'prototypes':
                self._data.load_oqmd(space=self.space,
                        search={'path__contains':'prototypes'},
                        stable=stable)
            if arg.startswith('get='):
                get = arg.replace('get=','')
                self._data.load_oqmd(space=self.space,
                        search={'path__contains':get},
                        stable=stable,
                        fit=fit)

    def load_tie_lines(self):
        raise NotImplementedError

    ####
    #### Properties of the space itself
    ####

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, bound_list):
        if bound_list is None:
            self._bounds = None
            self._orth = None
            self._raw_bounds = None
            return
        self._raw_bounds = bound_list
        self._bounds = []
        basis = []
        for b in bound_list:
            b = defaultdict(float, b)
            b_tot = float(sum(b.values()))
            self._bounds.append(
                    dict((k, v/b_tot) for k, v in b.items()))
            basis.append([ b[k]/b_tot for k in self.sorted_space])
        self._basis = np.array(basis)

    @property
    def dimension(self):
        '''
        Number of bounds; note this is distinct from the number of elements.

        Fe-Li-O is 2-D 
        FeO-Ni2O-CoO-Ti3O4 is 4-D
        FeO-Fe2O3-Fe is 3-D
        '''
        return len(self.bounds)

    @property
    def space(self):
        '''
        Set of elements present in the PhaseSpace.

        Fe-Si-Li -> set(['Fe', 'Li', 'Si'])
        FeO-NiO-Ti2O3 -> set(['Ti', 'Ni', 'O', 'Fe'])
        '''

        if self._space is None:
            self.get_space()
        return self._space

    @property
    def sorted_space(self):
        return sorted(self.space)

    ###
    ### Properties of the phases within the space
    ###

    @property
    def phases(self):
        '''
        list of phases in space
        '''
        if not self._phases:
            self.get_phases()
        return self._phases

    @property
    def phase_dict(self):
        '''
        dictionary of phases (keys are phase names)
        '''
        if self._phase_dict is None:
            self.get_phase_dict()
        return self._phase_dict

    @property
    def spaces(self):
        '''
        list of sets of elements, such that every phase in self.phases
        is contained in at least one set, and no set is a subset of
        any other.
        '''
        if self._spaces is None:
            self.get_spaces()
        return self._spaces

    @property
    def stable(self):
        '''
        list of stable phases
        '''
        if self._stable is None:
            self.get_space_hull()
        return self._stable

    @property
    def unstable(self):
        '''
        list of unstable phases.
        '''
        if self._stable is None:
            self.get_space_hull()
        return [ p for p in self.phase_dict.values() if
            not p in self._stable and self.in_space(p) ]

    @property
    def tie_lines(self):
        '''
        list of length 2 tuples of phases with tie lines between them
        '''
        if self._tie_lines is None:
            self.get_tie_lines()
        return self._tie_lines

    @property
    def hull(self):
        '''
        List of phases on convex hull within space
        '''
        if self._hull is None:
            if any( len(b) > 1 for b in self.bounds ):
                points = self.get_hull_points()
                self.get_qhull(phases=points)
            else:
                self.get_qhull()
        return self._hull

    @property
    def dual_spaces(self):
        '''
        list of sets of elements, such that any possible tie-line
        between two phases in phases is contained in at least one
        set, and no set is a subset of any other.
        '''
        if self._dual_spaces is None:
            self.get_dual_spaces()
        return self._dual_spaces

    @property
    def graph(self):
        '''
        networkx.Graph representation of the phase space.
        '''
        if self._graph is None:
            self.get_graph()
        return self._graph

    @property
    def cliques(self):
        '''
        Iterator over maximal cliques in the phase space. To get a list of
        cliques, use list(PhaseSpace.cliques).
        '''
        if self._cliques is None:
            self.get_maximal_cliques()
        return self._cliques

    ###
    ### property getters
    ###

    def get_space(self):
        space = set()
        if self.bounds is None:
            return None
        for b in self._raw_bounds:
            space |= set(b.keys())
        self._space = space

    def get_phases(self):
        self._phases = [ p for p in self._data.phases 
                if self.in_space(p) ]

    def get_phase_dict(self):
        phase_dict = {}
        for p in self._data.phase_dict.values():
            if self.in_space(p):
                phase_dict[p.name] = p
        self._phase_dict = phase_dict

    def get_spaces(self):
        spaces = [ p.space for p in self.phase_dict.values() ]
        spaces = set([ frozenset(space) for space in spaces if not 
                any( space < space2 for space2 in spaces ) ])
        self._spaces = spaces

    def get_tie_lines(self):
        if any( len(b) > 1 for b in self.bounds ):
            points = self.get_hull_points()
            self.get_qhull(phases=points)
        else:
            self.get_qhull()
            #self.get_dual_space_hull()

    def get_dual_spaces(self):
        if len(self.spaces) == 1:
            self._dual_spaces = self._spaces
            return

        dual_spaces = []
        imax = len(self.spaces)**2 / 2
        for i, c1 in enumerate(itertools.combinations(self.spaces, r=2)):
            for j, c2 in enumerate(dual_spaces):
                if c1 <= c2:
                    break
                elif c2 < c1:
                    dual_spaces[j] = c1
                    break
            else:
                dual_spaces.append(c1)

        second_pass = []
        imax = len(dual_spaces)
        for i, c1 in enumerate(dual_spaces):
            for c2 in list(dual_spaces):
                if c1 <= c2:
                    break
            else:
                second_pass.append(c1)

        dual_spaces = set(second_pass)
        #dual_spaces = set( frozenset(c1 | c2) for c1, c2 in
        #        itertools.combinations(spaces, r=2) )

        dual_spaces = set([ space for space in dual_spaces 
            if not any( space < space2 for space2 in dual_spaces) ])

        dual_spaces = set([ frozenset([ ids[elt] for elt in space ]) for space
            in dual_spaces])

        self._dual_spaces = dual_spaces

    def get_maximal_cliques(self):
        graph = nx.Graph()
        graph.add_edges_from(self.tie_lines)
        self._cliques = list(nx.find_cliques(graph))
    
    def get_graph(self):
        graph = nx.Graph()
        for n in self.stable:
            graph.add_node('$\\rm{%s}$' % n.latex)
        for t in self.tie_lines:
            t = list(t)
            graph.add_edge('$\\rm{%s}$' % t[0].latex, 
                    '$\\rm{%s}$' % t[1].latex)
        self._graph = graph

    ### hull finding methods

    def get_space_hull(self):
        '''
        Iterate over the maximal spaces, getting the hull of each space. 

        Sets the following variables:
            - stable (complete)

        Advantages:
            - Gets the stable phases quickly

        Disadvantages:
            - Misses a lot of tie lines and facets
        '''
        stable = set()
        tie_lines = set()
        hull = set()
        imax = len(self.spaces)-1
        i = 0
        for space in self.spaces:
            print 'space hull %s/%s : %s' % (i, imax, space)
            i += 1
            space = PhaseSpace('-'.join(space), pdata=self._data, load=None)
            space.get_qhull()

            stable |= space.stable
            tie_lines |= space.tie_lines
            hull |= space.hull
        self._hull = hull # [ list(face) for face in hull ]
        self._tie_lines = tie_lines
        self._stable = stable

    def get_dual_space_hull(self):
        '''
        Iterate over the maximal dual spaces, getting the hull of each space.

        Sets the following variables:
            - stable (complete)
            - tie_lines (complete)

        Advantages:
            - Very fast list of tie lines

        Disadvantages:
            - Slow(er) for getting stable
        '''
        stable = set()
        tie_lines = set()
        hull = set()
        imax = len(self.dual_spaces)-1
        i = 0
        for space in self.dual_spaces:
            print 'dual space hull %s/%s : %s' % (i, imax, space)
            i += 1
            space = PhaseSpace('-'.join(space), pdata=self._data, load=None)
            space.get_qhull()
            stable |= space.stable
            tie_lines |= space.tie_lines
            hull |= space.hull
        self._stable = list(stable)
        self._tie_lines = [ list(tl) for tl in tie_lines ]
        self_hull = list(hull)

    def get_full_hull(self):
        '''
        Iterate over cliques within the space, getting the hull of each.

        Sets the following variables (requires stable + tie_lines):
            - hull (complete)
        '''
        hull = set()
        tie_lines = set()
        stable = set()
        i = 0
        imax = len(self.cliques)-1
        for clique in self.cliques:
            #print 'full space hull %s/%s' % (i, imax)
            i += 1
            self.get_qhull(phases=clique)

            stable |= self.stable
            tie_lines |= self.tie_lines
            hull |= self.hull
        self._hull = hull # [ list(face) for face in hull ]
        self._tie_lines = tie_lines
        self._stable = stable

    ### Methods using GCLP 

    def gclp(self, composition={}, mus={}, phases=[]):
        '''
        Returns energy, phase composition which is stable at given composition

        Example:
        >>> space = PhaseSpace('Fe-Li-O')
        >>> phases, energy = space.gclp('FeLiO2')
        >>> print phases
        >>> print energy
        '''
        if not composition:
            return 0.0, {}

        if isinstance(composition, basestring):
            composition = parse_comp(composition)
            
        if not phases:
            phases = self.phase_dict.values()

        space = set(composition.keys())
        in_phases = []
        for phase in phases:
            if phase.energy is None:
                continue
            if phase.space <= space:
                in_phases.append(phase)

        return self._gclp(composition=composition,
                mus=mus, phases=in_phases)

    def _gclp(self, composition={}, mus={}, phases=[]):
        print phases
        prob = LpProblem('GibbsEnergyMin', LpMinimize)
        phase_vars = LpVariable.dicts('lib', phases, 0.0)
        prob += lpSum([ (phase.energy -
            sum([ phase.unit_comp[elt]*mu
                for elt, mu in mus.items() ])) * phase_vars[phase]
            for phase in phases]),\
                    "Free Energy"
        for elt, constraint in composition.items():
            prob += lpSum([ 
                phase.unit_comp.get(elt,0)*phase_vars[phase]
                for phase in phases ]) == float(constraint),\
                        'Conservation of '+elt

        #prob.solve(GUROBI(msg=False))
        #print phases
        #print composition
        prob.solve()

        xsoln = dict([ (phase, phase_vars[phase].varValue)
            for phase in phases if phase_vars[phase].varValue > 1e-5])
        #E = value(prob.objective)
        energy = sum( p.energy*amt for p, amt in xsoln.items() )
        return energy, xsoln

    def get_minima(self, phases, bounds):
        '''
        Given a set of Phases, get_minima will determine the minimum
        free energy elemental composition as a weighted sum of these
        compounds
        '''

        prob = LpProblem('GibbsEnergyMin', LpMinimize)
        pvars = LpVariable.dicts('phase', phases, 0)
        bvars = LpVariable.dicts('bound', bounds, 0.0, 1.0)
        prob += lpSum( phase.energy*pvars[phase] for phase in phases ) - \
                lpSum( bound.energy*bvars[bound] for bound in bounds ), \
                                "Free Energy"
        for elt in self.space:
            prob += sum([ p.unit_comp.get(elt,0)*pvars[p] for p in phases ])\
                        == \
                sum([ b.unit_comp.get(elt, 0)*bvars[b] for b in bounds ]),\
                            'Contraint to the proper range of'+elt
        prob += sum([ bvars[b] for b in bounds ]) == 1, \
                'sum of bounds must be 1'

        #prob.solve(GUROBI(msg=False))
        prob.solve()
        E = value(prob.objective)
        xsoln = defaultdict(float,
            [(p, pvars[p].varValue) for p in phases if 
                abs(pvars[p].varValue) > 1e-6])
        return xsoln, E

    def chempot_range(self, phase):
        e = phase.energy
        pot_bounds = {}
        for elt in phase.comp.keys():
            tcomp = dict(phase.unit_comp)
            tcomp[elt] -= 0.01
            eup, xup = self.gclp(tcomp)
            tcomp[elt] += 0.02
            edo, xdo = self.gclp(tcomp)
            pot_bounds[elt] = [ (edo-e)/0.01, (e-eup)/0.01 ]
        return pot_bounds
            

    def get_tie_lines_by_gclp(self, iterable=False):
        tie_lines=[]
        self.get_gclp_stable()

        for k1, k2 in itertools.combinations(self.stable, 2):
            #for k1, k2 in self.tie_lines:
            testpoint = (self.coord(k1.unit_comp) + self.coord(k2.unit_comp))/2
            energy, phases = self.gclp(self.comp(testpoint))
            if abs(energy - (k1.energy + k2.energy)/2) < 1e-8:
                tie_lines.append([k1,k2])
                if iterable:
                    yield [k1, k2]
        self._tie_lines = tie_lines

    def coord(self, composition):
        '''Returns the coordinate of a composition.
        
        Example:
        >>> space = PhaseSpace('Fe-Li-O')
        >>> space.coord({'Fe':1, 'Li':1, 'O':2})
        array([ 0.25,  0.25,  0.5 ])
        '''
        if isinstance(composition, Phase):
            composition = composition.comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        composition = defaultdict(float, composition)
        if self.bounds is None:
            return np.array([ composition[k] for k in self.sorted_space ])
        ctot = float(sum(composition.values()))
        cvec = np.array([ composition[k]/ctot for k in self.sorted_space ])
        coord = np.linalg.lstsq(self._basis.T, cvec)[0]
        if abs(sum(coord) - 1) > 1e-3 or any(c < -1e-3 for c in coord):
            raise PhaseSpaceError
        return coord

    def comp(self, coord):
        '''
        Returns the composition of a coordinate in phase space.

        Example:
        >>> space = PhaseSpace('Fe-Li-O')
        >>> space.comp([0.2, 0.2, 0.6])
        defaultdict(<type 'float'>, {'Fe': 0.20000000000000001, 
        'O':0.59999999999999998, 'Li': 0.20000000000000001})
        '''
        if self.bounds is None:
            return defaultdict(float, zip(self.sorted_space, coord))
        if len(coord) != len(self.bounds):
            raise PhaseSpaceError
        tot = sum(coord)
        coord = [ c/float(tot) for c in coord ]
        comp = defaultdict(float)
        for b, x in zip(self.bounds, coord):
            for elt, val in b.items():
                comp[elt] += val*x
        return defaultdict(float,
                dict( (k,v) for k,v in comp.items() if v > 0 ))

    def in_space(self, composition):
        '''
        Returns True, if the composition is in the right elemental-space 
        for this PhaseSpace.

        Example:
        >>> space = PhaseSpace('Fe-Li-O')
        >>> space.in_space('LiNiO2')
        False
        >>> space.in_space('Fe2O3')
        True
        '''

        if self.bounds is None:
            return True
        if isinstance(composition, Phase):
            composition = composition.comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        if set(composition.keys()) <= self.space:
            return True
        else:
            return False

    def in_bounds(self, composition):
        '''
        Returns True, if the composition is within the bounds of the phase space

        Example:
        >>> space = PhaseSpace('Fe2O3-NiO2-Li2O')
        >>> space.in_bounds('Fe3O4')
        False
        >>> space.in_bounds('Li5FeO8')
        True
        '''
        if self.bounds is None:
            return True
        if isinstance(composition, Phase):
            composition = composition.unit_comp
        elif isinstance(composition, basestring):
            composition = parse_comp(composition)

        if not self.in_space(composition):
            return False

        try:
            self.coord(composition)
        except PhaseSpaceError:
            return False
        return True

    ### analysis stuff

    def get_qhull(self, phases=None):
        '''Get the convex hull for a given space.
        
        Sets the following variables:
            - stable
            - tie_lines
            - hull
        '''
        if phases is None: ## ensure there are phases to get the hull of
            phases = self.phase_dict.values()

        ## ensure that all phases have negative formation energies
        phases = [ p for p in phases if p.energy <= 0 ]

        phase_space = set()
        for phase in phases:
            phase_space |= phase.space

        A = []
        for phase in phases:
            A.append(list(self.coord(phase))[1:] + [phase.energy])

        dim = len(A[0])
        for i in range(dim):
            tmparr = [ 0 if a != i-1 else 1 for a in range(dim) ]
            if not tmparr in A:
                A.append(tmparr)

        A = np.array(A)
        if len(A) == len(A[0]):
            self._hull = set([frozenset([ p for p in phases])])
            self._tie_lines = set([ frozenset([k1, k2]) for k1, k2 in 
                    itertools.combinations(phases, r=2) ])
            self._stable = set([ p for p in phases])
            return

        #if len(A[0]) < len(phase_space):
        conv_hull = ConvexHull(A)
        #else:
        #    conv_hull = ConvexHull(A, joggle=True)

        hull = set()
        tie_lines = set()
        stable = set()
        for facet in conv_hull.simplices:
            ### various exclusion rules
            if any([ ind >= len(phases) for ind in facet ]):
                continue

            if all( phases[ind].energy == 0 for ind in facet 
                    if ind < len(phases)):
                continue

            dim = len(facet)
            face_matrix = np.array([ A[i] for i in facet ])
            face_matrix[:, -1] = 1
            v = np.linalg.det(face_matrix)
            
            if abs(v) < 1e-8:
                continue

            face = frozenset([ phases[ind] for ind in facet 
                if ind < len(phases)])

            stable |= set(face)
            tie_lines |= set([ frozenset([k1, k2]) for k1, k2 in
                    itertools.combinations(face, r=2)])
            hull.add(face)

        self._hull = hull 
        self._tie_lines = tie_lines 
        self._stable = stable

    def get_hull_points(self):
        '''
        Gets out-of PhaseSpace points. i.e. for FeSi2-Li, there are no other
        phases in the space, but there are combinations of Li-Si phases and
        Fe-Si phases. This method returns a list of phases including composite
        phases from out of the space.

        Example:
        >>> space = PhaseSpace('FeSi2-Li')
        >>> space.get_hull_points()
        [<Phase FeSi2 (23408): -0.45110217625>, 
        <Phase Li (104737): 0>, 
        <Phase 0.680 Li13Si4 + 0.320 FeSi : -0.3370691816>, 
        <Phase 0.647 Li8Si3 + 0.353 FeSi : -0.355992801765>, 
        <Phase 0.133 Fe3Si + 0.867 Li21Si5 : -0.239436904167>, 
        <Phase 0.278 FeSi + 0.722 Li21Si5 : -0.306877209723>]
        '''
        self._hull = set() # set of lists
        self._stable = set() # set
        done_list = [] # list of sorted lists
        hull_points = [] # list of phases

        if len(self.phases) == len(self.space):
            self._hull = set(frozenset(self.phases))
            self._stable = set(self.phases)
            return

        for b in self.bounds:
            e, x = self.gclp(b)
            p = Phase.from_phases(x)
            hull_points.append(p)
        
        facets = [list(hull_points)]
        while facets:
            facet = facets.pop(0)
            done_list.append(sorted(facet))
            phases, E = self.get_minima(self.phase_dict.values(), facet)
            phase = Phase.from_phases(phases)
            if not phase in hull_points:
                hull_points.append(phase)
                for new_facet in itertools.combinations(facet, r=len(facet)-1):
                    new_facet = list(new_facet) + [phase]
                    if new_facet not in done_list:
                        facets.append(new_facet)
        return hull_points

    def compute_meta_stability(self, phase):
        '''
        Compute the distance from the convex hull. For phases which are
        unstable this is simply the computed distance to the hull. For phases
        which are stable, we further compute the distance to the hull, without
        that phase. i.e. how stable is the next-most-favorable phase
        composition at that phase's composiion?
        '''
        if self.phase_dict[phase.name] != phase:
            stable = self.phase_dict[phase.name]
            phase.meta_stability = phase.energy - stable.energy
        elif len(phase.comp) == 1:
            stable = self.phase_dict[phase.name]
            phase.meta_stability = phase.energy - stable.energy
        else:
            phases = self.phase_dict.values()
            phases.remove(phase)
            energy, gclp_phases = self.gclp(phase.unit_comp, phases=phases)
            phase.meta_stability = phase.energy - energy
        #f = phase.formation
        #f.hull_distance = phase.meta_stability
        #f.save()

    def compute_meta_stabilities(self, phases=None):
        if phases is None:
            phases = self.phases
        for phase in phases:
            if phase.energy == 0:
                continue
            if not phase.meta_stability:
                self.compute_meta_stability(phase)

    ###
    ### Reaction stuff
    ###

    def get_reaction(self, var, facet=None):
        '''
        For a given composition, what is the maximum delta_composition reaction
        on the given facet. If None, returns the whole reaction for the given
        PhaseSpace.

        Example:
        >>> space = PhaseSpace('Fe2O3-Li2O')
        >>> equilibria = space.hull[0]
        >>> space.get_reaction('Li2O', facet=equilibria)
        '''

        if isinstance(var, basestring):
            var = parse_comp(var)

        if facet:
            phases = facet
        else:
            phases = self.stable

        prob = LpProblem('BalanceReaction', LpMaximize)
        pvars = LpVariable.dicts('prod', phases, 0)
        rvars = LpVariable.dicts('react', phases, 0)
        prob += sum([ p.fraction(var)['var']*pvars[p] for p in phases ])-\
                sum([ p.fraction(var)['var']*rvars[p] for p in phases ]),\
                "Maximize delta comp"
        for celt in self.space:
            prob += sum([ p.fraction(var)[celt]*pvars[p] for p in phases ]) ==\
                    sum([ p.fraction(var)[celt]*rvars[p] for p in phases ]),\
                    'identical %s composition on both sides' % celt
        prob += sum([ rvars[p] for p in phases ]) == 1
        prob.solve()
        #prob.solve(GUROBI(msg=False))
        prods = defaultdict(float,[ (c, pvars[c].varValue) for c in phases
            if pvars[c].varValue > 1e-6 ])
        reacts = defaultdict(float,[ (c, rvars[c].varValue) for c in phases
            if rvars[c].varValue > 1e-6 ])
        n_elt = value(prob.objective)
        return reacts, prods, n_elt

    def get_reactions(self, var, electrons=2.0):
        '''
        Returns a list of Reactions.

        Example:
        >>> space = PhaseSpace('Fe-Li-O')
        >>> space.get_reactions('Li', electrons=1)
        '''
        if isinstance(var, basestring):
            var = parse_comp(var)
        vname = format_comp(reduce_comp(v))
        vphase = self.phase_dict[vname]
        for facet in self.hull:
            reacts, prods, delta_var = self.get_reaction(var, facet=facet)
            if vphase in facet:
                yield Reaction(
                    products={vphase:sum(vphase.comp.values())}, 
                    reactants={}, delta_var=1.0,
                    electrons=electrons, variable=var)
                continue
            yield Reaction(products=prods, reactants=reacts, 
                delta_var=delta_var,
                variable=var, electrons=electrons)

    def plot_reactions(self, var, electrons=2.0, save=False):
        '''
        Plot the convex hull along the reaction path, as well as the voltage
        profile.
        '''
        if isinstance(var, basestring):
            var = parse_comp(var)
        vname = format_comp(var)

        fig = plt.figure()
        ax1 = fig.add_subplot(211)

        #plot tie lines
        for p1, p2 in self.tie_lines:
            c1 = self.coord(p1)
            c2 = self.coord(p2)
            if abs(c1[1]) < 1e-6 or abs(c2[1]) < 1e-6:
                if abs(c1[1] - 1) < 1e-6 or abs(c2[1] - 1) < 1e-6:
                    if len(self.tie_lines) > 1:
                        continue
            ax1.plot([c1[1],c2[1]], [p1.energy, p2.energy], 'k')

        #plot compounds
        for p in self.stable:
            x = self.coord(p.unit_comp)[1]
            ax1.plot(x, p.energy, 'bo')
            ax1.text(x, p.energy, '$\\rm{%s}$' % p.latex,
                    ha='left', va='top')
        plt.ylabel('$\\rm{\Delta H}$ $\\rm{[eV/atom]}$')
        ymin, ymax = ax1.get_ylim()
        ax1.set_ylim(ymin - 0.1, ymax)

        ax2 = fig.add_subplot(212, sharex=ax1)
        ax2.set_xlim([0,1])
        points = set()
        for reaction in self.get_reactions(var):
            voltage = reaction.delta_h/reaction.delta_var/electrons
            points |= set([(reaction.r_var_comp, voltage), 
                    (reaction.p_var_comp, voltage)])

        points = sorted( points, key=lambda x: x[0] )
        points = sorted( points, key=lambda x: -x[1] )
        base = sorted(self.stable, key=lambda x:
                x.fraction(var)['var'])[0]

        if len(points) > 1:
            for i in range(len(points) - 2):
                ax2.plot([points[i][0], points[i+1][0]],
                        [points[i][1], points[i+1][1]], 'k')

            ax2.plot([points[-2][0], points[-2][0]], 
                    [points[-2][1], points[-1][1]], 'k')
            ax2.plot([points[-2][0], 1], 
                    [points[-1][1], points[-1][1]], 'k')
        else:
            ax2.plot([0, 1], [points[0][1], points[0][1]], 'k')
        
        plt.xlabel('$\\rm{x}$ $\\rm{in}$ $\\rm{(%s)_{x}(%s)_{1-x}}$' % ( 
            comp_to_latex(var),
            base.latex))
        plt.ylabel('$\\rm{Voltage}$ $\\rm{[V]}$')

        return ax1, ax2

        #if not save:
        #    plt.show()
        #else:
        #    plt.savefig('%s-%s.eps' % (save, vname),
        #            bbox_inches='tight', 
        #            transparent=True,
        #            pad_inches=0) 
