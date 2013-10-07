import sys, os, tempfile
import cardsharp as cs
__all__ = ['construct_random_dataset', 'get_temp_file']

from random import Random
from nose.tools import assert_raises, assert_almost_equal
import random
import base64

def construct_random_dataset(rows=None, unicode_range=(0, 65535), 
                             year_range=(0, 9999), unicode_length=1000, 
                             binary_length=1000, id=False):
    if not rows:
        rows = cs.config.test_rows
    
    _r = Random()
    _r.seed(1)

    import datetime
    from decimal import Decimal
    from functools import partial

    _r0 = partial(_r.randint, 0)
    _r1 = partial(_r.randint, 1)
    
    def _rint(range):
        return _r.randint(*range)
    
    def _rfloat(range):
        return _r.uniform(*range)
    
    quotes = ('\'','"')
    
    def _check_quotes(val):
        try: 
            if val[0] in quotes and val[-1] not in quotes: 
                val[-1] =  val[0]
        except:
            pass
        return val
    
    vars = [
        ('a', 'string', lambda: _check_quotes(''.join([unichr(_rint(unicode_range)) for _ in xrange(_r0(unicode_length))]))),
        ('b', 'integer', lambda: _r.randint(-10000, 10000)),
        ('c', 'decimal', lambda: Decimal(str(_r.uniform(-10000, 10000)))),
        ('d', 'float', lambda: _r.uniform(-10000, 10000)),
        ('e', 'datetime', lambda: datetime.datetime(year = _rint(year_range), month = _r1(12), day = _r1(28), hour = _r0(23), minute = _r0(59), second = _r0(59))),
        ('f', 'date', lambda: datetime.date(year = _rint(year_range), month = _r1(12), day = _r1(28))),
        ('g', 'time', lambda: datetime.time(hour = _r0(23), minute = _r0(59), second = _r0(59))),
        ('h', 'boolean', lambda: True if _r0(1) else False),
        ('i', 'binary', lambda: ''.join([unichr(_rint(unicode_range)) for _ in xrange(_r0(binary_length))]).encode('utf-8')),
    ]
        
    d = cs.Dataset([(v, f) for v, f, func in vars])
    if id:
        d.variables.append(('j', 'integer'))
    
    c = 0
    for _ in xrange(rows):
        c += 1
        r = [func() for v, f, func in vars]
        if id:
            r.append(c)
        d.add_row(r)
          
    return d

def get_temp_file(suffix):
    class TempFile(object):
        def __init__(self):
            self.name = tempfile.mktemp(
                          suffix='.' + suffix, 
                          prefix='test_', 
                          dir=os.path.join(os.path.dirname(__file__), '..', 'test'))
        
        def __enter__(self):
            return self
        
        def __exit__(self, ex_type, ex_value, ex_tb):
            if os.path.exists(self.name) and cs.config.test_remove_temp_files:
                try:
                    os.remove(self.name)
                except:
                    pass
    
    return TempFile()