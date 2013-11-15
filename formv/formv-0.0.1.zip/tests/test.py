#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import os, unittest, logging, errno, formv
from unittest.runner import TextTestRunner
from pprint import pprint
from formv.configuration import build
from tests import Country
from tests.validators import *
from tests.utils import Test as utils_match
from tests.utils.encoding import Test as utils_encoding
from formv.utils.compat import PY2, PY3
if PY2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
if PY3:
    from io import StringIO

logging.basicConfig(filename='../logs/formv.log', level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s][%(filename)s] %(name)s %(funcName)s (line: %(lineno)d) %(message)s')
log = logging.getLogger(__name__)

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  

def run_tests(mode, log_config=False, make_test_dirs=False, test_coverage=False):      
    """ 
    To run the tests w/out any changes, the following directories have to exist:
        - /srv/www/backup
        - /srv/www/email
        - /srv/www/public
        - /srv/www/storage
        - /srv/www/text
    They can be created automatically by setting make_test_dirs=True
    See formv/validators/files.py & tests/validators/files.py for details. 
    """
    assert mode in ('json_config', 'callables')
    
    if make_test_dirs:
        for d in ('/srv/www/backup','/srv/www/email',
                  '/srv/www/public','/srv/www/storage',
                  '/srv/www/text'):
            if not os.path.isdir(d):
                try:
                    os.makedirs(d)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
    
    if test_coverage:
        from coverage import coverage
        c = coverage()
        c.start()
    
    o = StringIO()
    try:
        if mode == 'json_config':
            o.write('Testing formv with json configuration...\n')
            o.write('-'*70 + '\n')
            formv.config = build(config_root=os.path.join(app_root, 'tests'))  
            
        if mode == 'callables':           
            o.write('Testing formv with callables configuration...\n')
            o.write('-'*70 + '\n')
            formv.config = build(config_root=os.path.join(app_root, 'tests'),
                                 countries={'USA': Country('USA')})
            
        unittest.main(testRunner=TextTestRunner(stream=o, verbosity=2), exit=False,)
    
        if log_config:      
            pprint(formv.config, o)
    
        log.info('\n'+o.getvalue())
        print(o.getvalue())
    finally:
        o.close()
                    
    if test_coverage:
        c.stop()
        c.html_report(directory='../logs/coverage')
                            
if __name__=='__main__':  
    run_tests(mode='json_config', log_config=False, 
              make_test_dirs=False, test_coverage=True)
     
    run_tests(mode='callables', log_config=False, 
              make_test_dirs=False, test_coverage=True)
    
    
