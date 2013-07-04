from PyQt4 import QtGui, QtCore
import guidata
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
import numpy
from pySAXS.LS import LSusaxs
from pySAXS.guisaxs.dataset import *
from pySAXS.guisaxs.qt import plugin
from pySAXS.LS import  invariant

classlist=['pluginInvariant'] #need to be specified

class pluginInvariant(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Calculate Invariant"
    subMenuText="invariant"
    #subMenuText="Background and Data correction"
        
    def execute(self):
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return

        
        self.DPQ=self.selectedData+" invariant low q"
        self.data_dict[self.DPQ]=dataset(self.DPQ,\
                                              self.data_dict[self.selectedData].q,\
                                              self.data_dict[self.selectedData].i,\
                                              comment="invariant low q",\
                                              type='calculated',
                                              parent=[self.selectedData])
        
        self.DGQ=self.selectedData+" invariant high q"
        self.data_dict[self.DGQ]=dataset(self.DGQ,\
                                              self.data_dict[self.selectedData].q,\
                                              self.data_dict[self.selectedData].i,\
                                              comment="invariant high q",\
                                              type='calculated',
                                              parent=[self.selectedData])
        
        
        
        self.q=self.data_dict[self.selectedData].q
        self.i=self.data_dict[self.selectedData].i
        qmini=self.q[0]
        qmaxi=self.q[-1]
        self.radius=300.0
        self.invariant=invariant.invariant(self.q,self.i,radius=self.radius,printout=self.printTXT)
        
        #dataset for low q range
        self.data_dict[self.DPQ].q=self.invariant.LowQq
        self.data_dict[self.DPQ].i=self.invariant.LowQi
        #dataset for high q range
        self.data_dict[self.DGQ].q=self.invariant.HighQq
        self.data_dict[self.DGQ].i=self.invariant.HighQi
        self.redrawTheList()
        self.Replot()
        
        
        #here we use guidata to generate a dialog box
        items = {"dataname":dataitems.StringItem("Datas :",self.selectedData).set_prop("display", active=False),
                 "bg": datatypes.BeginGroup("Variables :"),
                 "qmin":dataitems.FloatItem("q minimum :",qmini).set_prop("display", callback=self.calculateAll),
                 "radius": dataitems.FloatItem("estimate radius of giration (A)",self.radius).set_prop("display", callback=self.calculateAll),
                 "qmax": dataitems.FloatItem("q maximum :",qmaxi).set_prop("display", callback=self.calculateAll),
                 "B":dataitems.FloatItem("Large angle extrapolation (cm-5): ",self.invariant.B).set_prop("display", callback=self.calculateAll),
                 "eg":datatypes.EndGroup("Variables :"),
                 "bg2":datatypes.BeginGroup("Calculations :"),
                 "P1":dataitems.FloatItem("Small Angle part (cm-4)=",self.invariant.P1).set_prop("display", active=False),
                 "P2":dataitems.FloatItem("Middle Angle part (cm-4)= ",self.invariant.P2).set_prop("display", active=False),
                 "P3":dataitems.FloatItem("Large Angle part (cm-4)= ",self.invariant.P3).set_prop("display", active=False),
                 "Invariant":dataitems.FloatItem("Invariant (cm-4)= ",self.invariant.invariant).set_prop("display", active=False),
                 "volume":dataitems.FloatItem("Particule Volume (cm3) = ",self.invariant.volume).set_prop("display", active=False),
                 "eg2":datatypes.EndGroup("Calculations :"),       
        }
        clz = type("Invariant :", (datatypes.DataSet,), items)
        self.dlg = clz()
        self.dlg.edit() 
        #print "close" 
        
    def calculateAll(self,instance,item,value):#qmini,radius,qmaxi,B,other=None):
            #print "item: ", item, "value:", value
            qmini=instance.qmin
            radius=instance.radius
            qmaxi=instance.qmax
            B=instance.B
            #print qmini,radius,qmaxi,B
            #"--- Calculating Invariant ---")
            self.invariant.calculate(radius, qmini, qmaxi, B)
            
            #update dataset
            #dataset for low q range
            
            self.data_dict[self.DPQ].q=self.invariant.LowQq
            self.data_dict[self.DPQ].i=self.invariant.LowQi
            #dataset for high q range
            self.data_dict[self.DGQ].q=self.invariant.HighQq
            self.data_dict[self.DGQ].i=self.invariant.HighQi
            self.redrawTheList()
            self.Replot()
            
            #update 
            self.dlg.P1=self.invariant.P1
            self.dlg.P2=self.invariant.P2
            self.dlg.P3=self.invariant.P3
            self.dlg.invariant=self.invariant.invariant
            self.dlg.volume=self.invariant.volume       