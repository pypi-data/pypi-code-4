#!/usr/bin/env python
import sys
import pyLTFS

if len(sys.argv) < 3:
    print 'Syntax: addtape2db.py <path> <name> <customa> ... <customd> <checksums-file>'
    sys.exit(1)

sys.argv += ['', '', '', '', '', '', None]

args = sys.argv[1:8]

print """Adding tape
===========
Root     : %s
Name     : %s
Custom A : %s
Custom B : %s
Custom C : %s
Custom D : %s
Checksums: %s
===========
""" % tuple(args)

ltfs = pyLTFS.TapeLibraryHandler()
ltfs.options["iMaxDepth_sqlamp"] = 9999
ltfs.options["iLogLevel"] = 2
#ltfs.options["bAddAll"] = False
ltfs.lic_InitDB(
    sUser="dbuser",
    sPass="syslink",
    sDBName="syslink_tapelibrary",
    sDBType="postgresql"
)

CHECKSUM_FILE = '/var/lib/syslink/archive/checksums'

ltfs.lic_deleteTape(args[1])
ltfs.lic_CreateTape(
    *args
)

print 'Done!'
