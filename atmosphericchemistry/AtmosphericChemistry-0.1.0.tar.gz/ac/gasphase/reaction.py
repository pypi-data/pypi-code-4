# -*- coding: utf-8 -*-
"""
Reaction

Python class to manage properties of single gas-phase reactions.

Instantiation:
- c = Reaction(reactants, products, kterm [,tags][,revision][comments])
      Initiate the object with a list of reactants, a list of tuples (product, yield) for
      the products, and a kterm (any string with a mathematical expression) at a minimum.
      Optionally you can add reaction tags, a revision string ('YYYYMMDDxyz', where 'xyz'
      are author initials), and comments. It will generally be easier to initialize the
      Reaction object with a reaction string in one of the following formats.
- c = Reaction.from_csv(line, lineno, header, separator, filter)
      Create a reaction from a line in spreadsheet format. The format and arguments are
      described in the docstring of this routine.
- c = Reaction.from_kpp(line, lineno, filter)
      Create a reaction from a line in KPP format. The format and arguments are
      described in the docstring of this routine.
- c = Reaction.from_mch(line, lineno, filter)
      Create a reaction from the Stockwell/Goliff RACM input file format. This is a
      multi-line format. The format and arguments are described in the docstring of
      this routine.
- c = Reaction.from_mech(line, lineno)  [new master format]
      Create a reaction from a line in the 'mech' (aka 'master') format. The format and
      arguments are described in the docstring of this routine.
- c = Reaction.from_mozpp(line, lineno, filter)
      Create a reaction from a line in MOZPP format. The format and arguments are
      described in the docstring of this routine.
Attributes:
- author: the (revision) author for this reaction. Will be output together with the
      revision_date in the format 'YYYYMMDDxyz'. Author should generally be a three-letter
      initials.
- comments: an arbitrary string with comments on the reaction.
- kterm: a rateCoefficients object managing the rate coefficient information. For the most
      part it behaves just like a string with a mathematical expression.
- label: a (string) label which will be output in KPP and MOZPP formats. Normally, this is generated
      automatically.
- products: a reactionProducts object (see below).
- reactants: a list of reactant species names.
- revision: the date of the last revision for this reaction together with the author tag.
      This is automatically generated from combining the author and revision_date information.
- revision_date: the date of the last revision for this reaction 
- tags: A string or list of strings for categorizing a reaction (not standardized yet).
      r.tags will always return a comma-separated string. Use list comprehension to
      turn this into a list if you wish (r.tags = [s.strip() for s in tags.split(",")] ).
- _section: a section identifier set when reading from a mech file. Not to be changed by users
      (unless you know what you are doing)
- _lineno: the line number where this reaction was found in the input file. Not to be changed
      by the user.
Interface Methods:
- check_mass(model, speciestable [,ignore_o2])
      Tests the conservation of elements (thus mass) from the reactant to the product side.
      A model name and speciestable instance must be supplied in order to obtain the composition
      information associated with each molecule. The compounds "M" and "hv" will be ignored.
      Multiples of "O2" will also be ignored, unless the ignore_o2 keyword is set to False.
      Check_mass returns True if the mass is conserved in the reaction and False otherwise.
      The function will raise an error if a species is not found in the species table. It is
      therefore advised to call undefined_compounds before calling check_mass().
- get_product_names()
      Returns the compound names of the reaction products without their yields.
- preserve_m([move_right] [,warn])
      Tests for occurence of "M" as quenching partner on both sides of the reaction equation.
      If "M" is only present on the reactant side, it will be added to the product side. If "M"
      only occurs on the product side, an error is raised. Unless the keyword move_right is set
      to False, M will also be placed last on the reactant and product sides. As this is done via
      regex processing, any obscure yield values for M will automatically be removed.
      The warn flag (default: True) controls whether a warning is printed if M is present only
      on the reactant side or whether this is silently fixed. Fixing requires move_right to be True.
- rename_compounds(cdict)
      Changes species names from the keys to the values of the dictionary argument. Hence,
      r.rename({'CH2O':'HCHO', 'CH3COOOH':'CH3CO3H'}) will change all occurences of CH2O to
      HCHO and all occurences of CH3COOOH to CH3CO3H.
- set_revision(revdate, author)
      Sets the revision date and author tag for this reaction. Default is to use today's date
      and an empty author string.
- to_csv([separator] [,nreac] [,nprod] [,dictionary])
      Returns the reaction as a line in the CSV format. Default separator is '\t', default
      number of reactants is 3, default number of products is 12. The dictionary contains
      regular expressions and their replacement strings which will be applied after composing
      the reaction string (currently csv_dict is empty).
- to_easy_reac():
      Returns the reaction as a line in the Juelich EASY format. Note: EASY requires a separate
      call to to_easy_k() for output of the kterm. *** UNDER DEVELOPMENT ***
- to_kpp([label] [,extended] [,dictionary]):
      Returns the reaction as one line in KPP format. If no label is provided, a label will
      be created in the form '<RA_B>'. With extended=True (default), comments for reaction
      tags and revision will be inserted ("MECCA format"). The dictionary contains
      regular expressions and their replacement strings which will be applied after composing
      the reaction string (default: kpp_dict).
- to_mech([short] [,revision]):
      Returns the reaction as one line in the mech (aka 'master') format.
- to_mozpp([label] [,dictionary]):
      Returns the reaction as one line in the MOZPP format. If no label is provided, a label
      will be created in the form '[A_B]', and photolysis labels will be converted to lowercase.
      The dictionary contains regular expressions and their replacement strings which will be
      applied after composing the reaction string (default: moz_dict).
- undefined_compounds(model, speciestable)
      Returns a list of all compounds in the reaction that are not listed in the speciestable
      under a given model name. Model is a string, and speciestable a speciesTable object.

Internal methods (generally not called directly by user):
- convert_kcoeff_to_kterm(kcoeff, reactants, rxntype)
      The csv spreadsheet format specifies rate coefficients as lists of 7 elements, where
      index 0 i sused for constants, indices 0 and 2 for Arrhenius terms, and indices 0, 1,
      3, 4, and 6 for Troe reactions.
- extract_mozpp_jlabel(label)
      Extracts the relevant part of a MOZPP photolysis reaction label. Either a simple identifier
      'jxyz', or an alias expression 'jxyz->,[factor*]jzzz'.
- parse_reaction(rstring, [separator])
      Dissects a reaction string (without kterm, comments, etc.) into reactants and products with
      their yields. Default separator is '->'. For from_kpp the separator is set to '='.
- translate_kterm_from_mozpp(kterm)
      The MOZPP format specifies reaction rate coefficients as lists of 1, 2, or 5 values
      identifying constants, Arrhenius expressions, or Troe expressions, respectively.
      These lists are converted to a mathematical expression: either the constant, or
      'A*exp(B/T)', or 'ktroe(...)'. Note that MOZPP lists '-'Ea, so that the value enters
      the exponent without sign change.
- build_kcoeff_from_kterm()
      This is the reverse operation of convert_kcoeff_to_kterm and forms a 7-parameter list from
      a mathematical expression stored in the kterm attribute.
- build_label(reactants)
      Generates a suitable reaction label. Defaults to 'A_B' for a two-body reaction A+B->...
      Photolysis reactions will be formed as 'jA'.


The Reaction class uses special classes for reaction products and for the kterm management.
Kterm management is handled by the class reactionCoefficient (rates.py). The reactionProducts
class is described below.

class reactionProducts:

Initialisation:
- p = reactionProducts(products)
      The argument can be a string, a list of tuples in the form (product, yield), or
      a valid mathTree object.

Attributes:
- _tree: The reaction products are internally managed as a mathTree object in ordeer to
      preserve branching ratios etc. Some manipulations are however done on the string
      representation of the tree.

Interface methods:
- as_list()
      Return reaction products as alist of tuples with (product, yield)
- as_string([flatten][, multc][, pretty])
      Return reaction products and their yields as a string in the form 'y1*P1 + y2*P2...'.
      Yields that are 1.0 are omitted. If the flatten keyword is set to False, the string
      will preserve the branching notation and multiple yield factors (e.g. '0.3*0.6*(A+B)').
      If flatten is True (default), these will be factorized ('0.18*A+0.18*B' for the example
      above). Multc determines the character to be used for multiplying yields (default: '*',
      but KPP uses ' '), and pretty adds spaces around each '+' sign if True.
- as_tree()
      Return the mathTree object withthe reaction products.
- add(product, yield)
      Add a reaction product with a given yield (default yield is 1.0).
- find(product)
      Returns True if a product is contained in the product list and False otherwise.
- remove(product)
      Removes all occurences of the given product and its yields from the product expression
- rename(oldname, newname)
      Rename one product.
- rename_dict(pdict)
      Rename all occurences of the dictionary keys with the values of the dictionary. This is
      more efficient than renaming several products individually.

"""

# ** ToDo **: think about making reactants and products Compound objects
#             and make reaction "model aware"

from collections import OrderedDict
from copy import deepcopy
import re
import datetime as dt
import numpy as np
from ac.utils.mathtree import mathTree
import ac.utils.moleweight as mw
from ac.utils import format_number
from rates import rateCoefficient

__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-10-03'
__license__ = 'MIT'



# dialect translation dictionaries
# keys are regular expression patterns, values the substitution pattern
# XXX_filter will be used upon input (i.e. from_XXX() methods) before interpreting a line
# XXX_dict will be used upon output (i.e. to_XXX() methods) after composing a line
csv_filter = OrderedDict()
csv_dict = OrderedDict()


kpp_filter = OrderedDict()
kpp_filter[re.compile(r"x\(ip_([A-Za-z]+\w*)\)")] = r"\1"  # replace jx(ip_CCC) with jCCC
kpp_filter[re.compile(r"({§[§0-9.]*}(?:{[0-9.]*\+\-[0-9.]*})?)(?=.*;)")] = r"" # remove Monte Carlo factors 
kpp_filter[re.compile(r"({10\^\([0-9.\+\-]*\)})(?=.*;)")] = r"" # remove Monte Carlo factors (special form)
kpp_filter[re.compile(r"(TEMP)")] = r"T"                   # replace TEMP with T
kpp_filter[re.compile(r"(temp)")] = r"T"                   # replace temp with T
kpp_filter[re.compile(r"(EXP)")] = r"exp"                  # replace EXP with exp
kpp_filter[re.compile(r"(k_3rd\(T,\s?cair,\s?)")] = r"ktroe("  # replace k_3rd with ktroe
kpp_filter[re.compile(r"(\{\s*\+M\s*\})")] = r"+M"         # convert {+M} to +M 
kpp_filter[re.compile(r"(\{\s*[\+\-]\s*[A-Z.]+[A-Za-z0-9.]*\s*\})")] = r""         # remove {+ anything}
#kpp_filter[re.compile(r"(\{\s*\+O2\s*\})")] = r""          # remove {+O2}
#kpp_filter[re.compile(r"(\{\s*\+H2O\s*\})")] = r""         # remove {+H2O}
kpp_filter[re.compile(r"([=\+]\s*[0-9.]+)\s+([A-Z])")] = r"\1*\2"  # add '*' for products with yields

kpp_dict = OrderedDict()
kpp_dict[re.compile(r"(exp)")] = r"EXP"                    # replace exp with EXP
kpp_dict[re.compile(r"(/T)")] = r"/TEMP"                   # replace T in kterm expressions
kpp_dict[re.compile(r"(T/)")] = r"TEMP/"                   # (assumes always /T or T/)
kpp_dict[re.compile(r"(ktroe\()")] = r"k_3rd(TEMP,cair,"   # replace ktroe with k_3rd
kpp_dict[re.compile(r"j([A-Z]+\w*)(?=\b.*;|$|;)")] = r"jx(ip_\1)"         # reformat j labels
kpp_dict[re.compile(r"\b(M \+)")] = r"{M+}"                # comment out "M +" and "+ M"
kpp_dict[re.compile(r"(\+ M)\b")] = r"{+M}"                # comment out "M +" and "+ M"

# Note: mch_filter is only applied to SPECIAL kterms
mch_filter = OrderedDict()
mch_filter[re.compile(r"(TEMP)")] = r"T"                   # replace TEMP with T
mch_filter[re.compile(r"(EXP)")] = r"exp"                  # replace EXP with exp
mch_filter[re.compile(r"(CM)")] = r"M"                     # replace CM with M
mch_filter[re.compile(r"(PRES)")] = r"p"                   # replace PRES with p

mch_dict = OrderedDict()
mch_dict[re.compile(r"(T)")] = r"TEMP"                     # revert changes above
mch_dict[re.compile(r"(exp)")] = r"EXP"
mch_dict[re.compile(r"(\*M)")] = r"*CM"
mch_dict[re.compile(r"(M\*)")] = r"CM*"
mch_dict[re.compile(r"(p)")] = r"PRES"

mozpp_filter = OrderedDict()
mozpp_filter[re.compile(r"(\#)")] = r"!"                   # replace comment sign '#' with '!'

mozpp_dict = OrderedDict()
mozpp_dict[re.compile(r"\s*;\s*($|\!+.*$)")] = r"  \1"     # remove trailing ';' when rate terms are empty,
                                                           # leave comments intact



# ---- reactionProducts class ----

class reactionProducts(object):
    """handles the product terms of a chemical reaction including their yields.
    This class manages three forms of product representation:
    as_list: products are stored as a list of tuples with (product, yield)
    as_string: products are atored as mathematical expression, e.g. '3*C + 0.5*(A+B)'
    as_tree: the mathematical expression is converted into a mathTree object.
    Internally, the products are managed as mathTree object.
    Changes to reaction products (add, remove, replace) are made via regular expressions
    in the string representation."""

    def __init__(self, arg=None):
        """Initialize. Arg can be string, list of tuples or mathTree (or None)."""
        self._tree = None
        if isinstance(arg, mathTree):
            self._tree = arg
        elif isinstance(arg, basestring):
            self._tree = mathTree(arg, autoexecnumops=False)
            self._tree.resolve()
        elif arg is not None and arg:       # assume list of tuples
            s = "+".join(["%f*%s" % (y,p) for p, y in arg])
            self._tree = mathTree(s, autoexecnumops=False)
            self._tree.resolve()


    def __str__(self):
        return self.as_string()

    
    def as_list(self):
        """return products and yields as list of tuples. This is achieved through
        factorisation of a copy of the internal mathTree structure."""
        res = []
        if self._tree is not None:
            s = self.as_string(flatten=True)
            tokens = s.split("+")
            for item in tokens:
                subs = item.split("*")
                if len(subs) == 1:
                    res.append( (subs[0].strip(), 1.0) )
                elif len(subs) == 2:
                    res.append( (subs[1].strip(), float(subs[0])) )
                else:
                    raise ValueError("Cannot convert %s to (yield, product) tuple!"%(item))
        # check for empty list
        if len(res) == 1 and res[0] == ("", 1.):
            res = []
        return res


    def as_string(self, flatten=True, multc='*', pretty=True):
        """return products and yields as string (e.g. for input into mechanism file).
        If flatten is True, the string will be construced from a copy of the product tree
        after factorisation. Multc allows changing the character for multiplication
        (KPP uses blanks), and pretty=True adds spaces around the '+' characters."""
        res = ""
        if self._tree is not None:
            if flatten:
                tmp = self._tree.copy()
                tmp.factorize()
                res = str(tmp)
            else:
                res = str(self._tree)
        if multc != "*":
            res = res.replace("*", multc)
        if pretty:
            res = res.replace("+", " + ")
        return res
    
                
    def as_tree(self):
        """return products and yields as mathTree object."""
        return self._tree


    def add(self, product=None, factor=1.):
        """Append a product to the end of the reaction."""
        if product is not None:
            # safety checks
            if not isinstance(product, basestring):
                raise ValueError("Product must be string type! %s"%(str(product)))
            if not product:
                raise ValueError("Product must not be empty!")
            s = self.as_string(flatten=False)
            if np.abs(factor-1.) < 1.e-9:
                s += " + %s" % (product)
            else:
                s += " + %f*%s" % (factor, product)
            s = s.strip()
            if s.startswith("+"):
                s = s[1:]
            self._tree = mathTree(s)
            self._tree.resolve()
            

    def find(self, product):
        """Return True if product is contained in expression."""
        res = False
        if product is not None:
            s = self.as_string(flatten=False)
            # regular expression pattern:
            # p finds prod1
            p = re.compile(r"\b(%s+?)\b" % (product))
#            print ">>>> s=",s
            res = re.search(p, s)
        return res
    
        
    def remove(self, product=None):
        """Removes a product from the expression."""
        if product is not None:
            s = self.as_string(flatten=False)
            # regular expression patterns:
            # p1 finds '...+[yield*]product'
            # p2 finds '[yield*]product+...'
            # p3 finds any remaining terms with product
            p1 = re.compile(r"(\+\s*[0-9\.]*(?:[eE][-]?\d+)?\*%s+?|\+\s*%s+?)\b" % (product, product))
            p2 = re.compile(r"(\b[0-9\.]*(?:[eE][-]?\d+)?\*%s+?\s*\+|\b%s+?\s*\+)" % (product, product))
            p3=re.compile(r"\(?(\b[0-9\.]*(?:[eE][-]?\d+)?\*%s+?\s*|\b%s+?\b)\s*\)?" % (product, product))
#            print ">>>> s=",s
            s = re.sub(p1, "", s)
#            print ">>>> s=",s
            s = re.sub(p2, "", s)
#            print ">>>> s=",s
            s = re.sub(p3, "", s)
#            print ">>>> s=",s
            self._tree = mathTree(s)
            self._tree.resolve()
            

    def rename(self, prod1=None, prod2=None):
        """Rename a product compound."""
        if prod1 is not None:
            if prod2 is None or not prod2:
                raise ValueError("Replacement product must not be empty!")
            s = self.as_string(flatten=False)
            # regular expression pattern:
            # p finds prod1
            p = re.compile(r"\b(%s+?)\b"%(prod1))
#            print ">>>> s=",s
            s = re.sub(p, prod2, s)
#            print ">>>> s=",s
            self._tree = mathTree(s)
            self._tree.resolve()
            

    def rename_dict(self, cdict):
        """Rename all products given as dict keys to the respective dict values.
        More efficient to do all string processing at once."""
        if cdict is not None:
            s = self.as_string(flatten=False)
            for k, v in cdict.items():
                # regular expression pattern:
                # p finds prod1
                p = re.compile(r"\b(%s+?)\b"%(k))
#                print ">>>> s=",s
                s = re.sub(p, v, s)
#                print ">>>> s=",s
            self._tree = mathTree(s)
            self._tree.resolve()
            

# ---- Reaction class ----

class Reaction(object):
    """defines one chemical gas-phase reaction for use in a chemical model
    """

    def __init__(self, reactants=None, products=None, kterm=None,
                 tags=None, revision=None, comments="", label="", section="", lineno=-1):
        """arguments:
        reactants: list with species names reacting (may include 'M' or 'hv')
        products: list of tuples with species names and product yields
        kterm: string with rate coefficient term
        rtags: list of strings defining the reaction type, mechanism subset, etc.
        revdate: string with revision date and author (YYYYMMDDxyz)
        rcomment: comment string
        """
        self.reactants = reactants
        self.products = products
        self.kterm = kterm
        self._tags = tags
        self.set_revision(revision)   # sets self._revdate and self._author
        self._comments = comments
        self._label = label           # a reaction label (usually set automatically)
        self._section = section       # name of section (in mech file) where reaction is found
        self._lineno = lineno         # line number in file from where reaction was read
         

    @classmethod
    def from_csv(cls, line, lineno=-1, header=None, separator="\t", filter=csv_filter):
        """creates a Reaction instance from a spreadsheet line in Alex's
        format. Lineno can be used to track the line no from the input file for error
        reporting.
        Format is: code; reac.1; ...; reac.N; prod.1; ...; prod.M; ai.fac; bi.fac; ei.fac; \
                   a0.fac; b0.fac; e0.fac; ffac; mech; rxn.type; comment
        The meaning of each column must be supplied via the header argument which is a list of
        the column headings from the spreadsheet. The names given above must be present; other
        columns will simply be ignored. The max. number of reactants and products can vary.
        Default separator is tabstopp. 
        Missing entries are coded as NA. prod.x contains 'yield*' if yield != 1.
        Filter is a dictionary with compiled regular expressions which is applied before
        interpreting the line. Currently, no filtering is done by default.
        """
        if not line.strip():
            return None
        if header is None or not header:
            raise ValueError("From_csv requires a token list as header argument!")
        # apply initial string filtering
        line = line.rstrip("\r\n")  
        if filter is not None:
#            print "< ",line
            for k, v in filter.items():
                line = re.sub(k, v, line)
#            print "> ",line
        # split line
        tokens = line.split(separator, len(header)-1)  # extra columns treated as part of comment
        if len(tokens) != len(header):
            raise ValueError("Invalid line(%i): number of columns doesn't match! %s"%(lineno, line))
        # initialize
        code = ""
        reactants = []
        products = ""
        kcoeff = [None for i in range(7)]
        kterm = ""
        rxntype = ""   # only used to fix missing hv in photo reactions
        tags = ""
        comments = ""
        # loop over header tokens and interpret corresponding data column
        for i, h in enumerate(header):
            h = h.strip().lower()
            if h.startswith("code"):
                code = tokens[i]
            elif h.startswith("reac") and tokens[i].upper() != "NA":
                reactants.append(tokens[i])
            elif h.startswith("prod") and tokens[i].upper() != "NA":
                products += "+"+tokens[i]
            elif h.startswith("ai.fac") and tokens[i].upper() != "NA":
                kcoeff[0] = float(tokens[i])
            elif h.startswith("bi.fac") and tokens[i].upper() != "NA":
                kcoeff[1] = float(tokens[i])
            elif h.startswith("ei.fac") and tokens[i].upper() != "NA":
                kcoeff[2] = float(tokens[i])
            elif h.startswith("a0.fac") and tokens[i].upper() != "NA":
                kcoeff[3] = float(tokens[i])
            elif h.startswith("b0.fac") and tokens[i].upper() != "NA":
                kcoeff[4] = float(tokens[i])
            elif h.startswith("e0.fac") and tokens[i].upper() != "NA":
                kcoeff[5] = float(tokens[i])
            elif h.startswith("ffac") and tokens[i].upper() != "NA":
                kcoeff[6] = float(tokens[i])
            elif h.startswith("mech") and tokens[i].upper() != "NA":
                pass   # ignore mechanism information
            elif h.startswith("rxn.type") and tokens[i].upper() != "NA":
                rxntype = tokens[i]
            elif h.startswith("comment") and tokens[i].upper() != "NA":
                comments = tokens[i]
            elif tokens[i].upper() != "NA":
                print "*** unknown header column! %s" % (h)
        if products.startswith("+"):
            products = products[1:]
#        print "reactants = ",reactants
#        print "products = ",products
#        print "kcoeff = ",kcoeff
        # analyze kcoeff to form kterm
        # assume that we have either a one-parameter constant, a two-parameter Arrhenius
        # expression or a 5-parameter Troe expression. Photolysis reactions will get a j label
        # made up. If no kcoeff is defined for a non photolysis reaction, a 'k' label will be
        # constructed based on the reactants without 'M'
        kterm = cls.convert_kcoeff_to_kterm(kcoeff, reactants, rxntype)
        return cls(reactants, products, kterm, comments=comments, lineno=lineno)
        

    @classmethod
    def from_kpp(cls, line, lineno=-1, filter=kpp_filter):
        """creates a Reaction instance from a KPP formatted reaction.
        Lineno can be used to track the line no from the input file for error
        reporting.
        Format is: <label> reaction string : kterm ;
        reaction string is:  A [+ B | hv][+ C] = product expression
        Product yields are specified as factors without a '*' sign.
        Kterm can be any valid mathematical expression.
        This method partly supports the extended KPP/MECCA format, where a couple of optional
        comments are inserted with special meaning:
        <label> reaction string : {tags} kterm{MCF} ; {reference}
        Tags will be read out, the Monte Carlo factors (MCF) will be ignored, and the
        reference will be extracted as comment.
        Filter is a dictionary with compiled regular expressions which is applied before
        interpreting the line. From_kpp employs a several filters by default.
        """
        if not line.strip():
            return None
        # save copy for error reporting
        oriline = line
        # apply initial string filtering
        line = line.rstrip("\r\n")  
        if filter is not None:
#            print "< ",line
            for k, v in filter.items():
                line = re.sub(k, v, line)
#            print "> ",line
        # get end of line comment
        comments = ""
        ic0 = line.rfind("{")
        ic1 = line.rfind("}")
        isc = line.rfind(";", 0, ic0 if ic0 > 0 else len(line))
        if ic0 > isc and isc > 0:  # comment found (MECCA)
            comments = line[ic0+1:ic1].strip()
            line = line[0:ic0].strip()
        isc = line.rfind(";")
        if isc < 0:
            raise ValueError("Invalid KPP input line (%i): must end with ';'!\n%s\noriginal line: %s"  \
                             %(lineno, line, oriline))
        # remove end
        rline = line[0:isc].strip()
        # get kterm and tags
        rline, kexpr = rline.split(":", 1)
        kterm = kexpr.strip()
        tags = ""
        if kterm.startswith("{"):  # tags defined (MECCA)
            ic1 = kterm.find("}")
            tags = kterm[2:ic1].strip()  # ignore %-sign, too
            kterm = kterm[ic1+1:].strip()
        # remove label
        rline = rline.strip()
        if rline.startswith("<"):
            idx = rline.index(">")
            label = rline[1:idx]
            rline = rline[idx+1:].strip()
        # analyze reaction
        # insert '*' symbols where needed
        pattern = re.compile(r"([0-9.]) [A-Z]")   # finds last char of a number as start
        pos = re.finditer(pattern, rline)
        for p in pos:
            idx = p.start()
            rline = rline[0:idx+1] + "*" + rline[idx+2:]
        reactants, products = cls.parse_reaction(rline, separator="=")
        return cls(reactants, products, kterm, tags=tags, comments=comments, lineno=lineno)


    @classmethod
    def from_mch(cls, line, lineno=-1, kterm="", comments=""):
        """creates a Reaction instance from several input lines of the Stockwell/Goliff
        RACM input file format.
        Lineno can be used to track the line no from the input file for error
        reporting. The mechanism class will preprocess input so that only one reaction
        line is input as argument to this routine and kterm expressions and comments are
        already separated out.
        The format is a multi-line format with fixed column width. Column is given in
        parantheses. Fields may be empty.
        001 XXX1(5) XXX2(11) ->(21) yyy1(24) PPP1(29) yyy2(35) PPP2(41) yyy3(47) PPP3(53)
        &                           yyy4(24) ...
        KTYPE arguments
        ! comments
        Species names are max. 4 characters.
        KTYPE is one of:
        PHOTOLYSIS
        THERMAL  A-FACT  x.xxE-xx  E/R  xxx.x
        TROE  KO  x.xxE-xx  N  x.x  KINF x.xxE-xx  M x.xx [x.x] (option for fc)
        TROE-EQUIL  KO  x.xxE-xx  N  x.x  KINF x.xxE-xx  M x.xx (continued on next line!)
                 A-FACT  x.xxE-xx  B  xxxxx.x
        SPECIAL RWK(#) = kterm expression
        Note: SPECIAL can have several lines defining temporary variables. Example:
        SPECIAL TMP3 = kterm expression.
        Filter is a dictionary with compiled regular expressions which is applied before
        interpreting the line."""
        if not line.strip():
            return None
        # process reaction string
        left, right = line.split("->", 1)
        reactants = left.split()
        # must insert "+" and "*" into products
        products = ""
        tokens = right.split()
        for i, t in enumerate(tokens):
            products += t
            if i+1 < len(tokens):
                sep = "*" if t[0] in "0123456789." else "+"
                products += sep
        # process kterms
        kterm = kterm.replace(";", " ")
        if kterm.upper().startswith("PHOTOLYSIS"):
            # add hv to reactants
            reactants.append("hv")
            # build jlabel
            kterm = "j"+reactants[0]
        elif kterm.upper().startswith("THERMAL"):
            tokens = kterm.split()
            if float(tokens[4]) == 0.:
                kterm = tokens[2]
            elif tokens[4].startswith("-"):
                kterm = "%s*exp(%s/T)" % (tokens[2], tokens[4][1:])
            else:
                kterm = "%s*exp(-%s/T)" % (tokens[2], tokens[4])
        elif kterm.upper().startswith("TROE "):
            tokens = kterm.split()
            if len(tokens)<10:
                tokens.append("0.6")   # add fc factor
            kterm = "ktroe(%s,%s,%s,%s,%s)" % (tokens[2], tokens[4], tokens[6],
                                               tokens[8], tokens[9])
        elif kterm.upper().startswith("TROE-EQUIL"):
            tokens = kterm.split()
            kterm = "kt_equil(%s,%s,%s,%s,0.6,%s,%s)" % (tokens[2], tokens[4], tokens[6],
                                                         tokens[8], tokens[10], tokens[12])
        elif kterm.upper().startswith("SPECIAL"):
            kterm = "k" + "_".join([s for s in reactants if not s in ["M", "hv"]])
        else:
            raise ValueError("Unknown kterm expression in %s (line %i)"%(line, lineno))
            
        # create reaction instance
        tags = []
        revision = ""
        return cls(reactants, products, kterm, tags, revision, comments, lineno=lineno)

        
    @classmethod
    def from_mech(cls, line, lineno=-1, section=""):
        """creates a Reaction instance from an input line of the new 'master format'.
        Lineno can be used to track the line no from the input file for error
        reporting.
        Format is: reaction string : kterm [; tags] [! <revision> comments]
        reaction string is:  A [+ B | hv][+ C] -> product expression
        product expression can be any valid algebraic expression with
            species names, multipliers, sums, products, and parantheses
        kterm can be a mathematical expression (including simple numbers or constants)
        tags are a comma-separated list of 'reaction labels'
        revision is a string of form YYYYMMDDxyz, where xyz is the authors initials
        comments is an arbitrarily formatted string.
        """
        # don't do anything if string is empty
        if not line.strip():
            return None
        # save copy for error reporting
        oriline = line
        line = line.rstrip("\r\n")  
        # look for comments and revision
        comments = ""
        revision = ""
        if "!" in line:
            line, comments = line.split("!", 1)
            ir0 = comments.find("<")
            ir1 = comments.find(">")
            if ir0 > 0 and ir1 > ir0:   # found revision tag
                revision = comments[ir0+1:ir1].strip()
                comments = comments[ir1+1:].strip()
        # could be comment line - if nothing else: ignore
        if not line.strip():
            return None
        # get tags
        tags = []
        if ";" in line:
            line, tagline = line.split(";", 1)
            tags = [s.strip() for s in tagline.split(",")]
        # get kterm
        if ":" in line:
            line, kterm = line.split(":", 1)
            kterm = kterm.strip()
        else:
            raise ValueError("Reaction line must contain kterm! %s"%(oriline))
        # get reactants and products with yields
        reactants, products = cls.parse_reaction(line)
        return cls(reactants, products, kterm, tags, revision, comments, section=section, lineno=lineno)


    @classmethod
    def from_mozpp(cls, line, lineno=-1, filter=mozpp_filter, section=""):
        """creates a Reaction instance from a MOZART preprocessor (mozpp) formatted
        reaction. 
        Lineno can be used to track the line no from the input file for error
        reporting.
        Format is: [label] reaction string ; kterm [!|# comments]
        reaction string is:  A [+ B | hv][+ C] -> product expression
        If product expression contains yields != 1, they will have factors with '*' sign.
        kterm typically consists of one or two numbers for an Arrhenius expression, or of
        six values for a Troe expression. If blank it is treated as a 'usrrxt'. In this case
        a variable 'k_R1_R2' will be generated.
        Note: mozpp can have continuation lines which must start with '+' and contain only
        additional products. The rate term must be on the first line. This method expects
        that continuation lines have been 'merged' beforehand, and the entire reaction is
        given in one string.
        A couple of special reaction labels (cph, userdefined, tau, ion, elec) will be preserved
        as reaction tags.
        J-value labels are interpreted (see extract_mozpp_jlabel method).
        Filter is a dictionary with compiled regular expressions which is applied before
        interpreting the line. 
        """
        if not line.strip():
            return None
        # save copy for error reporting
        oriline = line
        line = line.rstrip("\r\n")  
        # apply initial string filtering
        if filter is not None:
#            print "< ",line
            for k, v in filter.items():
                line = re.sub(k, v, line)
#            print "> ",line
        # get comments (we assume that '#' was converted to '!' by a filter)
        comments = ""
        tags = []
        tokens = line.split("!", 1)
        if len(tokens) == 2:
            comments = tokens[1].strip()
        rline = tokens[0].strip()   # reaction expression
        # get kterm
        if ";" in rline:
            rline, kterm = rline.split(";", 1)
        else:
            kterm = None   # to be constructed later
        # remove label and construct kterm in case of j values or set special tags
        if rline.startswith("["):
            idx = rline.index("]")
            label = rline[1:idx]
            if label.startswith("j"):
                kterm, jtag = cls.extract_mozpp_jlabel(label)
                if jtag:
                    tags.append(jtag)
            elif "cph" in label.lower():
                tags.append("cph")
            elif "ion" in label.lower():
                tags.append("ion")
            elif "elec" in label.lower():
                tags.append("elec")
            elif "tau" in label.lower():
                tags.append("tau")
            rline = rline[idx+1:].strip()
        reactants, products = cls.parse_reaction(rline)
        # construct kterm as kR1_R2 if None
        if kterm is None:
            if "het" in label.lower():
                kterm = "het" + "_".join([r for r in reactants if r != "M" and r != "hv"])
            else:
                kterm = "k" + "_".join([r for r in reactants if r != "M" and r != "hv"])
        else:
            kterm = cls.translate_kterm_from_mozpp(kterm)
        return cls(reactants, products, kterm, tags, comments=comments, lineno=lineno, section=section)


    def __str__(self, separator=";"):
        """pretty print compound object"""
        res = separator.join(["%s"%(str(v)) for v in self._reactants])
        return res
    

    @property
    def reactants(self):
        """return list of reactants"""
        return self._reactants


    @reactants.setter
    def reactants(self, arg=None):
        """set reactants for this reaction. Arg must not be None or empty.
        If 'hv' is among the reactants the reaction is marked as photo reaction."""
        if arg is None or not arg:
            raise ValueError("At least one reactant must be defined!")
        self._isphoto = "hv" in arg
        self._reactants = arg


    def get_product_names(self):
        """return list of product names (without yields)."""
        return [p for p, y in self.products]

    
    @property
    def products(self):
        """return list of products and their yields"""
        return self._products.as_list()


    @products.setter
    def products(self, arg=None):
        """set products and yields for this reaction. Arg may be None or empty
        and can either be a string, a list of tuples with (product, yield), or a
        mathTree object.
        An instance of a reactionProduct object will be created."""
        self._products = reactionProducts(arg)
##        print "***TEST:"
##        print "string: ",self._products.as_string()
##        print "string2: ",self._products.as_string(flatten=False)
##        print "tree: ",self._products.as_tree()
##        print "list: ",self._products.as_list()
##        print "attribute: ",self.products

    @property
    def kterm(self):
        """return rate coefficient expression"""
        return self._kterm


    @kterm.setter
    def kterm(self, arg):
        """set rate coefficient expression for this reaction. This will create an instance of
        a rateCoefficient object. Arg can be either a string or a mathTree instance."""
        self._kterm = rateCoefficient(arg)


    @property
    def tags(self):
        """return always as string"""
        if self._tags is None:
            return ""
        elif isinstance(self._tags, basestring):
            return self._tags
        else:    # assume list
            return ",".join(self._tags)


    @tags.setter
    def tags(self, value):
        """Set reaction tags. Argument should be list of strings or single string"""
        self._tags = value

        
    @property
    def author(self):
        return self._author


    @property
    def revision_date(self):
        return self._revision_date


    @property
    def revision(self):
        if self._revision_date is None:
            res = self._author     # defaults to ""
        else:
            res = self._revision_date.strftime("%Y%m%d")+self._author
        return res


    def set_revision(self, revdate=dt.date.today(), author=""):
        if revdate is None or not revdate:
            self._revision_date = None    # may want to rethink this in order to force documentation(?)
        elif isinstance(revdate, basestring):
            # if more than 8 characters, assume it is YYYYMMDDxyz with xyz = author initials
            if len(revdate)>8:
                author = revdate[8:]
                revdate = revdate[0:8]
            try:
                self._revision_date = dt.date(int(revdate[0:4]), int(revdate[4:6]), int(revdate[6:8]))
            except ValueError:
                raise ValueError("Invalid format for revision date (must be 'YYYYMMDD[xyz]': >%s<" % (revdate))
        else:   # assume revdate is correct date object
            self._revision_date = revdate
        self._author = author


    @property
    def comments(self):
        return self._comments


    @property
    def label(self):
        return self._label


    @label.setter
    def label(self, label=""):
        self._label = label


    # --- interface methods ---
    def check_mass(self, model=None, speciestable=None, ignore_o2=True, quiet=False):
        """Count atoms on reactants and products side and report inconsistencies. Returns
        True if the reaction is mass conserving (optionally ignoring multiples of 'O2') and
        False otherwise. It is advised to call undefined_compounds() before calling this method.
        """
        if speciestable is None:
            raise ValueError("Speciestable must be a valid object!")
        mnames = speciestable.get_model_names()
        if model is None or model not in mnames:
            raise ValueError("Model must be a valid model name! Allowed names: %s"%(", ".join(mnames)))
        # compile mass information on reactant side
        rcomp = {}
        for r in self.reactants:
            if r != "M" and r != "hv" and r != "e":
                compound = speciestable.find_model_species(r, model)
                if compound is None:
                    raise ValueError("Unknown reactant %s (model:%s)\n%s"%(r, model, self.to_mech(short=True)))
                rtmp = compound.get_composition()
                if not rtmp:
                    raise ValueError("No composition information for reactant %s"%(r))
                for atom in rtmp:
                    if atom in rcomp:
                        rcomp[atom] += float(rtmp[atom])
                    else:
                        rcomp[atom] = float(rtmp[atom])
        # compile mass information on reactant side
        products = self.products
        pcomp = {}
        for p, y in products:
            compound = speciestable.find_model_species(p, model)
            if compound is None:
                raise ValueError("Unknown product %s (model:%s)\n%s" % (p, model, self.to_mech(short=True)))
            ptmp = compound.get_composition()
            if not ptmp and p != "M":
                raise ValueError("No composition information for product %s" % (p))
            for atom in ptmp:
                if atom in pcomp:
                    pcomp[atom] += y * ptmp[atom]
                else:
                    pcomp[atom] = y * ptmp[atom]
        # compare the two
        mismatch = []
        for ratom in rcomp:
            rcnt = rcomp[ratom]
            pcnt = pcomp.get(ratom, 0.)
            if np.abs(rcnt-pcnt) > 1.e-4:
                # exclude modulo O2
                if ignore_o2 and ratom == "O" and np.abs(rcnt-pcnt) % 2. < 1.e-4:
                    continue
                else:
                    mismatch.append("%s : %s" % (ratom, format_number(pcnt-rcnt)))
        # add newly formed elements
        for patom in pcomp:
            if not patom in rcomp:
                if ignore_o2 and patom == "O" and pcomp[patom] % 2. < 1.e-4:
                    continue
                mismatch.append("%s : %s" % (patom, format_number(pcomp[patom])))
        if len(mismatch) > 0 and not quiet:
            print "Mass imbalance in %s" % (self.to_mech(short=True))
            print ", ".join(mismatch)
            print ">>>> rcomp = ", rcomp
            print ">>>> pcomp = ", pcomp
            print
        return len(mismatch) == 0


    def copy(self):
        """Returns a clone of the reaction."""
        return deepcopy(self)

    
    def preserve_m(self, move_right=True, warn=True):
        """Ensure that +M appears on the product side if it appears on the reactant
        side; give warning if +M only occurs on the product side, and optionally move
        M to the last position in the reactant and product lists."""
        # need to work on products as string to preserve branching
        products = self._products.as_string(flatten=False, pretty=False)
        if "M" in self.reactants:
            if self._products.find("M"):
                # remove M and add again later. This makes sure it is rightmost
                # and also cleans up wrong multiplicities of M
                if move_right:
                    self._products.remove("M")
            elif warn:  # M only on reactant side
                print "*** Cannot find M in products although present in reactants!\n%s" % (self.to_mech(short=True))
            # move M to the right of reactant list
            if move_right:
                self._reactants.pop(self._reactants.index("M"))
                self._reactants.append("M")
                self._products.add("M")
        else:   # M not in reactants - check if in products only
            if self._products.find("M"):
                raise ValueError("M appears in product list, but not in reactants!\n%s" % (self.to_mech(short=True)))


    def rename_compounds(self, cdict=None):
        """Rename compounds based on a translation dictionary. This takes into account
        reactants, products, and kterm expressions."""
        if cdict is not None:
            # work on reactants
            for k, v in cdict.items():
                if k in self._reactants:
                    self.reactants[self.reactants.index(k)] = v
                # try again in case we have a self-reaction
                if k in self._reactants:
                    self.reactants[self.reactants.index(k)] = v
            # work on products
            self._products.rename_dict(cdict)
            # work on kterm
            kterm = str(self.kterm)
            for k, v in cdict.items():
                if k in kterm:
                    kterm = kterm.replace(k, v)
            self.kterm = kterm
                        
                    
    def to_csv(self, separator="\t", nreac=3, nprod=12, label=None, dictionary=csv_dict):
        """Returns string with reaction written as one spreadsheet line. See
        from_csv for format description.
        You can supply a reaction label to identify this reaction ('code' column). If None
        is given, the method first checks the object's label attribute and builds a default
        label if nothing is defined there. Note that the Mechanism object always constructs
        new labels in order to avoid duplicates."""
        NREACTANTS = nreac   # number of columns for reactants
        NPRODUCTS = nprod    # number of columns for products
        # construct label
        if label is None:
            label = self.label
            if not label:
                label = self.build_label(self.reactants)
        # prepare reactant list with fixed length
        rl = [r for r in self.reactants]
        while len(rl) < NREACTANTS:
            rl.append("NA")
        if len(rl) > NREACTANTS:
            raise ValueError("Too many reactants for spreadsheet! %s"%(str(rl)))
        # prepare product list with fixed length
        pl = self._products.as_string(pretty=False).split("+")
        while len(pl) < NPRODUCTS:
            pl.append("NA")
        if len(pl) > NPRODUCTS:
            raise ValueError("Too many products for spreadsheet! %s"%(str(pl)))
        # prepare 7-parameter k coefficient list
        kl = self.build_kcoeff_from_kterm()
        # prepare tags (put in "mech" column)
        tags = self.tags if self.tags else "NA"
        # store rxntype
        rxntype = "photolysis" if self._isphoto else "thermal"
        # prepare comments
        c = self.comments
        # put everything together
        output_list = [ label ]
        output_list.extend(rl)
        output_list.extend(pl)
        output_list.extend(kl)
        output_list.append(tags)
        output_list.append(rxntype)
        output_list.append(c)
        res = separator.join(output_list)
        # apply dictionary for final formatting
        if dictionary is not None:
            for k, v in dictionary.items():
                res = re.sub(k, v, res)
        return res
            

    def to_easy_reac(self):
        """Returns string with reaction in Juelich's easy format."""
        # *** UNDER DEVELOPMENT ***
        res = " + ".join(self.reactants)
        res += " --> "
        res += self._products.as_string()
        return res


    def to_easy_k(self):
        """Returns string with k-value in Juelich's easy format.
        This contains the entire reaction string."""
        return "k[%s]=%s" % (self.to_easy_reac(), str(self.kterm))

        
    def to_kpp(self, label=None, extended=True, add_prod=False, default_tags="StTrG",
               dictionary=kpp_dict):
        """Returns string with reaction written in KPP format.
        Use extended keyword to add extra information as in MECCA.
        Add_prod = True will add a dummy PROD compound as product to empty reactions.
        You can supply a reaction label to identify this reaction ('code' column). If None
        is given, the method first checks the object's label attribute and builds a default
        label if nothing is defined there. Note that the Mechanism object always constructs
        new labels in order to avoid duplicates.
        Default_tags are added to the string if no tags are stored in the reaction. These
        tags are used in MECCA for filtering reactions when building a mechanism."""
        if label is None:
            label = self.label
            if not label:
                label = self.build_label(self.reactants)
        if self._isphoto:
            label = "J" + label[1:]
        else:
            label = "R" + label
        label = "<%s>" % (label)
        res = "%-16s " % (label)
        res += " + ".join(self.reactants)
        res += " = "
        prods = self._products.as_string(multc=" ")
        # add dummy product if no products are defined in reaction
        if add_prod and not prods.strip():
            prods = "PROD"
        res += prods
        # potentially increase length
        res = "%-60s" % (res)
        # continue
        res += " : "
        if extended:
            tags = self.tags if self.tags else default_tags
            res += "{%%%s} " % (tags)
        res += str(self.kterm)
        res += ";"
        if extended and self.comments:
            res += "  {%s} " % (str(self.comments))
        # apply dictionary for final formatting
        if dictionary is not None:
            for k, v in dictionary.items():
                res = re.sub(k, v, res)
        return res

    
    def to_mech(self, short=False, revision=None):
        """Returns string with reaction written in mech format.
        If short is True, only the reaction string itself will be printed
        Use the revision keyword to overwrite the current revision tag (changes object)."""
        res = " + ".join(self.reactants)
        res += " -> "
        res += self._products.as_string(flatten=False)
        # potentially increase length
        res = "%-60s" % (res)
        # continue
        if not short:
            res += " : "
            res += str(self.kterm)
            if self.tags is not None:
                res += " ; "
                res += self.tags
            if revision is not None:
                self.set_revision(revision)
            if self.revision or self.comments:
                res += " !"
            if self.revision:
                res += " <%s>" % (self.revision)
            if self.comments:
                res += " %s" % (self.comments)
        return res

    
    def to_mozpp(self, label=None, dictionary=mozpp_dict, use_cph=True):
        """Returns string with reaction written in MOZPP format.
        You can supply a reaction label to identify this reaction ('code' column). If None
        is given, the method first checks the object's label attribute and builds a default
        label if nothing is defined there. Note that the Mechanism object always constructs
        new labels in order to avoid duplicates.
        MOZPP labels are quite 'elaborate'...
        Use_cph modifies reaction labels if a cph tag is found."""
        if label is None:
            label = self.label
            if not label:
                label = self.build_label(self.reactants)
        # add mozpp jalias if requested
        kexpr = str(self.kterm)
        # adjust label for juser tags
        if "juser1" in self.tags:
            label = kexpr + "=userdefined,"
        elif "juser2" in self.tags:
            label = kexpr + "=userdefined,userdefined"
        elif self._isphoto and kexpr[0] in "j.0123456789" and kexpr != label:
            label += "->,%s" % (kexpr)
        if self._isphoto:
            label = label.lower()
        # adjust label for cph tag
        if "cph" in self.tags and use_cph:
            label = "cph_" + label + ",cph"
        # adjust label for tau tag
        if "tau" in self.tags:
            label = label + "_tau"
        # adjust label for ion and elec tags
        if "ion" in self.tags:
            if label.startswith("cph_"):
                label = label[4:]    # replace cph_ with ion_
            label = "ion_" + label
        if "elec" in self.tags:
            if label.startswith("cph_"):
                label = label[4:]    # replace cph_ with ion_
            label = "elec_" + label
        # build completely new label if het reaction (kterm starts with 'het')
        if kexpr.startswith("het"):
            label = kexpr
        label = "[%s]" % (label)
        res = " %-16s " % (label)
        res += " + ".join(self.reactants)
        res += " -> "
        res += self._products.as_string()
        # potentially increase length
        res = "%-60s" % (res)
        # continue
        if not self._isphoto:
            res += " ; "
            kl = self.kterm.extract_coefficients()
            if len(kl) in [0, 1, 2, 5]:
                res += ", ".join([k for k in kl])
            else:
                print "**** Cannot translate kterm to MOZPP!\n%s" % (self.to_mech())
        if self.comments:
            res += "  ! %s" % (str(self.comments))
        # apply dictionary for final formatting
        if dictionary is not None:
            for k, v in dictionary.items():
                res = re.sub(k, v, res)
        return res


    def undefined_compounds(self, model=None, speciestable=None):
        """Ensure that all species in the reaction are valid species for this model.
        Speciestable must be a valid speciesTable object, and model must be a string
        that is contained in speciestable.get_model_names()."""
        if speciestable is None:
            raise ValueError("Speciestable must be a valid object!")
        mnames = speciestable.get_model_names()
        if model is None or model not in mnames:
            raise ValueError("Model must be a valid model name! Allowed names: %s"%(", ".join(mnames)))
        compounds = self.get_product_names()
        compounds.extend(self.reactants)
        ucompounds = set(compounds)   # removes duplicates
        undef = []
        for c in ucompounds:
            test = speciestable.find_model_species(c, model)
            if test is None:
                undef.append(c)
        return undef
    
        
    # --- helper routines ---
    @staticmethod
    def convert_kcoeff_to_kterm(kcoeff, reactants, rxntype):
        """Converts a 7-element list with values to a kterm expression. This is needed
        for reading in Alex's spreadsheet format."""
        vcnt = 7-kcoeff.count(None)   # number of valid entries
        if vcnt == 1:
            kterm = "%s" % (format_number(kcoeff[0], True))
        elif vcnt == 2:
            kterm = "%s*exp(%s/T)" % (format_number(kcoeff[0], True), format_number(kcoeff[2], True))
        elif vcnt == 5:
            kterm = "ktroe(%s, %s, %s, %s, %s)" % (format_number(kcoeff[0], True), \
                                                   format_number(kcoeff[1], True), \
                                                   format_number(kcoeff[3], True), \
                                                   format_number(kcoeff[4], True), \
                                                   format_number(kcoeff[6], True)
                                                  )
        elif vcnt == 0:
            if "hv" in reactants or rxntype.lower() == "photolysis":
                kterm = "j" + reactants[0]
                # workaround for missing hv in Alex's table
                if not "hv" in reactants:
                    reactants.append("hv")
            else:
                kterm = "k" + "_".join([r for r in reactants if not r == "M"])
        return kterm

                
    @staticmethod
    def extract_mozpp_jlabel(label):
        """Obtain a jlabel expression from a mozpp photoreaction label.
        Valid formats:
        jxyz : simple j label, use as is
        jxyz=userdefined,[userdefined] : add tag "juser1" or "juser2"
        jxyz->,[factor*]jzzz : alias, return part after ','."""
        tag = ""
        tokens = label.split("->", 1)
        if len(tokens) == 2:
            # remove leading ',' -- assumes there always is a ','
            res = tokens[1].split(",")[1].strip()
        elif "=userdefined" in label.lower():
            # check for second userdefined
            if label.lower().count("userdefined") == 2:
                tag = "juser2"
            else:
                tag = "juser1"
            idx = label.find("=")
            res = label[:idx]
        else:
            res = label.strip()
        # convert compound name to upper
        res = res.upper().replace("J", "j")
        return res, tag
            
        
    @staticmethod
    def mch_special(kterm, variablename="", filterdict=mch_filter):
        """Analyses RACM2 (mch) special rate coefficients and returns them as a list
        of variables that can be added to the mechanism. Will be called from the
        mechanism class after a reaction has been instantiated.
        Special kterms can extend across several lines and include the definition of
        temporary variables. The final k-term always starts with 'RWK(#) = '. This
        will be given the variable name passed as argument (normally 'kA_B')."""
        # split kterm lines
        lines = kterm.split(";")
        res = OrderedDict()
        for i in range(len(lines)-1):
            left, right = lines[i].split("=")
            # extract variable name
            left = left.replace("SPECIAL", "").strip()
            if left == "RWK(#)":
                left = variablename
            # run regex filter on right-hand side expression
            for k, v in filterdict.items():
                right = re.sub(k, v, right)
            res[left] = right.strip()
        return res


    @staticmethod
    def parse_reaction(rstring, separator="->"):
        """Parse a reaction string and return reactants and products"""
        left, right = rstring.split(separator)
        reactants = [s.strip() for s in left.split("+")]
        products = right.strip()
        return reactants, products


    @staticmethod
    def translate_kterm_from_mozpp(kterm):
        """Translate two-parameter expression into Arrhenius formula and five-parameter
        expression to 'ktroe(...)'."""
        res = kterm
        tokens = kterm.split(",")
        for i, t in enumerate(tokens):
            try:
                tokens[i] = format_number(float(t.strip()), True)
            except ValueError:
                pass      # don't convert if not a number
        if len(tokens) == 1:
            res = tokens[0]
        elif len(tokens) == 2:
            # Attention: mozpp has negative Ea: do not change sign!
            res = "%s*exp(%s/T)" % tuple(tokens)
        elif len(tokens) == 5:
            res = "ktroe(%s,%s,%s,%s,%s)" % tuple(tokens)
        else:
            raise ValueError("Invalid kterm expression! %s" % (kterm))
        return res
    

    def build_kcoeff_from_kterm(self):
        """Extracts numbers from a kterm expression and builds a 7-element list from it."""
        kl = self.kterm.extract_coefficients()
        res = ["NA" for i in range(7)]
        if self._isphoto:
            return res
        if len(kl) == 1: # constant value
            res[0] = kl[0]
        elif len(kl) == 2: # Arrhenius
            res[0] = kl[0]
            res[2] = kl[1]
        elif len(kl) == 5: # Troe
            res[0] = kl[0]
            res[1] = kl[1]
            res[3] = kl[2]
            res[4] = kl[3]
            res[6] = kl[4]
        return res

        
    def build_label(self):
        """Constructs a reaction label based on the reactants.
        Does include leading 'j' for photolysis reactions, but no decorative characters ([], <>, etc.)."""
        if self._isphoto:
            res = "j" + self.reactants[0]
        else:
            res = "_".join([v for v in self.reactants if v != "M" and v != "hv"])
        return res


