 #! /usr/bin/env python
"""
Stochastic Simulation Module
============================

The main module of StochPy

Written by T.R. Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: Augustus 21, 2013
"""
############################ IMPORTS ################################

import sys,copy,time,os,cPickle,subprocess,bisect,cStringIO,math

try: 
    import numpy as np  
except ImportError:
    print("Make sure that the NumPy module is installed")
    print("This program does not work without NumPy")
    print("See http://numpy.scipy.org/ for more information about NumPy")
    sys.exit()

import stochpy.modules.Analysis as Analysis
from stochpy.modules.PyscesMiniModel import RegularGridDataObj
from stochpy.modules.PyscesMiniModel import IntegrationStochasticDataObj
import stochpy.implementations

try: 
    import stochpy.modules.InterfaceCain as InterfaceCain    
    IS_STOCHPY_CAIN = True
except ImportError: 
    IS_STOCHPY_CAIN = False

try: 
    import stochpy.modules.InterfaceStochKit as InterfaceStochKit
    import PSC2StochkitXML
    InterfaceStochKit.DeleteExistingData()
    IS_STOCHPY_KIT = True
except ImportError:
    IS_STOCHPY_KIT = False

class SSASettings():
    """   
    Input:
     - *X_matrix* (array)
     - *timesteps* (integer)
     - *starttime* (float)
     - *endtime* (float)
     - *istrackpropensities* (boolean)
    """
    def __init__(self,X_matrix,timesteps,starttime,endtime,istrackpropensities):
        self.X_matrix = X_matrix
        self.timesteps = timesteps
        self.starttime = starttime
        self.endtime = endtime
        self.IsTrackPropensities = istrackpropensities

############################ END IMPORTS ############################

class SSA():
  """
  SSA(Method='Direct', File=None, dir=None, Mode='steps', End=1000, Trajectories=1, IsTrackPropensities=False)
  
  Input options:
   - *Method* [default = 'Direct'], Available methods: 'Direct', 'FirstReactionMethod','TauLeaping','Next Reaction Method'
   - *File* [default = ImmigrationDeath.psc]
   - *dir* [default = /home/user/stochpy/pscmodels/ImmigrationDeath.psc]
   - *Mode* [default = 'steps'] simulation for a total number of 'steps' or until a certain end 'time' (string)
   - *End* [default = 1000] end of the simulation (number of steps or end time)   (float)   
   - *Trajectories* [default = 1] (integer)   
   - *TrackPropensities* [default = False] (boolean)
  
  Usage (with High-level functions):
  >>> smod = stochpy.SSA()
  >>> help(smod)
  >>> smod.Model(File = 'filename.psc', dir = '/.../')
  >>> smod.Method('Direct')
  >>> smod.Reload()
  >>> smod.Trajectories(3)
  >>> smod.Timesteps(10000)
  >>> smod.DoStochSim()
  >>> smod.DoStochSim(end=1000,mode='steps',trajectories=5,method='Direct',IsTrackPropensities=True)
  >>> smod.PlotSpeciesTimeSeries()
  >>> smod.PlotPropensitiesTimeSeries()
  >>> smod.PlotAverageSpeciesTimeSeries()
  >>> smod.PlotWaitingtimesDistributions()
  >>> smod.PlotSpeciesDistributions(bin_size = 3)
  >>> smod.PrintSpeciesMeans()
  >>> smod.PrintSpeciesDeviations()
  >>> smod.PrintPropensitiesMeans()
  >>> smod.ShowOverview()
  >>> smod.ShowSpecies()
  >>> smod.DoTestsuite()
  """
  def __init__(self,Method='Direct',File=None,dir=None,Mode='steps',End=1000,Trajectories=1,IsTrackPropensities=False):
    if os.sys.platform != 'win32':
        output_dir = os.path.join(os.path.expanduser('~'),'Stochpy',)
        temp_dir = os.path.join(os.path.expanduser('~'),'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'
    else:
        output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
        temp_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'
    
    self.model_file = File
    self.model_dir = dir
    self.output_dir = output_dir
    self.temp_dir = temp_dir
    self.Method(Method)
    self.sim_end = End
    self.sim_mode = Mode
    self.sim_trajectories = Trajectories    
    self.IsTrackPropensities = IsTrackPropensities
    self.IsSimulationDone = False # TODO   
    self.IsFixedIntervalMethod = False # TODO   
    self.HAS_AVERAGE = False # TODO    
    self.sim_dump = []
    try: 
        Analysis.plt.ion()   # Set on interactive pylab environment
    except Exception,er:
        print(er)
            
  def Method(self,method):
    """
    Method(method)
    
    Input:
     - *method* (string)

    Select one of the following four methods:    
     - *Direct*
     - *FirstReactionMethod*
     - *NextReactionMethod*
     - *TauLeaping*
     
    Note: input must be a string --> 'Direct' (not case sensitive)
    """
    self.IsTauLeaping = False
    IsNRM = False
    if method.lower() == 'direct':
        import stochpy.implementations.DirectMethod as DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        print("Info: Direct method is selected to perform stochastic simulations")
        self.sim_method_name = "Direct"
    elif method.lower() == 'firstreactionmethod':
        import stochpy.implementations.FirstReactionMethod as FRM
        self.sim_method = FRM.FirstReactionMethod
        self.sim_method_name = "FirstReactionMethod"
        print("Info: First Reaction method is selected to perform stochastic simulations")
    elif method.lower() == 'tauleaping':
        import stochpy.implementations.TauLeaping as TauLeaping
        self.sim_method = TauLeaping.OTL
        self.sim_method_name = "TauLeaping"
        print("Info: Optimized Tau-Leaping method is selected to perform stochastic simulations")
        print("Info: User can change the 'epsilon' parameter with DoStochSim(epsilon = 0.01)")
        self.IsTauLeaping = True
    elif method.lower() == 'nextreactionmethod':
        import stochpy.implementations.NextReactionMethod as NRM
        self.sim_method = NRM.NextReactionMethod
        print("Info: Next Reaction method is selected to perform stochastic simulations")
        IsNRM = True
        self.sim_method_name = "NextReactionMethod"
    else:
        print("Warning: Only valid options are: 'Direct', 'FirstReactionMethod', 'NextReactionMethod','TauLeaping'.")
        print("Info: By default, the Direct method is selected")
        import stochpy.implementations.DirectMethod as DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        self.sim_method_name = "Direct"

    self.SSA = self.sim_method(self.model_file,self.model_dir,self.output_dir,self.temp_dir)
    self.data_stochsim = IntegrationStochasticDataObj()   
    self.data_stochsim_grid = RegularGridDataObj()   
    self.IsSimulationDone = False    
    self.HAS_AVERAGE = False   
    
  def Timesteps(self,s):
      """
      Timesteps(s)
      
      Set the number of time steps to be generated for each trajectory
      
      Input:
       - *s* (integer)
      """      
      try:
          self.sim_end  = abs(int(s))
          self.sim_mode = 'steps'
          print("Info: The number of time steps is: %s" % self.sim_end)
      except ValueError:
          raise ValueError, "Error: The number of time steps must be an integer"

  def Endtime(self,t):
      """
      Endtime(t)
      
      Set the end time of the exact realization of the Markov jump process
      
      Input:
       - *t* (float)
      """    
      try:
          self.sim_end  = abs(float(t))
          self.sim_mode = 'time'
          print("Info: The simulation end time is: %s" % self.sim_end)
      except ValueError:
          raise ValueError, "Error: The end time must be an integer or a float"

  def Trajectories(self,n):
      """
      Trajectories(n)
      
      Set the number of trajectories to be generated
      
      Input:
       - *n* (integer)
      """
      try:
          self.sim_trajectories = abs(int(n))
      except ValueError:
          raise ValueError, "Error: The number of trajectories must be an integer"

  def Reload(self):
      """ Reload the entire model again. Useful if the model file has changed """
      self.SSA.Parse(self.model_file,self.model_dir)      
      self.model_file = self.SSA.ModelFile 
      self.model_dir = self.SSA.ModelDir
      self.IsSimulationDone = False   
      self.HAS_AVERAGE = False 
      self.data_stochsim = IntegrationStochasticDataObj()       
      self.data_stochsim_grid = RegularGridDataObj()  

  def Model(self,File,dir=None):
      """
      Model(File,dir=None)
      
      Select model for simulation
            
      Input:
       - *File* (string)
       - *dir* [default = None] (string)
      """
      self.model_file = File
      if dir != None: 
          self.model_dir = dir
      self.Reload()

  def Mode(self,sim_mode='steps'):
      """
      Mode(sim_mode='steps')
      
      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *sim_mode* [default = 'steps'] (string) 'time' or 'steps'      
      """
      self.sim_mode = sim_mode.lower()
      if self.sim_mode.lower() not in ['steps','time']:
          print("Mode '%s' not recognized using: 'steps'" % sim_mode)
          self.sim_mode = 'steps'

  def GetTrajectoryData(self,n=1):
      """ 
      GetTrajectryData(n=1)
      
      Switch to another trajectory, by default, the last trajectory is accessible      
      
      Input:
       - *n* [default = 1] (integer)
      """ 
      try:      
          file_in = open(os.path.join(self.temp_dir,'%s%s.dat' % (self.model_file,n)),'r')
          self.data_stochsim = cPickle.load(file_in)
          file_in.close()
      except IOError:
          print("Error: Trajectory %s does not exist" % n)

  def DumpTrajectoryData(self,n):
      """ 
      DumpTrajectoryData(n)
      
      Input:
       - *n* (integer)
      """ 
      try:    
          filename_out = os.path.join(self.temp_dir,'%s%s.dat' % (self.model_file,n))
          self.sim_dump.append(filename_out)
          f = open(filename_out,'wb')
          cPickle.dump(self.data_stochsim,f)         
          f.close()
      except IOError:
          print("Error: Trajectory %s does not exist" % n)
          
  def ChangeParameter(self,parameter,value):
      """
      ChangeParameter(parameter,value)  
      
      Change parameter value   
      
      Input:
       - *parameter* (string)
       - *value* (float)
      """
      IsKeyError = False
      if type(parameter) == str and (type(value) == float or type(value) == int or type(value) == np.float64 or type(value) == np.float32):   
          try:
              self.SSA.parse.Mod.__pDict__[parameter]['initial'] = float(value)               
          except KeyError:              
              print("Error: Parameters are: %s" % (sorted(self.SSA.parse.Mod.__pDict__)))
              IsKeyError = True
          if not IsKeyError:    
              self.SSA.parse.BuildReactions()
              self.SSA.propensities = copy.deepcopy(self.SSA.parse.propensities)                    
      else:
          print("Error: arguments parameter = string and value = float")  

  def ChangeInitialSpeciesAmount(self,species,value):
      """
      ChangeInitialSpeciesAmount(species,value)     
      
      Change initial species Amount
      
      Input:
       - *species* (string)
       - *value* (float)
      """
      IsKeyError = False
      if (type(species) == str) and (type(value) == float or type(value) == int or type(value) == np.float64 or type(value) == np.float32):   
          try:
              self.SSA.parse.Mod.__sDict__[species]['initial'] = float(value)
          except KeyError:     
              print("Error: Species are: %s" % (sorted(self.SSA.parse.Mod.__sDict__)))
              IsKeyError = True              
          if not IsKeyError:
              if  self.SSA.parse.Mod.__sDict__[species]['fixed']: # rebuild reactions and propensities
                  self.SSA.parse.BuildReactions()
                  self.SSA.propensities = copy.deepcopy(self.SSA.parse.propensities)
              self.SSA.parse.BuildX()     
              self.SSA.X_matrixinit = copy.deepcopy(self.SSA.parse.X_matrix.transpose()[0])
      else:
          print("Error: species argument must be a string and value argument must be a float or integer") 
  
      
  def DoStochKitStochSim(self,endtime=100,frames=10000,trajectories=False,IsTrackPropensities=False,customized_reactions=None,solver=None,keep_stats = False,keep_histograms = False):
      """
      DoStochKitStochSim(endtime=100,frames=10000,trajectories=False,IsTrackPropensities=False,customized_reactions=None,solver=None,keep_stats = False,keep_histograms = False)
      
      Do Stochastic simulations with StochKit in StochPy
      Make sure that the input file contains net stoichiometric coefficients
      
      Input:
       - *endtime* [default = 100] (float)
       - *frames* [default = 10000] (integer)
       - *trajectories* [default = False] (integer)
       - *IsTrackPropensities* [default = False] (boolean)
       - *customized_reactions* [default=None] (list of strings)
       - *solver* [default = None] (string)
       - *keep_states* [default = False] (boolean)
       - *keep_histograms* [default = False) (boolean)
      """
      assert IS_STOCHPY_KIT,"Error: StochKit and/or InterfaceStochKit is not installed or the directories in InterfaceStochKit.ini are incorrect"         
      
      if IS_STOCHPY_KIT:      
          try: 
              self.DeleteTempfiles() # Delete '.dat' files
          except:
              pass                   # no '.dat' files to delete          
          
          print("Warning: Do not use net stoichiometric coefficients for fixed-interval output solvers. Use X > {2}  in stead of $pool > X")
          if type(frames) == int:
              pass
          elif type(frames) == float or type(frames) == np.float64 or type(frames) == np.float32:
              print("Warning: 'frames' must be an integer rather than a float; float %s is rounded to %s" % (frames,int(frames)))
              frames = int(frames) 
          else:
              print("Error: 'frames' must be an integer")
              sys.exit()   
          
          self.data_stochsim = IntegrationStochasticDataObj()
          self.data_stochsim_grid = RegularGridDataObj()  
          
          self.IsFixedIntervalMethod = True
          self.IsSimulationDone = False
          self.IsTrackPropensities = IsTrackPropensities
          self.HAS_AVERAGE = False          
          if trajectories != False:
              self.Trajectories(trajectories)                   
                    
          if customized_reactions != None:
              for r_id in customized_reactions:
                  r_index = self.SSA.rate_names.index(r_id)
                  self.SSA.parse.rate_eqs[r_index]['stochtype'] = 'customized'
                  
          assert not self.SSA.parse.Mod.__HAS_ASSIGNMENTS__, "Error: StochKit solvers do not support assignments. Use the StochPy solvers DoStochSim()"          
 
          if solver == None:                  
              solver = InterfaceStochKit.STOCHKIT_SOLVER # use the default solver
          
          t1 = time.time()
          stochkit_model_filename = self.model_file.split('.')[0]+'_stochkit.xml'
          doc = PSC2StochkitXML.xml_createStochKitDoc(self.SSA)
          PSC2StochkitXML.xml_viewStochKitXML(doc,fname=os.path.join(self.temp_dir,stochkit_model_filename))          
          stochkit_model_filename_path = os.path.join(self.temp_dir, stochkit_model_filename)            
          stochkit_keep_stats = keep_stats
          stochkit_keep_histograms = keep_histograms
          stochkit_keep_trajectories = True
          stochkit_cmd = "-m %s -t%s -r%s -i%s --label -f" % (stochkit_model_filename_path,endtime,self.sim_trajectories ,frames)
          if not stochkit_keep_stats:
              stochkit_cmd += " --no-stats"
          if stochkit_keep_histograms:
              stochkit_cmd += " --keep-histograms"
          if stochkit_keep_trajectories:
              stochkit_cmd += " --keep-trajectories"
          stochkit_cmd += " --out-dir %s" % (os.path.join(InterfaceStochKit.STOCHKIT_WORK_DIR,stochkit_model_filename))
          
          if self.sim_trajectories == 1:                  
              print("Info: %s trajectory is generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames))
          else:                  
              print("Info: %s trajectory are generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames))    
          try: 
              solver_path = os.path.join(InterfaceStochKit.STOCHKIT_SOLVER_DIR, solver)
              rcode = subprocess.call([solver_path, stochkit_cmd]) 
              IsSimulation = True
          except Exception,er:
              print(er)
              print(solver_path)
              IsSimulation = False
                                   
          if IsSimulation:    
              t2 = time.time()    
              self.simulation_time = t2-t1              
              print("Info: Simulation time including compiling %s" % self.simulation_time)
              if self.IsTrackPropensities:
                  print("Info: Parsing data to StochPy and calculating propensities and distributions ...")
              else:
                  print("Info: Parsing data to StochPy and calculating distributions ...")
              self.data_stochsim = InterfaceStochKit.GetStochKitOutput(stochkit_model_filename,self.SSA,endtime,self.sim_trajectories,frames,self.IsTrackPropensities)              
              self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
              try:
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
              except:
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
              self.IsSimulationDone = True
              print("Info: Data successfully parsed into StochPy")
     
  def DoCainStochSim(self,endtime=100,frames=10000,trajectories=False,solver="HomogeneousDirect2DSearch",IsTrackPropensities=False):
      """      
      DoCainStochSim(endtime=100,frames=10000,trajectories=False,solver="HomogeneousDirect2DSearch",IsTrackPropensities=False)
      
      Use Cain implementations for fixed-interval output stochastic simulations (www.cacr.caltech.edu/~sean/cain/DeveloperFile)
      Make sure that the input file contains net stoichiometric coefficients
      
      Input:
       - *endtime* [default = 100](float)
       - *frames* [default = 10000] (integer)
       - *trajectories* [default = False] (integer)
       - *solver* [default = HomogeneousDirect2DSearch] (string)
       - *IsTrackPropensities* [default = False] (boolean)
      """     
      assert IS_STOCHPY_CAIN, "Error: InterfaceCain is not installed"      
      if IS_STOCHPY_CAIN:
          print("Warning: Only mass-action kinetics can be correctly parsed by the Cain solvers")
          try:
              self.DeleteTempfiles() # Delete '.dat' files
          except:
              pass
          print("Warning: Do not use net stoichiometric coefficients for fixed-interval output solvers. Use X > {2} in stead of $pool > X")
          if type(frames) == int:
              pass
          elif type(frames) == float or type(frames) == np.float64 or type(frames) == np.float32:
              print("Warning: 'frames' must be an integer rather than a float; float %s is rounded to %s" % (frames,int(frames)))
              frames = int(frames) 
          else:
              print("Error: 'frames' must be an integer")
              sys.exit()             

          self.data_stochsim = IntegrationStochasticDataObj()
          self.data_stochsim_grid = RegularGridDataObj()         
      
          self.IsFixedIntervalMethod = True
          self.IsTrackPropensities = IsTrackPropensities
          self.HAS_AVERAGE = False  
          self.IsSimulationDone = False          
          if trajectories != False:
              self.Trajectories(trajectories)
                    
          assert not self.SSA.parse.Mod.__HAS_EVENTS__, "Error: Cain solvers do not support events. Use the StochPy solvers DoStochSim()"               
          assert not self.SSA.parse.Mod.__HAS_ASSIGNMENTS__, "Error: Cain solvers do not support assignments. Use the StochPy solvers DoStochSim()"
          ### Parse model to CAIN ###
          mersenne_twister_data = InterfaceCain.getCainInputfile(self.SSA,endtime,frames,self.sim_trajectories)            
          cain_cmd_filename = 'cain_in.txt'
          cmd_file = open(os.path.join(self.temp_dir, cain_cmd_filename), 'r')
          cain_cmd = cmd_file.read()
          cmd_file.close()
          ###########################
          
          try:
              if (os.sys.platform == 'win32') and (not solver.endswith('.exe')):
                  solver = solver.split('.')[0] + '.exe'                 
              solver_path = os.path.join(InterfaceCain.CAIN_SOLVER_PATH,solver)  
              proc = subprocess.Popen(os.path.join(InterfaceCain.CAIN_SOLVER_PATH,solver),stdin=subprocess.PIPE,stdout=subprocess.PIPE) 
              IsFoundSolver = True
          except Exception,er:
              print(er)
              print(solver_path)
              IsFoundSolver = False    
          
          if IsFoundSolver:
              if self.sim_trajectories == 1:                  
                  print("Info: %s trajectory is generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames))
              else:                  
                  print("Info: %s trajectory are generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames))
              t1 = time.time()     
              stdout_values = proc.communicate(cain_cmd)[0]              
              t2 = time.time() 
              self.simulation_time = t2-t1            
              print("Info: Simulation time %s" % self.simulation_time)
              if self.IsTrackPropensities:
                  print("Info: Parsing data to StochPy and calculating propensities and distributions ...")
              else:
                  print("Info: Parsing data to StochPy and calculating distributions ...")
                      
              self.data_stochsim = InterfaceCain.getCainOutput2StochPy(cStringIO.StringIO(stdout_values).readlines() ,mersenne_twister_data,self.SSA,endtime,self.sim_trajectories,frames,self.IsTrackPropensities)              
              self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
              try: 
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
              except:
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
              self.IsSimulationDone = True
              print("Info: Data successfully parsed into StochPy")
  
  def DoStochSim(self,end=False,mode=False,method=False,trajectories=False,epsilon = 0.03,IsTrackPropensities=False):
      """
      DoStochSim(end=10, mode='steps', method='Direct', trajectories=1, epsilon=0.03,IsTrackPropensities=False)

      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *end* [default=1000] simulation end (steps or time)
       - *mode* [default='steps'] simulation mode, can be one of:
         - *steps* (string) total number of steps to simulate
         - *time* (string) simulate until time is reached
       - *method* [default='Direct'] stochastic algorithm, can be one of:
         - Direct
         - FirstReactionMethod
         - NextReactionMethod
         - TauLeaping
       - *trajectories* [default = 1] number of trajectories
       - *epsilon* [default = 0.03] parameter for Tau-Leaping
       - *IsTrackPropensities* [default = False]
      """
      if mode != False:         
          self.Mode(sim_mode = mode)         
      if end != False:    
          if (type(end) == int) or (type(end) == float) or (type(end) == np.float64): 
              self.sim_end = end      
          else:
              print("Warning: 'end' should be an integer or float\n 1000 is used by default")
              self.sim_end = 1000   

      self.data_stochsim = IntegrationStochasticDataObj()
      self.data_stochsim_grid = RegularGridDataObj()  
          
      if method != False: 
          self.Method(method)
      if trajectories != False: 
          self.Trajectories(trajectories)
      self.IsTrackPropensities = IsTrackPropensities
      self.IsFixedIntervalMethod = False      
      self.HAS_AVERAGE = False      
      try: 
          self.DeleteTempfiles()  # Delete '.dat' files
      except:
          pass                    # No '.dat' files to delete
    
      if self.sim_trajectories == 1:
          print("Info: 1 trajectory is generated")
      else:      
          print("Info: %s trajectories are generated"  % self.sim_trajectories)
          print("Info: Time simulation output of the trajectories is stored at %s in directory: %s" % (self.model_file[:-4]+'(trajectory).dat',self.temp_dir))
      t1 = time.time()
      for self.current_trajectory in xrange(1,self.sim_trajectories+1):
          if self.sim_method_name == "TauLeaping":
              if self.sim_mode == 'time':
                  self.settings = SSASettings(self.SSA.X_matrixinit,10**10,0,self.sim_end,self.IsTrackPropensities)
                  self.SSA.Execute(self.settings,epsilon)
              elif self.sim_mode == 'steps':
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)  
                  self.SSA.Execute(self.settings,epsilon)
              else:
                  print("Warning: Simulation mode should be 'time' or 'steps'. Steps is done by default")
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)  
                  self.SSA.Execute(self.settings,epsilon)
          else:
              if self.sim_mode == 'time':
                  self.settings = SSASettings(self.SSA.X_matrixinit,10**10,0,self.sim_end,self.IsTrackPropensities)
                  self.SSA.Execute(self.settings)
              elif self.sim_mode == 'steps':
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)          
                  self.SSA.Execute(self.settings)
              else:
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)   
                  print("Warning: Simulation mode should be 'time' or 'steps'. Steps is done by default")
                  self.SSA.Execute(self.settings)
          self.data_stochsim = IntegrationStochasticDataObj()           
          self.FillDataStochsim()          
          if self.sim_trajectories == 1:
              print("Info: Number of time steps %s End time %s" % (self.SSA.timestep,self.SSA.sim_t))
          elif self.sim_trajectories > 1:
              self.DumpTrajectoryData(self.current_trajectory)
      t2 = time.time()
      self.simulation_time = t2-t1
      print("Info: Simulation time: %s" % self.simulation_time)
      self.IsSimulationDone = True      
      self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
      try: 
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
      except:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names) 

  def DoCompleteStochSim(self, error = 0.001, size=100000,IsTrackPropensities=False):
      """      
      DoCompleteStochSim(error = 0.001, size=100000,IsTrackPropensities=False)
      
      Do a stochastic simulation until the first four moments converge (in development, beta-status)
      
      Input:
       - *error* maximal allowed error
       - *size* (integer) number of steps before checking the first four moments
       - *IsTrackPropensities* (False)
      """    
      self.Trajectories(1)
      self.IsTrackPropensities = IsTrackPropensities
      self.IsFixedIntervalMethod = False
      self.HAS_AVERAGE = False
      try: 
          self.DeleteTempfiles()    # Delete '.dat' files
      except:
          pass                      # No '.dat' files to delete    
      
      self.current_trajectory = 1
      t1 = time.time()
      self.settings = SSASettings(self.SSA.X_matrixinit,size,0,10**10,self.IsTrackPropensities)          
      self.SSA.Execute(self.settings)      
      (L_probability_mass, D_means, D_stds,D_moments) = Analysis.GetDataDistributions(self.SSA.sim_output,self.SSA.species_names)      
      m1 = [np.array(D_moments[s_id].values()) for s_id in self.SSA.species_names]      
      IsContinue = True
      print('Info: %s time steps simulated' % (size))
      i=1      
      while IsContinue:          
          settings = SSASettings(self.SSA.X_matrix,size*(i+1),self.SSA.sim_t,10**10,self.IsTrackPropensities)          
          self.SSA.Execute(settings)
          (L_probability_mass,D_means,D_stds,D_moments) = Analysis.GetDataDistributions(self.SSA.sim_output,self.SSA.species_names)          
          m2 = [np.array(D_moments[s_id].values()) for s_id in self.SSA.species_names] 
          max_total = 0
          for j in xrange(self.SSA.n_species):                            
              max_s = abs(1-(m2[j]/m1[j])).max()
              if max_s > max_total:
                   max_total = max_s          
          m1 = copy.deepcopy(m2)  
          i+=1
          print('Info: %s time steps simulated' % (i*size))
          if max_total < error:
              IsContinue = False                  
      t2 = time.time()
      self.simulation_time = t2-t1
      print("Info: Simulation time: %s" % self.simulation_time)
      self.FillDataStochsim()
      self.IsSimulationDone = True
      self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
      try: 
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
      except:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)

  def PlotTimeSim(self,n_events2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Species Time Series Plot',xlabel='Time',ylabel='Copy Number'):      
      print '***DEPRECATION WARNING***: This function is replaced by PlotSpeciesTimeSeries()'
      self.PlotSpeciesTimeSeries(n_events2plot,species2plot,linestyle,marker,colors,title,xlabel,ylabel)      

  def PlotPropensities(self,n_events2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Time Series Plot',xlabel='Time',ylabel='Propensity'):    
      print '***DEPRECATION WARNING***: This function is replaced by PlotPropensitiesTimeSeries()'
      self.PlotPropensitiesTimeSeries(n_events2plot,rates2plot,linestyle,marker,colors,title,xlabel,ylabel)

  def PlotWaitingtimes(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Event Waitingtimes Plot',xlabel='Interarrival time t',ylabel='Probability'):
      print '***DEPRECATION WARNING***: This function is replaced by PlotWaitingtimesDistributions()'      
      self.PlotWaitingtimesDistributions(rates2plot,linestyle,marker,colors,title,xlabel,ylabel)
      
  def PlotDistributions(self,species2plot = True, linewidth=1,linestyle = 'dotted',colors=None,title = 'StochPy Species Probability Mass Function',bin_size=1,xlabel='Number of Molecules',ylabel='Probability'):  
      print '***DEPRECATION WARNING***: This function is replaced by PlotSpeciesDistributions()'  
      self.PlotSpeciesDistributions(species2plot,linestyle,linewidth,colors,title,xlabel,ylabel,bin_size)
   
  def GetMeanWaitingtimes(self):
      print '***DEPRECATION WARNING***: This functionality now belongs to GetWaitingtimes()'  
      self.GetWaitingtimes()
      
  def GetInterpolatedData(self,frames=51):
      print '***DEPRECATION WARNING***: This function is replaced by GetRegularGrid()'
      self.GetRegularGrid(frames)
      
  def PlotInterpolatedData(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Time Series Plot (# of trajectories = )',xlabel='Time',ylabel='Copy Number'):      
      print '***DEPRECATION WARNING***: This function is replaced by PlotAverageSpeciesTimeSeries()'
      self.PlotAverageSpeciesTimeSeries(species2plot,linestyle,marker,colors,title,xlabel,ylabel)

  def ShowMeans(self):      
      print '***DEPRECATION WARNING***: This function is replaced by PrintSpeciesMeans()'
      self.PrintSpeciesMeans()

  def ShowStandardDeviations(self):
      """ Print the standard deviations of each species for the selected trajectory"""  
      print '***DEPRECATION WARNING***: This function is replaced by PrintSpeciesStandardDeviations()'
      self.PrintSpeciesStandardDeviations()
  
  def PrintTimeSim(self):
      print '***DEPRECATION WARNING***: This function is replaced by PrintSpeciesTimeSeries()'
      self.PrintSpeciesTimeSeries()
  
  def PrintPropensities(self):
      print '***DEPRECATION WARNING***: This function is replaced by PrintPropensitiesTimeSeries()'
      self.PrintPropensitiesTimeSeries()
      
  def PrintDistributions(self):
      print '***DEPRECATION WARNING***: This function is replaced by PrintSpeciesDistributions()'
      self.PrintSpeciesDistributions()  

  def PrintWaitingtimes(self):
      print '***DEPRECATION WARNING***: This function is replaced by PrintWaitingtimesDistributions()'
      self.PrintWaitingtimesDistributions()  

  def PrintMeanWaitingtimes(self):
      print '***DEPRECATION WARNING***: This function is replaced by PrintWaitingtimesMeans()'
      self.PrintWaitingtimesMeans()  

  def PrintInterpolatedData(self): 
      print '***DEPRECATION WARNING***: This function is replaced by PrintAverageSpeciesTimeSeries()'
      self.PrintAverageSpeciesTimeSeries()  
            
  def PlotSpeciesTimeSeries(self,n_events2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Species Time Series Plot',xlabel='Time',ylabel='Copy Number',IsLegend=True):
      """
      PlotSpeciesTimeSeries(n_events2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Species Time Series Plot')
      
      Plot time simulation output for each generated trajectory
      Default: PlotSpeciesTimeSeries() plots time simulation for each species

      Input:
       - *n_events2plot* [default = 10000] (integer)
       - *species2plot* [default = True] as a list ['S1','S2'] 
       - *linestyle* [default = 'solid'] dashed, solid, and dash_dot (string)
       - *marker* [default = ''] ('v','o','s',',','*','.')
       - *title* [default = 'StochPy Species Time Series Plot']  (string)
       - *xlabel* [default = 'Time'] (string)
       - *ylabel* [default = 'Copy Number'] (string)
       - *IsLegend* [default = True] (boolean)
      """      
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"
      assert self.IsSimulationDone, "Error: Before plotting time simulation results first do a stochastic simulation"
         
      if species2plot == True:
          species2plot =self.SSA.species_names
      if type(species2plot) == str:
          species2plot = [species2plot]    
      for s_id in species2plot:          
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % s_id              
                    
      if str(n_events2plot).lower() == 'all':
              n_events2plot = self.data_stochsim.simulation_timesteps
      
      i=1
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          self.plot.TimeSeries(self.data_stochsim.getSpecies(),n_events2plot,species2plot,self.data_stochsim.species_labels,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend) # Plot time sim
          i+=1      
      self.plot.plotnum+=1


  def PlotPropensitiesTimeSeries(self,n_events2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Time Series Plot',xlabel='Time',ylabel='Propensity',IsLegend=True):
      """
      PlotPropensitiesTimeSeries(n_events2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Time Series Plot')
      
      Plot time simulation output for each generated trajectory

      Default: PlotPropensitiesTimeSeries() plots propensities for each species

      Input:
       - *n_events2plot* [default = 10000] (integer)
       - *rates2plot* [default = True]: species as a list ['S1','S2']
       - *marker* [default = ''] ('v','o','s',',','*','.')
       - *linestyle* [default = 'solid']: dashed, dotted, and solid (string)
       - *colors* [default = None] (list)
       - *title* [default = 'StochPy Propensities Time Series Plot'] (string)
       - *xlabel* [default = 'Time'] (string)
       - *ylabel* [default = 'Propensity'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"
      assert self.IsSimulationDone and self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
          
      if rates2plot  == True:
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]    
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % r_id                  
      
      if str(n_events2plot).lower() == 'all':
          n_events2plot = self.data_stochsim.simulation_timesteps
          
      i=1      
      while (i <= self.n_trajectories_simulated):
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          self.plot.TimeSeries(self.data_stochsim.getPropensities(),n_events2plot,rates2plot,self.SSA.rate_names,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1
      self.plot.plotnum+=1

  def PlotSpeciesDistributions(self,species2plot = True, linestyle = 'dotted',linewidth = 1,colors=None,title = 'StochPy Species Probability Mass Function',xlabel='Number of Molecules',ylabel='Probability',IsLegend=True,bin_size=1):  
      """
      PlotDistributions(species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Species Probability Mass Function',bin_size=1)
      
      Plots the PDF for each generated trajectory
      Default: PlotDistributions() plots PDF for each species

      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] (string)
       - *colors* (list)
       - *title* [default = 'StochPy Species Probability Mass Function'] (string)     
       - *xlabel* [default = 'Number of Molecules'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
       - *bin_size* [default=None] (integer)
      """       
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"
      assert self.IsSimulationDone, "Error: Before plotting species distributions first do a stochastic simulation"
      
      if species2plot == True:
          species2plot = self.SSA.species_names
      if type(species2plot) == str: 
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % s_id    
      
      i=1
      while i <= self.n_trajectories_simulated:    
          if self.sim_trajectories > 1:
              file_in = open(os.path.join(self.temp_dir,'%s%s.dat' % (self.model_file,i)),'r')	# Open dumped output
              self.data_stochsim = cPickle.load(file_in)
              file_in.close()
          self.plot.Distributions(self.data_stochsim.species_distributions,species2plot,self.data_stochsim.species_labels,i-1,linestyle,linewidth,colors,title,xlabel,ylabel,IsLegend,bin_size)
          i+=1          
      self.plot.plotnum += 1
      
              
  def PlotPropensitiesDistributions(self,rates2plot = True, linestyle = 'dotted',linewidth = 1,colors=None,title = 'StochPy Propensities Probability Mass Function',xlabel='Propensity',ylabel='Probability',IsLegend=True,bin_size=1):
      """
      PlotDistributions(species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Propensities Probability Mass Function',bin_size=None)
      
      Plots the PDF for each generated trajectory

      Default: PlotDistributions() plots PDF for each species

      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] (string)
       - *colors* (list)
       - *title* [default = 'StochPy Propensities Probability Mass Function'] (string)     
       - *xlabel* [default = 'Propensity'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
       - *bin_size* [default=1] (integer)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"
      assert self.IsSimulationDone and self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"  
      if rates2plot  == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
              rates2plot = [rates2plot]
      for r_id in rates2plot:
           assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % r_id           
      
      i=1
      while i <= self.n_trajectories_simulated:    
          if self.sim_trajectories > 1:
              file_in = open(os.path.join(self.temp_dir,'%s%s.dat' % (self.model_file,i)),'r')	# Open dumped output
              self.data_stochsim = cPickle.load(file_in)
              file_in.close()
          self.plot.Distributions(self.data_stochsim.propensities_distributions,rates2plot,self.SSA.rate_names,i-1,linestyle,linewidth,colors,title,xlabel,ylabel,IsLegend,bin_size) # Plot dist
          i+=1      
      self.plot.plotnum += 1
      
      
  def GetWaitingtimes(self):
      """ Get for each reaction the waiting times """      
      assert self.IsSimulationDone, "Error: Before getting waiting times first do a stochastic simulation (and do not use the Tau-Leaping method)"         
      assert not self.IsTauLeaping, "Error: Tau-Leaping method does not allow for calculation of waiting times"          
      assert not self.IsFixedIntervalMethod, "Error: Fixed-interval output solvers do not allow for calculation of waiting times"
      
      i=1
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          D_waitingtimes = Analysis.ObtainWaitingtimes(self.data_stochsim,self.SSA.rate_names)
          self.data_stochsim.setWaitingtimes(D_waitingtimes,self.SSA.rate_names)
          self.data_stochsim.setWaitingtimesMeans(self.data_stochsim.waiting_times,self.SSA.rate_names)        
          self.data_stochsim.setWaitingtimesStandardDeviations(self.data_stochsim.waiting_times,self.SSA.rate_names)
          if self.n_trajectories_simulated > 1:
              self.DumpTrajectoryData(i)           
          i+=1
    
  def PlotWaitingtimesDistributions(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Event Waiting times Plot',xlabel=r'inter-event time $t$',ylabel='Probability',IsLegend=True):
      """
      PlotWaitingtimesDistributions(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Waiting times Plot',xlabel='inter-event time t',ylabel='Probability')
      
      Plot event waiting time distributions
      
      default: PlotWaitingtimesDistributions() plots waiting times for all rates
    
      Input:
       - *rates2plot* [default = True]  as a list of strings ["R1","R2"]
       - *linestyle* [default = 'None'] dashed, dotted, dash_dot, and solid (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Event Waiting times Plot'] (string)
       - *xlabel* [default = 'inter-event time t'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
      """    
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"
      assert not self.IsTauLeaping, "Error: Tau-Leaping method does not allow for calculation of waiting times"
      
      if (not self.data_stochsim.HAS_WAITING_TIMES) and (not self.IsTauLeaping):
          self.GetWaitingtimes()
      if rates2plot == True:
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Reaction %s is not in the model" % r_id
      i=1
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          self.plot.WaitingtimesDistributions(self.data_stochsim.waiting_times,rates2plot,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1
      self.plot.plotnum+=1
              
  def GetRegularGrid(self,npoints=True):
      """
      GetRegularGrid(npoints=True)
      
      The Gillespie method generates data at irregular time points. However, it is possible to output data on a fixed regular time grid where the user can specify the resolution of the grid (npoints).  
     
      Input:
       - *npoints* [default = True] (integer)
      """
      assert self.IsSimulationDone, "Error: Before getting average data on a regular grid first do a stochastic simulation"            
      if npoints == True:
          npoints = int(self.data_stochsim.simulation_endtime+1)          
      if type(npoints) == int:
          pass
      elif type(npoints) == float or type(npoints) == np.float64 or type(npoints) == np.float32:
          print("Warning: 'npoints' must be an integer rather than a float; float %s is rounded to %s" % (npoints,int(npoints)))
          npoints = int(npoints)
      else:
          print("Error: Argument of GetRegularGrid() must be an integer")
          sys.exit()          
      
      n_species = len(self.data_stochsim.species_labels)          
      L_species = [[] for i in xrange(n_species)]                
      if self.IsTrackPropensities:
          n_rates = len(self.SSA.rate_names)
          L_propensities = [[] for i in xrange(n_rates)]
          self.data_stochsim_grid.propensities_autocorrelation = [[] for i in xrange(n_rates)]          
      if self.sim_mode == 'time':
          self.data_stochsim_grid.setTime(np.linspace(0,self.sim_end,npoints))
      else: 
          L_simulation_endtimes = []
          i=1
          while i <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              L_simulation_endtimes.append(self.data_stochsim.simulation_endtime)        
              i+=1               
          self.data_stochsim_grid.setTime(np.linspace(0,min(L_simulation_endtimes),npoints))
      i=1
      while i <= self.n_trajectories_simulated:              
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          L_species_grid = np.zeros([len(self.data_stochsim_grid.time),n_species])
          if self.IsTrackPropensities:
              L_propensities_grid = np.zeros([len(self.data_stochsim_grid.time),n_rates])
          j=0
          for time_point in self.data_stochsim_grid.time:
              time_index = bisect.bisect(self.data_stochsim.time,time_point)-1 # last time event before change
              L_species_grid[j] = self.data_stochsim.species[:][time_index]
              if self.IsTrackPropensities:
                  L_propensities_grid[j] = self.data_stochsim.propensities[:][time_index]                  
              j+=1              
          ### Put data in grid files ### 
          for j in xrange(n_species):
              L_species[j].append(L_species_grid[:,j])             
           
          if self.IsTrackPropensities:
              for j in xrange(n_rates):
                  L_propensities[j].append(L_propensities_grid[:,j])                  
          i+=1                       
      self.data_stochsim_grid.setSpecies(L_species)          
      (self.data_stochsim_grid.species_means,self.data_stochsim_grid.species_standard_deviations) = Analysis.GetAverageResults(self.data_stochsim_grid.species)
      if self.IsTrackPropensities:
          self.data_stochsim_grid.setPropensities(L_propensities) 
          (self.data_stochsim_grid.propensities_means,self.data_stochsim_grid.propensities_standard_deviations) = Analysis.GetAverageResults(self.data_stochsim_grid.propensities)
      self.HAS_AVERAGE = True

  def PlotAverageSpeciesTimeSeries(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Time Series Plot (# of trajectories = )',xlabel='Time',ylabel='Copy Number',IsLegend=True,nstd=1): 
      """
      PlotAverageSpeciesTimeSeries(species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Time Series Plot (# of trajectories = )')
      
      Plot the average time simulation result. For each time point, the mean and standard deviation are plotted 
      
      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Time (# of trajectories = ... )' ] (string)
       - *xlabel* [default = 'Time'] (string)
       - *ylabel* [default = 'Copy Number'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"  
      if not self.HAS_AVERAGE: 
          self.GetRegularGrid()
      
      IsPlot = True     
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str: 
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)
              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)      
          
      self.plot.AverageTimeSeries(self.data_stochsim_grid.species_means,self.data_stochsim_grid.species_standard_deviations,
                                   self.data_stochsim_grid.time,nstd,species2plot,self.SSA.species_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1
          
  def PlotAverageSpeciesDistributions(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Distributions Plot (# of trajectories = )',xlabel='Species Amount',ylabel='Probability',IsLegend=True,nstd=1): 
      """
      PlotAverageSpeciesDistributions(species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Distributions Plot (# of trajectories = )')

      Plot the average species distributions For each species Amount, the mean and standard deviation are plotted      

      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Time (# of trajectories = ... )' ] (string)
       - *xlabel* [default = 'Species Amount'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"  
      if not self.data_stochsim_grid.HAS_AVERAGE_SPECIES_DISTRIBUTIONS:
          self.GetAverageSpeciesDistributions()
      
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str: 
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)
              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)

      self.plot.AverageDistributions(self.data_stochsim_grid.species_distributions_means,self.data_stochsim_grid.species_distributions_standard_deviations,nstd,species2plot,
                                     self.SSA.species_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1
           
  def PlotAverageSpeciesDistributionsConfidenceIntervals(self,species2plot=True,colors = None,title = 'StochPy Average Species Distributions Plot (# of trajectories = )',xlabel='Species Amount',ylabel='Probability',IsLegend=True,nstd=1):
      """
      PlotAverageSpeciesDistributionsConfidenceIntervals(species2plot=True,colors = None,title = 'StochPy Average Species Distributions Plot (# of trajectories = )',xlabel='Species Amount',ylabel='Probability',IsLegend=True,nstd=1)
      
      Plot the average species distributions For each species Amount, the mean and standard deviation are plotted      

      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Time (# of trajectories = ... )' ] (string)
       - *xlabel* [default = 'Species Amount'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)      
      """            
      if not self.data_stochsim_grid.HAS_AVERAGE_SPECIES_DISTRIBUTIONS:
          self.GetAverageSpeciesDistributions()
      
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str:
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)             
      
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)
          
      self.plot.AverageDistributionsCI(self.data_stochsim_grid.species_distributions_means,self.data_stochsim_grid.species_distributions_standard_deviations,nstd,species2plot,
                                     self.SSA.species_names,colors,title,xlabel,ylabel,IsLegend)    
      self.plot.plotnum+=1
           
  def PlotAveragePropensitiesDistributionsConfidenceIntervals(self,rates2plot = True,colors = None,title = 'StochPy Average Propensities Distributions Plot (# of trajectories = )',xlabel='Propensity',ylabel='Probability',IsLegend=True,nstd=1):
      """
      PlotAveragePropensitiesDistributionsConfidenceIntervals(rates2plot = True,colors = None,title = 'StochPy Average Propensities Distributions Plot (# of trajectories = )',xlabel='Propensity',ylabel='Probability',IsLegend=True,nstd=1

      Plot the average time simulation result. For each time point, the mean and standard deviation are plotted      

      Input:

       - *rates2plot* [default = True] as a list ['R1','R2']       
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Time (# of trajectories = ... )' ] (string)
       - *xlabel* [default = 'Propensity'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
      """     
      if not self.data_stochsim_grid.HAS_AVERAGE_PROPENSITIES_DISTRIBUTIONS:
          self.GetAveragePropensitiesDistributions()          
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Reaction %s is not in the model" % (r_id)
      
      self.plot.AverageDistributionsCI(self.data_stochsim_grid.propensities_distributions_means,self.data_stochsim_grid.propensities_distributions_standard_deviations,
                                     nstd,rates2plot,self.SSA.rate_names,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1
              
  def PlotAveragePropensitiesDistributions(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Propensities Distributions Plot (# of trajectories = )',xlabel='Propensity',ylabel='Probability',IsLegend=True,nstd=1): 
      """
      PlotAveragePropensitiesDistributions(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Time Series Plot (# of trajectories = )')

      Plot the average time simulation result. For each time point, the mean and standard deviation are plotted      

      Input:

       - *rates2plot* [default = True] as a list ['R1','R2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Time (# of trajectories = ... )' ] (string)
       - *xlabel* [default = 'Propensity'] (string)
       - *ylabel* [default = 'Probability'] (string)
       - *IsLegend* [default = True] (boolean)
      """  
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"  
      if not self.data_stochsim_grid.HAS_AVERAGE_PROPENSITIES_DISTRIBUTIONS:
          self.GetAveragePropensitiesDistributions()
       
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str: 
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Reaction %s is not in the model" % (r_id)
              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)

      self.plot.AverageDistributions(self.data_stochsim_grid.propensities_distributions_means,self.data_stochsim_grid.propensities_distributions_standard_deviations,
                                     nstd,rates2plot,self.SSA.rate_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1 
          
  def PlotAveragePropensitiesTimeSeries(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Propensities Time Series Plot (# of trajectories = )',xlabel='Time',ylabel='Propensity',IsLegend=True,nstd=1): 
      """
      PlotAveragePropensitiesTimeSeries(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Propensities Time Series Plot (# of trajectories = )')
      
      Plot the average propensities For each time point, the mean and standard deviation are plotted 
      
      Input:
       - *rates2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Propensities Plot (# of trajectories = ...)' ] (string)
       - *xlabel* [default = 'Time'] (string)
       - *ylabel* [default = 'Propensity'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"       
      assert self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
      if (not self.HAS_AVERAGE) and (self.IsTrackPropensities): 
          self.GetRegularGrid()      
          
      if rates2plot == True:
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str: 
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Reaction %s is not in the model" % r_id
              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)

      self.plot.AverageTimeSeries(self.data_stochsim_grid.propensities_means,self.data_stochsim_grid.propensities_standard_deviations,
                                   self.data_stochsim_grid.time,nstd,rates2plot,self.SSA.rate_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1  
          
  def GetAverageSpeciesDistributions(self):
      """ Get average species distributions """      
      assert self.IsSimulationDone, "Error: Before getting average species distributions first do a stochastic simulation."         
      i=1
      D_distributions = {}
      for s_id in self.SSA.species_names:
          D_distributions[s_id] = {}
      L_distributions_means = []
      L_distributions_standard_deviations = []
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)        
          for j in xrange(len(self.SSA.species_names)):
              s_id = self.SSA.species_names[j]
              k=0
              for s_Amount in sorted(self.data_stochsim.species_distributions[j][0]):
                  if not s_Amount in sorted(D_distributions[s_id]):
                      D_distributions[s_id][s_Amount] = []
                  D_distributions[s_id][s_Amount].append(self.data_stochsim.species_distributions[j][1][k])
                  k+=1
          i+=1
          
      for s_id in self.SSA.species_names:
          L_Amount = sorted(D_distributions[s_id])  # for a given species 
          L_means = []
          L_stds = []   
          for s_Amount in L_Amount:
              while len(D_distributions[s_id][s_Amount]) < (i-1):
                  D_distributions[s_id][s_Amount].append(0)
              L_means.append(np.mean(D_distributions[s_id][s_Amount]))
              L_stds.append(np.std(D_distributions[s_id][s_Amount]))    
          L_distributions_means.append([L_Amount,L_means]) 
          L_distributions_standard_deviations.append([L_Amount,L_stds])
      self.data_stochsim_grid.setSpeciesDistributionAverage(L_distributions_means,L_distributions_standard_deviations)          
      
  def GetAveragePropensitiesDistributions(self):
      """ Get average propensities distributions """
      assert (self.IsSimulationDone and self.IsTrackPropensities), "Error: Before getting average propensities distributions first do a stochastic simulation (use the IsTrackPropensities flag in DoStochSim)."          
      i=1
      D_distributions = {}
      for r_id in self.SSA.rate_names:
          D_distributions[r_id] = {}
      L_distributions_means = []
      L_distributions_standard_deviations = []
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)        
          for j in xrange(len(self.SSA.rate_names)):
              r_id = self.SSA.rate_names[j]
              k=0
              for r_prop in sorted(self.data_stochsim.propensities_distributions[j][0]):
                  if not r_prop in sorted(D_distributions[r_id]): 
                      D_distributions[r_id][r_prop] = []
                  D_distributions[r_id][r_prop].append(self.data_stochsim.propensities_distributions[j][1][k])            
                  k+=1              
          i+=1
      for r_id in self.SSA.rate_names:
          L_propensities = sorted(D_distributions[r_id])  # for a given species 
          L_means = []
          L_stds = []   
          for r_prop in L_propensities:
              while len(D_distributions[r_id][r_prop]) < (i-1):
                  D_distributions[r_id][r_prop].append(0)
              L_means.append(np.mean(D_distributions[r_id][r_prop]))
              L_stds.append(np.std(D_distributions[r_id][r_prop]))    
          L_distributions_means.append([L_propensities,L_means])
          L_distributions_standard_deviations.append([L_propensities,L_stds])
      self.data_stochsim_grid.setPropensitiesDistributionAverage(L_distributions_means,L_distributions_standard_deviations)
          

  def GetSpeciesAutocorrelations(self,species2calc=True,gridpoints=True):
      """
      GetSpeciesAutocorrelations(pecies2calc=True,nlags=-1,gridpoints=True)
      
      Input:
       - *species2calc* [default = True] as a list ['S1','S2']
       - *gridpoints* (integer)
      """
      self.GetRegularGrid(gridpoints)
      
      IsContinue = True
      if species2calc == True:
          species2calc = self.SSA.species_names
      if type(species2calc) == str:
          species2calc = [species2calc]    
      for s_id in species2calc:
          assert s_id in self.SSA.species_names, "Error: species %s is not in the model" % s_id              
                           
      L_species_autocorrelations = [[] for j in xrange(len(self.data_stochsim.species_labels))]
      i=1
      while (i <= self.n_trajectories_simulated):               
          for s_id in species2calc:                  
              s_index = self.data_stochsim.species_labels.index(s_id)  
              L_species_autocorrelations[s_index].append(Analysis.Autocorrelation(self.data_stochsim_grid.species[s_index][i-1]))  
          i+=1          
      self.data_stochsim_grid.setSpeciesAutocorrelations(L_species_autocorrelations)
      (self.data_stochsim_grid.species_autocorrelations_means,
      self.data_stochsim_grid.species_autocorrelations_standard_deviations) = Analysis.GetAverageResults(L_species_autocorrelations)

  def GetSpeciesAutocovariances(self,species2calc=True,gridpoints=True):
      """
      GetSpeciesAutocovariances(species2calc=True,nlags=-1,gridpoints=True)
      
      Input:
       - *species2calc* [default = True] as a list ['S1','S2']
       - *gridpoints* (integer)
      """
      self.GetRegularGrid(gridpoints)     
      
      IsContinue = True
      if species2calc == True:
          species2calc = self.SSA.species_names
      if type(species2calc) == str:
          species2calc = [species2calc]    
      for s_id in species2calc:
          assert s_id in self.SSA.species_names, "Error: species %s is not in the model" % s_id
                           
      L_species_autocovariances = [[] for j in xrange(len(self.data_stochsim.species_labels))]
      i=1
      while (i <= self.n_trajectories_simulated):               
          for s_id in species2calc:                  
              s_index = self.data_stochsim.species_labels.index(s_id)  
              L_species_autocovariances[s_index].append(Analysis.AutoCov(self.data_stochsim_grid.species[s_index][i-1]))  
          i+=1          
      self.data_stochsim_grid.setSpeciesAutocovariances(L_species_autocovariances)
      (self.data_stochsim_grid.species_autocovariances_means,
      self.data_stochsim_grid.species_autocovariances_standard_deviations) = Analysis.GetAverageResults(L_species_autocovariances)

          
  def GetPropensitiesAutocorrelations(self,rates2calc=True,gridpoints=True):
      """
      GetPropensitiesAutocorrelations(rates2calc=True,gridpoints=True)
      
      Input:
       - *rates2calc* [default = True] as a list ['R1','R2']     
       - *gridpoints* (integer)
      """
      assert self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"           
      
      self.GetRegularGrid(gridpoints)      
      IsContinue = True
      if rates2calc == True:
          rates2calc = self.SSA.rate_names
      if type(rates2calc) == str:
          rates2calc = [rates2calc]    
      for r_id in rates2calc:
          assert r_id in self.SSA.rate_names, "Error: Reaction %s is not in the model" % r_id

      L_Propensities_autocorrelations = [[] for j in xrange(len(self.SSA.rate_names))]
      i=1
      while (i <= self.n_trajectories_simulated):             
          for r_id in rates2calc:
              r_index = self.SSA.rate_names.index(r_id)   
              L_Propensities_autocorrelations[r_index].append(Analysis.Autocorrelation(self.data_stochsim_grid.propensities[r_index][i-1]))
          i+=1         
      self.data_stochsim_grid.setPropensitiesAutocorrelations(L_Propensities_autocorrelations)
      self.data_stochsim_grid.propensities_autocorrelations_means, self.data_stochsim_grid.propensities_autocorrelations_standard_deviations = Analysis.GetAverageResults(self.data_stochsim_grid.propensities_autocorrelations)

  def GetPropensitiesAutocovariances(self,rates2calc=True,gridpoints=True): 
      """
      GetPropensitiesAutocovariances(rates2calc=True,gridpoints=True)

      Input:
       - *rates2calc* [default = True] as a list ['R1','R2']     
       - *gridpoints* (integer)
      """
      assert self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"           
      
      self.GetRegularGrid(gridpoints)      
      IsContinue = True
      if rates2calc == True:
          rates2calc = self.SSA.rate_names
      if type(rates2calc) == str:
          rates2calc = [rates2calc]    
      for r_id in rates2calc:
          assert r_id  in self.SSA.rate_names, "Error: Reaction %s is not in the model" % r_id

      L_Propensities_autocovariances = [[] for j in xrange(len(self.SSA.rate_names))]              
      i=1          
      while (i <= self.n_trajectories_simulated):             
          for r_id in rates2calc:
              r_index = self.SSA.rate_names.index(r_id)   
              L_Propensities_autocovariances[r_index].append(Analysis.Autocorrelation(self.data_stochsim_grid.propensities[r_index][i-1]))
          i+=1         
      self.data_stochsim_grid.setPropensitiesAutocovariances(L_Propensities_autocovariances)
      self.data_stochsim_grid.propensities_autocovariances_means, self.data_stochsim_grid.propensities_autocovariances_standard_deviations = Analysis.GetAverageResults(self.data_stochsim_grid.propensities_autocovariances)
                    
              
  def PlotSpeciesAutocorrelations(self,nlags = -1,species2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True):
      """
      PlotSpeciesAutocorrelations(species2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot',xlabel='Lag',ylabel='Auto-correlation')
      
      Plot species autocorrelations
      
      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Species Autocorrelation Plot'] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_SPECIES_AUTOCORRELATIONS:
          print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetSpeciesAutocorrelations(species2calc=True,gridpoints=True)")
          self.GetSpeciesAutocorrelations(species2calc = species2plot)
      
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str:
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)
              
      i=1
      while i <= self.n_trajectories_simulated:
          self.plot.Autocorrelations(self.data_stochsim_grid.time[0:nlags],zip(*self.data_stochsim_grid.species_autocorrelations)[i-1],
                                     species2plot,self.data_stochsim.species_labels,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1
      self.plot.plotnum+=1
      
  def PlotSpeciesAutocovariances(self,nlags = -1,species2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True):
      """
      PlotSpeciesAutocovariances(species2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot',xlabel='Lag',ylabel='Auto-correlation')
      
      Plot species auto-covariances
      
      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Species Autocorrelation Plot'] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_SPECIES_AUTOCOVARIANCES:
          print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetSpeciesAutocovariances(species2calc=True,gridpoints=True)")
          self.GetSpeciesAutocovariances(species2calc = species2plot)
      
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str:
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)
      i=1
      while i <= self.n_trajectories_simulated:
          self.plot.Autocorrelations(self.data_stochsim_grid.time[0:nlags],zip(*self.data_stochsim_grid.species_autocovariances)[i-1],
                                     species2plot,self.data_stochsim.species_labels,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1
      self.plot.plotnum+=1
         
  def PlotAverageSpeciesAutocorrelations(self,nlags=-1,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Autocorrelation Plot (# of trajectories = )',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True,nstd=1): 
      """
      PlotAverageSpeciesAutocorrelations(species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot (# of trajectories = )')
      
      Plot the average time simulation result. For each time point, the mean and standard deviation are plotted       

      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Average Species Autocorrelation Plot (# of trajectories = ... )' ] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_SPECIES_AUTOCORRELATIONS:
          print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetSpeciesAutocorrelations(species2calc=True,gridpoints=True)")
          self.GetSpeciesAutocorrelations(species2calc = species2plot,gridpoints=self.data_stochsim.simulation_endtime)
    
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str: 
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)
      
      self.plot.AverageTimeSeries(self.data_stochsim_grid.species_autocorrelations_means,self.data_stochsim_grid.species_autocorrelations_standard_deviations,
                                  self.data_stochsim_grid.time[0:nlags],nstd,species2plot,self.SSA.species_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1
      
  def PlotAverageSpeciesAutocovariances(self,nlags=-1,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Average Species Autocorrelation Plot (# of trajectories = )',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True,nstd=1): 
      """
      PlotAverageSpeciesAutocovariances(species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Species Autocorrelation Plot (# of trajectories = )')
      
      Plot the average time simulation result. For each time point, the mean and standard deviation are plotted       

      Input:

       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = 'o'] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)

       - *title* [default = 'StochPy Average Species Autocorrelation Plot (# of trajectories = ... )' ] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_SPECIES_AUTOCOVARIANCES:
          print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetSpeciesAutocovariances(species2calc=True,gridpoints=True)")
          self.GetSpeciesAutocovariances(species2calc = species2plot,gridpoints=self.data_stochsim.simulation_endtime)
    
      if species2plot == True: 
          species2plot = self.SSA.species_names
      if type(species2plot) == str: 
          species2plot = [species2plot]
      for s_id in species2plot:
          assert s_id in self.SSA.species_names, "Error: Species %s is not in the model" % (s_id)              
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)
      
      self.plot.AverageTimeSeries(self.data_stochsim_grid.species_autocovariances_means,self.data_stochsim_grid.species_autocovariances_standard_deviations,
                                  self.data_stochsim_grid.time[0:nlags],nstd,species2plot,self.SSA.species_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1
          
  def PlotPropensitiesAutocorrelations(self,nlags=-1,rates2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True):
      """
      PlotPropensitiesAutocorrelations(rates2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation')
      
      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *rates2plot* [default = True] as a list ['R1','R2']      
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = StochPy Propensities Autocorrelation Plot] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCORRELATIONS:
           print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetPropensitiesAutocorrelations(rates2calc=True,gridpoints=True)")
           self.GetPropensitiesAutocorrelations(rates2calc = rates2plot,gridpoints=self.data_stochsim.simulation_endtime)
           
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % (r_id)
                  
      i=1
      while i <= self.n_trajectories_simulated:
          self.plot.Autocorrelations(self.data_stochsim_grid.time[0:nlags],zip(*self.data_stochsim_grid.propensities_autocorrelations)[i-1],
                                     rates2plot,self.SSA.rate_names,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1              
      self.plot.plotnum+=1  
      
  def PlotPropensitiesAutocovariances(self,nlags=-1,rates2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True):
      """
      PlotPropensitiesAutocovariances(rates2plot=True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation')

      
      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *rates2plot* [default = True] as a list ['R1','R2']      

       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = StochPy Propensities Autocorrelation Plot] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)

       - *IsLegend* [default = True] (boolean)
      """
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"     
      if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCOVARIANCES:
           print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetPropensitiesAutocovariances(rates2calc=True,gridpoints=True)")
           self.GetPropensitiesAutocovariances(rates2calc = rates2plot,gridpoints=self.data_stochsim.simulation_endtime)
           
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % (r_id)
                  
      i=1
      while i <= self.n_trajectories_simulated:
          self.plot.Autocorrelations(self.data_stochsim_grid.time[0:nlags],zip(*self.data_stochsim_grid.propensities_autocovariances)[i-1],
                                     rates2plot,self.SSA.rate_names,i-1,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
          i+=1              
      self.plot.plotnum+=1  

  def PlotAveragePropensitiesAutocorrelations(self,nlags=-1,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot (# of trajectories = )',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True,nstd=1): 
      """
      PlotAveragePropensitiesAutocorrelation(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot (# of trajectories = )'))
      
      Plot the average propensities autocorrelation result for different lags. For each lag, the mean and standard deviation are plotted       

      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *rates2plot* [default = True] as a list ['R1','R2']      
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = StochPy Average Time (# of trajectories = ... ) ] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """  
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"         
      if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCORRELATIONS:
          print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetPropensitiesAutocorrelations(rates2calc=True,gridpoints=True)")
          self.GetPropensitiesAutocorrelations(rates2calc = rates2plot,gridpoints=self.data_stochsim.simulation_endtime)
      
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % (r_id)
                  
      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)      

      self.plot.AverageTimeSeries(self.data_stochsim_grid.propensities_autocorrelations_means,self.data_stochsim_grid.propensities_autocorrelations_standard_deviations,
                                   self.data_stochsim_grid.time[0:nlags],nstd,rates2plot,self.SSA.rate_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1

  def PlotAveragePropensitiesAutocovariances(self,nlags=-1,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot (# of trajectories = )',xlabel=r'Lag ($\tau$)',ylabel='Auto-correlation',IsLegend=True,nstd=1): 
      """
      PlotAveragePropensitiesAutocorrelation(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Propensities Autocorrelation Plot (# of trajectories = )'))
      
      Plot the average propensities autocorrelation result for different lags. For each lag, the mean and standard deviation are plotted       


      Input:
       - *nlags* [default = -1] (integer) 1,2,3 ... -1 where 3 means calculate the autocorrelation for the first 3 lags and -1 for all lags  
       - *rates2plot* [default = True] as a list ['R1','R2']      
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','s',',','*','.')
       - *colors* [default =  None] (list)
       - *title* [default = StochPy Average Time (# of trajectories = ... ) ] (string)
       - *xlabel* [default = r'Lag ($\tau$)'] (string)
       - *ylabel* [default = 'Autocorrelation'] (string)
       - *IsLegend* [default = True] (boolean)
      """  
      assert Analysis.IS_PLOTTING, "Error: Install matplotlib or use Export2file()"         
      if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCOVARIANCES:
          print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetPropensitiesAutocovariances(rates2calc=True,gridpoints=True)")
          self.GetPropensitiesAutocovariances(rates2calc = rates2plot,gridpoints=self.data_stochsim.simulation_endtime)
      
      if rates2plot == True: 
          rates2plot = self.SSA.rate_names
      if type(rates2plot) == str:
          rates2plot = [rates2plot]
      for r_id in rates2plot:
          assert r_id in self.SSA.rate_names, "Error: Species %s is not in the model" % (r_id)                  

      if '(# of trajectories = )' in title:
          title = title.replace('= ','= %s' % self.n_trajectories_simulated)
      self.plot.AverageTimeSeries(self.data_stochsim_grid.propensities_autocovariances_means,self.data_stochsim_grid.propensities_autocovariances_standard_deviations,
                                   self.data_stochsim_grid.time[0:nlags],nstd,rates2plot,self.SSA.rate_names,linestyle,marker,colors,title,xlabel,ylabel,IsLegend)
      self.plot.plotnum+=1

  def PrintSpeciesMeans(self):
      """ Print the means of each species for the selected trajectory"""
      assert self.IsSimulationDone, "Error: Before showing the means, do a stochastic simulation first"      
      print("Species\tMean")
      for s_id in self.data_stochsim.species_labels:         
          print("%s\t%s"  % (s_id,self.data_stochsim.species_means[s_id]))

  def PrintSpeciesStandardDeviations(self):
      """ Print the standard deviations of each species for the selected trajectory"""  
      assert self.IsSimulationDone, "Error: Before showing the standard deviations, do a stochastic simulation first"                
      print("Species\t","Standard Deviation")
      for s_id in self.data_stochsim.species_labels:          
          print("%s\t%s"  % (s_id,self.data_stochsim.species_standard_deviations[s_id]))
              
  def PrintPropensitiesMeans(self): 
      """ Print the means of each propensity for the selected trajectory"""      
      assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before printing propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"      
      print("Reaction\tMean")
      for r_id in self.SSA.rate_names:
          print("%s\t%s"  % (r_id,self.data_stochsim.propensities_means[r_id]))

  def PrintPropensitiesStandardDeviations(self):
      """ Print the standard deviations of each propensity for the selected trajectory"""  
      assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before printing propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"               
      print("Reaction\t","Standard Deviation")
      for r_id in self.SSA.rate_names:         
          print("%s\t%s"  % (r_id,self.data_stochsim.propensities_standard_deviations[r_id]))

  def PrintWaitingtimesMeans(self):
      """ Print the waiting time means for the selected trajectory """      
      assert not self.IsTauLeaping, "Error: Tau-Leaping method does not allow for calculation of waiting times"
      if (not self.data_stochsim.HAS_WAITING_TIMES) and (not self.IsTauLeaping): 
          self.GetWaitingtimes()

      i=1
      while i <= self.n_trajectories_simulated:  
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          print("Reaction\tMean")
          j=0
          for r_id in self.SSA.rate_names: 
              print("%s\t%s" % (r_id,self.data_stochsim.waiting_times_means[j]))
              j+=1
          i+=1
 
  def PrintWaitingtimesStandardDeviations(self):
      """ Print the waiting time standard deviations for the selected trajectory """
      assert not self.IsTauLeaping, "Error: Tau-Leaping method does not allow for calculation of waiting times"    
      if (not self.data_stochsim.HAS_WAITING_TIMES) and (not self.IsTauLeaping): 
          self.GetWaitingtimes()
      i=1
      while i <= self.n_trajectories_simulated:  
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          print("Reaction\tStandard deviation")
          j=0
          for r_id in self.SSA.rate_names: 
              print("%s\t%s" % (r_id,self.data_stochsim.waiting_times_standard_deviations[j]))
              j+=1
          i+=1
   
  def Export2File(self,analysis='timeseries',datatype='species', IsAverage = False, directory=None):      
      """    
      Export2File(analysis='timeseries',datatype='species', IsAverage = False, directory=None)
      
      Write data to a text document     
  
      Input:
       - *analysis* [default = 'timeseries'] (string) options: timeseries, distribution, mean, std, autocorrelation, autocovariance
       - *datatype*  [default = 'species'] (string) options: species, propensities, waitingtimes
       - *IsAverage* [default = False] (boolean)   
       - *directory* [default = None] (string)
      """         
      if directory == None:
          if not IsAverage:
              directory = os.path.join(self.output_dir,"%s_%s_%s" % (self.model_file,datatype,analysis))
          else:
              directory = os.path.join(self.output_dir,"%s_%s_%s_%s" % (self.model_file,"average",datatype,analysis))
      else:
          if not os.path.exists(directory):
              os.makedirs(directory)
          if not IsAverage:
              directory = os.path.join(directory,"%s_%s_%s" % (self.model_file,datatype,analysis))  
          else:
              directory = os.path.join(directory,"%s_%s_%s_%s" % (self.model_file,"average",datatype,analysis))
        
      if  (datatype.lower() == 'species') and (analysis.lower() == 'timeseries') and (not IsAverage):
          assert self.IsSimulationDone, "Error: Before exporting species time series to a file first do a stochastic simulation"          
          i=1
          while i <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)	# Dir/Filename
              file_out = open(file_path,'w')
              file_out.write('Time')
              for s_id in self.SSA.species_names:
                  file_out.write('\t%s' % s_id)
              if len(self.SSA.species_names)+1 < len(self.SSA.sim_output[0]):
                  file_out.write('\tFired Reaction')              
              file_out.write('\n')       
              #for timepoint in self.data_stochsim.getSpecies():                    
              for timepoint in self.SSA.sim_output:
                  slist = [str(value) for value in timepoint]
                  line = "\t".join(slist) 
                  line += '\n'
                  file_out.write(line)
              i+=1
              file_out.close()
              print("Info: Species time series output is successfully saved at: %s" % file_path)
                
      elif (datatype.lower() == 'species') and (analysis.lower() == 'distribution') and (not IsAverage):
          assert self.IsSimulationDone, "Error: Before exporting species time series to a file first do a stochastic simulation"          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              for L_species_dist in self.data_stochsim.species_distributions:
                  file_out.write("Amount\tProbability\n")
                  for j in xrange(len(L_species_dist[0])):                         
                      file_out.write("%s\t%s\n" % (L_species_dist[0][j],L_species_dist[1][j]))               
              i+=1 
              file_out.close()
              print("Info: Species distributions output is successfully saved at: %s" % file_path)
                
      elif  (datatype.lower() == 'species') and (analysis.lower() == 'autocorrelation') and (not IsAverage):
          if not self.data_stochsim_grid.HAS_SPECIES_AUTOCORRELATIONS:
              print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetSpeciesAutocorrelations(species2calc=True,gridpoints=True)")
              self.GetSpeciesAutocorrelations()          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              L_autocorrelations = zip(*self.data_stochsim_grid.species_autocorrelations)[i-1]
              j=0
              file_out.write('Lag (tau)')
              for L_acor in L_autocorrelations:
                  file_out.write('\tAutocorrelation (%s)' % self.SSA.species_names[j])
                  j+=1
              file_out.write('\n')
              for j in xrange(len(self.data_stochsim_grid.time)-1):                   
                  file_out.write('%s' % (self.data_stochsim_grid.time[j][0])) # lag                      
                  for acor in zip(*L_autocorrelations)[j]:                  
                      file_out.write('\t%s' % acor)
                  file_out.write('\n')                                              
              i+=1 
              file_out.close()
              print("Info: Species autocorrelation output is successfully saved at: %s" % file_path)

      elif  (datatype.lower() == 'species') and (analysis.lower() == 'autocovariance') and (not IsAverage):
          if not self.data_stochsim_grid.HAS_SPECIES_AUTOCOVARIANCES:
              print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetSpeciesAutocovariances(species2calc=True,gridpoints=True)")
              self.GetSpeciesAutocovariances()          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              L_autocovariances = zip(*self.data_stochsim_grid.species_autocovariances)[i-1]
              j=0
              file_out.write('Lag (tau)')
              for L_acov in L_autocovariances:
                  file_out.write('\tAutocorrelation (%s)' % self.SSA.species_names[j])
                  j+=1
              file_out.write('\n')
              for j in xrange(len(self.data_stochsim_grid.time)-1):                   
                  file_out.write('%s' % (self.data_stochsim_grid.time[j][0])) # lag                      
                  for acov in zip(*L_autocovariances)[j]:                  
                      file_out.write('\t%s' % acov)
                  file_out.write('\n')                                              
              i+=1 
              file_out.close()
              print("Info: Species autocovariance output is successfully saved at: %s" % file_path)
                  
      elif  (datatype.lower() == 'species') and (analysis.lower() == 'mean') and (not IsAverage):
          assert self.IsSimulationDone, "Error: Before exporting species time series to a file first do a stochastic simulation"          
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Species\tMean\n")
              j=0
              for s_id in self.SSA.species_names: 
                  file_out.write("%s\t%s\n" % (s_id,self.data_stochsim.species_means[s_id]))      
                  j+=1
              i+=1
              file_out.close()
              print("Info: Species means output is successfully saved at: %s" % file_path)
                  
      elif (datatype.lower() == 'species') and (analysis.lower() == 'std') and (not IsAverage):
          assert self.IsSimulationDone, "Error: Before exporting species time series to a file first do a stochastic simulation"          
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Species\tStandard deviation\n")
              j=0
              for s_id in self.SSA.species_names: 
                  file_out.write("%s\t%s\n" % (s_id,self.data_stochsim.species_standard_deviations[s_id]))
                  j+=1
              i+=1
              file_out.close()
              print("Info: Species standard deviations output is successfully saved at: %s" % file_path)
                  
      elif (datatype.lower() == 'propensities') and  (analysis.lower() == 'timeseries') and (not IsAverage):       
          assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before exporting propensities time series to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"          
          i=1
          while i <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              file_out.write('Time')
              for r_id in self.SSA.rate_names:
                  file_out.write('\t%s' % r_id)
              file_out.write('\n')      
              for timepoint in self.data_stochsim.getPropensities(): 
                  slist = [str(value) for value in timepoint]
                  line = "\t".join(slist) 
                  line += '\n'
                  file_out.write(line)
              i+=1
              file_out.close()
              print("Info: Propensities time series output is successfully saved at: %s" % file_path)
                  
      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'distribution') and (not IsAverage):
          assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before exporting propensities distributions to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w') 
              j=0
              for L_prop_dist in self.data_stochsim.propensities_distributions:
                  file_out.write("Propensity (%s)\tProbability\n"  % self.SSA.rate_names[j])
                  for k in xrange(len(L_prop_dist[0])):
                      file_out.write("%s\t%s\n" % (L_prop_dist[0][k],L_prop_dist[1][k]))
                  j+=1
              i+=1
              file_out.close()
              print("Info: Species distributions output is successfully saved at: %s" % file_path)
              
      elif  (datatype.lower() == 'propensities') and (analysis.lower() == 'autocorrelation') and (not IsAverage):
          if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCORRELATIONS:
              print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetPropensitiesAutocorrelations(rates2calc=True,gridpoints=True)")
              self.GetPropensitiesAutocorrelations(gridpoints=self.data_stochsim.simulation_endtime)          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              L_autocorrelations = zip(*self.data_stochsim_grid.propensities_autocorrelations)[i-1]
              j=0
              file_out.write('Lag (tau)')
              for L_acor in L_autocorrelations:
                  file_out.write('\tAutocorrelation (%s)' % self.SSA.rate_names[j])
                  j+=1
               
              file_out.write('\n')
              for j in xrange(len(self.data_stochsim_grid.time)-1):
                  file_out.write('%s' % (self.data_stochsim_grid.time[j][0])) # lag
                  for acor in zip(*L_autocorrelations)[j]:                         
                      file_out.write('\t%s' % acor)
                  file_out.write('\n')                    
              i+=1   
              file_out.close()
              print("Info: Propensities autocorrelation output is successfully saved at: %s" % file_path) 

      elif  (datatype.lower() == 'propensities') and (analysis.lower() == 'autocovariance') and (not IsAverage):
          if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCOVARIANCES:
              print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetPropensitiesAutocovariances(rates2calc=True,gridpoints=True)")
              self.GetPropensitiesAutocovariances(rates2calc = rates2plot,gridpoints=self.data_stochsim.simulation_endtime)
          
          i=1 
          while i <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')  
              L_autocovariances = zip(*self.data_stochsim_grid.propensities_autocovariances)[i-1]
              j=0
              file_out.write('Lag (tau)')
              for L_acov in L_autocovariances:
                  file_out.write('\tAutocovariance (%s)' % self.SSA.rate_names[j])
                  j+=1
               
              file_out.write('\n')
              for j in xrange(len(self.data_stochsim_grid.time)-1):
                  file_out.write('%s' % (self.data_stochsim_grid.time[j][0])) # lag
                  for acov in zip(*L_autocovariances)[j]:                         
                      file_out.write('\t%s' % acov)
                  file_out.write('\n')                    
              i+=1   
              file_out.close()
              print("Info: Propensities autocovariance output is successfully saved at: %s" % file_path)
                
      elif (datatype.lower() == 'propensities') and  (analysis.lower() == 'mean') and (not IsAverage):        
          assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before exporting propensities means to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"          
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Reaction\tMean\n")                
              for r_id in self.SSA.rate_names: 
                  file_out.write("%s\t%s\n" % (r_id,self.data_stochsim.propensities_means[r_id]))                    
              i+=1
              file_out.close()
              print("Info: Propensities means output is successfully saved at: %s" % file_path)
                                  
      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'std') and (not IsAverage):
          assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before exporting propensities standard deviations to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"                        
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Reaction\tStandard deviation\n")                
              for r_id in self.SSA.rate_names: 
                  file_out.write("%s\t%s\n" % (r_id,self.data_stochsim.propensities_standard_deviations[r_id]))                    
              i+=1
              file_out.close()
              print("Info: Propensities standard deviations output is successfully saved at: %s" % file_path)
                
      elif (datatype.lower() == 'waitingtimes') and (analysis.lower() == 'distribution') and (not IsAverage):          
          if (not self.data_stochsim.HAS_WAITING_TIMES):
              self.GetWaitingtimes()
          i=1
          while i <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')
              for r_id in sorted(self.data_stochsim.waiting_times):
                  file_out.write("Waitingtimes\t%s\n" % (r_id))
                  L_waiting_times_r = self.data_stochsim.waiting_times[r_id]
                  for time in L_waiting_times_r:
                      file_out.write("%s\n" % time)
              i+=1
              file_out.close()
              print("Info: Waitingtimes distributions output is successfully saved at: %s" % file_path)
                
      elif (datatype.lower() == 'waitingtimes') and (analysis.lower() == 'mean') and (not IsAverage):
          if (not self.data_stochsim.HAS_WAITING_TIMES):
              self.GetWaitingtimes()          
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Reaction\tMean\n")
              j=0
              for r_id in self.SSA.rate_names: 
                  file_out.write("%s\t%s\n" % (r_id,self.data_stochsim.waiting_times_means[j]))              
                  j+=1
              i+=1
              file_out.close()
              print("Info: Waitingtimes means output is successfully saved at: %s" % file_path)
                
      elif (datatype.lower() == 'waitingtimes') and (analysis.lower() == 'std') and (not IsAverage):
          if (not self.data_stochsim.HAS_WAITING_TIMES):
              self.GetWaitingtimes()          
          i=1            
          while i <= self.n_trajectories_simulated:            
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(i)
              file_path = "%s%s.txt" % (directory,i)
              file_out = open(file_path,'w')                      
              file_out.write("Reaction\tStandard deviation\n")
              j=0
              for r_id in self.SSA.rate_names: 
                  file_out.write("%s\t%s\n" % (r_id,self.data_stochsim.waiting_times_standard_deviations[j]))              
                  j+=1
              i+=1
              file_out.close()
              print("Info: Waiting times means output is successfully saved at: %s" % file_path)  
                 
      elif (datatype.lower() == 'species') and (analysis.lower() == 'timeseries') and (IsAverage):
          if not self.HAS_AVERAGE:
              self.GetRegularGrid()          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          file_out.write("t")
          for s_id in self.SSA.species_names + self.SSA.fixed_species:
              file_out.write("\t%s (Mean)\t%s (STD)" % (s_id,s_id))   
          file_out.write("\n")
          means = np.transpose(self.data_stochsim_grid.species_means)
          stds = np.transpose(self.data_stochsim_grid.species_standard_deviations)       
          i=0        
          for t in self.data_stochsim_grid.time: 
              file_out.write("%s" % t[0])  
              for j in xrange(len(self.data_stochsim_grid.species_means)):
                  file_out.write("\t%s\t%s" % (means[i][j],stds[i][j]))                   
              file_out.write("\n")
              i+=1  
          print("Info: Averaged species time series output is successfully saved at: %s" % file_path)
      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'timeseries') and (IsAverage):
          assert self.IsTrackPropensities, "Error: Before exporting averaged propensities to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
          if not self.HAS_AVERAGE and self.IsTrackPropensities:
              self.GetRegularGrid()          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          file_out.write("t")
          for r_id in self.SSA.rate_names:
              file_out.write("\t%s (Mean)\t%s (STD)" % (r_id,r_id))
          file_out.write("\n")
          means = np.transpose(self.data_stochsim_grid.propensities_means)
          stds = np.transpose(self.data_stochsim_grid.propensities_standard_deviations)       
          i=0        
          for t in self.data_stochsim_grid.time:
              file_out.write("%s" % t[0])  
              for j in xrange(len(self.data_stochsim_grid.propensities_means)):
                  file_out.write("\t%s\t%s" % (means[i][j],stds[i][j]))                   
              file_out.write("\n")
              i+=1  
          print("Info: Averaged propensities time series output is successfully saved at: %s" % file_path)
      elif (datatype.lower() == 'species') and (analysis.lower() == 'distribution') and (IsAverage):
          if not self.data_stochsim_grid.HAS_AVERAGE_SPECIES_DISTRIBUTIONS:              
              self.GetAverageSpeciesDistributions()          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0 
          for s_id in self.SSA.species_names + self.SSA.fixed_species:
              file_out.write("Amount\t%s (Mean)\t%s (STD)\n" % (s_id,s_id))   
              for j in xrange(len(self.data_stochsim.species_distributions_means[i][0])):
                  s_Amount = self.data_stochsim.species_distributions_means[i][0][j]
                  s_probability_mean = self.data_stochsim.species_distributions_means[i][1][j]
                  s_probability_std = self.data_stochsim.species_distributions_standard_deviations[i][1][j]
                  file_out.write("%s\t%s\t%s\n" % (s_Amount,s_probability_mean,s_probability_std))
              file_out.write("\n")
              i+=1
          print("Info: Averaged species distributions output is successfully saved at: %s" % file_path)
      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'distribution') and (IsAverage):
          if not self.data_stochsim_grid.HAS_AVERAGE_PROPENSITIES_DISTRIBUTIONS:
              self.GetAveragePropensitiesDistributions()
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0
          for r_id in self.SSA.rate_names:
              file_out.write("Propensity\t%s (Mean)\t%s (STD)\n" % (r_id,r_id))   
              for j in xrange(len(self.data_stochsim.propensities_distributions_means[i][0])):
                  r_prop = self.data_stochsim.propensities_distributions_means[i][0][j]
                  r_probability_mean = self.data_stochsim.propensities_distributions_means[i][1][j]
                  r_probability_std = self.data_stochsim.propensities_distributions_standard_deviations[i][1][j]                      
                  file_out.write("%s\t%s\t%s\n" % (r_prop,r_probability_mean,r_probability_std))
              file_out.write("\n")
              i+=1
          print("Info: Averaged propensities distributions output is successfully saved at: %s" % file_path)
      elif (datatype.lower() == 'species') and (analysis.lower() == 'autocorrelation') and (IsAverage):         
          if not self.data_stochsim_grid.HAS_SPECIES_AUTOCORRELATIONS:
              print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetSpeciesAutocorrelations(species2calc=True,gridpoints=True)")
              self.GetSpeciesAutocorrelations()
          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0 
          for s_id in self.SSA.species_names + self.SSA.fixed_species:
              file_out.write(r'Lag ($\tau$)\t%s (Mean)\t%s (STD)\n' % (s_id,s_id))   
              for j in xrange(len(self.data_stochsim_grid.species_autocorrelations_means[i])):
                  acor_mean = self.data_stochsim_grid.species_autocorrelations_means[i][j]
                  acor_std = self.data_stochsim_grid.species_autocorrelations_standard_deviations[i][j]                                     
                  file_out.write("%s\t%s\t%s\n" % (self.data_stochsim_grid.time[j][0],acor_mean,acor_std))
              file_out.write("\n")
              i+=1
          print("Info: Averaged species autocorrelations output is successfully saved at: %s" % file_path)
      elif (datatype.lower() == 'species') and (analysis.lower() == 'autocovariance') and (IsAverage):          
          if not self.data_stochsim_grid.HAS_SPECIES_AUTOCOVARIANCES:
              print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetSpeciesAutocovariances(species2calc=True,gridpoints=True)")
              self.GetSpeciesAutocovariances()
          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0 
          for s_id in self.SSA.species_names + self.SSA.fixed_species:
              file_out.write(r'Lag ($\tau$)\t%s (Mean)\t%s (STD)\n' % (s_id,s_id))   
              for j in xrange(len(self.data_stochsim_grid.species_autocovariances_means[i])):
                  acor_mean = self.data_stochsim_grid.species_autocovariances_means[i][j]
                  acor_std = self.data_stochsim_grid.species_autocovariances_standard_deviations[i][j]                                     
                  file_out.write("%s\t%s\t%s\n" % (self.data_stochsim_grid.time[j][0],acor_mean,acor_std))

              file_out.write("\n")
              i+=1
          print("Info: Averaged species autocovariances output is successfully saved at: %s" % file_path)
          
      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'autocorrelation') and (IsAverage):          
          if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCORRELATIONS:
              print("Warning: Autocorrelations are not yet calculated. StochPy automatically calculates autocorrelations with pre-defined settings. You can use GetPropensitiesAutocorrelations(rates2calc=True,gridpoints=True)")
              self.GetPropensitiesAutocorrelations()          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0 
          for r_id in self.SSA.rate_names:
              file_out.write(r'Lag ($\tau$)\t%s (Mean)\t%s (STD)\n' % (r_id,r_id))   
              for j in xrange(len(self.data_stochsim_grid.propensities_autocorrelations_means[i])):
                  acor_mean = self.data_stochsim_grid.propensities_autocorrelations_means[i][j]
                  acor_std = self.data_stochsim_grid.propensities_autocorrelations_standard_deviations[i][j]                                     
                  file_out.write("%s\t%s\t%s\n" % (self.data_stochsim_grid.time[j][0],acor_mean,acor_std))
              file_out.write("\n")
              i+=1
          print("Info: Averaged propensities autocorrelations output is successfully saved at: %s" % file_path)

      elif (datatype.lower() == 'propensities') and (analysis.lower() == 'autocovariance') and (IsAverage):          
          if not self.data_stochsim_grid.HAS_PROPENSITIES_AUTOCOVARIANCES:
              print("Warning: Autocovariances are not yet calculated. StochPy automatically calculates autocovariances with pre-defined settings. You can use GetPropensitiesAutocovariances(rates2calc=True,gridpoints=True)")
              self.GetPropensitiesAutocovariances()
          
          file_path = '%s.txt' % directory
          file_out = open(file_path,'w')
          i=0 
          for r_id in self.SSA.rate_names:
              file_out.write(r'Lag ($\tau$)\t%s (Mean)\t%s (STD)\n' % (r_id,r_id))   
              for j in xrange(len(self.data_stochsim_grid.propensities_autocovariances_means[i])):
                  acor_mean = self.data_stochsim_grid.propensities_autocovariances_means[i][j]
                  acor_std = self.data_stochsim_grid.propensities_autocovariances_standard_deviations[i][j]                                     
                  file_out.write("%s\t%s\t%s\n" % (self.data_stochsim_grid.time[j][0],acor_mean,acor_std))
              file_out.write("\n")
              i+=1
          print("Info: Averaged propensities autocovariances output is successfully saved at: %s" % file_path)

      else:
          print("""Error: The only valid options are: 
          Export2File(analysis='timeseries',datatype='species')
          Export2File(analysis='timeseries',datatype='species',IsAverage=True)
          Export2File(analysis='distribution',datatype='species')
          Export2File(analysis='distribution',datatype='species',IsAverage=True)
          Export2File(analysis='autocorrelation',datatype='species')
          Export2File(analysis='autocorrelation',datatype='species',IsAverage=True)
          Export2File(analysis='autocovariance',datatype='species')
          Export2File(analysis='autocovariance',datatype='species',IsAverage=True)
          Export2File(analysis='mean',datatype='species',IsAverage=False)
          Export2File(analysis='std',datatype='species',IsAverage=False)
          
          Export2File(analysis='timeseries',datatype='propensities')
          Export2File(analysis='timeseries',datatype='propensities',IsAverage=True)
          Export2File(analysis='distribution',datatype='propensities')
          Export2File(analysis='distribution',datatype='propensities',IsAverage=True)
          Export2File(analysis='autocorrelation',datatype='propensities')
          Export2File(analysis='autocorrelation',datatype='propensities',IsAverage=True)
          Export2File(analysis='autocovariance',datatype='propensities')
          Export2File(analysis='autocovariance',datatype='propensities',IsAverage=True)
          Export2File(analysis='mean',datatype='propensities',IsAverage=False)
          Export2File(analysis='std',datatype='propensities',IsAverage=False)                   

          Export2File(analysis='distribution',datatype='waitingtimes')
          Export2File(analysis='mean',datatype='waitingtimes',IsAverage=False)
          Export2File(analysis='std',datatype='waitingtimes',IsAverage=False)         
          """)
          
          
  def Import2StochPy(self,filename,filedir,delimiter='\t'):
      """
      Can import time series data with the following format:
      
      Time S1 S2 S3 Fired Reactions
      0    1  0  1  nan
      1.5  0  0  2  1
      etc.
      
      or 
      
      Time S1 S2 S3
      0    1  0  1
      1.5  0  0  2
      etc.      
      
      In the future, this function will probably support more data types. We currently accept the default output of the Gillespie algorithm from which other data types can be derived.
      
      Input: 
       - *filename* (string)
       - *filedir* (string)
       - *delimiter* (string)
      """
      print("Warning: In construction - This function currently accepts species time series data only!")
      try:
          filepath = os.path.join(filedir,filename)
          file_in = open(filepath,'r') 
      except IOError:
          print("Error: File path %s does not exist" % filepath)
          sys.exit()
      
      L_sim_output = []
      L_data = file_in.readlines()  
      L_header = L_data[0].strip().split(delimiter)
      L_species_names = L_header[1:]      
      self.IsTauLeaping = False
      if L_header[-1] != 'Fired Reaction': # no fired reactions stored                    
          self.IsTauLeaping = True
      else:
          L_species_names.pop(-1)         
           
      for dat in L_data[1:]:
          fdat = map(float,dat.strip().split(delimiter))          
          if not self.IsTauLeaping and not math.isnan(fdat[-1]):
             fdat[-1] = int(fdat[-1])                  
          L_sim_output.append(fdat)      
      self.SSA.sim_output = L_sim_output
      self.SSA.species_names = L_species_names
      self.SSA.timestep = len(L_sim_output)
      self.SSA.sim_t = L_sim_output[-1][0]
      nreactions = int(np.nanmax(np.transpose(self.SSA.sim_output)[-1]))
      self.SSA.rate_names = []
      for r in xrange(1,nreactions+1):
          self.SSA.rate_names.append('R%s' % r)          

      print("Info: Reaction identifiers are unknown, StochPy created the following identifiers automatically:\t%s" % self.SSA.rate_names)
      print("Info: Modify 'smod.SSA.rate_names' if other identifiers are desired")
      self.current_trajectory = 1 # HARD CODED
      self.n_trajectories_simulated = 1      
      self.IsTrackPropensities =  False
      self.data_stochsim = IntegrationStochasticDataObj()           
      self.FillDataStochsim()     
      try:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
      except:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
      self.IsSimulationDone = True
      
          
  def ShowSpecies(self):
      """ Print the species of the model """
      print(self.data_stochsim.species_labels)

  def ShowOverview(self):
      """ Print an overview of the current settings """
      print("Current Model:\t%s" % self.model_file)
      if self.sim_mode == "steps": 
          print("Number of time steps:\t%s" % self.sim_end)
      elif self.sim_mode == "time":
          print("Simulation end time:\t%s" % self.sim_end)
      print("Current Algorithm:\t%s" % self.sim_method)
      print("Number of trajectories:\t%s" % self.sim_trajectories)
      if self.IsTrackPropensities:
           print("Propensities are tracked")
      else:
           print("Propensities are not tracked")

  def DeleteTempfiles(self):
      """ Deletes all .dat files """
      for line in self.sim_dump:
          os.remove(line)

  def DoTestsuite(self,epsilon_ = 0.01,sim_trajectories=1000):
      """
      DoTestsuite(epsilon_ = 0.01,sim_trajectories=1000)
      
      Do "sim_trajectories" simulations until t=50 and print the interpolated result for t = 0,1,2,...,50
      
      Input:
       - *epsilon_* [default = 0.01]: useful for tau-Leaping simulations (float)
       - *sim_trajectories* [default = 1000]
      """
      self.sim_end = 50
      self.sim_mode = "time"
      self.sim_trajectories = sim_trajectories
      self.DoStochSim(epsilon = epsilon_)
      self.GetRegularGrid(npoints = 51)
      self.PrintAverageSpeciesTimeSeries()
      self.sim_end = 1000 # Reset settings to default values
      self.sim_mode = "steps"
      self.sim_trajectories = 1

  def FillDataStochsim(self):
      """ Put all simulation data in the data object data_stochsim"""
      (L_probability_mass,D_means,D_stds,D_moments) = Analysis.GetDataDistributions(self.SSA.sim_output,self.SSA.species_names)
      sim_dat = np.array(self.SSA.sim_output,'d')
      self.data_stochsim.setTime(sim_dat[:,0])
      self.data_stochsim.setSpeciesDist(L_probability_mass,D_means,D_stds,D_moments)
        
      L_all_species = copy.copy(self.SSA.species_names)
      L_all_species += [s_id for s_id in self.SSA.fixed_species]
      
      if self.IsTauLeaping:
          self.data_stochsim.setSpecies(sim_dat[:,1:],L_all_species)           # no 'firing' column
      else:
          self.data_stochsim.setSpecies(sim_dat[:,1:-1],L_all_species)
      self.data_stochsim.setFiredReactions(sim_dat[:,-1][1:])
      self.data_stochsim.setSimulationInfo(self.SSA.timestep,self.SSA.sim_t,self.current_trajectory)
      if self.IsTrackPropensities:
          (L_probability_mass,D_means,D_stds,D_moments) = Analysis.GetDataDistributions(self.SSA.propensities_output,self.SSA.rate_names)
          self.data_stochsim.setPropensitiesDist(L_probability_mass,D_means,D_stds,D_moments)
          self.data_stochsim.setPropensities(self.SSA.propensities_output,self.SSA.rate_names)
          
          
  def PrintSpeciesTimeSeries(self):
      """ Print time simulation output for each generated trajectory """      
      assert self.IsSimulationDone, "Error: Before printing time simulation results first do a stochastic simulation"      
      i=1
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          print 'Time\t',
          for s_id in self.SSA.species_names:
              print '%s\t' % (s_id),
          print ''
          for timepoint in self.data_stochsim.getSpecies():
              for value in timepoint:
                  print '%s\t' % (value),
              print ''
          i+=1

  def PrintPropensitiesTimeSeries(self):
      """ Print a time series of the propensities each generated trajectory """      
      assert (self.IsTrackPropensities and self.IsSimulationDone), "Error: Before plotting a time series of propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
      i=1
      while i <= self.n_trajectories_simulated:	
          if self.n_trajectories_simulated > 1:        
              self.GetTrajectoryData(i)
          print 'Time\t',              
          for r_id in self.SSA.rate_names: 
              print '%s\t' % (r_id),
          print ''
          for timepoint in self.data_stochsim.getPropensities():    
              for value in timepoint:
                   print '%s\t' % (value),
              print ''
          i+=1

  def PrintSpeciesDistributions(self):
      """ Print obtained distributions for each generated trajectory """      
      assert self.IsSimulationDone, "Error: Before printing distributions first do a stochastic simulation"
      i=1
      while i <= self.n_trajectories_simulated:    
          if self.n_trajectories_simulated > 1:  
              self.GetTrajectoryData(i)
          j=0
          for L_species_dist in self.data_stochsim.species_distributions:
              print "Amount (%s)\tProbability" % self.SSA.species_names[j]                              
              for k in xrange(len(L_species_dist[0])):
                  print "%s\t%s" % (L_species_dist[0][k],L_species_dist[1][k])
              j+=1
          i+=1

  def PrintPropensitiesDistributions(self):
      """ Print obtained distributions for each generated trajectory """     
      assert (self.IsTrackPropensities and self.IsSimulationDone),"Error: Before printing distributions first do a stochastic simulation"
      i=1
      while i <= self.n_trajectories_simulated:    
          if self.n_trajectories_simulated > 1:  
              self.GetTrajectoryData(i)
          j=0
          for L_prop_dist in self.data_stochsim.propensities_distributions:
              print "Propensity (%s)\tProbability"  % self.SSA.rate_names[j]
              for k in xrange(len(L_prop_dist[0])):
                  print "%s\t%s" % (L_prop_dist[0][k],L_prop_dist[1][k])
              j+=1
          i+=1

  def PrintWaitingtimesDistributions(self):
      """ Print obtained waiting times """
      assert not self.IsTauLeaping, "Error: Tau-Leaping method does not allow for calculation of waiting times"
      if (not self.data_stochsim.HAS_WAITING_TIMES) and (not self.IsTauLeaping):
          self.GetWaitingtimes()
      i=1
      while i <= self.n_trajectories_simulated:
          if self.n_trajectories_simulated > 1:
              self.GetTrajectoryData(i)
          D_waiting_times = self.data_stochsim.waiting_times
          for r_id in sorted(D_waiting_times):
              print "Waiting times\t(%s)" % r_id
              L_waiting_times_r = D_waiting_times[r_id]
              for time in L_waiting_times_r:
                  print time
          i+=1

  def PrintAverageSpeciesTimeSeries(self):    
      """ Analyze the average output over all generated trajectories """
      if not self.HAS_AVERAGE:
          self.GetRegularGrid()
      for s_id in self.data_stochsim.species_labels:              
          print "\t%s (Mean)\t%s (STD)" % (s_id,s_id),  
      print
      L_means = np.transpose(self.data_stochsim_grid.species_means)
      L_stds = np.transpose(self.data_stochsim_grid.species_standard_deviations)
      i=0
      for t in self.data_stochsim_grid.time: 
          print t[0],
          for j in xrange(len(self.data_stochsim_grid.species_means)): 
              print "\t%s\t%s" % (L_means[i][j],L_stds[i][j]),
          print ""
          i+=1
              
  def PrintAveragePropensitiesTimeSeries(self):    
      """ Analyze the average output over all generated trajectories """
      assert self.IsTrackPropensities, "Error: Before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
      if (not self.HAS_AVERAGE) and (self.IsTrackPropensities):
          self.GetRegularGrid()      
      print "Time",
      for r_id in self.SSA.rate_names:              
          print "\t%s (Mean)\t%s (STD)" % (r_id,r_id),
      print
      L_means = np.transpose(self.data_stochsim_grid.propensities_means)
      L_stds = np.transpose(self.data_stochsim_grid.propensities_standard_deviations)
      i=0
      for t in self.data_stochsim_grid.time: 
          print t[0],
          for j in xrange(len(self.data_stochsim_grid.propensities_means)): 
              print "\t%s\t%s" % (L_means[i][j],L_stds[i][j]),
          print ""
          i+=1
