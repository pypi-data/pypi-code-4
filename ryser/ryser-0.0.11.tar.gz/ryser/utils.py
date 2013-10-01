import csv

# Below, 'size' is the dimension of a latin square.
# Rows and columns are labelled: 0, 1, ... , size - 1
# Cells are labelled: 1, 2, ... , size^2

def cell(row, column, size):
    """The label of the cell in position (row, col)."""
    return (row * size) + column + 1

def row(cell, size): 
    """The row label of the row in a square of dimension 'size'
    containing the cell with label 'cell'."""
    return int((cell - 1)/size) 

def col(cell, size): 
    """The column label of the column in a square of dimension 'size'
    containing the cell with label 'cell'."""
    return (cell - 1) % size

def row_r(cell, size): 
    """A range of all labels of cells in the same row as 'cell'."""
    return range(row(cell, size)*size + 1, (row(cell, size) + 1)*size + 1)

def col_r(cell, size): 
    """A range of all labels of cells in the same column as 'cell'."""
    return range(col(cell, size) + 1, size**2 + 1, size)

def vertex(cell, size):
    """The row and column labels of 'cell', as a pair."""
    return (row(cell, size), col(cell, size))

def rect_r(tl, br, size):
    """A rectangular range which extends from tl in the top-left to br in the
    bottom right."""
    (i,j) = vertex(tl, size)
    (k,l) = vertex(br, size)
    cells = [(x, y) for x in range(i, k + 1) for y in range(j, l + 1)]
    return map(lambda x: cell(x[0], x[1], size), cells)

def list_assignment(partial_latin_square, size):
    """The (canonical) list assignment for a partial latin square. The list of
    a filled cell is the list containing just the element in that cell. The
    list of an empty cell contains only those symbols not already used in the
    same row and column as that cell."""
    P = partial_latin_square
    L = {}
    # initialise lists
    for i in range(1, size**2 + 1):
        if i in P.keys():
            L[row(i,size),col(i,size)] = [P[i]]
        else:
            L[row(i,size),col(i,size)] = range(1, size + 1)
    # update lists (remove used symbols from lists of same row/col)
    for i in range(1, size**2 + 1):
        if i in P.keys():
            # then remove P[i] from any list of a cell not in P from the same row/col
            for j in row_r(i, size) + col_r(i, size):
                if j not in P.keys():
                    if P[i] in L[row(j, size), col(j, size)]:
                        L[row(j, size), col(j, size)].remove(P[i])
    return L

def orthogonal_array(L, size):
    return [(i,j,L[i,j]) for i,j in range(size)]

def from_file(source, size):
    reader = csv.DictReader(filter(lambda row: row[0]!='#', source), range(size), delimiter=' ')
    row_list = []
    for row in reader:
        row_list.append(row)
    return row_list

def alt(P, size):
    """Fixed cells from a list colouring.

    Convert a symbols-to-(row,col) pairs dictionary to a cell-label-to-symbol
    dictionary.
    """
    L = {}
    for i in P:
        for j in P[i]:
            row = j[0]
            column = j[1]
            L[cell(row, column, size)] = int(i)
    return L

def alt2(P, size):
    """Fixed cells from a list of row dictionaries.

    Convert a list of column-labels-to-symbols dictionaries to a
    cell-label-to-symbol dictionary.
    """
    L = {}
    for i in range(len(P)):
        for j in P[i]:
            if P[i][j] != '.':
                row = i
                col = j
                L[cell(row, col, size)] = int(P[i][j])
    return L

