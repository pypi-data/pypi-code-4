'''Calculation instances correspond to a particular VASP calculation and
contains:
    -The necessary inputs to recreate the calculation
    -The interesting outputs
    -Make needed changes to fix problems encountered while running

'''

import os
import copy
import json
import time
import numpy as np
from os.path import exists, isfile, isdir

from django.db import models

from dev_qmpy.models.composition import Composition
from dev_qmpy.models.element import *
from dev_qmpy.models.structure import Structure, Atom
from dev_qmpy.utils import *

class VaspError(Exception):
    '''General problem with vasp calculation.'''

class VaspZPOTRFError(VaspError):
    '''VASP encountered ZPOTRF error'''

class VaspSGRCONError(VaspError):
    '''VASP encountered SGRCON error'''

class VaspINVGRPError(VaspError):
    '''VASP encountered INVGRP error'''

class VaspBRIONSError(VaspError):
    '''VASP encountered a BRIONS problems error'''

class VaspFEXCFError(VaspError):
    '''VASP encountered'''

class VaspFEXCPError(VaspError):
    '''VASP encountered'''

class VaspPRICELError(VaspError):
    '''VASP encountered'''

class VaspEDDDAVError(VaspError):
    '''VASP encountered'''

class VaspNotHermitianError(VaspError):
    '''VASP encountered'''

class VaspBRMIXError(VaspError):
    '''VASP encountered'''

class VaspIncompleteError(VaspError):
    '''VASP did not complete the calculation'''

class VaspElectronicConvergenceError(VaspError):
    '''VASP did not reach electronic convergence'''

class VaspIonicConvergenceError(VaspError):
    '''VASP did not reach ionic convergence'''

class VaspDOSCARError(VaspError):
    '''Not able to read the DOSCAR correctly'''

class VaspInputError(VaspError):
    '''Not able to read inputs correctly'''

class VaspAttemptsError(VaspError):
    '''VASP failed to successfully complete too many times in a row'''

class VaspIonsCloseError(VaspError):
    '''VASP found ions too close together'''

class VaspMultirunError(VaspError):
    '''VASP was run multiple times over simultaneously, leading to unparseable
    outputs'''

class VaspBandsError(VaspError):
    '''VASP encountered fill bands at some k-points, at some ionic step'''

class Calculation(models.Model):
    # labeling
    settings = models.CharField(db_index=True, max_length=15, 
            null=True, blank=True)
    hubbard_set = models.ManyToManyField('Hubbard')
    potential_set = models.ManyToManyField('Potential')

    entry = models.ForeignKey('Entry', db_index=True, 
            null=True, blank=True)
    path = models.CharField(max_length=255, null=True, db_index=True)
    args = models.CharField(max_length=255, default=json.dumps([]))
    attempt = models.IntegerField(default=0)
    done = models.BooleanField(blank=True)

    composition = models.ForeignKey('Composition', 
            null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True, 
            null=True, blank=True)
    formula = models.CharField(max_length=255, db_index=True, 
            null=True, blank=True)

    # inputs
    #   -Structure
    input = models.ForeignKey(Structure, related_name='calculations',
            null=True, blank=True)

    #   -General
    prec = models.CharField(max_length=10, null=True, blank=True)
    istart = models.IntegerField(default=1)
    icharg = models.IntegerField(default=1)
    ispin = models.IntegerField(default=1)
    lsorbit = models.BooleanField(default=False)
    nelect = models.FloatField(blank=True, null=True)
    ldau = models.BooleanField(default=False)

    # parallization
    npar = models.IntegerField(default=2)
    ncore = models.IntegerField(blank=True, null=True)
    nsim = models.IntegerField(blank=True, null=True)
    lplane = models.IntegerField(default=True)
    kpar = models.IntegerField(blank=True, null=True)

    #   -electronic relaxation 1
    encut = models.FloatField(null=True, blank=True)
    enaug = models.FloatField(null=True, blank=True)
    nelm = models.IntegerField(default=60)
    nelmin = models.IntegerField(default=2)
    ediff = models.FloatField(default=0.1E-3)
    lreal = models.CharField(max_length=10, default='false')
    lmaxmix = models.IntegerField(default=2)
    voskown = models.IntegerField(default=0)

    #   -Ionic relaxation
    ediffg = models.FloatField(default=0.1E-02)
    nsw = models.IntegerField(default=0)
    ibrion = models.IntegerField(default=0)
    isif = models.IntegerField(default=2)
    isym = models.IntegerField(default=1)
    pstress = models.FloatField(default=0.0)
    potim = models.FloatField(default=0.5)
    symprec = models.FloatField(default=1e-5)

    #   -DOS related
    nbands = models.IntegerField(null=True, blank=True)
    ismear = models.IntegerField(default=0)
    sigma = models.FloatField(default=0.2)

    #   -electronic relaxation 2
    algo = models.CharField(max_length=15, default='normal')
    amix = models.FloatField(default=0.4)
    bmix = models.FloatField(default=1.0)
    maxmix = models.IntegerField(default=-45)

    #   -write fields
    lwave = models.BooleanField(default=False)
    lcharg = models.BooleanField(default=True)
    lvtot = models.BooleanField(default=False)
    lvhar = models.BooleanField(default=True)
    lelf = models.BooleanField(default=True)
    lorbit = models.IntegerField(default=11)

    #   -dipol fields
    ldipol = models.BooleanField(default=False)
    idipol = models.IntegerField(default=0)
    epsilon = models.FloatField(null=True, blank=True)

    #   - custom fields
    custom = models.TextField(blank=True, null=True)
    
    #kpoints
    kppra = models.IntegerField(null=True, blank=True)
    irreducible_kpoints = models.IntegerField(null=True, blank=True)
    gamma = models.BooleanField(default=True)
    
    # outputs
    energy = models.FloatField(null=True, blank=True)
    energy_pa = models.FloatField(null=True, blank=True)
    magmom = models.FloatField(default=0)
    magmom_pa = models.FloatField(default=0)
    band_gap = models.FloatField(blank=True, null=True)
    fermi = models.FloatField(blank=True, null=True)
    volume = models.FloatField(null=True, blank=True)
    volume_pa = models.FloatField(null=True, blank=True)
    output = models.ForeignKey(Structure, 
            related_name='origin',
            null=True, blank=True)

    niter = models.IntegerField(default=0)
    econverged = models.NullBooleanField(null=True)
    fconverged = models.NullBooleanField(null=True)
    voluntary = models.NullBooleanField(null=True)
    runtime = models.FloatField(default=0)
    errors = models.CharField(max_length=255, default=json.dumps([]))

    class Meta:
        db_table = 'calculations'

    def __str__(self):
        if self.settings is not None:
            return '%s : %s' % (comp_to_name(self.input.comp), self.settings )
        else:
            return comp_to_name(self.input.comp)

    def __eq__(self, other):
        diff = []
        for attr in ['encut', 'prec', 'lreal', 'potentials']:
            if getattr(self, attr) is None:
                continue
            elif getattr(other, attr) is None:
                diff.append([ attr, 
                    getattr(self, attr),
                    getattr(other, attr)])
            elif getattr(self, attr) != getattr(other, attr):
                diff.append([ attr, 
                    getattr(self, attr),
                    getattr(other, attr)])

        if other.ispin < self.ispin:
            diff.append(['ispin', self.ispin, other.ispin])

        if self.hubbard:
            if not other.hubbard:
                diff.append(['hubbard', self.hubbards, other.hubbards ])
            else:
                for hub in self.hubbards:
                    if hub and hub not in other.hubbards:
                        diff.append(['hubbard', hub, None])
                for hub in other.hubbards:
                    if hub and hub not in self.hubbards:
                        diff.append(['hubbard', None, hub])
        if self.nsw > 0:
            if other.nsw <= 1:
                diff.append(['nsw', self.nsw, other.nsw])
        self.diff = diff
        other.diff = diff
        if diff:
            return False
        else:
            return True


    ### magic functions and other "builtins"

    def save(self, *args, **kwargs):
        if self.output is not None:
            self.output.save()
            self.output = self.output
            self.output.entry = self.entry
        if self.input is not None:
            self.input.save()
            self.input = self.input
            self.input.entry = self.entry
            self.composition = self.input.composition
        self.name = comp_to_name(self.input.comp, special='reduce')
        super(Calculation, self).save(*args, **kwargs)
        if hasattr(self, 'new_hubbards'):
            for hub in self.new_hubbards:
                self.hubbard_set.add(hub)
            del self.new_hubbards
        if hasattr(self, 'new_potentials'):
            for pot in self.new_potentials:
                self.potential_set.add(pot)
            del self.new_potentials

    def add_potential(self, potential):
        if not hasattr(self, 'new_potentials'):
            self.new_potentials = []
        self.new_potentials.append(potential)

    def add_hubbard(self, hubbard):
        if not hasattr(self, 'new_hubbards'):
            self.new_hubbards = []
        self.new_hubbards.append(hubbard)

    def add_potential(self, pot):
        if not hasattr(self, 'new_potentials'):
            self.new_potentials = []
        self.new_potentials.append(pot)

    @property
    def potentials(self):
        if hasattr(self, 'new_potentials'):
            return sorted(set(self.new_potentials), key=lambda x: x.element.symbol)
        elif self.id is None:
            return []
        return sorted(self.potential_set.distinct().all(), key=lambda x: x.element.symbol)

    @property
    def hubbards(self):
        if hasattr(self, 'new_hubbards'):
            return sorted(set(self.new_hubbards), key=lambda x:x.element.symbol)
        elif self.id is None:
            return []
        return sorted(self.hubbard_set.all(), key=lambda x:x.element.symbol)

    def get_args(self):
        return json.loads(self.args)

    def set_args(self, args):
        self.args = json.dumps(args)

    @property
    def comp(self):
        return defaultdict(int,
                name_to_comp(self.formula))

    @property
    def unit_comp(self):
        return defaultdict(float,
                name_to_comp(self.formula, special='unit'))

    @property
    def hubbard(self):
        return any( h for h in self.hubbards )

    ## setup stuff 
    @property
    def INCAR(self):
        incar = '# General\n'
        if not self.prec is None: 
            incar += ' PREC = %s\n' % self.prec.upper()
        if not self.istart is None:
            incar += ' ISTART = %s\n' % self.istart
        if not self.icharg is None:
            incar += ' ICHARG = %s\n' % self.icharg
        incar += self.input.INCAR
        if self.lsorbit:
            incar += ' LSORBIT = .TRUE.\n'
        if self.nelect is not None:
            incar += ' NELECT = %s\n' % self.nelect

        incar += '\n# parallization\n'
        incar += ' NPAR = %s\n' % self.npar
        if self.lplane:
            incar += ' LPLANE = .TRUE.\n'
        else:
            incar += ' LPLANE = .FALSE.\n'
        if self.nsim:
            incar += ' NSIM = %s\n' % self.nsim
        if self.ncore:
            incar += ' NCORE = %s\n' % self.ncore
        if self.kpar:
            incar += ' KPAR = %s\n' % self.kpar

        incar += '\n# electronic relaxation 1\n'
        if self.encut:
            incar += ' ENCUT = %s\n' % self.encut
        #if self.enaug:
        #    incar += ' ENAUG = %s\n' % self.enaug
        incar += ' NELM = %s\n' % self.nelm
        incar += ' NELMIN = %s\n' % self.nelmin
        incar += ' EDIFF = %s\n' % self.ediff
        if self.lreal is not None:
            incar += ' LREAL = %s\n' % self.lreal.upper()
        if self.voskown: incar += ' VOSKOWN = TRUE\n'

        incar += '\n# Ionic relaxation\n'
        incar += ' IBRION = %s\n' %  self.ibrion
        incar += ' ISIF = %s\n' % self.isif
        incar += ' NSW = %s\n' % self.nsw
        incar += ' ISYM = %s\n' % self.isym
        if not self.symprec is None:
            incar += ' SYMPREC = %s\n' % self.symprec
        incar += ' POTIM = %s\n' % self.potim

        incar += '\n# DOS related\n'
        if not self.nbands is None: incar += ' NBANDS = %s\n' % self.nbands
        if not self.ismear is None: incar += ' ISMEAR = %s\n' % self.ismear
        if not self.sigma is None: incar += ' SIGMA = %s\n' % self.sigma

        incar += '\n# electronic relaxation 2\n'
        incar += ' ALGO = %s\n' % self.algo.upper()
        incar += ' AMIX = %s\n' % self.amix
        incar += ' BMIX = %s\n' % self.bmix
        incar += ' MAXMIX = %s\n' % self.maxmix

        incar += '\n# write fields\n'
        if self.lwave: 
            incar += ' LWAVE = .TRUE.\n'
        else:
            incar += ' LWAVE = .FALSE.\n'
        if self.lcharg: 
            incar += ' LCHARG = .TRUE.\n'
        else:
            incar += ' LCHARG = .FALSE.\n'
        if self.lvtot: 
            incar += ' LVTOT = .TRUE.\n'
        else:
            incar += ' LVTOT = .FALSE\n'
        if self.lvhar:
            incar += ' LVHAR = .TRUE.\n'
        else:
            incar += ' LVHAR = .FALSE.\n'
        if self.lelf: 
            incar += ' LELF = .TRUE.\n'
        else:
            incar += ' LELF = .FALSE.\n'
        incar += ' LORBIT = %s\n' % int(self.lorbit)

        if self.ldipol:
            incar += '\n# dipole fields\n'
            incar += ' LDIPOL = .TRUE.\n'
            incar += ' IDIPOL = %s\n' % self.idipol
            incar += ' EPSILON = %s\n' % self.epsilon


        if not self.custom is None:
            incar += '\n# custom\n'   
            incar += '%s\n' % self.custom.upper()

        if  any(hub for hub in self.hubbards):
            incar += '\n# LDA+U fields\n'
            incar += ' LDAU = .TRUE.\n'
            incar += ' LDAUPRINT = 1\n'
            uvals = ' '.join(str(hub.ldau_u) for hub in self.hubbards)
            jvals = ' '.join('0' for hub in self.hubbards)
            lvals = ' '.join(str(hub.ldau_l) for hub in self.hubbards)
            incar += ' LDAUU = %s\n' % uvals
            incar += ' LDAUJ = %s\n' % jvals
            incar += ' LDAUL = %s\n' % lvals
        return incar

    @INCAR.setter
    def INCAR(self, incar):
        custom = ''
        magmoms = []
        ldauus = []
        ldauls = []
        ldaujs = []
        for line in open(incar):
            line = line.lower()
            # general
            if 'prec' in line:
                self.prec = line.split()[-1]
            elif 'encut' in line:
                self.encut = line.split()[-1]
            elif 'isif' in line:
                self.isif = line.split()[-1]
            elif 'ibrion' in line:
                self.ibrion = line.split()[-1]
            elif 'nbands' in line:
                self.nbands = line.split()[-1]
            elif 'lreal' in line:
                self.lreal = line.split()[-1]
            elif 'ismear' in line:
                self.ismear = line.split()[-1]
            elif 'sigma' in line:
                self.sigma = line.split()[-1]
            elif 'ldauu' in line:
                ldauus = line.split()[2:]
            elif 'ldaul' in line:
                ldauls = line.split()[2:]
            elif 'magmom' in line:
                magmoms = line.split()[2:]
            else:
                custom += line

        if self.input is not None:
            atom_types = []
            for atom in self.input.atoms:
                if atom.element.symbol in atom_types:
                    continue
                atom_types.append(atom.element.symbol)
            if ldauus and ldauls:
                #assert len(ldauus) == len(ldauls) == len(atom_types)
                for elt, u, l in zip(atom_types, ldauus, ldauls):
                    hub, created = Hubbard.objects.get_or_create(element_id=elt,
                            ldau_u=u, ldau_l=l, with_elt=None)
                    #if created:
                    #    hub.save()
                    self.add_hubbard(hub)
            if magmoms:
                real_moms = []
                for mom in magmoms:
                    if '*' in mom:
                        num, mom = mom.split('*')
                        real_moms += [mom]*int(num)
                    else:
                        real_moms.append(mom)
                for atom, mom in zip(self.input.atoms, real_moms):
                    atom.magmom = float(mom)
                    if atom.id is not None:
                        atom.save()

    @property
    def KPOINTS(self):
        n = float(len(self.input.atoms))
        refr = self.input.relative_rec_lat
        scale = 1.0
        kpts = np.ones(3)
        while n*np.product(kpts) < self.kppra:
            prev_kpts = kpts.copy()
            refk = np.array(np.ones(3)*refr)*scale
            kpts = np.array(map(np.ceil, refk))
            scale += 1
        if self.kppra - np.product(prev_kpts)*n < np.product(kpts)*n - self.kppra:
            kpts = prev_kpts.copy()
        if self.gamma:
            kpoints = 'KPOINTS \n0 \nGamma\n'
        else:
            kpoints = 'KPOINTS \n0 \nMonkhost-Pack\n'
        kpoints += ' '.join( str(int(k)) for k in kpts ) + '\n'
        kpoints += '0 0 0'
        return kpoints

    @KPOINTS.setter
    def KPOINTS(self, kpoints):
        raise NotImplementedError

    @property
    def POTCAR(self):
        potstr = ''
        for pot in self.potentials:
            potstr += pot.potcar
            potstr += ' End of Dataset\n'
        return potstr

    @POTCAR.setter
    def POTCAR(self, potcar):
        pots = Potential.read_potcar(potcar)
        for pot in pots:
            self.add_potential(pot)

    @property
    def POSCAR(self):
        return self.input.POSCAR

    @POSCAR.setter
    def POSCAR(self, poscar):
        self.input = Structure.create(poscar)

    def clear_outputs(self):
        if not os.path.exists(self.path):
            return
        for file in os.listdir(self.path):
            if os.path.isdir(self.path+'/'+file):
                continue
            if file in ['INCAR', 'POSCAR', 'KPOINTS', 'POTCAR',
                    'CHGCAR.gz']:
                continue
            os.unlink('%s/%s' % (self.path, file))

    def unpack(self):
        if 'OUTCAR.gz' in os.listdir(self.path):
            os.system('gunzip -f %s/OUTCAR.gz' % self.path)

    def pack(self):
        for file in os.listdir(self.path):
            if file in ['OUTCAR', 'CHGCAR', 'CHG', 'PROCAR', 'LOCPOT', 'ELFCAR']:
                os.system('gzip -f %s' % self.path+'/'+file)

    def copy(self):
        calc = copy.deepcopy(self)
        calc.id = None
        if self.input is not None:
            calc.input = self.input.copy()
        if self.output is not None:
            calc.output = self.output.copy()
        for p in self.potentials:
            calc.add_potential(p)
        for h in self.hubbards:
            calc.add_hubbard(h)
        return calc

    @staticmethod
    def read(path):
        '''
        Reads the outcar specified by the objects path. Populates input field
        values, as well as outputs, in addition to finding errors and
        confirming convergence.

        Example:
        >>> calc = Calculation.read('/path/to/calculation')
        '''
        if Calculation.objects.filter(path=path, done=True).exists():
            return Calculation.objects.get(path=path, done=True)

        calc = Calculation()
        calc.path = path
        try:
            calc.read_outcar()
            calc.check_stdout()
        except Exception, err:
            calc.add_error('exception: %s' % err)
            print '   -Exception:', err
        return calc

    def read_outcar(self):
        self.unpack()
        if not exists(self.path):
            return
        if not exists(self.path+'/OUTCAR'):
            return
        if len(open(self.path+'/OUTCAR').readlines()) < 100:
            return
        if not exists(self.path+'/CONTCAR'):
            return

        prev_attempts = []
        for dir in [d for d in os.listdir(self.path) if isdir(self.path+'/'+d)]:
            prev_attempts.append(d)
        self.attempt = len(prev_attempts)+1
        if self.attempt > 3:
            self.add_error('attempts')
        elif self.attempt > 30:
            self.add_error('3xattempts')

        outcar = open('%s/OUTCAR' % self.path,'r').readlines()
        stresses = []
        runcount = 0
        input_cell = []
        input_coords = []
        cell = []
        species = []
        coords = []
        forces = []
        magmoms = []
        charges = []
        look_for_total = False
        esteps = 0
        this_pot = {}
        ldauls = []
        ldauus = []
        atom_types = []
        for n, line in enumerate(outcar):
            line = line.strip()
            ### error lines
            if 'between ions is very small' in line:
                self.add_error('ions_close')
            elif 'Voluntary' in line:
                self.voluntary = True
                runcount += 1
                if runcount > 1:
                    self.add_error('multiruns')
            elif 'reached required accuracy' in line:
                self.fconverged = True
            elif '%s(' % self.nsw in line:
                self.add_error('ionic_convergence')
            elif 'highest band is occupied' in line:
                self.add_error('bands')

            ### input structure lines
            elif 'ions per type' in line:
                atom_types = []
                counts = line.split()[4:]
                int_counts = [ int(count) for count in counts ]
                assert len(int_counts) == len(species)
                for n, e in zip(int_counts, species):
                    atom_types += [Element.get(e)]*n
            elif 'nearest neighbor table' in line:
                i = 1
                cdata = outcar[n+i]
                while not 'LATTYP' in cdata:
                    if '-' in cdata:
                        input_coords.append([ float(v) for v in 
                            cdata.split('-')[0].split()[1:] ])
                    i += 1
                    cdata = outcar[n+i]
            elif 'A1 = (' in line:
                vec = line.split('(')[1].strip(')')
                vals = [ float(v.strip()) for v in vec.split(',') ]
                input_cell.append(vals)
            elif 'A2 = (' in line:
                vec = line.split('(')[1].strip(')')
                vals = [ float(v.strip()) for v in vec.split(',') ]
                input_cell.append(vals)
            elif 'A3 = (' in line:
                vec = line.split('(')[1].strip(')')
                vals = [ float(v.strip()) for v in vec.split(',') ]
                input_cell.append(vals)

            ### general options
            elif 'PREC' in line:
                self.prec = line.split()[2]
            elif 'ENCUT' in line:
                self.encut = line.split()[2]
            elif 'ENAUG' in line:
                self.enaug = line.split()[2]
            elif 'ISTART' in line:
                self.istart = line.split()[2]
            elif 'ISPIN' in line:
                self.ispin = int(line.split()[2])

            # electronic relaxation 1
            elif 'NELM' in line:
                self.nelm = int(line.split()[2].rstrip(';'))
                self.nelmin = int(line.split()[4].rstrip(';'))
            elif 'LREAL  =' in line:
                lreal = line.split()[2]
                if lreal == 'F':
                    self.lreal = 'false'
                elif lreal == 'A':
                    self.lreal = 'auto'
                elif lreal == 'T':
                    self.lreal = 'auto'

            # ionic relaxation 
            elif 'EDIFF  =' in line:
                self.ediff = line.split()[2]
            elif 'ISIF' in line:
                self.isif = line.split()[2]
            elif 'IBRION' in line:
                self.ibrion = line.split()[2]
            elif 'NSW' in line:
                self.nsw = line.split()[2].rstrip(';')
                if self.nsw <= 1:
                    self.fconverged = True
            elif 'PSTRESS' in line:
                self.pstress = line.split()[1]
            elif 'POTIM' in line:
                self.potim = line.split()[2]

            # DOS Flags
            elif 'ISMEAR' in line:
                line = line.split()
                self.ismear = line[2].rstrip(';')
                self.sigma = line[5]
            elif 'NBANDS=' in line:
                if not 'INCAR' in line:
                    self.nbands = int(line.split()[-1])

            # write flags
            elif 'LCHARG' in line:
                if line.split()[2] == 'F':
                    self.lcharg = False
            elif 'LWAVE' in line:
                if line.split()[2] == 'F':
                    self.lwave = False
            elif 'LVTOT' in line:
                if line.split()[2] == 'T':
                    self.lvtot = True
            elif 'LELF' in line:
                if line.split()[2] == 'T':
                    self.lelf = True
            elif 'LORBIT' in line:
                self.lorbit = line.split()[2]

            # electronic relaxation 2
            elif 'AMIX     =' in line:
                self.amix = line.split()[2].rstrip(';')
                self.bmix = line.split()[5]
            elif 'ALGO' in line:
                val = int(line.split()[2])
                if val == 38:
                    self.algo = 'normal'
                elif val == 68:
                    self.algo = 'fast'
                elif val == 48:
                    self.algo = 'very_fast'
                elif val == 58:
                    self.algo = 'all'
                elif val == 53:
                    self.algo = 'default'
            elif 'MAXMIX=' in line:
                self.maxmix = line.split()[-1]

            # dipole flags
            elif 'LDIPOL' in line:
                if line.split()[2] == 'T':
                    self.ldipol = True
            elif 'IDIPOL' in line:
                self.idipol = line.split()[2]
            elif ' EPSILON=' in line:
                self.epsilon = line.split()[1]

            # potentials
            elif 'POTCAR:' in line:
                this_pot = {'name':line.split()[2]}
                if not 'VRHFIN' in outcar[n+1]:
                    elt = line.split()[2].split('_')[0]
                    species.append(elt)
            elif 'Description' in line:
                pot = Potential.objects.get(**this_pot)
                self.add_potential(pot)
            elif 'LEXCH' in line:
                key = line.split()[2]
                if key == '91':
                    this_pot['xc'] = 'GGA'
                elif key == 'CA':
                    this_pot['xc'] = 'LDA'
                elif key == 'PE':
                    this_pot['xc'] = 'PBE'
            elif 'LULTRA' in line:
                key = line.split()[2]
                this_pot['us'] = ( key == 'T' )
            elif 'LPAW' in line:
                key = line.split()[2]
                this_pot['paw'] = ( key == 'T' )
            # hubbards
            elif 'LDAUL' in line:
                self.ldau = True
                ldauls = [ int(v) for v in line.split()[7:] ]
            elif 'LDAUU' in line:
                ldauus = [ float(v) for v in line.split()[7:] ]

            ### output structure lines
            if 'direct lattice vectors' in line:
                cell = []
                for i in range(3):
                    vec = []
                    vec.append(float(outcar[n+1+i][0:16]))
                    vec.append(float(outcar[n+1+i][16:29]))
                    vec.append(float(outcar[n+1+i][29:44]))
                    cell.append(vec)
            if self.ispin == 2 and 'magnetization (x)' in line:
                magmoms = []
                for ind in range(len(atom_types)):
                    magmoms.append(ffloat(outcar[n+4+ind].split()[-1]))
            if 'total charge' in line and not 'along one line' in line:
                charges = []
                for ind in range(len(atom_types)):
                    charges.append(ffloat(outcar[n+4+ind].split()[-1]))
            if 'POSITION' in line:
                coords = []
                forces = []
                for ind in range(len(atom_types)):
                    l = outcar[n+ind+2]
                    try:
                        l = l.split()
                    except:
                        l = [l[0:12], l[13:25], l[26:38], 
                                l[39:55], l[56:69],l[70:84]]
                    coords.append([ float(v) for v in l[0:3] ])
                    forces.append([ float(v) for v in l[3:6] ])

            ### output property lines
            if 'free  energy' in line:
                self.energy = ffloat(line.split()[4])
                self.energy_pa = self.energy/len(atom_types)
            if self.ispin == 2 and 'number of electron' in line:
                if len(line.split()) == 6:
                    self.magmom = abs(ffloat(line.split()[-1]))
                    self.magmom_pa = self.magmom/len(atom_types)
            if 'LOOP+' in line:
                if not len(line.split()) == 7:
                    continue
                self.runtime += ffloat(line.split()[-1].lstrip('time'))
            if 'irreducible' in line:
                self.irreducible_kpoints = int(line.split()[1])
            if 'volume of cell' in line:
                self.volume = ffloat(line.split()[-1])
                self.volume_pa = self.volume/len(atom_types)
            if 'Iteration' in line:
                if len(line.split()) == 5:
                    l = line.split()
                    self.niter = int(l[2].rstrip('('))
                    esteps = int(l[3].rstrip(')'))
            if 'FORCE on cell' in line:
                look_for_total = True
            if look_for_total and 'Total' in line:
                try:
                    stresses = [ ffloat(v) for v in line.split()[1:] ]
                except:
                    stresses = [ 
                            ffloat(line[9:20]), 
                            ffloat(line[21:32]), 
                            ffloat(line[33:44]),
                            ffloat(line[45:56]),
                            ffloat(line[57:68]),
                            ffloat(line[69:80])]
                look_for_total = False

        self.clean_fields()

        ### assign hubbard terms
        self.new_hubbards = []
        if ldauls and ldauus:
            self.ldau = True
            for elt, l, u in zip(species, ldauls, ldauus):
                hub, created = Hubbard.objects.get_or_create(
                        element_id=elt, ldau_u=u, ldau_l=l)
                if created:
                    hub.save()
                self.add_hubbard(hub)

        if esteps == self.nelm:
            self.econverged = False
        else:
            self.econverged = True

        if not self.voluntary:
            self.add_error('incomplete')
        elif not self.econverged and self.settings == 'standard':
            self.add_error('electronic_convergence')
        elif self.nsw > 1 and not self.fconverged:
            self.add_error('ionic_convergence')
        elif not self.get_errors():
            self.done = True

        ### create input structure
        if self.input is None:
            struct = Structure()
            struct.cell = input_cell
            for ind in range(len(atom_types)):
                atom = Atom()
                atom.element = atom_types[ind]
                atom.coord = input_coords[ind]
                struct.add_atom(atom)
            self.input = struct

        ### create output structure if applicable
        if self.niter > 1:
            output = Structure()
            output.cell = cell 
            output.stresses = stresses
            for ind in range(len(atom_types)):
                atom = Atom()
                atom.element = atom_types[ind]
                atom.direct = False
                atom.coord = coords[ind]
                atom.force = forces[ind]
                if magmoms: atom.magmom = magmoms[ind]
                if charges: atom.charge = charges[ind]
                output.add_atom(atom)
            self.output = output
        #else:
        #    self.output = self.input

        try:
            self.read_doscar()
        except:
            self.add_error('doscar_exc')
        self.pack()

    def read_doscar(self):
        if not os.path.exists(self.path+'/DOSCAR'):
            return None
        doscar = open(self.path+'/DOSCAR').readlines()
        bot = 0
        if len(doscar) < 20:
            return False
        for i in range(6):
            l=doscar.pop(0).rstrip()
        efermi = float(l.split()[3])
        self.fermi = efermi
        step1 = doscar.pop(0).split()[0]
        while step1 == '********':
            step1 = doscar.pop(0).split()[0]
        step2 = doscar.pop(0).split()[0]
        step_size = float(step2)-float(step1)
        not_found = True
        for l in doscar:
            l = l.split()
            if not not_found:
                break
            e = float(l.pop(0))
            dens = 0
            for i in range(len(l)/2):
                dens += float(l[i])
            if e < efermi and dens > 1e-3:
                bot = e
            elif e > efermi and dens > 1e-3:
                top = e
                not_found = False
            else:
                top = e
        if not bot:
            gap = 0
        else:
            if top - bot < step_size*2:
                gap = 0
            else:
                gap = top - bot
        if not not_found:
            self.band_gap = gap

    ### Error tracking stuff ###

    def add_error(self, error):
        errors = self.get_errors()
        if error not in errors:
            errors.append(error)
        self.errors = json.dumps(errors)

    def remove_error(self, error):
        errors = self.get_errors()
        if error in errors:
            errors.remove(error)
        self.errors = json.dumps(errors)

    def get_errors(self):
        return json.loads(self.errors)

    def check_stdout(self, filename='stdout.txt'):
        if not os.path.exists(self.path+'/'+filename):
            return
        stdout = open('%s/%s' % (self.path, filename)).read()
        if 'Error reading item' in stdout:
            self.add_error('input_error')
        if 'ZPOTRF' in stdout:
            self.add_error('zpotrf')
        if 'SGRCON' in stdout:
            self.add_error('sgrcon')
        if 'INVGRP' in stdout:
            self.add_error('invgrp')
        if 'BRIONS problems: POTIM should be increased' in stdout:
            self.add_error('brions')
        if 'FEXCF' in stdout:
            self.add_error('fexcf')
        if 'FEXCP' in stdout:
            self.add_error('fexcp')
        if 'PRICEL' in stdout:
            self.add_error('pricel')
        if 'EDDDAV' in stdout:
            self.add_error('edddav')
        if 'Sub-Space-Matrix is not hermitian in DAV' in stdout:
            self.add_error('hermitian')
        #if 'IBZKPT' in stdout:
        #    self.log += 'IBZKPT error'
        if 'BRMIX: very serious problems' in stdout:
            self.add_error('brmix')

    ### Problem solutions ###

    def address_errors(self):
        if not self.get_errors():
            print '   -Found no errors'
            return self
        
        new_calc = self.copy()
        errors = self.get_errors()
        
        #if errors == ['attempts']:
        #    new_calc.remove_error('attempts')
        #    return new_calc

        #if set(errors) == set(['ionic_convergence', 'attempts']):
        #    new_calc.remove_error('attempts')
        #    errors.remove('attempts')

        for err in errors:
            if err in ['duplicate','partial']:
                continue
            elif err == 'ionic_convergence':
                if self.niter > 1:
                    new_calc.remove_error('ionic_convergence')
                    new_calc.input = self.output.copy()
            elif err == 'electronic_convergence':
                new_calc.fix_electronic_convergence()
            elif err == 'doscar_exc':
                new_calc.fix_bands()
            elif err == 'bands':
                new_calc.fix_bands()
            elif err == 'edddav':
                new_calc.fix_dav()
            elif err == 'errrmm':
                new_calc.fix_rmm()
            elif err == 'sgrcon':
                new_calc.fix_sgrcon()
            elif err == 'zpotrf':
                new_calc.fix_zpotrf()
            elif err == 'invgrp':
                new_calc.fix_invgrp()
            elif err == 'exception':
                new_calc.clean_start()
            elif err == 'fexcf':
                new_calc.fix_fexcf()
            elif err == 'fexcp':
                new_calc.fix_fexcp()
            elif err == 'brions':
                new_calc.fix_brions()
            elif err == 'pricel':
                new_calc.fix_pricel()
            elif err == 'brmix':
                new_calc.fix_brmix()
            elif err == 'incomplete':
                continue
            elif err == 'hermitian':
                new_calc.fix_hermitian()
            else:
                print '   -Unsolvable error: %s' % err

        if 'incomplete' in new_calc.get_errors():
            if self.niter > 1:
                new_calc.input = self.output.copy()
                new_calc.remove_error('incomplete')
        if 'magnetic' in self.entry.keywords:
            new_calc.input.set_magnetism('ferro')
        return new_calc

    def move(self, path):
        path = os.path.abspath(path)
        try:
            os.system('mv %s %s' % (self.path, path))
        except Exception, err:
            print err
            return
        self.path = path
        self.save()

    def move_contents(self, path):
        path = os.path.abspath(path)
        try:
            os.system('mkdir %s &> /dev/null' % path)
            os.system('cp %s/* %s &> /dev/null' % (self.path, path))
            os.system('rm %s/* &> /dev/null' % self.path)
        except Exception, err:
            print err
            return
        self.path = path
        self.save()

    def backup(self):
        new_dir = '%s_' % self.attempt
        new_dir += '_'.join(self.get_errors())
        print '   -Backing up %s to %s' % (self.path, new_dir)
        self.move_contents(self.path+'/'+new_dir)

    def clean_start(self):
        depth = self.path.count('/') - self.path.count('..')
        if depth < 6:
            print '   -Too short path supplied to clean_start', self.path
            return
        else:
            print '   -Wiping path: %s' % self.path
            os.system('rm -rf %s &> /dev/null' % self.path)

    def fix_zhegev(self):
        raise NotImplementedError

    def fix_brmix(self):
        self.symprec = 1e-7
        self.algo = 'normal'
        self.remove_error('brmix')
        self.remove_error('incomplete')
        print '   -Fixed BRMIX error'

    def fix_fexcf(self):
        self.remove_error('fexcf')
        self.remove_error('incomplete')
        self.potim = 0.1
        self.algo = 'normal'
        print '   -Fixed FEXCF error'

    def fix_fexcp(self):
        self.remove_error('fexcp')
        self.remove_error('incomplete')
        self.potim = 0.1
        self.algo = 'normal'
        print '   -Fixed FEXCP error'

    def fix_pricel(self):
        self.remove_error('pricel')
        self.remove_error('incomplete')
        self.symprec=1e-7
        print '   -Fixed PRICEL error'

    def fix_electronic_convergence(self):
        if self.algo != 'normal':
            self.algo = 'normal'
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            print '   -switching to DAV'
        else:
            print '   -Can\'t fix electronic convergence.'

    def fix_invgrp(self):
        self.remove_error('invgrp')
        self.remove_error('incomplete')
        self.symprec=1e-7
        print '   -Fixed INVGRP error'

    def fix_sgrcon(self):
        self.remove_error('sgrcon')
        self.remove_error('incomplete')
        self.symprec=1e-7
        print '   -Fixed SGRCON error'

    def fix_brions(self):
        self.remove_error('brions')
        self.remove_error('incomplete')
        self.potim *= 2
        print '   -Fixed BRIONS problem'

    def fix_zpotrf(self):
        self.remove_error('zpotrf')
        self.remove_error('incomplete')
        self.algo = 'normal'
        self.potim = 0.1
        print '   -Fixed ZPOTRF error'

    def fix_bands(self):
        self.remove_error('bands')
        self.remove_error('incomplete')
        self.remove_error('doscar_exc')
        self.remove_error('electronic_convergence')
        self.nbands *= int(np.ceil(1.15))
        print '   -Fixed bands error: %s' % self.entry

    def fix_dav(self):
        if self.algo == 'fast':
            self.algo = 'very_fast'
            self.remove_error('edddav')
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            print '   -Error with DAV, switching to RMM'
        elif self.algo == 'normal':
            self.algo = 'very_fast'
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            self.remove_error('edddav')
            print '   -Problem with DAV and RMM. =/'
        elif self.algo == 'very_fast':
            print "   -Can't fix EDDDAV. Stopping."

    def fix_rmm(self):
        if self.algo == 'fast':
            self.algo = 'normal'
            self.remove_error('errrmm')
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            print '   -Error with RMM, switching to DAV'
        elif self.algo == 'very_fast':
            print '   -Problem with DAV and RMM. =/'
            self.algo = 'normal'
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            self.remove_error('errrmm')
        elif self.algo == 'normal':
            print "   -Can't fix RMM. Stopping."

    def fix_hermitian(self):
        if not self.algo == 'very_fast':
            self.algo = 'very_fast'
            self.remove_error('hermitian')
            self.remove_error('incomplete')
            self.remove_error('electronic_convergence')
            print "   -Fixing 'sub-space not hermitian' error."
        else:
            print "   -Can't fix 'sub-space not hermitian'. Stopping."

    #### calculation management

    def write(self):
        os.system('mkdir %s &> /dev/null' % self.path)
        poscar = open(self.path+'/POSCAR','w')
        potcar = open(self.path+'/POTCAR','w')
        incar = open(self.path+'/INCAR','w')
        kpoints = open(self.path+'/KPOINTS','w')
        poscar.write(self.POSCAR)
        potcar.write(self.POTCAR)
        incar.write(self.INCAR)
        kpoints.write(self.KPOINTS)
        poscar.close()
        potcar.close()
        incar.close()
        kpoints.close()

    @property
    def estimate(self):
        return 24*8*3600

    @property
    def instructions(self):
        if self.done:
            return {}
        elif self.get_errors():
            print '   -Still had errors:', self.get_errors()
            return {}

        instruction = {
                'path':self.path,
                'walltime':self.estimate,
                'header':'gunzip -f CHGCAR.gz &> /dev/null\ndate +%s\nulimit -s unlimited',
                'mpi':'mpirun -machinefile $PBS_NODEFILE -np $NPROCS',
                'binary':'vasp_53', 
                'pipes':' > stdout.txt 2> stderr.txt',
                'footer':'gzip -f CHGCAR OUTCAR PROCAR ELFCAR\nrm -f WAVECAR vasprun.xml\ndate +%s'}

        if self.input.natoms < 10:
            instruction.update({'mpi':'','binary':'vasp_53_serial',
                'serial':True})
        return instruction

    @staticmethod
    def do(input=None, type='standard', path=None, entry=None,
            args=[], hubbards='wang_act', potentials='oqmd_pbe', 
            **kwargs):
        
        t0 = time.time()
        # where to run
        if path is None:
            path = os.path.abspath(entry.path)
        else:
            path = os.path.abspath(path)

        print '   -Doing %s on %s!' % (type, entry)
        # is this an existing calculation in the given path?
        try:
            calc = Calculation.objects.get(path=path)
        except:
            # if the path doesn't exist
            if not os.path.exists(path):
                os.mkdir(path)

            calc = Calculation()
            calc.settings = type
            calc.path = path
            calc.input = input
            if any(a.magmom for a in calc.input.atoms):
                calc.ispin = 2
            calc.set_args(args)
            if entry:
                calc.entry=entry

        if calc.done:
            print 'Calc is done'
            return calc

        # 2
        ps = PotentialSet.objects.get(name=potentials)

        for elt1 in calc.input.elements:
            if elt1.induced_hubbards.filter(hubbardset__name=hubbards).exists():
                for elt2 in calc.input.elements:
                    hub, created = elt1.induced_hubbards.get_or_create(
                            element=elt2)
                    if created:
                        hub.save()
                    calc.add_hubbard(hub)

        for elt in calc.input.elements:
            calc.add_potential(ps.get(elt.symbol))

        calc.npar = 2
        if calc.input.natoms > 20:
            calc.lreal = 'auto'

        for k, v in vasp_settings[type].items():
            setattr(calc, k, v)

        if 'scale_encut' in vasp_settings:
            enmax = max(pot.enmax for pot in calc.potentials)
            calc.encut = int(vasp_settings['scale_encut']*enmax)

        if set(calc.get_errors()) <= set(['attempts', 'ionic_convergence']):
            calc.remove_error('attempts')
            calc.remove_error('ionic_convergence')

        # has the calculation been run yet?
        if not ( (os.path.exists(calc.path+'/OUTCAR') or 
            os.path.exists(calc.path+'/OUTCAR.gz')) and 
            os.path.exists(calc.path+'/CONTCAR')):
            ### but has it been written?
            if not ( os.path.exists(calc.path+'/INCAR') and
                    os.path.exists(calc.path+'/POTCAR') and 
                    os.path.exists(calc.path+'/KPOINTS') and
                    os.path.exists(calc.path+'/POSCAR')):
                calc.write()
            return calc

        calc.read_outcar()
        calc.check_stdout()

        if calc.done:
            return calc
        elif not calc.get_errors():
            calc.write()
            return calc
        
        fixed_calc = calc.address_errors()
        calc.backup()
        fixed_calc.clear_outputs()
        fixed_calc.write()
        return fixed_calc
