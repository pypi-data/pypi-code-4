
import os
import sys

HOME   = os.path.basename(sys.argv[0])
PUBLIC = HOME + '/public'

PATH_ACTION = os.path.basepath(__file__)

print 'HOME', HOME
print 'PUBL', PUBLIC
print 'ACTN', PATH_ACTION

import compact
import template
import database
import http


