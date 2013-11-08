#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import os

from django.db import models

from qmpy.db.custom import *
from qmpy.materials.composition import *
from qmpy.materials.element import Element, Species
from qmpy.materials.structure import Structure
from qmpy.utils import *
from qmpy.computing.resources import Project
from qmpy.data.meta_data import *
import qmpy.io as io
import qmpy.computing.scripts as scripts

k_desc = 'Descriptive keyword for looking up entries'
h_desc = 'A note indicating a reason the entry should not be calculated'

@add_meta_data('keyword', description=k_desc)
@add_meta_data('hold', description=h_desc)
class Entry(models.Model):
    '''
    The core model for typical database entries. An Entry model represents an
    input structure to the database, and can be created from any input file.
    
    Database fields:
        path                : Path to the Entry. (string)
        meta_data           : QuerySet of MetaData models. MetaData are tags
                              consisting of a type and a value. e.g.
                              MetaData(type="hold", value="partially occupied")
        label               : Brief description of the entry, e.g. ICSD-1415
                              (string)
        duplicate_of        : If this entry appears to be an exact duplicate of
                              another existing entry, the existing entry is
                              linked here.
        duplicates          : If another entry duplicates this one, you can
                              find those duplicate entries throug this
                              QuerySet.
        reference           : Journal reference for the input structure 
                              (Reference)
        prototype           : If this structure has been assigned to be an
                              instance of a prototype, it is specified here
        composition         : Composition object matching the composition of
                              input structure


        stable              : Is the structure on the convex hull?
        delta_e             : Formation energy per atom of structure (None if
                              not calculated) (float)

        element_set         : QuerySet of associated Elements
        species_set         : QuerySet of assicated Speices
        project_set         : QuerySet of associated Projects
        structure_set       : QuerySet of associated structures. Easier to
                              access this information through the structures
                              attribute.
        calculation_set     : QuerySet of associated calculations. Easier to
                              access this information through the calculations
                              attribute.
        job_set
        task_set

    '''
    ### structure properties
    path = models.CharField(max_length=255, db_index=True, unique=True)
    meta_data = models.ManyToManyField('MetaData')
    label = models.CharField(max_length=20, null=True)

    ### record keeping
    duplicate_of = models.ForeignKey('Entry', related_name='duplicates',
            null=True)

    ### 
    stable = models.BooleanField(default=False)
    delta_e = models.FloatField(blank=True, null=True)

    ## links
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    project_set = models.ManyToManyField('Project')
    composition = models.ForeignKey('Composition', blank=True, null=True)
    spacegroup = models.ForeignKey('Spacegroup', blank=True, null=True)
    reference = models.ForeignKey('Reference', null=True, blank=True)
    prototype = models.ForeignKey('Prototype', null=True, blank=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'entries'

    def __str__(self):
        return '%s : %s' % (self.id, self.name)

    def save(self, *args, **kwargs):
        '''Saves the Entry, as well as all associated objects.'''
        if not self.reference is None:
            if self.reference.id is None:
                self.reference.save()
                self.reference = self.reference
        self.delta_e = self.energy
        super(Entry, self).save(*args, **kwargs)
        for k, v in self.structures.items():
            if v.label != k:
                v.label = k
                v.entry = self
                v.save()
        for k, v in self.calculations.items():
            if v.label != k:
                v.label = k
                v.entry = self
                v.save()
        self.element_set = self.elements
        self.species_set = self.species
        self.project_set = self.projects
        self.meta_data = self.hold_objects + self.keyword_objects

    @classmethod
    def create(cls, source, keywords=[], projects=[], **kwargs):
        '''
        Create an Entry object from a provided input file.

        Optional arguments:
            keywords - list of keywords to associate with the entry
            projects - list of projects to associate with the entry

        '''
        source_file = os.path.abspath(source)
        path = os.path.dirname(source_file)
        if Entry.objects.filter(path=path).exists():
            return Entry.objects.get(path=path)
        entry = cls(**kwargs)
        
        entry.source_file = source_file
        entry.path = os.path.dirname(source_file)
        structure = io.read(source_file)
        structure.make_primitive()

        entry.structures['input'] = structure
        if any([ a.occupancy < 0.95 for a in structure ]):
            entry.holds.append('partial occupancy')
        if not structure.composition == structure.reported_composition:
            entry.holds.append('composition mismatch in CIF')
            entry.composition = entry.input.reported_composition
        else:
            entry.composition = entry.input.composition

        entry.ntypes = structure.ntypes
        entry.natoms = len(structure.atoms)
        entry.elements = entry.comp.keys() 
        entry.reference = structure.reference
        entry.prototype = structure.prototype
        entry.keywords = keywords
        entry.projects = projects
        return entry

    _elements = None
    @property
    def elements(self):
        '''List of Elements'''
        if self._elements is None:
            self._elements = [ Element.get(e) for e in self.comp.keys() ]
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = [ Element.get(e) for e in elements ]

    _species = None
    @property
    def species(self):
        '''List of Species'''
        if self._species is None:
            self._species = [ Species.get(s) for s in self.spec_comp.keys() ]
        return self._species

    @species.setter
    def species(self, species):
        self._species = [ Species.get(e) for e in species ]

    _projects = None
    @property
    def projects(self):
        '''List of Projects'''
        if self._projects is None:
            self._projects = list(self.project_set.all())
        return self._projects

    @projects.setter
    def projects(self, projects):
        self._projects = [ Project.get(p) for p in projects ]

    _structures = None
    @property
    def structures(self):
        if self._structures is None:
            if self.id is None:
                self._structures = {}
            else:
                structs = self.structure_set.exclude(label='')
                labels = [ s.label for s in structs ]
                if len(set(labels)) < len(labels):
                    print 'Warning! Some related objects have repeat names!'
                    print 'To address this, all labels have been appended',
                    print 'with the primary key of the related object.'
                    labels = [ '%s_%s' % (s.label, s.pk) for s in structs ]
                self._structures = dict((k, s) for k,s in zip(labels, structs))
        return self._structures

    @structures.setter
    def structures(self, structs):
        if not isinstance(structs, dict):
            raise TypeError('structures must be a dict')
        if not all( isinstance(v, Structure) for v in structs.values()):
            raise TypeError('structures must be a dict of Calculations')
        self._structures = structs

    _calculations = None
    @property
    def calculations(self):
        '''Dictionary of label:Calculation pairs.''' 
        if self._calculations is None:
            if self.id is None:
                self._calculations = {}
            else:
                calcs = self.calculation_set.exclude(label='')
                labels = [ c.label for c in calcs ]
                if len(set(labels)) < len(labels):
                    print 'Warning! Some related objects have repeat names!'
                    print 'To address this, all labels have been appended',
                    print 'with the primary key of the related object.'
                    labels = [ '%s_%s' % (c.label, c.pk) for c in calcs ]
                self._calculations = dict((k, c) for k,c in zip(labels, calcs))
        return self._calculations

    @calculations.setter
    def calculations(self, calcs):
        if not isinstance(calcs, dict):
            raise TypeError('calculations must be a dict')
        if not all( isinstance(v, Calculation) for v in calcs.values()):
            raise TypeError('calculations must be a dict of Calculations')
        self._calculations = calcs

    @property
    def input(self):
        return self.structures.get('input')

    @input.setter
    def input(self, structure):
        self.structures['input'] = structure

    @property
    def tasks(self):
        return list(self.task_set.all())

    @property
    def jobs(self):
        return list(self.job_set.all())

    @property
    def comp(self):
        if not self.composition_id is None:
            return parse_comp(self.composition_id)
        elif not self.input is None:
            return self.input.comp
        else:
            return {}

    @property
    def spec_comp(self):
        '''
        Composition dictionary, using species (element + oxidation state)
        instead of just the elements.
        
        '''
        if self.input is None:
            return {}
        else:
            return self.input.spec_comp

    @property
    def unit_comp(self):
        '''Composition dictionary, normalized to 1 atom.'''
        return normalize_comp(self.comp)

    @property
    def red_comp(self):
        '''Composition dictionary, in reduced form.'''
        return reduce_comp(self.comp)

    @property
    def name(self):
        '''Unformatted name'''
        return format_comp(reduce_comp(self.comp))

    @property
    def latex(self):
        '''LaTeX formatted name'''
        return latex_comp(reduce_comp(self.comp))

    @property
    def html(self):
        '''HTML formatted name'''
        return html_comp(reduce_comp(self.comp))

    @property
    def space(self):
        '''Return the set of elements in the input structure.
        
        Example:
        >>> e = Entry.create("fe2o3/POSCAR") # an input containing Fe2O3
        >>> e.space
        set(["Fe", "O"])
        
        '''
        return set([ e.symbol for e in self.elements])

    @property
    def total_energy(self):
        '''
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.

        '''
        if 'static' in self.calculations:
            if self.calculations['static'].converged:
                return self.calculations['static'].energy_pa
        if 'standard' in self.calculations:
            if self.calculations['standard'].converged:
                return self.calculations['standard'].energy_pa
        return None

    @property
    def energy(self):
        '''
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.

        '''
        if 'static' in self.calculations:
            if self.calculations['static'].converged:
                return self.calculations['static'].delta_e
        if 'standard' in self.calculations:
            if self.calculations['standard'].converged:
                return self.calculations['standard'].delta_e
        return None

    #@property
    #def spacegroup(self):
    #    for key in ['relaxed', 'fine_relaxed', 'input']:
    #        if key in self.structures:
    #            return self.structures[key].spacegroup

    @property
    def mass(self):
        '''Return the mass of the entry, normalized to per atom.'''
        return sum( Element.objects.get(symbol=elt).mass*amt for 
                elt, amt in self.unit_comp)

    @property
    def volume(self):
        '''
        If the entry has gone through relaxation, returns the relaxed
        volume. Otherwise, returns the input volume.
        
        '''
        if not self.relaxed is None:
            return self.relaxed.volume/self.natoms
        else:
            return self.input.volume/self.natoms

    @property
    def errors(self):
        '''List of errors encountered in all calculations.'''
        return dict( ( c.path, c.get_errors()) for c in self.calculations )

    @property
    def chg(self):
        '''
        Attempts to load the charge density of the final calculation, if it is
        done. If not, returns False.

        '''
        if not hasattr(self, '_chg'):
            if not self.done:
                self._chg = False
            else:
                self._chg = Grid.load_xdensity(self.path+'/standard/CHGCAR.gz')
        return self._chg

    def do(self, module, *args, **kwargs):
        '''
        Looks for a computing script matching the first argument, and attempts
        to run it with itself as the first argument. Sends *args and **kwargs
        to the script. Should return a Calculation object, or list of
        Calculation objects. 

        Example:
        >>> e = Entry.objects.get(id=123)
        >>> e.do('relaxation')
        <Calculation: 523 @ relaxation settings>

        '''
        script = getattr(scripts, module)
        return script(self, *args, **kwargs)

    def move(self, path):
        '''
        Moves all calculation files to the specified path.

        '''
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
    def running(self):
        return self.job_set.filter(state=1)

    def reset(self):
        '''
        Deletes all calculations, removes all associated structures - returns
        the entry to a pristine state.

        '''
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
        '''Attempts to open the input structure for visualization using VESTA'''
        os.system('VESTA %s/POSCAR' % self.path)

