# -*- coding: cp1252 -*-
import datetime as dt
from reaction import Reaction

# for testing and debugging
# (output: may be overwritten!)
testfile_csv = "../test/test.txt"
testfile_easy = "../test/test.easy"
testfile_kpp = "../test/test_kpp.eqn"
testfile_mech = "../test/test.mech"
testfile_mozpp = "../test/test_mozpp.in"



# ---- TESTING ----
def report(reaction):
    if isinstance(reaction, Reaction):
        print "Reactants =", reaction.reactants
        print "Products =", reaction.products
        print "kterm =", reaction.kterm
        print "Tags =", reaction.tags
        print "Revision =", reaction.revision
        print "Comments =", reaction.comments
        print
        mech = reaction.to_mech(revision=dt.date.today().strftime("%Y%m%d")+"mgs")
        csv = reaction.to_csv()
        kpp = reaction.to_kpp()
        mozpp = reaction.to_mozpp()
        print "mech: ", mech
        print "CSV: ", csv
        print "KPP: ", kpp
        print "MOZ: ", mozpp
        print 76*"-"
        # save to files
        with open(testfile_csv, "a") as f:
            f.write(csv+"\n")
            f.close()
        with open(testfile_easy, "a") as f:
            f.write(reaction.to_easy_reac()+"\n")
            f.write(reaction.to_easy_k()+"\n")
            f.close()
        with open(testfile_kpp, "a") as f:
            f.write(kpp+"\n")
            f.close()
        with open(testfile_mech, "a") as f:
            f.write(mech+"\n")
            f.close()
        with open(testfile_mozpp, "a") as f:
            f.write(mozpp+"\n")
            f.close()
        

        
def test_mech_input(file="../test/dummy.mech"):
    with open(file, "r") as f:
        parsing = False
        for lineno,line in enumerate(f):
            if parsing:
                if line.startswith("CONSTANTS"):
                    parsing = False
                else:
                    print
                    print "line %4i: %s" %(lineno, line)
                    r = Reaction.from_mech(line, lineno)
                    report(r)
            elif line.startswith("REACTIONS"):
                parsing = True


def test_csv_input(file="../test/chem_mechanism_alex.csv", separator="\t"):
    with open(file, "r") as f:
        for lineno,line in enumerate(f):
            if lineno == 0:  # read header
                header = line.split(separator)
                continue
            print "line %4i: %s" %(lineno+1, line)
            r = Reaction.from_csv(line, lineno, header=header, separator=separator)
            report(r)


def test_mozpp_input():
    # simple Arrhenius with label and comment
    line = " [O_O3]       O + O3 -> 2*O      ; 8e-12, -2060  ! JPL17(2011)"
    r = Reaction.from_mozpp(line)
    report(r)
    # constant, no label, with comment
    line = "  O1D + CH4 -> CH2O + H + HO2                 ; 0.35e-10      # JPL17(2011)"
    r = Reaction.from_mozpp(line)
    report(r)
    # label, M, Troe, no comment
    line = "[NO2_HO2]    NO2 + HO2 + M -> HO2NO2 + M; 2.0e-31,3.4, 2.9e-12,1.1, 0.6"
    r = Reaction.from_mozpp(line)
    report(r)
    # product yields
    line = "CH3OOH + OH -> .7 * CH3O2 + .3 * OH + .3 * CH2O + H2O;3.8e-12,200"
    r = Reaction.from_mozpp(line)
    report(r)
    # no kterm, includes M
    line = "CO + OH + M -> CO2 + H"
    r = Reaction.from_mozpp(line)
    report(r)
    # no products and no kterm, without comment
    line = "PHAN ->"
    r = Reaction.from_mozpp(line)
    report(r)
    # no products and no kterm, same with comment
    line = "PHAN -> # comment"
    r = Reaction.from_mozpp(line)
    report(r)
    # photo reaction without alias
    line = "[joclo]               OCLO + hv -> O + CLO! j-value from netcdf file jCAM.nc "
    r = Reaction.from_mozpp(line)
    report(r)
    # photo reaction with alias
    line = "[jtepomuc->,.10*jno2] TEPOMUC + hv -> .5*CH3CO3 + HO2 + 1.5*CO  !    MCM also has reactions with OH, O3, NO3"
    r = Reaction.from_mozpp(line)
    report(r)


def test_kpp_input():
    # simple equation
    line = "<R529>  OH + RA13OOH = CARB3 + UDCARB8 + OH 	:	9.77E-11	;"
    r = Reaction.from_kpp(line)
    report(r)
    # another one with an elaborate kterm and spaces/tabs removed
    line = "<R2>  O = O3:6.00E-34*O2*O2*((TEMP/300)**-2.6);"
    r = Reaction.from_kpp(line)
    report(r)
    # simple equation in MECCA format
    line = "<G7301>  BrO  + NO       = Br  + NO2      : {%StTrGNBr}  8.7E-12{§§0.1}*EXP(260./temp); {&1845}"
    r = Reaction.from_kpp(line)
    report(r)
    # a wild one
    line = "<G7402a> BrO  + CH3O2    = HOBr + HCHO      : {%TrGBr}   G7402a_yield*5.7E-12{§1.11}{5.7+-0.6}; {&822}"
    r = Reaction.from_kpp(line)
    report(r)
    # a really long one with plenty of yields
    line = "<G4544>  LHC4ACCHO  + O3  = .2225 CH3CO3 + .89 CO + .0171875 HOCH2CO2H + .075625 H2O2 + .0171875 HCOCO2H + .2775 ACETOL + .6675 HO2 + .2603125 GLYOX + .2225 HCHO + .89 OH + .2603125 HOCH2CHO + .5 MGLYOX : {%TrGC} 2.40E-17{§}; {&2419}"
    r = Reaction.from_kpp(line)
    report(r)
    # a line with M
    line = "<G4302>  C3H6 {+M}   + OH  = HYPROPO2                                        : {%TrGC}  k_3rd(temp,cair,8.E-27,3.5,3.E-11,0.,0.5){§}; {&1207}"
    r = Reaction.from_kpp(line)
    report(r)
    # and one with +O2
    line = "<G4210>  CH3CO2H + OH {+O2}= CH3O2  + CO2 + H2O : {%TrGC}  4.2E-14{§§0.15}*EXP(855./temp); {&1759}"
    r = Reaction.from_kpp(line)
    report(r)
    # photo reaction
    line = "<J3104a> N2O5    + hv = NO2 + NO3  : {%StTrGNJ} jx(ip_N2O5){§}; {&&}"
    r = Reaction.from_kpp(line)
    report(r)
    # photo reaction with alias j value
    line = "<J4300>  IC3H7OOH    + hv = CH3COCH3 + HO2 + OH      : {%TrGCJ}  jx(ip_CH3OOH){§};"
    r = Reaction.from_kpp(line)
    report(r)
    # and another one with a weird kterm
    line = "<J4307>  NOA         + hv = CH3CO3 + HCHO + NO2      : {%TrGCJ}  J_IC3H7NO3+jx(ip_CH3COCH3){§}; {&&}"
    r = Reaction.from_kpp(line)
    report(r)
    

if __name__ == "__main__":
    import speciestable as st
    t = st.speciesTable.from_csv()
    models = t.get_model_names()
    line = "ENEO2 + NO -> CH3CHO + .5*CH2O + .5*CH3COCH3 + HO2 + NO2 : 4.2e-12*exp(180/T)"
    r = Reaction.from_mech(line)
    print r.to_mech()
    for m in models:
        undef = r.undefined_compounds(m, t)
        print "Undefined species in model %s: %s"%(m, ", ".join(undef) if len(undef)>0 else "None")
        if len(undef) == 0:
            r.check_mass(m, t, ignore_o2=False)
    
# create new test files
    with open(testfile_csv, "w") as f:
        f.close()
    with open(testfile_easy, "w") as f:
        f.close()
    with open(testfile_kpp, "w") as f:
        f.write("// testfile created %s\n"%(dt.datetime.now().isoformat()))
        f.close()
    with open(testfile_mech, "w") as f:
        f.write("! testfile created %s\n"%(dt.datetime.now().isoformat()))
        f.close()
    with open(testfile_mozpp, "w") as f:
        f.write("! testfile created %s\n"%(dt.datetime.now().isoformat()))
        f.close()

#    test_csv_input()
    test_kpp_input()
    test_mozpp_input()
    test_mech_input()
