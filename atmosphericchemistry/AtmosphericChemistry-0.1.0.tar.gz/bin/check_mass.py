#!/usr/bin/env python

"""Check mass budget for reactions of a specific compound"""

from ac.gasphase import mechanism
from ac import TESTDATADIR

m = mechanism.Mechanism.from_mech(TESTDATADIR+"/sample.mech")
t = m._speciestable
model = "MOZ_MIM2"

compound = "CH3CHO"

print "Checking mass conservation for reactions of %s" % (compound)
subset = m.find_reactions([compound])
for rr in subset:
    if rr.check_mass(model, t):
        print "OK: ", rr.to_mech(short=True)

# Note: errors will be reported automatically, hence we only need to print
# reactions that are mass-conserving.


