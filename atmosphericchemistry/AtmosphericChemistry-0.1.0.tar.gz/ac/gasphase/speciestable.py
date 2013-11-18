# -*- coding: utf-8 -*-
"""
SpeciesTable

Python module to access (and verify) information in the master_species_table.csv
file. This file collects species names and properties as used in chemistry
transport models, provides a reference for chemical and physical properties
of these compounds and attempts to uniquely identify them.

The species table is essentially a list of Compound objects.

Instantiation:
- t = speciesTable(compounds, sections, comments)
      arguments are lists with Compound objects and strings, respectively
- t = speciesTable.from_csv([filename][, separator])
      read all species information from a csv file (default "master_species_table.csv")
      and return an object instance.
Attributes:
- comments: a list of comment strings extracted from a csv file (or added manually)
- compounds: a list of Compound objects
- sections: a list of section headings (extracted from respective comments in csv file)
Methods:
- find(value, property_name="", model=None [, exact=True|False][, tol=value])
      return a list of Compound objects that match the given query. If
      property_name is left blank, the query will look at all Compound properties
      to find a match. Use the model kyeword to only return compounds that are
      defined in that model's compound list. Note the use of the exact keyword
      as defined in the Compound object's match_property method.
- find_model_species(name, model)
      return Compound object for a given species from a specific model mechanism
- get_model_names()
      return names of all models for which a 'model:XXX' column exists in the table
- index(value, start=0, property_name="", model=None,  [, exact=True|False][, tol=value])
      return the index of the first occurence of a compound with matching
      properties (see find above). Set start to the returned index+1 if you
      want to look for further occurences.
- write_csv(filename, separator=";")
      save the current species table back to file

Use cases:
  As the speciesTable is primarily a container object for Compound instances, almost
  any application will rely on the interplay of the two classes. Here are a few
  examples for typical tasks:
- preparation: read the master species table
    from speciestable import speciesTable as st
    t=st.from_csv()
- report Henry coefficients of all aldehydes:
    cl=t.find("CHO", "fgroups", exact=False)
    for cc in cl:
        print cc.get_property("structure"),cc.get_property("henry")," ;  ",cc.get_name()
- same for all nitrates in the CAM-CHEM model:
    cl=t.find("ONO2", "fgroups", model="CAM-CHEM", exact=False)
    for cc in cl:
        print cc.get_property("model:CAM-CHEM"),cc.get_property("henry")," ;  ",cc.get_name()
- check consistency of species structure information (except SMILES):
    import speciestable as st
    t=st.speciesTable.from_csv()
    for cc in t._compounds:
	print cc.get_name()
	dummy=cc.cross_check_composition()
"""

# Use example:
# import speciestable as st
# t=st.speciesTable.from_csv()
# myc=t._compounds[178]
# res=myc.get_pub_chem_compound()
# for i in range(20,30):
#	myc=t._compounds[i]
#	print myc.get_property("name", exact=False)
#	myc.cross_check_pub_chem()

import os
from collections import OrderedDict
import datetime as dt
import numpy as np
import ac.utils.moleweight as mw
from compound import Compound
from ac.gasphase import DATADIR

__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-09-24'
__license__ = 'MIT'

masterTableFile = DATADIR+"/master_species_table_v01_20131021.csv"
print "speciestable: default = ", masterTableFile


def read_csv(filename=masterTableFile, separator=";"):
    """read master species table from csv file
Extra comments and section headings will be preserved
A section tag will be introduced to each line"""
    sections = []
    compounds = []
    comments = []
    headings = []
    hassec = False
    with open(filename, "r") as f:
        nlines = 0
        for line in f:
            nlines += 1
            line.replace("\n","")
            ## improve the following by use of a regular expression so that blanks or tabs are ignored
            if "model:" in line:
#                print "#HEADER#:",line
                tokens = line.split(separator)
                tokens[0] = tokens[0][2:]
                headings = [t.strip() for t in tokens]
                # add section number to headings
                if "section" in headings:
                    hassec = True
                else:
                    hassec = False
                    headings.insert(0, "section")
            elif line.startswith("# Section"):
#                print "#SECTION#:",line
                sections.append(line[line.find(":")+1:].replace(separator,"").strip())
            elif line.startswith("#"):
#                print "#COMMENT#:",line
                test = line[1:].strip().replace(separator, "").strip()
                if test:
                    comments.append(test)
            elif not line.replace(separator, "").strip():
                pass   # empty comment line
            else:
                # create new compound entry from text line; add section number
                # Warning: section count starts with 1, 0 means undefined
                if not hassec:
                    line = "%i" % (len(sections)) + separator + line
                compounds.append(Compound.from_string(line, headings, separator, lineno=nlines))
    return sections, compounds, comments


class speciesTable(object):
    """defines the master species table as a list of compounds

    table = speciesTable([compounds])  generates a new table, optionally with a list of compounds
    table = speciesTable.from_csv([filename])  reads the table from a csv file
    table = speciesTable.from_txt([filename])  reads the table from a txt file
    table.write_csv([filename]) writes the table as csv file
    table.write_txt([filename]) writes the table as txt file
    """
    
    def __init__(self, compounds=None, sections=None, comments=None):
        # initialize with a list of Compounds objects if given
        if compounds is None:
            self._compounds = []
        else:
            self._compounds = compounds
        # initialize with a list of section names if given
        if sections is None:
            self._sections = []
        else:
            self._sections = sections
        # initialize with a list of comments if given
        if comments is None:
            self._comments = []
        else:
            self._comments = comments
            

    @classmethod
    def from_csv(cls, filename=masterTableFile, **kwargs):
        sections, compounds, comments = read_csv(filename, **kwargs)
        return cls(compounds, sections, comments)


    @property
    def comments(self):
        return self._comments

    @property
    def compounds(self):
        return self._compounds

    @property
    def sections(self):
        return self._sections


    def find(self, value, property_name="", model=None, **kwargs):
        """finds compounds with given properties.
        Examples:
        table.find("bromine", "name", exact=False)
        table.find("alpha-pinene", "name")
        table.find(159., "moleweight", exact=False, tol=.1)
        table.find("CHO", "fgroups", exact=False)  # returns all aldehydes"""
        res = []
        for el in self._compounds:
            if not el.match_property(value, property_name, **kwargs) is None:
                if model is None:
                    res.append(el)
                elif el.get_property("model:"+model):
                    res.append(el)     # only append if compound is defined for given model
        return res
    

    def find_model_species(self, value, model=None):
        """find the compound information for a particular model species"""
        if model is None:
            # return compound if defined for any model
            # First match will be returned. Be careful!
            for el in self._compounds:
                for m in self.get_model_names():
                    key = "model:"+m
                    if el.get_property(key) == value:
                        return el
        else:
            key = "model:"+model
            for el in self._compounds:
                if el.get_property(key) == value:
                    return el
        return None
    

    def get_model_names(self):
        """return a list of the valid model names, i.e. the 'XXX' in all table
        headings with the string 'model:XXX'."""
        res = []
        if len(self._compounds) > 0:
            mtags = self._compounds[0].get_keys()
            res = [m[6:] for m in mtags if m.startswith("model:")]
        return res

        
    def index(self, value, start=0, property_name="", model=None, **kwargs):
        """returns first index of the compound with given properties."""
        for i, el in enumerate(self._compounds[start:]):
            if not el.match_property(value, property_name, **kwargs) is None:
                if model is None:
                    return start+i
                elif el.get_property("model:"+model):
                    return start+i
        raise ValueError("No compound with property %s found!"%(value))


    def write_csv(self, filename="master_species_table_%s.csv" % (dt.date.today().isoformat()),
                  separator=";"):
        """Save species table in csv format"""
        with open(filename, "w") as f:
            # write comments
            for c in self.comments:
                f.write("# %s\n" %(c))
            f.write("\n")
            # determine column header from first compound
            keys = self._compounds[0]._properties.keys()
            header = separator.join(keys)
            # loop through compounds: add empty line and section header for each section change
            section = self._compounds[0].get_property("section") - 1
            for c in self._compounds:
                if c.get_property("section") > section:
                    f.write("\n")
                    f.write("# Section %i: %s\n" %(section+1, self.sections[section]))
                    f.write("# %s\n" % (header))
                    section += 1
                f.write(c.__str__(separator)+"\n")
                

