#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""prepare_mecca: collection of routines to convert various mechanisms to MECCA chemistry
files.

These routines use the Mechanism class from the AtmosphericChemistry package."""

import os
from ac.gasphase.mechanism import Mechanism
from ac import TESTDATADIR

try:
    os.mkdir(TESTDATADIR+"/mecca_files")
except WindowsError as e:
    if e.args[0] == 183:
        pass    # Windows complains if folder already exists
    else:
        raise WindowsError(e)
    

def moz_mim2_to_mecca(filename=TESTDATADIR+"/hammoz_mim2.mech",
                      outfile=TESTDATADIR+"/mecca_files/moz_mim2_base.eqn"):
    """Convert MOZ_MIM2 mech file to KPP MECCA. Extract only tropospheric reactions and
    omit aerosol reactions and Rn (these are identified by their reaction tags.
    Afterwards, reset all remaining reaction tags so that MECCA defaults (StTrG) are used."""
    m = Mechanism.from_mech(filename)
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # stratospheric reactions
        if "S" in r.tags:
            dellist.append(i)
        # aerosol reactions
        elif "aer" in r.tags:
            dellist.append(i)
        # synthetic tracer reactions
        elif "syn" in r.tags:
            dellist.append(i)
        # het reactions
        elif str(r.kterm).startswith("het"):
            dellist.append(i)
        # undesired reactants
        else:
            omit = ["e", "Rn", "NH3", "SO2", "DMS", "CL"]
            for rsp in omit:
                if rsp in r.reactants:
                    dellist.append(i)
    dellist = sorted(list(set(dellist)))
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # reset reaction tags
    for r in m.reactions:
        r.tags = []

    # save remaining set as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()

    

def racm2_to_mecca(filename=TESTDATADIR+"/RACM2_5M4e.txt",
                   outfile=TESTDATADIR+"/mecca_files/racm2.eqn"):
    """Convert RACM2 file to KPP MECCA."""
    m = Mechanism.from_mch(filename)
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # undesired reactants
        omit = ["Rn", "NH3", "SO2", "DMS"]
        for rsp in omit:
            if rsp in r.reactants:
                dellist.append(i)
    dellist = sorted(list(set(dellist)))
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # reset reaction tags
    for r in m.reactions:
        r.tags = []

    # rename to MOZ_MIM2 namespace
    m.translate_to_model("MOZ_MIM2")
    # save as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()

    

def mecca_to_mecca(filename=TESTDATADIR+"/mainz.eqn",
                   outfile=TESTDATADIR+"/mecca_files/mecca.eqn"):
    """Convert MECCA file to KPP MECCA. Eliminate various reactions and rename compounds to
    MOZ_MIM2 namespace."""
    m = Mechanism.from_kpp(filename)
    m.model = "MECCA"
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # undesired tags
        omit = ["GCl", "GBr", "GI", "GS", "GNCl", "GNBr", "GNI", "GNS", "GCCl", "GCBr",
                "GHg", "GF", "Het"]
        for rsp in omit:
            if rsp in r.tags:
                dellist.append(i)
    dellist = sorted(list(set(dellist)))
    print "#### dellist = ", dellist
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # rename to MOZ_MIM2 namespace
    m.translate_to_model("MOZ_MIM2")
    # save as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()


def mocage_to_mecca(filename=TESTDATADIR+"/mocage.eqn",
                   outfile=TESTDATADIR+"/mecca_files/mocage.eqn"):
    """Convert MOCAGE file to KPP MECCA. Eliminate various reactions and rename compounds to
    MOZ_MIM2 namespace.
    Note: H2O and CH4 photolysis needs to be manually removed afterwards."""
    m = Mechanism.from_kpp(filename)
    m.model = "MOCAGE"
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # undesired elements in reactants
        omit = ["Cl", "Br", "DMS", "CFC", "N2O", "SO2", "H1211", "H1301"]
        for rsp in omit:
            for j in r.reactants:
                if rsp in j:
                    dellist.append(i)
    dellist = sorted(list(set(dellist)))
    print "#### dellist = ", dellist
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # clear reaction labels
    m.clear_labels()
    # rename to MOZ_MIM2 namespace
    m.translate_to_model("MOZ_MIM2")
    # save as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()


def mozart_to_mecca(filename=TESTDATADIR+"/mozart35.in",
                   outfile=TESTDATADIR+"/mecca_files/mozart.eqn"):
    """Convert MOZART file as used in MACC to KPP MECCA. Eliminate various
    reactions and rename compounds to MOZ_MIM2 namespace.
    Note: O2, H2O and CH4 photolysis needs to be manually removed afterwards,
    N and N2O and their reactions can also be removed."""
    m = Mechanism.from_mozpp(filename)
    m.model = "CAM-CHEM"
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # undesired elements in reactants
        omit = ["CL", "BR", "DMS", "HCFC", "N2D", "CF", "Rn", "NH3", "NH4", "SO2"]
        for rsp in omit:
            for j in r.reactants:
                if rsp in j:
                    dellist.append(i)
        if "het" in str(r.kterm):
            dellist.append(i)
    dellist = sorted(list(set(dellist)))
    print "#### dellist = ", dellist
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # reset reaction tags
    for r in m.reactions:
        r.tags = []

    # rename to MOZ_MIM2 namespace
    m.translate_to_model("MOZ_MIM2")
    # save as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()


def tm5_to_mecca(filename=TESTDATADIR+"/tm5.eqn",
                   outfile=TESTDATADIR+"/mecca_files/tm5.eqn"):
    """Convert MOCAGE file to KPP MECCA. Eliminate various reactions and rename compounds to
    MOZ_MIM2 namespace."""
    m = Mechanism.from_kpp(filename)
    m.model = "TM5"
    # remove unwanted reactions
    dellist = []
    for i, r in enumerate(m.reactions):
        # undesired elements in reactants
        omit = ["DMS", "SO", "NH2", "NH3", "NH4"]
        for rsp in omit:
            for j in r.reactants:
                if rsp in j:
                    dellist.append(i)
    print "#### dellist = ", dellist
    # need to remove backwards
    for i in range(len(dellist)-1, -1, -1):
        del m.reactions[dellist[i]]

    # rename to MOZ_MIM2 namespace
    m.translate_to_model("MOZ_MIM2")
    # save as KPP MECCA file
    m.write_kpp_mecca(outfile)
    m.statistics()



            
