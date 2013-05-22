from PyGS import Import

history = \
"""
0.4.0 - 07/05/13
        Major (backwards-incompatible) update.
        Now the project file is in HDF5 format, eliciting faster read-in.
        numpy recarrays replaced with pandas DataFrame
        Extreme simplification of __init__ method logic
        Made most units smaller and more manageable.
        
0.3.3 - 08/04/13
        Added clean() method to PyGS object which gets rid of 'stupid' data
        Severely changed lumfunct.f90 to be cleaner
        
0.3.2 - 05/03/13
        Jake Hebert wrote fortran code to calculate EEP luminosity function
        Integrated this code into the PyGS package.
        Fixed a typo which made the whole program useless
        Fixed a bug with _LumDistance()
        
0.3.1 - 22/01/13
        Added an empty 'Cosmology' module/class which will be used to output cosmology plots
        Put correct units on many of the power spectra plots
        Added a uniqueness test based on ID to the import.
        
0.3.0 - 4/12/12
        Major re-organization of code to be much more modular. 
        Each type of calculation has a separate module containing a subclass of PyGS.
        Not much difference to the interface.
        
0.2.5 - 13/11/12
        Now calculates the K-Correction, the luminosity distance, absolute magnitude, and luminosity
        Author: Jake Hebert
        
0.2.4 - 12/11/12
        Cleaned up column-specifying behaviour. 
        
0.2.3 - 8/11/12
        Thanks to Jake Hebert, fixed a bug on importing. 
        Now imports g-band apparent magnitudes ready for K-corrections.
        
0.2.2 - 17/09/12
        Now can calculate selection function upon import and deals with weight values more homogeneously
        Added support for power spectra (fixed) and histograms to receive the weights.
        NOTE: selection function calculated for data stopping before z=0.25 seems to be inaccurate.
        
0.2.1 - 17/09/12
        Updated the radial power spectra calculations to involve an optional weighting form the selection function.
        
0.2.0 - 17/09/12
        Added simple selection function routines, to define AND create samples from the analytic selection function.
        
0.1.5 - 14/09/12
        Imports sample cuts from file when starting from a sample file for more homogeneous usage.
        
0.1.4 - 13/09/12
        Changed default bounds of 1D power spectra to be more useful.
        Fixed bug which made program hang if 'no' was selected when asked to overwrite project folder.
        Fixed bug where setting a cut to 0 would render it useless.
        
0.1.3 - Hid LuminosityFromAppMag method from user
        Cleaned up a lot of input/raw_input statements
        Fixed a bug that meant angles weren't converting to radians
        Cut specification overhaul with range now indicated and if a cut removes all data it is flagged and you must re-specify.
        
0.1.2 - Hid unwanted methods and variables from end user (6/09/12)
0.1.1 - Fixed import when importing from scratch. Now creates sample directory properly. (6/09/12)
0.1.0 - All power spectra implemented, and importing of data roughly implemented.
"""
