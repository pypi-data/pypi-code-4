

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


from time import time

# a faster heuristic for solving the assignment problem
# for COST matrices


class Heuristic:
    def __init__(self):
        pass
    def compute_experimental(self,a_list, n_indexes):
        a_list.sort()
        bad_rows={}
        bad_cols={}
        indexes=[]
        best_pos=0
        siz=len(a_list)
        c_idx=0
        result=0
        while c_idx<n_indexes and best_pos < siz:
            sim, brow, bcol=a_list[best_pos]
            if brow not in bad_rows:
                if bcol not in bad_cols:
                    #bad_rows.append(brow)
                    #bad_cols.append(bcol)
                    bad_rows[brow]=1
                    bad_cols[bcol]=1
                    indexes.append((brow,bcol))
                    result+=-sim
                    c_idx+=1
            best_pos+=1


        indexes.sort()
        return result, indexes


    def compute(self,mat):
        t1=time()
	cost_mat=[]
	for row in mat: cost_mat.append(row[:])
        nrows=len(mat)
        ncols=len(mat[0])
        indexes=[]
        the_min=min(ncols, nrows)
        highrow=[1e33]*ncols

        nrows=len(cost_mat)
        the_rows=range(nrows)

        ncols=len(cost_mat[0])
        the_cols=range(ncols)

        while len(indexes)<the_min:
            best=1e34
            #first identify the best row
            r=0
            for nrow in the_rows:
                row=cost_mat[nrow]
                row_min=min(row)
                if row_min<best:
                    best=row_min
                    brow=nrow
                    bpos=r  #row position of the best in the the_rows array
                r+=1
            #now search the col
            bcol=the_cols[0]
            cpos=0 #col position
            #bcol=0
            while cost_mat[brow][bcol]>best: #bcol+=1
                cpos+=1
                bcol=the_cols[cpos]
            idx= (brow,bcol)
            indexes.append(idx)

            cost_mat[brow]=highrow
            del the_rows[bpos]

            for row in cost_mat: row[bcol]=1e33
            del the_cols[cpos]

        indexes.sort()
        return indexes
    
    def compute_oldest(self,mat):
	self.cost_mat=[]
	for row in mat: self.cost_mat.append(row[:])
        self.nrows=len(mat)
        self.ncols=len(mat[0])
        indexes=[]
        the_min=min(self.ncols, self.nrows)
        while len(indexes)<the_min:
            idx=self.get_index()
            indexes.append(idx)
            self.delete_row(idx[0])
            self.delete_col(idx[1])
        indexes.sort()
        return indexes

    def get_index(self):
        best=1e34
        r=0
        #first identify the best row
        for row in self.cost_mat:
            the_min=min(row)
            if the_min<best:
                best=the_min
                brow=r
            r += 1
        #now search the col
        c=0
        for v in self.cost_mat[brow]:
            if v==best: return (brow,c)
            c+=1
        #we should NEVER get here!
        return "ERRO!"

    def delete_row(self, row):
        # not actual deletion, we just replace the row with  high values
        highrow=[1e33]*self.ncols
        self.cost_mat[row]=highrow
    
    def delete_col(self, col):
        # not actual deletion, we just replace the col values with high values
        for row in self.cost_mat:
            row[col]=1e33


            
if __name__ == '__main__':
    
    costMatrix = [
		[62,75,80,93,95,97, 45],
		[75,80,82,85,71,97, 64],
		[80,75,81,98,90,97, 73],
		[78,82,84,80,50,98, 64],
		[90,85,85,80,85,99, 56],
		[65,75,80,75,68,96, 82]]
    h=Heuristic()
    idx=h.compute(costMatrix)

    vfinal=0
    for r,c in idx: vfinal+= costMatrix[r][c]
    print "heuristic-->", idx, vfinal

    from munkres import Munkres
    m = Munkres()
    idx = m.compute(costMatrix)

    vfinal=0        
    for r,c in idx: vfinal+= costMatrix[r][c]
    print "munkres-->", idx, vfinal




  
