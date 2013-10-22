from nams import doubleb_e_z

#alternatively the inchi notation ca be used with input_type="inchi"
line_notation="I/C=C/Cl"
input_type="smi"

#classification of the type of double bond stereoisomerism
stereo=doubleb_e_z.Stereodoubleb(line_notation, input_type)

#the output bond IDs will be relative to the canonical SMILES
print stereo.can_smi

#using bond indexes (including bonds to hydrogen atoms):
for bond_id in range(stereo.n_bonds):
    #1 -> Z; -1 -> E; 0 -> none. 
    print stereo.get_e_z_bond(bond_id)

#alternatively the atom indexes can be used:
#stereo.get_e_z_at(at1, at2)
