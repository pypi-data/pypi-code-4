import cardsharp as cs
from cardsharp.test import construct_random_dataset, get_temp_file, construct_dataset, assert_raises, assert_cs_raises
from cardsharp.errors import RuleError, LoadError

import os

def test_length():
    ds = construct_random_dataset(rows = 1)
    
    ds1 = cs.Dataset(['s',])
    t = ''
    
    for x in xrange(1000):
        t += u"\u0411".encode('utf-16')
    
    print len('\xff')
    print len('\xff'.encode('utf-8'))
    print len(t)
    ds1.add_row([t,])
    ds1['s'].rules.length = 1000
    
#    ds['a'].rules.length = 1000
#    ds['b'].rules.length = 1000
#    ds['c'].rules.length = 1000
#    ds['d'].rules.length = 1000
#    ds['e'].rules.length = 1000
#    assert_cs_raises(RuleError, ds)
    

from datetime import datetime

def test_load_length():
    print "start @ %s." % datetime.now().isoformat(' ')
    ds = cs.load(source=os.path.join(os.path.dirname(__file__),  'data', 
                                     'rule.txt'), 
                 format='text',
                 length_rules ={'A':1, 'B':2})
    print "complete @ %s." % datetime.now().isoformat(' ')
    cs.wait()
    if ds.variables['a'].rules.length == '1':
        raise RuleError("Length not set correctly. Expected: 1 Got: %s" % ds.variables['a'].rules.length)
    elif ds.variables['a'].rules.length == '2':
        raise RuleError("Length not set correctly. Expected: 2 Got: %s" % ds.variables['b'].rules.length)
    
    
#    assert_cs_raises(LoadError, cs.load(source=os.path.join(os.path.dirname(__file__),  'data', 
#                                     'rule.txt'), 
#                 format='text',
#                 length_rules ={'F':1, 'B':2})) 