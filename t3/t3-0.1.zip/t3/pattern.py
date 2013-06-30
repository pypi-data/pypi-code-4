# ======================================================================
#
# Copyright (C) 2013 Kay Schluehr (kay@fiber-space.de)
#
# t3pattern.py, v B.0 2013/09/03
#
# ======================================================================

import sys
import string
import abc
from copy import copy
from t3.t3abc import T3Matcher
from t3.number import T3Number, Hex
from t3.util.reverb import*
import pprint


class T3Match(object):
    def __init__(self, value, rest):
        self.value = value
        self.rest  = rest

    def __nonzero__(self):
        return self.value is not T3Number.NULL

    def __eq__(self, other):
        if isinstance(other, T3Match):
            return self.value == other.value and self.rest == other.rest
        return False

    def __repr__(self):
        return "<T3Match <%s:%s>>"%(self.value, self.rest)

class T3MatchFail(T3Match):
    def __init__(self, rest, fail_pos, err_object = None):
        self.value = T3Number.NULL
        self.rest  = rest
        self.fail_pos = fail_pos
        self.err_object = err_object

    def __repr__(self):
        return "<T3MatchFail <%s:%s>>"%(self.value, self.rest)

class T3LMatch(T3Match):
    def __init__(self, value, left, right):
        super(T3LMatch, self).__init__(value, right)
        self.left = left

class MatchingFailure(Exception):
    def __init__(self, t3match):
        self.t3match = t3match

    def __str__(self):
        S = ""
        try:
            S = "\n\n"+str(self.t3match.err_object)+"\n\n"
        except AttributeError:
            pass

        if self.t3match.fail_pos == 0:
            S1 = ""
            k  = len(str(self.t3match.rest[:self.t3match.fail_pos+1]))
            z  = 0
        else:
            S1 = str(self.t3match.rest[:self.t3match.fail_pos])
            S2 = str(self.t3match.rest[:self.t3match.fail_pos+1])
            k = len(S2)-len(S1)
            z = 0
            for c in S2[len(S1):]:
                if c == " ":
                    k-=1
                    z+=1
                else:
                    break

        pos_marker = "at position %s."%(self.t3match.fail_pos+1,)
        if not S:
            underline = " "*(50+len(S1)+z-len(pos_marker)) + k*"^"
        else:
            underline = " "*(22+len(S1)+z-len(pos_marker)) + k*"^"
        return S+"Failed to match data '%s'\n%s%s\n"%(self.t3match.rest, pos_marker, underline)

pPrefix     = Group(Required(Digit)+Text("'") | Text("b'") | Text("n'"), "NUMBASE")
pHex        = Required(Digit|Set("abcdefABCDEF"))
pWhite      = Required(Whitespace)
pNumber     = Group(pHex+Optional(pWhite+pHex), "NUMBER")
pLetter     = Set(string.letters+"_")
pWord       = Group(pLetter + Optional(Alphanum), "NAME")
pStar       = Group(Text("*"), "STAR")
pWildcard   = Group(Text("?"), "WILDCARD")
pVbar       = Group(Text("|"), "VBAR")
pColon      = Group(Text(":"), "COLON")
pLpar       = Group(Text("("), "LPAR")
pRpar       = Group(Text(")"), "RPAR")
pRange      = Group(Required(".", 2), "RANGE")
pLbra       = Group(Text("{"), "LBRA")
pRbra       = Group(Text("}"), "RBRA")
pWhitespace = Group(pWhite, "WHITE")
pToken      = Re( pPrefix | pNumber | pWord | pStar | pWildcard | pVbar | pLpar | pRpar | pRange | pLbra | pRbra | pColon | pWhitespace )

TOKEN_TYPE  = 0
TOKEN_STR   = 1
TOKEN_COL   = 1
SYMBOL_TYPE = 0

def tokenize(S):
    tokens = []
    k = 1
    while S:
        m = pToken.match(S)
        if m:
            for name, value in m.groupdict().items():
                if value is not None:
                    n = len(value)
                    if name != "WHITE":
                        tokens.append([name, value, (k, k+n)])
                    k+= n
                    S = S[n:]
                    break
        else:
            raise SyntaxError("Tokenizer failed at character '%s' in input string at position %s."%(S[0], k))
    return tokens

'''
pattern: pattern_alt
pattern_alt: pattern_seq ('|' pattern_seq)*
pattern_seq: pattern_range+
pattern_range: ( pattern_atom |
                 pattern_atom bit_field |
                 pattern_atom RANGE [ pattern_atom ]
                 pattern_atom bit_field RANGE [ pattern_atom bit_field]
               ) [multiple]

pattern_atom: NAME | [NUMBASE] NUMBER | STRING | '*' | WILDCARD | '(' pattern_alt ')' [multiple]

multiple: '{' range_expr '}'
range_expr: NUMBASE* (  atom |
                        atom bit_field |
                        atom [bit_field] RANGE [ [NUMBASE] atom [bit_field]]
                      )

bit_field: ':' NUMBER
'''

def find_name(name, frame):
    if name in frame.f_globals:
        return frame.f_globals[name]
    elif frame.f_back:
        return find_name(name, frame.f_back)

def Tree(sq):
    if len(sq)>1:
        return sq

def parse(tokens):
    P, tokens = parse_alt(tokens)
    if P:
        return ["pattern", P], tokens
    return None, tokens

def parse_alt(tokens):
    alt = ["alt"]
    while tokens:
        P, tokens = parse_seq(tokens)
        if P:
            alt.append(P)
        else:
            return Tree(alt), tokens
        if tokens:
            T = tokens[0]
            if T[TOKEN_TYPE] == "VBAR":
                tokens = tokens[1:]
                continue
            else:
                break
    return Tree(alt), tokens

def parse_seq(tokens):
    seq = ["seq"]
    while tokens:
        P, tokens = pattern_range(tokens)
        if P:
            seq.append(P)
        else:
            return Tree(seq), tokens
        if tokens:
            continue
        else:
            return Tree(seq), []

def pattern_range(tokens):
    pt = ["range"]
    P, tokens = pattern_atom(tokens)
    if P:
        pt.append(P)
        if tokens:
            P, tokens = pattern_bitfield(tokens)
            is_bitfield = False
            if P:
                pt.append(P)
                is_bitfield = True
            if tokens:
                T = tokens[0]
                if T[TOKEN_TYPE] == "RANGE":
                    pt.append(T)
                    tokens = tokens[1:]
                    P, tokens = pattern_atom(tokens)
                    if P:
                        pt.append(P)
                        if tokens:
                            P, tokens = pattern_bitfield(tokens)
                            if P:
                                pt.append(P)
                                if not is_bitfield:
                                    tokens.insert(0, ["ERROR", "Incomplete bit range. Upper bound missing", T[TOKEN_COL]])
                            elif is_bitfield:
                                tokens.insert(0, ["ERROR", "Incomplete bit range. Lower bound missing", T[TOKEN_COL]])

        if tokens:
            P, tokens = pattern_multiple(tokens)
            if P:
                pt.append(P)
    elif tokens[0][TOKEN_TYPE] == "RANGE":
        T = tokens[0]
        tokens.insert(0, ["ERROR", "Range must have a lower bound. None found", T[TOKEN_COL]])
    return Tree(pt), tokens


def pattern_atom(tokens):
    atom = ["atom"]
    if tokens:
        T = tokens[0]
        if T[0] == "ERROR":
            return None, tokens
        elif T[0] in ("NAME", "STAR", "WILDCARD"):
            atom.append(T)
            tokens = tokens[1:]
        elif T[0] == "NUMBER":
            atom.append(["number", T])
            tokens = tokens[1:]
        elif T[0] == "NUMBASE":
            tokens = tokens[1:]
            if not tokens or tokens[0][TOKEN_TYPE]!="NUMBER":
                if tokens[0][0] != "ERROR":
                    tokens.insert(0, ["ERROR", "Number expected. '%s' found."%tokens[0][TOKEN_STR], T[TOKEN_COL][0]])
                return None, tokens
            else:
                atom.append(["number", T, tokens[0]])
                tokens = tokens[1:]
        elif T[0] == "LPAR":
            P, tokens = parse_alt(tokens[1:])
            if not tokens:
                tokens.insert(0, ["ERROR", "Closing parenthesis ')' expected.", (-1, -1)])
                return None, tokens
            elif tokens[0][0]!="RPAR":
                tokens.insert(0, ["ERROR", "Closing parenthesis ')' expected. '%s' found."%tokens[0][TOKEN_STR], tokens[0][TOKEN_COL]])
                return None, tokens
            else:
                tokens = tokens[1:]
                if P:
                    atom.append(P)
                    P, tokens = pattern_multiple(tokens)
                    if P:
                        atom.append(P)
    return Tree(atom), tokens

def pattern_bitfield(tokens):
    mt = ["bitfield"]
    if tokens:
        T = tokens[0]
        if T[0] == "COLON":
            t = tokens[1:]
            P, tokens = pattern_atom(t)
            if not P or P[1][0]!="number" or P[1][1][0]!="NUMBER":
                tokens.insert(0, ["ERROR", "Number expected. '%s' found."%t[0][TOKEN_STR], t[0][TOKEN_COL]])
            else:
                mt.append(P[1][1])
    return Tree(mt), tokens


def pattern_multiple(tokens):
    mt = ["mult"]
    if tokens:
        T = tokens[0]
        if T[TOKEN_TYPE] == "LBRA":
            P, tokens = pattern_range(tokens[1:])
            if not tokens:
                tokens.insert(0, ["ERROR", "Closing brace '}' expected.", (-1, -1)])
                return None, tokens
            elif tokens[0][0]!="RBRA":
                tokens.insert(0, ["ERROR", "Closing brace '}' expected. '%s' found."%tokens[0][TOKEN_STR], tokens[0][TOKEN_COL]])
                return None, tokens
            elif not P:
                tokens.insert(0, ["ERROR", "Range expected. '%s' found."%tokens[0][TOKEN_STR], tokens[0][TOKEN_COL]])
            else:
                tokens = tokens[1:]
                mt.append(P)
    return Tree(mt), tokens




def T3Pattern(expr):
    tokens = tokenize(expr)
    P, tokens = parse(tokens)
    if tokens:
        T = tokens[0]
        if T[0] == "ERROR":
            a, b = T[TOKEN_COL]
            err_message = "Failure at '%s'. Cannot parse '%s' at position %s.\n             %s"%(expr[a-1:b-1], expr, T[2][0], T[1])
            raise SyntaxError(err_message)
        else:
            raise SyntaxError("Failure at '%s'. Cannot parse '%s' at position %s"%(T[TOKEN_STR], expr, T[TOKEN_TYPE][0]))
    assert P[SYMBOL_TYPE] == "pattern", P[SYMBOL_TYPE]
    assert P[1][SYMBOL_TYPE] == "alt"
    return T3PatternAlt.compile(P[1])


class T3PatternObject(object):
    @classmethod
    def compile(cls, tree):
        pass

    def find(self, data):
        n = len(data)
        i = 0
        while i<n:
            sub = data[i:]
            m = self.match(sub)
            if m:
                return T3LMatch(m.value, data[:i], m.rest)
            i+=1
        return T3MatchFail(data, 0)

    def rfind(self, data):
        n = len(data)-1
        while n>=0:
            sub = data[n:]
            m = self.match(sub)
            if m:
                return T3LMatch(m.value, data[:n], m.rest, True)
            n-=1
        return T3MatchFail(data, 0)

    def __add__(self, other):
        if isinstance(other, T3PatternSequence):
            other.patterns.insert(0, self)
            return other
        else:
            return T3PatternSequence(self, other)

    def __or__(self, other):
        if isinstance(other, T3PatternAlt):
            other.patterns.insert(0, self)
            return other
        else:
            return T3PatternAlt(self, other)

    def is_variable(self):
        return False


class T3PatternAlt(T3PatternObject):
    def __init__(self, *args):
        self.patterns = args

    def match(self, data):
        for p in self.patterns:
            m = p.match(data)
            if m:
                return m
        return T3MatchFail(data, 0)

    @classmethod
    def compile(cls, tree):
        assert tree[SYMBOL_TYPE] == "alt", tree[SYMBOL_TYPE]
        if len(tree)>2:
            return T3PatternAlt(*[T3PatternSeq.compile(T) for T in tree[1:]])
        else:
            return T3PatternSeq.compile(tree[1])


class T3PatternSeq(T3PatternObject):

    def __init__(self, *args):
        self.patterns = []
        last = None
        for i, arg in enumerate(args):
            if last:
                if type(arg) == type(last):
                    if type(arg) == T3PatternVar:
                        continue
                    elif type(arg) == T3PatternWildcard:
                        self.patterns[-1].digits+=arg.digits
                    elif type(arg) in ( T3PatternSeq, T3PatternAlt ):
                        self.patterns[-1].patterns+=arg.patterns
                elif type(arg) == T3PatternWildcard and type(last) == T3PatternVar:
                    self.patterns.pop()
                    arg, last = last, arg
                    self.patterns.append(last)
            self.patterns.append(arg)
            last = arg

    def match(self, data):
        m = T3Match(T3Number.NULL, data)
        sb = []
        i = 0
        n = len(self.patterns)
        while i<n:
            pattern = self.patterns[i]
            if pattern.is_variable():
                if i == n-1:
                    m = pattern.match(m.rest)
                    i+=1
                else:
                    i+=1
                    next = self.patterns[i]
                    if i == n-1:
                        m1 = next.rfind(m.rest)
                        if m1.rest is not T3Number.NULL:
                            return T3MatchFail(data, len(data)-len(m.rest))
                    else:
                        m1 = next.find(m.rest)
                    if not m1:
                        return T3MatchFail(data, len(data)-len(m.rest))
                    left = m1.left
                    if left is not T3Number.NULL:
                        m2 = pattern.match(left)
                        sb.append(left.digits())
                    sb.append(m1.value.digits())
                    m = m1
                    i+=1
                    continue
            else:
                m = pattern.match(m.rest)
                i+=1
            if m:
                if isinstance(m.value, T3Matcher):
                    sb.append(m.value.get_value().digits())
                else:
                    sb.append(m.value.digits())
            elif not isinstance(m, T3MatchFail):
                continue
            else:
                m.fail_pos   = len(data)-len(m.rest)
                m.err_object = pattern
                m.rest       = data
                return m
        if sb:
            if isinstance(m.rest, T3Number):
                return T3Match(m.rest.__class__("".join(sb), m.rest.base), m.rest)
            else:
                return T3Match(data.__class__("".join(sb), data.base), m.rest)
        else:
            return T3MatchFail(data, 0)


    @classmethod
    def compile(cls, tree):
        assert tree[SYMBOL_TYPE] == "seq", tree[SYMBOL_TYPE]
        if len(tree)>2:
            return T3PatternSeq(*[T3PatternRange.compile(T) for T in tree[1:]])
        else:
            return T3PatternRange.compile(tree[1])


class T3PatternRange(T3PatternObject):
    def __init__(self, left, right):
        self.left  = left
        if right is None:
            self.right = self.left.__class__(sys.maxint, self.left.base)
        else:
            self.right = right
        if self.right<self.left:
            self.left, self.right = self.right, self.left

    def match(self, data):
        if not isinstance(data, T3Number):
            data = T3Number(data, self.left.base)
        k = len(self.left)
        if data.base!=self.left.base:
            matches = self.left.__class__(data, self.left.number.base)[:k]
        else:
            matches = data[:k]
        if matches>=self.left:
            if matches<=self.right:
                k+=1
                n = len(self.right)
                while k<n:
                    match_next = data[:k]
                    if match_next<=self.right:
                        matches = match_next
                        k +=1
                    else:
                        break
                    return T3Match(matches, data[len(matches):])
        return T3MatchFail(data, 0)


    @classmethod
    def compile(cls, tree):
        '''
        pattern_range: ( pattern_atom |
                         pattern_atom bit_field |
                         pattern_atom RANGE [ pattern_atom ]
                         pattern_atom bit_field RANGE [ pattern_atom bit_field]
                       ) [multiple]
        bit_field: ':' NUMBER
        '''
        assert tree[SYMBOL_TYPE] == "range", tree[SYMBOL_TYPE]
        if len(tree) == 2:
            return T3PatternAtom.compile(tree[1])
        else:
            T = tree[2]
            if T[TOKEN_TYPE] == "RANGE":
                left  = T3PatternAtom.compile(tree[1])
                if not isinstance(left, T3PatternNumber):
                    raise TypeError("Lower bound of range object must have type <T3Number>. Found %s"%type(left))
                right = tree[3] if (len(tree)>3 and tree[3][SYMBOL_TYPE] == "atom") else None
                if right:
                    right = T3PatternAtom.compile(right)
                    if not isinstance(right, T3PatternNumber):
                        raise TypeError("Upper bound of range object must have type <T3Number>. Found %s"%type(right))
                P = T3PatternRange(left.number, right.number)
                if tree[-1][SYMBOL_TYPE] == "mult":
                    M = T3PatternMultiple.compile(tree[-1], P)
                    return M
                else:
                    return P
            elif T[SYMBOL_TYPE] == "mult":
                P = T3PatternAtom.compile(tree[1])
                M = T3PatternMultiple.compile(tree[2], P)
                return M
            elif T[SYMBOL_TYPE] == "bitfield":
                N = T3PatternAtom.compile(tree[1])
                if not isinstance(N, T3PatternNumber):
                    raise TypeError("Bit-field must have the form N:bt where N is of type <T3Number>. Found %s"%type(left))
                # since this is a pattern we don't really know at this point how
                B  = tree[2][1]
                n_left  = N.number
                bt_left = int(B[1])
                if bt_left<=0:
                    raise TypeError("Bit index must not be 0 or negative. Index found %d"%bt_left)
                if len(tree) == 3:
                    return T3PatternBitRange(n_left, n_left, bt_left, bt_left)
                elif len(tree) >= 4:
                    if len(tree) == 4:
                        return T3PatternBitRange(n_left, n_left, bt_left, 1)
                    else:
                        N = T3PatternAtom.compile(tree[4])
                        if not isinstance(N, T3PatternNumber):
                            raise TypeError("Bit-field must have the form N:bt where N is of type <T3Number>. Found %s"%type(left))
                        # since this is a pattern we don't really know at this point how
                        B  = tree[5][1]
                        n_right  = N.number
                        bt_right = int(B[1])
                        if bt_right<=0:
                            raise TypeError("Bit index must be >0. Index found %d"%bt_right)
                        upper = bt_left if bt_left>bt_right else bt_right
                        lower = bt_left if upper == bt_right else bt_left
                        if n_left>n_right:
                            raise TypeError("Left range bound must be smaller or equal than right bound. Found left-bound = %s, right-bound = %s"%(n_left, n_right))
                        return T3PatternBitRange(n_left, n_right, bt_left, bt_right)


class T3PatternAtom(T3PatternObject):
    @classmethod
    def compile(cls, tree):
        '''
        pattern_atom: NAME | [NUMBASE] NUMBER | '*' | '?' | '(' pattern_alt ')' [multiple]
        '''
        assert tree[SYMBOL_TYPE] == "atom", tree[SYMBOL_TYPE]
        if len(tree) == 2:
            T = tree[1]
            if T[SYMBOL_TYPE] == "alt":
                return T3PatternAlt.compile(T)
            if T[SYMBOL_TYPE] == "number":
                if len(T) == 3:
                    NUMBASE = T[1]
                    base = NUMBASE[1].replace("'", "").replace('"', '')
                    return T3PatternNumber(T3Number(T[2][1], int(base)))
                else:
                    return T3PatternNumber(Hex(T[1][1], leftpad = True))
            elif T[TOKEN_TYPE] == "NAME":
                frame = sys._getframe()
                R = find_name(T[1], sys._getframe())
                if R is None:
                    raise NameError("name '%s' is not defined"%T[1])
                if isinstance(R, str):
                    return T3Pattern(R)
                elif isinstance(R, T3PatternObject):
                    return R
                elif isinstance(R, T3Number):
                    return T3PatternNumber(T3PatternNumber(R))
                else:
                    raise TypeError("Illegal type %s of %s in pattern expression"%(type(R), T[1]))
            elif T[TOKEN_TYPE] == "STAR":
                return T3PatternVar()
            elif T[TOKEN_TYPE] == "WILDCARD":
                return T3PatternWildcard()
        else:
            P = T3PatternAlt.compile(tree[1])
            M = T3PatternMultiple.compile(tree[2], P)
            return M

class T3PatternMultiple(T3PatternObject):
    def __init__(self, left, right, pattern = None):
        self.left  = left
        self.right = right
        if self.left>self.right:
            self.left, self.right = self.right, self.left
        self.pattern = pattern

    def match(self, data):
        sb = []
        m = T3Match(T3Number.NULL, data)
        k = 0
        pos = -1
        while k<self.right:
            m = self.pattern.match(m.rest)
            if m:
                k+=1
                sb.append(m.value.digits())
            else:
                pos = len(data) - len(m.rest)
                break
        if k>=self.left:
            return T3Match(data.__class__("".join(sb), data.base), m.rest)
        else:
            return T3MatchFail(data, pos)


    @classmethod
    def compile(cls, tree, pattern):
        assert tree[SYMBOL_TYPE] == "mult", tree[SYMBOL_TYPE]
        if isinstance(pattern, T3PatternVar):
            return pattern
        P = T3PatternRange.compile(tree[1])
        if isinstance(P, T3PatternRange):
            if isinstance(P.left, T3PatternNumber):
                if P.right is None:
                    return T3PatternMultiple(P.left.number.number(), sys.maxint, pattern)
                elif isinstance(P.right, T3PatternNumber):
                    return T3PatternMultiple(P.left.number.number(), P.right.number.number(), pattern)
                else:
                    raise TypeError("Upper bound of range object must have type <T3Number>. Found %s"%type(P.right))
            else:
                raise TypeError("Lower bound of range object must have type <T3Number>. Found %s"%type(P.right))
        elif isinstance(P, T3PatternNumber):
            k = P.number.number()
            if isinstance(pattern, T3PatternWildcard):
                return T3PatternWildcard(k)
            else:
                return T3PatternMultiple(P.number.number(), P.number.number(), pattern)
        elif isinstance(P, T3PatternWildcard):
            return T3PatternMultiple(1, 1, pattern)
        elif isinstance(P, T3PatternVar):
            return T3PatternMultiple(0, sys.maxint, pattern)


class T3PatternNumber(T3PatternObject):
    def __init__(self, number):
        self.number = number

    def match(self, data):
        if not isinstance(data, T3Number):
            data = T3Number(data, self.number.base)
        if self.number is T3Number.NULL:
            return T3MatchFail(data, 0)
        else:
            n = len(self.number)
            matches = data[:n]
            if self.number == matches:
                return T3Match(matches, data[n:])
            else:
                return T3MatchFail(data, 0)


class T3PatternVar(T3PatternObject):
    def is_variable(self):
        return True

    def match(self, data):
        if not isinstance(data, T3Number):
            data = T3Number(data)
        return T3Match(data, T3Number.NULL)


class T3PatternWildcard(T3PatternObject):
    def __init__(self, digits = 1):
        self.digits = digits

    def __nonzero__(self):
        return bool(self.digits)

    def match(self, data):
        # print "DATA", data
        if not isinstance(data, T3Number):
            data = T3Number(data, data.base)
        value = data[:self.digits]
        if len(value) == self.digits:
            return T3Match(value, data[self.digits:])
        else:
            return T3MatchFail(data, len(value))


class T3PatternBitRange(T3PatternObject):
    def __init__(self, from_item, to_item, upper_bit, lower_bit):
        self.start  = int((from_item-1)*8 + (8-upper_bit))
        if to_item == from_item:
            self.digits = upper_bit - lower_bit + 1
        else:
            self.digits = int(upper_bit + (to_item-from_item-1)*8 + (8-lower_bit+1))

    def match(self, data):
        if isinstance(data, T3Number):
            bits = T3Number(data, 2)
        else:
            bits = T3Number(Hex(data), 2)
        value = bits[self.start:self.start+self.digits]
        if len(value) == self.digits:
            rest = bits[self.start+self.digits:]
            return T3Match(value, rest if rest is not T3Number.NULL else T3Number.NULL)
        else:
            return T3MatchFail(data, len(value))


class T3PrefixedPattern(T3PatternObject):
    def __init__(self, prefix, pattern):
        self.prefix  = prefix
        self.pattern = pattern

    def match(self, data):
        m = self.prefix.match(data)
        if m:
            return self.pattern.match(data)
        else:
            return m

    def __copy__(self):
        return T3PrefixedPattern(self.prefix, copy(self.pattern))


if __name__ == '__main__':
    print "1:8..1:6", T3Pattern("1:8..1:6").match("FF")
    print "1:5", T3Pattern("1:5").match("FF")
    print "1:4..", T3Pattern("1:4..").match("FF")
    print "2:7..", T3Pattern("2:7..").match("FF 81")
    print "1:8..1:1", T3Pattern("1:8..1:1").match("FF 81")
    print "-"*50
    print "1:8..1:7", T3Pattern("1:8..1:7").match("8C C0")
    print "1:8..2:8", T3Pattern("1:8..2:8").match("FF 81")
    print "1:6..2:7", T3Pattern("1:6..2:7").match("8C C0")
    print "2:6..4:5", T3Pattern("2:6..4:5").match("8C C0 10")
    print T3Pattern("8")
    print T3Pattern("(8)(C|0)").match("8C C0 10")

