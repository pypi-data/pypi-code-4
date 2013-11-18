"""Test suite for Mechanism class

To run these tests:
from ac.gasphase.test import test_mechanism
test_mechanism.testsuite()

You can modify user settings in testsuite below.
"""

import os
import datetime as dt
from ac.gasphase.mechanism import Mechanism
from ac.utils import wait
from ac import TESTDATADIR as BASEPATH



def test_reading():
    
    # ----------------------------------------------------------------------
    # Read (different) mechanisms in different formats
    # mech format
    m0 = Mechanism.from_mech(BASEPATH+"/sample.mech")
    print

    # spreadsheet format:
    m1 = Mechanism.from_csv(BASEPATH+"/sample.csv",
                            start="EQUATIONS", stop="END EQUATIONS")
    print

    # KPP MECCA (original Mainz mechanism)
    # can also handle simpler KPP format
    m2 = Mechanism.from_kpp(BASEPATH+"/sample.eqn")
    print

    # MOZPP format
    m3 = Mechanism.from_mozpp(BASEPATH+"/sample_mozpp1.in")
    print

    return m0, m1, m2, m3



def test_writing(m):
    # ----------------------------------------------------------------------
    # Write mechanism in various formats
    # filename will be determined automatically
    curdir = os.getcwd()
    now = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    wrkdir = BASEPATH+"/"+now
    os.mkdir(wrkdir)
    os.chdir(wrkdir)
    
    print "Writing %s in Mech format..." % (m)
    m.write_mech()   
    print
    print "Writing %s in CSV format..." % (m)
    m.write_csv(separator=";")   
    print
    print "Writing %s in KPP UKCA format..." % (m)
    m.write_kpp_ukca()   
    print
    print "Writing %s in KPP MECCA format..." % (m)
    m.write_kpp_mecca()   
    print
    print "Writing %s in MOZPP format..." % (m)
    m.write_mozpp()   
    print
    os.chdir(curdir)

    

def test_attributes(m):
    # ----------------------------------------------------------------------
    # Read and write mechanism attributes such as name and model name

    print "Mechanism %s: Name=%s, model=%s" % (m, m.name, m.model)
    print "Changing name to pp_dummy and model to CAM-CHEM..."
    m.name = "pp_dummy"
    m.model = "CAM-CHEM"
    print "Mechanism %s: Name=%s, model=%s" % (m, m.name, m.model)

    print "Other properties:"
    print "Variables:"
    print m.variables
    print "Comments:"
    print m.comments
    print "Number of reactions: ", len(m.reactions)
    print "Mechanism revision = ", m.revision
    print "Adding a revision tag to reactions 1..20..."
    for i in range(20):
        r = m.reactions[i]
        if not r.revision:
            r.set_revision(dt.date(2013, 10, 1), author="mgs")



def test_M(m):
    # ----------------------------------------------------------------------
    # Make sure M is used properly in all reactions
    print "Ensuring consistency in the use of 'M' in all reactions..."
    for r in m.reactions:
        r.preserve_m()
    print "Done."


def test_mass_balance(m):
    # ----------------------------------------------------------------------
    # Check mass balance for all reactions
    # first, load species table
    print "testing mass balance for all reactions ..."
    m.check_mass_balance()
    print "Done."


def test_rename(m, newmodel):
    # ----------------------------------------------------------------------
    # Rename species to anothe rmodel namespace (where available)
    # Write out in mech format (includes list of variables and functions)
    m.translate_to_model(newmodel)
    m.write_mech(BASEPATH+"/translation_test_%s.mech" % (newmodel))
    print "Species translation successful. Translation table:"
    for k, v in m._translate.items():
        print "%s -> %s" % (k, v)


def test_shorten(m, nchar=8):
    # ----------------------------------------------------------------------
    # shorten species names to max. nchar characters
    # Note, that this prevents species translation, because truncated compound
    # names are not found in sepciestable.
    m.shorten_species_names(nchar)
    m.write_mozpp(BASEPATH+"/shorten_test_%s.mech" % (m))


def testsuite():
    m0, m1, m2, m3 = test_reading()
    wait()
    # --- USER SETTINGS ---
    mtest = m0   # models: m0:MOZ_MIM2, m1:CAM-CHEM, m2:MECCA, m3:CAM-CHEM
    oldmodel = mtest.model
    if not oldmodel.strip():
        oldmodel = raw_input("Enter model name (namespace) to continue. Mechanism=%s: "%(mtest))
        mtest.model = oldmodel
    newmodel = "MECCA"
    # --- END USER SETTINGS ---
    test_writing(mtest)
    wait()
    test_attributes(mtest)
    wait()
    test_M(mtest)
    wait()
    # must (re)set model name to correct name for the following
    mtest.model = oldmodel
    # use a try except block here in case we have undefined reactants
    try:
        test_mass_balance(mtest)
    except ValueError as e:
        print "**** ValueError: ", e.args[0]
    wait()
    test_rename(mtest, newmodel)
    wait()
    test_shorten(mtest)

    
if __name__ == "__main__":
    testsuite()
