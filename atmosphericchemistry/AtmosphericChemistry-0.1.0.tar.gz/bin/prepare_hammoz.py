#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""prepare_hammoz: extract reactions for troposphere and lower-mid stratosphere
from monster mechanism and write out as MOZPP file."""


import os
from ac.gasphase.mechanism import Mechanism
from ac import TESTDATADIR

try:
    os.mkdir(TESTDATADIR+"/hammoz_files")
except WindowsError as e:
    if e.args[0] == 183:
        pass    # Windows complains if folder already exists
    else:
        raise WindowsError(e)
    

def moz_mim2_to_hammoz(filename=TESTDATADIR+"/hammoz_mim2.mech",
                       outfile=TESTDATADIR+"/hammoz_files/hammoz_v2.in"):
    """Convert MOZ_MIM2 mech file to MOZPP."""
    # read mechanism, preamble and footer
    m = Mechanism.from_mech(filename)
    with open(TESTDATADIR+"/hammoz_v2_preamble.txt", "r") as f:
        txtpre = f.readlines()
    with open(TESTDATADIR+"/hammoz_v2_footer.txt", "r") as f:
        txtaft = f.readlines()
    
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # aerosol reactions
        if "aer" in r.tags:
            dellist.append(i)
        # synthetic tracer reactions
        elif "syn" in r.tags:
            dellist.append(i)
        # ion reactions
        elif "ion" in r.tags:
            dellist.append(i)
        # EUV photolysis
        elif "euv_" in str(r.kterm).lower():
            dellist.append(i)
        # NO photolysis channel 2
        elif "jno_i" in str(r.kterm).lower():
            dellist.append(i)
        # undesired reactants
        else:
            omit = ["e", "Rn", "N2D", "SF6em", "O2p", "NOp", "O2_1S", "O2_1D"]
            for rsp in omit:
                if rsp in r.reactants:
                    dellist.append(i)
    dellist = sorted(list(set(dellist)))
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # change product names O2_1D and  O2_1S to O2 (two reactions)
    rlist = m.find_reactions(["O3","hv"])
    for r in rlist:
        ps = r._products.as_string().replace("O2_1D", "O2")
        r.products = ps
        print r.to_mech(short=True)
    rlist = m.find_reactions(["O1D","O2"])
    for r in rlist:
        ps = r._products.as_string().replace("O2_1S", "O2")
        r.products = ps
        print r.to_mech(short=True)
    
    # remove cph tags
    for r in m.reactions:
        if "cph" in r.tags:
            r.tags = r.tags.replace("cph","")
            
    # save remaining set MOZPP file
    m.write_mozpp(outfile, preamble=txtpre, footer=txtaft)
    m.statistics()


if __name__ == "__main__":
    moz_mim2_to_hammoz()
    
