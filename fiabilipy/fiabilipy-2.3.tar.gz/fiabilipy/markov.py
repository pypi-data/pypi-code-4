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

from __future__ import print_function

from numpy import zeros, empty, binary_repr, where, array
from scipy.linalg import expm

from system import System, Component

__all__ = ['Markovprocess']

class Markovprocess(object):

    def __init__(self, components, initstates):
        """ Initialize the markov process management of the system.
            - `components` is the list of the components to manage
            - `initstates` describes the initial state of the process.

            Example :
                Let S be a system of two components A and B.

                >>> comp = (A, B)
                >>> init = [0.8, 0.1, 0.1, 0]
                >>> process = Markovprocess(comp, init)

                init[0] is the probability of having A and B working
                init[1] is the probability of having A working and not B
                init[2] is the probability of having B working and not A
                init[3] is the probability of having neither A nor B working

                In a general way init[i] is the probability of having :
                    for c, state in enumerate(binary_repr(i, len(components))):
                        if state :
                            print('%s working' % components[c])
                        else:
                            print('%s not working' % components[c])

                `initstates` may be very sparse, and given through a
                dictionnary as follow :

                >>> init = {}
                >>> init[0] = 0.8
                >>> init[1] = init[2] = 0.1

        """

        self.components = tuple(components) #assert order won’t change
        self.matrix = None
        if isinstance(initstates, dict):
            N = len(self.components)
            self.initstates = array([initstates.get(x, 0) for x in xrange(2**N)])
        else:
            self.initstates = array(initstates)
        self._initmatrix()

    def _initmatrix(self):
        N = len(self.components)
        #2^N different states
        #Let’s build the 2^(2N) matrix…
        self.matrix = zeros((2**N, 2**N))

        for i in xrange(2**N):
            currentstate = array([int(x) for x in binary_repr(i, N)])
            for j in xrange(i+1, 2**N):
                newstate = array([int(x) for x in binary_repr(j, N)])
                tocheck = where(newstate != currentstate) #Components changed
                if len(tocheck[0]) > 1: #Impossible to reach
                    continue

                component = self.components[tocheck[0][0]]#The changed component
                self.matrix[i, j] = component.lambda_
                self.matrix[j, i] = component.mu

        rowsum = self.matrix.sum(axis=1)
        self.matrix[xrange(2**N), xrange(2**N)] = -rowsum

    def computestates(self, func):
        """
            `func` is a function defining if a state is tracked or not

            >>> comp = (A, B, C, D)
            >>> process = Markovprocess(comp, {0:1})
            >>> states = lambda x: (x[0]+x[1]) * (x[2]+x[3])
            >>> process.definestates(states)

            This defines the following parallel-series system :

                 | -- A -- |    | -- C -- |
            E -- |         | -- |         | -- S
                 | -- B -- |    | -- D -- |
        """

        N = len(self.components)
        N2 = 2**N
        states = []
        for x in xrange(N2):
            s = [int(i) for i in binary_repr(N2 - 1 - x, N)]
            if func(s):
                states.append(x)
        return states

    def value(self, t, states=None):
        v = self.initstates.dot(expm(t*self.matrix))
        if not states :
            return v
        else :
            return v[(states, )].sum()

    def draw(self, output=None):
        def bin(x, N):
            return ''.join([i for i in binary_repr(x, N)])

        N = len(self.components)
        N2 = 2**N
        data = ['digraph G {', '\trankdir=LR;']
        for i in xrange(N2):
            bini = bin(N2 - 1 - i, N)
            for j in xrange(i, N2):
                if not self.matrix[i, j]:
                    continue

                if i == j:
                    data.append('%s -> %s [label = "%s"]'
                                % (bini, bini, 1.0 + self.matrix[i, j]))
                else:
                    binj = bin(N2 - 1 - j, N)
                    data.append('%s -> %s [label = "%s"]'
                                % (bini, binj, self.matrix[i, j]))
                    data.append('%s -> %s [label = "%s"]'
                                % (binj, bini, self.matrix[j, i]))
        data.append('}')
        if not output:
            print('\n'.join(data))
        else:
            try:
                output.write('\n'.join(data) + '\n')
            except AttributeError:
                with open(output, 'w') as fobj:
                    fobj.write('\n'.join(data) + '\n')
