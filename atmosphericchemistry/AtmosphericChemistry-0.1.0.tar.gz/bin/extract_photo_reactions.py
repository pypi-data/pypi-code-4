#!/usr/bin/env python

"""Read monster mechanism and extract photolysis reactions"""

from ac.gasphase.mechanism import Mechanism
from ac import TESTDATADIR

m = Mechanism.from_mech(TESTDATADIR+"/sample.mech")
reactions = []
for r in m.reactions:
    if r._isphoto:
        reactions.append(r)
m._reactions = reactions
m.write_mech(TESTDATADIR+"/test_sample_photo.mech")


