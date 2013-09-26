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

from __future__ import print_function, absolute_import
import unittest2

from system import Component, Voter, System

class TestComponent(unittest2.TestCase):
    pass

class TestVoter(unittest2.TestCase):
    pass

class TestSystem(unittest2.TestCase):

    def setUp(self):
        #Let’s build some standard systems
        systems = {'simple':System(),
                   'series-parallel':System(),
                   'parallel-series':System(),
                   'complex':System(),
                   'voter':System(),
                  }

        lambdas = {'alim':1e-4, 'motor':2e-5}
        mus = {'alim':5e-4, 'motor':2e-3}

        alim = [Component('Alim_A', lambda_=lambdas['alim'], mu=mus['alim']),
                Component('Alim_B', lambda_=lambdas['alim'], mu=mus['alim']),
                Component('Alim_C', lambda_=lambdas['alim'], mu=mus['alim']),
               ]
        motors = [Component('Motor_A', lambda_=lambdas['motor'], mu=mus['motor']),
                  Component('Motor_B', lambda_=lambdas['motor'], mu=mus['motor']),
                 ]

        voter = Voter(alim[0], M=2, N=3)

        systems['simple']['E'] = alim[0]
        systems['simple'][alim[0]] = motors[0]
        systems['simple'][motors[0]] = 'S'

        systems['series-parallel']['E'] = [alim[0], alim[1]]
        systems['series-parallel'][alim[0]] = motors[0]
        systems['series-parallel'][alim[1]] = motors[1]
        systems['series-parallel'][motors[0]] = 'S'
        systems['series-parallel'][motors[1]] = 'S'

        systems['parallel-series']['E'] = [alim[0], alim[1]]
        systems['parallel-series'][alim[0]] = [motors[0], motors[1]]
        systems['parallel-series'][alim[1]] = [motors[0], motors[1]]
        systems['parallel-series'][motors[0]] = 'S'
        systems['parallel-series'][motors[1]] = 'S'

        systems['complex']['E'] = [alim[0], alim[1], alim[2]]
        systems['complex'][alim[0]] = motors[0]
        systems['complex'][alim[1]] = [motors[0], motors[1]]
        systems['complex'][alim[2]] = motors[1]
        systems['complex'][motors[0]] = 'S'
        systems['complex'][motors[1]] = 'S'

        systems['voter']['E'] = voter
        systems['voter'][voter] = [motors[0], motors[1]]
        systems['voter'][motors[0]] = 'S'
        systems['voter'][motors[1]] = 'S'

        self.systems = systems
        self.alim = alim
        self.motors = motors
        self.voter = voter
        self.lambdas = lambdas
        self.mus = mus

    def test_successpaths(self):
        paths = {
            'simple' : set([('E', self.alim[0], self.motors[0], 'S')]),
            'series-parallel': set([('E', self.alim[0], self.motors[0], 'S'),
                                    ('E', self.alim[1], self.motors[1], 'S')]),
            'parallel-series': set([('E', self.alim[0], self.motors[0], 'S'),
                                    ('E', self.alim[0], self.motors[1], 'S'),
                                    ('E', self.alim[1], self.motors[1], 'S'),
                                    ('E', self.alim[1], self.motors[0], 'S')]),
            'complex': set([('E', self.alim[0], self.motors[0], 'S'),
                            ('E', self.alim[1], self.motors[0], 'S'),
                            ('E', self.alim[1], self.motors[1], 'S'),
                            ('E', self.alim[2], self.motors[1], 'S')]),
            'voter': set([('E', self.voter, self.motors[0], 'S'),
                          ('E', self.voter, self.motors[1], 'S')]),
        }

        for (name, S) in self.systems.iteritems():
            for path in S.successpaths:
                paths[name].remove(tuple(path))
            self.assertEqual(paths[name], set())

    def test_minimalcuts(self):
        #test is for orders 1 and 2 only…
        cuts = {
            1: {
                 'simple': set([frozenset([self.alim[0]]),
                                frozenset([self.motors[0]])]),
                 'series-parallel': set(),
                 'parallel-series': set(),
                 'complex': set(),
                 'voter': set([frozenset([self.voter])]),
               },
            2: {
                 'simple': set([frozenset([self.alim[0]]),
                                frozenset([self.motors[0]])]),
                 'series-parallel': set([frozenset([self.alim[1], self.alim[0]]),
                                         frozenset([self.alim[1], self.motors[0]]),
                                         frozenset([self.motors[1], self.alim[0]]),
                                         frozenset([self.motors[1], self.motors[0]]),
                                        ]),
                 'parallel-series': set([frozenset([self.alim[1], self.alim[0]]),
                                         frozenset([self.motors[1], self.motors[0]])]),
                 'complex': set([frozenset([self.motors[0], self.motors[1]])]),
                 'voter': set([frozenset([self.voter]),
                               frozenset([self.motors[0], self.motors[1]])]),
               },
        }

        for order in [1, 2]:
            for (name, S) in self.systems.iteritems():
                for cut in S.minimalcuts(order):
                    cuts[order][name].remove(cut)
                self.assertEqual(cuts[order][name], set([]))

    def test_mttfvalues(self):
        #Testing MTTF values is interesting because there are computed by
        #integration of reliability from 0 to \inf.
        #So if the values of MTTF are correct, it means :
        # - MTTF values are correct
        # - Reliabitily value for any t are correct too.
        #The drawback is that if this test fails, we don’t known which of MTTF
        #property or reliability method is failing.

        la = self.lambdas['alim']
        lm = self.lambdas['motor']
        mttf = {'simple': 1.0/(la + lm),
                'series-parallel': 3.0/(2*(la + lm)),
                'parallel-series':
                    1.0/(2*la + 2*lm) - 2.0/(2*la + lm) \
                    - 2.0/(la + 2*lm) + 4.0/(la + lm),
                'complex':
                    4.0/(la + lm) - 1.0/(2*lm + la) + 1.0/(2*lm + 3*la) \
                    - 1.0/(2*lm + 2*la) - 2.0/(2*la + lm),
                'voter':
                    6.0/(2*la + lm) - 3.0/(2*la + 2*lm) - 6.0/(3*la + lm) \
                    + 3.0/(3*la + 2*lm) + 2.0/(3*la + lm) - 1.0/(3*la + 2*lm)
               }

        for (name, values) in mttf.iteritems():
            self.assertAlmostEqual(values, self.systems[name].MTTF)

    def test_graphmanagement(self):
        component = [Component('C%s' % i, 1e-3) for i in xrange(4)]
        system = System()

        #because 'E' must be the first inserted element
        with self.assertRaises(ValueError):
            system[component[0]] = 'S'

        #Assert the following constructions don’t fail.
        #from a list
        system['E'] = [component[0], component[1]]
        system[component[0]] = 'S'
        self.assertEqual(system._graph, {'E':[component[0], component[1]],
                                         component[0]:'S'})
        del system[component[0]] #This component isn’t used anymore
        #from a single element
        system['E'] = component[1]
        system[component[1]] = 'S'
        self.assertEqual(system._graph, {'E':[component[1]],
                                         component[1]:'S'})


if __name__ == '__main__':
    unittest2.main()


