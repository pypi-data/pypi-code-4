# Copyright Matthew Henderson 2013.
# Created 18th December 2010.
# Last updated: Mon Sep 30 19:45:32 BST 2013.

from ryser.output import dict_to_string_simple
from ryser.utils import cell, row_r, alt, alt2

class Latin:

    def __init__(self, P, size, symbols = None, format = ''):
        self._size = size
        if symbols == None:
            self._symbols = range(1, size + 1)
        else:
            self._symbols = symbols
        if format == 'alt':
            self._P = alt(P, size)
        elif format == 'alt2':
            self._P = alt2(P, size)
        else:
            self._P = P

    def __repr__(self):
        return dict_to_string_simple(self._P, self._size)

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, key):
        return self._P[cell(key[0], key[1], self._size)]

    def size(self):
        return self._size

    def symbols(self):
        return self._symbols

    def row_presences(self, row_index):
        result = []
        first_cell = cell(row_index, 1, self._size)
        row = row_r(first_cell, self._size)
        for cell_ in row:
            symbol = self._P.get(cell_)
            if symbol!=None:
                result.append(symbol)
        return result

    def row_absences(self, row_index):
        result = self.symbols()[:]
        presences = self.row_presences(row_index)
        for x in presences:
            if x in result:
               result.remove(x)
        return result

    def fixed_cells(self):
        return self._P

    def extend(self, disjoint_fixed):
        self._P.update(disjoint_fixed)

