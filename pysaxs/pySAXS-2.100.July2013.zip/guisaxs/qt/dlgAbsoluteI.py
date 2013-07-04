from PyQt4 import QtGui, QtCore

from pySAXS.guisaxs.qt import dlgAbsoluteIui
import pySAXS.LS.SAXSparametersXML as SAXSparameters
import sys
from pySAXS.tools import isNumeric
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset 
#from copy import deepcopy

class dlgAbsolute(QtGui.QDialog,dlgAbsoluteIui.Ui_dlgSAXSAbsolute):
    def __init__(self,parent,saxsparameters=None,datasetname=None,printout=None,referencedata=None):
        QtGui.QDialog.__init__(self)
        
        self.datasetname=datasetname
        self.parentwindow=parent
        self.workingdirectory=self.parentwindow.getWorkingDirectory()
        self.params=saxsparameters
        #print self.params
        self.paramscopy=None
        if self.params is not None:
            self.paramscopy=self.params.copy()
        self.referencedata=referencedata
        #print 'reference data :',referencedata
        #print self.paramscopy
        #self.printout=printout
        self.printout=parent.printTXT
        #print 'printout : ',printout
        #print self.params
        if self.params is None:
            self.params=SAXSparameters.SAXSparameters(printout=printout)
            if self.referencedata is not None :
                #reference has parameters ?
                #print 'reference has parameters ?'
                if self.parentwindow.data_dict[self.referencedata].parameters is not None:
                    #print 'Found parameters in reference datas : ',self.referencedata
                    self.params=self.parentwindow.data_dict[self.referencedata].parameters.copy()
                else:
                    father=self.parentwindow.data_dict[self.referencedata].parent
                    if father is not None:
                        #try to get parameters from parents
                        if self.parentwindow.data_dict[father[0]].parameters is not None:
                            #print 'Found parameters in father of reference datas : ',father[0]
                            self.params=self.parentwindow.data_dict[father[0]].parameters.copy()
        self.params.printout=self.printout                    
        #setup UI    
        self.setupUi(self)
        self.ConstructUI()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        
    def ConstructUI(self):
        #---- set the text
        if self.datasetname<>None:
            self.labelDataset.setText(self.datasetname)
            
        #--- dynamic controls
        self.listStaticText={}
        self.listTextCtrl={}
        
        #-sorting parameters
        paramslist=self.params.order()
        #- controls
        i=0
        for name in paramslist:
            par=self.params.parameters[name]
            self.listStaticText[name] = QtGui.QLabel(par.description+" : ",self.groupBox)
            self.listStaticText[name].setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            self.formLayout.setWidget(i, QtGui.QFormLayout.LabelRole, self.listStaticText[name])
            self.listTextCtrl[name]=QtGui.QLineEdit(str(par.value),self.groupBox)
            self.formLayout.setWidget(i, QtGui.QFormLayout.FieldRole, self.listTextCtrl[name])
            if par.datatype=="float":
                self.listTextCtrl[name].setValidator(QtGui.QDoubleValidator())
            elif par.datatype=="int":
                self.listTextCtrl[name].setValidator(QtGui.QIntValidator())
            if par.formula is not None:
                self.listTextCtrl[name].setReadOnly(True)
                self.listTextCtrl[name].setStyleSheet('color: blue')
                self.listStaticText[name].setStyleSheet('color: blue')          
            else:
                self.listTextCtrl[name].setReadOnly(False)
                self.listTextCtrl[name].textChanged.connect(self.onParamEdited)
                    
            i+=1
    
        self.checkIrange.setChecked(True)
        if self.referencedata is not None:
            self.groupBoxReference.setEnabled(True)
            self.txtReference.setText(str(self.referencedata))
        else :
            self.groupBoxReference.setEnabled(False)
            self.txtReference.setText(str('not defined'))
    
    def  eraseUI(self):
        '''
        erase the UI
        '''
        for name in self.listStaticText:
            self.formLayout.removeWidget(self.listStaticText[name])
            self.listStaticText[name].deleteLater()
            self.formLayout.removeWidget(self.listTextCtrl[name])
            self.listTextCtrl[name].deleteLater()
        self.listStaticText={}
        self.listTextCtrl={} 
    
    def accepted(self):
        '''
        user click on an accepted button (ok, open,...)
        do nothing
        '''
        print "on accepted"
        pass
    
    def onParamEdited(self):
        #compute
        self.Control2Params() #entries -> datas
        self.params.calculate_All(verbose=False) #calculate datas
        self.ParamsWithFormula2Control() #datas -> entries
    
    def onParamChanged(self):
        #compute
        self.Control2Params() #entries -> datas
        self.params.calculate_All() #calculate datas
        self.Params2Control() #datas -> entries
    
    def click(self,obj=None):
        name=obj.text()
        #rprint name
        if name=="OK":
            self.close()
        elif name=="Cancel":
            #print 'close'
            if self.paramscopy is not None:
                self.params=self.paramscopy.copy()
            else:
                self.params=None
            #print self.params
            self.parentwindow.data_dict[self.datasetname].parameters=self.params
            self.close()
        elif name=="Close":
            #print 'close'
            #self.params=deepcopy(self.paramscopy)
            #print self.params
            #self.parentwindow.data_dict[self.datasetname].parameters=self.params
            self.close()
        elif name=="Apply":
            self.onParamChanged()
            #apply
            #-- on wich data set ?
            if self.parentwindow is None:
                return #could not apply
            if self.datasetname<>None:
                 #-- call  the method in parentwindow
                 self.parentwindow.data_dict[self.datasetname].parameters=self.params
                 self.OnScalingSAXSApply(self.checkQrange.isChecked(),
                                              self.checkIrange.isChecked(),
                                              self.datasetname)
        elif name=="Save":
            #save
            self.saveClicked()
        elif name=="Open":
            #open
            self.openClicked()
        
    def openClicked(self):
        #-- open dialog for parameters
        fd = QtGui.QFileDialog(self)
        #get the filenames, and the filter
        filename=fd.getOpenFileName(self, caption="SAXS parameter",filter="*.xml",directory=self.workingdirectory)
        #print "file selected: -",filename,"-"
        filename=str(filename)
        if len(filename)>0:
            self.printTXT("loading parameters file ",str(filename))
            ext=filetools.getExtension(filename)
            self.params=SAXSparameters.SAXSparameters(printout=self.printTXT)
            self.params.openXML(filename)
            self.params.parameters['filename'].value=filename
            self.params.printout=self.printTXT
            
            self.eraseUI()
            self.ConstructUI()
    
    def saveClicked(self):
        '''
        User click on save button
        '''
        self.Control2Params()
        fd = QtGui.QFileDialog(self)
        filename=fd.getSaveFileName(self, caption="SAXS parameter",filter="*.xml")
        wc = "Save parameters file(*.xml)|*.xml"
        filename=str(filename)
        if len(filename)<=0:
            return
        #check if file exist already
        if filetools.fileExist(filename):
                  ret=QtGui.QMessageBox.question(self,"pySAXS", "file "+str(filename)+" exist. Replace ?", buttons=QtGui.QMessageBox.No|QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel,\
                                                  defaultButton=QtGui.QMessageBox.NoButton)
                  if ret==QtGui.QMessageBox.No:
                      self.printTXT("file "+str(filename)+" exist. Datas was NOT replaced")
                      return
                  elif ret==QtGui.QMessageBox.Cancel:
                      return self.saveClicked()
        self.params.saveXML(filename)
        if self.params.parameters.has_key('filename'):
            self.params.parameters['filename'].value=filename
            self.onParamEdited()
        self.printTXT("parameters was saved in "+filename)
        self.parent.setWorkingDirectory(filename) #set working dir
        
    def Params2Control(self):
        for key,value in self.params.parameters.items():
            if self.listTextCtrl.has_key(key):
                self.listTextCtrl[key].setText(str(self.params.parameters[key].value))

    def ParamsWithFormula2Control(self):
        for key,value in self.params.parameters.items():
            if self.listTextCtrl.has_key(key):
                if self.params.parameters[key].formula is not None:
                    #print "----------",key," : ",self.params.parameters[key].value
                    self.listTextCtrl[key].setText(str(self.params.parameters[key].value))

    def Control2Params(self):
        for key,value in self.params.parameters.items():
            #print key,value,self.params.parameters[key].datatype
            if (self.params.parameters[key].datatype=='float') or (self.params.parameters[key].datatype=='int'):
                if isNumeric.isNumeric(self.listTextCtrl[key].text()):
                    self.params.parameters[key].value=float(self.listTextCtrl[key].text())
                    #print "changed", self.params.parameters[key].value
            else:
                self.params.parameters[key].value=str(self.listTextCtrl[key].text())
            #print var,self.params.parameters[var]
     
    def OnScalingSAXSApply(self,applyQ,applyI,dataname):
        '''
        child dialog box ask to apply parameters
        '''
        #-- 1 create new datas
        q=self.parentwindow.data_dict[dataname].q
        i=self.parentwindow.data_dict[dataname].i
        saxsparameters=self.parentwindow.data_dict[dataname].parameters
        print saxsparameters
        error=self.parentwindow.data_dict[dataname].error
        #-- 2 apply parameters
        self.parentwindow.printTXT("------ absolute intensities ------")
        if applyQ:
            self.parentwindow.printTXT("--set q range --")
            q=saxsparameters.calculate_q(q)
        if applyI:
            if self.checkSubstractRef.isChecked():
                b=self.parentwindow.data_dict[self.referencedata].i
                i,error=saxsparameters.calculate_i(i,deviation=error,b=b)
            else :
                i,error=saxsparameters.calculate_i(i,deviation=error)
            self.parentwindow.printTXT("------ absolute intensities END ------")
        #-- 3 replot
        col=None
        if self.parentwindow.data_dict.has_key(dataname+' scaled'):
            col=self.parentwindow.data_dict[dataname+' scaled'].color
        self.parentwindow.data_dict[dataname+' scaled']=dataset.dataset(dataname+' scaled',q,i,dataname+' scaled',\
                                                   parameters=None,error=error,\
                                                   type='scaled',parent=[dataname],color=col)
        self.parentwindow.redrawTheList()
        self.parentwindow.Replot()
        
    def printTXT(self,txt="",par=""):
        '''
        for printing messages
        '''
        if self.printout==None:
            print(str(txt)+str(par))
        else:
            self.printout(txt,par)
        
if __name__ == "__main__":
      app = QtGui.QApplication(sys.argv)
      param=SAXSparameters.SAXSparameters()
      dlg=dlgAbsolute(None,param,"test")
      dlg.exec_()
      