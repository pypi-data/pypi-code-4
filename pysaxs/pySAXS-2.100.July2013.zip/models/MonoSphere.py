from model import Model
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.LS.LSsca import getV
from pySAXS.LS.LSsca import P1
import numpy

class MonoSphere(Model):
    '''
    
    class monoSphere from LSSca
    by OT 10/06/2009
    '''
    def MonoSphereFunction(self,q,par):
        """
        q array of q (A-1)
        par[0] radius of the sphere (A)
        par[1] scattering length density of sphere (cm-2)
        par[2] scattering length density of outside (cm-2)
        par[3] concentration of sphere (cm-3)
        """
        if len(par)!=4:
            sys.stderr.write("This function requires a list of 4 parameters")
            return -1.
        else:
            return par[3]*(par[1]-par[2])**2.*getV(par[0])*getV(par[0])*1e-48*P1(q,par[0])
            #sys.stderr.write(str(par[0]))
            #return P1(q,par[0])
            
    '''
    parameters definition
    Model(0,MonoSphere,Qlogspace(1e-4,1.,500.),([250.0,2e11,1e10,1.5e15]),
    ("radius (A)","scattering length density of sphere (cm-2)","scattering length density of outside (cm-2)","number concentration (cm-3)")
    ,("%f","%1.3e","%1.3e","%1.3e"),(True,True,False,False)),
    from LSsca
    '''
    IntensityFunc=MonoSphereFunction #function
    N=0
    q=Qlogspace(1e-4,1.,500.)      #q range(x scale)
    Arg=[30.0,9.8e11,9.8e10,1.e10]           #list of defaults parameters
    Format=["%f","%1.3e","%1.3e","%1.3e"]      #list of c format
    istofit=[True,True,False,False]    #list of boolean for fitting
    name="Spheres Monodisperse"          #name of the model
    Doc=["radius (A)",\
         "scattering length density of sphere (cm-2)",\
         "scattering length density of medium (cm-2)",\
         "number concentration (cm-3)"] #list of description for parameters
    
if __name__=="__main__":
    '''
    test code
    '''
    modl=MonoSphere()
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
