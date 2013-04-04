"""
This module defines the class cloud, which is the basic class of
DESPOTIC. The cloud class defines the properties of a cloud, both
physical and chemical, and provides methods to perform a variety of
computations on that cloud.
"""

import numpy as np
from scipy.optimize import root
from scipy.optimize import newton
from scipy.integrate import odeint
from emitter import emitter
from composition import composition
from radiation import radiation
from dustProp import dustProp
from despoticError import despoticError
from copy import deepcopy

# Define some global physical constants in cgs units
import scipy.constants as physcons
kB = physcons.k/physcons.erg
c = physcons.c/physcons.centi
mH = physcons.m_p/physcons.gram
h = physcons.h*1e7
sigma=physcons.sigma/physcons.erg*physcons.centi**2
a = 4*sigma/c
G = physcons.G*1e3

# Small numerical value
small = 1e-50

class cloud:
    """
    A class describing the properties of an interstellar cloud, and
    providing methods to perform calculations using those properties.

    Attributes
    ----------
    nH : float
         number density of H nuclei, in cm^-3
    colDen : float
         center-to-edge column density of H nuclei, in cm^-2
    sigmaNT : float
         non-thermal velocity dispersion, in cm s^-1
    dVdr : float
         radial velocity gradient, in s^-1 (or cm s^-1 cm^-1)
    Tg : float
         gas kinetic temperature, in K
    Td : float
         dust temperature, in K
    comp : class composition
         a class that stores information about the chemical
         composition of the cloud
    dust : class dustProp
         a class that stores information about the properties of the
         dust in a cloud
    rad : class radiation
         the radiation field impinging on the cloud
    emitters : dict
         keys of the dict are names of emitting species, and values
         are objects of class emitter

    Methods
    -------
    __init__ -- initialization
    read -- read the properties of a cloud from a file
    addEmitter -- add an emitting species to the cloud
    sigmaVirial -- compute the virial velocity dispersion
    dEdt -- return values of heating and cooling terms
    setTempEq -- calculate equilibrium gas and dust temperatures and
                 set gas and dust temperatures to these values
    setDustTempEq -- set the dust to its equilibrium temperature,
                     treating the gas temperature as fixed
    setGasTempEq -- set the gas to its equilibrium temperature,
                    treating the dust temperature as fixed
    tempEvol -- calculate the time evolutio of the gas temperature
    lineLum -- return the CMB-subtracted line luminosity / intensity /
         brightness temperature of transitions from the specified
         emitter
    """


########################################################################
# Method to initialize
########################################################################
    def __init__(self, fileName=None, verbose=False):
        """
        Paramters
        ---------
        fileName : string
            name of file from which to read cloud description
        verbose : Boolean
            print out information about the cloud as we read it

        Returns
        -------
        Nothing
        """

        # Initial values when class is created
        self.nH = 0.0
        self.colDen = 0.0
        self.sigmaNT = 0.0
        self.dVdr = 0.0
        self.Tg = 0.0
        self.Td = 0.0
        self.comp = composition()
        self.rad = radiation()
        self.dust = dustProp()
        self.emitters = {}

        # Read if file name is given
        if fileName != None:
            self.read(fileName, verbose=verbose)


########################################################################
# Method to return the list of emitters for a cloud
########################################################################
    def emitterList(self):
        return self.emitters.keys()

########################################################################
# Method to set velocity dispersion to virial value
########################################################################
    def setVirial(self, alphaVir=1.0, setColDen=False, setnH=False):
        """
        Set sigmaNT, colDen, or nH to the value required to give a
        virial ratio of unity

        Parameters
        ----------
        alphaVir : float
            virial ratio to be used in computation; defaults to 1
        setColDen : Boolean
            if True, sigmaNT and nH are fixed, and colDen is
            altered to give the desired virial ratio
        setnH : Boolean
            if True, sigmaNT and colDen are fixed, and nH is altered
            to give the desired virial ratio

        Returns
        -------
        Nothing

        Remarks
        -------
        By default the routine fixed nH and colDen and computes
        sigmaNT, but this can be overridden by specifying either
        setColDen or setnH. It is an error to set both of these to
        true.
        """

        # Safety check
        if setColDen==True and setnH==True:
            raise despoticError, "setVirial: cannot use both" +\
                " setColDen and setnH"

        # Thermal velocity disperison squared
        sigmaThSqr = kB*self.Tg / (self.comp.mu*mH)

        # Default case
        if setColDen==False and setnH==False:
            # Total velocity dispersion squared, from definition of
            # alphaVir
            sigmaTotSqr = (3.0*np.pi*alphaVir*G/20.0) * \
                self.colDen**2/self.nH * self.comp.muH*mH
            # Set non-thermal part
            if sigmaTotSqr > sigmaThSqr:
                self.sigmaNT = np.sqrt(sigmaTotSqr - sigmaThSqr)
            else:
                self.sigmaNT = 0.0
                print "setVirial warning: setting sigmaNT = 0, " + \
                    "virial ratio still exceeds desired value"
        elif setnH==True:
            # Set nH from colDen and sigmaNT
            sigmaTotSqr = np.sqrt(self.sigmaNT**2 + sigmaThSqr)
            self.nH = (3.0*np.pi*alphaVir*G/20.0) * \
                self.colDen**2/sigmaTotSqr * self.comp.muH*mH
        else:
            # Set colDen from nH and sigmaNT
            sigmaTotSqr = np.sqrt(self.sigmaNT**2 + sigmaThSqr)
            self.colDen = np.sqrt( \
                sigmaTotSqr*self.nH / (3.0*np.pi*alphaVir*G/20.0) / \
                    (self.comp.muH*mH) )
                                    

########################################################################
# Method to read cloud properties from a file
########################################################################
    def read(self, fileName, verbose=False):
        """
        Read the composition from a file

        Pamameters
        ----------
        fileName : string
            string giving the name of the composition file
        verbose : Boolean
            print out information about the cloud as it is read
        
        Returns
        -------
        Nothing

        Remarks
        -------
        For the format of cloud files, see the user guide
        """

        # Read file
        try:
            fp = open(fileName, 'r')
            if verbose:
                print "Reading from file "+fileName+"..."
        except IOError:
            raise despoticError, "cannot open file "+fileName
        for line in fp:

            # Skip empty and comment lines
            if line=='\n':
                continue
            if line.strip()[0] == "#":
                continue

            # Break line up based on equal sign
            linesplit = line.split("=")
            if len(linesplit) < 2:
                raise despoticError, "Error parsing input line: "+line
            if linesplit[1] == '':
                raise despoticError, "Error parsing input line: "+line

            # Trim trailing comments from portion after equal sign
            linesplit2 = linesplit[1].split('#')

            # Proceed based on the token that precedes the equal sign
            if linesplit[0].upper().strip() == 'NH':

                self.nH = float(linesplit2[0])
                if verbose:
                    print("Setting nH = "+str(self.nH))

            elif linesplit[0].upper().strip() == 'COLDEN':

                self.colDen = float(linesplit2[0])
                if verbose:
                    print "Setting column density = " + \
                        str(self.colDen) + " H cm^-2"

            elif linesplit[0].upper().strip() == 'SIGMANT':

                self.sigmaNT = float(linesplit2[0])
                if verbose:
                    print "Setting sigmaNT = " + \
                        str(self.sigmaNT) + " cm s^-1"

            elif linesplit[0].upper().strip() == 'DVDR':

                self.dVdr = float(linesplit2[0])
                if verbose:
                    print "Setting sigmaNT = " + \
                        str(self.dVdr) + " cm s^-1 cm^-1"

            elif linesplit[0].upper().strip() == 'TG':

                self.Tg = float(linesplit2[0])
                if verbose:
                    print "Setting Tg = "+str(self.Tg) + " K"

            elif linesplit[0].upper().strip() == 'TD':

                self.Td = float(linesplit2[0])
                if verbose:
                    print "Setting Td = "+str(self.Td) + " K"

            elif linesplit[0].upper().strip() == 'ALPHAGD':

                self.dust.alphaGD = float(linesplit2[0])
                if verbose:
                    print "Setting alpha_GD = " + \
                        str(self.dust.alphaGD) + \
                        " erg cm^3 K^-3/2"

            elif linesplit[0].upper().strip() == 'SIGMAD10':

                self.dust.sigma10 = float(linesplit2[0])
                if verbose:
                    print "Setting sigma_d,10 = " + \
                        str(self.dust.sigma10) + \
                        " cm^2 g^-1"

            elif linesplit[0].upper().strip() == 'SIGMADPE':

                self.dust.sigmaPE = float(linesplit2[0])
                if verbose:
                    print "Setting sigma_d,PE = " + \
                        str(self.dust.sigmaPE) + \
                        " cm^2 H^-1"

            elif linesplit[0].upper().strip() == 'SIGMADISRF':

                self.dust.sigmaISRF = float(linesplit2[0])
                if verbose:
                    print "Setting sigma_d,ISRF = " + \
                        str(self.dust.sigmaISRF) + \
                        " cm^2 H^-1"

            elif linesplit[0].upper().strip() == 'ZDUST':

                self.dust.Zd = float(linesplit2[0])
                if verbose:
                    print "Setting Z'_d = " + \
                        str(self.dust.Zd)

            elif linesplit[0].upper().strip() == 'BETADUST':

                self.dust.beta = float(linesplit2[0])
                if verbose:
                    print "Setting beta_dust = "+str(self.dust.beta)

            elif linesplit[0].upper().strip() == 'XHI':

                self.comp.xHI = float(linesplit2[0])
                if verbose:
                    print "Setting xHI = "+str(self.comp.xHI)

            elif linesplit[0].upper().strip() == 'XPH2':

                self.comp.xpH2 = float(linesplit2[0])
                if verbose:
                    print "Setting xpH2 = "+str(self.comp.xpH2)

            elif linesplit[0].upper().strip() == 'XOH2':

                self.comp.xoH2 = float(linesplit2[0])
                if verbose:
                    print "Setting xoH2 = "+str(self.comp.xoH2)

            elif linesplit[0].upper().strip() == 'H2OPR':

                opr = float(linesplit2[0])
                if verbose:
                    print "Setting H2 ortho-para ratio = "+str(opr)

            elif linesplit[0].upper().strip() == 'XH2':

                try:
                    opr==None
                except UnboundLocalError:
                    opr = 0.25
                    print("Warning: H2 OPR unspecified, assuming 0.25")
                self.comp.xpH2 = 1.0/(1.0+opr)*float(linesplit2[0])
                self.comp.xoH2 = opr/(1.0+opr)*float(linesplit2[0])
                if verbose:
                    print "Setting xpH2 = "+str(self.comp.xpH2)
                    print "Setting xoH2 = "+str(self.comp.xoH2)

            elif linesplit[0].upper().strip() == 'XHE':

                self.comp.xHe = float(linesplit2[0])
                if verbose:
                    print "Setting xHe = "+str(self.comp.xHe)

            elif linesplit[0].upper().strip() == 'XE':

                self.comp.xe = float(linesplit2[0])
                if verbose:
                    print "Setting xe = "+str(self.comp.xe)

            elif linesplit[0].upper().strip() == 'XH+':

                self.comp.xe = float(linesplit2[0])
                if verbose:
                    print "Setting xH+ = "+str(self.comp.xe)

            elif linesplit[0].upper().strip() == 'TCMB':

                self.rad.TCMB = float(linesplit2[0])
                if verbose:
                    print "Setting T_CMB = "+str(self.rad.TCMB)+" K"

            elif linesplit[0].upper().strip() == 'TRADDUST':

                self.rad.TradDust = float(linesplit2[0])
                if verbose:
                    print "Setting T_radDust = " + \
                        str(self.rad.TradDust)+" K"

            elif linesplit[0].upper().strip() == 'IONRATE':

                self.rad.ionRate = float(linesplit2[0])
                if verbose:
                    print "Setting primary ionization rate = " + \
                        str(self.rad.ionRate)+" s^-1 H^-1"

            elif linesplit[0].upper().strip() == 'CHI':

                self.rad.chi = float(linesplit2[0])
                if verbose:
                    print "Setting chi = " + \
                        str(self.rad.chi)

            elif linesplit[0].upper().strip() == 'EMITTER':

                # Emitter lines are complicated. There are two
                # required elements, a name and an abundance, that
                # must come first. There are also four optional
                # elements: energySkip, extrapolate, file:FileName,
                # and URL:url

                # Split up the tokens after the equal sign
                linesplit3 = linesplit2[0].split()

                # Make sure the number of tokens is acceptable
                if len(linesplit3) < 2 or len(linesplit3) > 6:
                    raise despoticError, "Error parsing input line: "+line

                # Do we have optional tokens?
                if len(linesplit3) == 2:

                    # Handle case of just two tokens
                    if verbose:
                        print "Adding emitter "+linesplit3[0]+ \
                                  " with abundance "+linesplit3[1] 
                    self.addEmitter(linesplit3[0], \
                                        float(linesplit3[1]))

                else:

                    # We have optional tokens; initialize various
                    # options to their defaults, then alter them based
                    # on the tokens we've been given
                    energySkip=False
                    extrap=False
                    emitterFile=None
                    emitterURL=None
                    for token in linesplit3[2:]:
                        if token.upper().strip() == 'ENERGYSKIP':
                            energySkip=True
                        elif token.upper().strip() == 'EXTRAPOLATE':
                            extrap=True
                        elif token.upper().strip()[0:5] == 'FILE:':
                            emitterFile=token[5:].strip()
                        elif token.upper().strip()[0:4] == 'URL:':
                            emitterURL=token[4:].strip()
                        else:
                            raise despoticError, \
                                'unrecognized token "' + \
                                token.strip()+'" in line: ' \
                                + line

                    # Now print message and add emitter
                    if verbose:
                        msg = "Adding emitter "+linesplit3[0]+ \
                                  " with abundance "+linesplit3[1]
                        if energySkip:
                            msg += "; setting energySkip"
                        if extrap:
                            msg += "; allowing extrapolation"
                        if emitterFile != None:
                            msg += "; using file name "+emitterFile
                        if emitterURL != None:
                            msg += "; using URL "+emitterURL
                        print msg
                    self.addEmitter(linesplit3[0], \
                                        float(linesplit3[1]), \
                                        energySkip=energySkip, \
                                        extrap=extrap, \
                                        emitterFile=emitterFile, \
                                        emitterURL=emitterURL)

            else:
                # Line does not correspond to any known keyword, so
                # throw an error
                raise despoticError, "unrecognized token " + \
                    linesplit[0].strip() + " in file " + fileName

        # Close file
        fp.close()

        # Check that the hydrogen adds up. If not, raise error
        if self.comp.xHI + self.comp.xHplus + \
                2.0*(self.comp.xpH2 + self.comp.xoH2) != 1:
            raise despoticError, \
                "total hydrogen abundance xHI + xH+ + 2 xH2 != 1"

        # Set derived properties based on composition, temperature
        self.comp.computeDerived(self.nH)
        if self.Tg > 0.0:
            self.comp.computeCv(self.Tg)

        # If verbose, print results for derived quantities
        if verbose:
            print "Derived quantities:"
            print "   ===> mean mass per particle = " + \
                str(self.comp.mu) + " mH"
            print "   ===> mean mass per H = " + \
                str(self.comp.muH) + " mH"
            print "   ===> energy added per ionization = " + \
                str(self.comp.qIon/1.6e-12) + " eV"
            if self.Tg > 0.0:
                print "   ===> c_v/(k_B n_H mu_H) = " + \
                    str(self.comp.cv)


########################################################################
# Method to add an emitter
########################################################################
    def addEmitter(self, emitName, emitAbundance, emitterFile=None, \
                       emitterURL=None, energySkip=False, \
                       extrap=False):
        """
        Add an emitting species

        Pamameters
        ----------
        emitName : string
            name of the emitting species
        emitAbundance : float
            abundance of the emitting species relative to H

        Returns
        -------
        Nothing

        Additional parameters
        ---------------------
        emitterFile : string
            name of LAMDA file containing data on this species; this
            option overrides the default
        emitterURL : string
            URL of LAMDA file containing data on this species; this
            option overrides the default
        energySkip : Boolean
            if set to True, this species is ignored when calculating
            line cooling rates
        extrap : Boolean
            if set to True, collision rate coefficients for this species
            will be extrapolated to temperatures outside the range given
            in the LAMDA table. By default, no extrapolation is perfomed,
            and providing temperatures outside the range in the table
            produces an error
        """
        self.emitters[emitName] = \
            emitter(emitName, emitAbundance, \
                        emitterFile=emitterFile, \
                        emitterURL=emitterURL, \
                        extrap=extrap, energySkip=energySkip)


########################################################################
# Method to calculate instantaneous values of all heating, cooling terms
########################################################################
    def dEdt(self, c1Grav=0.0, thin=False, LTE=False, \
                 fixedLevPop=False, noClump=False, \
                 escapeProbGeom='sphere', PsiUser=None, \
                 sumOnly=False, dustOnly=False, gasOnly=False, \
                 dustCoolOnly=False, dampFactor=0.5, \
                 verbose=False, overrideSkip=False):
        """
        Return instantaneous values of heating / cooling terms

        Parameters
        ----------
        c1Grav : float
            if this is non-zero, the cloud is assumed to be
            collapsing, and energy is added at a rate
            Gamma_grav = c1 mu_H m_H cs^2 sqrt(4 pi G rho)
        thin : Boolean
            if set to True, cloud is assumed to be opticall thin
        LTE : Boolean
           if set to True, gas is assumed to be in LTE
        fixedLevPop : Boolean
           if set to True, level populations and escape
           probabilities are not recomputed, so the cooling rate is
           based on whatever values are stored
        escapeProbGeom : string, 'sphere' or 'LVG' or 'slab'
           specifies the geometry to be assumed in calculating
           escape probabilities
        noClump : Boolean
           if set to True, the clumping factor used in estimating
           rates for n^2 processes is set to unity

        Returns
        -------
        rates : dict
           A dict containing the values of the various heating and
           cooling rate terms; all quantities are in units of erg s^-1
           Hz^-1, and by convention positive = heating, negative =
           cooling; for dust-gas exchange, positive indicates heating
           of gas, cooling of dust

           Elements of the dict are as follows by default, but can be
           altered by the additional keywords listed below
           GammaPE : float
               photoelectric heating rate
           GammaCR : float
               cosmic ray heating rate
           GammaGrav : float
               gravitational contraction heating rate
           LambdaLine : dict
               cooling rate from lines; dictionary keys correspond to
               species in the emitter list, values give line cooling
               rate for that species
           PsiGD : float
               dust-gas energy exchange rate
           GammaDustISRF : float
               dust heating rate due to the ISRF
           GammaDustCMB : float
               dust heating rate due to CMB
           GammaDustIR : float
               dust heating rate due to IR field
           GammaDustLine : float
               dust heating rate due to absorption of line radiation
           LambdaDust : float
               dust cooling rate due to thermal emission
           PsiUserGas : float
               gas heating / cooling rate from user-specified
               function; only included if PsiUser != None
           PsiUserDust : float
               gas heating / cooling rate from user-specified
               function; only included is PsiUser != None

        Additional parameters
        ---------------------
        dampFactor : float
            Damping factor to use in level population calculations;
            see emitter.setLevPopEscapeProb
        PsiUser : function
            A user-specified function to add additional heating /
            cooling terms to the calculation. The function takes the
            cloud object as an argument, and must return a two-element
            array Psi, where Psi[0] = gas heating / cooling rate,
            Psi[1] = dust heating / cooling rate. Positive values
            indicate heating, negative values cooling, and units are
            assumed to be erg s^-1 H^-1.
        sumOnly : Boolean
            if true, rates contains only four entries: dEdtGas and
            dEdtDust give the heating / cooling rates for the
            gas and dust summed over all terms, and maxAbsdEdtGas and
            maxAbsdEdtDust give the largest of the absolute values of
            any of the contributing terms for dust and gas
        gasOnly : Boolean
            if true, the terms GammaISRF, GammaDustLine, LambdaDust, \
            and PsiUserDust are omitted from rates. If both gasOnly
            and sumOnly are true, the dict contains only dEdtGas
        dustOnly : Boolean
            if true, the terms GammaPE, GammaCR, LambdaLine,
            GamamDLine, and PsiUserGas are omitted from rates. If both
            dustOnly and sumOnly are true, the dict contains only
            dEdtDust. Important caveat: the value of dEdtDust returned
            in this case will not exactly match that returned if
            dustOnly is false, because it will not contain the
            contribution from gas line cooling radiation that is
            absorbed by the dust
        dustCoolOnly : Boolean
            as dustOnly, but except that now only the terms
            LambdaDust, PsiGD, and PsiUserDust are computed
        overrideSkip : Boolean
            if True, energySkip directives are ignored, and cooling
            rates are calculated for all species
        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Gas terms
        if dustOnly == False and dustCoolOnly == False:

            # Photoelectric heating rate
            GammaPE = 4.0e-26 * self.rad.chi * self.dust.Zd * \
                np.exp(-self.colDen * self.dust.sigmaPE / 2.0)

            # Gravitational heating rate (Masunaga & Inutsuka 1998)
            GammaGrav = c1Grav * kB * self.Tg / (self.comp.mu * mH) * \
                (4 * np.pi * G * self.nH * self.comp.muH * mH) * \
                self.comp.muH * mH

            # Cosmic ray heating rate
            GammaCR = self.rad.ionRate * self.comp.qIon

            # Line cooling rate, and heating rate of dust by lines
            LambdaLine = {}
            GammaDLine = 0.0

            # Iterate over emitting species
            for em in self.emitters.values():

                # Skip energetically unimportant emitters
                if em.energySkip and not overrideSkip:
                    continue

                # Calculate level populations and escape probabilities, using
                # specified assumptions
                if fixedLevPop == False:
                    if LTE==True:   # LTE
                        em.setLevPopLTE(self) 
                        if thin==False:  # LTE, not optically thin
                            em.setEscapeProb(self)
                    elif thin==True:
                        # Optically thin but not in LTE
                        em.setLevPop(self, thin=thin, \
                                         noClump=noClump)
                    else:
                        # Neither optically thin nor in LTE; note that
                        # we try multiple times with progressively
                        # smaller damping factors if need be
                        attempts = 0
                        dFac = dampFactor
                        while em.setLevPopEscapeProb( \
                            self, escapeProbGeom = escapeProbGeom, \
                                noClump = noClump, \
                                verbose = verbose, \
                                dampFactor = dFac) == False:
                            # If we're here, we failed to converge the
                            # level populations, so try again with a
                            # smaller damping factor; allow two
                            # retries before giving up
                            dFac = dFac / 2.0
                            attempts = attempts + 1
                            if attempts > 3:
                                raise despoticError, "convergence " + \
                                    "failed for "+em.name
                            else:
                                print "Warning: convergence failed " + \
                                    "for "+em.name+", RETRYING " + \
                                    "with damping factor = " + str(dFac)
                else:
                    # Safety check
                    if em.levPopInitialized == False:
                        raise despoticError, \
                            "for emitter " + em.name + ": " + \
                            "cannot use fixedLevPop in dEdt" + \
                            " if any level populations are uninitialized"
                    if em.escapeProbInitialized == False and \
                            thin == False:
                        raise despoticError, \
                            "for emitter " + em.name + ": " + \
                            "cannot use fixedLevPop in dEdt" + \
                            " if any escape probabilities are uninitialized"

                # Calculate cooling rates per H for all lines
                lineLum = em.luminosityPerH(self.rad, thin=thin)

                # Calculate total luminosities
                LambdaLine[em.name] = sum(lineLum)

                # Calculate dust heating rate due to lines
                if gasOnly == False:
                    betaDLine = 1.0 / \
                        (1.0 + 0.375 * self.colDen*self.dust.sigma10* \
                             (em.data.radFreq/(10.0*kB/h))**self.dust.beta)
                    GammaDLine += sum((1.0 - betaDLine)*lineLum)

        # End gas terms

        # Dust terms
        if gasOnly == False:

            # Optically thin dust cooling rate
            LambdaDThin = self.dust.sigma10 * \
                (self.Td/10.)**self.dust.beta * \
                c * a * self.Td**4

            # Optically thick dust cooling rate
            LambdaDThick = c * a * self.Td**4 / self.colDen

            # Actual dust cooling rate
            LambdaD = min(LambdaDThin, LambdaDThick)

            if dustCoolOnly == False:

                # ISRF heating rate
                GammaISRF = 3.9e-24 * self.rad.chi * self.dust.Zd * \
                    np.exp(-self.dust.sigmaISRF * self.colDen/2.0)

                # CMB heating rate
                GammaDCMB = self.dust.sigma10 * \
                    (self.rad.TCMB/10.)**self.dust.beta * \
                    c * a * self.rad.TCMB**4

                # IR heating rate
                GammaDIR = self.dust.sigma10 * \
                    (self.rad.TradDust/10.)**self.dust.beta * \
                    c * a * self.rad.TradDust**4

        # End dust terms

        # Grain-gas energy exchange rate
        if noClump == False:
            cs2 = kB * self.Tg / (self.comp.mu * mH)
            cfac = np.sqrt(1.0 + 0.75*self.sigmaNT**2/cs2)
        else:
            cfac = 1.0
        PsiGD = self.dust.alphaGD * cfac * self.nH * \
            np.sqrt(self.Tg) * (self.Td - self.Tg)

        # User terms
        if PsiUser != None:
            PsiUserVal = PsiUser(self)
        else:
            PsiUserVal = np.zeros(2)

        # Build dict of results
        rates = {}
        if sumOnly == False:
            if dustOnly == False and dustCoolOnly == False:
                rates['GammaPE'] = GammaPE
                rates['GammaGrav'] = GammaGrav
                rates['GammaCR'] = GammaCR
                rates['LambdaLine'] = LambdaLine
                if PsiUser != None:
                    rates['PsiUserGas'] = PsiUserVal[0]
            if gasOnly == False:
                if dustCoolOnly == False:
                    rates['GammaDustISRF'] = GammaISRF
                    rates['GammaDustCMB'] = GammaDCMB
                    rates['GammaDustIR'] = GammaDIR
                rates['LambdaDust'] = LambdaD
                if PsiUser != None:
                    rates['PsiUserRad'] = PsiUserVal[1]
            if gasOnly == False and dustOnly == False and \
                    dustCoolOnly == False:
                rates['GammaDustLine'] = GammaDLine
            rates['PsiGD'] = PsiGD
        else:
            if dustOnly == False and dustCoolOnly == False:
                rates['dEdtGas'] = GammaPE + GammaGrav + GammaCR - \
                    sum(LambdaLine.values()) + PsiGD + PsiUserVal[0]
                rates['maxAbsdEdtGas'] = \
                    max(abs(GammaPE), abs(GammaGrav), abs(GammaCR), \
                            abs(sum(LambdaLine.values())), \
                            abs(PsiGD), abs(PsiUserVal[0]))
            if gasOnly == False:
                rates['dEdtDust'] = - LambdaD - PsiGD + PsiUserVal[1]
                rates['maxAbsdEdtDust'] = \
                    max(abs(LambdaD), abs(PsiGD), abs(PsiUserVal[1]))
                if dustCoolOnly == False:
                    rates['dEdtDust'] += GammaISRF + GammaDCMB + \
                        GammaDIR
                    rates['maxAbsdEdtDust'] = \
                        max(rates['maxAbsdEdtDust'], abs(GammaISRF), \
                                abs(GammaDCMB), abs(GammaDIR))
                    if dustOnly == False:
                        rates['dEdtDust'] += GammaDLine
                        rates['maxAbsdEdtDust'] = \
                            max(rates['maxAbsdEdtDust'], \
                                    abs(GammaDLine))

        # Return
        return rates


########################################################################
# Method to calculate equilibrium dust temperature for fixed gas
# temperature
########################################################################
    def setDustTempEq(self, PsiUser=None, Tdinit=None, \
                          noLines=False, noClump=False, \
                          verbose=False, dampFactor=0.5):
        """
        Set Td to equilibrium dust temperature at fixed Tg

        Parameters
        ----------
        Tdinit : float
               initial guess for gas temperature
        PsiUser : function
            A user-specified function to add additional heating /
            cooling terms to the calculation. The function takes the
            cloud object as an argument, and must return a two-element
            array Psi, where Psi[0] = gas heating / cooling rate,
            Psi[1] = dust heating / cooling rate. Positive values
            indicate heating, negative values cooling, and units are
            assumed to be erg s^-1 H^-1.
        noLines : Boolean
            If true, line heating of the dust is ignored. This can
            make the calculation significantly faster.
        noClump : Boolean
           if set to True, the clumping factor used in estimating
           rates for n^2 processes is set to unity
        dampFactor : float
            Damping factor to use in level population calculations;
            see emitter.setLevPopEscapeProb
        verbose : Boolean
            if true, diagnostic information is printed
                                         

        Returns
        -------
        success : Boolean
            True if dust temperature calculation converged, False if not
        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Step 1: initialize dust temperature if initial value is given
        if Tdinit != None:
            self.Td = Tdinit

        # Step 2: compute heating and cooling rates initially; this is
        # useful so that we can compute the terms that don't depend on
        # the dust temperature just once and store them for the rest
        # of the calculation
        rates = self.dEdt(PsiUser=PsiUser, dustOnly=noLines, \
                              noClump=noClump, verbose=verbose, \
                              dampFactor=dampFactor)
        GammaSum = rates['GammaDustISRF'] + rates['GammaDustIR'] + \
            rates['GammaDustCMB']
        GammaSumMax = max(rates['GammaDustISRF'], \
                              rates['GammaDustIR'], \
                              rates['GammaDustCMB'])
        if noLines == False:
            GammaSum += rates['GammaDustLine']
            GammaSumMax = max(GammaSumMax, rates['GammaDustLine'])

        # Step 3: if we don't have an initial guess, make one by
        # assuming that dust-gas coupling is negligible, and that the
        # cloud is not optically thick, which are often the case
        if self.Td == 0.0:
            self.Td = \
                (GammaSum / \
                     (c*a*self.dust.sigma10*0.1**self.dust.beta)) ** \
                     (1.0/(4.0+self.dust.beta))

        # Step 4: solve for T_d using Newton's method
        self.Td = newton(_dustTempResid, self.Td, \
                             maxiter=200, \
                             args=(self, PsiUser, \
                                       GammaSum, GammaSumMax, \
                                       verbose))

        # Check that we're really converged; if not, try again
        # starting from guessed starting position
        if abs(_dustTempResid(self.Td, self, PsiUser, GammaSum, \
                                  GammaSumMax, False)) > 1.0e-3:
            self.Td = \
                (GammaSum / \
                     (c*a*self.dust.sigma10*0.1**self.dust.beta)) ** \
                     (1.0/(4.0+self.dust.beta))
            self.Td = newton(_dustTempResid, self.Td, \
                                 maxiter=200, \
                                 args=(self, PsiUser, \
                                           GammaSum, GammaSumMax, \
                                           verbose))

        # Test for success and return appropriate value
        if abs(_dustTempResid(self.Td, self, PsiUser, GammaSum, \
                                  GammaSumMax, False)) > 1.0e-3:
            return False
        else:
            return True


########################################################################
# Method to calculate equilibrium gas temperature for dust gas
# temperature
########################################################################
    def setGasTempEq(self, c1Grav=0.0, thin=False, noClump=False, \
                         LTE=False, Tginit=None, fixedLevPop=False, \
                         escapeProbGeom='sphere', PsiUser=None, \
                         verbose=False):
        """
        Set Tg to equilibrium gas temperature at fixed Td

        Parameters
        ----------
        c1Grav : float
            if this is non-zero, the cloud is assumed to be
            collapsing, and energy is added at a rate
            Gamma_grav = c1 mu_H m_H cs^2 sqrt(4 pi G rho)
        thin : Boolean
               if set to True, cloud is assumed to be opticall thin
        LTE : Boolean
              if set to True, gas is assumed to be in LTE
        Tginit : float
               initial guess for gas temperature
        fixedLevPop : Boolean
                      if set to true, level populations are held fixed
                      at the starting value, rather than caclculated
                      self-consistently from the temperature
        escapeProbGeom : string, 'sphere' or 'LVG' or 'slab'
            specifies the geometry to be assumed in computing escape
            probabilities
        noClump : Boolean
           if set to True, the clumping factor used in estimating
           rates for n^2 processes is set to unity
        PsiUser : function
            A user-specified function to add additional heating /
            cooling terms to the calculation. The function takes the
            cloud object as an argument, and must return a two-element
            array Psi, where Psi[0] = gas heating / cooling rate,
            Psi[1] = dust heating / cooling rate. Positive values
            indicate heating, negative values cooling, and units are
            assumed to be erg s^-1 H^-1.
        verbose : Boolean
            if True, print status messages while running

        Returns
        -------
        success : Boolean
            True if the calculation converges, False if it does not
        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Initialize gas temperatures if necessary
        if Tginit != None:
            self.Tg = Tginit
        else:
            if self.Tg==0.0:
                self.Tg = 10.0

        # Solve for Tg
        self.Tg = newton(_gasTempResid, self.Tg, \
                             args=(self, c1Grav, \
                                       thin, LTE, \
                                       escapeProbGeom, PsiUser, \
                                       noClump, verbose))

        # Check for success and return appropriate value
        if abs(_gasTempResid(self.Tg, self, c1Grav, thin, LTE, \
                                 escapeProbGeom, PsiUser, \
                                 noClump, verbose)) > 1.0e-3:
            return False
        else:
            return True


########################################################################
# Method to calculate equilibrium gas and dust temperatures
# simultaneously
########################################################################
    def setTempEq(self, c1Grav=0.0, thin=False, noClump=False, \
                      LTE=False, Tinit=None, fixedLevPop=False, \
                      escapeProbGeom='sphere', PsiUser=None, \
                      verbose=False, tol=1e-4):
        """
        Set Tg and Td to equilibrium gas and dust temperatures

        Parameters
        ----------
        c1Grav : float
               coefficient for rate of gas gravitational heating
        thin : Boolean
               if set to True, cloud is assumed to be opticall thin
        LTE : Boolean
              if set to True, gas is assumed to be in LTE
        Tinit : array(2)
               initial guess for gas and dust temperature
        noClump : Boolean
           if set to True, the clumping factor used in estimating
           rates for n^2 processes is set to unity
        fixedLevPop : Boolean
                      if set to true, level populations are held fixed
                      at the starting value, rather than caclculated
                      self-consistently from the temperature
        escapeProbGeom : string, 'sphere' or 'LVG' or 'slab'
            specifies the geometry to be assumed in computing escape
            probabilities
        PsiUser : function
            A user-specified function to add additional heating /
            cooling terms to the calculation. The function takes the
            cloud object as an argument, and must return a two-element
            array Psi, where Psi[0] = gas heating / cooling rate,
            Psi[1] = dust heating / cooling rate. Positive values
            indicate heating, negative values cooling, and units are
            assumed to be erg s^-1 H^-1.
        verbose : Boolean
            if True, the code prints diagnostic information as it runs

        Returns
        -------
        success : Boolean
            True if the iteration converges, False if it does not
        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Initialize gas and dust temperatures if necessary
        if Tinit != None:
            self.Tg = Tinit[0]
            self.Td = Tinit[1]
        else:
            if self.Tg==0.0:
                self.Tg = 10.0
            if self.Td==0.0:
                self.Td = 10.0
        Tinit = np.array([self.Tg, self.Td])

        # Iterate to get equilibrium temperatures
        res = root(_gdTempResid, Tinit, \
                           args=(self, c1Grav, thin, \
                                     LTE, escapeProbGeom, \
                                     PsiUser, noClump, verbose), \
                       method='hybr', options = { 'xtol' : tol })

        # Make sure we've converged.
        if res.success == False:
            return False

        # Store final result
        self.Tg = res.x[0]
        self.Td = res.x[1]
        return True



########################################################################
# Method to calculate time-dependent evolution of gas temperature for
# given starting conditions; note that we assume that the dust is
# always in thermal equilibrium, since its equilibration time is small
# compared to that of the gas.
########################################################################
    def tempEvol(self, tFin, tInit=0.0, c1Grav=0.0, noClump=False, \
                     thin=False, LTE=False, fixedLevPop=False, \
                     escapeProbGeom='sphere', nOut=100, dt=None, \
                     tOut=None, PsiUser=None, isobaric=False, \
                     fullOutput=False, dampFactor=0.5, \
                     verbose=False):
        """
        Calculate the evolution of the gas temperature in time

        Parameters
        ----------
        tFin : float
            end time of integration, in sec
        tInit : float
            start time of integration, in sec
        c1Grav : float
            coefficient for rate of gas gravitational heating
        thin : Boolean
            if set to True, cloud is assumed to be opticall thin
        LTE : Boolean
            if set to True, gas is assumed to be in LTE
        isobaric : Boolean
            if set to True, cooling is calculated isobarically;
            otherwise (default behavior) it is computed
            isochorically
        fixedLevPop : Boolean
            if set to true, level populations are held fixed
            at the starting value, rather than caclculated
            self-consistently from the temperature
        noClump : Boolean
            if set to True, the clumping factor used in estimating
            rates for n^2 processes is set to unity
        escapeProbGeom : string, 'sphere' or 'LVG' or 'slab'
            specifies the geometry to be assumed in computing escape
            probabilities
        nOut : int
            number of times at which to report the temperature; this
            is ignored if dt or tOut are set
        dt : float
            time interval between outputs, in s; this is ignored if
            tOut is set
        tOut : array
            list of times at which to output the temperature, in s;
            must be sorted in increasing order
        PsiUser : function
            A user-specified function to add additional heating /
            cooling terms to the calculation. The function takes the
            cloud object as an argument, and must return a two-element
            array Psi, where Psi[0] = gas heating / cooling rate,
            Psi[1] = dust heating / cooling rate. Positive values
            indicate heating, negative values cooling, and units are
            assumed to be erg s^-1 H^-1.
        fullOutput : Boolean
            if True, the full cloud state is returned at every time,
            as opposed to simply the gas temperature
        dampFactor : float
            Damping factor to use in level population calculations;
            see emitter.setLevPopEscapeProb

        Returns
        -------
        if fullOutput == False:
            Tg : array of floats
                array of gas temperatures at specified times, in K
            time : array of floats
                array of output times, in sec
        if fullOutput == True:
            cloudState : list of clouds
                each element of the list is a deepcopy of the cloud
                state at the corresponding time; there is one list
                element per output time
            time : array of floats
                array of output times, in sec

        Remarks
        -------
        If the settings for nOut, dt, or tOut are such that some of
        the output times requested are past tEvol, the cloud will only
        be evolved up to time tEvol. Similarly, if the last output
        time is less than tEvol, the cloud will still be evolved up to
        time tEvol, and the gas temperature Tg will be set to its
        value at that time.
        
        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Set up array of output times if necessary
        if tOut==None:
            if dt==None:
                tOut = tInit + np.arange(nOut+1)*float(tFin-tInit)/nOut
            else:
                tOut = np.arange(tInit, (tFin-tInit)*(1+1e-10), dt)

        # Sanity check on output times: eliminate any output times
        # that are not between tInit and tFin
        tOut1 = tOut[tOut >= tInit]
        tOut1 = tOut1[tOut1 <= tFin]

        # If we're isobaric, record the isobar we're on; otherwise set
        # the isobar value to -1 to flag that we're isochoric
        if isobaric:
            isobar = self.nH * self.Tg
        else:
            isobar = -1

        # Integrate the ODE to the requested times; if fullOuptut is
        # set, we need to manually stop the integration at the
        # requested times so that we can dump detailed output.
        if fullOutput == False:
            Tgout = \
                odeint(_gasTempDeriv, self.Tg, tOut1, \
                           args=(self, c1Grav, thin, LTE, \
                                     escapeProbGeom, PsiUser, \
                                     noClump, isobar, dampFactor, \
                                     verbose))
        else:
            cloudList = [deepcopy(cloud)]
            for i, t in enumerate(tOut1[1:]):
                tvec = [tOut[i], t]
                Tgtemp = \
                    odeint(_gasTempDeriv, self.Tg, tvec, \
                               args=(self, c1Grav, thin, LTE, \
                                         escapeProbGeom, PsiUser, \
                                         noClump, isobar, \
                                         dampFactor, verbose))
                cloudList.append(deepcopy(cloud))

        # If necessary, continue integrating up to tEvol
        if tOut1[-1] < tFin:
            odeint(_gasTempDeriv, self.Tg, \
                                 np.array([tFin-tOut1[-1]]), \
                                 args=(self, c1Grav, thin, LTE, \
                                           escapeProbGeom, PsiUser, \
                                           noClump, isobar, \
                                           dampFactor, verbose))


        # Return gas temperature history
        if fullOutput == False:
            return Tgout, tOut
        else:
            return cloudList, tOut


########################################################################
# Method to return the continuum-subtrated luminosity / intensity /
# brightness temperature of lines from the specified emitter
########################################################################
    def lineLum(self, emitName, LTE=False, noClump=False, \
                    transition=None, thin=False, intOnly=False, \
                    TBOnly=False, lumOnly=False, \
                    escapeProbGeom='sphere', dampFactor=0.5, \
                    noRecompute=False, abstol=1.0e-8, \
                    verbose=False):
        """
        Return the frequency-integrated intensity of various lines

        Parameters
        ----------
        emitName : string
            name of the emitter for which the calculation is to be
            performed
        transition : list of two arrays of shape (M)
            transition[0] = array of upper states
            transition[1] = array of lower states

        Returns
        -------
        if intOnly, TBOnly, and lumOnly are all False:
        res : list of length (M)
              by default M = the number of transitions for this
              species with non-zero Einstein A
              each element of res is a dict containing the following
              key - value pairs:
              'freq' : float, frequency of the line in Hz
              'upper' : int, index of upper state, with ground state
                        = 0 and states ordered by energy
              'lower' : int, index of lower state
              'Tupper' : float, energy of the upper state, in K
                         (i.e. energy over kB)
              'Tex' : excitation temperature relating the upper and
                      lower levels
              'intIntensity' : frequency-integrated intensity of the
                     line, with the CMB contribution subtracted off;
                     units are erg cm^-2 s^-1 sr^-1 
              'intTB' : velocity-integrated brightness temperature of
                     the line, with the CMB contribution subtracted off;
                     units are K km s^-1
              'lumPerH' : luminosity of the line per H nucleus; units
                     are erg s^-1 H^-1
              'tau' : float
                  optical depth in the line, not including dust
              'tauDust' : float
                  dust optical depth in the line
        if intOnly, TBOnly, or lumOnly are True:
        res: array, shape(M)
             array giving intIntensity, TB, or lumPerH for each line,
             corresponding to the values in the dict above

        Additional Parameters
        ---------------------
        TBOnly: Boolean
            if true, the output is simply an array containing the
            velocity-integrated brightness temperatures of the
            specified lines; mutually exclusive with intOnly and
            lumOnly
        intOnly: Boolean
            if true, the output is simply an array containing the
            frequency-integrated intensity of the specified lines;
            mutually exclusive with TBOnly and lumOnly
        lumOnly: Boolean
            if true, the output is simply an array containing the
            luminosity per H nucleus in each of the specified lines;
            mutually eclusive with intOnly and TBOonly
        noRecompute : False
             if True, level populations and escape probabilities are
             not recomputed; instead, stored values are used
        noClump : Boolean
             if set to True, the clumping factor used in estimating
             rates for n^2 processes is set to unity
        escapeProbGeom : string, 'sphere' or 'LVG' or 'slab'
             sets problem geometry that will be assumed in calculating
             escape probabilities; ignored if the escape probabilities
             are already initialized
        dampFactor : float
            Damping factor to use in level population calculations;
            see emitter.setLevPopEscapeProb
        thin : Boolean
            if True, the calculation is done assuming the cloud is
            optically thin; if level populations are uninitialized,
            and LTE is not set, they will be computed assuming the
            cloud is optically thin
        LTE : Boolean
            if True, and level populations are unitialized, they will
            be initialized to their LTE values; if they are
            initialized, this option is ignored

        """

        # Make sure composition-derived quantities are initialized
        if self.comp.mu == 0.0:
            self.comp.computeDerived(self.nH)

        # Step 1. Safety check and initial setup
        if not emitName in self.emitters:
            raise despoticError, 'unknown emitter '+emitName
        em=self.emitters[emitName]
        if transition==None:
            u = em.data.radUpper
            l = em.data.radLower
        else:
            u = transition[0]
            l = transition[1]

        # Step 2. Unless we've been asked not to, compute level
        # populations and escape probabilities
        if not noRecompute:
            if LTE==True:
                em.setLevPopLTE(self.Tg)
                if thin==False:
                   em.setEscapeProb(self, escapeProbGeom=escapeProbGeom) 
            elif thin==True:
                em.setLevPop(self, thin=True, noClump=noClump)
            else:
                em.setLevPopEscapeProb(\
                    self, noClump=noClump, dampFactor=dampFactor, \
                        escapeProbGeom=escapeProbGeom, \
                        abstol=abstol, verbose=verbose)
        # Safety check: make sure we're initialized
        if em.levPopInitialized == False:
            raise despoticError, 'cannot use noRecompute if level' + \
                ' popuplations are uninitialized'
        if em.escapeProbInitialized == False and thin == False:
            raise despoticError, 'cannot use noRecompute if escape' + \
                ' probabilities are uninitialized'

        # Step 3. Compute luminosity per H
        lumPerH = self.emitters[emitName]. \
            luminosityPerH(self.rad, transition=transition, \
                               thin=thin)
        if lumOnly == True:
            return lumPerH

        # Step 4. Compute frequency-integrated intensity (units of erg
        # cm^-2 s^-1 sr^-1), including dust attenuation
        tauDust = self.colDen*self.dust.sigma10 * \
            (em.data.freq[u,l]/(10.0*kB/h))**self.dust.beta
        intIntensity = lumPerH * self.colDen / (4.0*np.pi) / \
            (1.0 + 0.375*tauDust)
        if intOnly == True:
            return intIntensity

        # Step 5. Convert to velocity-integrated brightness
        # temperature; note the division by 10^5 to convert from cm
        # s^-1 to km s^-1; also not the special handling of negative
        # integrated intensities, corresponding to lines where there
        # is absorption of the background CMB. By convention we assign
        # these negative brightness temperatures, with a magnitude
        # equal to the brightness temperature of the absolute value of
        # the intensity
        intIntensityMask = intIntensity.copy()
        intIntensityMask[intIntensity <= 0] = small
        TB = h*self.emitters[emitName].data.freq[u,l]/kB / \
            np.log(1+2*h*em.data.freq[u,l]**3 / (c**2*intIntensityMask)) * \
                    c / (em.data.freq[u,l]) \
                    / 1e5
        TB[intIntensity == 0] = 0.0
        mask = np.where(intIntensity < 0)
        TB[mask] = \
            -h*self.emitters[emitName].data.freq[u[mask],l[mask]]/kB / \
            np.log(1+2*h*em.data.freq[u[mask],l[mask]]**3 / \
                    (-c**2*intIntensity[mask])) * \
                    c / (em.data.freq[u[mask],l[mask]]) \
                    / 1e5
        if TBOnly == True:
            return TB

        # Step 6. Construct output dict
        outDict = []
        tau = em.opticalDepth(transition=transition, \
                                  escapeProbGeom=escapeProbGeom)
        for i, T in enumerate(TB):
            line = { \
                'freq' : em.data.freq[u[i], l[i]], \
                    'upper' : u[i], \
                    'lower' : l[i], \
                    'Tupper' : em.data.levTemp[u[i]], \
                    'Tex' : em.data.dT[u[i],l[i]] / \
                    np.log( em.data.levWgt[u[i]]*em.levPop[l[i]] / \
                             (em.data.levWgt[l[i]]*em.levPop[u[i]]) ), \
                    'lumPerH' : lumPerH[i], \
                    'intIntensity' : intIntensity[i], \
                    'intTB' : TB[i], \
                    'tau' : tau[i], \
                    'tauDust' : tauDust[i] }
            outDict.append(line)
        return outDict


########################################################################
# Method to compute the line profile for a specified transition,
# assuming that the gas is in LTE
########################################################################
    def lineProfLTE(self, emitName, u, l, offset=0.0, vOut=None, \
                        vLim=None, \
                        nOut=100, dv=None, denProf=None, \
                        TProf=None, vProf=None, sigmaProf=None):
        """
        Return the brightness temperature versus velocity for a
        specified line, assuming the level populations are in LTE.

        Parameters
        ----------
        emitName : string
            emitter for which the computation is to be made
        u : int
            upper state of line to be computed
        l : int
            lower state of line to be computed
        offset : float
                 fractional distance from cloud center at which
                 measurement is made; 0 = at cloud center, 1 = at
                 cloud edge; valid values are 0 - 1
        vOut : array
            array of velocities (relative to line center at 0) at
            which the output is to be returned
        vLim : array (2)
            maximum and minimum velocities relative to line center at
            which to compute TB
        nOut : int
            number of velocities at which to output
        dv : float
            velocity spacing at which to produce output
        denProf : function denProf(r), r = float, returns float
            function that returns density of the emitting species (in
            H cm^-3) as a function of radius r within the cloud, where
            r is normalized so that the cloud center is 0, and the
            cloud edge is 1. If not set, the cloud density is assumed
            to be uniform with value nH * abundance of emitter.
        TProf : function Tprof(r), r = float, returns float
            same as denProf, but returning temperature (in K)
            vs. radius; if not set, temperature is taken to be Tg at
            all points
        vProf : function vProf(r), r = float, returns float
            same as denProf, but returning radial velocity (in cm
            s^-1) vs. r; the convention is that outward velocities are
            positive; if not set, velocity is v + r dv/dr
        sigmaProf : function sigmaProf(r), r = float, returns float
            same as denProf, but returning the non-thermal velocity
            dispersion (in cm s^-1) vs. r; if not set, this value is
            taken to be sigmaNT at all points

        Returns
        -------
        TB : array
             brightness temperature as a function of velocity (in K)
        vOut : array
               velocities at which TB is computed (in cm s^-1)
        """

        # Step 1: safety check
        if not emitName in self.emitters:
            raise despoticError, 'unknown emitter '+emitName
        if self.emitters[emitName].EinsteinA[u,l] == 0.0:
            raise depoticError, 'no radiative transition from state ' \
                +str(u)+' to state '+str(l)+' found for species ' \
                +emitName
        if offset < 0.0 or offset > 1.0:
            raise despoticError, 'offset must be in the range 0 - 1'

        # Step 2: construct list of velocities at which to output
        if vOut == None:
            if dv == None:
                if vLim == None:
                    # No input given, so take velocity limits to be
                    # offset from line center by max of 3*sigma + v
                    if sigmaProf == None:
                        sigmaMax = self.sigmaNT
                    else:
                        sigmaMax = max(sigmaProf(0), sigmaProf(1))
                    if vProf == None:
                        vMax = abs(self.dVdr * self.colDen/self.nH)
                    else:
                        vMax = max(vProf(0), vProf(1))
                    vLim = [-3*sigmaMax-vMax, 3*sigmaMax+vMax]
                # Compute vOut from vLim and nOut
                vOut = np.arange(vLim[0], vLim[1]*(1.0+1e-6), \
                                  (vLim[1]-vLim[0])/nOut)
            else:
                # dv is non-zero, so set velocities from dv and nOut
                vOut = np.arange(-dv*(nOut/2.0), \
                                   dv*(nOut/2.0+1.0e-6), dv)

        # Step 3: compute normalization constants
        if TProf==None:
            T0 = self.Tg
        else:
            T0 = TProf(1)
        if sigmaProf==None:
            sigma0 = self.sigmaNT
        else:
            sigma0 = sigmaProf(1)
        if vProf==None:
            v0 = self.dVdr * (self.colDen/self.nH)
        else:
            v0 = vProf(1)
        if denProf==None:
            d0 = self.nH * self.emitters[emitName].abundance
        else:
            d0 = denProf(1)

        # Step 4: compute dimensionless ratios and scalings
        cs0 = np.sqrt(kB*T0/(mH*self.emitters[emitName].molWgt))
        beta = v0/c
        betas0 = cs0/c
        betas = sigma0 / cs0
        wavelength = c / self.emitters[emitName].data.freq[u,l]

        prefac = self.emitters[emitName].data.levWgt[u] * \
            np.exp(-self.emitters[emitName].levTemp[l]/T0) / (4*np.pi)

        I0 = self.emitters[emitName].EinsteinA[u,l] * h * \
            self.colDen * self.emitters[emitName].abundance
        Theta = (self.emitters[emitName].levTemp[u] - \
                     self.emitters[emitName].levTemp[l]) / T0
        tau = self.colDen * self.emitters[emitName].abundance * \
            self.emitters[emitName].EinsteinA[u,l] * c**2 / \
            (2.0*self.emitters[emitName].freq[u,l]**3)
        partFunc = self.emitters[emitName].partFunc
        g0 = self.emitters[emitName].levWgt[l]
        g1 = self.emitters[emitName].levWgt[u]

        print T0, tau, boltzFac0, Theta, beta0, betas0, Mach0, \
            offset, g0, g1

        # Step 4: integrate the transfer equation at the specified
        # velocities
        iOut = np.zeros(len(vOut))
        for i, v in enumerate(vOut):
            f = 1 + v/c   # Frequency normalized to line-center value
            iOut[i] = \
                odeint(transferEqn, 0, \
                                     [-np.sqrt(1.0-offset**2), \
                                           np.sqrt(1.0-offset**2)], \
                                     args=(f, T0, tau, Theta, \
                                               beta0, betas0, \
                                               Mach0, offset, \
                                               g0, g1, boltzFac0, partFunc, \
                                               denProf, TProf, \
                                               vProf, sigmaProf))[1]

        # Step 5: convert intensities to brightness temperatures
        TB = h*self.emitters[emitName].freq[u,l]/kB / \
            log(1.0+2.0*h*self.emitters[emitName].freq[u,l]**3 / \
                    (c**2*iOut*I0))

        # Step 6: return
        return TB, vOut
            


########################################################################
# End of class gasProp
########################################################################



########################################################################
# Helper function to return the residuals for calculation of gas and
# dust temperatures. The function takes as its primary argument a
# two-element vector giving (Tgas, Tdust). Additional
# arguments are:
#    cloud -- the calling cloud
#    TCMB -- CMB temperature
#    TradDust -- radiation field temperature seen by the dust
#    zetaCR -- cosmic ray ionization rate
#    GammaPE0 -- photoelectric heating rate in *unattenuated* gas;
#               actual heating rate will be reduced due to dust
#               opacity
#    c1Grav -- coefficient to describe heating rate due to
#              gravitational compression; rate = c1Grav * c_s**2 *
#              sqrt(4 pi G rho) * mu_H * m_H
#    lumScale -- luminosity scale in the problem, used to normalize
#                the dEdt values calculated by this routine. This is a
#                two-element vector, giving scales for gas and dust
#                independently, since they can be quite different.
#    thin -- Boolean; if true, gas is assumed to be optically thin
#    LTE -- Boolean; if true, gas is assumed to be in LTE
#    escapeProbGoem -- string; specified geoemetry to be assumed in
#         computing escape probabilities
#    PsiUser -- an optional user-specified function that gives extra
#        heating and cooling
#    noClump -- Boolean; if true, clumping factors are turned off
########################################################################
def _gdTempResid(Tgd, cloud, c1Grav, thin, LTE, \
                    escapeProbGeom, PsiUser, noClump, verbose):

    # Insert current dust and gas temperatures into cloud structure;
    # floor to CMB temperature to prevent numerical badness in case
    # the iterative solver has wantered off to negative values
    cloud.Tg = max(Tgd[0], cloud.rad.TCMB)
    cloud.Td = max(Tgd[1], cloud.rad.TCMB)
    if verbose:
        print ""
        print "***"
        print "setTempEq: calculating residual at Tg = " + \
            str(cloud.Tg) + " K, Td = " + str(cloud.Td) + " K..."

    # Get net heating / cooling rates
    rates = cloud.dEdt(c1Grav=c1Grav, thin=thin, LTE=LTE, \
                           escapeProbGeom=escapeProbGeom, \
                           sumOnly=True, PsiUser=PsiUser, \
                           noClump=noClump, \
                           verbose=verbose)

    # Print status
    if verbose:
        print "setTempEq: dE_gas/dt = " + str(rates['dEdtGas']) + \
            " erg s^-1 H^-1, dE_dust/dt = " + \
            str(rates['dEdtDust']) + " erg s^-1 H^-1, " + \
            "residuals = " + str(rates['dEdtGas']/rates['maxAbsdEdtGas']) + \
            " " + str(rates['dEdtDust']/rates['maxAbsdEdtDust'])

    # Return result
    return np.array([rates['dEdtGas'], rates['dEdtDust']]) \
        / np.array([rates['maxAbsdEdtGas'], rates['maxAbsdEdtDust']])


########################################################################
# Helper function to return the residuals for calculation of dust
# temperatures at fixed Tgas. The function takes the arguments:
#    Td -- dust temperature (float)
#    cloud -- the calling cloud
#    lumScale -- characteristic luminosity values
#    PsiUser -- an optional user-specified function that gives extra
#        heating and cooling
#    GammaSum -- sum of heating terms that don't depend on T_d
#    GammaSumMax -- maximum of absolute values of the heating terms
#        that go into GammaSum, needed for normalization
#    verbose -- verbose or not
########################################################################
def _dustTempResid(Td, cloud, PsiUser, GammaSum, GammaSumMax, verbose):

    # Insert current dust temperature into gas structure, with a floor
    # equal to the CMB floor to prevent numerical problems if the
    # rootfinder wanders into negative values
    cloud.Td = max(Td, small)

    # Get net heating / cooling rates
    rates = cloud.dEdt(dustCoolOnly=True, sumOnly=True, \
                           PsiUser=PsiUser, \
                           fixedLevPop=True, \
                           verbose=verbose)


    # Print status if verbose
    if verbose:
        print "_dustTempResid called with Td = "+str(cloud.Td) + \
            ", dEdt = " + str(GammaSum+rates['dEdtDust']) + \
            ", residual = " + \
            str((GammaSum+rates['dEdtDust'])/ \
                    max(GammaSumMax, rates['maxAbsdEdtDust']))

    # Return dE/dt with correct normalization
    return (GammaSum+rates['dEdtDust'])/ \
        max(GammaSumMax, rates['maxAbsdEdtDust'])


########################################################################
# Helper function to return the residuals for calculation of gas
# temperatures at fixed Tdust. The function takes the arguments:
#    Tg -- gas temperature (float)
#    cloud -- the calling cloud
#    c1Grav -- coefficient to describe heating rate due to
#              gravitational compression; rate = c1Grav * c_s**2 *
#              sqrt(4 pi G rho) * mu_H * m_H
#    thin -- Boolean; if true, gas is assumed to be optically thin
#    LTE -- Boolean; if true, gas is assumed to be in LTE
#    escapeProbGoem -- string; specified geoemetry to be assumed in
#        computing escape probabilities
#    PsiUser -- user-specified function to add extra heating / cooling
#        terms
#    noClump -- Boolean; if true, clumping factors are turned off
#    verbose -- verbose or not
########################################################################
def _gasTempResid(Tg, cloud, c1Grav, thin, LTE, \
                     escapeProbGeom, PsiUser, noClump, verbose):

    # Insert current dust temperature into gas structure, using CMB
    # temperature as a floor
    cloud.Tg = max(Tg, cloud.rad.TCMB)

    # Get net heating / cooling rates
    rates = cloud.dEdt(c1Grav=c1Grav, \
                           thin=thin, LTE=LTE, \
                           escapeProbGeom=escapeProbGeom, \
                           gasOnly=True, noClump=noClump, \
                           sumOnly=True, PsiUser=PsiUser)

    # If verbose, print status
    if verbose:
        print "_gasTempResid called with Tg = "+str(cloud.Tg) + \
            ", dEdt = " + str(rates['dEdtGas']) + \
            ", residual = " + \
            str(rates['dEdtGas']/rates['maxAbsdEdtGas'])


    # Return dE/dt with correct normalization
    return rates['dEdtGas']/rates['maxAbsdEdtGas']


########################################################################
# Helper function to return dEdt for gas and dust in a form that the
# ODE integrator is happy with. Arguments are:
#    Tg -- current gas temperature
#    time -- current time
#    cloud -- the calling cloud
#    c1Grav -- coefficient to describe heating rate due to
#              gravitational compression; rate = c1Grav * c_s**2 *
#              sqrt(4 pi G rho) * mu_H * m_H
#    thin -- Boolean; if true, gas is assumed to be optically thin
#    LTE -- Boolean; if true, gas is assumed to be in LTE
#    escapeProbGoem -- string; specified geoemetry to be assumed in
#         computing escape probabilities
#    PsiUser -- user-specified function to add extra heating / cooling
#        terms
#    noClump -- Boolean; if true, clumping factors are turned off
#    isobar -- float; if > 0, this gives the fixed value of n*T; if
#        <= 0, this indicates the calculation is done isochorically,
#        i.e. n = constant
########################################################################
def _gasTempDeriv(Tg, time, cloud, c1Grav, thin, LTE, \
                      escapeProbGeom, PsiUser, noClump, isobar, \
                      dampFactor, verbose):

    # Update temperature
    cloud.Tg = Tg[0]

    # If we're isobaric, update density
    if isobar > 0:
        cloud.nH = isobar / cloud.Tg

    if verbose:
        print "t = "+str(time)+": Tg = "+str(cloud.Tg) + \
            ", nH = "+str(cloud.nH)

    # Compute new dust temperature
    cloud.setDustTempEq(PsiUser=PsiUser, verbose=verbose, \
                            dampFactor=dampFactor)

    # Call dEdt to get time rate of change of energy for gas; note
    # that the level populations do not need to be recomputed here,
    # because they were already computed in solving for the dust
    # temperature value, whcih depends on the line heating rate
    rates = cloud.dEdt(c1Grav=c1Grav, \
                           thin=thin, LTE=LTE, \
                           escapeProbGeom=escapeProbGeom, \
                           gasOnly=True, noClump=noClump, \
                           sumOnly=True, PsiUser=PsiUser, \
                           fixedLevPop=True)
    dEdtGas = rates['dEdtGas']

    # Compute specific heat c_v at current temperature
    cloud.comp.computeCv(cloud.Tg)

    # Convert from dE/dt to dTemp/dt by dividing by the c_V
    if isobar > 0:
        if verbose:
            print "dE/dt = "+str(dEdtGas)+", dT/dt = " + \
                str(dEdtGas/((cloud.comp.cv+1.0)*kB))
        return dEdtGas/((cloud.comp.cv+1.0)*kB)
    else:
        if verbose:
            print "dE/dt = "+str(dEdtGas)+", dT/dt = " + \
                str(dEdtGas/((cloud.comp.cv)*kB))
        return dEdtGas/(cloud.comp.cv*kB)
