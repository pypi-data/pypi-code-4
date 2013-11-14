#!/usr/bin/python
import numpy as np
import time
import sys
# miedema.py v1.6 12-13-2012 Jeff Doak jeff.w.doak@gmail.com

def input_elements(filename):
    """Returns a dictionary containing as keys all the elements which have
    tabulated Miedema model input parameters. The value associated with each key
    is a list containing these input parameters. The parameters in the list are:
    Phi, n_ws^(1/3.), vol^(2/3.), Z, Valence, TM, RtoP, Htrans(kJ/mol)"""
    file = open(filename,"r")
    elements = {}
    for line in file:
        if line.startswith("#"):
            continue
        line = line.split()
        if len(line) == 1:
            elements[line[0]] = []
        if len(line) > 1:
            # Miedema File Format:
            # Element_name Phi Rho Vol Z Valence TM? RtoP Htrans
            # 0            1   2   3   4 5       6   7    8
            #              0   1   2   3 4       5   6    7
            # str          float...... int.......... float......
            key = line[0]
            val = []
            val.append(float(line[1]))
            val.append(float(line[2]))
            val.append(float(line[3]))
            val.append(int(line[4]))
            val.append(int(line[5]))
            val.append(int(line[6]))
            val.append(float(line[7]))
            val.append(float(line[8]))
            elements[key] = val
    file.close()
    return elements

def pick_P(elementA,elementB,database):
    """Chooses a value of P based on the transition metal status of the elements
    A and B. There are 3 values of P for the cases where both A and B are TM,
    where only one of A and B is a TM, and where neither are TMs."""
    possibleP = [14.2,12.35,10.7]
    if (database[elementA][5] + database[elementB][5]) == 2:
        # Both elementA and elementB are Transition Metals.
        return possibleP[0]
    elif (database[elementA][5] + database[elementB][5]) == 1:
        # Only one of elementA and elementB are Transition Metals.
        return possibleP[1]
    else:
        # Neither elementA nor elementB are Transition Metals.
        return possibleP[2]

def pick_RtoP(elementA,elementB,database):
    """Calculate and return the value of RtoP based on the transition metal
    status of elements A and B, and the elemental values of RtoP for elements A
    and B."""
    # List of Transition Metals as given in Fig 2.28 of 
    # de Boer, et al., Cohesion in Metals (1988) (page 66).
    tmrange = []
    tmrange.extend(range(20,30))
    tmrange.extend(range(38,48))
    tmrange.extend(range(56,58))
    tmrange.extend(range(72,80))
    tmrange.extend([90,92,94])
    # List of Non-Transition Metals as given in Fig 2.28 of 
    # de Boer, et al., Cohesion in Metals (1988) (page 66).
    nontmrange = []
    nontmrange.extend(range(3,8))
    nontmrange.extend(range(11,16))
    nontmrange.extend([19])
    nontmrange.extend(range(30,34))
    nontmrange.extend([37])
    nontmrange.extend(range(48,52))
    nontmrange.extend([55])
    nontmrange.extend(range(80,84))
    # If one of A,B is in tmrange and the other is in nontmrange, set RtoP
    # to the product of elemental values, otherwise set RtoP to zero.
    if (database[elementA][3] in tmrange) and (database[elementB][3] in
            nontmrange):
        RtoP = database[elementA][6]*database[elementB][6]
    elif (database[elementA][3] in nontmrange) and (database[elementB][3] in
            tmrange):
        RtoP = database[elementA][6]*database[elementB][6]
    else:
        RtoP = 0.0
    return RtoP

def pick_a(elementA,database):
    """Choose a value of a based on the valence of element A."""
    possible_a = [0.14,0.1,0.07,0.04]
    if database[elementA][4] == 1:
        return possible_a[0]
    elif database[elementA][4] == 2:
        return possible_a[1]
    elif database[elementA][4] == 3:
        return possible_a[2]
    #elif elementA in ["Ag","Au","Ir","Os","Pd","Pt","Rh","Ru"]:
    elif elementA in ["Ag","Au","Cu"]:
        return possible_a[2]
    else:
        return possible_a[3]

def gamma_ab(elementA,elementB,database):
    """Calculate and return the value of Gamma_AB (= Gamma_BA) for the solvation
    of element A in element B."""
    QtoP = 9.4  # Constant from Miedema's Model.
    phi = [database[elementA][0],database[elementB][0]]
    rho = [database[elementA][1],database[elementB][1]]
    delta_phi = phi[0] - phi[1]
    delta_rho = rho[0] - rho[1]
    average_rho = (1/rho[0] + 1/rho[1])/2.
    P = pick_P(elementA,elementB,database)
    RtoP = pick_RtoP(elementA,elementB,database)
    Gamma = P*(QtoP*delta_rho**2 - delta_phi**2 - RtoP)/average_rho
    Gamma = int(round(Gamma))
    return Gamma

def H_form_ord(elementA,elementB,xB,database):
    """Calculate the enthalpy of formation for an ordered compound of elements A
    and B with a composition xB of element B."""
    Gamma = gamma_ab(elementA,elementB,database)
    vol0_A = database[elementA][2]
    vol0_B = database[elementB][2]
    phi = [database[elementA][0],database[elementB][0]]
    htrans = [database[elementA][7],database[elementB][7]]
    # Determine volume scale parameter a.
    a_A = pick_a(elementA,database)
    a_B = pick_a(elementB,database)
    # Calculate surface concentrations using original volumes.
    c_S_A = (1-xB)*vol0_A/((1-xB)*vol0_A+xB*vol0_B)
    c_S_B = xB*vol0_B/((1-xB)*vol0_A+xB*vol0_B)
    # Calculate surface fractions for ordered compounds using original volumes.
    f_BA = c_S_B*(1+8*(c_S_A*c_S_B)**2)
    f_AB = c_S_A*(1+8*(c_S_A*c_S_B)**2)
    # Calculate new volumes using surface fractions (which use original
    # volumes).
    vol_A = vol0_A*(1+a_A*f_BA*(phi[0]-phi[1]))
    vol_B = vol0_B*(1+a_B*f_AB*(phi[1]-phi[0]))
    # Recalculate surface concentrations using new volumes.
    c_S_A = (1-xB)*vol_A/((1-xB)*vol_A+xB*vol_B)
    c_S_B = xB*vol_B/((1-xB)*vol_A+xB*vol_B)
    # Recalculate surface fractions for ordered compounds using new volumes.
    f_BA = c_S_B*(1+8*(c_S_A*c_S_B)**2)
    f_AB = c_S_A*(1+8*(c_S_A*c_S_B)**2)
    D_htrans = xB*htrans[1]+(1-xB)*htrans[0]
    H_ord = (Gamma*(1-xB)*xB*vol_A*vol_B*(1+8*(c_S_A*c_S_B)**2)/
            ((1-xB)*vol_A+xB*vol_B) + D_htrans)
    return round(H_ord*0.01036427, 2)
    #return int(round(H_ord))

def get_miedema_energy(composition):
    '''
    composition must be a dictionary of elements and amounts. If not binary, or
    if any element isn't parameterized, returns None.

    composition = {'A':Nx, 'B':Ny, 'C':Nz}
    '''
    # validate composition
    if len(composition) != 2:
        return None
    filename = "../miedema.dat"
    elements = input_elements(filename)

    if not all( elements[k] for k in composition ):
        return None
    natoms=sum(composition.values())
    A,B = composition.keys()
    xB = float(composition[B])/natoms
    return H_form_ord(A,B,xB,elements)
