from django.db import models
from composition import Composition

from utils import *

class Author(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        db_table = 'authors'

    def __str__(self):
        return self.name

class Journal(models.Model):
    code = models.CharField(max_length=10, unique=True)
    full_name = models.TextField(null=True)
    class Meta:
        db_table = 'journals'

    def __str__(self):
        return self.code

class Reference(models.Model):
    authors = models.ManyToManyField(Author, related_name='references',
            null=True)
    journal = models.ForeignKey(Journal, related_name='references', 
            null=True)
    title = models.TextField(null=True)
    volume = models.IntegerField(null=True)
    page_first = models.IntegerField(null=True)
    page_last = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)
    class Meta:
        db_table = 'publications'

    def __str__(self):
        s = self.title
        if self.authors is not None:
            s += ': %s' % self.authors.all()[0]
        if self.journal is not None:
            s += ': %s' % self.journal
        return s

    @property
    def citation(self):
        auths = ', '.join(str(a) for a in self.authors.all())
        return '{auths} ({year}). {title}. {jrnl}, {vol}, {pb}-{pe}'.format(
                auths=auths,
                year=self.year,
                title=self.title,
                jrnl=self.journal,
                vol=self.volume,
                pb=self.page_first,
                pe=self.page_last)

class Experiment(models.Model):
    energy = models.FloatField(null=True)
    delta_e = models.FloatField(null=True)
    delta_g = models.FloatField(null=True)

    temperature = models.FloatField(null=True)
    pressure = models.FloatField(null=True)
    state = models.CharField(max_length=2)

    composition = models.ForeignKey('Composition', null=True)
    name = models.CharField(max_length=255, null=True)
    dft = models.BooleanField(default=False)

    comment = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=10, blank=True, null=True)
    #reference = models.ForeignKey(Reference, null=True, blank=True)

    class Meta:
        db_table = 'experiments'

    def __str__(self):
        return '%s : %s' % (self.composition, self.delta_e)

    @property
    def comp(self):
        return self.composition.comp

    @property
    def unit_comp(self):
        return self.composition.unit_comp

    @staticmethod
    def create(name, delta_e, d_g, source):
        comp = Composition.get(name)
        expt = Experiment(name=name,
                delta_e=delta_e, d_g=d_g,
                composition=comp,
                source=source)
        return expt

class ICSD(models.Model):
    coll_code = models.IntegerField(primary_key=True)
    composition = models.ForeignKey('Composition', null=True,
            related_name='icsd_obj')

    chemical_name = models.TextField()
    chemical_formula_structural = models.TextField()
    chemical_formula_sum = models.TextField()

    temperature = models.FloatField(default=293)
    pressure = models.FloatField(default=101.325)

    spacegroup_HM = models.CharField(max_length=20)
    spacegroup = models.IntegerField(default=1)
    r_factor = models.FloatField()

    cif = models.TextField()
    reference = models.ForeignKey(Reference, null=True)

    class Meta:
        db_table = 'icsd'

    def __str__(self):
        return str(self.coll_code)

    @staticmethod
    def parse_cif(cif):
        from ase.io.cif import parse_cif
        cifdict = parse_cif(cif)[0][1]

        icsd = ICSD()

        icsd.coll_code =\
                cifdict['_database_code_icsd']
        icsd.chemical_formula_structural =\
                cifdict.get('_chemical_formula_structural', '')
        icsd.chemical_name =\
                cifdict.get('_chemical_name_systematic', '')
        icsd.chemical_formula_sum = \
                cifdict.get('_chemical_formula_sum', '')

        icsd.temperature =\
                cifdict.get('_cell_measurement_temperature', 293)
        icsd.pressure =\
                cifdict.get('_cell_measurement_pressure', 101.325)
        icsd.r_factor =\
                cifdict.get('_refine_ls_r_factor_all',0)
        icsd.spacegroup =\
                cifdict.get('_symmetry_int_tables_number', 1)
        icsd.spacegroup_hm =\
                cifdict.get('_symmetry_space_group_name_h-m', 'P1')
        icsd.save()

        for wyck in zip(
                cifdict['_atom_site_type_symbol'],
                cifdict['_atom_site_wyckoff_symbol'],
                cifdict['_atom_site_symmetry_multiplicity'],
                cifdict['_atom_site_fract_x'],
                cifdict['_atom_site_fract_y'],
                cifdict['_atom_site_fract_z'],
                cifdict['_atom_site_occupancy'],
                cifdict['_atom_site_attached_hydrogens']):
            wyck = list(wyck)
            elt = ''
            charge = ''
            negative = False
            for char in wyck[0]:
                if char.isalpha():
                    elt += char
                elif char == '+':
                    continue
                elif char == '-':
                    negative=True
                else:
                    charge += char
            if negative:
                charge = -1*int(charge)
            else:
                charge =int(charge)

            if isinstance(wyck[6], basestring):
                    wyck[6] = float(wyck[6].split('(')[0])

            wyckobj = WyckoffSite(
                    icsd=icsd,
                    element=elt,
                    charge=charge,
                    symbol=wyck[1],
                    multiplicity=wyck[2],
                    x = wyck[3],
                    y = wyck[4],
                    z = wyck[5],
                    occupancy = wyck[6],
                    attached_hydrogens = wyck[7])
            wyckobj.save()
        return icsd

class WyckoffSite(models.Model):
    icsd = models.ForeignKey(ICSD)
    symbol = models.CharField(max_length=1)

    element = models.CharField(max_length=2)
    charge = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    multiplicity = models.IntegerField(default=1)
    occupancy = models.FloatField(default=1)
    attached_hydrogens = models.IntegerField(default=0)

    class Meta:
        db_table = 'wyckoff_sites'

    def __str__(self):
        return '%s on %s' % (self.element, self.symbol)

