from nams import nams

#Create a nams object
ms=nams.Nams()

#Define 2 molecules: (molecular_representation_type, molecular_representation) 
mol_t1= ("smi", "CCC(=O)C(c1ccccc1)c2ccccc2")
mol_t2= ("smi", "O=C(CC)N(c1ccncc1)c3ccccc3")

#Extract the set of characteristics of the atoms/bonds 
mol1, mol_info1 = ms.get_mol_info(mol_t1[0],mol_t1[1])
mol2, mol_info2 = ms.get_mol_info(mol_t2[0],mol_t2[1])

#Calculate the similarity between the pair of molecules
sim11, d_atoms = ms.get_similarity(mol_info1, mol_info1) 
sim22, d_atoms = ms.get_similarity(mol_info2, mol_info2)
sim12, d_atoms = ms.get_similarity(mol_info1, mol_info2)

#Print self and pairwise similarity
print "Self similarity 1: %6.2f" % sim11
print "Self similarity 2: %6.2f" % sim22
print "Total similarity: %6.2f -> Jaccard: %6.3f" % (sim12, sim12/(sim11+ sim22 -sim12))

ks=d_atoms.keys()
ks.sort()

#Print the atomic alignment between the molecules and its similarity score
for k in ks:
    print "\t%5d (%3s)  -%3d  (%3s) --> %6.2f" % (k[0], mol1.atoms[k[0]-1].OBAtom.GetType(),
                                                      k[1], mol2.atoms[k[1]-1].OBAtom.GetType(),
                                                      d_atoms[k])
