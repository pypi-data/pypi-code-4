from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import *
import numpy

class MonoEllipse(Model):
    '''
    Mono Ellipse
    by OT 10/06/2009
    '''
    def MonoEllipseFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] Semi major axis(A)
        par[1] Eccentricity
        par[2] concentration of sphere (cm-3)
        par[3] scattering length density of sphere (cm-2)
        par[4] scattering length density of outside (cm-2)
        """
        R=par[0]
        ec=par[1]
        return par[2]*(1.e-48)*(( numpy.pi*(4./3.)*(ec*par[0]**3.) )**2.)*((par[3]-par[4])**2.)*P5(q,R,e)
            
    '''
    parameters definition
    Model(3,MonoEllipse,
    Qlogspace(1e-4,1.,500.)
    ,([100.,0.5,1.5e14,2e11,1e10])
    ,("Semi major axis (A)"
    ," Eccentricity","Number density",
    "Scattering length density of ellipse (cm-2)"
    ,"scattering length density of medium (cm-2)")
    ,("%f","%f","%1.3e","%1.3e","%1.3e"),(True,True,True,False,False)),
    
     
    
    from LSsca
    '''
    IntensityFunc=MonoEllipseFunction #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[100.,0.5,9.8e11,9.8e10,1e10]          #list of defaults parameters
    Format=["%f","%f","%1.3e","%1.3e","%1.3e"]      #list of c format
    istofit=[True,True,True,False,False]    #list of boolean for fitting
    name="Mono Ellipse"          #name of the model
    Doc=["Semi major axis (A)",\
         " Eccentricity","Number density",\
         "Scattering length density of ellipse (cm-2)"\
         ,"scattering length density of medium (cm-2)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=MonoEllipse()
    #plot the model
    import Gnuplot
    gp=Gnuplot.Gnuplot()
    gp("set logscale xy")
    c=Gnuplot.Data(modl.q,modl.getIntensity(),with_='points')
    gp.plot(c)
    raw_input("enter") 
    #plot and fit the noisy model
    yn=modl.getNoisy(0.4)
    cn=Gnuplot.Data(modl.q,yn,with_='points')
    res=modl.fit(yn) 
    cf=Gnuplot.Data(modl.q,modl.IntensityFunc(modl.q,res),with_='lines')
    gp.plot(c,cn,cf)
    raw_input("enter")    
    #plot and fit the noisy model with fitBounds
    bounds=modl.getBoundsFromParam() #[250.0,2e11,1e10,1.5e15]
    res2=modl.fitBounds(yn,bounds)
    print res2
    raw_input("enter")  
