# -*- coding: utf-8 -*-
"""
Mechanism

Python class to convert and analyze a chemical reaction mechanism for a global or regional
chemistry transport model or box model. Much of the functionality of this class stems from
the Reaction and Compound (or speciesTable) classes. This class adds the management of the
mechanism as a whole.

Instantiation:
- m = Mechanism(name, model, revision, reactions, variables, functions, comments)
      Initiate a chemistry mechanism object. Name is the name of the mechanism, model defines
      the species namespace for property lookup and translation, revision should be a string
      in the form 'YYYYMMDDxyz', where 'xyz' are author initials, reactions is a list of
      Reaction objects (see reaction.py), variables is a dictionary (preferably OrderedDict)
      with variable names as keys and values (any mathematical expression as string) as values,
      functions is a similar dictionary for function definitions (arguments are part of the
      function name), and comments is a dictionary with section names as keys ('header',
      'reactions', 'variables', 'functions', 'end') and lists of strings (or docstrings?) as
      values. Normally, you will instantiate a Mechanism object through one of the from_...
      methods described below.
- m = Mechanism.from_csv(fileid, separator, start, stop, name, model, revision)
      Create a mechanism object by reading the content of file fileid. Fileid can be a filename
      or the handler of an already opened spreadsheet (csv) file. The default separator is
      '\t' (tabstop). Start and stop can either be line numbers or string tokens between
      which the lines are parsed for reaction information. The first line to be parsed must be
      a header line. For details on the format of the csv file, see method description below.
      Name, model, and revision are described above.
- m = Mechanism.from_kpp(fileid, start, stop, name, model, revision)
      Create a mechanism object by reading the content of a KPP equation file. Fileid can be
      a filename or the handler of an already opened file. Start and stop can either be line
      numbers or string tokens between which the lines are parsed for reaction information. The
      default is to parse from the '#EQUATIONS' label to the end of the file. For details on the
      format of a KPP file, see method description from_kpp() in reaction.py.
      Name, model, and revision are described above.
- m = Mechanism.from_mch(fileid, name, model, revision)
      Create a mechanism object by reading the content of a RACM file ('mch' format). Fileid can be
      a filename or the handler of an already opened file. For details on the format of a mch file,
      see method description below. Name, model, and revision are described above. The default model
      name is 'RACM2'.
- m = Mechanism.from_mech(fileid, name, model, revision)
      Create a mechanism object by reading the content of a 'mech' file. This format is a hybrid of
      the KPP and MOZPP format designed with readability and completeness of documentation in mind.
      The author of this tool suite advises the creation of mech files as a starting point for
      mechanism conversion as this will preserve the most features of each format. For details on the
      format of a mech file, see method description below. 
      Fileid can be a filename or the handler of an already opened file. Name, model, and revision
      are described above.
- m = Mechanism.from_mozpp(fileid, name, model, revision)
      Create a mechanism object by reading the content of a MOZPP input file. For details on the
      format of a mozpp file, see method description below. 
      Fileid can be a filename or the handler of an already opened file. Name, model, and revision
      are described above.

Attributes:
- name: The name of the mechanism. If the object is instantiated via one of the from_... methods,
      the name will default to the basename of the file that has been read.
- model: The name of the model for which the mechanism has been built. This defines the namespace for
      reactants and products, which are needed to obtain species properties from the speciestable
      (see speciestable.py). The model name must be associated with a 'model:name' column in the
      species table.
- revision: The default revision tag to be applied to all reactions of this mechanism. Each reaction
      carries its own revision tag, which will not be overwritten. (the handling of revision information
      would deserve a more thorough treatment, for example by linking it to databases or revision
      control systems).
- reactions: List of reaction objects that belong to this mechanism. See reaction.py for details.
- variables: Dictionary of variables. See Instantiation above.
- functions: Dictionary of functions. See Instantiation above.
- comments: Dictionary of comments. See Instantiation above.
- _translate: A dictionary for species translation from one model (namespace) to another. Species names
      that are not defined in the target namespace will remain unchanged.
- _translate_model: The name of the model (namespace) to which the mechanism shall be translated.
- _speciestable: a reference to a speciestable object which contains all compound information
      (see speciestable.py).

Interface Methods:
- build_label(preserve_labels, add_underscore, translate)
      Construct a list of suitable reaction labels (without decoration such as '[...]' or
      '<...>'). For each reaction the build_label method from the Reaction class is called.
      This will generate a label such as 'A' for a unimolecular reaction involving A as
      reactant, and 'A_B' for a bimolecular reaction. 'M' and 'hv' are ignored.
      After building the initial list, it is tested for duplicates. If duplicates are found they
      will be appended with '_a', '_b' etc.. Add_underscore will add an underscore character
      between the label and the enumerator character (this is the default).
      If translate is True (default), species names in the label will be translated according to the
      self._translate dictionary. Preserve_labels (default is False) will use existing reaction
      labels that are stored in the Reaction objects.
- check_mass_balance()
      Tests the conservation of elements (thus mass) from the reactant to the product side (see
      check_mass method of the Reaction class). Multiples of O2 will be ignored. Note that this
      method may still flag reactions as unbalanced if multiple channels exist and not all of them
      add or remove the same amount of O2 molecules (e.g. A+B -> 0.3*X + 0.7*(Y+O2)).
      The method will print each reaction that does not conserve mass and list the elemental
      composition of reactants and products as well as the imbalance. The check_mass method of the
      Reaction class relies on the information given in the speciestable and cannot handle non-integer
      mass (this occurs in some VOC lumping approaches).
- clear_labels()
      Remove all existing reaction labels from the reactions of this mechanism.
- extend_variables()
      Add new variables (e.g. those found in a reaction expression) to the variable dictionary
      of the mechanism. A warning is printed if the variable already exists, and the new variable
      will then be marked with '***'.
      Note: this method is still somewhat preliminary and could be optimized. At present, all
      function expressions (e.g. 'ktroe(...)') will also be listed as variables if they are
      encountered for example in a KPP input file. If you read in a mechanism from a properly
      formatted mech file, such errors should not occur.
- extract_variables()
      Extracts lists of variables and functions in the kterm expressions of all reactions and
      stores them as self._variables and self._functions, respectively. This method is used to
      generate an initial variables and functions block when writing a mechanism as mech file.
- find_reactions(reactants)
      Returns a list of all Reaction objects which contain the given reactants. Reactants must
      be given as a list of strings. Example: m.find_reactions(["N2O5","hv"]) will return photolysis
      reactions of N2O5.
- reset_translation()
      Resets the translation table for species names. Further output of the mechanism (write_...
      methods) will no longer translate species names afterwards.
- shorten_species_names(nchar)
      Shorten all species names to a maximum of nchar characters. The default is 8 characters.
      Initially, longer names will simply be truncated at nchar characters. If the new name already
      exists it will be replaced by XXNNNN, where NNN is a 4-digit number. Therefore, nchar should
      not be less than 6 characters.
- statistics()
      Report some statistics about this mechanism (number of species, reactions and photolysis
      reactions.
- translate_label(label)
      Renames species in a reaction label according to the self._translate dictionary. The label
      must be of the form 'A_B' (or 'A', 'A_B_C').
- translate_to_model(model)
      Set up translation directory for species names. Every name that is defined for the target
      model and has a different name will be entered into the translation dictionary so that the
      new name will be used when the mechanism is written. The translation dictionary is reset
      prior to this operation. Note that this method does not alter any species names, labels, etc.
      It is therefore always possible to revert to the original species names by simply resetting
      the translation table (reset_translation method).
- write_csv(fileid, separator, preserve_labels)
      Output mechanism as csv file with individual reactants and products in individual columns
      (see format description in reaction.py). Fileid can be a filename or the file handler of a
      file opened for writing. If no fileid is supplied, a filename will be constructed based on
      the mechanism name and revision tag.
      The default separator is '\t' (tabstop). Use the preserve_labels flag to preserve existing
      reaction labels where possible.
- write_kpp_species(filename, species, orispecies)
      Write a species definition file (.spc) in KPP format. This file will contain all species
      present in the mechanism together with their molecular composition, a Latex label and a
      long name. The long name is the 'best possible' name of the compound (see compound.py).
      Species and orispecies are lists of species names in their translated and original form,
      respectively. 
- write_kpp_variables(filename)
      Write a pseudo-FORTRAN90 file contain variable declarations and settings for use with
      the CAABA/MECCA boxmodel which is based on KPP. This file will require some editing and
      needs to be merged with the eqn file (see write_kpp_mecca below). This is just a helper
      method which facilitates building a CAABA/MECCA mechanism.
- write_kpp_mecca(fileid, preserve_labels)
      Generate a KPP equations file in the CAABA/MECCA format, i.e. with annotations and reaction
      labels. This file will contain only the '#EQUATIONS' section and must be manually edited
      in order to be compiled in CAABA/MECCA. This method also calls write_kpp_species and
      write_kpp_variables.
- write_kpp_ukca(filebasename, preserve_labels)
      Generate three plain KPP equations files for bimolecular, termolecular and photolysis
      reactions, respectively. This is required by the UKCA model.
(Note: there is currently no write_mch routine)
- write_mech(fileid)
      Write the mechanism in the mech format including sections for variables and functions.
      Comments will be written in the respective sections. However, the exact placement of
      comments is not preserved and all comments of a block will appear at the beginning of that
      block (this is on the ToDo list...). Fileid can be a filename or the object of a previously
      opened file. If None, a filename will be constructed based on the mechanism name and
      revision tag.
- write_mozpp(fileid, preamble, footer, fixed, explicit, preserve_labels)
      Write the mechanism in the MOZART preprocessor (MOZPP) format including the species and
      reactions sections. Optionally a preamble (list of strings) can be prepended, and a footer
      can be appended at the end. The fixed keyword may contain a list of species which are then
      marked as fixed, and the explicit keyword may contain a list of species which shall be solved
      explicitly.
Internal methods (generally not called directly by user):
- convert_kcoeff_to_kterm(kcoeff, reactants, rxntype)
- _get_parse_flags()
- insert_continuation_line()
- _make_csv_header()
- _start_stop_params()


"""

from collections import OrderedDict
import re
import os.path
import datetime as dt
import numpy as np
import ac.utils.moleweight as mw
from reaction import Reaction, kpp_dict
from speciestable import speciesTable


__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-10-09'
__license__ = 'MIT'


# ---- Mechanism class ----

class Mechanism(object):
    """defines a chemical gas-phase reaction mechanism for a global or regional
    chemistry transport or chemistry climate model.
    """

    def __init__(self, name="", model="", revision="", reactions=None, variables=None,
                 functions=None, comments=None):
        """arguments:
        name: name of the mechanism
        model: name of model (for species names in speciestable)
        revision: revision tag of the mechanism (YYYYMMDDxyz, where xyz are author initials).
        reactions: list of reaction objects
        variables: list of rateCoefficient objects
        functions: list of ???
        comments: dictionary of string lists with section names as keys
        """
        self.name = name           # a name of the mechanism
        self.model = model
        self._revision = revision   # a revision tag (format YYYYMMDDxyz)
        if reactions is None:
            self._reactions = []  # list of Reaction objects
        else:
            self._reactions = reactions
        if variables is None:
            self._variables = OrderedDict()   # dictionary of variables with their expressions
        else:
            self._variables = variables
        if functions is None:
            self._functions = OrderedDict()   # dictionary of functions with their arguments and expressions
        else:
            self._functions = functions
        if comments is None:
            self._comments = {}    # dictionary with string lists and 'section' keys
        else:
            self._comments = comments
        self._translate = OrderedDict() # translation dictionary for species names
        self._translate_model = ""      # model namespace for translation table values
        try:
            self._speciestable = speciesTable.from_csv()
        except IOError as e:
            raise IOError("Could not open species table. Reason: %s (%i)"%(e.args[1], e.args[0]))
        # report statistics
        self.statistics()


    @classmethod
    def _file_open(cls, fileid, mode="r"):
        """Opens a file for reading or writing and handles IOErrors.
        Fileid can be a filename or the handle of a previously opened file."""
        if fileid is None:
            raise ValueError("Must supply fileid argument (filename or file handler)!")
        if isinstance(fileid, basestring):
            try:
                f = open(fileid, mode)
            except IOError as e:
                raise IOError("Cannot open file %s. Reason: %s (errno %i)"%  \
                              (fileid, e.args[1], e.args[0]))
        else:
            f = fileid
        return f


    @classmethod
    def _get_parse_flags(cls, line, lineno, parseCond):
        """Determine whether the line needs to be parsed as a reaction or not.
        Returns parse, first, parseFromNext as boolean flags.
        Note: lineno must be passed to this routine as lineno+1 in order to
        interpret istart and istop as beginning from 1."""
        parseCond["first"] = parseCond["parseFromNext"]
        parseCond["parse"] = parseCond["parse"] or parseCond["parseFromNext"]
        parseCond["parseFromNext"] = line.startswith(parseCond["tstart"])
        if lineno == parseCond["istart"]:
            parseCond["parse"] = True
            parseCond["first"] = True
        if lineno >= parseCond["istop"] or line.startswith(parseCond["tstop"]):
            parseCond["parse"] = False
        

    @classmethod
    def _start_stop_params(cls, start, stop):
        """Sets istart, istop integer values (line numbers) and tstart, tstop
        strings depending on input"""
        if start is None:
            start = 1
        istart = 9999999 if isinstance(start, basestring) else start
        tstart = start if isinstance(start, basestring) else "MAGIC-**-CIGAM"
        istop = 9999999 if isinstance(stop, basestring) or stop is None else stop
        tstop = stop if isinstance(stop, basestring) else "MAGIC-**-CIGAM"
        res = {"istart":istart, "istop":istop, "tstart":tstart, "tstop":tstop,
               "parse":False, "parseFromNext":False, "first":False}  # set default
        return res

        
    @classmethod
    def from_csv(cls, fileid=None, separator="\t", start=None, stop=None,
                 name=None, model="", revision=""):
        """creates a Mechanism instance and reads a reaction spreadsheet (Alex).
        Fileid can be a filename or the handler of a previously opened file.
        Separator is the separator character used in the csv file (normally tab '\t',
        or semicolon ';').
        Start and stop can be used to extract only a portion of the csv file, for example
        if it contains additional comment lines. If start (stop) is a string, then the
        parsing will begin (end) with the line following (before) a line that starts with
        this string. If start (stop) is an integer value, then parsing will begin (end)
        at the respective line no (counting from 1!). Note that the header line must be
        the first line to be parsed.
        Name identifies the mechanism (default: file basename) and revision is an
        (optional) revision tag which can be used to update the revision information for
        individual reactions.
        
        The format of a csv reaction file is:
            code; reac.1; ...; reac.N; prod.1; ...; prod.M; ai.fac; bi.fac; ei.fac; \
            a0.fac; b0.fac; e0.fac; ffac; mech; rxn.type; comment
        The header must contain these column names. Any extra columns will be ignored.
        The number of reactants and products is flexible. 
        Missing entries are coded as NA.
        Prod.x contains 'yield*' if yield != 1.
        """
        # initialize attributes
        reactions = []   # list of Reaction objects
        # csv doesn't support variables, functions, and (general) comments
        # try to open file
        f = cls._file_open(fileid)
        print "Reading mechanism from file %s" % (f.name)
        # read lines and obtain reactions between start and stop
        parseCond = cls._start_stop_params(start, stop)
        for lineno, line in enumerate(f):
            cls._get_parse_flags(line, lineno+1, parseCond)
            if parseCond["parse"]:
                if parseCond["first"]:
                    # first line is header    
                    header = line.split(separator)
                else:
                    r = Reaction.from_csv(line, lineno+1, header=header, separator=separator)
                    reactions.append(r)
        if name is None:
            name = os.path.splitext(os.path.basename(f.name))[0]
        return cls(name, model, revision, reactions)
        
        

    @classmethod
    def from_kpp(cls, fileid, start="#EQUATIONS", stop=None,
                 name=None, model="", revision=""):
        """creates a Mechanism instance and reads the EQUATIONS section of a KPP file.
        Fileid can be a filename or the handler of a previously opened file.
        Start and stop can be used to extract only a portion of the csv file, for example
        if it contains additional comment lines. If start (stop) is a string, then the
        parsing will begin (end) with the line following (before) a line that starts with
        this string. If start (stop) is an integer value, then parsing will begin (end)
        at the respective line no (counting from 1!). Default is to read from the
        '#EQUATIONS' tag to the end of the file.
        Name identifies the mechanism (default: file basename) and revision is an
        (optional) revision tag which can be used to update the revision information for
        individual reactions.
        Format is: <label> reaction string : kterm ;
        reaction string is:  A [+ B | hv][+ C] = product expression
        Product yields are specified as factors without a '*' sign.
        Kterm can be any valid mathematical expression.
        This method partly supports the extended KPP/MECCA format, where a couple of optional
        comments are inserted with special meaning:
        <label> reaction string : {tags} kterm{MCF} ; {reference}
        Tags will be read out, the Monte Carlo factors (MCF) will be ignored, and the
        reference will be extracted as comment.
        Note that the input from KPP files will be filtered with various regular expressions.
        """
        # initialize attributes
        reactions = []   # list of Reaction objects
        variables = OrderedDict()
        # kpp does support variables, functions, and (general) comments, but these
        # are too unspecific to be parsed efficiently. We only extract variable names.
        # try to open file
        f = cls._file_open(fileid)
        print "Reading mechanism from file %s" % (f.name)
        # read lines and obtain reactions between start and stop
        parseCond = cls._start_stop_params(start, stop)
        for lineno, line in enumerate(f):
            cls._get_parse_flags(line, lineno+1, parseCond)
            if parseCond["parse"]:
                # ignore comment lines
                line = line.strip()
                if not line or line.startswith("//") or line.startswith("{"):
                    continue
                else:
                    r = Reaction.from_kpp(line, lineno+1)
                    reactions.append(r)
                    # test for variable name in kterm (also tests rate expression for syntax errors)
                    try:
                        newvars = r.kterm.get_variables()
                    except ValueError as e:
                        raise ValueError("%s (line %i)" % (e.args[0], lineno))
                    Mechanism.extend_variables(variables, newvars)
        if name is None:
            name = os.path.splitext(os.path.basename(f.name))[0]
        return cls(name, model, revision, reactions, variables=variables)


    @classmethod
    def from_mch(cls, fileid, name=None, model="RACM2", revision=""):
        """creates a Mechanism instance and reads the content of a RACM file (mch format).
        Fileid can be a filename or the handler of a previously opened file.
        Name identifies the mechanism (default: file basename) and revision is an
        (optional) revision tag which can be used to update the revision information for
        individual reactions.
        The format is a multi-line format (see reaction.py:from_mch method).
        Before using a line to instantiate a Reaction class we seek to collect all information
        pertaining to one reaction including comment lines which usually follow the reaction
        definition."""
        # initialize attributes
        reactions = []   # list of Reaction objects
        comments = {}
        comments["header"] = []
        variables = OrderedDict()
        # try to open file
        f = cls._file_open(fileid)
        print "Reading mechanism from file %s" % (f.name)
        rline = ""             # last reaction being processed
        rkterm = ""            # last kterm
        rcomments = ""         # last comments
        rlineno = 0            # line number where a reaction begins
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            # ignore !End of mechanism and END tags
            if line.startswith("! END") or line.startswith("END"):
                continue
            # collect comments until we reach the first reaction (line not starting with "!")
            # otherwise, the comments will be appended to the current reaction string
            if line.startswith("!"):
                if not rline:
                    comments["header"].append(line[1:])  # remove leading "!"
                else:
                    rcomments += line[1:]+"&n"   # fake newline character
                continue
            # if we get here we need to process reaction information
            # 3-digit numerical label: start of new reaction
            # parse current reaction and begin new rline
            if line[0:3].isdigit():
                if rline:
                    r = Reaction.from_mch(rline, rlineno, rkterm, rcomments)
                    if rkterm.startswith("SPECIAL"):
                        variablename = str(r.kterm)
                        newvars = r.mch_special(rkterm, variablename)
                        Mechanism.extend_variables(variables, newvars)
##                        for k,v in newvars.items():
##                            variables[k] = v
                    reactions.append(r)
                rlineno = lineno
                rline = line[3:].strip()
                rkterm = ""
                rcomments = ""
            elif line.startswith("&"):   # continuation line (additional products)
                rline += " " + line[1:].strip()
            # everything else must be part of kterm expression
            else:
                rkterm += line + ";"  # insert separator
        # process last reaction
        if rline:
            if rkterm.startswith("SPECIAL"):
                rkterm = "special"
            r = Reaction.from_mch(rline, rlineno, rkterm, rcomments)
            if rkterm.startswith("SPECIAL"):
                variablename = str(r.kterm)
                newvars = r.mch_special(rkterm, variablename)
                Mechanism.extend_variables(variables, newvars)
##              for k,v in newvars.items():
##                  variables[k] = v
            reactions.append(r)
        # set mechanism name
        if name is None:
            name = os.path.splitext(os.path.basename(f.name))[0]
        # instantiate object
        tmp = cls(name, model, revision, reactions, variables=variables, comments=comments)
        # fix duplicate kterms (labels) in photolysis reactions
        labels = tmp.build_labels()
        for i, r in enumerate(tmp.reactions):
            if r._isphoto:
                r.kterm = labels[i]
        return tmp


    @classmethod
    def from_mech(cls, fileid, name=None, model="", revision=""):
        """creates a Mechanism instance and reads the mechanism from a mech file.
        Fileid can be a filename or the handler of a previously opened file.
        Name identifies the mechanism (default: file basename) and revision is an
        (optional) revision tag which can be used to update the revision information for
        individual reactions.
        Format of reactions is: reaction string : kterm ; tags ! <revision> comments
        reaction string is:  A [+ B | hv][+ C] -> product expression
        product expression can be any valid algebraic expression with
            species names, multipliers, sums, products, and parantheses
        kterm can be a mathematical expression (including simple numbers or variables)
        tags are a comma-separated list of 'reaction labels'
        revision is a string of form YYYYMMDDxyz, where xyz is the authors initials
        comments is an arbitrarily formatted string.
        The file should have the three sections "REACTIONS", "VARIABLES", and "FUNCTIONS".
        Within the REACTIONS block, individual subsections can be marked with "SECTION name"
        inside a comment string.
        Comments (lines starting with "!" or "#") may be inserted at will.
        """
        # initialize attributes
        reactions = []   # list of Reaction objects
        variables = OrderedDict()
        functions = OrderedDict()
        comments = {}
        sections = ["header", "reactions", "variables", "functions", "end"]
        for s in sections:
            comments[s] = []
        isec = 0
        rsec = "" # sub-section name within REACTIONS block
        # try to open file
        f = cls._file_open(fileid)
        print "Reading mechanism from file %s" % (f.name)
        # read and interpret lines
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            # check if we enter a new section
            words = line.split()
            if words[0].lower() in sections:
                isec = sections.index(words[0].lower())
                continue
            # store model name
            if line.upper().startswith("MODEL"):
                if not model:   # don't overwrite method argument
                    model = line[6:].strip()
            # store sub section
            if "SECTION" in line.upper():
                idx = line.upper().find("SECTION")
                if idx == 0 or line[idx-1] in " !#.,;:/\\$%\t":   # avoid "cross-section" etc.
                    rsec = line[idx+7:].strip()
                continue
            # check for comment lines (don't need comment character in header or footer section)
            if line.startswith("!") or line.startswith("#") or isec==0 or isec==4:
                # add comment to current section unless it's a separator line
                if not ("------" in line or "======" in line):
                    comments[sections[isec]].append(line)
                continue
            # everything else must be valid reaction, variable or function
            if isec == 1:
                r = Reaction.from_mech(line, lineno+1, section=rsec)
                reactions.append(r)
            elif isec == 2:
                if "=" in line:
                    left, right = line.split("=", 1)
                else:
                    left = line
                    right = ""
                variables[left.strip()] = right.strip()
            elif isec == 3:
                if "=" in line:
                    left, right = line.split("=", 1)
                else:
                    left = line
                    right = ""
                # **** ToDo: remove function arguments... ****
                functions[left.strip()] = right.strip()
        if name is None:
            name = os.path.splitext(os.path.basename(f.name))[0]
        return cls(name, model, revision, reactions, variables, functions, comments)


    @classmethod
    def insert_continuation_line(cls, rline, line):
        """inserts a MOZPP continuation line into the current reaction line."""
        # test if rline has kterm (";" before possible comment character)
        kterm = ""
        isc = rline.find(";")
        ic1 = rline.find("!")
        ic2 = rline.find("#")
        if ic1 > 0 and ic2 > 0:
            icc = min(ic1, ic2)
        elif ic1 > 0:
            icc = ic1
        else:
            icc = ic2  # may still be < 0
        if isc > 0 and (icc < 0 or isc < icc):
            # split rline
            rline, kterm = rline.split(";", 1)
            rline = rline.strip()
        # append continuation line
        rline += line
        if kterm:
            rline += ";" + kterm
        return rline
            

    @classmethod
    def from_mozpp(cls, fileid, name=None, model="MOZ_MIM2", revision=""):
        """creates a Mechanism instance and reads the Photolysis and Reactions sections
        of a MOZPP input file.
        Fileid can be a filename or the handler of a previously opened file.
        Name identifies the mechanism (default: file basename) and revision is an
        (optional) revision tag which can be used to update the revision information for
        individual reactions.
        Format is: [label] reaction string ; kterm [!|# comments]
        reaction string is:  A [+ B | hv][+ C] -> product expression
        If product expression contains yields != 1, they will have factors with '*' sign.
        kterm typically consists of one or two numbers for an Arrhenius expression, or of
        six values for a Troe expression. If blank it is treated as a 'usrrxt'. In this case
        a variable 'k_R1_R2' will be generated.
        Note: mozpp can have continuation lines which must start with '+' and contain only
        additional products. The rate term must be on the first line. """
        # initialize attributes
        reactions = []   # list of Reaction objects
        comments = {}
        comments["header"] = []
        # try to open file
        f = cls._file_open(fileid)
        print "Reading mechanism from file %s" % (f.name)
        # read lines and obtain reactions between start and stop
        parseComments = False  # True if "Comments" tag is found, but also allow "*"
        parse = False          # True for photolysis and Reactions sections
        rline = ""             # last reaction being processed
        rsec = ""              # sub-section name within REACTIONS block
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith("comments"):
                parseComments = True
                continue
            elif line.lower().startswith("end comments"):
                parseComments = False
                continue

            if line.lower().startswith("photolysis"):
                parse = True
                continue
            elif line.lower().startswith("end photolysis"):
                parse = False

            if line.lower().startswith("reactions"):
                parse = True
            elif line.lower().startswith("end reactions"):
                parse = False
                if rline:
                    r = Reaction.from_mozpp(rline, lineno, section=rsec)
                    reactions.append(r)
            elif parseComments or (line.startswith("*") and lineno < 40):
                comments["header"].append(line)
            elif line.startswith("*") and "SECTION" in line.upper():
                # create reaction from rline and start new rline
                if rline:
                    r = Reaction.from_mozpp(rline, lineno, section=rsec)
                    reactions.append(r)
                rline = ""
                # store section name
                idx = line.upper().find("SECTION")
                rsec = line[idx+7:]
            elif parse and line.startswith("+"):  # continuation line
                if not rline:
                    raise ValueError("Invalid input line: %s (line no %i)"%(line, lineno))
                rline = cls.insert_continuation_line(rline, line)
            elif parse and not (line.startswith("!") or line.startswith("*")):
                # create reaction from rline and start new rline
                if rline:
                    r = Reaction.from_mozpp(rline, lineno, section=rsec)
                    reactions.append(r)
                rline = line
        if name is None:
            name = os.path.splitext(os.path.basename(f.name))[0]
        return cls(name, model, revision, reactions, comments=comments)


    def __str__(self):
        """pretty print mechanism object"""
        res = self.name
        return res
    

    @property
    def name(self):
        """return name of mechanism"""
        return self._name


    @name.setter
    def name(self, name=None):
        """set name of reaction mechanism."""
        self._name = name


    @property
    def model(self):
        """return model name"""
        return self._model


    @model.setter
    def model(self, name=None):
        """set model name for species lookup."""
        self._model = name


    @property
    def revision(self):
        # Note: error checking is done on the reaction level
        return self._revision


    @revision.setter
    def revision(self, revision=""):
        self._revision = revision


    @property
    def reactions(self):
        return self._reactions

    
    @property
    def variables(self):
        return self._variables.keys()

    
    @property
    def functions(self):
        return self._functions.keys()
    
    
    @property
    def comments(self):
        return self._comments

    
    # ----- Utility methods -----
    def translate_label(self, label):
        """Renames species in a reaction label according to the self._translate
        dictionary"""
        tokens = label.split("_")
        for i in range(len(tokens)):
            for k, v in self._translate.items():
                if tokens[i] == k:
                    tokens[i] = v
        label = "_".join(tokens)
        return label
    
        
    def build_labels(self, preserve_labels=False, add_underscore=True, translate=True):
        """Construct a list of suitable reaction labels (without decoration).
        General format is 'A_B' for a two-body reaction. Details can be found in
        the build_label method of the Reaction class.
        Preserve_labels=True will use existing reaction labels.
        Add_underscore will add an underscore character between label and duplicate
        character. Translate will translate species names in the label if the
        self._translate dictionary is not empty."""
        # Characters to add for duplicates
        dchar = "abcdefghijklmnopqrstuvwxyz"
        sep = "_" if add_underscore else ""
        # Generate list of 'primary' labels (this may contain duplicates)
        labels = []
        for r in self.reactions:
            if r.label and preserve_labels:
                rlabel = r.label
            else:
                rlabel = r.build_label()
            # Translate species names
            if translate and self._translate:
                rlabel = self.translate_label(rlabel)
            labels.append(rlabel)    
        # Test for duplicates and append lowercase letters to distinguish these
        for i, v in enumerate(labels):
            if labels.count(v) > 1:
                # get indices of duplicates (offset by i)
                idxlist = [j for j, x in enumerate(labels[i:]) if x == labels[i]]
                for k, idx in enumerate(idxlist):
                    labels[i+idx] += sep+dchar[k]
        return labels
                

    def check_mass_balance(self):
        """Test mass balance of all reactions in the mechanism.
        This requires that the model and speciestable attributes are set."""
        if not self.model:
            raise ValueError("Model attribute must be set for mass balance check!")
        if not isinstance(self._speciestable, speciesTable):
            raise ValueError("Species table must be loaded for mass balance check!")
        for r in self.reactions:
            r.check_mass(model=self.model, speciestable=self._speciestable)

        
    def clear_labels(self):
        """Clear the label tag for all reactions.
        This may be necessary/advisable before writing a mechanism to a different file format."""
        for r in self.reactions:
            r.label = ""

            
    @staticmethod
    def extend_variables(variables, newvars):
        """Append new variables to existing variable dictionary. Warn about duplicates
        and rename duplicates."""
        for k, v in newvars.items():
            if k in variables:
                print "**** Duplicate variable: %s" % (k)
                k = "***%s***" % (k)
##                k = "XX_"+k
            variables[k] = v


    def extract_variables(self):
        """Extracts lists of (undefined) variables and functions in the kterm expressions
        of all reactions and stores them as self._variables and self._functions, respectively.
        Note: it is not possible to obtain the variable expressions or function terms from the
        reaction set. Hence the respective dictionary entries will remain empty."""
        variables = self._variables
        functions = self._functions
        for r in self.reactions:
            try:
                vr = r.kterm.extract_variables(undefined=True)
            except ValueError:
                print "**** Error in kterm for reaction %s" % (r.to_mech())
                vr = []
            for v in vr:
                # variable or function?
                idx = v.find("(")
                if idx > 0:  # function
                    if not v[:idx] in functions:
                        functions[v[:idx]] = ""
                else:  # variable
                    if not v in variables:
                        variables[v] = ""
        self._variables = variables
        self._functions = functions
        

    def find_reactions(self, reactants=None):
        """Returns a list of all Reaction objects which contain the given reactants."""
        res = []
        if reactants is None:
            return res
        for r in self.reactions:
            include = True
            for reac in reactants:
                if not reac in r.reactants:
                    include = False
                    break
            if include:
                res.append(r)
        return res
                

    def get_species(self, translate=True, ignore_dummy=False):
        """Return a sorted list of all species names occuring in the mechanism.
        If the translate keyword is set, the species names will be translated accordingly.
        Use ignore_dummy to omit dummy species such as M, hv, and e."""
        spset = set()
        for r in self.reactions:
            spset = spset.union(r.reactants)
            spset = spset.union(r.get_product_names())
        spset = spset.difference({""})
        species = sorted(list(spset))
        if translate and len(self._translate) > 0:
            for k, v in self._translate.items():
                if k in species:
                    idx = species.index(k)
                    species[idx] = v
        if ignore_dummy:
            if "M" in species:
                del species[species.index("M")]
            if "hv" in species:
                del species[species.index("hv")]
            if "e" in species:
                del species[species.index("e")]
        return species

        
    def reset_translation(self):
        """Remove all entries in the translation dictionary for species names."""
        self._translate = OrderedDict()
        self._translate_model = ""

        
    def shorten_species_names(self, nchar=8):
        """Attempt to shorten the names of the species that are defined in the mechanism
        to a maximum of nchar characters. The routine will first try to cut the length of
        the species. If it then duplicates another species, it will instead define a
        systematic name as 'XXNNNN' where NNNN is a 4-digit number starting with 0001."""
        if nchar < 6:
            raise ValueError("Nchar argument must be at least 6!")
        # obtain list of current species names
        species = self.get_species(translate=False)
        # set up a translation dictionary
        spdict = OrderedDict()
        num = 1
        for s in species:
            if len(s) > nchar:
                test = s[:nchar]
                if test in species:
                    test = "XX%04i" % (num)
                    num += 1
                spdict[s] = test
        # save replacement dictionary
        # Cannot apply it now, because we might need species information from speciestable
        self._translate = spdict
        self._translate_model = self.model  # the closest we can get...


    def statistics(self):
        """Prints a number of statistical quantities about the mechanism."""
        # number of species
        species = self.get_species(translate=False, ignore_dummy=True)
        spcnt = len(species)
        # number of reactions
        rcnt = len(self.reactions)
        # number of photolysis reactions
        photocnt = 0
        for r in self.reactions:
            if r._isphoto:
                photocnt += 1
        # report statistics
        name = self.name if self.name else "This mechanism"
        print "%s has %i species and %i reactions, including %i photolysis reactions." % (name, spcnt, rcnt, photocnt)

        
    def translate_to_model(self, model=None):
        """Set up translation directory for species names. Every name that is defined
        for the target model and has a different name will be entered into the translation
        dictionary so that the new name will be used when the mechanism is written.
        The translation dictionary is reset prior to this operation."""
        from_model = self.model
        if model is None or not model:
            raise ValueError("Must supply name of target model!")
        # load species table and find out  if model name is valid
        t = self._speciestable
        if not model in t.get_model_names():
            raise ValueError("Invalid model name: %s!"%(model))
        # establish list of all species names in current mechanism
        species = self.get_species(translate=False)
        # set up translation dictionary
        spdict = OrderedDict()
        for s in species:
            # find name for model
            test = t.find_model_species(s, from_model)
            if test is not None:
                newname = test.get_property("model:%s"%(model))
                if newname and newname != s:
                    # add to translation dictionary
                    spdict[s] = newname
        # save dictionary (resets old values)
        self._translate = spdict
        self._translate_model = model

        
    def translate_variables(self, sort=True):
        """Translate variable names of a pattern 'cSP1_SP2' where c is any single letter
        and SP1, SP2 (or more) are species names. Returns an OrderedDict with variable
        names and values. Variables that don't follow the pattern are copied verbatim."""
        if self._translate:
            vkeys = self._variables.keys()
            vvals = self._variables.values()
            newvars = OrderedDict()
            for i in range(len(vkeys)):
                varname = vkeys[i]
                prefix = varname[0]
                tokens = varname[1:].split("_")
                for j in range(len(tokens)):
                    for k, v in self._translate.items():
                        if tokens[j] == k:
                            tokens[j] = v
                varname = prefix + "_".join(tokens)
                newvars[varname] = vvals[i]
        else:
            newvars = OrderedDict(self._variables.items())
        # replace M with cair
        for k, v in newvars.items():
            if v is not None:
                newvars[k] = v.replace("M*","cair*").replace("*M","*cair")
        # sort variables if requested
        if sort:
            newvars = OrderedDict(sorted(newvars.items(), key=lambda t: t[0]))
        return newvars

        
    # ----- Mechanism output -----
    def _make_csv_header(self, separator="\t"):
        """Create a csv file header line based on the information stored in the reactions."""
        # find max. number of reactants and products
        maxreac = 0
        maxprod = 0
        for r in self.reactions:
            nreac = len(r.reactants)
            if nreac > maxreac:
                maxreac = nreac
            nprod = len(r.get_product_names())
            if nprod > maxprod:
                maxprod = nprod
        # construct header line
        header = [ "code" ]
        header.extend(["reac.%i"%(i+1) for i in range(maxreac)])
        header.extend(["prod.%i"%(i+1) for i in range(maxprod)])
        header.extend(["ai.fac", "bi.fac", "ei.fac", "a0.fac", "b0.fac", "e0.fac", "ffac",  \
                       "mech", "rxn.type", "comment"])
        return header, maxreac, maxprod


    def write_csv(self, fileid=None, separator="\t", preserve_labels=False):
        """Output mechanism as csv file.
        Fileid can be a filename or the file handler of a file opened for writing. If
        no fileid is supplied, a filename will be constructed based on the mechanism name
        and revision tag.
        Use the preserve_labels flag to preserve existing reaction labels where possible
        (this could lead to duplicate labels)."""
        # Open file
        # try to open file
        if fileid is None:
            suffix = "txt" if separator == "\t" else "csv"
            revision = self.revision if self.revision else dt.date.today().strftime("%Y%m%d")
            fileid = "%s_%s.%s" % (self.name, revision, suffix)
            print "Writing mechanism to file ", fileid
        f = self._file_open(fileid, "w")
        # construct and output header
        header, maxreac, maxprod = self._make_csv_header(separator)
        f.write(separator.join(header)+"\n")
        # build label list
        labels = self.build_labels(preserve_labels)
        # write photolysis reactions
        for i, r in enumerate(self.reactions):
            if r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_csv(separator, maxreac, maxprod, label=labels[i])+"\n")
        # write other reactions
        for i, r in enumerate(self.reactions):
            if not r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_csv(separator, maxreac, maxprod, label=labels[i])+"\n")
        # that's it
        f.close()


    def write_kpp_species(self, filename, species=None, orispecies=None):
        """Generate a KPP spc file with information about the mechanism species"""
        if species is None:
            species = self.get_species(translate=True)
        if orispecies is None:
            orispecies = self.get_species(translate=False)
        print "Writing species definitions to file ", filename
        f = self._file_open(filename, "w")
        f.write("\n")
        f.write("#INCLUDE atoms\n")
        f.write("{}\n")
        f.write("#DEFVAR\n")
        f.write("\n")
        f.write("{%s}\n"%(72*"-"))
        spctable = self._speciestable
        model = self.model
        for i, s in enumerate(species):
            if s in ["M", "hv"]:
                continue
            cshort = s
            c = spctable.find_model_species(orispecies[i], model=model)
            if c is None:
                f.write("%-16s = **** UNDEFINED ****\n"%(s))
            else:
                cdict = c.get_composition()
                cstring = " + ".join(["%i%s" % (v, k) for k, v in cdict.items()])
                clatex = "{@%s}" % (mw.cdict_to_string(cdict, latex=True))
                cname = c.get_name()
                f.write("%-16s = %32s ; %-24s {%s}\n" % (cshort, cstring, clatex, cname))
        f.close()        


    def write_kpp_variables(self, filename):
        """Write mechanism variables (constants for rate expressions) into a pseudo
        f90 file for use in MECCA."""
        def condition(varname):
            res = False
            test = varname.lower()
            if test.startswith("k"):
                res = True
            elif test.startswith("tmp"):
                res = True
            elif test.startswith("x"):
                res = True
            elif test.startswith("***"):
                res = True
            return res
        
        variables = self.translate_variables()
        print "Writing variable definitions to file ", filename
        f = self._file_open(filename, "w")
        f.write("\n")
        f.write("#INLINE F90_GLOBAL\n")
        f.write("\n")
        line = "  REAL :: "
        for i, k in enumerate(variables):
            if condition(k):
                line += k
                if i < len(self.variables)-1:
                    line += ", "
            if len(line) > 68:
                f.write(line+"&\n")
                line = "          "
        if line.strip():
            f.write(line+"\n")
        f.write("  REAL :: RO2\n")
        f.write("\n")
        f.write("\n")
        f.write("#INLINE F90_RCONST\n")
        f.write("\n")
        f.write("  USE messy_main_constants_mem  ! atm2Pa, N_A, R_gas\n")
        f.write("  USE messy_cmn_photol_mem      ! IP_MAX, ip_*, jname\n")
        f.write("\n")
        for k, v in variables.items():
            if condition(k):
                if v is None or not v.strip():
                    v = "0."    # set default value
                # apply the kpp dictionary to change ktroe to k_3rd, replace T with TEMP, etc.
                for dk, dv in kpp_dict.items():
                    v = re.sub(dk, dv, v)
                f.write("  %s = %s\n" % (k, v))
        f.write("\n")
        f.close()        


    def write_kpp_mecca(self, fileid=None, preserve_labels=False):
        """Output mechanism as KPP files.
        Write_kpp_mecca produces an spc and an eqn file.
        Fileid can be a filename or the file handler of a file opened for writing. If
        no fileid is supplied, a filename will be constructed based on the mechanism name
        and revision tag.
        Write_kpp_mecca generates one eqn and one spc file which include reaction labels
        and comments. Use write_kpp_ukca to generate three eqnfiles instead.
        Use the object's model attribute to make sure the spc definitions are correct. If
        set, the search for a species in the speciestable will only look for compounds
        that are defined for this model. Default is to look for a definition for any model."""
        # try to open eqn file
        if fileid is None:
            revision = self.revision if self.revision else dt.date.today().strftime("%Y%m%d")
            fileid = "%s_%s.eqn" % (self.name, revision)
        f = self._file_open(fileid, "w")
        print "Writing mechanism to file ", f.name
        f.write("\n")
        f.write("#EQUATIONS\n")
        # get list of species
        # we also need untranslated species names in order to find composition information
        species = self.get_species()
        orispecies = self.get_species(translate=False)
        # add N2 if not present (needed for cair calculation)
        if not "N2" in species:
            species.append("N2")
            orispecies.append("N2")
        # build label list
        labels = self.build_labels(preserve_labels)
        # write non-photolysis reactions
        cursec = "MAGIC --**-- CIGAM"
        for i, r in enumerate(self.reactions):
            if not r._isphoto:
                if r._section and r._section != cursec:
                    # write new section heading
                    f.write("\n")
                    f.write("// "+80*"-"+"\n")
                    f.write("// SECTION %s\n"%(r._section))
                    f.write("// "+80*"-"+"\n")
                    f.write("\n")
                    cursec = r._section
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_kpp(label=labels[i], add_prod=True)+"\n")
        # write photolysis reactions
        f.write("\n")
        f.write("// "+80*"-"+"\n")
        f.write("// Photolysis reactions\n")
        f.write("// "+80*"-"+"\n")
        f.write("\n")
        for i, r in enumerate(self.reactions):
            if r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_kpp(label=labels[i], add_prod=True)+"\n")
        # remember filename for spc file
        filename = f.name
        f.close()
        self.write_kpp_species(filename.replace(".eqn",".spc"), species, orispecies)
        # generate 'variable' file with INLINE sections on variable declarations and definitions
        # the contents of this file must be inserted into the eqn file for use in MECCA
        # Only variables starting with 'k' are included.
        self.write_kpp_variables(filename.replace(".eqn","_variables.f90"))


    def write_kpp_ukca(self, filebasename=None, preserve_labels=False):
        """Output mechanism as KPP files.
        Write_kpp_ukca generates three eqn files for use in the UKCA model.
        Filebasename shall be the path and filename template for three eqn files which are
        separated into photolysis, bimolecular and termolecular reactions.
        '_photo.eqn', '_bimol.eqn', and '_termol.eqn' will be added automatically. If
        no filebasename is supplied, it will be constructed based on the mechanism name
        and revision tag."""
        # try to open eqn file
        if filebasename is None:
            revision = self.revision if self.revision else dt.date.today().strftime("%Y%m%d")
            file1 = "%s_%s_photo.eqn" % (self.name, revision)
            file2 = "%s_%s_bimol.eqn" % (self.name, revision)
            file3 = "%s_%s_termol.eqn" % (self.name, revision)
        # build label list
        labels = self.build_labels(preserve_labels)
        # write photolysis reactions
        f = self._file_open(file1, "w")
        print "Writing photolysis reactions to file %s" % (f.name)
        f.write("#EQUATIONS\n")
        for i, r in enumerate(self.reactions):
            if r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_kpp(extended=False, label=labels[i])+"\n")
        f.close()
        # write bimolecular reactions
        f = self._file_open(file2, "w")
        print "Writing bimolecular reactions to file %s" % (f.name)
        f.write("#EQUATIONS\n")
        for i, r in enumerate(self.reactions):
            if not "M" in r.reactants and not r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_kpp(extended=False, label=labels[i])+"\n")
        f.close()
        # write termolecular reactions
        f = self._file_open(file3, "w")
        print "Writing termolecular reactions to file %s" % (f.name)
        f.write("#EQUATIONS\n")
        for i, r in enumerate(self.reactions):
            if "M" in r.reactants and not r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_kpp(extended=False, label=labels[i])+"\n")
        f.close()


    def write_mech(self, fileid=None):
        """Output mechanism as mech file (new master format).
        Fileid can be a filename or the file handler of a file opened for writing. If
        no fileid is supplied, a filename will be constructed based on the mechanism name
        and revision tag."""
        # try to open file
        if fileid is None:
            revision = self.revision if self.revision else dt.date.today().strftime("%Y%m%d")
            fileid = "%s_%s.mech" % (self.name, revision)
        f = self._file_open(fileid, "w")
        print "Writing mechanism to file ", f.name
        # write header comments and look for "MODEL" tag
        hasmodeltag = False
        hc = self.comments.get("header", [])
        for l in hc:
            f.write(l.strip("\r\n")+"\n")
            if "MODEL" in l:
                hasmodeltag = True
        f.write("\n")
        # write MODEL tag
        if not hasmodeltag:
            f.write("# namespace for finding compounds in speciestable")
            f.write("MODEL: %s"%(self.model))
            f.write("\n")
        # write Reactions section with optional reaction comments
        f.write("\n\n")
        f.write("REACTIONS\n")
        rc = self.comments.get("reactions", [])
        for l in rc:
            if not (l.strip().startswith("!") or l.strip().startswith("#")):
                l = "# "+l
            f.write(l.strip("\r\n")+"\n")
        cursec = "MAGIC --**-- CIGAM"
        for r in self.reactions:
            if r._section and r._section != cursec:
                # write new section heading
                f.write("\n")
                f.write("! "+80*"-"+"\n")
                f.write("! SECTION %s\n"%(r._section))
                f.write("! "+80*"-"+"\n")
                f.write("\n")
                cursec = r._section
            rc = r.copy()
            if len(self._translate) > 0:
                rc.rename_compounds(self._translate)
            f.write(rc.to_mech()+"\n")
        # write variables section with optional comments
        f.write("\n\n")
        f.write("VARIABLES\n")
        cc = self.comments.get("variables", [])
        for l in cc:
            if not (l.strip().startswith("!") or l.strip().startswith("#")):
                l = "# "+l
            f.write(l.strip("\r\n")+"\n")
        if len(self.variables) == 0:
            self.extract_variables()
        variables = self.translate_variables()
        for c in variables:
            if variables[c]:
                f.write("%s = %s\n" %(c, variables[c]))
            else:
                f.write(c+"\n")
        # write functions section with optional comments
        f.write("\n\n")
        f.write("FUNCTIONS\n")
        fc = self.comments.get("functions", [])
        for l in fc:
            if not (l.strip().startswith("!") or l.strip().startswith("#")):
                l = "# "+l
            f.write(l.strip("\r\n")+"\n")
        for c in sorted(self._functions):
            if self._functions[c]:
                f.write("%s = %s\n" %(c, self._functions[c]))
            else:
                f.write(c+"\n")
        # write final comments if they exist
        f.write("\n")
        f.write("END\n\n")
        fc = self.comments.get("end", [])
        for l in fc:
            f.write(l.strip("\r\n")+"\n")
        f.write("\n")
        f.close()
        

    def write_mozpp(self, fileid=None, preamble=None, footer=None, fixed=None,
                    explicit=None, preserve_labels=False):
        """Output mechanism as MOZPP file.
        Fileid can be a filename or the file handler of a file opened for writing. If
        no fileid is supplied, a filename will be constructed based on the mechanism name
        and revision tag.
        The output will be a complete, albeit minimalistic mozpp file.
        Use the preamble and footer keywords to supply a template header and footer section
        (header above 'SPECIES', footer below 'End Reactions'). If no fixed species are given,
        M, N2, O2 will be assumed. If no explicit specdies are given, the Implicit solver
        section will contain the keyword 'All'.
        Use the object's model attribute to make sure the spc definitions are correct. If
        set, the search for a species in the speciestable will only look for compounds
        that are defined for this model. Default is to look for a definition for any model."""
        # a few preparations
        if fixed is None:
            fixed = ["M", "N2", "O2"]
        if explicit is None:
            explicit = []
        # try to open file
        if fileid is None:
            revision = self.revision if self.revision else dt.date.today().strftime("%Y%m%d")
            fileid = "%s_%s.in" % (self.name, revision)
        f = self._file_open(fileid, "w")
        print "Writing mechanism to file ", f.name
        # build label list
        labels = self.build_labels(preserve_labels)
        # get list of species
        # we also need untranslated species names in order to find composition information
        species = self.get_species()
        orispecies = self.get_species(translate=False)
        # get species composition
        spctable = self._speciestable
        model = self.model
        if self._translate and self._translate_model:
            model = self._translate_model
        spdict = OrderedDict()
        for j, s in enumerate(species):
            if s in ["M", "hv", "e"]:
                continue
            c = spctable.find_model_species(orispecies[j], model=model)
            if c is None:
                print("**** Undefined species: %s"%(s))
                spdict[s] = "***"+s+"***"   # dummy entry
            else:
                cstring = mw.cdict_to_string(c.get_composition()).strip()
                if not cstring:
                    print("**** Undefined composition for species: %s"%(s))
                    # quick fix
                    spdict[s] = "C"
                spdict[s] = cstring
        # write header section
        if preamble is not None:
            for l in preamble:
                f.write(l.strip("\r\n")+"\n")  # make sure we have one EOL character
        f.write("\n")
        # write header comments
        hc = self.comments.get("header", [])
        for l in hc:
            f.write(" * "+l.strip("\r\n")+"\n")
        f.write("\n")
        # write species section
        f.write("Species\n")
        f.write("\n")
        f.write("      Solution\n")
        line = " "
        for k, v in spdict.items():
            # skip electrons
            if k == "e":
                continue
            # translate species name if translation dictionary is active
            if k in self._translate:
                k = self._translate[k]
            if k == v:
                line += k+", "
            else:
                line += k+" -> "+v+", "
            if len(line) > 78:
                f.write(line[:-2]+"\n")
                line = " "
        if line.strip():
            f.write(line[:-2]+"\n")   # last line
        f.write("      End Solution\n")
        # write fixed and col-int sections
        f.write("\n")
        f.write("\n")
        f.write("      Fixed\n")
        f.write(", ".join(fixed)+"\n")
        f.write("      End Fixed\n")
        f.write("\n")
        f.write("\n")
        f.write("      Col-int\n")
        f.write(" O3 = 0.\n")
        f.write(" O2 = 0.\n")
        f.write("      End Col-int\n")
        f.write("\n")
        f.write("\n")
        f.write("End Species\n")
        # write solution classes section
        f.write("Solution Classes\n")
        if explicit:
            f.write("       Explicit\n")
            f.write(", ".join(explicit)+"\n")
            f.write("       End Explicit\n")
        f.write("       Implicit\n")
        if explicit:
            line = "        "
            for s in species:
                if s in self._translate:
                    s = self._translate[s]
                if not s in explicit and not s in ["M", "hv"]:
                    line += s+", "
                if len(line) > 78:
                    f.write(line[:-2]+"\n")
                    line = "        "
            if line:
                f.write(line[:-2]+"\n")   # last line
        else:  # no explicit species
            f.write("        All\n")
        f.write("       End Implicit\n")
        f.write("End Solution Classes\n")
        f.write("\n")
        f.write("\n")
        # write chemistry section
        f.write("Chemistry\n")
        # photolysis 
        f.write("       Photolysis\n")
        # write photolysis reactions
        for i, r in enumerate(self.reactions):
            if r._isphoto:
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_mozpp(label=labels[i])+"\n")
        f.write("       End Photolysis\n")
        f.write("\n")
        # other reactions 
        f.write("       Reactions\n")
        # write non-photolysis reactions
        cursec = "MAGIC --**-- CIGAM"
        for i, r in enumerate(self.reactions):
            if not r._isphoto:
                if r._section and r._section != cursec:
                    # write new section heading
                    f.write("\n")
                    f.write(" * "+80*"-"+"\n")
                    f.write(" * SECTION %s\n"%(r._section))
                    f.write(" * "+80*"-"+"\n")
                    f.write("\n")
                    cursec = r._section
                rc = r.copy()
                if len(self._translate) > 0:
                    rc.rename_compounds(self._translate)
                f.write(rc.to_mozpp(label=labels[i])+"\n")
        f.write("       End Reactions\n")
        f.write("\n")
        f.write("\n")
        # Finish with footer or add 'End Chemistry' if no footer section is given
        if footer is not None:
            for l in footer:
                f.write(l.strip("\r\n")+"\n")  # make sure we have one EOL character
            f.write("\n")
        else:
            f.write("End Chemistry\n")
        f.close()


