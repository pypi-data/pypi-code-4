
def binary(num, size):
    if(num < 0):
        num = ~num + 1
        representation = bin(num)[2:]
        while(len(representation) < size):
            representation = '1' + representation
    else:
        representation = bin(num)[2:]
        while(len(representation) < size):
            representation = '0' + representation
    return representation


class Cond(object):
    NEVER = 0b0000
    EQUAL = 0b0001
    NOT_EQUAL = 0b0010
    GREATER_EQUAL = 0b0011
    GREATER = 0b0100
    LESS_EQUAL = 0b0101
    LESS = 0b0110
    OVERFLOW = 0b0111
    NOT_OVERFLOW = 0b1000
    ALWAYS = 0b1111
    UNSET = -1

    @staticmethod
    def fromString(string):
        return {
            'equal': Cond.EQUAL,
            'not equal': Cond.NOT_EQUAL,
            'greater than': Cond.GREATER,
            'greater than or equal': Cond.GREATER_EQUAL,
            'less than': Cond.LESS,
            'less than or equal': Cond.LESS_EQUAL,
            'zero': Cond.EQUAL,
            'not zero': Cond.NOT_EQUAL,
            'positive': Cond.GREATER,
            'positive or zero': Cond.GREATER_EQUAL,
            'negative': Cond.LESS,
            'negative or zero': Cond.LESS_EQUAL,
            'overflow': Cond.OVERFLOW,
            'not overflow': Cond.NOT_OVERFLOW,
            'never': Cond.NEVER,
            'always': Cond.ALWAYS,
        }[string.lower()]


class Instruction(object):

    cond = Cond.UNSET
    opcode = 0


class RRR(Instruction):

    rd = 0
    rs = 0
    rt = 0
    function = 0

    def __init__(self, rd, rs, rt):
        super(RRR, self).__init__()
        self.rd = rd
        self.rs = rs
        self.rt = rt

    def toBinary(self, debug=False):
        return ['', 'cond  opcode  rd     rs     rt     N/A     function\n'][
            debug] + \
            binary(self.cond, 4) + \
            ['', '  '][debug] + \
            binary(self.opcode, 4) + \
            ['', '    '][debug] + \
            binary(self.rd, 5) + \
            ['', '  '][debug] + \
            binary(self.rs, 5) + \
            ['', '  '][debug] + \
            binary(self.rt, 5) + \
            ['', '  '][debug] + \
            '00000' + \
            ['', '  '][debug] + \
            binary(self.function, 4)

    def __repr__(self):
        return self.__class__.__name__.lower() + ' ' + str(self.rd) + \
            ', ' + str(self.rs) + ', ' + str(self.rt)


class RRI(Instruction):
    rd = 0
    rs = 0
    immediate = 0
    function = 0

    def __init__(self, rd, rs, immediate):
        super(RRI, self).__init__()
        self.rd = rd
        self.rs = rs
        self.immediate = immediate
        if immediate >= 1024 or immediate < -1024:
            raise Exception("Too large immediate!" +
                            " It must be in the range [-1024, 1024).")

    def toBinary(self, debug=False):
        return ['', 'cond  opcode  rd     rs     immediate   function\n'][
            debug] + \
            binary(self.cond, 4) + \
            ['', '  '][debug] + \
            binary(self.opcode, 4) + \
            ['', '    '][debug] + \
            binary(self.rd, 5) + \
            ['', '  '][debug] + \
            binary(self.rs, 5) + \
            ['', '  '][debug] + \
            binary(self.immediate, 10) + \
            ['', '  '][debug] + \
            binary(self.function, 4)

    def __repr__(self):
        return self.__class__.__name__.lower() + ' ' + str(self.rd) + \
            ', ' + str(self.rs) + ', ' + str(self.immediate)


class RI(Instruction):

    rd = 0
    immediate = 0

    def __init__(self, rd, immediate):
        super(RI, self).__init__()
        self.rd = rd
        self.immediate = immediate
        if immediate >= 2**19 or immediate < -2**19:
            raise Exception("Too large immediate!" +
                            " It must be in the range [-2^19, 2^19-1).")

    def toBinary(self, debug=False):
        return ['', 'cond  opcode  rd     immediate\n'][debug] + \
            binary(self.cond, 4) + \
            ['', '  '][debug] + \
            binary(self.opcode, 4) + \
            ['', '    '][debug] + \
            binary(self.rd, 5) + \
            ['', '  '][debug] + \
            binary(self.immediate, 19)

    def __repr__(self):
        return self.__class__.__name__.lower() + ' ' + \
            str(self.rd) + ', ' + str(self.immediate)
