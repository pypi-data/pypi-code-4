import os, sys, unittest2, re
sys.path.append(os.path.join(__file__, '..', '..', '..', '..'))

#TODO: fix imports
import cardsharp as cs
from cardsharp.drivers import *
from cardsharp.test.drivers import *
from itertools import izip_longest

def _roundtrip(d1, row_test, **kw):
    '''Testing function to ensure that every loader is able to save data 
    to its respective format and that when it loads the saved data 
    the data matches the original csharp dataset.
    '''
    
    err = 'Datasets do not have the same length'
    
    with get_temp_file('txt') as temp:
        row_dict1, row_dict2 = {}, {}
        
       
        d1.save(source=temp.name, **kw)
        cs.wait()
        d2 = cs.load(source=temp.name, **kw)    
        cs.wait()
         
        for i, (r1, r2) in enumerate(izip_longest(d1, d2)):
            assert r1 is not None and r2 is not None, err  
            row_test(i, r1, r2)

def _row_test(i, r1, r2):
    r1 = (r1[0], unicode(r1[1]), unicode(r1[2]), unicode(repr(r1[3])), 
          unicode(r1[4]).replace('-', '/'), unicode(r1[5]).replace('-', '/'), 
          unicode(r1[6]), u'1' if r1[7] else u'0', r1[8].encode('base64'))
    r2 = tuple(x or u'' for x in r2)
    
    err = 'Row %i does not match after saving and loading for text handler' % i
    assert r1 == r2, err
                 
class TestRoundtrip(unittest2.TestCase):
    def setUp(self):
        self.ds = construct_random_dataset()
         
    def test_txt_roundtrip(self): 
        _roundtrip(self.ds, row_test=_row_test, format='text', encoding='utf_8')
    
    def test_txt_delimiter(self):
        for delim, line_delim in (
            ('\t', '\n'), 
            ('\r\r', '!!!!!'),
            ('1279811', '####')):
            with get_temp_file('txt') as temp:
                self.ds.save(source = temp.name, format = 'text', line_delimiter = line_delim, delimiter = delim)
                cs.wait()
                d1 = cs.load(source = temp.name, format = 'text', line_delimiter = line_delim, delimiter = delim)
                for i, (r1, r2) in enumerate(izip_longest(self.ds, d1)):
                    assert r1 is not None and r2 is not None, 'Datasets do not have the same length' 
                    _row_test(i, r1, r2)
                    
                    
                    