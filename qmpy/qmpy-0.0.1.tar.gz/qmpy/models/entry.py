from django.db import models
from getpass import getuser
from collections import defaultdict
import os
import json
from datetime import datetime
from ase.io.cif import read_cif, parse_cif
import time

from resources import Project
from structure import Structure
from experiment import ICSD, Reference, Journal, Author
from composition import Composition
from calculation import Calculation
from thermodynamics import *
from element import Element
from utils import *
from grid import Grid

class Entry(models.Model):
    '''
    An Entry is a structure submitted to the database. This entry can then be:
        - checked for uniqueness
        - relaxed and evaluated
        - checked for ferro vs anti-ferromagnetism (tbd)
        - compared to other entries at the same composition
    '''

    ### structure properties
    path = models.CharField(max_length=255, db_index=True, unique=True)
    source_file = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, db_index=True, null=True)
    formula = models.CharField(max_length=255, db_index=True, null=True)

    ntypes = models.IntegerField(blank=True, null=True)
    natoms = models.IntegerField(blank=True, null=True)
    keywords = models.CharField(max_length=255, default='')
    label = models.CharField(max_length=20, null=True)
    holds = models.CharField(max_length=255, default='')
    log = models.TextField(default='')
    unique = models.BooleanField(default=False)
    stable = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    ## links
    composition = models.ForeignKey('Composition', null=True)
    element = models.ManyToManyField('Element', null=True)
    reference = models.ForeignKey('Reference', null=True)
    icsd = models.OneToOneField('ICSD', related_name='entry',
            null=True, blank=True)
    project = models.ForeignKey(Project, blank=True, null=True)

    class Meta:
        db_table = 'entries'

    def __str__(self):
        return '%s : %s' % (self.id, self.name)

    def save(self, *args, **kwargs):
        super(Entry, self).save(*args, **kwargs)
        if hasattr(self, 'new_elements'):
            for elt in self.new_elements:
                self.element.add(elt)
            del self.new_elements
        if hasattr(self, 'new_structures'):
            for struct in self.new_structures:
                self.structure_set.add(struct)
            del self.new_structures

    ###
    ###  Creation
    ###

    @staticmethod
    def create(source, keywords=[], project=None, **kwargs):
        source_file = os.path.abspath(source)
        path = os.path.dirname(source_file)
        if Entry.objects.filter(path=path).exists():
            return Entry.objects.get(path=path)
        entry = Entry(**kwargs)
        entry.source_file = source_file
        entry.path = os.path.dirname(source_file)

        ## Read in source file
        if source_file.endswith('.cif'):
            try:
                poscar = cif_to_poscar(source_file)
                f = open(entry.path+'/POSCAR','w')
                f.write(poscar)
                f.close()
            except Exception, err:
                print 'ERROR:', err
                print 'path:', source_file
                a = read(source_file)
                write_vasp(entry.path+'/POSCAR', a, vasp5=True, direct=True)
            structure = Structure.create(entry.path+'/POSCAR')
        else:
            structure = Structure.create(source_file)
        
        entry.add_structure(structure, label='source')
        entry.formula = comp_to_formula(structure.comp)
        entry.name = comp_to_name(structure.comp, special='reduce')
        entry.assign_composition()
        entry.assign_elements()
        entry.ntypes = structure.ntypes
        entry.natoms = len(structure.atoms)

        for k in keywords:
            entry.add_keyword(k)
        if project is not None:
            entry.set_project(project)
        if source_file.endswith('.cif'):
            entry.read_addtl_cif_data()
        entry.write_log('created %s' % datetime.now())
        return entry

    ## helpers for filling in fields
    def assign_composition(self):
        composition = Composition.get(self.comp)
        self.composition = composition

    def assign_elements(self):
        for k in self.comp.keys():
            elt = Element.get(k)
            self.add_element(elt)

    def add_element(self, elt):
        if not hasattr(self, 'new_elements'):
            self.new_elements = []
        self.new_elements.append(elt)

    def read_addtl_cif_data(self):
        if not self.source_file.endswith('.cif'):
            return

        cif_data = parse_cif(self.source_file)[0][1]
        journal, created =\
                Journal.objects.get_or_create(code=cif_data['_citation_journal_id_astm'][0])
        if created:
            journal.full_name = cif_data['_citation_journal_full'][0]

        reference, created= Reference.objects.get_or_create(
                journal=journal,
                year=cif_data['_citation_year'][0],
                title=cif_data['_publ_section_title'])
        self.reference = reference
        
        for author in cif_data['_publ_author_name']:
            auth, created = Author.objects.get_or_create(name=author)
            reference.authors.add(auth)

        icsd = ICSD.parse_cif(self.source_file)
        self.icsd = icsd

        if any([s < 0.98 for s in cif_data['_atom_site_occupancy']]):
            print cif_data['_atom_site_occupancy']
            self.add_hold('partial')
        nom_comp = cif_data['_chemical_formula_sum']
        nom_dict = name_to_comp(nom_comp, special='unit')
        if set(nom_dict.keys()) != set(self.comp.keys()):
            self.add_hold('incomplete_composition')
        else:
            scales = [ self.unit_comp[k]/v for k,v in nom_dict.items() ]
            if any([ abs(1-s) > 0.05 for s in scales ]):
                self.add_hold('composition_mismatch_in_cif')
            elif len(set(scales)) > 1:
                self.add_keyword('slight_composition_mismatch')

    ###
    ### Dynamically calculated properties
    ###

    @property
    def space(self):
        return set([ e.symbol for e in self.elements])

    @property
    def elements(self):
        return list(self.element.all())

    @property
    def tasks(self):
        return list(self.task_set.all())

    @property
    def jobs(self):
        return list(self.job_set.all())

    @property
    def comp(self):
        return name_to_comp(self.formula)

    @property
    def nom_comp(self):
        return name_to_comp(self.formula, special='reduce')

    @property
    def unit_comp(self):
        return name_to_comp(self.formula, special='unit')

    @property
    def latex(self):
        return comp_to_latex(self.comp)

    @property
    def calculations(self):
        return list(self.calculation_set.all())

    @property
    def energy(self):
        if self.calculation_set.filter(settings='standard', done=True).exists():
            return self.calculation_set.get(settings='standard', done=True).energy_pa 
        else:
            return None

    @property
    def mass(self):
        return sum( Element.get(elt)*amt for elt, amt in self.unit_comp)

    @property
    def volume(self):
        if not self.relaxed is None:
            return self.relaxed.volume/self.natoms
        else:
            return self.input.volume/self.natoms

    ### holds
    def add_hold(self, hold):
        holds = self.get_holds()
        if hold not in holds:
            holds.append(hold)
        self.holds = ' '.join(holds)

    def get_holds(self):
        holds = self.holds.strip().split(' ')
        return [ h for h in holds if h ]

    def remove_hold(self, hold):
        holds = self.get_holds()
        holds.remove(hold)
        self.holds = ' '.join(holds)

    ## keywords
    def add_keyword(self, keyword):
        keywords = self.get_keywords()
        if keyword not in keywords:
            keywords.append(keyword)
        self.keywords = ' '.join(keywords)

    def get_keywords(self):
        return self.keywords.strip().split(' ')

    def remove_keyword(self, keyword):
        keywords = self.get_keywords()
        keywords.remove(keyword)
        self.keywords = ' '.join(keywords)

    ## log
    def write_log(self, event):
        self.log += '\n'
        self.log += str(event)

    ## project
    def set_project(self, project):
        proj, created = Project.objects.get_or_create(name=project)
        if created:
            print 'Making new project', project
            print 'NOTE: Has no available resources!'
        self.project = proj

    ## structures
    def add_structure(self, structure, label=None):
        if not hasattr(self, 'new_structures'):
            self.new_structures = []
        if label is not None:
            structure.label = label
        self.new_structures.append(structure)

    def get_structure(self, label):
        ret = None
        if hasattr(self, 'new_structures'):
            for struct in self.new_structures:
                if struct.label == label:
                    ret = struct
        test = self.structure_set.filter(label=label)
        if test.exists():
            return test[0]

    @property
    def structures(self):
        ret_structs = []
        for struct in self.structure_set.all():
            ret_structs.append(struct)
        if hasattr(self, 'new_structures'):
            for struct in self.new_structures:
                ret_structs.append(struct)
        return ret_structs

    @property
    def input(self):
        return self.get_structure('source')

    @property
    def coarse_relaxed(self):
        return self.get_structure('coarse_relaxed')

    @property
    def relaxed(self):
        return self.get_structure('relaxed')

    ## calculations

    def get_calculation(self, settings, **kwargs):
        test = self.calculation_set.filter(settings=settings, **kwargs)
        if test.count() == 1:
            return test[0]
        elif test.count() > 1:
            return test.order_by('energy')[0]
        elif test.count() == 0:
            return None

    def is_done(self, settings):
        calc = self.get_calculation(settings, done=True)
        if calc is None:
            return False
        else:
            return True

    def initialize(self, args=[]):
        if self.is_done('initialize'):
            return self.get_calculation('initialize', done=True)

        self.input.set_magnetism('ferro')
        calc = Calculation.do(self.input, entry=self,
                type='initialize', path=self.path+'/initialize', args=args)
        calc.npar = 2
        calc.write()
        if calc.done:
            if calc.magmom > 0.1:
                self.add_keyword('magnetic')
        calc.save()
        return calc

    def coarse_relax(self, args=[]):
        if self.is_done('coarse_relax'):
            return self.get_calculation('coarse_relax', done=True)

        calc = self.initialize(args=args)
        if not calc.done:
            calc.npar = 2
            calc.write()
            return calc
        if not 'magnetic' in self.keywords:
            self.input.set_magnetism('none')
        calc = Calculation.do(self.input, entry=self,
            type='coarse_relax', path=self.path+'/coarse_relax', args=args)
        if calc.done:
            if calc.output is None:
                calc.output = calc.input
                calc.save()
            calc.output.save()
            self.add_structure(calc.output, label='coarse_relaxed')
        elif not os.path.exists(self.path+'/coarse_relax/CHGCAR.gz'):
            os.system('cp %s/initialize/CHGCAR.gz %s/coarse_relax/' % 
                    (self.path, self.path))
        calc.save()
        self.save()
        return calc

    def fine_relax(self, args=[]):
        if self.is_done('fine_relax'):
            return self.get_calculation('fine_relax', done=True)

        calc = self.coarse_relax(args=args)
        if not calc.done:
            calc.npar = 2
            calc.write()
            return calc
        if 'magnetic' in self.keywords:
            self.coarse_relaxed.set_magnetism('ferro')

        calc = Calculation.do(self.coarse_relaxed, entry=self,
            type='fine_relax', path=self.path+'/fine_relax', args=args)
        if calc.done:
            if calc.output is None:
                calc.output = calc.input
                calc.save()
            self.add_structure(calc.output, label='relaxed')
        elif not os.path.exists(self.path+'/standard/CHGCAR.gz'):
            os.system('cp %s/coarse_relax/CHGCAR.gz %s/fine_relax/'
                    % (self.path, self.path))

        calc.save()
        self.save()
        return calc

    def standard(self, args=[]):
        if self.is_done('standard'):
            return self.get_calculation('standard', done=True)
        calc = self.fine_relax(args=args)
        if not calc.done:
            calc.npar = 2
            calc.write()
            return calc

        if 'magnetic' in self.keywords:
            self.relaxed.set_magnetism('ferro')

        calc = Calculation.do(self.relaxed, entry=self,
            type='standard', path=self.path+'/standard', args=args)
        if calc.done:
            #from thermopy import PhaseSpace
            Formation.get(calc, fit='standard')
            #s = PhaseSpace('-'.join(self.comp.keys()))
            #s.load('oqmd')
            #s.get_meta_stabilities()
            # maybe add to global phase diagram?
        elif not os.path.exists(self.path+'/standard/CHGCAR.gz'):
            os.system('cp %s/fine_relax/CHGCAR.gz %s/standard' % 
                    (self.path, self.path))
        calc.save()
        return calc

    @property
    def oqmd(self):
        calcs = self.calculation_set.filter(settings='standard', done=True)
        if calcs.exists():
            return calcs.order_by('energy')[0]
        else:
            return None

    def do(self, module, args=[]):
        return getattr(self, module)(args=args)

    @property
    def errors(self):
        return dict( ( c.path, c.get_errors()) for c in self.calculations )

    def move(self, path):
        path = os.path.abspath(path)
        try:
            os.system('mv %s %s' % (self.path, path))
        except Exception, err:
            print err
            return
        self.path = path
        print 'Moved %s to %s' % (self, path)
        self.save()

    @property
    def chg(self):
        if not hasattr(self, '_chg'):
            if not self.done:
                self._chg = False
            else:
                self._chg = Grid.load_xdensity(self.path+'/standard/CHGCAR.gz')
        return self._chg

    def reset(self):
        for structure in self.structures:
            if structure.label != 'source':
                structure.delete()
        
        for calc in self.calculations:
            calc.clean_start()
            calc.delete()

        for task in self.tasks:
            task.state = 0 
            task.save()

        for job in self.job_set.filter(state=1):
            job.collect()
            job.delete()
        self.job_set.all().delete()

        for dir in ['initialize', 'coarse_relax', 'fine_relax', 'standard']:
            os.system('rm -rf %s/%s &> /dev/null' % (self.path, dir))

    def visualize(self, structure='source'):
        os.system('/usr/local/bin/VESTA %s/POSCAR' % self.path)
