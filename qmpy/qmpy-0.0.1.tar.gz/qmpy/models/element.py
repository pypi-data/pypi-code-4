from django.db import models

class Element(models.Model):
    ### Identification
    z = models.IntegerField(db_index=True)
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=9, primary_key=True)

    ### Periodic table
    grp = models.IntegerField()
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
    abundance = models.FloatField()
    production = models.FloatField(default=0)
    radioactive = models.BooleanField(default=False)

    ### calculated properties
    base_mu = models.FloatField(null=True)

    class Meta:
        db_table = 'elements'

    def __str__(self):
        return self.symbol

    @property
    def get_elementstring(self):
        save_str = ''
        for k, v in self.fields.items():
            save_str += '{key} = {val}\n'.format(key=k, val=str(v))
        return save_str

    @staticmethod
    def write_elementfiles(dirname):
        import os
        os.chdir(dirname)

        elements = Element.objects.all()
        for elt in elements:
            f = open(elt.symbol,'w')
            f.write(elt.get_elementstring)
            f.close()

    @staticmethod
    def read_elementfiles(dirname):
        import os
        for elt in os.listdir(dirname):
            var_dict = {}
            for line in open(dirname+'/'+elt, 'r'):
                k, v = line.split(' = ')
                var_dict[k] = v.rstrip('\n')
            elt, created = Element.objects.get_or_create(**var_dict)
            if created:
                elt.save()

    @staticmethod
    def get(symbol):
        return Element.objects.select_related().get(symbol=symbol)

    @property
    def mu(self):
        all = self.entry_set.filter(ntypes=1,
                calculation__settings='standard',
                calculation__done=True)
        gs = sorted(all, key=lambda x: x.energy)
        if not gs:
            return None 
        return gs[0].energy
        
class ElementSet(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    elements = models.ManyToManyField(Element)
    class Meta:
        db_table = 'element_classes'

    @staticmethod
    def read(pgfile):
        e_string = open(pgfile).read()
        e_string = e_string.strip()
        egroup = {}
        elts = []
        for line in e_string.split('\n'):
            line = line.lstrip('-')
            if ' = ' in line:
                k, v = line.split(' = ')
                egroup[k] = v
            else:
                elts.append(line)
        eg, created = ElementSet.objects.get_or_create(**egroup)
        if not created:
            return eg
        eg.save()
        for elt in elts:
            eltobj = Element.objects.get(symbol=elt)
            eg.elements.add(eltobj)
        return eg

    #@property
    #def elements(self):
    #    return list(self.element_set.all())

class Potential(models.Model):
    potid = models.AutoField(primary_key=True)
    potcar = models.TextField()
    element = models.ForeignKey(Element)

    name = models.CharField(max_length=10)
    xc = models.CharField(max_length=3)
    gw = models.BooleanField(default=False)
    paw = models.BooleanField(default=False)
    us = models.BooleanField(default=False)
    enmax = models.FloatField()
    enmin = models.FloatField()
    date = models.CharField(max_length=20)
    electrons = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'potentials'

    def __str__(self):
        ident = '%s %s' % (self.name, self.xc)
        if self.paw:
            ident += ' PAW'
        if self.us:
            ident += ' US'
        if self.gw:
            ident += ' GW'
        return ident

    @staticmethod
    def read_potcar(potfile):
        pots = open(potfile).read()
        pots = pots.strip().split('End of Dataset')
        potobjs = []
        for pot in pots:
            if not pot:
                continue
            potcar = {}
            for line in pot.split('\n'):
                if 'TITEL' in line:
                    potcar['name'] = line.split()[3]
                    elt = potcar['name'].split('_')[0]
                    date = potcar['name'].split('_')[-1]
                    potcar['element'] = Element.objects.get(symbol=elt)
                    if 'GW' in line:
                        potcar['gw'] = True
                    if 'PAW' in line:
                        potcar['paw'] = True
                    if 'US' in line:
                        potcar['us'] = True
                if 'ENMAX' in line:
                    data = line.split()
                    potcar['enmax'] = float(data[2].rstrip(';'))
                    potcar['enmin'] = float(data[5])
                if 'VRHFIN' in line:
                    potcar['electrons'] = line.split(':')[1]
                if 'LEXCH' in line:
                    key = line.split()[-1]
                    if key == '91':
                        potcar['xc'] = 'GGA'
                    elif key == 'CA':
                        potcar['xc'] = 'LDA'
                    elif key == 'PE':
                        potcar['xc'] = 'PBE'
            potobj, created = Potential.objects.get_or_create(**potcar)
            if created:
                potobj.potcar = pot
            potobjs.append(potobj)
        return potobjs

class Hubbard(models.Model):
    element = models.ForeignKey(Element, related_name='hubbards')
    with_elt = models.ForeignKey(Element, related_name='induced_hubbards',
            null=True, blank=True, default=None)
    ldau_u = models.FloatField(default=0)
    ldau_l = models.IntegerField(default=-1)
    class Meta:
        db_table = 'hubbards'

    def __str__(self):
        if self.with_elt is not None:
            return '%s (with %s) U=%s L=%s' % (self.element.symbol,
                    self.with_elt.symbol, self.ldau_u, self.ldau_l)
        else:
            return '%s U=%s L=%s' % (self.element.symbol, 
                    self.ldau_u, self.ldau_l)


    def __nonzero__(self):
        if self.ldau_u > 0 and self.ldau_l != -1:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.element != other.element:
            return False
        if self.ldau_u != other.ldau_u:
            return False
        if self.ldau_l != other.ldau_l:
            return False
        return True

    @property
    def get_hubbardstring(self):
        return str(self)

def read_potentials():
    import os
    potdir = '/home/sjk648/bin/qmpy/config/potentials'
    dirs = os.listdir(potdir) 
    for d in dirs:
        for pot in os.listdir(potdir+'/'+d):
            if not os.path.exists(potdir+'/'+d+'/'+pot+'/POTCAR'):
                print 'No', d+'/'+pot+'/POTCAR'
                continue
            potobj = Potential.read_potcar(potdir+'/'+d+'/'+pot+'/POTCAR')[0]
            potobj.save()

def read_elements():
    Element.read_elementfiles('/home/sjk648/bin/qmpy/config/elements')


class PotentialSet(models.Model):
    name = models.CharField(max_length=30)
    xc = models.CharField(max_length=3, default='PBE')
    gw = models.BooleanField(default=False)
    paw = models.BooleanField(default=True)
    us = models.BooleanField(default=False)
    potentials = models.ManyToManyField(Potential)

    class Meta:
        db_table = 'potential_sets'

    def get(self, element):
        return self.potentials.get(element__symbol=element)

    def get_pg_str(self):
        outstr = 'name = %s\n' % self.name
        outstr += '-xc = %s\n' % self.xc 
        outstr += '-paw = %s\n' % self.paw
        outstr += '-us = %s\n' % self.us
        for pot in self.potentials.all():
            outstr += '--%s\n' % pot.name

    @property
    def filter(self):
        return {'us':self.us, 
                'gw':self.gw,
                'xc':self.xc,
                'paw':self.paw}

    @staticmethod
    def read(pgfile):
        pg_string = open(pgfile).read()
        pg_string = pg_string.rstrip('\n')
        potgroup = {}
        pots = []
        for line in pg_string.split('\n'):
            line = line.lstrip('-')
            if ' = ' in line:
                k, v = line.split(' = ')
                potgroup[k] = v
            else:
                pots.append(line)
        pg, created = PotentialSet.objects.get_or_create(**potgroup)
        if not created:
            return pg
        pg.save()
        for pot in pots:
            potobj = Potential.objects.filter(**pg.filter).get(name=pot)
            pg.potentials.add(potobj)
        return pg

    def __str__(self):
        return "%s : %s" % (self.name, self.xc)


class HubbardSet(models.Model):
    name = models.CharField(max_length=30)
    hubbards = models.ManyToManyField(Hubbard)
    class Meta:
        db_table = 'hubbard_sets'

    def get(self, element):
        hub, created = self.hubbards.get_or_create(element__symbol=element)
        if created:
            hub.save()
        return hub

    def get_pg_str(self):
        for hub in self.hubbards.all():
            outstr += hubbard.get_hubbardstring()

    @staticmethod
    def read(path):
        h_string = open(path).read()
        h_string = h_string.strip()
        for line in h_string.split('\n'):
            if ' = ' in line:
                line = line.split(' = ')
                hub_group, created = HubbardSet.objects.get_or_create(name=line[1])
                if not created:
                    return hub_group
                continue
            line = line.split()
            hubbard, created = Hubbard.objects.get_or_create(element_id=line[0], 
                    with_elt_id=line[1],
                    ldau_u=float(line[2]), ldau_l=float(line[3]))
            hub_group.hubbards.add(hubbard)
        return hub_group

    def get_hubbardgroup_string(self):
        hstring = ''
        for h in self.hubbards.all():
            hstring += h.get_hubbardstring()+'\n'
        return hstring

    def __str__(self):
        return self.name

def read_hubbard_groups():
    import os
    path='/home/sjk648/bin/qmpy/config/collections/hubbards'
    groups = os.listdir(path)
    HubbardSet.objects.all().delete()
    for group in groups:
        hg = HubbardSet.read(path+'/'+group)
        hg.save()

def read_element_groups():
    import os
    path='/home/sjk648/bin/qmpy/config/collections/elements'
    groups = os.listdir(path)
    ElementSet.objects.all().delete()
    for group in groups:
        eg = ElementSet.read(path+'/'+group)
        eg.save()

def read_potential_groups():
    import os
    path='/home/sjk648/bin/qmpy/config/collections/potentials'
    groups = os.listdir(path)
    PotentialSet.objects.all().delete()
    for group in groups:
        pg = PotentialSet.read(path+'/'+group)
        pg.save()
