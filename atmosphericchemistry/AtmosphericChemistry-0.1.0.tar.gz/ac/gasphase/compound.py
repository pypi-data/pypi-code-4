# -*- coding: utf-8 -*-
"""
Compound

Python class to access and verify information about gas-phase chemical compounds.

Instantiation:
- c = Compound(propertydict)
      propertydict: an (ordered) dictionary with compound properties (see below)
- c = Compound.from_string(csv_line, template [,separator][, lineno])
      csv_line: a string (line from a csv file) containing property values
      template: a list with the column headings
      separator: character to be used to split the csv_line (default ";")
      lineno: line number in the input file (defaults to -1)
Attributes:
- properties: an ordered dictionary with property names and values
      (see master_species_table.csv)
      Most of the object functionality will work regardless of the property names
      and values as long as property values are strings. However, there are a few
      exceptions and properties with special handling:
      "model:MODELNAME" : these denote compound names used in model chemical mechanisms
      "lumped" and "emis" are expected to be bool values
      "moleweight" and "dryreac" are expected to be float values
      "henry" is expected to be a tuple of two float values
      "section" is expected to be an int value
      Note, that these properties need not be defined for the object to function.
Methods:
- get_property(key [, exact=True|False])
      Return the value of the compound property with the given key. Exact=False
      allows for fuzzy search; in this case the given key needs only be contained
      in the property name
- get_composition()
      Return the molecular composition as dictionary (uses moleweight)
- get_keys()
      Return the dictionary keys of the compound properties (i.e. column headings
      of the species table)
- get_name()
      Return the best possible name of the compound. If defined, this will be the
      IUPAC_Name, else the alt_Name, and finally the structure term
- match_property(value [, property_name=""][, exact=True][, tol=1.e-2])
      Return a list of property names which contain the given value. The search
      can be narrowed by specifying a property_name or a subset (e.g. "model").
      Exact=True requires an exact match of the value. The tol keyword can be
      used to specify the numerical tolerance for float values to be regarded equal.
      If no properties match, the result is an empty list.
- cross_check_composition()
      Checks consistency between the structure and composition properties and
      tests if the given moleweight is within 0.01 of the calculated value from
      these. Returns True if everything is correct, False otherwise.
- get_pub_chem_compound(self, cid=None)
      Tries to retrieve the matching entries for this compound from the PubChem
      database at http://pubchem.ncbi.nlm.nih.gov/. If a cid is given, this will
      override all information stored in the object. Else a search is performed
      based on a valid PUBCHEM_cid property (value > 0), or - if not present -
      based on the IUPAC_Name and alt_Name properties. The result is a list of
      pubchempy Compound objects (not that that class has the same name but differs).
- cross_check_pub_chem(self, cid=None, add_info=True)
      Compare the property values in this object with the corresponding values
      in the PubChem database and update the property values if requested.

Uses pubchempy module by Matt Swain for PubChem database queries if available"""

import os
from collections import OrderedDict
import numpy as np
from ac.utils import yesno
import ac.utils.moleweight as mw
try:
    import ac.utils.pubchempy as pc
    haspc = True
except:
    haspc = False

__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-09-24'
__license__ = 'MIT'


class Compound(object):
    """defines one chemical substance for use in a chemical model
    compound = Compound([properties])
    compound = Compound.from_string(string, template)
    """
    def __init__(self, properties=None):
        """properties must be a dictionary with compound properties"""
        if properties is None:
            self._properties = OrderedDict()
        else:
            self._properties = properties
            

    @classmethod
    def from_string(cls, string, template, separator=";", lineno=-1):
        """creates a Compound instance from a semicolon delimited string
        template is a list of table column headings which will be used as
        dictionary keys
        Use separator keyword to change from semicolon to any other character"""
        c = OrderedDict()
        converter = { "section": lambda x: int(x),
                      "lumped": lambda x: x.lower() == "true",
#                      "PUBCHEM_cid": lambda x: int(x),
                      "moleweight": lambda x: float(x),
                      "henry": lambda x : tuple([float(v) for v in x[1:-1].split(",")]),
                      "dryreac": lambda x: float(x),
                      "emis": lambda x: x.lower() == "true" }
        defaults = { "section": "0",
                     "lumped" : "False",
                     "moleweight": "-999.9",
                     "henry": "(-999.9, 0.)",
                     "dryreac": "0.",
                     "emis": "False" }
        tokens = string.split(separator)
#        print ">>> template:",template
#        print ">>> tokens  :",tokens
        for i, k in enumerate(template):
            if i < len(tokens) and tokens[i]:
                prop = tokens[i].replace('"', '')   # eliminate single quotes (Excel thing)
            else:
                prop = defaults.get(k, "")
            if k in converter:
                try:
                    c[k] = converter[k](prop)
                except ValueError:
                    print tokens
                    print "Error in %s - token %s (line no %i)" % (string, prop, lineno)
            else:
                c[k] = prop.strip()
        return cls(c)


    def __str__(self, separator=";"):
        """pretty print compound object"""
        res = separator.join(["%s" % (str(v)) for v in self._properties.values()])
        return res
    

    @property
    def properties(self):
        """return dictionary with all properties
        c.properties["section"]
        c.properties"""
        return self._properties

    
    def get_property(self, property_name=None, exact=True):
        """returns the value of a given property.
        Use exact=True (default) to return a value only if the property name
        matches exactly, and exact=False if the given property_name must be
        contained in the actual property key. Use exact=False and an empty
        string for property_name in order to return all properties as a list.
        Example: get_property("model", exact=True) will return None, while
        get_property("model", exact=False) will return the values for all
        "model:XXX" columns in the master species table as a list."""
        if property_name is None:
            raise ValueError("Invalid property_name argument!")
        if exact:
            return self._properties.get(property_name, None)
        else:
            res = []
            for k in self._properties:
                if property_name.lower() in k.lower():
                    res.append(self._properties[k])
            if len(res) == 0:
                res = None
            return res
    

    def get_composition(self):
        """Return molecular composition as dictionary"""
        composition = self.get_property("composition")
        cdict = mw.cstring_to_cdict(composition)
        return cdict
    

    def get_keys(self):
        """return the names of the properties."""
        return self._properties.keys()

    
    def get_name(self):
        """return the best possible name of the compound
        If present, this will be the IUPAC_name, else the alt_name, else the structure"""
        res = self.get_property("IUPAC_Name")
        if not res:
            res = self.get_property("alt_Name")
        if not res:
            res = self.get_property("structure")
        return res
    
        
    def match_property(self, value, property_name="", exact=True, tol=1.e-2):
        """test if the given value is equivalent to any or a specific
        property of the compound. If exact=True (default) the value must
        match the property value exactly. If exact=False it needs only be
        contained in the property value or be numerically similar.
        Use the property_name keyword to confine the search to a specific or
        a limited set of properties.
        The method returns the property name(s) which match the given value."""
        res = []
        for k in self._properties:
            if property_name.lower() in k.lower():
                # tests differ by data type (I know, this is not purely pythonic...)
                test = self._properties[k]
                if isinstance(value, basestring):
                    if not isinstance(test, basestring):
                        test = str(test)
                    if exact:
                        if value.lower() == test.lower():
                            res.append(k)
                    else:
                        if value.lower() in test.lower():
                            res.append(k)
                elif isinstance(value, float):
                    if not isinstance(test, float):
                        continue
                    if exact:
                        if value == test:
                            res.append(k)
                    else:
                        if np.abs(value-test)<tol:
                            res.append(k)
                else:    # other data types only allow for exact comparison
                    if value == test:
                        res.append(k)
        if len(res) == 0:
            res = None
        return res
    

    def cross_check_composition(self):
        """Ensure consistency between the structure and composition properties
        and make sure the moleweight is (approximately) correct"""
        structure = self.get_property("structure")
        composition = self.get_property("composition")
        mweight = self.get_property("moleweight")
        # convert structure and composition to cdicts (moleweight module)
        sdict = mw.composition_from_structure(structure)
        cdict = mw.cstring_to_cdict(composition)
        if not mw.compare_composition(sdict, cdict):
            res = False
            # do again and report errors
            mw.compare_composition(sdict, cdict, verbose=True)
            # print all three moleweight estimates
            fmt = "moleweights:\nvalue: %12.5f, from structure: %12.5f, from composition: %12.5f"
            print fmt % (mweight, mw.moleweight(sdict), mw.moleweight(cdict))
        else:
            # compare mole weights
            tol = 1.e-2
            mweight_fs = mw.moleweight(sdict)
            if np.abs(mweight-mweight_fs) > tol:
                res = False
                fmt = "moleweights:\nvalue: %12.5f, from structure: %12.5f"
                print fmt % (mweight, mweight_fs)
            else:
                res = True
        return res
    

    def get_pub_chem_compound(self, cid=None):
        """attempt to retrieve PubChem record for this compound
        If cid is passed as argument or the 'PUBCHEM_cid' property value
        of the compound is > 0, the PubChem search will look for
        a compound with this compound id. Otherwise, a search is performed
        on the IUPAC_Name and alt_Name properties.
        Note that this can return more than one ChemPub compound.
        The result will always be a list."""
        if not haspc:
            raise ImportError("Module pubchempy could not be loaded!")
        # extract object's PUBCHEM_cid value
        try:
            objcid = int(self.get_property("PUBCHEM_cid"))
        except ValueError:
            objcid = -1
        print "objcid = ", objcid
        # if cid is given, go for it
        if objcid > 0 and cid is None:
            cid = objcid
        if not cid is None or objcid > 0:
            try:
                tmp = pc.get_compounds(cid)
            except pc.NotFoundError:
                tmp = []
            return tmp
        # else try different searches
        cl = []
        name = self.get_property("IUPAC_Name")
        if name:
            try:
                tmp = pc.get_compounds(name, "name")
            except pc.NotFoundError:
                tmp = []
            if len(tmp) > 0:
                cl.extend(tmp)
        name = self.get_property("alt_Name")
        if name:
            # since they are objects Compound(cid) is not the same as Compound(cid)
            # and will not be compressed with set() command. Therefore we must
            # check for existing cids ourselves
            cids = [c.cid for c in cl]
            try:
                tmp = pc.get_compounds(name, "name")
            except pc.NotFoundError:
                tmp = []
            for c in tmp:
                if not c.cid in cids:
                    cl.append(c)
        return cl


    def cross_check_pub_chem(self, cid=None, add_info=True):
        """attempt to retrieve PubChem record for this compound and cross
        check IUPAC name, molecular formula, and molecular weight.
        Returns True if exactly one record was foun don PubChem.
        Use add_info keyword to add the PubChem information into the table
        (will only be done if result is True and after user confirmation)."""
        # report object properties
        formula = self.get_property("composition")
        weight = self.get_property("moleweight")
        name = self.get_property("IUPAC_Name")
        objcid = self.get_property("PUBCHEM_cid")
        if objcid:
            objcid = int(objcid)
        else:
            objcid = 0
        smiles = self.get_property("SMILES")
        print "      %8s %24s %48s %8s %s" % ("CID", "formula", "IUPAC_Name", "weight", "SMILES")
        print "obj : %8i %24s %48s %8.3f %s" % (objcid, formula, name, weight, smiles)
        cl = self.get_pub_chem_compound(cid)
        cequal = False
        if len(cl) == 0:
            print "No PubChem record found."
        elif len(cl) > 1:
            print "More than 1 PubChem record."
        for c in cl:
            print "rec : %8i %24s %48s %8.3f %s" % (c.cid, c.molecular_formula,
                                             c.iupac_name, c.molecular_weight,
                                             c.canonical_smiles)
            # check molecular composition
            cequal = mw.compare_composition(formula, c.molecular_formula)
        # prepare function result
        res = len(cl) == 1
        # add to table if requested
        default = not self.get_property("lumped") and cequal
        if add_info and res and yesno("Update table information?", default):
            self._properties["PUBCHEM_cid"] = cl[0].cid
            if not cl[0].iupac_name is None:
                self._properties["IUPAC_Name"] = cl[0].iupac_name
            else:
                self._properties["IUPAC_Name"] = ""
            self._properties["composition"] = cl[0].molecular_formula
            self._properties["moleweight"] = cl[0].molecular_weight
            self._properties["SMILES"] = cl[0].canonical_smiles
        elif add_info and len(cl) == 0:
            self._properties["PUBCHEM_cid"] = -1  # indicate that no record is available
        return res
    

