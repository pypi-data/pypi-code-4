"""TODO
    Find a way to convert to lists, than add to the class
    Draw the fomulas combined

    """


class Names:
    def __init__(self, a_name, a_formula = []):
        self.name = a_name
        self.formula = a_formula
    def add_name(self, name_v):
        self.name = name_v
    def add_formula(self, formula_v):
        self.formula.extend(formula_v)


def z_count(z_n):
    prim = 0
    seg = 0
    terc = 0
    quar = 0
    quint = 0
    six = 0
    z7 = 0
    z8 = 0
    z9 = 0
    z10 = 0
    z11 = 0
    z12 = 0
    z13 = 0
    z14 = 0
    z15 = 0
    z16 = 0
    z17 = 0
    z18 = 0
    z19 = 0
    
    while z_n != 0:

        if z_n <= 2:
            prim = prim + 1
            z_n -= 1

            if prim > 2:
                z_n -= 1

        elif z_n > 2 and z_n <= 4:
            seg += 1
            z_n -= 1

            if seg > 2:
                z_n -= 1

        elif z_n > 4 and z_n <= 10:
            terc += 1
            z_n -= 1

            if terc > 6:
                z_n -= 1

        elif z_n <= 12 and z_n > 10:
            quar += 1
            z_n -= 1

            if quar > 2:
                z_n -= 1

        elif z_n > 12 and z_n <= 18:
            quint += 1
            z_n -= 1

            if quint > 6:
                z_n -=1

        elif z_n > 18 and z_n <= 28:
            six += 1
            z_n -= 1

            if six > 10:
                z_n -=1

        elif z_n > 28 and z_n <= 30:
            z7 += 1
            z_n -= 1
            if z7 > 2:
                z_n -= 1

        elif z_n > 30 and z_n <= 36:
            z8 += 1
            z_n -= 1

        elif z_n > 36 and z_n <= 46:
            z9 += 1
            z_n -= 1

        elif z_n > 46 and z_n <= 60:
            z10 += 1
            z_n -=1

        elif z_n > 60 and z_n <= 62:
            z11 += 1
            z_n -= 1

        elif z_n > 62 and z_n <= 68:
            z12 += 1
            z_n -= 1

        elif z_n > 68 and z_n <= 78:
            z13 += 1
            z_n -= 1

        elif z_n > 78 and z_n <= 92:
            z14 += 1
            z_n -= 1

        elif z_n > 92 and z_n <= 94:
            z15 += 1
            z_n -= 1

        elif z_n > 94 and z_n <= 100:
            z16 += 1
            z_n -= 1

        elif z_n > 100 and z_n <= 110:
            z17 += 1
            z_n -= 1

        elif z_n > 110 and z_n <= 112:
            z18 += 1
            z_n -= 1

        elif z_n > 112 and z_n <= 118:
            z19 += 1
            z_n -= 1

    nome_e = input("Name: ")
    nome = Names(str(nome_e))


    return(read_z(prim, seg, terc, quar, quint, six, z7, z8, z9, z10, z11, z12,
           z13, z14, z15, z16, z17, z18, z19))
    
"""
    read_z(prim, seg, terc, quar, quint, six, z7, z8, z9, z10, z11, z12,
           z13, z14, z15, z16, z17, z18, z19)       


    return(prim, seg, terc, quar, quint, six, z7, z8, z9, z10, z11, z12,
           z13, z14, z15, z16, z17, z18, z19)
"""

    


#Other function... Shit
def read_z(f1, f2 = False, f3 = False,
           f4 = False, f5 = False, f6 = False, f7 = False, f8 = False,
           f9 = False, f10 = False, f11 = False, f12 = False, f13 = False,
           f14 = False, f15 = False, f16 = False, f17 = False, f18 = False,
           f19 = False):

    r1 = "1s" + str(f1)
    r2 = "2s" + str(f2)
    r3 = "2p" + str(f3)
    r4 = str(f4)
    r5 = str(f5)
    r6 = str(f6)
    r7 = str(f7)
    r8 = str(f8)
    r9 = str(f9)
    r10 = str(f10)
    r11 = str(f11)
    r12 = str(f12)
    r13 = str(f13)
    r14 = str(f14)
    r15 = str(f15)
    r16 = str(f16)
    r17 = str(f17)
    r18 = str(f18)
    r19 = str(f19)
    
    print("The diagram of Linus Pauling: \n")

    print(r1 + "\n")
    print(r2 + " " + r3 + "\n")
    print("3s" + r4 + " 3p" + r5 + " 3d" + r6 + "\n")
    print("4s" + r7 + " 4p" + r8 + " 4d" + r9 + " 4f" + r10 + "\n")
    print("5s" + r11 + " 5p" + r12 + " 5d" + r13 + " 5f" + r14 + "\n")
    print("6s" + r15 + " 6p" + r16 + " 6d" + r17 + "\n")
    print("7s" + r18 + " 7p" + r19 + "\n")

    print("Eletronic distribution in geometric order: \n")

    print(r1 + " " + r2 + " " + r3 + " " + "3s" + r4 + " 3p" + r5 + " 3d" + r6 + " " +
          "4s" + r7 + " 4p" + r8 + " 4d" + r9 + " 4f" + r10 + " " +
          "5s" + r11 + " 5p" + r12 + " 5d" + r13 + " 5f" + r14 + " " +
          "6s" + r15 + " 6p" + r16 + " 6d" + r17 + " " +
          "7s" + r18 + " 7p" + r19 + "\n")


    print("Eletronic distribution in energetic order: \n")

    print(r1 + " " + r2 + " " + r3 + " " + "3s" + r4 + " 3p" + r5 +
          " 4s" + r7 + " 3d" + r6 + " " + " 4p" + r8 + " 5s" + r11 + " 4d" + r9 +
          " 5p" + r12 + " 6s" + r15 + " 4f" + r10 + " 5d" + r13 + " 6p" + r16 +
          " 7s" + r18 + " 5f" + r14 + " 6d" + r17 + " 7p" + r19 + "\n")
          
          
          
