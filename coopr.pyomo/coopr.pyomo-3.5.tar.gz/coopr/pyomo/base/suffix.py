#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Suffix','active_export_suffix_generator','active_import_suffix_generator']

import sys
import logging
import weakref
import copy
import pyutilib.math
from six import iteritems, iterkeys, itervalues

from coopr.pyomo.base.component import Component, register_component

logger = logging.getLogger('coopr.pyomo')

# A list of convenient suffix generators, including:
#   - active_export_suffix_generator **(used by problem writers)
#   - export_suffix_generator
#   - active_import_suffix_generator **(used by OptSolver and PyomoModel._load_solution)
#   - import_suffix_generator
#   - active_local_suffix_generator
#   - local_suffix_generator
#   - active_suffix_generator
#   - suffix_generator

def active_export_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.exportEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.exportEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def export_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.exportEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.exportEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_import_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.importEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.importEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def import_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.importEnabled() is True:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.importEnabled() is True) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_local_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.getDirection() is Suffix.LOCAL:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if (suffix.getDirection() is Suffix.LOCAL) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def local_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.getDirection() is Suffix.LOCAL:
                yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if (suffix.getDirection() is Suffix.LOCAL) and \
               (suffix.getDatatype() is datatype):
                yield name, suffix

def active_suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            yield name, suffix
    else:
        for name, suffix in iteritems(a_block.active_subcomponents(Suffix)):
            if suffix.getDatatype() is datatype:
                yield name, suffix

def suffix_generator(a_block,datatype=False):
    if (datatype is False):
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            yield name, suffix
    else:
        for name, suffix in iteritems(a_block.subcomponents(Suffix)):
            if suffix.getDatatype() is datatype:
                yield name, suffix

# THOUGHTS: 

# TODO: Should we, when setting the value on a component, start collecting
#       a dictionary of components by their type (like on Blocks)

# TODO: Should calling clearValue on a parent component (like _VarArray) clear
#       its own dictionary entry AS WELL AS any possible dictionary entries
#       corresponding to its subcomponent entries (e.g. _VarData members)?
#       Right now this does not happen. One could ask the same of setValue.


class Suffix(Component):
    """A model suffix, representing extranious model data"""

    """
    Constructor Arguments:
        direction   The direction of information flow for this suffix.
                        By default, this is LOCAL, indicating that no
                        suffix data is exported or imported.
        datatype    A variable type associated with all values of this
                        suffix.
    """

    # Suffix Directions
    # If more directions are added be sure to update the error
    # message in the setDirection method
    LOCAL  = 0 # neither
    EXPORT = 1 # sent to solver or other external location
    IMPORT = 2 # obtained from solver or other external source
    IMPORT_EXPORT = 3 # both
    SuffixDirections = (LOCAL,EXPORT,IMPORT,IMPORT_EXPORT)
    SuffixDirectionToStr = {LOCAL:'Suffix.LOCAL',EXPORT:'Suffix.EXPORT',IMPORT:'Suffix.IMPORT',IMPORT_EXPORT:'Suffix.IMPORT_EXPORT'}
    # Suffix Datatypes
    FLOAT = 4
    INT = 0
    SuffixDatatypes = (FLOAT,INT,None)
    SuffixDatatypeToStr = {FLOAT:'Suffix.FLOAT',INT:'Suffix.INT',None:str(None)}

    def __getstate__(self):
        """
        This method must be defined for deepcopy/pickling because 
        this class relies on component ids.
        """
        result = super(Suffix, self).__getstate__()
        result['_subcomponent_value_map'] = tuple((ref(),val) for ref,val in itervalues(self._subcomponent_value_map) if ref() is not None)
        return result

    def __setstate__(self, state):
        """
        This method must be defined for deepcopy/pickling because 
        this class relies on component ids.
        """
        id_func = id
        weakref_func = weakref.ref
        state['_subcomponent_value_map'] = dict((id_func(comp),(weakref_func(comp),val)) for comp,val in state['_subcomponent_value_map'])
        return super(Suffix,self).__setstate__(state)

    def __init__(self, *args, **kwds):
        
        # Suffix type information
        self._direction = None
        self._datatype = None
        self._rule = None
        
        # The meat of suffixes... a dictionary mapping 
        # Pyomo component ids to suffix values
        self._subcomponent_value_map = {}
        
        # TODO: __FIX_ME__: Blocks assume everything is a (Sparse)IndexedComponent inside
        #       __setattr__ so until this is fixed we need to define a dummy _index data
        #       member
        self._index = None
        
        # The suffix direction
        direction = kwds.pop('direction',Suffix.LOCAL)
        # The suffix datatype
        datatype = kwds.pop('datatype',Suffix.FLOAT)
        # The suffix construction rule
        self._rule = kwds.pop('rule',None)
        
        # Initialize base class
        kwds.setdefault('ctype', Suffix)
        Component.__init__(self, *args, **kwds)
        
        # Check that keyword values make sense 
        # (these function have internal error checking).
        self.setDirection(direction)
        self.setDatatype(datatype) 

        if self._rule is None:
            self.construct()

    def reset(self):
        """
        Reconstructs this component by clearing all values and re-calling
        construction rule if it exists.
        """
        self.clearAllValues()
        self._constructed = False
        self.construct()

    def construct(self, data=None):
        """
        Constructs this component, applying rule if it exists.
        """
        generate_debug_messages = (__debug__ is True) and (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing suffix %s",self.cname())

        if self._constructed is True:
            return

        self._constructed = True

        if self._rule is not None:
            # TODO: expande=?
            self.updateValues(self._rule(self._parent()))

    def exportEnabled(self):
        """
        Returns True when this suffix is enabled for export to solvers.
        """
        return bool(self._direction & Suffix.EXPORT)

    def importEnabled(self):
        """
        Returns True when this suffix is enabled for import from solutions.
        """
        return bool(self._direction & Suffix.IMPORT)

    def updateValues(self,data_buffer,expand=True):
        """
        Updates the suffix data given a list of component,value tuples. Provides
        an improvement in efficiency over calling setValue on every component.
        """
        if expand is True:
            # set array components first
            id_func = id
            weakref_func = weakref.ref
            # TODO: Check if we need to copy in order to iterate over twice (e.g., it's a generator or iterator)
            data_buffer = list(data_buffer)
            for comp,value in ((_comp,_value) for _comp,_value in data_buffer if _comp.component() is _comp):
                self._subcomponent_value_map.update((id_func(subcomp),(weakref_func(subcomp),value)) for subcomp in itervalues(comp))
            # set subcomponents last
            self._subcomponent_value_map.update((id_func(comp),(weakref_func(comp),val)) for comp,val in data_buffer if comp.component() is not comp)
        else:
            id_func = id
            weakref_func = weakref.ref
            self._subcomponent_value_map.update((id_func(comp),(weakref_func(comp),val)) for comp,val in data_buffer)

    def extractValues(self):
        """
        Extract all data stored on this Suffix into a list of component, value tuples.
        """
        return list((subcomponent_ref(),value) for subcomponent_ref,value in itervalues(self._subcomponent_value_map) if subcomponent_ref() is not None)
        
    def setValue(self,component,value,expand=True):
        """
        Sets the value of this suffix on the specified component.
        """
        if expand is True:
            if component.component() is not component:
                self._subcomponent_value_map[id(component)] = (weakref.ref(component),value)
            else:
                id_func = id
                weakref_func = weakref.ref
                self._subcomponent_value_map.update((id_func(subcomponent),(weakref_func(subcomponent),value)) for subcomponent in itervalues(component))
        else:
            self._subcomponent_value_map[id(component)] = (weakref.ref(component),value)

    def setAllValues(self,value):
        """
        Sets the value of this suffix on all components.
        """
        self._subcomponent_value_map = dict((ID,(ref,value)) for ID,(ref,old_value) in iteritems(self._subcomponent_value_map))

    def getValue(self,component):
        """
        Returns the current value of this suffix for the specified component.
        """
        # check if the component has been assigned an individual
        # suffix value.
        # **Note: We do this safely by checking that the id is still valid
        #         for the original component it was assigned to by checking
        #         the weakref
        cid = id(component)
        if cid in self._subcomponent_value_map:
            ref,value = self._subcomponent_value_map[cid]
            if ref() is component:
                return value
            else:
                # A rare case where the id was reassigned
                del self._subcomponent_value_map[cid]
        return None

    def clearValue(self,component, expand=True):
        """
        Clears suffix information for a component.
        """
        # clearing the value on a specified component
        if (expand is False) or (component.component() is not component):
            cid = id(component)
            if cid in self._subcomponent_value_map:
                del self._subcomponent_value_map[cid]
        else:
            for subcomponent in itervalues(component):
                cid = id(subcomponent)
                if cid in self._subcomponent_value_map:
                    del self._subcomponent_value_map[cid]

    def clearAllValues(self):
        """
        Clears all suffix data.
        """
        self._subcomponent_value_map = {}
        
    def setDatatype(self,datatype):
        """
        Set the suffix datatype.
        """
        if datatype not in self.SuffixDatatypes:
            raise ValueError("Suffix datatype must be one of: %s. \n" \
                              "Value given: %s" % (list(Suffix.SuffixDatatypeToStr.values()),datatype))
        self._datatype = datatype

    def getDatatype(self):
        """
        Return the suffix datatype.
        """
        return self._datatype

    def setDirection(self,direction):
        """ 
        Set the suffix direction.
        """
        if not direction in self.SuffixDirections:
            raise ValueError("Suffix direction must be one of: %s. \n" \
                              "Value given: %s" % (list(self.SuffixDirectionToStr.values()),direction))
        self._direction = direction

    def getDirection(self):
        """
        Return the suffix direction.
        """
        return self._direction

    def __str__(self):
        """
        Return a string representation of the suffix.  If the name attribute is None,
        then return ''
        """
        if self.cname() is None:
            return ""
        else:
            return self.cname()

    def _pprint(self):
        return (
            [('Direction', self.SuffixDirectionToStr[self._direction]),
             ('Datatype', self.SuffixDatatypeToStr[self._datatype]),
             ],
            ( (str(k()),v) for k,v in itervalues(self._subcomponent_value_map) 
              if k() is not None ),
            ("Key","Value"),
            lambda k,v: [ k, v ]
            )

    def Xpprint(self, ostream=None, verbose=False, prefix='  '):
        """
        Print component information. Setting verbose to True includes suffix values."""
        if ostream is None:
            ostream = sys.stdout
        ostream.write(prefix+self.cname()+" :")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
        else:
            ostream.write('\n')
        ostream.write(prefix)
        ostream.write("\tDirection= ")
        if self._direction in self.SuffixDirectionToStr:
            ostream.write(self.SuffixDirectionToStr[self._direction]+"\n")
        else:
            raise ValueError("Unexpected Suffix direction encountered in pprint method: %s" % (self._direction))
        ostream.write("\tDatatype= ")
        if self._datatype in self.SuffixDatatypeToStr:
            ostream.write(self.SuffixDatatypeToStr[self._datatype]+"\n")
        else:
            raise ValueError("Unexpected Suffix datatype encountered in pprint method: %s" % (self._datatype))
        # print all component values
        if verbose is True:
            ostream.write('\tValues=\n')
            name_data = dict((ref().cname(True),val) for ref,val \
                                                     in itervalues(self._subcomponent_value_map) \
                                                     if ref() is not None)
            for key in sorted(iterkeys(name_data)):
                ostream.write('\t  %s = %s\n' % (key, name_data[key]))

register_component(Suffix, "Extraneous model data")
