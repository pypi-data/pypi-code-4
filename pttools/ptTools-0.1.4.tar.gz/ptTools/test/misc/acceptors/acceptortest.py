#!/usr/bin/env python3

import unittest

from ptTools.misc import acceptors
from ptTools.misc.acceptors import Final
from ptTools.misc.acceptors import Single
from ptTools.misc.acceptors import Union
from ptTools.misc.acceptors import Compound


class RegularLanguageAcceptorTest(unittest.TestCase):

    def assertAccept(self, coll, expr):
        """Pass if expr accepts coll."""        
        self.assertTrue(expr.accepts(coll))
        ## Comment the following line, if copying fails!
        self.assertTrue(expr.copy().accepts(coll))

    def denyAccept(self, coll, expr):
        """Fails if expr accepts coll."""
        self.assertFalse(expr.accepts(coll))
        ## Comment the following line, if copying fails!        
        self.assertFalse(expr.copy().accepts(coll))

    def assertTypes(self, rx, dict):
        copy = rx.copy()
        for k,v in dict.items():
            self.assertEqual(len(rx.states_of_type(k)), v)
            ## Comment the following line, if copying fails!
            self.assertEqual(len(copy.states_of_type(k)), v)

    def assertPath(self, word, expected):
        start = expected[0]
        path = [a for a,b in start.path_of(word)]
        self.assertListEqual(path, expected)
        
    def test_single_00(self):
        """Matching word of single element."""
        a = Single('a')
        self.assertAccept('a', a)
        self.denyAccept('', a)
        self.denyAccept('aaa', a)                        
        self.denyAccept(0, a)
        self.denyAccept(None, a)
        self.assertTypes(a, {Single  : 1,
                             Union   : 0,
                             Final   : 1})
        self.assertPath('a',
                        [a, a.final_states[0]])

    def test_single_01(self):
        """Manually creating a positive closure."""
        a = Single('a')
        f = Final()
        u = Union(f, a)
        a.successor = u
        self.assertAccept('a', a)
        self.assertAccept('aa', a)
        self.assertAccept('aaa', a)
        self.denyAccept('', a)
        self.denyAccept('b', a)        
        self.denyAccept('ab', a)        
        self.denyAccept('ba', a)        
        self.denyAccept('aba', a)
        self.assertTypes(a, {Single  : 1,
                             Union   : 1,
                             Final   : 1})

    def test_single_02(self):
        """
        Beware!        
        >>> ().__eq__(())
        True
        >>> () == []
        False

        But:        
        >>> ().__eq__([])
        NotImplemented
        >>> [].__eq__(())
        NotImplemented
        >>> bool(NotImplemented)
        True

        Hence:
        >>> bool(().__eq__([])) ## WTF!
        True 
        
        """
        self.assertRaises(TypeError, Single)
        self.assertAccept([False], Single(False))
        self.assertAccept([True], Single(True))
        self.assertAccept([None], Single(None))
        self.assertAccept(([],), Single([]))
        self.assertAccept([()], Single(()))
        ## self.denyAccept([()], Single([]))
        ## self.denyAccept([[]], Single(()))
        self.assertAccept((0,), Single(0))
        self.assertAccept([23], Single(23))
        self.assertAccept(['spam'], Single('spam'))
        self.denyAccept('spam', Single('spam'))
        
    def test_final_00(self):
        """Accepting the empty collection."""
        e = Final()
        self.assertAccept('', e)
        self.assertAccept([], e)        
        self.assertAccept(None, e)
        self.denyAccept('a', e)
        self.assertTypes(e, {Single : 0,
                             Final  : 1,
                             Union  : 0})

    def test_Epsilon_04(self):
        """Manually creating a kleene closure."""
        a = Single('a')        
        e = Union(Final(), a)
        a.replace_all_final(e)
        self.assertAccept('', e)
        self.assertAccept('a', e)        
        self.assertAccept('aaa', e)
        self.denyAccept('b', e)
        self.assertTypes(e, {Single : 1,
                             Final  : 1,
                             Union  : 1})

    def test_concatenation_00(self):
        """Concatenating acceptors."""        
        r = Single('r')
        s = Single('s')
        rs = r + s
        self.assertAccept('rs', rs)
        self.denyAccept('', rs)
        self.denyAccept('r', rs)
        self.denyAccept('s', rs)
        self.denyAccept('rr', rs)
        self.denyAccept('sr', rs)
        self.denyAccept('ss', rs)
        self.assertTypes(rs, {Single : 2,
                              Final  : 1,
                              Union  : 0})

    def test_concatenation_01(self):
        """Concatenating acceptors."""        
        r = Single('r')
        s = Single('s')
        t = Single('t')
        rst = r + s + t
        self.assertAccept('rst', rst)
        self.denyAccept('', rst)
        self.denyAccept('r', rst)
        self.denyAccept('rs', rst)
        self.denyAccept('rt', rst)
        self.denyAccept('st', rst)
        self.denyAccept('rrst', rst)
        self.denyAccept('rstt', rst)
        self.denyAccept('rsst', rst)
        self.denyAccept('rstrst', rst)
        self.assertTypes(rst, {Single : 3,
                               Final  : 1,
                               Union  : 0})

    def test_concatenation_02(self):
        """Concatenating concatenations."""
        r = Single('r')
        s = Single('s')
        t = Single('t')
        u = Single('u')        
        rx = (r + s) + (t + u)
        self.assertAccept('rstu', rx)
        self.denyAccept('rs', rx)
        self.denyAccept('tu', rx)
        self.denyAccept('rst', rx)
        self.denyAccept('rsu', rx)
        self.assertTypes(rx, {Single : 4,
                              Final  : 1,
                              Union  : 0})

    def test_concatenation_03(self):
        """Concatenating Final."""
        r = Single('r')
        u = Union(Final())
        rx = r + u
        self.assertAccept('r', rx)
        self.denyAccept('', rx)
        self.denyAccept('rr', rx)
        rx = u + r
        self.assertAccept('r', rx)
        self.denyAccept('', rx)
        self.denyAccept('rr', rx)

    def test_union_00(self):
        """Union of acceptors."""
        r = Single('r')
        s = Single('s')
        t = Single('t')
        rx = r | s | t
        self.assertAccept('r', rx)
        self.assertAccept('s', rx)
        self.assertAccept('t', rx)
        self.denyAccept('', rx)        
        self.denyAccept('rs', rx)
        self.denyAccept('rt', rx)
        self.denyAccept('st', rx)
        self.denyAccept('rr', rx)
        self.assertTypes(rx, {Single : 3,
                              Final  : 3, ## One after each of r,s,t.
                              Union  : 1})

    def test_union_01(self):
        """Concatenating a Union."""
        r = Single('r')
        s = Single('s')
        t = Single('t')
        rx = (r | s) + t ## Results in diamond shape.
        self.assertAccept('rt', rx)
        self.assertAccept('st', rx)
        self.denyAccept('', rx)        
        self.denyAccept('r', rx)
        self.denyAccept('s', rx)
        self.denyAccept('t', rx)        
        self.denyAccept('rs', rx)
        self.assertTypes(rx, {Single  : 3,
                              Union   : 1,
                              Final   : 1})

    def test_union_02(self):
        """Appending a state to a Union."""
        r = Single('r')
        s = Single('s')
        t = Single('t')
        rx = r + (s | t)
        self.assertAccept('rt', rx)
        self.assertAccept('rs', rx)
        self.denyAccept('', rx)        
        self.denyAccept('r', rx)
        self.denyAccept('s', rx)
        self.denyAccept('t', rx)        
        self.denyAccept('st', rx)
        self.assertTypes(rx, {Single  : 3,
                              Union   : 1,
                              Final   : 2})

    def test_union_03(self):
        """Manually creating a union."""
        e = Union()
        a = Single('a')
        b = Single('b')
        e.options.append(a)
        e.options.append(b)
        self.assertAccept('a', e)
        self.assertAccept('b', e)
        self.denyAccept('aa', e)
        self.denyAccept('ab', e)
        self.denyAccept('ba', e)
        self.denyAccept('bb', e)
        self.assertTypes(e, {Single : 2,
                             Final  : 2,
                             Union  : 1})

    def test_option_00(self):
        rx = -Single('r')
        self.assertAccept('', rx)
        self.assertAccept('r', rx)        
        self.denyAccept('rrrr', rx)                
        self.assertTypes(rx, {Single  : 1,
                              Union   : 1,
                              Final   : 2})

    def test_option_01(self):
        r = Single('r')
        s = Single('s')
        rx = -(r+s)
        self.assertAccept('', rx)
        self.assertAccept('rs', rx)        
        self.denyAccept('r', rx)                
        self.denyAccept('s', rx)                
        self.denyAccept('rrs', rx)                
        self.assertTypes(rx, {Single  : 2,
                              Union   : 1,
                              Final   : 2})

    def test_positive_closure_00(self):
        """Simple positive closure."""
        rx = +Single('r')
        self.assertAccept('r', rx)
        self.assertAccept('rrrr', rx)                
        self.denyAccept('', rx)
        self.assertTypes(rx, {Single  : 1,
                              Union   : 1,
                              Final   : 1})

    def test_positive_closure_01(self):
        """Closure of concatenation."""        
        rs = Single('r') + Single('s')
        rx = +rs
        self.assertAccept('rs', rx)
        self.assertAccept('rsrs', rx)                
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('rsr', rx)
        self.denyAccept('rss', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 1,
                              Final   : 1})

    def test_positive_closure_02(self):
        """Appending to closure."""
        r = Single('r')
        s = Single('s')
        rx = +r + s
        self.assertAccept('rs', rx)
        self.assertAccept('rrrrs', rx)
        self.denyAccept('', rx)
        self.denyAccept('s', rx)
        self.denyAccept('r', rx)
        self.denyAccept('rrr', rx)
        self.denyAccept('rrsr', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 1,
                              Final   : 1})

    def test_positive_closure_03(self):
        """Closure of union."""
        r = Single('r')
        s = Single('s')
        rx = +(r | s)
        self.assertAccept('r', rx)
        self.assertAccept('s', rx)
        self.assertAccept('rrrrs', rx)
        self.assertAccept('srrsrrs', rx)
        self.denyAccept('', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 2,
                              Final   : 1})

    def test_positive_closure_04(self):
        """Closure with tail.  Tests backtracking."""
        ab = Single('a') + Single('b')
        ac = Single('a') + Single('c')
        rx = +ab + ac
        self.assertAccept('abac', rx)
        self.assertAccept('ababac', rx)
        self.denyAccept('ac', rx)
        self.denyAccept('abc', rx)
        self.denyAccept('acac', rx)
        self.assertTypes(rx, {Single  : 4,
                              Union   : 1,
                              Final   : 1})

    def test_positive_closure_05(self):
        """Manually creating a kleene closure."""
        a = +Single('a')        
        e = Union(a, Final())
        self.assertAccept('', e)
        self.assertAccept('a', e)        
        self.assertAccept('aaa', e)
        self.denyAccept('b', e)
        self.assertTypes(e, {Single  : 1,
                             Union   : 2,
                             Final   : 2})

    def test_kleene_closure_00(self):
        """Simple kleene closure."""
        rx = ~Single('r')
        self.assertAccept('', rx)
        self.assertAccept('r', rx)
        self.assertAccept('rrrr', rx)                
        self.assertTypes(rx, {Single  : 1,
                              Union   : 2,
                              Final   : 2})

    def test_kleene_closure_01(self):
        """Closure of concatenation."""        
        rs = Single('r') + Single('s')
        rx = ~rs
        self.assertAccept('', rx)
        self.assertAccept('rs', rx)
        self.assertAccept('rsrs', rx)                
        self.denyAccept('r', rx)
        self.denyAccept('rsr', rx)
        self.denyAccept('rss', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 2, 
                              Final   : 2})

    def test_kleene_closure_02(self):
        """Appending to kleene closure."""
        r = Single('r')
        s = Single('s')
        rx = ~r + s
        self.assertAccept('s', rx)
        self.assertAccept('rs', rx)
        self.assertAccept('rrrrs', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('rrr', rx)
        self.denyAccept('rrsr', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 2,
                              Final   : 1})

    def test_kleene_closure_03(self):
        """Closure of union."""
        r = Single('r')
        s = Single('s')
        rx = ~(r | s)
        self.assertAccept('', rx)
        self.assertAccept('r', rx)
        self.assertAccept('s', rx)
        self.assertAccept('rrrrs', rx)
        self.assertAccept('srrsrrs', rx)
        self.assertTypes(rx, {Single  : 2,
                              Union   : 3,
                              Final   : 2})

    def test_kleene_closure_04(self):
        """Manually creating a kleene closure."""
        """Closure with tail.  Tests backtracking."""
        ab = Single('a') + Single('b')
        ac = Single('a') + Single('c')
        rx = ~ab + ac
        self.assertAccept('ac', rx)
        self.assertAccept('abac', rx)
        self.assertAccept('ababac', rx)
        self.denyAccept('abc', rx)
        self.denyAccept('acac', rx)

    def test_copy_00(self):
        rx = Single('r').copy()
        self.assertAccept('r', rx)
        self.denyAccept('', rx)
        self.denyAccept('rr', rx)
        
    def test_copy_01(self):        
        r = Single('r')
        s = Single('s')
        rx = (r + s).copy()
        self.assertAccept('rs', rx)
        self.denyAccept('r', rx)                
        self.denyAccept('s', rx)                

    def test_copy_03(self):        
        r = Single('r')
        s = Single('s')
        rx = (r | s).copy()
        self.assertAccept('r', rx)
        self.assertAccept('s', rx)        
        self.denyAccept('', rx)                
        self.denyAccept('rs', rx)                

    def test_copy_04(self):        
        rx = Single('r') * 3
        self.assertAccept('rrr', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('rr', rx)                          
        self.denyAccept('rrrr', rx)

    def test_copy_05(self):        
        r = Single('r')
        s = Single('s')
        t = Single('t')        
        rx = ((r | s) + t).copy()
        self.assertAccept('rt', rx)
        self.assertAccept('st', rx)        
        self.denyAccept('', rx)                
        self.denyAccept('rs', rx)
        self.denyAccept('rst', rx)

    def test_copy_06(self):        
        r = Single('r')
        rx = (~r).copy()
        self.assertAccept('', rx)
        self.assertAccept('r', rx)
        self.assertAccept('rrr', rx)                

    def test_repetition_00(self):
        r = Single('r')
        rx = r * 1
        self.assertAccept('r', rx)
        self.denyAccept('', rx)
        self.denyAccept('rr', rx)

    def test_repetition_01(self):
        r = Single('r')
        rx = r * 2
        self.assertAccept('rr', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)        
        self.denyAccept('rrr', rx)
        self.denyAccept('rrrr', rx)        

    def test_repetition_02(self):
        r = Single('r')
        rx = r * 3
        self.assertAccept('rrr', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)                
        self.denyAccept('rr', rx)        
        self.denyAccept('rrrr', rx)

    def test_repetition_03(self):
        r = Single('r')
        s = Single('s')        
        rx = (r * 3) + s
        self.assertAccept('rrrs', rx)
        self.denyAccept('', rx)
        self.denyAccept('s', rx)        
        self.denyAccept('rs', rx)                
        self.denyAccept('rrs', rx)        
        self.denyAccept('rrrrs', rx)

    def test_repetition_04(self):
        r = Single('r')
        s = Single('s')        
        rx = (r | s) * 3
        self.assertAccept('rrr', rx)
        self.assertAccept('rrs', rx)
        self.assertAccept('rsr', rx)
        self.assertAccept('rss', rx)
        self.assertAccept('srr', rx)
        self.assertAccept('srs', rx)
        self.assertAccept('ssr', rx)
        self.assertAccept('sss', rx)                                        

    def test_repetition_05(self):
        r = Single('r')
        s = Single('s')        
        rx = (r + s) * 2
        self.assertAccept('rsrs', rx)
        self.denyAccept('rs', rx)
        self.denyAccept('rsrsrs', rx)
        self.denyAccept('rrs', rx)                        
        self.denyAccept('rrrs', rx)                        
        self.denyAccept('rss', rx)
        self.denyAccept('rsss', rx)

    def test_compound_00(self):
        rs = Single('r') + Single('s')
        rx = Compound(rs)
        self.assertAccept('rs', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('s', rx)
        self.denyAccept('rr', rx)
        self.denyAccept('ss', rx)
        self.denyAccept('sr', rx)
        self.denyAccept('rsrs', rx)

    def test_compound_01(self):
        rs = Single('r') + Single('s')
        rx = Compound(+rs)
        self.assertAccept('rs', rx)
        self.assertAccept('rsrs', rx)
        self.assertAccept('rsrsrs', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('s', rx)
        self.denyAccept('rsr', rx)

    def test_compound_02(self):
        rs = Single('r') + Single('s')
        rx = +Compound(rs)
        self.assertAccept('rs', rx)
        self.assertAccept('rsrs', rx)
        self.assertAccept('rsrsrs', rx)
        self.denyAccept('', rx)
        self.denyAccept('r', rx)
        self.denyAccept('s', rx)
        self.denyAccept('rsr', rx)


if __name__ == '__main__':

    unittest.main()
