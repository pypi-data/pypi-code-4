# -*- coding: cp1252 -*-
"""
LIONS_SAXS python routines for small angle xray scattering.
Model class
version 0.1b 04/07/2010
04-07-2010 DC: calculation of residuals corrected in fitBounds
04-07-2010 DC: calculation of chi square corrected
03-07-2010 DC: syntax error on fitBounds corrected
"""


import sys
from string import *
from math import *
#import Numeric
import numpy
from scipy import special as SPspecial
from scipy import stats as SPstats
from scipy import integrate as SPintegrate
from scipy import optimize 
import random
from time import clock
from xml.etree import ElementTree
from pySAXS.tools import xmltools
import pySAXS

class Model:
    '''
    Model class templates
    test
    '''
    IntensityFunc=None #function
    N=0
    q=None          #q range(x scale)
    Arg=[]        #list of parameters
    Format=[]     #list of c format
    istofit=[]    #list of boolean for fitting
    name=""         #name of the model can be different from the class name
    Doc=[]          #list of description for parameters
    Description=""  # description of model
    Author="LIONS"  #name of Author
    WarningForCalculationTime=False     #if calculation time is too high, set to false
    specific=False  #for specific model, set to true
    prefit=None     #prefit function, by default is None
    '''
    def prefit(self,Iexp):
        #   try to estimate some parameters from Iexp
        #return a list of estimate parameters
        
        return [1,2,3,4,5,6]
    '''
    
    def __init__(self,q=None,Arg=[],istofit=None,name=""):
        if q<>None:
            self.q=q
        if (Arg<>[])and (Arg!=None):
            self.Arg=Arg
        if name!="":
            self.name=name
        #if istofit == none then fit all datas (array of true)
        if (istofit==None)and (self.istofit==None):
            self.istofit=Arg
            if len(Arg)>=0:
                for i in range(len(Arg)):
                    self.istofit[i]=True
    
    def __str__(self):
        return "Model "+self.name+ " with parameters : "+str(self.Arg)
        
    def __repr__(self):
        return self.__str__()
    
    def xml(self):
        '''
        return an xml object
        with name, args, and isTofit
        <model name='Gaussian'>
        <par value='0.123' fit='true'>height of gaussian</par>
        ...
        </model>
        '''
        #create the root </root><root>
        root_element = ElementTree.Element("model",name=self.__class__.__name__)
        for i in range(len(self.Arg)):
            attrib={'value':str(self.Arg[i]),\
                    'fit':str(self.istofit[i]),
                    'order':str(i)}
            child = ElementTree.Element("par",attrib)
            child.text=str(self.Doc[i])
            #now append
            root_element.append(child)
        return root_element
        
    
    def addParameter(self,description,value,istofit=True,dataformat='%6.2f'):
        self.Arg.append(value)
        self.Doc.append(description)
        self.istofit.append(istofit)
        self.Format.append(dataformat)


    def getNumber(self):
        return self.N
    def setQ(self,q):
        '''
        set the q scale
        '''
        self.q=q
        
    def getQ(self):
        '''
        get the q scale
        as a numpy array
        '''
        temp=numpy.zeros(len(self.q),dtype='float')
        for i in range(len(self.q)):
            temp[i]=self.q[i]
        return temp
    
    def setArg(self,par):
        '''
        set the model parameters
        '''
        self.Arg=par
        
    def getArg(self):
        '''
        return the model parameters 
        as list
        '''
        temp=list(range(len(self.Arg)))
        for i in range(len(self.Arg)):
            temp[i]=self.Arg[i]
        return temp

    def setIstofit(self,ITF):
        '''
        set istofit varaiable
        '''
        self.istofit=ITF
        
    def getIstofit(self):
        temp=list(range(len(self.istofit)))
        for i in range(len(self.istofit)):
            temp[i]=self.istofit[i]
        return temp

    def getIntensity(self):
        '''
        compute the intensity function for the model
        '''
        
        try:
            y=self.IntensityFunc(self.q,self.Arg)
        except:
            y=numpy.zeros(numpy.shape(self.q))
        return y
    
    def getNoisy(self,randompercent=0.1):
        '''
        return a noisy intensity computed for the model
        '''
        y=self.getIntensity()
        for i in range(len(self.q)):
            y[i]=y[i]*(1+((random.random()-0.5)*randompercent))
        return y
    
    def getBoundsFromParam(self,aroundParam=0.2):
        '''
        return bounds of parameters
        with a percent of aroundParam
        '''
        bounds=[]
        for i in range(len(self.Arg)):
            boundsmin=self.Arg[i]*(1-aroundParam)
            boundsmax=self.Arg[i]*(1+aroundParam)
            bounds.append((boundsmin,boundsmax))
        return bounds
            
    def residuals(self,par,Iexp,plotexp=0):
        """
        residuals
        par is the list of the parameters to be fitted
        """
        par_to_fit=self.Arg[:]
        j=0 
        for i in range(len(par_to_fit)):
            if self.istofit[i]==True:
                par_to_fit[i]=par[j]
                j+=1
        err=(Iexp*self.q**plotexp-self.IntensityFunc(self.q,par_to_fit)*self.q**plotexp)
        return err

    def residuals_bounds(self,par,Iexp,plotexp=0):
        """
        residuals used for the fit with bounds (arguments for leastsq and fmin.tnc are different)
        par is the list of the parameters to be fitted
        """
        par_to_fit=self.Arg[:]
        j=0 
        for i in range(len(par_to_fit)):
            if self.istofit[i]==True:
                par_to_fit[i]=par[j]
                j+=1
        err=numpy.sum((Iexp*self.q**plotexp-self.IntensityFunc(self.q,par_to_fit)*self.q**plotexp)**2)
        return err
        
    def chi_carre(self,par,Iexp,plotexp=0):
        '''
        chi_carre
        par is the list of all parameters (either to be fitted or not)
        Here the chi square is calculated assuming that the standard deviation equals the function
        '''
        '''par=[]
        for i in range(len(self.Arg)):
            if self.istofit[i]==True:
                par.append(self.Arg[i])
        '''
        res=self.residuals(par,Iexp,plotexp)**2.
        i=self.IntensityFunc(self.q,par)
        chi = numpy.sum(res/i)
        return chi
    
    def fit(self,Iexp,plotexp=0,verbose=False):
        '''
        Fit the models with leastsq
        '''
        # params can be not fitted (from istofit)
        #--produce a new param : param0
        param0=[]
        NF=0 #if many parameters to fit
        for i in range(len(self.Arg)):
            if self.istofit[i]:
                param0.append(self.Arg[i])
                NF=NF+1
        #print param0
        #-- fitting procedure
        t0=clock()
        res=optimize.leastsq(self.residuals,param0,args=(Iexp,plotexp),full_output=1)
        t1=clock()
        if verbose:
            print 'Parameters found for the fit= ', res[0], ' in ',t1-t0,'s'  
            print 'Covariance matrix of the parameters',res[1]
        # results to new params
        par=self.Arg
        j=0
        for i in range(len(par)):
            if self.istofit[i]:
                if NF==1:
                    par[i]=res[0]
                else:
                    par[i]=res[0][j]
                #par[i]=res[j]
                j=j+1
        return par
    
    def fitBounds(self,Iexp,bounds,plotexp=0,verbose=False):
        '''
        fit the model with fmin_tnc 
        with bounds as 
        bounds = [(0.0,10.0)]
        bounds must have same size than params
        '''
        # params can be not fitted (from istofit)
        #--produce a new param : param0
        # and newbounds
        #if isttofit is not True, then bounds or params are not taken into acount
        param0=[]
        newbounds=[]
        NF=0
        for i in range(len(self.Arg)):
            if self.istofit[i]==True:
                param0.append(self.Arg[i])
                newbounds.append(bounds[i])
                NF=NF+1
        #fitting with bounds
        t0=clock()
        res, nfeval, rc = optimize.fmin_tnc(self.residuals_bounds, param0, fprime=None, args=([Iexp,plotexp]),\
                                  approx_grad=1, bounds=newbounds, epsilon=1e-08, scale=None, messages=0,\
                                  maxCGit=-1, maxfun=None, eta=-1, stepmx=0, accuracy=0, fmin=0, ftol=-1, rescale=-1)
        t1=clock()
        if verbose:
            print 'Parameters found for the fit= ', res, ' in ',t1-t0,'s'  
        # results to new params
        par=self.Arg
        j=0
        for i in range(len(par)):
            if self.istofit[i]==True:
                if NF==1:
                    par[i]=res
                else:
                    par[i]=res[j]
                #par[i]=res[j]
                j=j+1
        return par
        
        return message
    
def getModelFromXML(element):
    attrib=element.attrib
    #print attrib
    if not(attrib.has_key('name')):
           return None
    
    modelname=attrib['name']
    M=getattr(pySAXS.models,modelname)()#create a new model
    #print "create new model from class :",modelname
    arg={}
    istofit={}
    l=[]
    for subelement in element:
            tag=subelement.tag
            subattrib=subelement.attrib
            if subattrib.has_key('order'):
                if subattrib.has_key('value'):
                    arg[subattrib['order']]=float(subattrib['value'])
                    istofit[subattrib['order']]=subattrib['fit']
                    l.append(subattrib['order'])
    #here we have a list and a dictionnary
    l.sort()
    returnArg=[]
    returnIsToFit=[]
    for i in l:
            returnArg.append(arg[i])
            returnIsToFit.append(xmltools.convertText(istofit[i],datatype='bool'))
    M.Arg=returnArg
    M.istofit=returnIsToFit
    #print M
    return M
        
                  
