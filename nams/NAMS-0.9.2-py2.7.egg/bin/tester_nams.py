from nams import nams
import os
import openbabel
import pybel

data_path = os.path.join(os.path.dirname(nams.__file__),'data')


def test_list(mfile, mtype, ms, hs, nelems_m):
    import time
    fil=open(mfile, "rt")
    file_name1 = "sim_matrix_nelems="+str(nelems_m)+"_"+str(ms.BS_ALPHA)+"_aring="+str(ms.ANRINGS_FAC)+"_chir="+str(ms.ACHIR_FAC)+"_dbstereo="+str(ms.DBSTEREO_FAC)+"_bring="+str(ms.BRING_FAC)+"_barom="+str(ms.BAROM_FAC)+"_border="+str(ms.BORDER_FAC)+"_pen="+str(ms.PEN)+"_H="+str(hs)+".txt"
    fout=open(file_name1, "wt")
    file_name2 = "tanimoto_matrix_nelems="+str(nelems_m)+"_"+str(ms.BS_ALPHA)+"_aring="+str(ms.ANRINGS_FAC)+"_chir="+str(ms.ACHIR_FAC)+"_dbstereo="+str(ms.DBSTEREO_FAC)+"_bring="+str(ms.BRING_FAC)+"_barom="+str(ms.BAROM_FAC)+"_border="+str(ms.BORDER_FAC)+"_pen="+str(ms.PEN)+"_H="+str(hs)+".txt"
    fout_t=open(file_name2, "wt")
    lins=fil.readlines()
    fil.close()
    molecs=[]
    print "reading and processing data"
    count=1
    t1=time.time()
    tinit=t1
    for lin in lins[0:]:
        molf, mol_id=lin.split("\t")
        mol_id = mol_id.strip()     
        if pybel.readstring(mtype,molf):
            mol=pybel.readstring(mtype,molf)
            if hs == True: mol.addh()
            natoms=len(mol.atoms)
            can_smi = mol.write("can")
            print "\t", count, mol_id, can_smi.strip()
            #Extract molecular information
            if natoms > 2:
                mol1, mol_info = ms.get_mol_info("can", can_smi, hs)
                molecs.append((mol_id, mol1, mol_info))
                count +=1
            else:
                print "Warning: NAMS cannot be applied to molecules with less than 3 atoms (including hydrogen atoms). I am skipping this molecule...."
        else:
           print "Warning: invalid molecule, input format or correspondence between the molecule and input format.. I am skipping this molecule...." 
    t2=time.time()
    print "TIME SPENT", t2-tinit
    t1=t2
    dmat={}
    #write headers and calc self_similarities
    print "write headers and calc self_similarities"
    s="      "
    i=1
    tinit=t2
    for m in range(len(molecs)):
        s+="%s " % molecs[m][0]
        #compute self similarities
        sim, d_atoms = ms.get_similarity(molecs[m][2], molecs[m][2], False)
        t2=time.time()
        print "\t%5s %8.3f %8.3f %8.3f" % (molecs[m][0], sim, t2-t1, (t2-tinit)/i)
        t1=t2
        dmat[(m,m)]=sim
        i+=1
        
    s+="\n"
    t = s
    print "calc similarities..."
    tinit=t2
    i=1
    for m1 in range(1,len(molecs)):
        for m2 in range(m1):
            # calculate similarities
            sim12, d_atoms = ms.get_similarity(molecs[m1][2], molecs[m2][2], False) #, mol1.atoms, mol2.atoms)
            dmat[(m1,m2)]=sim12
            dmat[(m2,m1)]=sim12
            i+=1
        t2=time.time()
        print "\t%5s %8.3f %8.3f %8.3f" % (molecs[m1][0], sim, t2-t1, (t2-tinit)/i)
        t1=t2
    print "TIME SPENT", t2-tinit
    print "WRITING FILE"
    #write matrix
    fout.write(s)
    fout_t.write(t)
    for m1 in range(len(molecs)):
        s = "%-s" % molecs[m1][0]
        t = "%-s" % molecs[m1][0]
        for m2 in range(len(molecs)):
            tanimoto=dmat[(m1,m2)]/(dmat[(m1,m1)]+dmat[(m2,m2)] - dmat[(m1,m2)])
            s += "%7.3f" % dmat[(m1,m2)]
            t += "%7.3f" % tanimoto
        s += "\n"
        t += "\n"
        fout.write(s)
        fout_t.write(t)
    fout.close()
    fout_t.close()
    print "DONE!"                


#Define NAMS parameters

ms=nams.Nams()
ms.BS_ALPHA = 2.0 #importance of the bond distance to an atom
ms.ANRINGS_FAC = 0.8   #number of rings an atom belongs to
ms.ACHIR_FAC = 0.95     #chiral atom
ms.DBSTEREO_FAC = 0.95  #double bond stereo
ms.BRING_FAC = 0.9     #bond in ring
ms.BAROM_FAC = 0.9     #bond aromaticity
ms.BORDER_FAC = 0.8    #bond order
ms.PEN = -0.2   #penalty

#5 atom substitution matrixes are available: 0, 1, 2, 3, 4 as defined in http://nams.lasige.di.fc.ul.pt/help.php#params
nelems_m=3
ms.set_elems_dists(nelems_m)
#for the bond assignment, munkres algorithm can also be used: ms.set_bond_assigner("MUNKRES")
ms.set_bond_assigner("HEURISTIC")
#Include hydrogens: True or False
h_experimental=True

#######Test a list of molecules
#file with mols: mol \t id
mfile=os.path.join(data_path,'HC_100.smi')
mtype="smi"
test_list(mfile, mtype, ms, h_experimental, nelems_m)

