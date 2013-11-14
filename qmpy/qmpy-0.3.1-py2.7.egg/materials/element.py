from django.db import models

from qmpy.utils import *

class Element(models.Model):
    '''
    Database Attributes:
        =-- Identification --=
        z                   : atomic number (int)
        name                : full atomic name (str)
        symbol              : atomic symbol (str)
        
        =-- Periodic table location --=
        group               : group in the periodic table (int)
        period              : period in the periodic table (int)

        =-- Physical characteristics --=
        mass                : Atomic mass, in AMU (float)
        density             : Density at STP, in g/cm^3 (float)
        volume              : Atomic volume at STP, in A^3/atom (float)
        atomic_radii        : in A (float)
        van_der_waals radii : in A (float)
        covalent_radii      : in A (float)

        =-- Thermodynamic characteristics --=
        melt                : melting point in K (float)
        boil                : boiling point in K (float)
        specific_heat       : C_p (float)

        =-- Electronic structure --=
        electronegativity   : Pauling electronegativity (float)
        ion_energy          : Energy to ionize the first electron (float)
        s_elec              : # of s electrons (int)
        p_elec              : # of p electrons (int)
        d_elec              : # of d electrons (int)
        f_elec              : # of f electrons (int)

        =-- Additional information --=
        production          : Annual tons of element produced (float)
        radioactive         : (bool)

    Methods:
        (classmethod)
        get(identity)
            Returns Element corresponding to identity. Identity can be
            elemental name, symbol or atomic number. Can also be a species
            name, i.e. Fe3+, O2-, which which case it only returns the element.

        species_distribution()
            Retuns dict of {oxidation_state: # of occurences}
    '''
    ### Identification
    z = models.IntegerField(db_index=True)
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=9, primary_key=True)

    ### Periodic table
    group = models.IntegerField()
    period = models.IntegerField()

    ### Phyical characteristics
    mass = models.FloatField()
    density = models.FloatField()
    volume = models.FloatField()
    atomic_radii = models.IntegerField()
    van_der_waals_radii = models.IntegerField()
    covalent_radii = models.IntegerField()

    ### Thermodynamics
    melt = models.FloatField()
    boil = models.FloatField()
    specific_heat = models.FloatField()

    ### Electonic structure
    electronegativity = models.FloatField()
    first_ionization_energy = models.FloatField()
    s_elec = models.IntegerField()
    p_elec = models.IntegerField()
    d_elec = models.IntegerField()
    f_elec = models.IntegerField()

    ### misc
    production = models.FloatField(default=0)
    radioactive = models.BooleanField(default=False)

    class Meta:
        app_label = 'qmpy'
        db_table = 'elements'

    # builtins
    def __str__(self):
        return self.symbol

    # accessor
    @classmethod
    def get(cls, value):
        '''
        Return an element object. Accepts symbols and atomic numbers, or a list
        of symbols/atomic numbers.
        
        Example:
        >>> Element.get('Fe')
        >>> Element.get(26)
        >>> Element.get(['Fe', 'O', 2])
        '''
        if isinstance(value, cls):
            return value
        elif isinstance(value, list):
            return [ cls.get(v) for v in value ]
        elif isinstance(value, int):
            return cls.objects.get(z=value)
        elif isinstance(value, basestring):
            return cls.objects.get(symbol=value)

    # methods
    def species_distribution(self):
        counts = {}
        for s in self.species_set.all():
            counts[s.ox] = s.structure_set.count()
        return counts

class Species(models.Model):
    '''
    Database Attributes:
        name        : Species name, e.g. Fe3+, O2- (str)
        element     : Element object, <Element: Fe>, <Element: O>
        ox          : Oxidation state - accepts non-integer values. (float)

    Convenience Attributes:

    Methods:
        (classmethod)
        get(identity) -> Species
            return Species object from a descriptive value. Accepts many forms
            of identity. Examples inlcude: Fe3+, Fe3, {'element':'Fe', 'ox':3}.
            Also accepts a list of such descriptors, returns list of Species.
    '''
    name = models.CharField(max_length=8, primary_key=True)
    element = models.ForeignKey(Element, blank=True, null=True)
    ox = models.FloatField(blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'species'

    # builtins
    def __str__(self):
        return str(self.name)

    # accessor
    @classmethod
    def get(cls, value):
        '''
        Return a Species object. 

        Example:
        >>> Species.get('Fe3+')
        >>> Species.get('Fe3')
        >>> Species.get({'element':'Fe', 'state':3})
        >>> Species.get(('Fe', 3))
        >>> Species.get([ 'Fe3+', 'O2-', 'Li1+'])
        '''
        if isinstance(value, cls):
            return value
        elif isinstance(value, basestring):
            spec, new = cls.objects.get_or_create(name=value)
            if new:
                elt, ox = parse_species(value)
                spec.element_id = elt
                spec.ox = ox
                spec.save()
            return spec
        elif isinstance(value, list):
            return [ cls.get(value) for value in list ]

    @property
    def ox_format(self):
        if self.ox is None:
            return 0
        elif is_integer(self.ox):
            return int(self.ox)
        else:
            return float(round(self.ox, 3))
        
