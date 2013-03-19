"""
Boolean Tables

Interface Functions:
    expr2truthtable

Interface Classes:
    Table
        TruthTable
        ImplicantTable
"""

from pyeda import __version__
from pyeda.common import bit_on, cached_property, iter_space
from pyeda.boolfunc import Function
from pyeda.expr import Expression

# Positional Cube Notation
PC_VOID, PC_ONE, PC_ZERO, PC_DC = range(4)

PC_VALS = [PC_ZERO, PC_ONE]

PC_STR = {
    PC_VOID : "?",
    PC_ZERO : "0",
    PC_ONE  : "1",
    PC_DC   : "-"
}

def expr2truthtable(expr):
    """Convert an expression into a truth table.

    If the expression lists the variables in a, b, c order, 'a' will
    be in the LSB. Conventionally we read left-to-right, so reverse
    the inputs to put 'a' in the MSB.
    """
    inputs = expr.inputs[::-1]
    outputs = (PC_VALS[expr.restrict(point)] for point in iter_space(inputs))
    return TruthTable(inputs, outputs)


class Table(Function):
    def __repr__(self):
        return self.__str__()


class TruthTable(Table):

    def __init__(self, inputs, outputs):
        self._inputs = inputs
        self._data = bytearray()
        pos = 0
        for pcval in outputs:
            if pos == 0:
                self._data.append(0)
            self._data[-1] += (pcval << pos)
            pos = (pos + 2) & 7

    def __str__(self):
        """Return the table in Espresso input file format.

        >>> from pyeda.expr import var
        >>> a, b = map(var, "ab")
        >>> expr2truthtable(a * -b)
        .i 2
        .o 1
        .ilb a b
        00 0
        01 0
        10 1
        11 0
        .e
        """
        #s = ["# auto-generated by pyeda version: ", __version__, "\n"]
        s = [".i ", str(self.degree), "\n"]
        s += [".o 1", "\n"]
        s.append(".ilb ")
        s.append(" ".join(str(v) for v in reversed(self._inputs)))
        s.append("\n")
        for n in range(2 ** self.degree):
            s += [str(bit_on(n, i)) for i in range(self.degree - 1, -1, -1)]
            # n >> 2 == n / 4; n & 3 == n % 4
            byte = self._data[n >> 2]
            output = (byte >> ((n & 3) << 1)) & 3
            s += [" ", PC_STR[output], "\n"]
        s.append(".e")
        return "".join(s)

    # From Function
    @cached_property
    def support(self):
        return set(self._inputs)

    @property
    def inputs(self):
        return self._inputs
