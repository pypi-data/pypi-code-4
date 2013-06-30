# -*- coding: iso-8859-1 -*- #
# ======================================================================
#
# Copyright (C) 2013 Kay Schluehr (kay@fiber-space.de)
#
# t3.pattern.py, v B.0 2013/09/03
#
# ======================================================================


import t3
import sys
import collections
import warnings
from copy import copy
from t3.util import load_dynamic
from t3.t3abc import T3Matcher, T3Value
from t3.number import T3Number, Hex, Bin
from t3.pattern import T3Match, T3MatchFail, T3LMatch, MatchingFailure, \
                       T3PrefixedPattern, T3PatternObject, T3PatternWildcard, T3Pattern, \
                       T3PatternSeq, T3PatternBitRange, T3PatternNumber


warnings.simplefilter("once", Warning)

class T3Binding(object):
    def get_value(self):
        return self.callback(self._get_bound_value())

class T3TableBinding(T3Binding):
    def __init__(self, code, callback):
        '''
        code:

            "abc" # alphanumeric - identifier
            "*"   # this table object
            ".*"  # subtable created from rows succeeding this row
            "*."  # subtable created from rows preceeding this row
            "*/"  # parent table object
            "*//" # grandparent table object
            "*/".."/" # n-th grandparent
        '''
        self.mode     = "auto"
        self.callback = callback
        self.code  = code
        self.table = None

    def _get_bound_value(self):
        if self.code.isalnum():
            return getattr(self.table, self.code)
        elif self.code == "*":
            return self.table
        elif self.code == ".*":
            for i, row in enumerate(self.table):
                if row.value_binding == self:
                    table = self.table.__class__()
                    table._parent = self.table._parent
                    table._rows   = self.table._rows[i+1:]
                    table._rownames = {}
                    for row in table._rows:
                        k = table._rownames.get(row.name, 0)
                        table._rownames[row.name] = k+1
                    return table
        elif self.code == "*.":
            for i, row in enumerate(self.table):
                if row.value_binding == self:
                    table = self.table.__class__()
                    table._parent = self.table._parent
                    table._rows   = self.table._rows[:i-1]
                    table._rownames = {}
                    for row in self._rows:
                        k = table._rownames.get(row.name, 0)
                        table._rownames[row.name] = k+1
                    return table
        elif self.code[0] == "*":
            n = self.code.count("/")
            if n == len(self.code)-1:
                P = self.table
                while n:
                    P = P._parent
                    if P is None:
                        return
                    n-=1
                return P
        return ValueError("unknown binding code '%s'"%self.code)


class T3DynamicBinding(T3Binding):
    def __init__(self, name, callback = lambda x: x):
        self.mode = "dynamic"
        self.callback = callback
        self.name = name

    def _get_bound_value(self):
        return load_dynamic(self.name)


class binding(object):
    @classmethod
    def table(cls, *args):
        return T3TableBinding(*args)

    @classmethod
    def dynamic(cls, *args):
        return T3DynamicBinding(*args)

T3Value.register(T3Binding)

class T3Row(object):
    '''
      O                O          M     O              O       O
    .-------------------------------------------------------------------------.
    | PatternBinding | Pattern | Name | ValueBinding | Value | ValueFormatter |
    '-------------------------------------------------------------------------'
    '''
    def __init__(self, PatternBinding = None,
                       Pattern = None,
                       Name = None,
                       ValueBinding = None,
                       Value = T3Number.NULL,
                       ValueFormatter = None):
        self.table   = None
        self.name    = Name
        self.value   = Value
        self.pattern = Pattern
        self.pattern_binding = PatternBinding
        self.value_binding   = ValueBinding
        self.value_formatter = ValueFormatter

    def __copy__(self):
        if isinstance(self.pattern, T3Table) or isinstance(self.pattern, T3PrefixedPattern):
            pattern = copy(self.pattern)
        else:
            pattern = self.pattern
        row = T3Row(self.pattern_binding, pattern, self.name, self.value_binding, self.value, self.value_formatter)
        return row

    def set_table(self, table):
        self.table = table
        if isinstance(self.pattern, T3PrefixedPattern) and not isinstance(table, T3Set):
            self.pattern = T3PrefixedPattern(self.pattern.prefix, table)

    def __nonzero__(self):
        return self.value is not None

    def is_variable(self):
        return self.pattern and self.pattern.is_variable()

    def get_value(self):
        if self.value is not None and self.value is not T3Number.NULL:
            return self.value
        if self.value_binding:
            if self.value_binding.mode == "auto":
                self.value_binding.table = self.table
            value = self.value_binding.get_value()
            if self.table:
                return self.table._coerce(value)
            else:
                return value
        return self.value


    def get_pattern(self, data):
        if self.pattern_binding:
            P = self.pattern_binding(self.table, data)
            if isinstance(P, (T3PatternObject, T3Matcher)):
                return P
            elif isinstance(P, T3Number):
                return T3PatternWildcard(P.number())
            elif isinstance(P, int):
                return T3PatternWildcard(P)
            elif isinstance(P, (str, unicode)):
                return T3Pattern(P)
        else:
            return self.pattern

    def set_formatter(self, value):
        if self.value_formatter and hasattr(value, "formatter"):
            value.formatter = self.value_formatter(value)

    def match(self, data):
        self.pattern = self.get_pattern(data)
        if self.pattern:
            try:
                m = self.pattern.match(data)
            except AttributeError:
                raise
            if m:
                self.value = m.value
                self.set_formatter(self.value)
            else:
                self.value = "???????????"
            return m
        elif isinstance(self.pattern, T3PatternWildcard) and self.pattern.digits == 0:
            self.value = None
            return T3Match(T3Number.NULL, data)
        else:
            raise TypeError("pattern not found in row '%s'"%self.name)

    def find(self, data):
        self.pattern = self.get_pattern(data)
        n = len(data)
        i = 0
        while i<n:
            sub = data[i:]
            m = self.pattern.match(sub)
            if m:
                self.value = m.value
                self.set_formatter(self.value)
                return T3LMatch(m.value, data[:i], m.rest, True)
            i+=1
        self.value = "???????????"
        return T3MatchFail(data, 0)

    def rfind(self, data):
        self.pattern = self.get_pattern(data)
        n = len(data)-1
        while n>=0:
            sub = data[n:]
            m = self.pattern.match(sub)
            if m:
                self.value = m.value
                self.set_formatter(self.value)
                return T3LMatch(m.value, data[:n], m.rest)
            n-=1
        self.value = "???"
        return T3MatchFail(data, 0)

    # The following three methods are defined for convenience. They are used when either a T3Row or a list [T3Row] of
    # T3Row objects is returned. So a T3Row object is equipped with a simple list-like interface.

    def __getitem__(self, i):
        '''
        This method is defined for convenience. It is used when either a T3Row or a list [T3Row] of T3Row objects
        is returned.
        '''
        if i!=0:
            raise IndexError("row index out of range")
        return self

    def __len__(self):
        return 1

    def __iter__(self):
        return (self,).__iter__()

    def __repr__(self):
        return "<t3table.T3Row '%s = %s'>"%(self.name, self.get_value())

T3Value.register(T3Row)

class T3Table(object):
    def __init__(self):
        self._rows       = []
        self._rownames   = {}
        self._parent     = None

    def _coerce(self, rowvalue):
        if isinstance(rowvalue, T3Number):
            return rowvalue
        else:
            return Hex(rowvalue)

    def _get_null_value(self):
        return T3Number.NULL

    def _set_value_and_binding(self, row, v):
        if isinstance(v, T3Binding):
            row.value_binding = v
        elif v is None or isinstance(v, T3Table):
            row.value = v
        elif isinstance(v, T3Row):
            if row.name != v.name:
                raise ValueError("Cannot update row '%s' with row '%s'. Rows must have equal names"%(row.name, v.name))
            if v.pattern_binding:
                row.pattern = None
                row.pattern_binding = v.pattern_binding
            else:
                row.pattern_binding = None
                self._set_pattern_and_binding(row, v.pattern)
            if v.value_binding:
                row.value = self._get_bull_value()
                row.value_binding = v.value_binding
            else:
                row.value_binding = None
                self._set_value_and_binding(row, v.value)
        else:
            row.value = self._coerce(v)
        return row

    def _set_pattern_and_binding(self, row, P):
        if isinstance(P, T3Table):
            row.pattern = P
        elif hasattr(P, "__call__"):
            row.pattern_binding = P
        elif isinstance(P, T3PatternObject):
            row.pattern = P
        elif isinstance(P, T3Number):
            self.pattern = T3PatternWildcard(P.number())
        elif isinstance(P, int):
            row.pattern = T3PatternWildcard(P)
        elif isinstance(P, (str, unicode)):
            row.pattern = T3Pattern(P)
        elif P is None:
            pass
        else:
            raise TypeError("invalid pattern type %s"%type(P))

    def _new_row(self, pattern, field):
        if isinstance(pattern, T3Row):
            return pattern[0]
        else:
            if not field:
                raise TypeError("T3Row:name is mandatory attribute. Cannot construct T3Row")
            keys = field.keys()
            if "__repr__" in keys:
                ValueFormatter = field["__repr__"]
                del field["__repr__"]
            else:
                ValueFormatter = None
            if len(field)>1:
                raise TypeError("Cannot construct T3Row from dictionary %s."%field)
            name, v = field.items()[0]
            row = T3Row(Name = name, ValueFormatter = ValueFormatter)
            row = self._set_value_and_binding(row, v)
            self._set_pattern_and_binding(row, pattern)
            if row.name in T3Table.__dict__ or row.name in self.__dict__:
                raise TypeError("can't add row which has a T3Table attribute name: '%s'"%row.name)
        return row

    def __getitem__(self, name):
        k = self._rownames.get(name, 0)
        if k == 0:
            raise AttributeError("Row with name '%s' not found"%name)
        elif k == 1:
            for row in self._rows:
                if row.name == name:
                    return row
        else:
            return list(row for row in self._rows if row.name == name)

    def __len__(self):
        return len(self._rows)

    def __contains__(self, name):
        return name in self._rownames

    def _get_root(self):
        if self._parent is not None:
            return self._parent._get_root()
        return self

    def _clear(self):
        # Nulls values of TRows with ValueBindings. This causes a re-computation
        # of those values when the T3Table is updated.
        for row in self._rows:
            if isinstance(row.value, T3Table):
                row.value._clear()
            elif row.value_binding:
                if row.value is not None:
                    row.value = self._get_null_value()

    def __call__(self, **fields):
        P = self._get_root()
        memo  = {}
        root  = P._treecopy(memo)
        table = memo[id(self)]
        n = len(fields)
        for name, value in fields.items():
            if name == '__doc__':
                table.__doc__ = value
            elif name not in table._rownames:
                raise TypeError("__call__() got an unexpected keyword argument '%s'"%name)
            else:
                table.__setattr__(name, value)
                if n >= 2:
                    for r in table[name]:
                        if r.value_binding is not None:

                            warnings.warn_explicit("undetermined result. Assigned to value bound row in unspecified order.", UserWarning, "t3.table", lineno = sys._getframe(0).f_lineno)

        return root

    def _treecopy(self, memo):
        table = self.__copy__()
        memo[id(self)] = table
        table.__doc__ = self.__doc__
        for row in table._rows:
            if isinstance(row.value, T3Table):
                c = row.value._treecopy(memo)
                row.value = c
                c._parent = table
        return table

    def __copy__(self):
        table = self.__class__()
        for row in self._rows:
            R = copy(row)
            R.set_table(table)
            table._rows.append(R)
        table._rownames = self._rownames.copy()
        return table

    def __getattr__(self, name):
        row = self.__getitem__(name)
        if len(row) == 1:
            return row.get_value()
        else:
            return [r.get_value() for r in row]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._update(name, value)

    def _update(self, name, value):
        self._get_root()._clear()
        row = self.__getitem__(name)
        if len(row) == 1:
            if isinstance(value, (list, tuple)):
                if len(value) == 1:
                    self._set_value_and_binding(row, value[0])
                else:
                    raise TypeError("cannot unpack value %s"%value)
            elif isinstance(value, T3Row):
                value.name = name
                self._set_value_and_binding(row, value)
                self._set_pattern_and_binding(row, row.pattern)
                value.table = self
            elif isinstance(value, T3Table):
                self._set_value_and_binding(row, value)
                value._parent = self
            else:
                self._set_value_and_binding(row, value)
        elif isinstance(value, (list, tuple)):
            if len(value) == len(row):
                for i, r in enumerate(row):
                    self._set_value_and_binding(r, value[i])
            elif len(value)<len(row):
                if len(value) == 1:
                    raise ValueError("need more than 1 value to unpack. %d expected"%len(row))
                else:
                    raise ValueError("need more than %d values to unpack. %d expected"%(len(value), len(row)))
            else:
                raise ValueError("too many values to unpack. %d expected. %d received."%(len(row), len(value)))
        else:
            raise ValueError("not enough values to unpack. %d expected. %d received."%(len(row), 1))
        # reset computed values
        for row in self._rows:
            if row.name!=name and row.value_binding:
                row.value = self._get_null_value()

    def __iter__(self):
        return self._rows.__iter__()

    def __floordiv__(self, other):
        table = self.__class__()
        S1 = copy(self)
        S2 = copy(other)
        table._rows = S1._rows + S2._rows
        table._rownames = S1._rownames
        for name in S2._rownames:
            if name in table._rownames:
                table._rownames[name] += S2._rownames[name]
            else:
                table._rownames[name] = S2._rownames[name]
        return table

    def _tostring(self, indent = 0):
        S = []
        for row in self._rows:
            value = row.get_value()
            if row.value_binding:
                name = "$"+row.name
            else:
                name = row.name
            if isinstance(value, T3Table):
                S.append(indent*" "+value._to_string_top(name))
                S+=value._tostring(indent+4)
            elif value is not None:
                S.append(indent*" "+name+": " + str(value))
        return S

    def _to_string_top(self, name):
        return name+":"

    def __repr__(self):
        # return object.__repr__(self)
        try:
            for name, value in sys._getframe().f_back.f_locals.items():
                if self == value:
                    break
            else:
                name = ""
        except Exception:
            name = ""
        S = []
        if name:
            S.append(self._to_string_top(name))
            S+=self._tostring(4)
        else:
            if self._parent:
                for row in self._parent._rows:
                    if isinstance(row.value, T3Table) and id(row.value) == id(self):
                        S.append(row.value._to_string_top(row.name))
                        break
                else:
                    S.append(object.__repr__(self))
            else:
                S.append(object.__repr__(self))
            S+=self._tostring(4)
        return "\n".join(S)


    def add(self, pattern = 0, **field):
        row = self._new_row(pattern, field)
        self._rows.append(row)
        k = self._rownames.get(row.name, 0)
        self._rownames[row.name] = k+1
        if isinstance(row.value, T3Table):
            row.value._parent = self
        row.table = self
        return self

    def __lshift__(self, data):
        m = self.match(data)
        if not m:
            raise MatchingFailure(m)
        else:
            return m.value

    def match(self, data):
        data = self._coerce(data)
        table = copy(self)
        rows = [row for row in table._rows if row]
        P = T3PatternSeq(*rows)
        m = P.match(data)
        if m:
            m.value = table
            for row in table._rows:
                if isinstance(row.value, T3Table):
                    row.value._parent = table
        else:
            m.err_object = table
        return m

    def find(self, row_name):
        '''
        Breadth first search for a T3Row with a given ``row_name``.
        '''
        for row in self._rows:
            if row.name == row_name:
                return row.get_value()
        for row in self._rows:
            if isinstance(row.value, T3Table):
                res = row.value.find(row_name)
                if res:
                    return res

    def get_value(self):
        value = []
        for row in self._rows:
            if row:
                v = row.get_value()
                if v is not None:
                    if isinstance(v, T3Value):
                        value.append(v.get_value())
                    else:
                        value.append(v)
        if len(value) == 0:
            return self._get_null_value()
        if len(value) == 1:
            return value[0]
        return reduce(lambda x,y: x // y, value)

    def is_variable(self):
        '''
        Implemented for T3Matcher conformance.
        '''
        return False


T3Matcher.register(T3Table)
T3Value.register(T3Table)


class T3Bitmap(T3Table):
    def __init__(self):
        super(T3Bitmap, self).__init__()
        self._bits = []

    def _coerce(self, rowvalue):
        if isinstance(rowvalue, T3Number):
            return rowvalue
        else:
            return Bin(rowvalue)

    def match(self, data):
        if not (isinstance(data, T3Number) and data.base == 2):
            bits = Bin(data)
            k = len(bits)%8
            if k:
                bits.zfill(len(bits)+8-k)
        else:
            bits = data
        m = super(T3Bitmap, self).match(bits)
        if m.rest and isinstance(data, T3Number):
            if data.base!=2:

                R  = data.__class__(m.rest.bytes(), data.base)
                m.rest = R
        return m

    def add(self, pattern, **field):
        if isinstance(pattern, int):
            k = pattern
        elif isinstance(pattern, (str, unicode)):
            k = int(pattern)
        elif isinstance(pattern, T3Number):
            k = pattern.number()
        else:
            raise TypeError("cannot create bitpattern from object of type %s"%type(pattern))
        if self._bits:
            p = T3PatternWildcard(k)
        else:
            b, r = divmod(k, 8)
            r = 8 - r + 1
            p = T3PatternBitRange(1, 1+b, 8, r)
            self._bits.append(k)
        for key, value in field.items():
            if isinstance(value, (int, T3Number, str, unicode)):
                field[key] = Bin(value)
        row = self._new_row(p, field)
        if row.name in T3Bitmap.__dict__ or row.name in self.__dict__:
            raise TypeError("can't add row which has a T3Bitmap attribute name: '%s'"%row.name)
        row.table = self
        self._rows.append(row)
        k = self._rownames.get(row.name, 0)
        self._rownames[row.name] = k+1
        return self

    def _to_string_top(self, name):
        return name+": %s"%Bin(self)



class T3Set(T3Table):
    def _set_pattern_and_binding(self, row, P = None):
        if isinstance(row.value, T3Matcher) and (isinstance(P, T3Number) or isinstance(P, int)):
            P = Hex(P) if isinstance(P, int) else P
            row.pattern = T3PrefixedPattern(T3PatternNumber(P), row.value)
        else:
            super(T3Set, self)._set_pattern_and_binding(row, P)

    def match(self, data):
        data = self._coerce(data)
        m = T3Match(T3Number.NULL, data)
        rows  = [copy(row) for row in self._rows if row]
        table = self.__class__()
        while rows:
            data = m.rest
            for i, row in enumerate(rows):
                try:
                    m = row.match(data)
                except MatchingFailure, f:
                    pass
                if m:
                    break
            else:
                raise MatchingFailure(m)
            table.add(rows[i])
            del rows[i]
            if not m.rest:   # completed
                break
        if m:
            m.value = table
            return m
        else:
            raise MatchingFailure(m)

class T3Repeater(object):
    def __init__(self, table, minimum = 1, maximum = sys.maxint):
        self.table = table
        self._min  = minimum
        self._max  = maximum

    def match(self, data):
        data = self.table._coerce(data)
        m = T3Match(T3Number.NULL, data)
        table = self.table.__class__()
        i = 0
        while i<self._max:
            R = m.rest
            m = self.table.match(R)
            if isinstance(m, T3MatchFail):
                if i<self._min:
                    return m
                else:
                    return T3Match(table, R)
            else:
                table = table // m.value
            i+=1
        return T3Match(table, R)

    def __lshift__(self, data):
        m = self.match(data)
        if not m:
            raise MatchingFailure(m)
        else:
            return m.value


class T3TableContext(T3Table):
    def __init__(self):
        super(T3Response, self).__init__()
        self._status = "OK"

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        if typ:
            if typ in (AssertionError, MatchingFailure):
                self._status = "FAIL"
                self.fail_message(value)
            else:
                self._status = "ERROR"
                self.error_message(value)

        else:
            self.ok_message(value)

    def fail_message(self, value):
        traceback.print_exc()

    def error_message(self, value):
        traceback.print_exc()

    def ok_message(self, value):
        pass





if __name__ == '__main__':

    K = 42
    B = binding.dynamic("K")
    def foo(binding):
        K = -42
        return binding.get_value()
    assert foo(B) == -42

    def test_tlv():
        print "call: test_tlv()"

        def BERLen(v):
            # v = binding.bound_value()
            if v is not None:
                try:
                    n = len(v.get_value())
                except AttributeError:
                    n = len(v)
                k = Hex(n)
                if len(k) == 1:
                    if k>=0x80:
                        return 0x81 // k
                    else:
                        return k
                else:
                    return (0x80 | len(k)) // k

        def tag_size(tlv, data):
            if data[0] & 0x1F == 0x1F:
                return 2
            else:
                return 1

        def len_size(tlv, data):
            if data[0] & 0x80 == 0x80:
                lenlen = data[0] & 0x0F
                return 1+lenlen
            return 1

        def value_size(tlv, data):
            if isinstance(tlv.Value, T3Matcher):
                return tlv.Value
            if tlv.Len & 0x80 == 0x80:
                return tlv.Len[1:].number()
            else:
                return tlv.Len.number()

        Tlv = T3Table()
        Tlv.__doc__ = "TLV data structure"

        Tlv.add(tag_size, Tag = "A5")
        Tlv.add(len_size, Len = binding.table(".*", BERLen))
        Tlv.add(value_size, Value = "89 89")

        Tlv << "A7 02 03 05 06"
        assert Tlv.get_value() == "A5 02 89 89"
        assert Hex(Tlv) == "A5 02 89 89"
        assert Tlv.Len == 2
        assert Tlv.Value == "89 89"
        Tlv.Value = "00"*0x80
        # print len(Tlv._rows[2].table._rows)
        Tlv << "A7 02 03 05 06"
        assert Tlv.Len == "81 80"

        Tlv2 = copy(Tlv)
        Tlv2.Value = "00"
        assert Tlv2.Len == 1

        Tlv3 = Tlv2(Tag = "A6")
        assert Tlv3.Tag == 0xA6

        try:
            Tlv3.add(1, _rows = 0)
            assert False, "TypeError exception not raised"
        except TypeError:
            pass

        Tlv2.Value = Tlv3
        assert Hex(Tlv2.Value(Value = "89 AF")) == 'A5 04 A6 02 89 AF'

        TlArray = T3Table()
        TlArray.add(Tag = 0x9A)
        TlArray.add(Len = 0x04)
        TlArray.add(Tag = 0x5F0A)
        TlArray.add(Len = 0x02)
        TlArray.add(Tag = 0x8A)
        TlArray.add(Len = 0x08)

        assert len(TlArray["Len"]) == 3
        assert TlArray.Len == [0x04, 0x02, 0x08]
        assert len(TlArray["Tag"]) == 3
        assert TlArray.Tag == [0x9A, 0x5F0A, 0x8A]

        dol = TlArray(Tag = [0x95, 0x5F0A, 0x8A])

        assert len(zip(dol.Tag, dol.Len)) == 3

        Tlv4 = Tlv << "A7 02 03 05 06"

        assert Tlv4.Tag  == "A7"
        assert Tlv4.Len  == "02"
        assert Tlv4.Value == "03 05"

        Tlv4.Value = "03 05 06"
        assert Tlv4.Len == "03"
        Tlv4.Value = "03 05 06 07"
        assert Tlv4.Len == "04"

        Tlv5 = Tlv4(Len = T3Row(Pattern = '05', Value = 0x05))
        assert (Tlv5 << 'A0 05 01 02 03 04 05').Len == '05'

        try:
            print Tlv5 << "A7 04 01 02 03 04"
            assert False, "MatchingFailure exception not raised"
        except MatchingFailure:
            pass

        A = T3Table()
        A.add(B = 0x00)
        A.add(C = 0x01)
        A.C = A()
        assert Hex(A.C(B = 0x78)) == '00 78 01'

        assert copy(A.C).B == 0x00
        assert copy(A.C).C == 0x01

        RApdu = T3Table()
        RApdu.add("*", Data = '00')
        RApdu.add(1, Le = None)
        RApdu.add(2, SW = '00 00')

        Tlv.Value = "00 00 00"

        r = RApdu << '00 01 02 00 67 90 00'
        assert r.SW == 0x9000
        assert r.Data == '00 01 02 00 67'

        T1 = Tlv(Tag = 0x78)
        T2 = Tlv(Tag = 0xA6)
        ts = T3Set()
        ts.add(0x78, T1 = T1)
        ts.add(0xA6, T2 = T1)
        tree = ts << '78 01 06 A6 03 01 02 04'
        assert tree.T1.Tag == '78'
        assert tree.T2.Tag == 'A6'
        assert Hex(tree.T1(Value = 0x07)) == '78 01 07 A6 03 01 02 04'
        tree = ts << 'A6 03 01 02 04 78 01 06'
        assert Hex(tree) ==  'A6 03 01 02 04 78 01 06'
        tree.T1.Value = '05 06'
        assert Hex(tree) == 'A6 03 01 02 04 78 02 05 06'

        X1 = T3Set()
        X1.add(0x78, F_87 = Tlv(Tag = 0x78))
        X1.add(0xA6, F_A6 = Tlv(Tag = 0xA6, Value = 'AA'))

        X = X1()
        H = Hex(X)
        X << H

        X2 = T3Set()
        X2.add(0x9F01, F_9F01 = Tlv(Tag = 0x9F01))
        X2.add(0x9F02, F_9F02 = Tlv(Tag = 0x9F02))
        X2.add(0x9F03, F_9F03 = Tlv(Tag = 0x9F03))

        Y1 = Tlv(Tag = 0x8C, Value = X1)
        Y2 = Tlv(Tag = 0x8D, Value = X2)

        Y = T3Set()
        Y.add(0x8C, F_8C = Y1)
        Y.add(0x8D, F_8D = Y2)

        T = T3Set()
        T.add(0xA5, Value = Tlv(Tag = 0xA5, Value = Y))

        F_8C = T.find("F_8C")
        n = F_8C.Len
        F_A6 = T.find("F_A6")
        assert len(F_A6.Value) == 1
        F_A6.Value = "01 02 03 04"
        assert F_8C.Len == n + 3

        R = F_A6(Value = "01 02 03 04 05")
        assert F_8C.Len == n + 3
        assert R.find("F_8C").Len == n + 4
        F_A6.Value = "01"

        R = T << Hex(T)
        assert Hex(T) == Hex(R)

        R2 = R()
        R3 = R2 << Hex(R2)
        assert Hex(R2) == Hex(R3)

        F_8C = R.find("F_8C")
        n = F_8C.Len
        F_A6 = R.find("F_A6")
        assert len(F_A6.Value) == 1
        F_A6.Value = "01 02 03 04"
        assert F_8C.Len == n + 3

        R = F_A6(Value = "01 02 03 04 05")
        assert F_8C.Len == n + 3
        assert R.find("F_8C").Len == n + 4

        R = T << 'A5 1F 8C 09 A6 02 00 00 78 03 00 00 01 8D 12 9F 01 03 00 00 00 9F 02 03 00 00 00 9F 03 03 00 00 00'

        assert Hex(R.find("F_8C")) == "8C 09 A6 02 00 00 78 03 00 00 01"
        assert Hex(R.find("F_8C").find("F_A6")) == "A6 02 00 00"
        assert Hex(R.find("F_8C").find("F_87")) == "78 03 00 00 01"

        R.find("F_8C").find("F_87").Value = "00 00 01 02"

        assert Hex(R.find("F_8C")) == "8C 0A A6 02 00 00 78 04 00 00 01 02"
        #print T3Number(0x8CC010,2)
        btmp = T3Bitmap()
        btmp.add(2, A = 1)
        btmp.add(6, B = 1)
        R = btmp << 0x8CC010
        assert R.A == 2
        assert R.B == 0xC
        btmp = btmp(B = T3Row(Pattern = 8))
        R = btmp << 0x8CC010
        assert R.A == 2
        assert R.B == 0x33
        btmp = btmp(B = T3Row(Pattern = 15))
        R = btmp << 0x8CC010
        assert R.A == 2
        assert R.B == Hex('19 80')
        btmp = T3Bitmap()
        btmp.add(6, A = 1)
        btmp.add(15, B = 1)
        btmp.add(3, C = 1)
        R = btmp << 0x8CC011
        assert R.A == 0x23
        assert R.B == 0x1802
        assert R.C == 1
        T = T3Table()
        T.add(T3Bitmap().add(5, f1 = 0)
                        .add(3, f2 = 0)
                        .add(4, f3 = 0)
                        .add(4, f4 = 0),
              A = 0
        )
        T.add(T3Bitmap().add(2, f1 = 0)
                        .add(5, f2 = 0),
              B = 0
        )

        B = T << Bin('111 1000 0100 0101 0011 0100')
        assert B.A.f1 == 0x1E, B.A.f1

        B = T << '78 45 34'
        assert B.A.f1 == 0x0F, B.A.f1
        T.add(1, C = 0)
        B = T << '78 45 34 78'
        # print B

        T = Tlv(Tag = 0x78, Value = 0x65) // Tlv(Tag = 0xA6, Value = 0x62)
        T["Value"][0].value = Hex('42 54 22 62')
        assert Hex(T) == '78 04 42 54 22 62 A6 01 62', Hex(T)


    def test_atr():
        print "call: test_atr()"
        def get_frequency(value):
            "FI     Value F     f max [MHz]"
            S ='''
            0000    372         4
            0001    372         5
            0010    558         6
            0011    744         8
            0100    1116        12
            0101    1488        16
            0110    1860        20
            0111    RFU         RFU
            1000    RFU         RFU
            1001    512         5
            1010    768         7.5
            1011    1024        10
            1100    1536        15
            1101    2048        20
            1110    RFU         RFU
            1111    RFU         RFU
            '''.split("\n")
            for s in S:
                s = s.strip()
                if s:
                    code, Value_F, frequency = [r.strip() for r in s.split(" ") if r.strip()]
                    if Bin(code) == value:
                        return (Value_F, frequency)

        def format_FI(value):
            value_formatter = value.formatter
            def formatter():
                Value_F, frequency = get_frequency(value)
                return value_formatter() + "  ==> Fi: %s; f max [MHz]: %s"%(Value_F, frequency)
            return formatter

        def format_DI(value):
            value_formatter = value.formatter

            S = '''
            0000    RFU
            0001    1
            0010    2
            0011    4
            0100    8
            0101    16
            0110    32
            0111    RFU
            1000    12
            1001    20
            1010    RFU
            1011    RFU
            1100    RFU
            1101    RFU
            1110    RFU
            1111    RFU
            '''.split("\n")
            def formatter():

                for s in S:
                    s = s.strip()
                    if s:
                        code, D = [r.strip() for r in s.split(" ") if r.strip()]
                        if Bin(code) == value:
                            return value_formatter()+ "  ==> D: %s"%(D,)
            return formatter

        def format_Protocol(value):
            value_formatter = value.formatter
            def formatter():
                n = T3Number(value, 10).number()
                if n in (0,1,14):
                    return value_formatter()+ "  ==> T = %s"%n
                else:
                    return value_formatter()+ "  ==> RFU"
            return formatter


        def interface_char_size(field, bit):

            def compute_len(atr, data):
                try:
                    B = getattr(atr, field)
                    if B is not None:
                        mask = 1<<(bit-1)
                        if Hex(B) & mask == mask:
                            if bit == 8:
                                n = int(field[-1])+2
                                fields = [{"TD%s_used"%n: 0},
                                          {"TC%s_used"%n: 0},
                                          {"TB%s_used"%n: 0},
                                          {"TA%s_used"%n: 0}]
                                return (T3Bitmap().add(1, **fields[0])
                                                  .add(1, **fields[1])
                                                  .add(1, **fields[2])
                                                  .add(1, **fields[3])
                                                  .add(4, Protocol = 0, __repr__ = format_Protocol))
                            elif (field, bit) == ("T0", 5):
                                return T3Bitmap().add(4, FI = 0, __repr__ = format_FI).add(4, DI = 0, __repr__ = format_DI)
                            return 1
                        else:
                            return 0
                    return 0
                except AttributeError:
                    return 0

            return compute_len

        def historicals(atr, data):
            return atr.T0.nbr_of_historicals

        def tck(atr, data):
            if data:
                return 1
            else:
                return 0


        ATR = T3Table()
        ATR.add('3B|3F', TS = '3B')
        ATR.add(T3Bitmap().add(1, TD1_used = 0)
                          .add(1, TC1_used = 0)
                          .add(1, TB1_used = 0)
                          .add(1, TA1_used = 0)
                          .add(4, nbr_of_historicals = 0),
                T0 = 0)
        ATR.add(interface_char_size("T0", 5), TA1 = '00')
        ATR.add(interface_char_size("T0", 6), TB1 = '00')
        ATR.add(interface_char_size("T0", 7), TC1 = '00')
        ATR.add(interface_char_size("T0", 8), TD1 = '00')

        ATR.add(interface_char_size("TD1", 5), TA2 = '00')
        ATR.add(interface_char_size("TD1", 6), TB2 = '00')
        ATR.add(interface_char_size("TD1", 7), TC2 = '00')
        ATR.add(interface_char_size("TD1", 8), TD2 = '00')

        ATR.add(interface_char_size("TD2", 5), TA3 = '00')
        ATR.add(interface_char_size("TD2", 6), TB3 = '00')
        ATR.add(interface_char_size("TD2", 7), TC3 = '00')
        ATR.add(interface_char_size("TD2", 8), TD3 = '00')

        ATR.add(interface_char_size("TD3", 5), TA4 = '00')
        ATR.add(interface_char_size("TD3", 6), TB4 = '00')
        ATR.add(interface_char_size("TD3", 7), TC4 = '00')
        ATR.add(interface_char_size("TD3", 8), TD4 = '00')

        ATR.add(historicals, HistoricalCharacters = '00 00 00 00')
        ATR.add(tck, TCK = '00')

        atr = ATR << '3B FF 18 00 FF 81 31 FE 45 65 63 11 05 40 02 50 00 10 55 10 03 03 05 00 43'
        assert atr.TS == 0x3B
        assert atr.TD1.TD2_used == 1
        atr2 = atr.TD1(TD2_used = 0)
        assert atr2.TD1.TD2_used == 0
        #print atr2
        assert Hex(atr) == '3B FF 18 00 FF 81 31 FE 45 65 63 11 05 40 02 50 00 10 55 10 03 03 05 00 43'
        try:
            ATR << '3E FF 18 00 FF 81 31 FE 45 65 63 11 05 40 02 50 00 10 55 10 03 03 05 00 43'
            assert False, "MatchingFailure exception not raised"
        except MatchingFailure:
            pass


    def test_apdu():
        print "call: test_apdu()"
        def data_len(Data):
            n = len(Data)
            if n<=0xFF:
                return Hex(n)
            else:
                raise ValueError("Data length must be <= 0xFF")

        Apdu = T3Table()
        Apdu.add(1, Cla  = 0x00)
        Apdu.add(1, Ins  = 0xA4)
        Apdu.add(1, P1   = 0x00)
        Apdu.add(1, P2   = 0x00)
        Apdu.add(1, Lc   = binding.table("Data", data_len))
        Apdu.add("*", Data = 0x00)

        Apdu.Data = "3F 00"
        assert Apdu.Lc == 2
        Apdu.Data = "3F 00 DF 01 EF 01"
        assert Apdu.Lc == 6
        assert Hex(Apdu) == "00 A4 00 00 06 3F 00 DF 01 EF 01"

        Select_MF = Apdu << '00 A4 00 00 02 3F 00 00 00 00'
        assert Select_MF.Lc == 2
        Select_MF.Data = '90 89 78'
        assert Select_MF.Lc == 3
        Select_MF = Apdu << '00 A4 00 00 02 3F 00 00 00 00'
        Select_MF.P1 = 0x01
        assert Select_MF.Lc == 5
        assert Select_MF.Data == '3F 00 00 00 00'

        def data_size(table, data):
            return table.Lc.number()

        Apdu = T3Table()
        Apdu.add(1, Cla  = 0x00)
        Apdu.add(1, Ins  = 0xA4)
        Apdu.add(1, P1   = 0x00)
        Apdu.add(1, P2   = 0x00)
        Apdu.add(1, Lc   = binding.table("Data", data_len))
        Apdu.add(data_size, Data = 0x00)
        Apdu.__doc__ = "APDU"
        Select_MF = Apdu << '00 A4 00 00 02 3F 00 00 00 00'
        assert Select_MF.Data == '3F00'

        Select = Apdu()
        assert Select.__doc__ == "APDU"
        Select = Apdu(__doc__ = "SELECT")
        assert Select.__doc__ == "SELECT"

    def test_empty_match():
        print "call: test_empty_match()"
        t = T3Table().add(r = 0).add(s = 0)
        assert isinstance(t.match("89 67"), T3MatchFail)
        try:
            t << "89 67"
            assert 1 == 0
        except MatchingFailure:
            pass

    def test_dynamic_binding():
        K = 0
        T = T3Table()
        T.add(S = binding.dynamic("K"))
        T.add(R1 = '90')
        T.add(R2 = '91')
        assert Hex(T) == '00 90 91'
        K = 1
        assert Hex(T) == '01 90 91'
        T2 = T3Table()
        T2.add(R = '12')
        T2.add(S = binding.dynamic("T", lambda T: T.S // T.R1))
        assert Hex(T2) == '12 01 90'
        K = 2
        assert Hex(T2) == '12 02 90'

        def check_dynamic(table):
            K = 3
            assert table.S == '03'

        check_dynamic(T)

        assert T.S == '02'

        B = binding.dynamic("K")
        assert B.get_value() == 2
        def foo(binding):
            K = 7
            return binding.get_value()
        assert foo(B) == 7
        assert B.get_value() == 2

    def test_repeater():
        t = T3Table().add(
                (T3Table().add(1, s = 0)
                          .add(1, r = 0)),
                u = 0)
        tr = T3Repeater(t, 2, 4)
        v = tr << "01 02 03 04"
        assert len(v["u"]) == 2
        v = tr << "01 02 03 04 05 06"
        assert len(v["u"]) == 3
        v = tr << "01 02 03 04 05 06 07 08"
        assert len(v["u"]) == 4
        v = tr << "01 02 03 04 05 06 07 08 09 0A"
        assert len(v["u"]) == 4
        tr = T3Repeater(t, 3, 4)
        #v = tr << "01 02 03 04"




    test_tlv()
    test_atr()
    test_apdu()
    test_empty_match()
    test_dynamic_binding()
    test_repeater()


    t = T3Table().add(T3Table().add(1, s = 0).add(1, r = 0), u = 0)

    tr = T3Repeater(t, 2, 4)
    v = tr << "27 82 72 87 28 72 67 88 00 70"
    #print v

    Array = T3Table()
    Array.add(1, Length = binding.table("Data", len))
    Array.add("*", Data = '00')

    Array(Length = '03', Data = '00')



