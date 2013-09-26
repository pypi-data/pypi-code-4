#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Copyright (C) 2013 Chabot Simon

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

from numpy import exp, empty, ones, delete, inf
from scipy.special import binom
from scipy.integrate import quad
from itertools import combinations, chain
from collections import Iterable

__all__ = ['System', 'Component', 'Voter']

allsubsets = lambda n: (chain(*[combinations(range(n), ni) for ni in xrange(n+1)]))


class Component(object):
    """ Describe a component with a constant failure rate """

    def __init__(self, name, lambda_, mu=0, initialy_avaible=True):
        """ Build a component :
                `name` is the name of the component
                `lambda_` is its reliability
                `mu` is its maintainability.
                `initialy_avaible` is a boolean set to True is the component is
                avaible at t=0.
        """
        self.lambda_ = lambda_
        self.mu = mu
        self.name = name
        self.initialy_avaible = initialy_avaible

    def __repr__(self):
        return u'Component(%s)' % self.name

    def reliability(self, t):
        """ Compute the reliability of the component at t """
        return exp(-self.lambda_ * t)

    def maintainability(self, t):
        """ Compute the maintainability of the component at t """
        return 1.0 - exp(-self.mu * t)

    def availability(self, t):
        """ Compute the availability of the component at t """
        if self.mu == self.lambda_ == 0:
            return 1
        a = self.mu / (self.mu + self.lambda_)
        if self.initialy_avaible:
            b = self.lambda_ / (self.mu + self.lambda_)
        else:
            b = - self.mu / (self.mu + self.lambda_)

        return a + b*exp(-(self.lambda_ + self.mu) * t)

    @property
    def MTTF(self):
        """ Return the Mean Time To Failure of the whole system.
            MTTF is defined as :
                       infty
                MTTF =  int R(t)dt = 1/lambda_ when lambda_ is constant
                         0
        """
        return 1.0/self.lambda_

    @property
    def MTTR(self):
        """ Return the Mean Time To Repair of the whole system.
            MTTR is defined as :
                       infty
                MTTR =  int 1 - M(t)dt = 1/mu when mu is constant
                         0
        """
        return 1.0/self.mu


class Voter(Component):
    """ Describe a voter with identical components having a constant failure
        rate
    """

    def __init__(self, component, M, N, lambda_=0, mu=0, initialy_avaible=True):
        """ `component` is kind of components used by the voter
            `N` is the initial number of components
            `M` is the minimal number of working components
            `lambda_` is the reliability of the voter
            `mu` is its maintainability
            `initialy_avaible`is a boolean set to True is the voter is avaible
            at t=0.
        """

        self.component = component
        name = '%s out-of %s − %s' % (M, N, component.name)
        super(Voter, self).__init__(name=name, lambda_=lambda_, mu=mu,
                                    initialy_avaible=initialy_avaible)
        self.M = M
        self.N = N

    def __repr__(self):
        return u'Voter(%s out-of %s)' % (self.M, self.N)

    def _probabilitiescomputation(self, t, method):
        prob = 0
        for k in xrange(self.M, self.N+1):
            a = getattr(self.component, method)(t)**k
            b = (1 - getattr(self.component, method)(t))**(self.N-k)
            prob += binom(self.N, k) * a * b
        return prob

    def reliability(self, t):
        """ Compute the reliability of the voter (and its components) at t """
        ownrel = super(Voter, self).reliability(t)
        return ownrel * self._probabilitiescomputation(t, 'reliability')

    def maintainability(self, t):
        raise NotImplementedError()

    def availability(self, t):
        """ Compute the availability of the voter (and its components) at t """
        ownavail = super(Voter, self).availability(t)
        return ownavail * self._probabilitiescomputation(t, 'availability')

    @property
    def MTTF(self):
        """ Return the Mean Time To Failure of the voters
            MTTF is defined as :
                       infty
                MTTF =  int R(t)dt
                         0
        """
        return quad(self.reliability, 0, inf)[0]

    @property
    def MTTR(self):
        """ Return the Mean Time To Repair of the whole system.
            MTTR is defined as :
                       infty
                MTTR =  int 1 - M(t)dt
                         0
        """
        raise NotImplementedError()


class System(object):

    def __init__(self, graph=None):
        """ Build a system made of different components.

            The components are linked together thanks to a reliability diagram.
            This reliability diagram is represented by a graph. This graph *must*
            have two special nodes called `E` and `S`. `E` represents the start
            of the system and `S` its end (names stand for “Entrée” (start) and
            “Sortie” (end) in French).

            Let’s have a look to the following system :

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
            >>> S.draw('my_system.dot')

            So, you can use the `System` object as a simple python dictionnary
            where each key is a component and the value associated it the list
            of the component’s successors.
        """
        self._graph = graph or {}
        self._tocompute = {'paths': True, 'mttf': True, 'mttr': True}
        self._allsuccesspaths = []
        self._mttf = 0.0
        self._mttr = 0.0

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
        for key in self._tocompute:
            self._tocompute[key] = True

    def __delitem__(self, component):
        del self._graph[component]
        for key in self._tocompute:
            self._tocompute[key] = True

    def __len__(self):
        return len(self._graph)

    def __repr__(self):
        return u'I\'m a system'

    @property
    def components(self):
        """ The list of the components used by the system """
        return [comp for comp in self._graph.iterkeys() if comp not in ['E', 'S']]

    def _probabilitiescomputation(self, t, method):
        #TODO : improve complexity ?
        #   n
        # P(U a_i) = sum     (-1)^{-1+|s|} P(^a_i)
        #  i=1      s\in[1,n],              i\in s
        #           s != {}
        #
        paths = self.successpaths
        R = 0.0
        for S in allsubsets(len(paths)):
            if not S:
                continue
            comps = set([c for i in S for c in paths[i][1:-1]])
            r = reduce(lambda x, y:x*getattr(y, method)(t), comps, 1)
            R += -r if len(S) % 2 == 0 else r
        return R

    def availability(self, t):
        """ Compute the availability of the whole system """
        return self._probabilitiescomputation(t, 'availability')

    def reliability(self, t):
        """ Compute the reliability of the whole system """
        return self._probabilitiescomputation(t, 'reliability')

    def maintainability(self, t):
        """ Compute the maintainability of the whole system """
        raise NotImplementedError()

    @property
    def MTTF(self):
        """ Return the Mean Time To Failure of the whole system.
            MTTF is defined as :
                       infty
                MTTF =  int R(t)dt
                         0
        """
        if self._tocompute['mttf']:
            self._mttf = quad(self.reliability, 0, inf)[0]
            self._tocompute['mttf'] = False
        return self._mttf

    @property
    def MTTR(self):
        """ Return the Mean Time To Repair of the whole system.
            MTTR is defined as :
                       infty
                MTTR =  int 1 - M(t)dt
                         0
        """
        raise NotImplementedError()


    @property
    def successpaths(self):
        """ Return all the success paths of the reliability diagram """
        if self._tocompute['paths']:
            self._allsuccesspaths = self.findallpaths(start='E', end='S')
            self._tocompute['paths'] = True
        return self._allsuccesspaths

    def findallpaths(self, start='E', end='S', path=[]):
        """ Find all paths from `start` to `end` in the reliability diagram """
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
        """ List the minimal cuts of the system of order <= `order`
            The method returns a list of frozensets, each frozenset contains a
            minimal cut.
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
        """ Print (or write) the content of the dot file needed to draw the
            fault tree of the system.

            If `output` is given, then the content is write into this file.
            `order` is the maximum order of the minimal cuts the function looks
            for.
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
        """ Print the content of the dot file needed to draw the system
            If `output` is given, then the content is write into this file.
        """
        def _getname(state):
            if state in ['E', 'S']:
                return state
            return state.name

        data = ['digraph G {', '\trankdir=LR;', '\tnode [shape=box];'
                '\tsplines=ortho;']
        for state in self._graph:
            for succ in self._graph[state]:
                data.append('\t"%s" -> "%s"' % (_getname(state), _getname(succ)))
        data.append('}')

        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')
