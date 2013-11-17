from base import RRR, RRI, RI, Cond, Instruction


class Add(RRR):
    opcode = 0b1000
    function = 0


class Addi(RRI):
    opcode = 0b1100
    function = 0


class And(RRR):
    opcode = 0b1000
    function = 0b0101


class Andi(RRI):
    opcode = 0b1100
    function = 0b0101


class Mul(RRR):
    opcode = 0b1000
    function = 0b0010


class Muli(RRI):
    opcode = 0b1100
    function = 0b0010


class Or(RRR):
    opcode = 0b1000
    function = 0b0100


class Ori(RRI):
    opcode = 0b1100
    function = 0b0100


class Sll(RRR):
    opcode = 0b1000
    function = 0b0111


class Slli(RRI):
    opcode = 0b1100
    function = 0b0111


class Sra(RRR):
    opcode = 0b1000
    function = 0b0011


class Srai(RRI):
    opcode = 0b1100
    function = 0b0011


class Srl(RRR):
    opcode = 0b1000
    function = 0b1000


class Srli(RRI):
    opcode = 0b1100
    function = 0b1000


class Sub(RRR):
    opcode = 0b1000
    function = 0b0001


class Subi(RRI):
    opcode = 0b1100
    function = 0b0001


class Xor(RRR):
    opcode = 0b1000
    function = 0b0110


class Xori(RRI):
    opcode = 0b1100
    function = 0b0110


class Call(RI):
    opcode = 0b0011


class Jmp(RI):
    opcode = 0b0010


class Ld(RRI):
    opcode = 0b0000

    def __init__(self, rd, rs, immediate):
        self.rd = rd
        self.rs = rs
        self.immediate = immediate


class Ldi(RI):
    opcode = 0b0100


class St(RRI):
    opcode = 0b0001

    def __init__(self, rd, rs, immediate):
        self.rd = rd
        self.rs = rs
        self.immediate = immediate


class Sti(RI):
    opcode = 0b0101


class Ldg(RRR):
    opcode = 0b1001

    def __init__(self, rd):
        self.rd = rd


class Setg(RI):
    opcode = 0b1011

    def __init__(self, rd):
        self.rd = rd


class Stg(RRR):

    opcode = 0b1010

    def __init__(self, rs, rt):
        self.rs = rs
        self.rt = rt


# Pseudo instructions

class Cmp(Instruction):
    def __new__(self, rs, rt):
        return Sub(0, rs, rt)


class Mv(Instruction):
    def __new__(self, rd, rs):
        return Ori(rd, rs, 0)


class Neg(Instruction):
    def __new__(self, rd, rs):
        return Sub(rd, 0, rs)


class Nop(Instruction):
    def __new__(self):
        nop = Add(0, 0, 0)
        nop.cond = Cond.NEVER
        return nop


class Not(Instruction):
    def __new__(self, rd, rs):
        return Xori(rd, rs, -1)


class Ret(Instruction):
    def __new__(self):
        return Jmp(31, 0)
