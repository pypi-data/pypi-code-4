
"""
The NAMS python package calculates the similarity between molecules based on the 
structural/topological relationships of each atom towards all the others 
within a molecule.

This program is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published on the official site of Open Source Initiative
and attached above.

Copyright (C) 2013, Andre Falcao and Ana Teixeira, University of Lisbon - LaSIGE

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Please cite the authors in any work or product based on this material:

AL Teixeira, AO Falcao. 2013. A non-contiguous atom matching structural similarity function. J. Chem. Inf. Model. DOI: 10.1021/ci400324u.


"""
import pybel, openbabel
import sys
from munkres import Munkres, print_matrix
from heuristic import Heuristic
from chirality import Chirality
from doubleb_e_z import Stereodoubleb
from math import sqrt
import os

data_path = os.path.join(os.path.dirname(__file__),'data')

class Nams:

    # 1. process the molecular bond information for one molecule
    # 2. compare 2 molecules
    def read_dists(self, fname):
        dists={}
        fil=open(fname, "rt")
        lins=fil.readlines()
        fil.close()
        lin=lins[0].strip()
        elems=lin.split("\t")
        row=0
        for lin in lins[1:]:
            stuff=lin.split("\t")
            col=0
            row=int(stuff[0])
            for s in stuff[1:]:
                dists[(row, int(elems[col]))]= float(s)
                col+=1
        return dists
    
    def read_dists_default(fname):
        dists={}
        fil=open(fname, "rt")
        lins=fil.readlines()
        fil.close()
        lin=lins[0].strip()
        elems=lin.split("\t")
        row=0
        for lin in lins[1:]:
            stuff=lin.split("\t")
            col=0
            row=int(stuff[0])
            for s in stuff[1:]:
                dists[(row, int(elems[col]))]= float(s)
                col+=1
        return dists    
    #Default parameters
    BS_ALPHA = 2.0

    ANRINGS_FAC=0.8      #number of rings an atom belongs to
    ACHIR_FAC = 0.95     #chiral atom
    DBSTEREO_FAC = 0.95  #double bond stereo
    BRING_FAC = 0.9      #bond in ring
    BAROM_FAC = 0.9      #bond aromaticity
    BORDER_FAC = 0.9     #bond order
    PEN = -0.2
    bond_assigner = Heuristic()
    h_experimental=True
    fname=os.path.join(data_path,'nelems_dist3.txt')
    ELEMS_DISTS = read_dists_default(fname)
    
    def __init__(self, params=[]):
        if len(params)>0:
            self.set_params(params)
        self.bond_assigner = Heuristic()


    def set_bond_assigner(self, method):
        if method=="HEURISTIC":
            self.bond_assigner = Heuristic()
        else:
            self.bond_assigner = Munkres()

    def set_params(self, params):
        self.BS_ALPHA = params[0]
        self.ACHIR_FAC = params[1] 
        self.BRING_FAC = params[2]
        self.BAROM_FAC = params[3]
        self.BORDER_FAC = params[4]
        self.PEN =  params[5]
        self.DBSTEREO_FAC = params[6]
        self.ELEMS_DISTS = params[7]

    def set_elems_dists(self, distm):
        if distm == 0:
            fname=os.path.join(data_path,'nelems_dist0.txt')
        elif distm == 1:
            fname=os.path.join(data_path,'nelems_dist1.txt')
        elif distm == 2:
            fname=os.path.join(data_path,'nelems_dist2.txt')
        elif distm == 3:
            fname=os.path.join(data_path,'nelems_dist3.txt')
        elif distm == 4:
            fname=os.path.join(data_path,'nelems_dist4.txt')
        else:
            fname=os.path.join(data_path,'nelems_dist3.txt')
            
        self.ELEMS_DISTS = self.read_dists(fname)

    def get_num_rings(self, mol, atom):
        #counts the number of rings an atom belongs to
        cont_rings = 0
        for ring in mol.GetSSSR():
            if ring.IsMember(atom):
                cont_rings += 1
        
        return cont_rings



    def process_bonds(self, start_set, all_bonds, n_big_atoms, elliminated, lvl_bonds):
        #the idea is to select all the immediate bonds in the start set
        # append them to the current level_bonds and elliminate them from the connection matrix
        to_follow={}
        for at1 in start_set:
            for at2 in all_bonds[at1]:
                if (at1, at2) not in elliminated:
                    my_bond=(at1, at2)
                                  
                    lvl_bonds[-1].append(my_bond)
                    
                    if at2<n_big_atoms: to_follow.setdefault(at2,1)
                    elliminated.append((at1,at2))
                    elliminated.append((at2,at1))
        # now pick up the new nodes (from the bonds) and create a new start set
        #process recursively until no more nodes are extant to process
        #the recursion proceeds at most as many times as the total length of the graph 
        new_starts=to_follow.keys()

        if len(new_starts)>0:
            lvl_bonds.append([])
            self.process_bonds(new_starts, all_bonds, n_big_atoms, elliminated, lvl_bonds)
                

    def comp_bonds(self, bnd1, bnd2):

        #this should output a SIMILARITY between bonds
        numb11, nrings11, chir11, numb12, nrings12, chir12, inring1, arom1, order1, dbstereo1 = bnd1
        numb21, nrings21, chir21, numb22, nrings22, chir22, inring2, arom2, order2, dbstereo2 = bnd2

        simil=1.0
        simil *= (1-self.ELEMS_DISTS[(numb11, numb21)])
        simil *= (1-self.ELEMS_DISTS[(numb12, numb22)])
        if int(chir11*chir21)==-1: simil *= self.ACHIR_FAC
        if int(chir12*chir22)==-1: simil *= self.ACHIR_FAC
        simil *= (1.0 - abs(nrings11-nrings21)*self.ANRINGS_FAC/4.0)
        simil *= (1.0 - abs(nrings12-nrings22)*self.ANRINGS_FAC/4.0)
            
        if inring1!= inring2: simil *= self.BRING_FAC
        if arom1  != arom2: simil   *= self.BAROM_FAC
        if order1 != order2: simil  *= self.BORDER_FAC
        if int(dbstereo1 * dbstereo2) == -1: simil *= self.DBSTEREO_FAC
        
        return 2*simil-1.0 



    def comp_atoms_new(self,bonds1, bonds2, sims, LMAT):
        #receives the indices and levels of the bondtypes and levels for 2 atoms
        #as well as the similarity matrix between ALL bondtypes
        #Returns the similarity between 2 atoms
        
        m = self.bond_assigner #heuristic or munkres!
        score=0
        if self.h_experimental==True:
            sims_list=[]
            siz=len(bonds2)
            row=0
            threshold=0 #self.PEN/2.0
            for id1, L1 in bonds1:
                col=0
                for id2, L2 in bonds2:
                    sim= sims[id1][id2]*LMAT[L1][L2]
                    if sim>threshold:  #the THRESHOLD SPEEDUP APPROACH
                        sims_list.append((-sim, row, col)) 
                    col += 1
                row+=1
                
            n_indexes=col-1
            if n_indexes> row-1: n_indexes=row-1
            sum_sims, indexes = m.compute_experimental(sims_list, n_indexes)
            rows=[]
            cols=[]
            for row, col in indexes:
                rows.append(row)
                cols.append(col)
        else:        
            matrix=[]
            sims_list=[]
            siz=len(bonds2)
            row=0
            for id1, L1 in bonds1:
                a_row=[0]*siz
                col=0
                for id2, L2 in bonds2:
                    sim= sims[id1][id2]*LMAT[L1][L2]
                    a_row[col]=-sim
                    col += 1
                matrix.append(a_row)
                row+=1
                
            indexes = m.compute(matrix)
            sum_sims = 0
            rows=[]
            cols=[]
            for row, col in indexes:
                sum_sims -= matrix[row][col]
                rows.append(row)
                cols.append(col)
        #end of calculating the optimal bond matching

        #penalties -> Add the penalties for each bond that did not fit, weighted accoriding to its level
        pens=0
        row=0
        for bond in bonds1:
            if row not in rows: pens+=self.PEN/((bond[1]+1)**self.BS_ALPHA)
            row+=1
        col=0
        for bond in bonds2:
            if col not in cols: pens+=self.PEN/((bond[1]+1)**self.BS_ALPHA)
            col+=1

        score=sum_sims + pens              
        return score

    def calc_btypes(self, mol_info):
        # get the existing bondtypes from a mol_info
        # output a dictionary with the bond types
        #     and the mol info redesigned for the bond types which can then be forgotten
        btypes={}
        nbonds={}
        idx=0
        for at in mol_info:
            lvls = mol_info[at]
            nbonds[at]=[]
            L=0
            for lvl in lvls:
                for bond in lvl:
                    if bond not in btypes:
                        btypes[bond]=idx
                        nbonds[at].append((idx, L))
                        idx+=1
                    else:
                        nbonds[at].append((btypes[bond], L))
                L+=1
        return btypes, nbonds

    def get_bond_type_sims(self, btypes1, btypes2):
        #calculates the similarty between 2 bond types of different molecules
        #returns the similarity matrix between each

        matrix=[]
        siz_row=len(btypes2)
        for bnd1 in btypes1:
            row=[0]*siz_row
            matrix.append(row)

        for bnd1 in btypes1:
            for bnd2 in btypes2:
                matrix[btypes1[bnd1]][btypes2[bnd2]]=self.comp_bonds(bnd1, bnd2)
        return matrix

    def calc_level_matrix(self, nbonds1, nbonds2):
        max_l1=0
        max_l2=0
        for at1 in nbonds1:
            bnds1 = nbonds1[at1]
            for id1, L1 in bnds1:
                if L1>max_l1: max_l1=L1
            
        for at2 in nbonds2:
            bnds2 = nbonds2[at2]
            for id2, L2 in bnds2:
                if L2>max_l2: max_l2=L2

        lev_mat=[]
        for L1 in xrange(max_l1+1):
            row=[]
            for L2 in xrange(max_l2+1): row.append(1.0/((abs(L1-L2)+max(L1,L2)+1.0)**self.BS_ALPHA))
            lev_mat.append(row)
        return lev_mat

    

    def get_similarity_matrix(self, mol_info1, mol_info2, verbose):
        #gets 2 molecules with all the bonds in all levels for all atoms
        #and computes a distance checking how many correspondences there are
        #for each atomr pair.
        #uses a decay function:decay = 1/level - The highest the level, the lowest the imporance
        # mol_dinfo is a dictionary of list of dictionaries, one element for each atom
        # mol_info={atom1: [ {bond1:ntimes, bond2: ntimes, ...}, { ...} ], atom2
        # dic of atoms         list of levels  dic of bonds

        mi1=mol_info1
        mi2=mol_info2
        
        #first make the matrix
        siz1=len(mi1)
        siz2=len(mi2)
        matrix=[]
        for row in range(siz1):matrix.append([0]*siz2)

        #calculate bond_types for each molecule
        btypes1, nbonds1=self.calc_btypes(mi1)
        btypes2, nbonds2=self.calc_btypes(mi2)
        #evaluate
        sims=self.get_bond_type_sims(btypes1, btypes2)
        #compute the matrix for all LEvels
        LMAT=self.calc_level_matrix(nbonds1, nbonds2)

                                 
        # now for each atom pair, get the similarity
        row=0
        v=0
        for at1 in nbonds1:
            bnds1 = nbonds1[at1]
            col=0
            for at2 in nbonds2:
                bnds2 = nbonds2[at2]
                matrix[row][col]=- self.comp_atoms_new(bnds1, bnds2, sims, LMAT) #negative values as this function returns a similarity
                if verbose==True: sys.stdout.write("%7.2f" % -matrix[row][col])
                col+=1
            if verbose==True: sys.stdout.write("\n")
            row+=1
        return matrix        

    def calc_optimal_matching(self, matrix):
        m = Munkres()
        indexes = m.compute(matrix)
        return indexes        

    def calc_similarity(self, matrix, indexes):
        total = 0
        my_indices={}
        for row, column in indexes:
            value = -matrix[row][column]
            if value>0: 
                total += value
                my_indices[(row+1, column+1)]=value
        return total, my_indices


    def get_similarity(self, mol_info1, mol_info2, verbose=False):

        #first make the distance (similarity) matrix
        matrix =self.get_similarity_matrix(mol_info1, mol_info2, verbose)

        # get the best attribution using the hungarian method!!!!
        indices=self.calc_optimal_matching(matrix)

        #get the similarities and return them
        return self.calc_similarity(matrix, indices)

    def get_distance(self, mol_info1, mol_info2, verbose=False):
        #this actually computes the distance between molecules

        #first compute the similarities among themselves
        sim11, inds11=self.get_similarity(mol_info1, mol_info1, False)
        sim22, inds22=self.get_similarity(mol_info2, mol_info2, False)
        #now compute the similarity between the 2 molecules
        sim12, inds12=self.get_similarity(mol_info1, mol_info2, verbose)

        #now compute the distance = sqrt(sim11+sim22-2*sim12)
        dist12=sqrt(sim11+sim22-2*sim12)
        return dist12, inds12

    def eval_solution(self, mol_info1, mol_info2, matches, verbose=False):
        #this method evaluats a solution provided by the user

        #first make the similarity matrix as usual
        matrix =self.get_similarity_matrix(mol_info1, mol_info2, verbose)        


        #get the distances and return them
        total, my_indices = self.calc_similarity(matrix, matches)
        return total, my_indices


    def get_bonds(self, mol, atom_id):
        #for a given atom in a molecule find the bonds
        natoms=len(mol.atoms)
        bonds=[]
        obatom=mol.atoms[atom_id].OBAtom
        id1=obatom.GetIndex()
        t1=obatom.GetType()
        for n_atom in openbabel.OBAtomAtomIter(obatom):
            id2 = n_atom.GetIndex()
            t2=n_atom.GetType()
            bond = obatom.GetBond(n_atom)
            bonds.append((id1, id2, bond.GetBondOrder()))
        return bonds


    def get_bonds2(self, mol, atom_id):
        #for a given atom in a molecule find the bonds
        natoms=mol.NumAtoms()
        bonds=[]
        obatom = mol.GetAtom(atom_id)
        id1 = obatom.GetIndex()
        t1 = obatom.GetType()
        for n_atom in openbabel.OBAtomAtomIter(obatom):
            id2 = n_atom.GetIndex()
            t2=n_atom.GetType()
            bond = obatom.GetBond(n_atom)
            bonds.append((id1+1, id2+1))
        return bonds


    def get_mol_info(self, typ, mol_str, hydros=False):
        obConversion = openbabel.OBConversion()
        if obConversion.SetInAndOutFormats(typ, "can"):
            mol = openbabel.OBMol()
            if obConversion.ReadString(mol, mol_str):
                n_big_atoms_1 = mol.NumAtoms()
                mol.StripSalts()
                n_big_atoms = mol.NumAtoms()
                if n_big_atoms_1 > n_big_atoms:
                    print "Warning: Disconnected structures were removed. "
                can_smi = obConversion.WriteString(mol)
           
                
                #use canonical smiles ONLY!!!
                mol = pybel.readstring("smi", can_smi)
                obmol=mol.OBMol
                n_big_atoms = len(mol.atoms)

                #this is the chirality/double bond stereo stuff (both work with explicit Hs)
                chir=Chirality(can_smi, "can")
                dbstereo=Stereodoubleb(can_smi, "can")
                       
                if hydros==True: obmol.AddHydrogens()
                n_tot_atoms=obmol.NumAtoms()
                all_bonds={}
                mol_info={}
                mol_atoms=[]
                
                if n_tot_atoms > 2:
                #start up the connection matrix as a dictionary of dictionaries (sparse matrix)
                
                    for atom_id in range(n_tot_atoms):
                        ida=atom_id+1
                        atm=obmol.GetAtom(ida)
                        if atom_id<n_big_atoms: the_chir=chir.get_chirality(atom_id)
                        else: the_chir=0
                        mol_atoms.append((atm, atm.GetAtomicNum(), self.get_num_rings(obmol,atm), the_chir))
                        bonds = self.get_bonds2(obmol, atom_id+1)
                        for b in bonds:
                            all_bonds.setdefault(b[0], {})[b[1]]=1   #b[2]
                            all_bonds.setdefault(b[1], {})[b[0]]=1   #b[2]
                    #for each BIG atom in the molecule compute the bonds according to their separation levels 
                    for atom_id in range(1,n_big_atoms+1):
                        elliminated=[]
                        lvl_bonds=[[]]
                        lvl=0
                        start_set=[atom_id]
                        #get all the bonds for each separation level
                        self.process_bonds(start_set, all_bonds, n_tot_atoms, elliminated, lvl_bonds)
                        #for some weird reason the last level is always empty so take it out
                        #for lvl in lvl_bonds: print lvl
                        lvl_bonds=lvl_bonds[:-1]
                        the_bonds=[]
                        for level in lvl_bonds:
                            the_bonds.append([])
                            for at1, at2 in level:
                                ai1, ai2=at1-1, at2-1
                                a1 = mol_atoms[ai1][0]
                                a2 = mol_atoms[ai2][0]
                                
                                bnd12 = a1.GetBond(a2)
                                #get double bond stereoisomerism
                                dbstereo12 = dbstereo.get_e_z_at(a1, a2)
                                if bnd12.IsAromatic():
                                    my_bond=(mol_atoms[ai1][1], mol_atoms[ai1][2], mol_atoms[ai1][3],
                                             mol_atoms[ai2][1], mol_atoms[ai2][2], mol_atoms[ai2][3],
                                             bnd12.IsInRing(),bnd12.IsAromatic(), 1.5, dbstereo12) 
                                else:
                                    my_bond=(mol_atoms[ai1][1], mol_atoms[ai1][2], mol_atoms[ai1][3],
                                             mol_atoms[ai2][1], mol_atoms[ai2][2], mol_atoms[ai2][3],
                                             bnd12.IsInRing(),False, bnd12.GetBondOrder(), dbstereo12)  

                                
                                the_bonds[-1].append(my_bond)
                                
                        mol_info[atom_id]=the_bonds

                    return mol, mol_info
                else:
                    print "Error 3: NAMS cannot be applied to molecules with less than 3 atoms (including hydrogen atoms)."
            else:
                print "Error 2: Invalid molecule or correspondence between the molecule and input format."                
        else:
            print "Error 1: Invalid molecule format. Please check here http://openbabel.org/docs/2.3.1/FileFormats/Overview.html the supported formats and respective names/codes"
            
