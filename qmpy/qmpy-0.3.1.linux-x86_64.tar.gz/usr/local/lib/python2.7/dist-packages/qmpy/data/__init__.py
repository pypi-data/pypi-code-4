import yaml
import os.path

location = os.path.dirname(__file__)

data = open(location+'/elements/groups.yml').read()
element_groups = yaml.load(data)

data = open(location+'/elements/data.yml').read()
elements = yaml.load(data)

data = open(location+'/elements/chemical_potentials.yml').read()
chem_pots = yaml.load(data)
