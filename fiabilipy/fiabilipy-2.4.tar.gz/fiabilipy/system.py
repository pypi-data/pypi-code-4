#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Copyright (C) 2013 Chabot Simon, Sadaoui Akim

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

r""" Reliability system design and computation

This modude gives classes and functions to design complex systems and
compute some metrics, such as the reliability, the availability, the
Mean-Time-To-Failure, and so on.

"""

from numpy import empty, ones, delete
from sympy import exp, Symbol, oo
from scipy.special import binom
from itertools import combinations, chain
from collections import Iterable

__all__ = ['System', 'Component', 'Voter']

ALLSUBSETS = lambda n: (chain(*[combinations(range(n), ni)
                        for ni in xrange(n+1)]))


class Component(object):
    r""" Describe a component with a constant failure rate.

        This class is used to create all the components of a system.

        Attributes
        ----------
        name : str
            the name of the component. (It has to be a unique name for the whole
            system)
        lambda_ : float
            the constant failure rate of the component
        mu : float, optional
            the constant maintainability rate of the component
        initialy_avaible : boolean, optional
            whether the component is avaible at t=0 or not

        Examples
        --------
        >>> motor = Component('M', 1e-4, 3e-2)
        >>> motor.lambda_
        0.0001
    """

    def __init__(self, name, lambda_, mu=0, initialy_avaible=True):
        self.lambda_ = lambda_
        self.mu = mu
        self.name = name
        self.initialy_avaible = initialy_avaible

    def __repr__(self):
        return u'Component(%s)' % self.name

    def reliability(self, t):
        r""" Compute the reliability of the component at `t`

            This method compute the reliability of the component at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The reliability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> t = Symbol('t', positive=True)
            >>> motor.reliability(t)
            exp(-0.0001*t)
            >>> motor.reliability(1000)
            0.904837418035960
        """
        return exp(-self.lambda_ * t)

    def maintainability(self, t):
        r""" Compute the maintainability of the component at `t`

            This method compute the maintainability of the component at `t`.

            Parameters
            ----------
            t : int or Symbol

            Returns
            -------
            out : float or symbolic expression
                The maintainability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> t = Symbol('t', positive=True)
            >>> motor.maintainability(t)
            -exp(-0.03*t) + 1.0
            >>> motor.maintainability(1000)
            0.999999999999906
        """
        return 1.0 - exp(-self.mu * t)

    def availability(self, t):
        r""" Compute the availability of the component at `t`

            This method compute the availability of the component at `t`.

            Parameters
            ----------
            t : int or Symbol

            Returns
            -------
            out : float or symbolic expression
                The availability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> t = Symbol('t', positive=True)
            >>> motor.availability(t)
            0.00332225913621263*exp(-0.0301*t) + 0.996677740863787
            >>> motor.availability(1000)
            0.996677740863788
        """
        if self.mu == self.lambda_ == 0:
            return 1
        a = self.mu / (self.mu + self.lambda_)
        if self.initialy_avaible:
            b = self.lambda_ / (self.mu + self.lambda_)
        else:
            b = - self.mu / (self.mu + self.lambda_)

        return a + b*exp(-(self.lambda_ + self.mu) * t)

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the component

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt = \frac{1}{\lambda}`

            when the failure rate (:math:`\lambda` is constant)

            Returns
            -------
            out : float
                The component MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> motor.mttf
            10000.0
        """
        return 1.0/self.lambda_

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the component

            The MTTR is defined as :
                :math:`MTTR = \int_{0}^{\infty} 1 - M(t)dt = \frac{1}{\mu}`

            when the failure rate (:math:`\mu` is constant)

            Returns
            -------
            out : float
                The component MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> motor.mttr
            33.333333333333336
        """
        return 1.0/self.mu


class Voter(Component):
    r""" A voter with identical components having a constant failure rate

        This class is used to describe a voter. A voter M out-of N works if
        and only if *at least* M components out of the N avaible work.

        Attributes
        ----------
        component: `Component`
            the component to be replicated by the voter
        N: int
            the initial number of components
        M: int
            the minimal number of working components
        lambda_ : float
            the constant failure rate of the voter
        mu : float, optional
            the constant maintainability rate of the voter
        initialy_avaible: boolean, optional
            whether the component is avaible at t=0 or not

        Examples
        --------
        >>> motor = Component('M', 1e-4, 3e-2)
        >>> voter = Voter(motor, 2, 3)
        >>> voter.mttf
        8333.33333333333
    """

    def __init__(self, component, M, N, lambda_=0, mu=0, initialy_avaible=True):
        self.component = component
        name = '%s out-of %s − %s' % (M, N, component.name)
        super(Voter, self).__init__(name=name, lambda_=lambda_, mu=mu,
                                    initialy_avaible=initialy_avaible)
        self.M = M
        self.N = N

    def __repr__(self):
        return u'Voter(%s out-of %s)' % (self.M, self.N)

    def _probabilitiescomputation(self, t, method):
        """ Compute the `method` (reliability, availability, maintainability) of
            a voter, given its components, and the initial number of components
            and the minimal number of components.
        """
        prob = 0
        for k in xrange(self.M, self.N+1):
            a = getattr(self.component, method)(t)**k
            b = (1 - getattr(self.component, method)(t))**(self.N-k)
            prob += binom(self.N, k) * a * b
        return prob

    def reliability(self, t):
        r""" Compute the reliability of the voter at `t`

            This method compute the reliability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The reliability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3)
            >>> t = Symbol('t', positive=True)
            >>> voter.reliability(t)
            3.0*(-exp(-0.0001*t) + 1)*exp(-0.0002*t) + 1.0*exp(-0.0003*t)
            >>> voter.reliability(1000)
            0.974555817870510
        """
        ownrel = super(Voter, self).reliability(t)
        return ownrel * self._probabilitiescomputation(t, 'reliability')

    def maintainability(self, t):
        r""" Compute the maintainability of the voter at `t`

            This method compute the maintainability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The maintainability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> t = Symbol('t', positive=True)
            >>> voter.maintainability(t) #doctest: +NORMALIZE_WHITESPACE
            (1.0*(-exp(-0.03*t) + 1.0)**3 + 3.0*(-exp(-0.03*t) 
                + 1.0)**2*exp(-0.03*t))*(-exp(-0.001*t) + 1.0)
            >>> voter.maintainability(1000)
            0.632120558828558
        """
        raise NotImplementedError()

    def availability(self, t):
        r""" Compute the availability of the voter at `t`

            This method compute the availability of the voter at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The availability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> t = Symbol('t', positive=True)
            >>> voter.availability(t) #doctest: +NORMALIZE_WHITESPACE
            3.0*(-0.00332225913621263*exp(-0.0301*t) +
            0.00332225913621265)*(0.00332225913621263*exp(-0.0301*t) +
            0.996677740863787)**2 + 1.0*(0.00332225913621263*exp(-0.0301*t) +
            0.996677740863787)**3
            >>> voter.availability(1000)
            0.999966961120940
        """
        ownavail = super(Voter, self).availability(t)
        return ownavail * self._probabilitiescomputation(t, 'availability')

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the voter

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt`

            Returns
            -------
            out : float
                The component MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3)
            >>> voter.mttf
            8333.33333333333
        """
        t = Symbol('t', positive=True)
        return self.reliability(t).integrate((t, 0, oo))

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the voter

            The MTTR is defined as :
                :math:`MTTR = \int_{0}^{\infty} 1 - M(t)dt`

            Returns
            -------
            out : float
                The component MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> voter = Voter(motor, 2, 3, mu=1e-3)
            >>> voter.mttr
            1000.57547188695
        """
        raise NotImplementedError()


class System(object):
    r""" Describe a system with different components.

        The components are linked together thanks to a reliability diagram.
        This reliability diagram is represented by a graph. This graph
        *must* have two special nodes called `E` and `S`. `E` represents the
        start of the system and `S` its end (names stand for “Entrée”
        (start) and “Sortie” (end) in French).

        Examples
        --------

        Let’s have a look to the following system::

                 | -- C0 -- |
            E -- |          | -- C2 -- S
                 | -- C1 -- |

        Thus, to represent such a system, you must create the three
        components C0, C1 and C2 and link them.

        >>> C = [Component(i, 1e-4) for i in xrange(3)]
        >>> S = System()
        >>> S['E'] = [C[0], C[1]]
        >>> S[C[0]] = [C[2]]
        >>> S[C[1]] = [C[2]]
        >>> S[C[2]] = ['S']

        So, you can use the `System` object as a simple python dictionnary
        where each key is a component and the value associated it the list
        of the component’s successors.
    """

    def __init__(self, graph=None):
        self._graph = graph or {}
        self._cache = {}
        self._t = Symbol('t', positive=True)

    def __getitem__(self, component):
        return self._graph.get(component, [])

    def __setitem__(self, component, successors):
        #Let’s do different checks before inserting the element
        if not isinstance(successors, Iterable):
            if not isinstance(successors, Component):
                msg = u'successors must be a list of components, a component '
                raise ValueError(msg)
            successors = [successors]
        if component != 'E' and 'E' not in self._graph:
            msg = u"'E' must be the first inserted component"
            raise ValueError(msg)
        self._graph[component] = successors

        #reset the cache
        self._cache = {}

    def __delitem__(self, component):
        for c in self._graph:
            try:
                self._graph[c].remove(component)
            except ValueError:
                pass
            except AttributeError:
                assert self._graph[c] == 'S'
        del self._graph[component]
        #reset the cache
        self._cache = {}

    def __len__(self):
        return len(self._graph)

    def __repr__(self):
        return u'I\'m a system'

    def copy(self):
        r""" Return a copy of the system.

            Returns
            -------
            out: System
                A copy of the current system

            Notes
            -----
                The components are the same (same reference).
                Only the internal graph is new
        """
        _copy = System()
        _copy['E'] = [] #'E' must be the first inserted component
        for c in self._graph:
            _copy[c] = self[c][:]
        return _copy

    @property
    def components(self):
        r""" The list of the components used by the system

            Returns
            -------
            out: list
                the list of the components used by the system, except `E` and
                `S`
        """
        return [comp for comp in self._graph.iterkeys()
                if comp not in ['E', 'S']]

    def _probabilitiescomputation(self, t, method):
        """ Given a system and a `method` (either availability or
            maintainability or reliability), this method evaluates the asking
            value by exploring the graph at time `t`.
        """
        #TODO : improve complexity ?
        #   n
        # P(U a_i) = sum     (-1)^{-1+|s|} P(^a_i)
        #  i=1      s\in[1,n],              i\in s
        #           s != {}
        #
        paths = self.successpaths
        R = 0.0
        for S in ALLSUBSETS(len(paths)):
            if not S:
                continue
            comps = set([c for i in S for c in paths[i][1:-1]])
            r = reduce(lambda x, y:x*getattr(y, method)(t), comps, 1)
            R += -r if len(S) % 2 == 0 else r
        return R

    def availability(self, t):
        r""" Compute the availability of the whole system

            This method compute the availability of the system at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The availability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.availability(t) #doctest: +NORMALIZE_WHITESPACE
            (200/201 + exp(-201*t/1000000)/201)*(300/301 +
            exp(-301*t/10000)/301)
            >>> S.availability(1000)
            0.995774842225189
        """
        try:
            formula = self._cache['availability']
        except KeyError:
            formula = self._probabilitiescomputation(self._t, 'availability')
            self._cache['availability'] = formula

        if isinstance(t, Symbol):
            return formula.nsimplify()
        else:
            return formula.subs(self._t, t).evalf()

    def reliability(self, t):
        r""" Compute the reliability of the whole system

            This method compute the reliability of the system at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The reliability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.reliability(t)
            exp(-101*t/1000000)
            >>> S.reliability(1000)
            0.903933032885864
        """
        try:
            formula = self._cache['reliability']
        except KeyError:
            formula = self._probabilitiescomputation(self._t, 'reliability')
            self._cache['reliability'] = formula

        if isinstance(t, Symbol):
            return formula.nsimplify()
        else:
            return formula.subs(self._t, t).evalf()

    def maintainability(self, t):
        r""" Compute the maintainability of the whole system

            This method compute the maintainability of the system at `t`.

            Parameters
            ----------
            t : float or Symbol

            Returns
            -------
            out : float or symbolic expression
                The maintainability calculated for the given `t`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> t = Symbol('t', positive=True)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.maintainability(t)
            (1 - exp(-3*t/100))*(1 - exp(-t/5000))
            >>> S.maintainability(1000)
            0.181269246922001
        """
        raise NotImplementedError()

    @property
    def mttf(self):
        r""" Compute the Mean-Time-To-Failure of the system

            The MTTF is defined as :
                :math:`MTTF = \int_{0}^{\infty} R(t)dt`

            Returns
            -------
            out : float
                The system MTTF

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.mttf
            1000000/101
        """
        try:
            return self._cache['mttf']
        except KeyError:
            t = Symbol('t', positive=True)
            self._cache['mttf'] = self.reliability(t).integrate((t, 0, oo))
            return self._cache['mttf']

    @property
    def mttr(self):
        r""" Compute the Mean-Time-To-Repair of the system

            The MTTR is defined as :
                :math:`MTTF = \int_{0}^{\infty} 1 - M(t)dt`

            Returns
            -------
            out : float
                The system MTTR

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> power = Component('P', 1e-6, 2e-4)
            >>> S = System()
            >>> S['E'] = [power]
            >>> S[power] = [motor]
            >>> S[motor] = 'S'
            >>> S.mttr
            2265100/453
        """
        raise NotImplementedError()


    @property
    def successpaths(self):
        r""" Return all the success paths of the reliability diagram

            A success path is defined as a path from 'E' to 'S'.

            Returns
            -------
            out : list of paths
                the list of all the success paths. A path, is defined as a list
                of components

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.successpaths #doctest: +NORMALIZE_WHITESPACE
            [['E', Component(P0), Component(M), 'S'],
             ['E', Component(P1), Component(M), 'S']]
        """
        try:
            return self._cache['successpaths']
        except KeyError:
            self._cache['successpaths'] = self.findallpaths(start='E', end='S')
            return self._cache['successpaths']

    # pylint: disable=W0102
    def findallpaths(self, start='E', end='S', path=[]):
        #the default value for `path` *is* wanted because all the subcalls have
        #modify the same list.
        r""" Find all paths between two components in the reliability diagram

            Parameters
            ----------
            start : Component, optional
                find paths from this component
            end : Component, optional
                find paths to this component
            path : list
                this argument is not intented to be used by the user.

            Returns
            -------
            out : list
                the list of the paths from `start` to `stop`

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.findallpaths(start=powers[0])
            [[Component(P0), Component(M), 'S']]
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self._graph:
            return []
        paths = []
        for node in self._graph.get(start, []):
            if node not in path:
                for newpath in self.findallpaths(node, end, path):
                    paths.append(newpath)
        return paths

    def minimalcuts(self, order=1):
        r""" List the minimal cuts of the system of order <= `order`

            A minimal cut of order :math:`n`, is a set of :math:`n` components,
            such as if there all unavailable, the whole system is unavailable.

            This function aims to find out every minimal cuts of order inferior
            to `order`.

            Parameters
            ----------
            order : int, optional
                The maximal order to look for.

            Returns
            -------
            out : list of frozensets
                each frozenset contains the components that constitute a minimal
                cut

            Examples
            --------
            >>> motor = Component('M', 1e-4, 3e-2)
            >>> powers = [Component('P{}'.format(i), 1e-6, 2e-4) for i in (0,1)]
            >>> S = System()
            >>> S['E'] = [powers[0], powers[1]]
            >>> S[powers[0]] = S[powers[1]] = [motor]
            >>> S[motor] = 'S'
            >>> S.minimalcuts(order=1) #doctest: +ELLIPSIS
            [frozenset(...)]
            >>> S.minimalcuts(order=2) #doctest: +ELLIPSIS
            [frozenset(...), frozenset(...)]
        """
        paths = self.successpaths
        incidence = empty((len(paths), len(self.components)))

        for path in xrange(len(paths)):
            for comp in xrange(len(self.components)):
                if self.components[comp] in paths[path]:
                    incidence[path, comp] = 1
                else:
                    incidence[path, comp] = 0

        pairs = list(self.components)
        minimal = []

        for k in xrange(1, order+1):
            if incidence.shape[1] == 0: #No more minimalcuts
                break
            #Let’s looking for column of ones
            vones = ones(len(paths))
            indicetodelete = []
            for comp in xrange(len(pairs)):
                if (incidence[:, comp] == vones).all():
                    if isinstance(pairs[comp], frozenset):
                        minimal.append(pairs[comp])
                    else:
                        minimal.append(frozenset([pairs[comp]]))
                    indicetodelete.append(comp)

            if k >= order:
                #so it’s useless to compute newpairs and the new incidence
                #matrix because they won’t be used anymore.
                continue

            incidence = delete(incidence, indicetodelete, axis=1)
            pairs = [p for i, p in enumerate(pairs) if i not in indicetodelete]
            newpairs = list(combinations(range(len(pairs)), k+1))
            incidence_ = empty((len(paths), len(newpairs)))
            for x in xrange(incidence_.shape[0]):
                for y in xrange(incidence_.shape[1]):
                    value = 0
                    for comp in newpairs[y]:
                        if incidence[x, comp]:
                            value = 1
                            break
                    incidence_[x, y] = value

            incidence = incidence_
            pairs = [frozenset([pairs[x] for x in p]) for p in newpairs]

        return minimal

    def faulttreeanalysis(self, output=None, order=2):
        r""" Build the fault tree analysis of the system

            Print (or write) the content of the dot file needed to draw the
            fault tree of the system.

            Parameters
            ----------
            output : file-like object, optional
                If `output` is given, then the content is written into this
                file. `output` *must* have a :py:meth:`write` method.

            order : int, optional
                This is the maximum order of the minimal cuts the function looks
                for.

            Notes
            -----
            Please, see the `Graphviz <http://graphviz.org/>` website for more
            information about how to transform the ouput code into a nice
            picture.

        """
        #TODO the tree needs to be simplified
        cuts = self.minimalcuts(order)
        data = ['digraph G {']
        data.append('\t"not_S" -> "or"')
        for i, cut in enumerate(cuts):
            data.append('\tor -> and_%s' % i)
            for comp in cut:
                data.append('\tand_%s -> "%s"' % (i, comp.name))
        data.append('}')

        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')


    def draw(self, output=None):
        r""" Print the content of the dot file needed to draw the system

            Print (or write) the content of the dot file needed to draw the
            fault tree of the system.

            Parameters
            ----------
            output : file-like object, optional
                If `output` is given, then the content is written into this
                file. `output` *must* have a :py:meth:`write` method.

            Notes
            -----
            Please, see the `Graphviz <http://graphviz.org/>`_ website to have
            more information about how to transform the ouput code into a nice
            picture.
        """
        def _getname(state):
            """ Return the name of the given component """
            if state in ['E', 'S']:
                return state
            return state.name

        data = ['digraph G {', '\trankdir=LR;', '\tnode [shape=box];'
                '\tsplines=ortho;']
        for state in self._graph:
            for succ in self._graph[state]:
                data.append('\t"%s" -> "%s"'
                            % (_getname(state), _getname(succ)))
        data.append('}')

        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')
