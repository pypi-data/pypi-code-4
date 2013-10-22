from nams import chirality

#alternatively the inchi notation can be used with input_type="inchi"
line_notation="C([C@@H](C(=O)O)N)S"
input_type="smi"

#classification of the type of chirality
chir=chirality.Chirality(line_notation, input_type)

#the output atom IDs will be relative to the canonical SMILES
print chir.can_smi

for atom_id in range(chir.n_atoms):
    #1 -> R; -1 -> S; 0 -> none.
    print chir.get_chirality(atom_id)
