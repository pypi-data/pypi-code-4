import numpy

class Variable(object):
    def __init__(self, name, inverted=False):
        self.name = name
        self.inverted = inverted

    def __neg__(self):
        v = Variable(self.name)
        v.inverted = not self.inverted
        return v

    def __and__(self, other):
        c = Cnf.create_from(self)
        return c & other

    def __or__(self, other):
        c = Cnf.create_from(self)
        return c | other

    def __xor__(self, other):
        c = Cnf.create_from(self)
        return c ^ other

    def __rshift__(self, other): # implies
        c = Cnf.create_from(self)
        return -c | other

    def __str__(self):
        return ("-" if self.inverted else "") + self.name

    def __eq__(self, other):
        return self.name == other.name and self.inverted == other.inverted

    def __hash__(self):
        return hash(self.name) ^ hash(self.inverted)

    def __cmp__(self, other):
        if self == other:
            return 0
        if (self.name, self.inverted) < (other.name, other.inverted):
            return -1
        else:
            return 1

class Cnf(object):
    def __init__(self):
        self.dis = []

    @classmethod
    def create_from(cls, x):
        if isinstance(x, Variable):
            cnf = Cnf()
            cnf.dis = [frozenset([x])]
            return cnf
        elif isinstance(x, cls):
            return x
        else:
            raise Exception("Could not create a Cnf object from %s" % str(type(x)))

    def __and__(self, other):
        other = Cnf.create_from(other)
        result = Cnf()
        result.dis = self.dis + other.dis
        return result

    def __or__(self, other):
        other = Cnf.create_from(other)

        if len(self.dis) > 0 and len(other.dis) > 0:
            new_dis = []
            for d1, d2 in [(d1,d2) for d1 in self.dis for d2 in other.dis]:
                d3 = d1 | d2
                new_dis.append(d3)
        elif len(self.dis) == 0:
            new_dis = other.dis
        else:
            new_dis = self.dis

        c = Cnf()
        c.dis = new_dis
        return c

    def __xor__(self, other):
        return (self | other) & (-self | -other)

    def __neg__(self):
        cnfs = []

        for d in self.dis:
            c = Cnf()
            for v in d:
                c.dis.append(frozenset([-v]))
            cnfs.append(c)

        ret = cnfs.pop()
        for cnf in cnfs:
            ret |= cnf

        return ret

    def __rshift__(self, other): # implies
        return -self | other

    def __str__(self):
        ret = []
        for d in self.dis:
            ret.append(" | ".join(map(str,d)))
        return "(" + ") & (".join(ret) + ")"

    def __eq__(self, other):
        return self.dis == other.dis

    def __hash__(self):
        return hash(self.dis)

class BitVariable(object):
    varmap = {}
    def __init__(self, name, varz):
        if BitVariable.varmap.has_key(name):
            self.varno = BitVariable.varmap[name]
        else:
            self.varno = len(BitVariable.varmap)
            BitVariable.varmap[name] = self.varno
        self.name = name
        self.inverted = 0
        self.chunk = self.varno / 32
        #print (((self.varno % 16) * 2) + self.inverted)
        self.bitfield = (1 << (((self.varno % 31) * 2) + self.inverted))
        self.varz = varz

    def __neg__(self):
        v = BitVariable(self.name, self.varz)
        v.inverted = 1 - self.inverted
        v.bitfield = (1 << (((v.varno % 31) * 2) + v.inverted))
        return v

    def __and__(self, other):
        c = BitCnf.create_from(self, self.varz)
        return c & other

    def __or__(self, other):
        c = BitCnf.create_from(self, self.varz)
        return c | other

    def __xor__(self, other):
        c = BitCnf.create_from(self, self.varz)
        return c ^ other

    def __rshift__(self, other): # implies
        c = BitCnf.create_from(self, self.varz)
        return -c | other

    def __str__(self):
        return ("-" if self.inverted else "") + self.name

    def __eq__(self, other):
        return self.name == other.name and self.inverted == other.inverted

    def __hash__(self):
        return hash(self.name) ^ hash(self.inverted)

    def __cmp__(self, other):
        if self == other:
            return 0
        if (self.name, self.inverted) < (other.name, other.inverted):
            return -1
        else:
            return 1

class BitCnf(object):
    def __init__(self, varz):
        self.clauses = []   # Bit table
        self.varz = varz    # Number of possible variables

    @classmethod
    def _new_clause(cls,varz):
        return numpy.zeros(varz/32+1, dtype=numpy.int64)

    def dedup_clauses(self):
        """Eliminate double clauses
        """
        newclauses = []
        for clause in self.clauses:
            if clause not in newclauses:
                newclauses.append(clause)
        self.clauses = newclauses

    def dedup_vars(self):
        """Eliminates e | -e type of expressions
        """
        lsmask = int('10'*32,2)
        rsmask = int('01'*32,2)

        for clause in self.clauses:
            numpy.vectorize(lambda a: a & ~(a & (a << 1) & lsmask) & ~(a & (a >> 1) & rsmask))(self.clauses)

    @classmethod
    def create_from(self,v,varz):
        if isinstance(v, BitVariable):
            cnf = BitCnf(varz)
            c = BitCnf._new_clause(varz)
            c[v.chunk] |= v.bitfield
            cnf.clauses.append(c)
            return cnf
        else:
            return v

    def __iand__(self, other):
        other = self.create_from(other, self.varz)

        for clause in other.clauses:
            self.clauses.append(clause[:])
        return self

    def __or__(self, other):
        other = self.create_from(other, self.varz)
        newcnf = BitCnf(self.varz)

        if len(self.clauses) > 0 and len(other.clauses) > 0:
            for c1, c2 in [(c1,c2) for c1 in self.clauses for c2 in other.clauses]:
                newcnf.clauses.append(c1 | c2) # Numpy for the rescue
        elif len(self.clauses) == 0:
            for clause in other.clauses:
                newcnf.clauses.append(clause[:])
        else:
            for clause in self.clauses:
                newcnf.clauses.append(clause[:])

        return newcnf

    def __and__(self, other):
        other = self.create_from(other, self.varz)
        newcnf = BitCnf(self.varz)
        for clause in self.claues:
            newcnf.clauses.append(clause[:])
        if isinstance(other, BitVariable):
            c = BitCnf._new_clause(self.varz)
            c[other.chunk] |= other.bitfield
            newcnf.clauses.append(c)
            return newcnf
        else:
            for clause in other.claues:
                newcnf.clauses.append(clause[:])
            return newcnf
