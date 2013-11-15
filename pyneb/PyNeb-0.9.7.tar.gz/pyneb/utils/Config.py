import os
from misc import execution_path
from logging import my_logging

class _Config(object):
    """
    This is the place where to put stuff that any module may need, a kind of COMMON.
    An instantiation is done in the main __init__ file using the "config" name.

    """


    def __init__(self):
        """
        Define variables that will be known from everywhere:
        - INSTALLED: a dictionary whose keys are the libraries that PyNeb may need
            e.g. 'plt' for matplotlib.pyplot, 'scipy' for scipy.interpolate. and whose values
            are Boolean
        
        - Datafile: a dictionary holding the HI atom, which can be used intensively in Atom.getIonicAbundance
        
        - pypic_path: the default value for the pypic_path parameter of getEmisGridDict().
            The first try is ./.pypics: if it cannot be created, or it exists but it is not writable, 
            /tmp/pypics is tried; if it cannot be created, or it exists but it is not writable, the path
            is set to None and a pypic_path value shall be provided to getEmisGridDict().
        
        Parameters: none
        
        """
        self.log_ = my_logging()
        self.calling = '_Config'
        
        self.INSTALLED = {}
        try:
            import matplotlib.pyplot as plt
            self.INSTALLED['plt'] = True
        except:
            self.INSTALLED['plt'] = False
            self.log_.message('matplotlib not available', calling=self.calling)
        try:
            from scipy import interpolate
            self.INSTALLED['scipy'] = True
        except:
            self.INSTALLED['scipy'] = False
            self.log_.message('scipy not available', calling=self.calling)
        try:
            import multiprocessing as mp
            self.INSTALLED['mp'] = True
            self.Nprocs = mp.cpu_count()
        except:
            self.INSTALLED['mp'] = False
            self.log_.message('multiprocessing not available', calling=self.calling)
            self.Nprocs = 1
            
        self.DataFiles = {}
    
        self._initPypicPath()
        
        self.unuse_multiprocs()
        
        self.kappa = None
        
                
    def _initPypicPath(self):
        """
        Defining the pypic_path variable
        """
        self.pypic_path = './pypics/'
        if os.path.exists(self.pypic_path):
            if not os.access(self.pypic_path, os.W_OK):
                self.log_.message('Directory {0} not writable'.format(self.pypic_path),
                                  calling=self.calling)
                self.pypic_path = None
        else:
            try:
                os.makedirs(self.pypic_path)
                self.log_.message('Directory {0} created'.format(self.pypic_path),
                                  calling=self.calling)
            except:
                self.pypic_path = None
        if self.pypic_path is None:
            self.pypic_path = '/tmp/pypics/'
            if os.path.exists(self.pypic_path):
                if not os.access(self.pypic_path, os.W_OK):
                    self.log_.message('Directory {0} not writable'.format(self.pypic_path),
                                      calling=self.calling)                                   
                    self.pypic_path = None 
            else:
                try:
                    os.makedirs(self.pypic_path)
                    self.log_.message('Directory {0} created'.format(self.pypic_path),
                                      calling=self.calling)
                except:
                    self.pypic_path = None
        self.log_.message('pypic_path set to {0}'.format(self.pypic_path),
                                      calling=self.calling)
    
    
    def use_multiprocs(self):
        self._use_mp = True
    
        
    def unuse_multiprocs(self):
        self._use_mp = False    
        
