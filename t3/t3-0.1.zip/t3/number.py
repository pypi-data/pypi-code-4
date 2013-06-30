# ======================================================================
#
# Copyright (C) 2013 Kay Schluehr (kay@fiber-space.de)
#
# t3number.py, v B.0 2013/09/03
#
# ======================================================================

__all__ = ["T3Number", "default_formatter", "Hex", "Bin", "Bcd"]

from array import array
from t3.t3abc import T3Value

DIGIT = "0123456789ABCDEF"
DIGITS_PER_BYTE = "xx864443333333332"

def log2base(n):
    r = 0
    while True:
        n = n>>1
        if n == 0:
            break
        r+=1
    return r

def default_formatter(tabular = False):

    block = {}

    for n in range(2, 16):
        block[n] = len(T3Number(256, n).digits())

    def split_to_blocks(s, block_size, front = True):
        n = len(s)
        blocks = []
        if front:
            i = n % block_size
            if i:
                blocks.append(s[:i])
        else:
            i = 0
        while i<n:
            blocks.append(s[i:i+block_size])
            i+=block_size
        return blocks

    def hex_formatter(number):
        lines = []
        if tabular:
            for line in split_to_blocks(split_to_blocks(number.digits(), 2), 16, front = False):
                lines.append(" ".join(line))
            n = len(number.digits())
            if n<256:
                k = 3
            else:
                k = 4
            L = []
            h = 0x10
            for i, line in enumerate(lines):
                pre = " "*4
                L.append(pre+line)
            return "\n".join(L)
        else:
            return " ".join(split_to_blocks(number.digits(), 2))

    def bcd_formatter(number):
        return "bcd'"+" ".join(split_to_blocks(number.digits(), 2))

    def bin_formatter(number):
        lines = []
        k = len(number.digits())%8
        digits = number.digits()
        for line in split_to_blocks(split_to_blocks(digits, 8), 8):
            lines.append(" ".join(line))
        return "\n".join(lines) + " (h'%s)"%(Hex(int(number)),)

    def dez_formatter(number):
        s = number.digits()
        if len(s)<4:
            return s
        k = len(s)%3
        if k:
            return s[:k]+"."+'.'.join(split_to_blocks(number.digits()[:-k], 3))
        else:
            return '.'.join(split_to_blocks(number.digits(), 3))

    def num_formatter(number):
        d = block[number.base-1]
        s = number.digits()
        if len(s)<d:
            return s
        k = len(s)%3
        return number._num_prefix()+''.join(split_to_blocks(number.digits(), d))


    def format(number):
        sign  = "-" if int(number)<0 else ""
        if isinstance(number, Hex):
            n = hex_formatter(number)
        elif isinstance(number, Bin) or number.base == 2:
            n = bin_formatter(number)
        elif isinstance(number, Bcd):
            n = bcd_formatter(number)
        else:
            n = num_formatter(number)
        return sign+n

    return format


class T3Number(object):
    '''
    A T3Number is a triple (N, S, b) consisting of

        * an integer N
        * a numeral string S
        * the numeral base b of S or the radix

    S is a numeral representation of N. A T3Number is a *hybrid type* which means that it acts like
    an
    '''
    _convertible_types = (int, long, str, unicode, array)
    formatter = None

    def __init__(self, data, base = 16):
        if 2<=base<=16:
            self.base = base
        else:
            ValueError("base must be in {2..16}. base value '%s' was found"%base)
        self._str = ''
        self._int = -1

        if data is not None:
            if isinstance(data, T3Value):
                data = data.get_value()
            if isinstance(data, T3Number):
                self._from_t3number(data, base)
                self._preserve_leading_zeros(data, base)
            elif isinstance(data, (str, unicode)):
                self._from_string(data, base)
            elif isinstance(data, (int, long)):
                self._from_integer(data, base)
            elif isinstance(data, array):
                self._from_array(data, base)
            else:
                raise TypeError("illegal argument type %s"%type(data))

    def _preserve_leading_zeros(self, data, base):
        '''
        This function is used preserve leading zeros of a number represented in base B1 when converted into base B2.
        '''
        if data.base == base:
            return
        k = 0
        for c in data._str:
            if c == '0':
                k+=1
            else:
                break
        K2 = int(DIGITS_PER_BYTE[data.base])
        if k>=K2:
            K1 = int(DIGITS_PER_BYTE[base])
            if self._int == 0:
                self._str = "0"*(k*K1/K2)
            else:
                self._str = "0"*(k*K1/K2)+self._str

    def set_formatter(self, formatter):
        self.formatter = formatter

    def _num_prefix(self):
        return str(self.base)+"'"

    def _from_t3number(self, N, base):
        if base == N.base:
            self._str = N._str
            self._int = N._int
        else:
            self._from_integer(N._int, base)

    def _from_string(self, S, base):
        digits = []
        S = repr(S).replace("\\x", "").upper()
        begin = ''
        for i, c in enumerate(S):
            if c in ("'", '"'):
                if i:
                    S = S[i:]
                break
        for c in S:
            if begin:
                if c == '}':
                    begin = ''
                else:
                    digits.append(str(self.__class__(ord(c), base)))
            elif c in DIGIT:
                digits.append(c)
            elif c == '{':
                begin = c
        if begin:
            raise ValueError("Missing terminating brace '}'")
        self._str = ''.join(digits)
        self._int = int(self._str, base)

    def _from_integer(self, n, base):
        self._int = n
        if n == 0:
            self._str = "0"
        else:
            digits = []
            if n<0:
                n = -n
            while n>0:
                n, r = divmod(n, base)
                digits.append(DIGIT[r])
            self._str = "".join(digits[::-1])

    def _from_array(self, a, base):
        if a.typecode == 'b':
            bytes = [(x+256 if x<0 else x) for x in a]
        elif a.typecode == 'B':
            bytes = a.tolist()
        else:
            raise TypeError("typecode of array must be 'b' or 'H'")
        S = []
        for b in bytes:
            if 0<=b<16:
                S.append("0"+DIGIT[b])
            else:
                S.append(hex(b)[2:])
        n = T3Number(''.join(S), 16)
        self._int = n._int
        if base == 16:
            self._str = n._str
        else:
            n._str = T3Number(n._int, base)._str

    def _maxfill(self, other):
        if other.base == self.base:
            return self.base, max(len(self._str), len(other._str)), self.__class__
        if other.base>self.base:
            return other.base, len(other._str), other.__class__
        elif self.base>other.base:
            return self.base, len(self._str), self.__class__

    def _bits_per_item(self):
        return log2base(self.base)

    def __hash__(self):
        return hash(self._int)

    def __len__(self):
        return len(self._str)

    def concat(self, other):
        return self.__floordiv__(other)

    def __floordiv__(self, other):
        '''
        Concatenation operator
        '''
        if isinstance(other, T3Number):
            if other is T3Number.NULL:
                return self
            if self is T3Number.NULL:
                return other
            elif other.base == self.base:
                return self.__class__(self._str + other._str, self.base)
            elif other.base < self.base:
                n = T3Number(self._int, other.base)
                return self.__class__(int(n._str + other._str, other.base), self.base)
            else:
                n = T3Number(other._int, self.base)
                return self.__class__(int(self._str + n._str, self.base), other.base)
        else:
            return self.__floordiv__(T3Number(other, self.base))

    def __rfloordiv__(self, other):
        return self.__class__(other, self.base).__floordiv__(self)

    def __nonzero__(self):
        return self._int != 0

    def __radd__(self, other):
        return self.__class__(other, self.base).__add__(self)

    def __add__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int + other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__add__(T3Number(other, self.base))

    def __rmul__(self, other):
        return self.__class__(other, self.base).__mul__(self)


    def __mul__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int * other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__mul__(T3Number(other, self.base))

    def __rsub__(self, other):
        return self.__class__(other, self.base).__sub__(self)


    def __sub__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int - other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__sub__(T3Number(other, self.base))

    def __rmod__(self, other):
        return self.__class__(other, self.base).__mod__(self)

    def __mod__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int % other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__mod__(T3Number(other, self.base))

    def __rrshift__(self, other):
        return self.__class__(other, self.base).__rshift__(self)

    def __rshift__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int >> other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__rshift__(T3Number(other, self.base))

    def __rlshift__(self, other):
        return self.__class__(other, self.base).__lshift__(self)

    def __lshift__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int << other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__lshift__(T3Number(other, self.base))

    def __rdiv__(self, other):
        return self.__class__(other, self.base).__div__(self)

    def __div__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int / other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__div__(T3Number(other, self.base))

    def __ror__(self, other):
        return self.__class__(other, self.base).__or__(self)

    def __or__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int | other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__or__(T3Number(other, self.base))

    def __rand__(self, other):
        return self.__class__(other, self.base).__and__(self)

    def __and__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int & other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__and__(T3Number(other, self.base))

    def __rxor__(self, other):
        return self.__class__(other, self.base).__xor__(self)

    def __xor__(self, other):
        if isinstance(other, T3Number):
            base, fill, cls = self._maxfill(other)
            n = cls(self._int ^ other._int, base)
            n.zfill(fill)
            return n
        else:
            return self.__xor__(T3Number(other, self.base))

    def __eq__ (self, other):
        if isinstance(other, T3Number):
            return self._int == other._int
        elif isinstance(other, self._convertible_types):
            return T3Number(other, self.base).__eq__(self)
        return False

    def __ne__ (self, hNbr):
        return not self.__eq__(hNbr)

    def __lt__(self, other):
        if isinstance(other, T3Number):
            return self._int < other._int
        elif isinstance(other, self._convertible_types):
            return self.__lt__((other, self.base))
        return False

    def __gt__(self, other):
        if isinstance(other, T3Number):
            return self._int > other._int
        elif isinstance(other, self._convertible_types):
            return self.__gt__(self.__class__(other, self.base))
        return False

    def __le__(self, other):
        if isinstance(other, T3Number):
            return self._int <= other._int
        elif isinstance(other, self._convertible_types):
            return self.__le__(T3Number(other, self.base))
        return False


    def __ge__(self, other):
        if isinstance(other, T3Number):
            return self._int >= other._int
        elif isinstance(other, self._convertible_types):
            return self.__ge__(T3Number(other, self.base))
        return False

    def __invert__(self):
        return self.__class__(self.__class__(DIGIT[self.base - 1]*len(self._str), self.base)._int - self._int, self.base)

    def __index__(self):
        return self._int

    def __int__(self):
        return self._int

    def __getitem__(self, i):
        if self.base == 1:
            return self
        s = self._str[i]
        if s:
            return self.__class__(self._str[i], self.base)
        else:
            return T3Number.NULL

    def number(self):
        return self._int

    def digits(self):
        return self._str

    def bytes(self):
        _bytes = []
        n = self._int
        while n>0:
            n, r = divmod(n, 256)
            _bytes.append(r if r<0x80 else r - 0x100)
        k = 0
        for c in self._str:
            if c == '0':
                k+=1
            else:
                break
        m, r = divmod(k, int(DIGITS_PER_BYTE[self.base]))
        if m:
            _bytes+=[0]*m
        return array('b', _bytes[::-1])

    def zfill(self, width):
        """
        Pad a numeric string S with zeros on the left, to fill a field of the specified width.
        """
        self._str = self._str.zfill(width)

    def __iter__(self):
        for c in self._str:
            yield T3Number(c, self.base)

    def find(self, sub, start = 0, end = None):
        if end:
            s = self._str[start:end]
        else:
            s = self._str[start:]
        sub = T3Number(sub, self.base)
        return s.find(sub._str)

    def split(self, size = 1):
        chunks = []
        n = len(self)
        i = 0
        while i<n:
            chunks.append(self[i:i+size])
            i+=size
        return chunks

    @classmethod
    def join(cls, *args):
        numbers = [cls(arg) for arg in args]
        if len(numbers) == 1:
            return numbers[0]
        else:
            return reduce(lambda x, y: x//y, numbers)


    def _getsubst(this):

        class T3NumberSubst:
            def __init__(self):
                self.digits = None
                self.bits = None

            def __getitem__(self, i):
                if self.digits is not None:
                    self.bits = i
                    return self.__call__
                else:
                    self.digits = i
                    return self

            def __call__(self, value):
                if self.digits is None:
                    if hasattr(value, "__call__"):
                        return value(this)
                    else:
                        return this.__class__(value, this.base)
                else:
                    if isinstance(self.digits, slice):
                        a = self.digits.start
                        b = self.digits.stop
                        s = self.digits.step
                        n0, n1, n2 = this[:a], this[self.digits], this[b:]
                    else:
                        n0, n1, n2 = this[:self.digits], this[self.digits], this[self.digits+1:]

                    if self.bits is not None:
                        v     = T3Number(value, 16).number()
                        B     = this._bits_per_item()
                        b_n1  = T3Number(n1, 2)
                        b_n1.zfill(B)
                        if isinstance(self.bits, slice):
                            a = self.bits.start
                            b = self.bits.stop
                            if a<1 or a>B:
                                raise IndexError("Bit index '%d' used. Bit index must be in 1..%d"%(a, B))
                            if b<1 or b>B:
                                raise IndexError("Bit index '%d' used. Bit index must be in 1..%d"%(b, B))
                            a = B - a
                            b = B - b
                            v = T3Number(v & ((2<<abs(b-a))-1), 2).digits()
                        else:
                            a = self.bits
                            if a<1 or a>B:
                                raise IndexError("Bit index '%d' used. Bit index must be in 1..%d"%(a, B))
                            a = b = B - a
                            v = T3Number(v & 1).digits()
                        s = b_n1._str[:a] + v + b_n1._str[b+1:]
                        return n0 // T3Number(T3Number(s, 2), this.base) // n2
                    else:
                        if hasattr(value, "__call__"):
                            return n0 // value(n1) // n2
                        else:
                            return n0 // this.__class__(value, this.base) // n2
        return T3NumberSubst()


    subst = property(_getsubst, None, None,
                        """
subst[i](value)      -> T3Number
subst[i:j](value)    -> T3Number
subst[i][k](value)   -> T3Number
subst[i][k:m](value) -> T3Number

    subst() sets or resets digits of bits in a T3Number and returns a new T3Number
    where those changes have been applied.

    subst() allows single or double subscripting using either indices or slices to access a
    part of the T3Number which shall be changed, then it replaces this part using the
    value argument.

    The value argument is allowed to be a function of one argument returning a number
    which will then substitute the selected part. The selected part is the value of
    the argument passed to the function.


    Examples:

        >>> N = T3Number("56789", 16)
        >>> N.subst[1](0)               # substitute digit 1 of N with 0
        50789
        >>> N.subst[1:3](0)             # shrinks number
        5089
        >>> N.subst[1][3](0)            # sets bit 3 of digit 1 to 0
        52789
        >>> N.subst[1](lambda s: ~s)    # substitutes first digit by its bitwise inversion
        59789
                        """)

    def __repr__(self):
        try:
            return self.formatter()
        except TypeError:
            return self.formatter(self)

T3Number.formatter = default_formatter()

class _NullNumber(T3Number):
    def __init__(self, data = None, base = 2):
        self._str = "0"
        self._int = 0
        self.base = 2

    def __repr__(self):
        return "NULL"

    def __len__(self):
        return 0

    def __mul__(self, other):
        return self

    def __add__(self, other):
        return other

    def __rlshift__(self, other):
        return other

    def __rmod__(self, other):
        return other

    def __rrshift__(self, other):
        return other

    def __radd__(self, other):
        return other

    def __rsub__(self, other):
        return other

    def __rmul__(self, other):
        return self

    def __rfloordiv__(self, other):
        return other

    def __ror__(self, other):
        return other

    def __or__(self, other):
        return other

    def _from_string(self, S, base):
        self._str = "0"
        self._int = 0

    def _from_int(self, S, base):
        self._str = "0"
        self._int = 0

T3Number.NULL = _NullNumber(0, 2)

class Bin(T3Number):
    def __init__(self, data, base = 2):
        super(Bin, self).__init__(data, 2)

    def bytes(self):
        _bytes = []
        n = len(self)
        i = n%8
        r = self[0:i].number()
        _bytes.append(r if r<0x80 else r - 0x100)
        while i<n:
            r = self[i:i+8].number()
            _bytes.append(r if r<0x80 else r - 0x100)
            i+=8
        return array('b', _bytes)

class Hex(T3Number):
    def __init__(self, data, base = 16, leftpad = False):
        if isinstance(data, T3Number):
            leftpad = True
        super(Hex, self).__init__(data, 16)
        if len(self._str) & 1 == 1:
            if leftpad:
                self._str = "0"+self._str
            else:
                raise ValueError("Hex object was constructed with an odd number of digits. An even number was expected")

    def _from_integer(self, n, base):
        super(Hex, self)._from_integer(n, base)
        if len(self._str) & 1 == 1:
            self._str = "0" + self._str

    def modexp(self, x, m):
        expm = []
        for s in x, m:
            if isinstance(s, T3Number):
                expm.append(x._int)
            elif isinstance(s, int):
                expm.append(s)
            else:
                expm.append(T3Number(s)._int)
        return Hex(pow(self._int, expm[0], expm[1]))

    def bytes(self):
        _bytes = []
        for b in self:
            r = b.number()
            _bytes.append(r if r<0x80 else r - 0x100)
        return array('b', _bytes)

    def _bits_per_item(self):
        return 8

    def __len__(self):
        return len(self._str)/2

    def __iter__(self):
        i = 0
        while i<len(self._str):
            yield Hex(self._str[i:i+2])
            i+=2

    def __getitem__(self, i):
        if isinstance(i, slice):
            i = slice(2*i.start if i.start is not None else i.start,
                      2*i.stop if i.stop is not None else i.stop,
                      i.step)
            s = self._str[i]
        else:
            s = self._str[i*2:i*2+2]
        if s:
            return self.__class__(s, self.base)
        else:
            return T3Number.NULL


class Bcd(T3Number):
    def __init__(self, data, base = 10):
        super(Bcd, self).__init__(data, 10)
        if len(self._str) & 1 == 1:
            self.zfill(len(self._str)+1)

    def _num_prefix(self):
        return "bcd'"

    def _from_t3number(self, N, base):
        if N.base == 10:
            self._int = N._int
            self._str = N._str
        else:
            if N.base == 16 and N._str.isdigit():
                bcd = Bcd(N._str)
            else:
                bcd = Bcd(N._int)
            self._str = bcd._str
            self._int = bcd._int

    def bytes(self):
        _bytes = []
        i = 0
        while i<len(self._str):
            d1 = int(self._str[i])
            d2 = int(self._str[i+1])
            n = (d1<<4) + d2
            _bytes.append(n if n<0x80 else n - 0x100)
            i+=2
        return array('b', _bytes)

    def _from_array(self, a, base):
        if a.typecode == 'b':
            bytes = [(x+256 if x<0 else x) for x in a]
        elif a.typecode == 'B':
            bytes = a.tolist()
        else:
            raise TypeError("invalid typecode '%s' of array. Typecode must be either 'b' or 'B'"%a.typecode)
        S = []
        for i, b in enumerate(bytes):
            d1 = ((b&0xF0)>>4)
            d2 = (b&0x0F)
            if d1>9:
                raise ValueError("Number is not BCD. Digit '%X' found in byte %d"%(d1, i+1))
            if d2>9:
                raise ValueError("Number is not BCD. Digit '%X' found in byte %d"%(d2, i+1))
            S.append(str(d1))
            S.append(str(d2))
        self._str = ''.join(S)
        self._int = int(self._str)


if __name__ == '__main__':
    b1 = T3Number("0101", 2)
    b2 = T3Number("0010", 2)
    b3 = T3Number("0001", 2)
    assert b1 + b2 == 7
    assert b1 * b2 == 10
    assert b1 ^ b3 == 4
    assert b1 - b3 == 4
    assert b1 << 4 == 80
    assert b1 >> 4 == 0
    assert len(b1>>4) == 4
    assert len(b1<<4) == 7
    b4 = T3Number("00000000", 2)
    assert len(b4+4) == 8
    b5 = T3Number("01", 16)
    assert b1*2+b5  == Hex("0B")
    assert list(b1) == [0, 1, 0,  1]
    assert len(Hex("0B")) == 1
    assert b5>b4
    assert b5>b4

    d = {b1: "b1", b2: "b2"}
    assert d[2] == "b2"
    assert d[Hex(5)] == "b1"

    assert b4.subst[1](1) == Bin("01000000")
    assert b4.subst[1](1) != Bin("01000001")
    N = T3Number("56789", 16)
    assert N.subst[1](0) == "50789"
    assert N.subst[1:3](0) == "5089", N.subst[1:3](0)
    assert N.subst[1][1](1) == "57789", N.subst[1][1](1)
    assert N.subst[1][2](0) == "54789", N.subst[1][2](0)
    assert N.subst[1][3](0) == "52789", N.subst[1][3](0)
    assert N.subst[1][4](1) == "5E789", N.subst[1][4](1)

    try:
        N.subst[1][0](1)
        assert False, "IndexError exception not raised"
    except IndexError:
        pass
    try:
        N.subst[1][5](1)
        assert False, "IndexError exception not raised"
    except IndexError:
        pass

    N = T3Number("56789", 10)
    assert N.subst[1](0) == "50789"
    assert N.subst[1:3](0) == "5089", N.subst[1:3](0)
    assert N.subst[1][1](1) == "57789", N.subst[1][1](1)
    assert N.subst[1][2](0) == "54789", N.subst[1][2](0)
    assert N.subst[1][3](0) == "52789", N.subst[1][3](0)

    try:
        assert N.subst[1][4](1) == "5E789", N.subst[1][4](1)
        assert False, "IndexError exception not raised"
    except IndexError:
        pass
    assert list(Hex("89AF")) == [0x89, 0xAF]

    assert Hex(0xA60289AF) == 0xA60289AF


    h = Hex("A60289"*99)
    #print h
    h.formatter = default_formatter(tabular = True)

    #print h

    d = Bcd("00 11 98 15 42 15 52 42 54")
    assert d == Bcd(d.bytes())
    assert d.bytes() == Bcd(d.bytes()).bytes()
    assert d.digits() == Bcd(d.bytes()).digits()


    d.zfill(19)
    print Bcd(d)

    h = Hex(u"A9 78")
    print h

    print Hex("80 01 02 03")[4]
    assert T3Number.NULL[0]   == T3Number.NULL
    assert T3Number.NULL[1:3] == T3Number.NULL
    assert T3Number.NULL+3 == 3
    assert T3Number.NULL+3 == 3
    assert 3*T3Number.NULL == T3Number.NULL
    assert 3 == 3+T3Number.NULL, 3+T3Number.NULL
    assert T3Number.NULL*16 == T3Number.NULL
    assert T3Number.NULL*2 == T3Number.NULL
    assert 1+T3Number.NULL == 1
    assert T3Number.NULL<<4 == T3Number.NULL
    assert T3Number.NULL>>4 == T3Number.NULL
    assert int(T3Number.NULL) == 0
    assert list(T3Number.NULL) == [T3Number.NULL]
    assert T3Number.NULL.digits() == "0"
    assert T3Number.NULL.bytes() == array('b')
    assert int(T3Number.NULL) == 0
    assert T3Number.NULL // T3Number.NULL == T3Number.NULL
    assert T3Number.NULL // Hex(0x78) == Hex(0x78)
    assert Hex(0x78) // T3Number.NULL == Hex(0x78)
    assert len(T3Number.NULL*16) == 0
    assert list(T3Number.NULL*16) == [T3Number.NULL]
    assert T3Number.NULL<<3 == T3Number.NULL
    assert 3<<T3Number.NULL == 3


    assert Bin(~Hex(0xAF)) & Bin(0xAF) == Bin(0x00)
    assert Bin(~Hex(0xAF)) & Bin(0xAF) == Bin(0x00)
    assert Hex(00)-Hex(78) == Hex(-78)

    print T3Number("23333334", 6)

    assert Bin("1100") == Bin("001100")
    assert list(Bin("1100")) != list(Bin("001100"))

    print Hex("2526"*56).modexp(627282929, '42 52 42 72 62 76 25 26 52 24 52 42 54 25 40')

    h = Hex("702782782782782626227827287287287282782267262F27827287287388298006272525")
    h.formatter = default_formatter(tabular = True)
    print h

    assert Hex.join('72', 0x6627, T3Number(67, 10)) == '72 66 27 43'
    print Bin.join('110010', 0x6627, T3Number(67, 16))

    assert Bin(T3Number(67, 16)) == '1000011'


    assert (Hex('00 01')*10).digits() == '000A'
    assert Bin(Hex(Bin('000000000000000000000000'))) == '000000000000000000000000'
    assert Hex(Bin(Hex('00 00 00'))).digits() == '000000'





