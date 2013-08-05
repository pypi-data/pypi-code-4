import unittest
import CoolProp.CoolProp as CP
from CoolProp.CoolProp import Props
from CoolProp.Plots.Plots import Ph
import matplotlib.pyplot as plt
import CoolProp
import numpy as np
       
def test_TTSE():
    fluid = 'R245fa'
    
    CP.enable_TTSE_LUT(fluid)
    sTTSE = CP.Props('S','T',400,'D',0.5,fluid)
    
    hmin, hmax, pmin, pmax = CP.get_TTSESinglePhase_LUT_range(fluid)

    CP.set_TTSE_mode(fluid,'BICUBIC')
    
    Ph(fluid)
    
    for h in np.linspace(hmin, hmax, 133):
        for p in np.linspace(pmin, pmax, 227):
            try:
                CP.disable_TTSE_LUT(fluid)
                sEOS = CP.Props('S','H',h,'P',p,fluid)
                
                CP.enable_TTSE_LUT(fluid)
                sBICUBIC = CP.Props('S','H',h,'P',p,fluid)
                
                if abs(sEOS-sBICUBIC) > 1e-6:
                    print sEOS,sBICUBIC,sEOS-sBICUBIC
                    
            except ValueError:
                plt.plot(h,p,'bo')
                print 'FAILED',"'P',",p,",'H',",h
    plt.show()

if __name__=='__main__':
    test_TTSE()
    
##     import nose
##     nose.runmodule()