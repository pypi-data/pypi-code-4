#!/usr/bin/env python
import sys
from pyltfs2 import LTFS

if len(sys.argv) < 3:
    print 'Syntax: addtape2db.py <xml file> <name> <customa> ... <customd>'
    sys.exit(1)

sys.argv += ['', '', '', '', '', '', None]

args = sys.argv[1:7]

print """Adding tape
===========
XML      : %s
Name     : %s
Custom A : %s
Custom B : %s
Custom C : %s
Custom D : %s
===========
""" % tuple(args)
#Checksums: %s

url = 'mysql+mysqlconnector://root:123@localhost/syslink_tapelibrary'
ltfs = LTFS(url)

try:
    args[0] = open(args[0]).read()
except:
    print 'Can\'t read XML file'
    sys.exit(1)

#CHECKSUM_FILE = '/var/lib/syslink/archive/checksums'
ltfs.delete_tape(name=args[1])
ltfs.create_tape(
    *args
)

print 'Done!'
