import operator

#===========================================================

def enum(t):
    """Enum decorator that adds to_string and parse support
    
    Example:
    @enum
    class MyEnum:
        (Val1, Val2) = range(2)
    
    e = MyEnum.Val1
    MyEnum.toString(e) # outputs 'Val1'
    e = MyEnum.parse('val2', default=None) # assigns MyEnum.Val2
    
    MyEnum.values # returns list of values
    """
    
    fs = { }
    ts = { }
    
    values = []
    
    for k, v in t.__dict__.iteritems():
        if not k.startswith('_') and isinstance(v, int):
            values.append(v)
            fs[k.lower()] = v
            ts[v] = k
    
    def _to_string(c, val, default=None): return c._ts.get(val, default)
    def _parse(c, s, default=None): return c._fs.get(s.lower(), default)
    
    setattr(t, 'toString', classmethod(_to_string))
    setattr(t, 'parse', classmethod(_parse))
    setattr(t, 'values', values)
    
    setattr(t, '_ts', ts)
    setattr(t, '_fs', fs)
    return t

#===========================================================

def flags(t):
    """Decorator for enums that intended to be used as bit flags
    
    Example:
    @flags
    class Caps(object):
        Read, Write, Create, Delete = flags_seq(4)
        All = 0xff
    
    """
    
    fs = { }
    ts = { }
    
    values = []
    
    for k, v in t.__dict__.iteritems():
        if not k.startswith('_') and isinstance(v, int):
            values.append(v)
            fs[k.lower()] = v
            ts[v] = k
    
    def _to_string(c, val, default=None):
        if val in c.values:
            return c._ts.get(val)
        
        in_values = [ v for v in c.values if v and (val & v) == v ]
        all_values = reduce(operator.or_, in_values)

        if all_values != val or not in_values:
            return default

        in_values.sort()
        return ' | '.join( ( c._ts.get(v) for v in in_values ) )
    
    def _parse(c, s, default=None):
        elems = map(str.strip, s.split('|'))
        valelems = [ c._fs.get(e) for e in elems ]
        
        if not elems or None in valelems:
            return default
        
        return reduce(operator.or_, valelems)
    
    setattr(t, 'toString', classmethod(_to_string))
    setattr(t, 'parse', classmethod(_parse))
    setattr(t, 'values', values)
    
    setattr(t, '_ts', ts)
    setattr(t, '_fs', fs)
    return t

#===========================================================

def flags_seq(num):
    """Use to generate flags enum values
    
    Example:
    @flags
    class MyFlags(object):
        A, B, C = flags_seq(3)
        ALL = 0xf
    
    MyFlags.A == 0x1
    MyFlags.B == 0x2
    MyFlags.C == 0x4
    """
    
    return [1 << i for i in range(num)]

