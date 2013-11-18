#!/usr/bin/env python

"""Test RACM2 reading and compound translation"""

from ac.gasphase.reaction import Reaction
from ac.gasphase.speciestable import speciesTable

t = speciesTable.from_csv()
model = "MOZ_MIM2"

rstring = raw_input("Reaction: ")
r = Reaction.from_mech(rstring+": 0.;")
r.check_mass(model, t)
