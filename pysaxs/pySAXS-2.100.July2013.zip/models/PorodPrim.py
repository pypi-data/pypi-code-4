from model import Model
from pySAXS.LS.LSsca import Qlogspace
import numpy
import scipy

class PorodPrim(Model):
    '''
    Porod
    
    for Porod Model
    by OT & CG 17/01/2012
    '''
    def PorodPrimFunction(self,q,par):
        """
        Porod model to fit q-4 part at high q
        par[0] : B1
        par[1] : rg
        """
        B1=par[0]
        Rg=par[1]
        er=(scipy.special.erf(q*Rg/(6.0**0.5)))**3
        q4=(q/er)**(-4.0)
        return B1*q4
                
    
    
    IntensityFunc=PorodPrimFunction #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[1e-6,100]           #list of defaults parameters
    Format=["%1.3e","%1.3e"]      #list of c format
    istofit=[True,True]    #list of boolean for fitting
    name="PorodPrimaire"          #name of the model
    Doc=["B1",\
         "Rg"] #list of description for parameters
    specific=True  #for specific model, set to true
    Description="Porod model to fit q-4 part at high q"  # description of model
    Author="OT & CG 17/01/2012"       #name of Author
    
