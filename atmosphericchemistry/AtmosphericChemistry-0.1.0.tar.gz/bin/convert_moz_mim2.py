#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""Convert_moz_mim2 from mozpp to mech and back"""


from ac.mechanism import Mechanism


infile = "../testdata/sample_mozpp1.in"
preamble = "../testdata/mozpp_preamble.txt"
footer = "../testdata/mozpp_footer.txt"
outfile = "../testdata/test_mozpp_out.in"

mechfile = "../testdata/test_mozpp_to_mech.mech"

m = Mechanism.from_mozpp(infile)

#for r in m.reactions:
#    r.preserve_m()
    
m.write_mech(mechfile)

# read preamble and footer
with open(preamble, "r") as f:
    lpre = f.readlines()
with open(footer, "r") as f:
    lfoot = f.readlines()
    
m.write_mozpp(outfile, preamble=lpre, footer=lfoot)
