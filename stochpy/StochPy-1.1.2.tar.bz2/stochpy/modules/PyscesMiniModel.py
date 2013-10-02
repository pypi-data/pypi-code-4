#! /usr/bin/env python
"""
PySCeS MDL Parser
=================
The PySCeS parser is used to import a model written in the MDL of PySCeS. Further, all required input do to stochastic simulations is build.

Written by T.R. Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 20, 2013
"""

import os,copy,time,sys,operator
try: 
    import numpy as np
except ImportError:
    print "Error: The NumPy module is not installed"
    sys.exit()
  
import stochpy.modules.PyscesParse
import stochpy.modules.SBML2PSC as SBML2PSC
from stochpy import model_dir, output_dir
from stochpy.core2.InfixParser import MyInfixParser

InfixParser = MyInfixParser()
InfixParser.buildlexer()
InfixParser.buildparser(debug=0, debugfile='infix.dbg', tabmodule='infix_tabmodule')
InfixParser.setNameStr('self.', '')

mach_spec = np.MachAr()
pscParser = stochpy.modules.PyscesParse.PySCeSParser(debug=0)

class NewCoreBase(object):
    """
    Core2 base class, needed here as we use Core2 derived classes
    in PySCes
    """
    name = None
    __DEBUG__ = False

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name

    def get(self, attr):
        """Return an attribute whose name is str(attr)"""
        return self.__getattribute__(attr)
        
# this must stay in sync with core2
class NumberBase(NewCoreBase):
    """
    Derived Core2 number class.
    """
    value = None
    value_initial = None

    def __call__(self):
        return self.value

    def getValue(self):
        return self.value

    def setValue(self, v):
        self.value = v
        
class EventAssignment(NumberBase):
    """
    Event assignments are actions that are triggered by an event.
    Ported from Core2 to build an event handling framework fro PySCeS
    """
    variable = None
    symbols = None
    formula = None
    code_string = None
    xcode = None
    mod = None
    piecewises = None
    __DEBUG__ = False

    def __call__(self):
        setattr(self.mod, self.variable, self.value)
        if self.__DEBUG__: print '\tAssigning %s = %s' % (self.variable, self.value)
        return True

    def __init__(self, name, mod):
        self.setName(name)
        self.mod = mod

    def setVariable(self, var):
        self.variable = var

    def setFormula(self, formula):
        self.formula = formula
        InfixParser.setNameStr('self.mod.', '')
        InfixParser.SymbolReplacements = {'_TIME_':'self.mod._TIME_'} # TODO
        InfixParser.parse(formula)
        self.piecewises = InfixParser.piecewises
        self.symbols = InfixParser.names
        self.code_string = 'self.value=%s' % InfixParser.output
        self.xcode = compile(self.code_string, 'EvAs: %s' % self.name, 'exec')
        ##  print '\t', self.name, self.code_string

    def evaluateAssignment(self):
        exec(self.xcode)

# adapted from core2
class Event(NewCoreBase):
    """
    Event's have triggers and fire EventAssignments when required.
    Ported from Core2.
    """
    trigger = None
    delay = 0.0
    formula = None
    code_string = None
    xcode = None
    state0 = False
    state = False
    assignments = None
    _TIME_ = 0.0
    _ASS_TIME_ = 0.0   
    _TRIGGER_TIME_ = False
    _need_action = False
    symbols = None
    _time_symbol = None
    piecewises = None
    mod = None
    __DEBUG__ = True

    def __init__(self, name, mod):
        self.setName(name)
        self.assignments = []
        self.mod = mod

    def __call__(self, time,X_matrix):#,__species__):        
        self._TIME_ = time
        exec(self.xcode)       
        #print self._TIME_,self.state,__species__.P2
        ret = False
        if self.state0 and not self.state:
            self.state0 = self.state
        if not self.state0 and self.state:
            #for ass in self.assignments:
            #    ass.evaluateAssignment()
            self.state0 = self.state
            self._need_action = True
            self._ASS_TIME_ = time + self.delay
            #print self._ASS_TIME_            
            #print '\nevent %s is evaluating at %s' % (self.name, time)
            ret = False
        if self._need_action and self._TIME_ >= self._ASS_TIME_:
            #for ass in self.assignments:
            #    ass()
            #print 'event %s is assigning at %s (delay=%s)' % (self.name, time, self.delay)
            self._need_action = False
            ret = True
        return ret

    def setTrigger(self, formula, delay=0.0):
        self.formula = formula
        self.delay = delay
        InfixParser.setNameStr('self.mod.', '')
        ##  print formula, delay
        if self._time_symbol != None:
            InfixParser.SymbolReplacements = {self._time_symbol : '_TIME_'}
        else:
            InfixParser.SymbolReplacements = {'_TIME_' : '_TIME_'}
        InfixParser.parse(formula)
        self.piecewises = InfixParser.piecewises
        self.symbols = InfixParser.names
        self.code_string = 'self.state=%s' % InfixParser.output
        #self.code_string = InfixParser.output
        #self.code_string = self.code_string.replace('self.mod._TIME_','self.sim_t')
        self.code_string = self.code_string.replace('self.mod._TIME_','self._TIME_')
        #self.code_string = 'IsTrigger = ' + self.code_string # TODO
        #self.code_string = self.code_string.replace('self.mod.','__species__.')        
        #self.xcode = compile(self.code_string, 'Ev: %s' % self.name, 'exec')
        ##  print self.name, self.code_string

    def setAssignment(self, var, formula):
        ass = EventAssignment(var, mod=self.mod)
        ass.setVariable(var)
        ass.setFormula(formula)
        self.assignments.append(ass)
        self.__setattr__('_'+var, ass)

    def reset(self):
        self.state0 = False
        self.state = False
        self._TIME_ = 0.0
        self._ASS_TIME_ = 0.0        
        self._TRIGGER_TIME_ = False

class NewCoreBase(object):
    """ Core2 base class, needed here as we use Core2 derived classes in PySCeS """
    name = None
    __DEBUG__ = False

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name

    def get(self, attr):
        """Return an attribute whose name is str(attr)"""
        return self.__getattribute__(attr)

class Function(NewCoreBase):
    """ Function class ported from Core2 to enable the use of functions in PySCeS """
    formula = None
    code_string = None
    xcode = None
    value = None
    symbols = None
    argsl = None
    mod = None
    piecewises = None
    functions = None

    def __init__(self, name, mod):
        self.name = name
        self.argsl = []
        self.functions = []
        self.mod = mod

    def __call__(self, *args):
        for ar in xrange(len(args)):
            self.__setattr__(self.argsl[ar], args[ar])
        exec(self.xcode)
        return self.value

    def setArg(self, var, value=None):
        self.__setattr__(var, value)
        self.argsl.append(var)

    def addFormula(self, formula):
        self.formula = formula
        InfixParser.setNameStr('self.', '')
        InfixParser.SymbolReplacements = {'_TIME_':'mod._TIME_'}
        InfixParser.parse(formula)
        self.piecewises = InfixParser.piecewises
        self.symbols = InfixParser.names
        self.functions = InfixParser.functions
        self.code_string = 'self.value=%s' % InfixParser.output
        self.xcode = compile(self.code_string, 'Func: %s' % self.name, 'exec')

class PyscesInputFileParser(object):
    """ This class contains the PySCeS model loading """
    ModelDir = None
    ModelFile = None
    ModelOutput = None
    __settings__ = None
    N = None        
    def __init__(self, File, dir, output_dir=None):         
        self.ModelDir = dir
        self.ModelFile = File
        self.IsConverted = False
        if output_dir == None:
            self.ModelOutput = os.getcwd()
        else:
            assert os.path.exists(output_dir),"n&s is not a valid path" % output_dir
        self.__settings__ = {}
        self.InitialiseInputFile()    
        self.InitialiseEvents()    
        #self.Nmatrix = self.buildN()    # Stoch Matrix

    def InitialiseInputFile(self):
        """ Parse the input file associated with the PySCeS model instance and assign the basic model attributes """
        self.__parseOK = 1 # check that model has parsed ok
        path_ = os.path.join(self.ModelDir,self.ModelFile)
        try:
            if os.path.exists(os.path.join(self.ModelDir,self.ModelFile)): pass
            #else: print '\nInvalid self.ModelFile: ' + os.path.join(self.ModelDir,self.ModelFile)
        except:
            print 'Warning: Problem verifying: ' + os.path.join(self.ModelDir,self.ModelFile)
        
        if self.ModelFile[-4:] == '.psc':
            pass
        elif self.ModelFile[-4:].lower() == '.xml':
            try:
                print "Info: extension is .xml"
                converter = SBML2PSC.SBML2PSC()
                converter.SBML2PSC(self.ModelFile,self.ModelDir)
                print "Info: SBML data is converted into psc data and is stored at:",model_dir
                self.ModelFile += '.psc'
                self.ModelDir = model_dir            
                self.IsConverted = True
            except:
                print "Error: Make sure that the libsbml and libxml2 are installed and that the input file is written in SBML format"
                print "Info: Use the psc format if both libraries are not available."              
                sys.exit()          
        else:
            print 'Assuming extension is .psc'
            self.ModelFile += '.psc'

        print 'Parsing file: %s' % os.path.join(self.ModelDir, self.ModelFile)
        pscParser.ParsePSC(self.ModelFile,self.ModelDir,self.ModelOutput)
        badlist = pscParser.KeywordCheck(pscParser.ReactionIDs)
        badlist = pscParser.KeywordCheck(pscParser.Inits,badlist)

        if len(badlist) != 0:
            print '\n******************************\nPSC input file contains PySCeS keywords please rename them and reload:'
            for item in badlist:
                print '   --> ' + item
            print '******************************\n'
            self.__parseOK = 0

        if self.__parseOK:
            # brett 2008
            self.__nDict__ = pscParser.nDict.copy()
            self.__sDict__ = pscParser.sDict.copy()
            self.__pDict__ = pscParser.pDict.copy()
            self.__uDict__ = pscParser.uDict.copy()            
            self.__eDict__ = pscParser.Events.copy()
            self.__aDict__ = pscParser.AssignmentRules.copy()
            # model attributes are now initialised here brett2008
            self.__InitDict__ = {}
            # set parameters and add to __InitDict__
            for p in sorted(self.__pDict__):
                setattr(self, self.__pDict__[p]['name'], self.__pDict__[p]['initial'])
                self.__InitDict__.update({self.__pDict__[p]['name'] : self.__pDict__[p]['initial']})
            # set species and add to __InitDict__ and set mod.Xi_init
            for s in sorted(self.__sDict__):
                setattr(self, self.__sDict__[s]['name'], self.__sDict__[s]['initial'])
                if not self.__sDict__[s]['fixed']:
                    setattr(self, self.__sDict__[s]['name']+'_init', self.__sDict__[s]['initial'])
                self.__InitDict__.update({self.__sDict__[s]['name'] : self.__sDict__[s]['initial']})

            # setup keywords
            self.__KeyWords__ = pscParser.KeyWords.copy()
            if self.__KeyWords__['Modelname'] == None:

                self.__KeyWords__['Modelname'] = self.ModelFile.replace('.psc','')
            if self.__KeyWords__['Description'] == None:
                self.__KeyWords__['Description'] = self.ModelFile.replace('.psc','')

            # if SpeciesTypes undefined assume []
            if self.__KeyWords__['Species_In_Conc'] == None:
                self.__KeyWords__['Species_In_Conc'] = True
            # if OutputType is undefined assume it is the same as SpeciesType
            if self.__KeyWords__['Output_In_Conc'] == None:
                if self.__KeyWords__['Species_In_Conc']:
                    self.__KeyWords__['Output_In_Conc'] = True
                else:
                    self.__KeyWords__['Output_In_Conc'] = False

            # set the species type in sDict according to 'Species_In_Conc'
            for s in sorted(self.__sDict__):
                if not self.__KeyWords__['Species_In_Conc']:
                    self.__sDict__[s]['isamount'] = True
                else:
                    self.__sDict__[s]['isamount'] = False

            # setup compartments
            self.__compartments__ = pscParser.compartments.copy()
            if len(sorted(self.__compartments__)) > 0:
                self.__HAS_COMPARTMENTS__ = True
            else:
                self.__HAS_COMPARTMENTS__ = False                
                
            if  self.__aDict__ != {}:
                self.__HAS_ASSIGNMENTS__ = True
                print 'Assignement(s) detected.'
            else:  
                self.__HAS_ASSIGNMENTS__ = False

            # no (self.)
            self.__fixed_species__ = copy.copy(pscParser.fixed_species)
            #print "Fixes Species",self.__fixed_species__
            self.__species__ = copy.copy(pscParser.species)
            #print "Species Vector",self.__species__
            self.__parameters__ = copy.copy(pscParser.parameters)
            #print "Parms",self.__parameters__
            self.__reactions__ = copy.copy(pscParser.reactions)
	    #print "Reactions--> rate_eqs",self.__reactions__
            self.__modifiers__ = copy.copy(pscParser.modifiers)
            #print self.__modifiers__
            self.__functions__ = pscParser.Functions.copy() 
            #print self.__functions__
            if self.__functions__ != {}:
                print "Warning: The current version of StochPy does not support function input"
        else:
            print '\nERROR: model parsing error, please check input file.\n'
        # added in a check for model correctness and human error reporting (1=ok, 0=error)
        if len(pscParser.SymbolErrors) != 0:
            print '\nUndefined symbols:\n%s' % self.SymbolErrors
        if not pscParser.ParseOK:
            print '\n\n*****\nModel parsing errors detected in input file '+ self.ModelFile +'\n*****'
            print '\nInput file errors'
            for error in pscParser.LexErrors:
                print error[0] + 'in line:\t' + str(error[1]) + ' ('+ error[2][:20] +' ...)'
            print '\nParser errors'
            for error in pscParser.ParseErrors:
                try:
                    print error[0] + '- ' + error[2][:20]
                except:
                    print error
            assert pscParser.ParseOK == 1, 'Input File Error'            
        
    def InitialiseEvents(self):
        """ Initialise Events """
        self.__events__ = []
        # for each event
        for e in self.__eDict__:
            ev = Event(e, self)
            ev._time_symbol = self.__eDict__[e]['tsymb']
            ev.setTrigger(self.__eDict__[e]['trigger'], self.__eDict__[e]['delay'])
            # for each assignment
            for ass in self.__eDict__[e]['assignments']:
                ev.setAssignment(ass, self.__eDict__[e]['assignments'][ass])
            self.__events__.append(ev)
            setattr(self, ev.name, ev)
            assert (not '_TIME_' in ev.formula or not ev.delay), "Error: The time event, %s, cannot have a delay" % ev.name            
            #if ('_TIME_' in ev.formula and ev.delay):
            #    print "Error: The time event, %s, cannot have a delay" % ev.name       
            #    sys.exit()
        os.chdir(self.ModelOutput)
        if len(self.__events__) > 0:
            self.__HAS_EVENTS__ = True
            print 'Event(s) detected.'
        else:
            self.__HAS_EVENTS__ = False

class PySCeS_Connector(PyscesInputFileParser):
  def __init__(self,ModelFile,ModelDir,IsNRM = False):
    """ 
    Use the PySCeS parser to import a set of reactions, which will be used to perform stochastic simulations. Further, some initial stuff that is necessary for stochastic simulations is build.
    
    Input:
     - *ModelFile* (string)
     - *ModelDir* (string)
    """
    self.IsConverted = False
    try:
        self.Mod = PyscesInputFileParser(File = ModelFile, dir = ModelDir)      
    except Exception,er:
        print er
        sys.exit()        
                 
    self.BuildN()
    if self.Mod.IsConverted:
        self.IsConverted = True  
    self.BuildX()
    self.BuildReactions()        
    if IsNRM:
        self.DetermineAffects()
        self.BuildDependencyGraph()

  def BuildN(self):
      """ Generates the stoichiometric matrix N from the parsed model description. Returns a stoichiometric matrix (N) as a NumPy array """
      VarReagents = ['self.'+s for s in self.Mod.__species__]
      self.N_matrix = np.zeros((len(VarReagents),len(self.Mod.__reactions__)))#,dtype=int)
      for reag in VarReagents:
          for id in self.Mod.__reactions__:
              if reag in sorted(self.Mod.__nDict__[id]['Reagents']):
                  self.N_matrix[VarReagents.index(reag)][self.Mod.__reactions__.index(id)] = self.Mod.__nDict__[id]['Reagents'][reag]       
 
  def BuildX(self):  
    """ Builds the initial concentrations of all species (X). """
    self.species = copy.deepcopy(self.Mod.__species__)	   # Species names from parser
    n_species = len(self.species)
    self.fixed_species = []
    self.fixed_species_amount = []
    for species in sorted(self.Mod.__sDict__):
        if species not in self.species:
            s_amount = self.Mod.__sDict__[species]['initial']
            self.fixed_species.append(species)
            self.fixed_species_amount.append(s_amount)
   
    self.X_matrix = np.zeros((n_species,1))#dtype = int)    
    for i in xrange(n_species):
        species = self.species[i]
        init_conc = self.Mod.__sDict__[species]['initial']
        if not self.Mod.__sDict__[species]['isamount']:    # Handle amount/concentration 19 September 2011
            if self.Mod.__compartments__:
                compartments = sorted(self.Mod.__compartments__)
                if len(compartments) > 1:
                    print "Warning: Multiple compartments are detected"
                if self.Mod.__compartments__[compartments[0]]['size'] != 1:
                    print "Warning: Species are given in concentrations and the volume is unequal to one, the species concentrations are multiplied by the compartment volume which will result in different numbers. This means that the rate equations also change."
                init_conc *= self.Mod.__compartments__[compartments[0]]['size']
        self.X_matrix[i] = init_conc                       # Add initial conc.

  def BuildReactions(self):
    """ Extract information out of each reaction, such as what are the reagents/reactants and which parameter is used for that particular reaction. """
    self.reagents  = [] 
    self.reactants = []
    self.rate_eqs  = []
    self.propensities = []     
    #self.reactions = copy.copy(self.Mod.__reactions__)
    IsReversible = False
    for r_id in self.Mod.__reactions__:
        temp_reactant = []
        temp_product  = []      
        rate_eq = self.Mod.__nDict__[r_id]['RateEq']      # Rate eq. info      
        L_parms = self.Mod.__nDict__[r_id]['Params']      # Parm from rate eq.         
        for parm in L_parms:                              # Replace parm values (fixed)                  
            parm = parm.replace('self.','')            
            if parm in self.Mod.__parameters__:
                if parm in sorted(self.Mod.__pDict__):
                    parm_value = self.Mod.__pDict__[parm]['initial']             
                elif parm in sorted(self.Mod.__sDict__): # Fix 28 Feb 2013
                    parm_value = self.Mod.__sDict__[parm]['initial']
            elif parm in sorted(self.Mod.__compartments__):
                parm_value = self.Mod.__compartments__[parm]['size']
            rate_eq = rate_eq.replace('self.%s' % parm,str(parm_value))
        rate_eq = rate_eq.replace('self.','__species__.') # Make a special object 'species' where all species amounts are stored 20 Oct 2011        
        self.propensities.append(rate_eq)                 # Add rate equation to props eq         
        self.rate_eqs.append(self.Mod.__nDict__[r_id])
        L_reagents = sorted(self.Mod.__nDict__[r_id]['Reagents']) # Remove fixed species      
        L_s_indices = []                                  # Convert reagents of each reaction into species indexes
        for reagent in L_reagents:
            reagent = reagent.replace('self.','')
            if reagent in self.species:
                L_s_indices.append(self.species.index(reagent))	# reagents of reaction r 16/09
        self.reagents.append(L_s_indices)               
        
        for reagent in L_reagents:	                  # Determine the reactants of each reaction
            if self.Mod.__nDict__[r_id]['Reagents'][reagent] < 0:    # Reactant                          
                reagent = reagent.replace('self.','')
                temp_reactant.append(reagent)
        for species in self.Mod.__nDict__[r_id]['Modifiers']:      
             temp_reactant.append(species.replace('self.',''))
                 
        self.reactants.append(temp_reactant)      
        if self.Mod.__nDict__[r_id]['Type'] == 'Rever':        
            IsReversible = True
        assert not IsReversible, "Error: The model contains reversible reactions, while Stochastic Simulation Algorithms require irreversible reactions."

  def DetermineAffects(self):  
    """ Determine the affects for each reaction"""
    self.affects = [] 
    n=0    
    for r_id in self.Mod.__reactions__: 
        D_reagents = self.Mod.__nDict__[r_id]['Reagents']
        n+=1
        temp_affects = []      
        for species in D_reagents:                   
            if D_reagents[species] != 0:
                s_id = species.replace('self.','')  # September 19, 2013               
                temp_affects.append(s_id)
        self.affects.append(temp_affects)

  def BuildDependencyGraph(self):
    """ Function which builds a dependency graph """
    # Bug removed on September 19, 2013       
    self.dep_graph = []       
    for i in xrange(len(self.affects)):
        change = []
        for species_name in self.affects[i]:
            j=0
            for reactants in self.reactants:
                if species_name in reactants:
                   change.append(j)
                j+=1        
        self.dep_graph.append(np.unique(change).tolist())               
        
    
class RegularGridDataObj(object):    
    """
    This class is specifically designed to store the results of a stochastic time simulation on fixed time intervals
    It has methods for setting the Time, Labels, Species and Propensity data and
    getting Time, Species and Rate (including time) arrays. However, of more use:

    - getOutput(\*args) feed this method species/rate labels and it will return
      an array of [time, sp1, r1, ....]
    - getDataAtTime(time) the data generated at time point "time".
    - getDataInTimeInterval(time, bounds=None) more intelligent version of the above
      returns an array of all data points where: time-bounds <= time <= time+bounds
    """
    time = None
    species = None
    propensities = None
    species_autocorrelations = None 

    species_means = None
    species_standard_deviations = None
    species_autocorrelations_means = None
    species_autocorrelations_standard_deviations = None
    propensities_means = None
    propensities_standard_deviations = None
    
    HAS_SPECIES = False
    HAS_PROPENSITIES = False
    HAS_TIME = False  
    HAS_SPECIES_AUTOCORRELATIONS = False
    HAS_PROPENSITIES_AUTOCORRELATIONS = False
    
    HAS_SPECIES_AUTOCOVARIANCES = False
    HAS_PROPENSITIES_AUTOCOVARIANCES = False
    
    HAS_AVERAGE_SPECIES_DISTRIBUTIONS = False
    HAS_AVERAGE_PROPENSITIES_DISTRIBUTIONS = False    
    
    def setSpeciesDistributionAverage(self,mean,std):
        """
        Set means and stds of species data
        
        Input:
         - *mean* (list)
         - *std* (list)
        """
        self.species_distributions_means = mean
        self.species_distributions_standard_deviations = std
        self.HAS_AVERAGE_SPECIES_DISTRIBUTIONS = True

    def setPropensitiesDistributionAverage(self,mean,std):
        """
        Set means and stds of species data

        Input:
         - *mean* (list)
         - *std* (list)
        """
        self.propensities_distributions_means = mean
        self.propensities_distributions_standard_deviations = std        
        self.HAS_AVERAGE_PROPENSITIES_DISTRIBUTIONS = True
    
    def setSpecies(self, species, lbls=None):
        """
        Set the species array
        
        Input:
         - *species* an array of species vs time data
         - *lbls* [default=None] a list of species labels
        """
        self.species = species
        self.HAS_SPECIES = True
        if lbls != None:
            self.species_labels = lbls   
            
    def setTime(self, time, lbl=None):
        """
        Set the time vector

        Input:
         - *time* a 1d array of time points
         - *lbl* [default=None] is "Time" set as required
        """
        self.time = time.reshape(len(time), 1)
        self.HAS_TIME = True
        if lbl != None:
            self.time_label = lbl

    def getSpecies(self, lbls=False):
        """
        Return an array of time+species

        Input:
        - *lbls* [default=False] return only the time+species array or optionally both the data array and a list of column label
        """
        output = None
        if self.HAS_SPECIES:
            output = np.hstack((self.time, self.species))
            labels = [self.time_label]+self.species_labels
        else:
            output = self.time
            labels = [self.time_label]
        if not lbls:
            return output
        else:
            return output, labels   
            
    def getTime(self, lbls=False):
        """
        Return the time vector

        Input:
         - *lbls* [default=False] return only the time array or optionally both the time array and time label
        """
        output = None
        if self.HAS_TIME:
            output = self.time.reshape(len(self.time),)
        if not lbls:
            return output
        else:
            return output, [self.time_label]    
            
    def setPropensities(self, propensities):
        """
        Sets an array of propensities.

        Input:
         - *propensities* (list)
        """ 
        self.propensities = propensities
        self.HAS_PROPENSITIES = True

    def setSpeciesAutocorrelations(self,auto_correlations, lbls=None):
        """
        Set the `autocorrelations` ***

        Input:
         - *auto_correlation* a list of auto correlations
         - *lbls* [default=None] a list of matching reaction names         
        """
        self.species_autocorrelations = auto_correlations
        self.HAS_SPECIES_AUTOCORRELATIONS = True   

    def setSpeciesAutocovariances(self,auto_covariances, lbls=None):
        """
        Set the `autocorrelations` ***


        Input:
         - *auto_correlation* a list of auto correlations
         - *lbls* [default=None] a list of matching reaction names         
        """
        self.species_autocovariances = auto_covariances
        self.HAS_SPECIES_AUTOCOVARIANCES = True       
        
    def setPropensitiesAutocorrelations(self,auto_correlations, lbls=None):
        """
        Set the `autocorrelations` ***

        Input:
         - *auto_correlation* a list of auto correlations
         - *lbls* [default=None] a list of matching reaction names         
        """
        self.propensities_autocorrelations = auto_correlations
        self.HAS_PROPENSITIES_AUTOCORRELATIONS = True

    def setPropensitiesAutocovariances(self,auto_covariances, lbls=None):
        """
        Set the `autocovariances` ***


        Input:
         - *auto_correlation* a list of auto covariances
         - *lbls* [default=None] a list of matching reaction names         
        """
        self.propensities_autocovariances = auto_covariances
        self.HAS_PROPENSITIES_AUTOCOVARIANCES = True             

class IntegrationStochasticDataObj(object):
    """
    This class is specifically designed to store the results of a stochastic time simulation
    It has methods for setting the Time, Labels, Species and Propensity data and
    getting Time, Species and Rate (including time) arrays. However, of more use:

    - getOutput(\*args) feed this method species/rate labels and it will return
      an array of [time, sp1, r1, ....]
    - getDataAtTime(time) the data generated at time point "time".
    - getDataInTimeInterval(time, bounds=None) more intelligent version of the above
      returns an array of all data points where: time-bounds <= time <= time+bounds
    """
    time = None
    waiting_times = None
    species = None
    species_distributions = None    
    species_distributions_means = None
    species_distributions_standard_deviations = None
    
    propensities = None
    propensities_distributions = None
    propensities_distributions_means = None
    propensities_distributions_standard_deviations = None
    
    xdata = None
    time_label = 'Time'
    waiting_times_labels = None
    species_labels = None
    propensities_labels = None
    xdata_labels = None
    HAS_SPECIES = False
    HAS_WAITING_TIMES = False
    HAS_PROPENSITIES = False    
    HAS_TIME = False
    HAS_XDATA = False
    IS_VALID = True
    TYPE_INFO = 'Stochastic'
    def setSpeciesDist(self,distributions,means,stds,moments):
        """
        setSpeciesDist stuff for the determination of distributions
        
        Input:
         - *distributions* (list)
         - *means* (dictionairy)
         - *stds* (dictionairy)
         - *moments* (dictionairy) 
        """
        self.species_distributions = distributions
        self.species_means = means
        self.species_standard_deviations = stds
        self.species_moments = moments

    def setPropensitiesDist(self,distributions,means,stds,moments):
        """
        setPropensitiesDist stuff for the determination of distributions
        
        Input:
         - *distributions* (list)
         - *means* (dictionairy)
         - *stds* (dictionairy)
         - *moments* (dictionairy) 
        """
        self.propensities_distributions = distributions
        self.propensities_means = means
        self.propensities_standard_deviations = stds
        self.propensities_moments = moments

    def setSimulationInfo(self,timesteps,endtime,simulation_trajectory):
        """
        set Simulation Information
        
        Input:
         - *timesteps* (integer)
         - *endtime* (float)
         - *simulation_trajectory* (integer)
        """
        self.simulation_timesteps = timesteps
        self.simulation_endtime = endtime
        self.simulation_trajectory = simulation_trajectory

    def setFiredReactions(self,fired_reactions):
        """
        Set the reactions that fired
        
        Input:    
         - *fired_reactions* (list)
        """
        self.fired_reactions = fired_reactions        

    def setLabels(self, species):
        """
        Set the species
        
        Input:
         - *species* a list of species labels
        """
        self.species_labels = species

    def setTime(self, time, lbl=None):
        """
        Set the time vector

        Input:
         - *time* a 1d array of time points
         - *lbl* [default=None] is "Time" set as required
        """
        self.time = time.reshape(len(time), 1)
        self.HAS_TIME = True
        if lbl != None:
            self.time_label = lbl

    def setSpecies(self, species, lbls=None):
        """
        Set the species array
        
        Input:
         - *species* an array of species vs time data
         - *lbls* [default=None] a list of species labels
        """
        self.species = species
        self.HAS_SPECIES = True
        if lbls != None:
            self.species_labels = lbls

    def setWaitingtimesMeans(self,waiting_times,rate_names):
        """
        set waiting times means
        
        Input:
         - *waiting_times* (dictionary)
        """
        self.waiting_times_means = []
        for r_id in rate_names:
            waiting_times_r = waiting_times[r_id]
            self.waiting_times_means.append(np.mean(waiting_times_r))

    def setWaitingtimesStandardDeviations(self,waiting_times,rate_names):
        """
        set waiting times standard deviations
        
        Input:
         - *waiting_times* (dictionary)
        """
        self.waiting_times_standard_deviations = []
        i=0
        for r_id in rate_names:
            waiting_times_r = np.array(waiting_times[r_id])
            if len(waiting_times_r):                
                variance = sum((self.waiting_times_means[i]- waiting_times_r)**2)/len(waiting_times_r)
                self.waiting_times_standard_deviations.append(variance**0.5)         
            else:
                self.waiting_times_standard_deviations.append(np.NAN)
            i+=1
          

    def setWaitingtimes(self, waiting_times, lbls=None):
        """
        Set the `waiting_times` this data structure is not an array but a nested list of: waiting time log bins per reaction per trajectory.         
        waiting_times = [traj_1, ..., traj_n]
        traj_1 = [wt_J1, ..., wt_Jn] # in order of SSA_REACTIONS
        wt_J1 = (xval, yval, nbin)
        xval =[x_1, ..., x_n]
        yval =[y_1, ..., y_n]
        nbin = n

        Input:
         - *waiting_times* a list of waiting times
         - *lbls* [default=None] a list of matching reaction names         
        """
        self.waiting_times = waiting_times
        self.HAS_WAITING_TIMES = True
        if lbls != None:
            self.waiting_times_labels = lbls

    def setPropensitiesLabels(self,labels): 
        """
        Input:
         - *labels* (list)
        """
        self.propensities_labels = labels            

    def setPropensities(self, propensities,lbls=None):
        """
        Sets an array of propensities.

        Input:
         - *propensities* (list)
        """ 
        P_ARR = np.zeros((len(propensities), len(propensities[0])-1), 'd')
        #P_ARR[-1,:] = np.NaN
        for r in xrange(P_ARR.shape[0]):
            P_ARR[r, :] = propensities[r][1:]
        self.propensities = P_ARR
        self.HAS_PROPENSITIES = True 
        if lbls != None:
            self.propensities_labels = lbls           

    def setXData(self, xdata, lbls=None):
        """
        Sets an array of extra simulation data

        Input:
        - *xdata* an array of xdata vs time
        - *lbls* [default=None] a list of xdata labels
        """
        self.xdata = xdata
        self.HAS_XDATA = True
        if lbls != None:
            self.xdata_labels = lbls

    def getTime(self, lbls=False):
        """
        Return the time vector

        Input:
         - *lbls* [default=False] return only the time array or optionally both the time array and time label
        """
        output = None
        if self.HAS_TIME:
            output = self.time.reshape(len(self.time),)
        if not lbls:
            return output
        else:
            return output, [self.time_label]

    def getSpecies(self, lbls=False):
        """
        Return an array of time+species

        Input:
        - *lbls* [default=False] return only the time+species array or optionally both the data array and a list of column label
        """
        output = None
        if self.HAS_SPECIES:
            output = np.hstack((self.time, self.species))
            labels = [self.time_label]+self.species_labels
        else:
            output = self.time
            labels = [self.time_label]
        if not lbls:
            return output
        else:
            return output, labels

    def getWaitingtimes(self, lbls=False, traj=[]):
        """
        Return waiting times, time+waiting_time array

        Input:
         - *lbls* [default=False] return only the time+waiting_time array or optionally both the data array and a list of column label
         - *traj* [default=[0]] return the firs or trajectories defined in this list
        """
        output = None
        labels = None
        if self.HAS_WAITING_TIMES:
            output = []
            if len(traj) == 0:
                traj = xrange(len(self.waiting_times))
            ##  if len(traj) == 1:
                ##  output = self.waiting_times[0]
            ##  else:
            for t in traj:
                output.append(self.waiting_times[t])
            labels = self.waiting_times_labels
        else:
            output = []
            labels = []
        if not lbls:
            return output
        else:
            return output, labels

    def getPropensities(self, lbls=False):
        """
        Return time+propensity array

        Input:        
         - *lbls* [default=False] return only the time+propensity array or optionally both the data array and a list of column label        
        """
        #assert self.propensities != None, "\nNo propensities"
        output = None
        if self.HAS_PROPENSITIES:
            #print self.time.shape
            #print self.propensities.shape  
            output = np.hstack((self.time, self.propensities))
            labels = [self.time_label]+self.propensities_labels
        else:
            output = self.time
            labels = [self.time_label]
        if not lbls:
            return output
        else:
            return output, labels

    def getXData(self, lbls=False):
        """
        Return time+xdata array

        Input:
        - *lbls* [default=False] return only the time+xdata array or optionally both the data array and a list of column label
        """
        output = None
        if self.HAS_XDATA:
            output = np.hstack((self.time, self.xdata))
            labels = [self.time_label]+self.xdata_labels
        else:
            output = self.time
            labels = [self.time_label]
        if not lbls:
            return output
        else:
            return output, labels

    def getDataAtTime(self, time):
        """
        Return all data generated at "time"

        Input:
         - *time* the required exact time point
        """
        #TODO add rate rule data
        t = None
        sp = None
        ra = None
        ru = None
        xd = None
        temp_t = self.time.reshape(len(self.time),)
        for tt in xrange(len(temp_t)):
            if temp_t[tt] == time:
                t = tt
                if self.HAS_SPECIES:
                    sp = self.species.take([tt], axis=0)
                if self.HAS_PROPENSITIES:
                    ru = self.propensities.take([tt], axis=0)
                if self.HAS_XDATA:
                    xd = self.xdata.take([tt], axis=0)
                break

        output = None
        if t is not None:
            output = np.array([[temp_t[t]]])
            if sp is not None:
                output = np.hstack((output,sp))
            if ra is not None:
                output = np.hstack((output,ra))
            if ru is not None:
                output = np.hstack((output,ru))
            if xd is not None:
                output = np.hstack((output,xd))
        return output

    def getDataInTimeInterval(self, time, bounds=None):
        """
        Returns an array of all data in interval: time-bounds <= time <= time+bounds
        where bound defaults to step size

        Input:
         - *time* the interval midpoint
         - *bounds* [default=None] interval half span defaults to step size
        """

        temp_t = self.time.reshape(len(self.time),)
        if bounds == None:
            bounds = temp_t[1] - temp_t[0]
        c1 = (temp_t >= time-bounds)
        c2 = (temp_t <= time+bounds)
        print 'Searching (%s:%s:%s)' % (time-bounds, time, time+bounds)

        t = []
        sp = None
        ra = None
        for tt in xrange(len(c1)):
            if c1[tt] and c2[tt]:
                t.append(tt)
        output = None
        if len(t) > 0:
            output = self.time.take(t)
            output = output.reshape(len(output),1)
            if self.HAS_SPECIES and self.HAS_TIME:
                output = np.hstack((output, self.species.take(t, axis=0)))
            if self.HAS_PROPENSITIES:
                output = np.hstack((output, self.propensities.take(t, axis=0)))
            if self.HAS_XDATA:
                output = np.hstack((output, self.xdata.take(t, axis=0)))
        return output

    def getAllSimData(self,lbls=False):
        """
        Return an array of time + all available simulation data

        Input:
         - *lbls* [default=False] return only the data array or (data array, list of labels)
        """
        labels = [self.time_label]
        if self.HAS_SPECIES and self.HAS_TIME:
            output = np.hstack((self.time, self.species))
            labels += self.species_labels
        if self.HAS_PROPENSITIES:
            output = np.hstack((output, self.propensities))
            labels += self.propensities_labels
        if self.HAS_XDATA:
            output = np.hstack((output, self.xdata))
            labels += self.xdata_labels
        if not lbls:
            return output
        else:
            return output, labels

    def getSimData(self, *args, **kwargs):
        """
        Feed this method species/xdata labels and it will return an array of [time, sp1, ....]

        Input:
         - 'speces_l', 'xdatal' ...
         - *lbls* [default=False] return only the data array or (data array, list of labels)
        """
        output = self.time

        if kwargs.has_key('lbls'):
            lbls = kwargs['lbls']
        else:
            lbls = False
        lout = [self.time_label]
        for roc in args:
            if self.HAS_SPECIES and roc in self.species_labels:
                lout.append(roc)
                output = np.hstack((output, self.species.take([self.species_labels.index(roc)], axis=-1)))
            if self.HAS_PROPENSITIES and roc in self.propensities_labels:
                lout.append(roc)
                output = np.hstack((output, self.propensities.take([self.propensities_labels.index(roc)], axis=-1)))
            if self.HAS_XDATA and roc in self.xdata_labels:
                lout.append(roc)
                output = np.hstack((output, self.xdata.take([self.xdata_labels.index(roc)], axis=-1)))
        if not lbls:
            return output
        else:
            return output, lout
