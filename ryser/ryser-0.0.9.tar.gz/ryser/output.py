# Copyright Matthew Henderson 2013.
# Last updated Mon Mar 25 16:31:47 GMT 2013.

from ryser.utils import cell

def row_string(fixed, size, row, col_sep='|', padding=0):
    """
    Converts a dict of fixed cells to a string.

    fixed - a cell-symbol dictionary
    size - the dimension of the PLS
    row - the row to convert to a string
    col_sep - a string used as a separator between columns
    padding - number of spaces either side of a symbol
    """
    s = col_sep
    for col in range(size):
        symbol = fixed.get(cell(row, col, size))
        if symbol:
            s += ' '*padding + str(symbol)
        else:
            s += ' '*padding + '.'   
        s += col_sep
    return s

def dict_to_string(fixed, size, col_sep = '', row_sep = '', padding = 0, top = '', bottom = ''):
    """
    Returns a puzzle string of dimension 'boxsize' from a dictionary of 
    'fixed' cells.
    
    padding : number of spaces between adjacent symbols
    row_end : a string added to the last symbol of every row 
    col_sep : a string added to the last symbol of every column
    
    """
    rows = range(size)
    s = top
    for row in rows[:-1]:
        s += row_string(fixed, size, row, col_sep, padding)
        s += row_sep
    s += row_string(fixed, size, rows[size-1], col_sep, padding)
    s += ' '*padding
    s += bottom
    return s

def dict_to_string_simple(fixed, size):
    return dict_to_string(fixed, size, col_sep = '|', row_sep = '\n', padding = 0, top = '', bottom = '')


