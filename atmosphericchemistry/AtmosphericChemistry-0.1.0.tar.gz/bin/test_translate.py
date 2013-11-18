#!/usr/bin/env python

"""Test RACM2 reading and compound translation"""

import os
from ac.gasphase.mechanism import Mechanism
from ac import TESTDATADIR

m = Mechanism.from_mch(TESTDATADIR + "sample_mch.txt")
m.translate_to_model("MOZ_MIM2")
m.write_mech(TESTDATADIR + "test_mch.mech")
m.write_kpp_mecca(TESTDATADIR + "test_mch.eqn")
