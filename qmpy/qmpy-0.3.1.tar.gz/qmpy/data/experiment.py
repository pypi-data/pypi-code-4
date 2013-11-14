#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import json

from qmpy.materials.composition import Composition

from utils import *

class ExperimentalFormationEnergy(models.Model):
    composition = models.ForeignKey('Composition', null=True, blank=True)
    delta_e = models.FloatField(null=True)
    delta_g = models.FloatField(null=True)
    source = models.CharField(max_length=127, blank=True, null=True)
    dft = models.BooleanField(default=False)

    class Meta:
        app_label = 'qmpy'
        db_table = 'experimental_formation_energies'

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    @classmethod
    def read_file(cls, filename, dft=False):
        source = filename.split('.')[0]
        expts = []
        for line in open(filename, 'r'):
            comp, energy = line.strip().split()
            print comp
            expt, new = ExperimentalFormationEnergy.objects.get_or_create(delta_e=energy,
                    composition=Composition.get(comp),
                    source=source, 
                    dft=dft)
            if new:
                expt.save()
            expts.append(expt)
        return expts

class Author(models.Model):
    last = models.CharField(max_length=30, blank=True, null=True)
    first = models.CharField(max_length=30, blank=True, null=True)
    class Meta:
        app_label = 'qmpy'
        db_table = 'authors'

    @property
    def proper_last(self):
        if not self.last:
            return None
        elif len(self.last) == 1:
            return self.last.upper()
        else:
            return self.last[0].upper()+self.last[1:]

    @property
    def proper_first(self):
        if not self.first:
            return None
        elif len(self.first.split()) == 1:
            if len(self.first) == 1:
                return self.first[0].upper()+'.'
            else:
                return self.first[0].upper()+self.first[1:]
        else:
            return ' '.join(l[0].upper()+"." for l in self.first.split())

    def __str__(self):
        if self.first and self.last:
            return '%s, %s' % (self.proper_last, self.proper_first)
        elif self.first and not self.last:
            return self.proper_first
        elif self.last and not self.first:
            return self.proper_last

    @classmethod
    def from_name(cls, name):
        commas = name.count(',')
        spaces = name.count(' ')
        if commas == 1:
            last, first = name.split(',')
        elif commas == 0 and spaces:
            first = name.split()[0]
            last = ' '.join(name.split()[1:])
        else:
            last = name.split(',')[0]
            first = ' '.join(name.split(',')[1:])
        author, new = Author.objects.get_or_create(
                last=last.lower().strip(), first=first.lower().strip())
        return author


class Journal(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.TextField(null=True)
    class Meta:
        app_label = 'qmpy'
        db_table = 'journals'

    def __str__(self):
        if self.name:
            return self.name
        elif self.code:
            return self.code

class Reference(models.Model):
    author_set = models.ManyToManyField(Author, related_name='references',
            null=True)
    journal = models.ForeignKey(Journal, related_name='references', 
            null=True)
    title = models.TextField(null=True)
    volume = models.IntegerField(null=True)
    page_first = models.IntegerField(null=True)
    page_last = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)

    _authors = []
    class Meta:
        app_label = 'qmpy'
        db_table = 'publications'

    def save(self,*args, **kwargs):
        if self.journal:
            self.journal.save()
        super(Reference, self).save(*args, **kwargs)
        self.author_set = self._authors

    @property
    def authors(self):
        if not self._authors:
            self._authors = list(self.author_set.all())
        return self._authors

    @authors.setter
    def authors(self, authors):
        self._authors = authors

    def __str__(self):
        s = self.title
        if self.authors:
            s += ': %s' % self.authors[0]
        if self.journal is not None:
            s += ': %s' % self.journal
        return s

    @property
    def citation(self):
        retval = ', '.join(str(a) for a in self.authors)
        if self.year:
            retval += '('+str(self.year)+')'
        if self.title:
            retval += '. '+self.title.strip().rstrip('.')
        if self.journal:
            retval += '. '+str(self.journal)
            if self.volume:
                retval += ', '+str(self.volume)
                if self.page_first:
                    retval += ', '+str(self.page_first)
                    if self.page_last:
                        retval += '-'+str(self.page_last)
        return retval+'.'

