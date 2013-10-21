__author__ = 'alexey.grachev'

import types
import math
def safe(item):
    return item if item else ''
def safelen(item):
    return len(str(item)) if item else 0

def print_table_row(row, top_border=False, bottom_border=False):
    """Prints columns of a single table row with ascii cell seperator and
    an optional top and/or bottom border line.
    """
    result = str()
    cc = "+"
    """corner char"""
    hc = "-"
    """horizontal char"""
    vc = "|"
    """vertical char"""
    # create seperator line and output row
    sep = ""
    """seperator line"""
    out = ""
    """output row"""
    sep = cc
    out = vc
    c = 0
    for col in row:
        sep = sep + hc * safelen(col) + cc
        out = out + (row[c] if row[c] else '') + vc
        c += 1
        # now print table row
    if top_border:
        result += sep
    result += out + '\n'
    if bottom_border:
        result += sep + '\n'
    return result

def print_table(rows):
    """Prints the rows of a table by calling print_table_row function.
    The first row is assumed to be the heading line. The heading line
    and the last line of the table are printed with seperator lines.
    """

    result = str()
    r = 0
    """row counter"""
    # space-pad the cells and right align the contents
    c = 0
    """column number"""
    while c < len(rows[0]):
        col = get_column(rows, c)
        cell_width = max_cell_length(col)
        for row in rows:
            row[c] = align_cell_content(row[c], cell_width, 0, False)
        c+=1
    for row in rows:
        result += print_table_row(row)
        r += 1
    return result

def get_column(matrix=[], column=0):
    """Returns one column from the given matrix."""
    col = []
    for row in matrix:
        cell=""
        if len(row) >= column:
            cell = row[column]
        col.append(cell)
    return col

def max_cell_length(cells):
    """Returns the length of the longest cell from all the given cells."""
    max_len=0
    for c in cells:
        cur_len=safelen(c)
        if cur_len > max_len:
            max_len = cur_len
    return max_len

def align_cell_content(cell, max_cell_length=0, alignment=0, truncate=True):
    """Returns the given cell padded with spaces to the max_cell_length.
    You may choose the alignment of the cell contents:

    0 : align left
    1 : align right
    2 : center

    In case the cell contents is longer than max_cell_length, the contents
    gets truncated. You may choose to not truncate any cell data.
    """
    cell = cell if cell else ''
    if max_cell_length == 0:
        return cell
    cur_cell_length = len(cell)
    padding=max_cell_length-cur_cell_length
    if padding == 0: return cell
    if padding < 0:
        if truncate:
            return cell[:max_cell_length]
        else:
            return cell
    else:
        if alignment == 0:
            # align left
            return cell + " " * padding
        if alignment == 1:
            # align right:
            return " " * padding + cell
        else:
            # center
            pl = int(math.ceil(padding / 2.0))
            pr = padding - pl
            return " " * pl + cell + " " * pr
