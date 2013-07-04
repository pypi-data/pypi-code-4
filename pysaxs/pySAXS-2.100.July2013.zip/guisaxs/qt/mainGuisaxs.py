# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
mainGuisaxs a new GUI made with qt
author : Olivier Tache
(C) CEA 2012
"""

from PyQt4 import QtGui, QtCore
import sys
import unicodedata
from pySAXS.tools import isNumeric
from pySAXS.guisaxs.qt import QtMatplotlib
#from pySAXS.guisaxs.qt import Qtguiqwt
from pySAXS.guisaxs.qt import mainGuisaxsui
from pySAXS.guisaxs.qt import dlgClipQRange
from pySAXS.guisaxs.qt import dlgConcatenate
from pySAXS.guisaxs.qt import dlgCalculator
from pySAXS.guisaxs.qt import dlgAbsoluteI
from pySAXS.guisaxs.qt import pluginUsaxs
try:
    from pySAXS.guisaxs.qt import pluginFAI
except:
    pass
from pySAXS.guisaxs.qt import dlgModel
from pySAXS.guisaxs.qt import dlgTextView
from pySAXS.guisaxs.qt import dlgAbsorption

from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import colors
import matplotlib.font_manager as font_manager
from pySAXS.guisaxs import pySaxsColors
import os
from os import path
import pySAXS
import itertools
import numpy
from scipy import stats
from pySAXS.guisaxs.dataset import *
from pySAXS.tools import filetools
from pySAXS.tools import DetectPeaks
import unicodedata
import pySAXS.LS.SAXSparametersXML as SAXSparameters
from pySAXS.models import listOfModels
import pySAXS.models

import guidata
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
from pySAXS.guisaxs.qt import preferences
  
ICON_PATH=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'qt'+os.sep    

#type of datas [description, file extension, color]
typefile={'usaxs':['USAXS Raw Data file','txt','BLUE'],\
                  'usaxsrck':['USAXS Rocking Curve','txt','MAROON' ],\
                  'usaxsdsm':['USAXS Desmeared File','dsm','MAROON'],\
                  'saxs':['SAXS raw datas','rgr','FIREBRICK'],\
                  'fit2d':['datas from fit2D','chi','RED'],\
                  'txttab':['datas in 2 columns (or 3 with error) with tab separator','*','MAROON'],\
                  'txtcomma':['datas in 2 columns (or 3 with error) with comma separator','*','PURPLE'],\
                  'scaled':['datas scaled','*','TEAL'],\
                  'calculated':['datas calculated','*','PURPLE'],\
                  'referenceVal':['reference','*','VIOLET RED'],\
                  'reference':['reference datas','*','VIOLET RED'],\
                  'model':['model','*','GREEN'],\
                  'supermodel':['super model','*','INDIAN RED'],\
                  'resfunc':['USAXS resolution function','dat','MAROON']}
        
#list of data type to propose in open file dialog        
typefile_list=['saxs','usaxs','usaxsrck','usaxsdsm','fit2d','txttab','txtcomma','resfunc'] 

class mainGuisaxs(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui =mainGuisaxsui.Ui_mainGuisaxsWindows()
        self.ui.setupUi(self)
        self.setWindowTitle("pySAXS")
        self.icon=QtGui.QIcon(ICON_PATH+'pySaxs.png')
        self.setWindowIcon(self.icon)
        self.DatasetFilename=""
        self.workingdirectory=""
        self.referencedata=None
        self.setAcceptDrops(True)
        
        #-- colors
        self.colors=pySaxsColors.pySaxsColors()
        
        #-- get preferences
        self.pref=preferences.prefs()
        if self.pref.fileExist():
            self.pref.read()
            #print "file exist"
            dr=self.pref.get('defaultdirectory')
            if dr is not None:
                self.workingdirectory=dr
                #print 'set wd',dr
        else:
            self.pref.save()
        #print 'last file : ',self.pref.getLastFile()
        #add the recent file menu
        rec=self.pref.getRecentFiles()
        for name in rec:
            name=name.strip('\'\"')
            action=self.ui.menuRecents.addAction(name)#add text in the menu
            item=name
            self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnRecentFile(item))
        self.ui.menuFile.addAction(self.ui.menuRecents.menuAction())
        #-- connect menus
        #File
        QtCore.QObject.connect(self.ui.actionOpen,QtCore.SIGNAL("triggered()"),self.OnFileOpen)
        QtCore.QObject.connect(self.ui.actionOpen_Dataset,QtCore.SIGNAL("triggered()"),self.OnFileOpenDataset)
        QtCore.QObject.connect(self.ui.actionAppend_Dataset,QtCore.SIGNAL("triggered()"),self.OnFileAppendDataset)
        QtCore.QObject.connect(self.ui.actionSave,QtCore.SIGNAL("triggered()"),self.OnFileSave)
        QtCore.QObject.connect(self.ui.actionSave_As,QtCore.SIGNAL("triggered()"),self.OnFileSaveAs)
        QtCore.QObject.connect(self.ui.actionExport,QtCore.SIGNAL("triggered()"),self.OnFileExport)
        QtCore.QObject.connect(self.ui.actionReset_datas,QtCore.SIGNAL("triggered()"),self.OnFileResetDatas)
        QtCore.QObject.connect(self.ui.actionExit,QtCore.SIGNAL("triggered()"),self.close)
        #Edit
        QtCore.QObject.connect(self.ui.actionSelect_All,QtCore.SIGNAL("triggered()"),self.OnEditSelectAll)
        QtCore.QObject.connect(self.ui.actionUnselect_All,QtCore.SIGNAL("triggered()"),self.OnEditUnselectAll)
        QtCore.QObject.connect(self.ui.actionRefresh_from_file,QtCore.SIGNAL("triggered()"),self.OnEditRefresh)
        QtCore.QObject.connect(self.ui.actionRename,QtCore.SIGNAL("triggered()"),self.OnEditRename)
        QtCore.QObject.connect(self.ui.actionRemove,QtCore.SIGNAL("triggered()"),self.OnEditRemove)
        QtCore.QObject.connect(self.ui.actionDuplicate,QtCore.SIGNAL("triggered()"),self.OnEditDuplicate)
        QtCore.QObject.connect(self.ui.actionDuplicate_without_links,QtCore.SIGNAL("triggered()"),self.OnEditDuplicateWLinks)
        QtCore.QObject.connect(self.ui.actionClip_Q_range,QtCore.SIGNAL("triggered()"),self.OnEditClipQRange)
        QtCore.QObject.connect(self.ui.actionScale_Q_range,QtCore.SIGNAL("triggered()"),self.OnEditScaleQ)
        QtCore.QObject.connect(self.ui.actionConcatenate,QtCore.SIGNAL("triggered()"),self.OnEditConcatenate)
        QtCore.QObject.connect(self.ui.actionDerivate,QtCore.SIGNAL("triggered()"),self.OnEditDerivate)
        QtCore.QObject.connect(self.ui.actionFind_Peaks,QtCore.SIGNAL("triggered()"),self.OnEditFindPeaks)
        QtCore.QObject.connect(self.ui.actionSmooth,QtCore.SIGNAL("triggered()"),self.OnEditSmooth)
        QtCore.QObject.connect(self.ui.actionCalculator,QtCore.SIGNAL("triggered()"),self.OnEditCalculator)
        QtCore.QObject.connect(self.ui.actionStatistics,QtCore.SIGNAL("triggered()"),self.OnEditStat)
        QtCore.QObject.connect(self.ui.actionGenerate_Noise,QtCore.SIGNAL("triggered()"),self.OnEditGenerateNoise)
        QtCore.QObject.connect(self.ui.actionAddReferenceValue,QtCore.SIGNAL("triggered()"),self.OnEditAddReference)
        QtCore.QObject.connect(self.ui.actionRemove_dependencies,QtCore.SIGNAL("triggered()"),self.OnEditRemoveDependencies)
        QtCore.QObject.connect(self.ui.actionChange_color,QtCore.SIGNAL("triggered()"),self.OnEditChangeColor)
        QtCore.QObject.connect(self.ui.actionSet_as_reference,QtCore.SIGNAL("triggered()"),self.OnEditSetAsReference)
        
        
        QtCore.QObject.connect(self.ui.actionCalculate_Resolution_function,QtCore.SIGNAL("triggered()"),self.NotYetImplemented)
        QtCore.QObject.connect(self.ui.actionInvariant,QtCore.SIGNAL("triggered()"),self.NotYetImplemented)
        QtCore.QObject.connect(self.ui.actionX_ray_absorption,QtCore.SIGNAL("triggered()"),self.OnToolsAbsorption)
        QtCore.QObject.connect(self.ui.actionChanges,QtCore.SIGNAL("triggered()"),self.OnHelpChanges)
        QtCore.QObject.connect(self.ui.actionLicence,QtCore.SIGNAL("triggered()"),self.OnHelpLicense)
        QtCore.QObject.connect(self.ui.actionAbout,QtCore.SIGNAL("triggered()"),self.OnHelpAbout)
        
        
        #-- connect other objects
        #QtCore.QObject.connect(self.ui.treeWidget, QtCore.SIGNAL("itemChanged(QTreeWidgetItem*, int)"),self.OnItemChanged) #itemPressed 
        QtCore.QObject.connect(self.ui.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem*, int)"),self.OnItemChanged)
        QtCore.QObject.connect(self.ui.treeWidget, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem*, int)"),self.OnItemDoubleClicked)
        self.ui.treeWidget.setHeaderLabels(["Datas"])
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.popup)
        #------------ main object  for datas 
        self.data_dict={}
        #generate filters names self.filterList
        self.createFilters()
        
        #---- Matplotlib window
        self.move(QtCore.QPoint(100,100))
        self.createPlotframe()
        QtCore.QObject.connect(self.plotframe, QtCore.SIGNAL("closing()"), self.OnPlotframeClosed)
    
        self.printTXT("<b>--- Welcome to GuiSAXS in QT ---</b>")
        
        #test for creation of an automatic plugin menu
        p=path.dirname(pySAXS.__file__)
        p+=os.sep+'guisaxs'+os.sep+'qt'
        pl= self.plugins_list(p)    #get the list of the plugins 
        base="pySAXS.guisaxs.qt."
        #objlist=[]
        submenuDict={}
        for name in pl:
            try:
                m=self.my_import(base+name) #import plugins
                cl= m.classlist             #the the class list from the plugin
                #print cl
                for c in cl:
                    o=getattr(m,c)          #create an object 
                    #objlist.append(o)
                    #print o.menu,o.subMenu,o.subMenuText #get the menus
                    sub=o.subMenu
                    item=o
                    '''if o.subMenuText=='':
                        #no submenu, just an action
                        action = self.ui.menuData_Treatment.addAction(o.subMenu) #add in the menu
                        self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.callPlugin(item))
                    else:'''
                    if not submenuDict.has_key(sub):
                            #submenu doesn t exist
                            itemSub = QtGui.QMenu(self.ui.menuData_Treatment)
                            itemSub.setObjectName(sub)
                            itemSub.setTitle(sub)
                            submenuDict[sub]=itemSub
                    #submenu exist
                    itemSub=submenuDict[sub]
                    action = itemSub.addAction(o.subMenuText) #add in the menu
                    self.ui.menuData_Treatment.addAction(itemSub.menuAction())
                    self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.callPlugin(item))
            except:
                pass
        #self.ui.menuData_Treatment
        menuModels = QtGui.QMenu(self.ui.menuFit) #add in the menu
        menuModels.setTitle('Models')
        menuModels.setObjectName('Models')
        # self.ui.menuData_Treatment.addAction(itemSub.menuAction())
        modelsDict=listOfModels.listOfModels() #get {'Spheres Monodisperse': 'MonoSphere', 'Gaussian': 'Gaussian'}
        dd=modelsDict.items()               #[('Spheres Monodisperse', 'MonoSphere'), ('Gaussian', 'Gaussian')]
        dd=self.sortDictByKey(modelsDict)
        self.modelsDictId={}
        for id in range(len(dd)):
            #construct a dictionary of models with id item
            #{0,('Spheres Monodisperse', 'MonoSphere') : 1,('Gaussian', 'Gaussian')}
            self.modelsDictId[id]=dd[id]
            #item = submenu.Append(id, dd[id][0])
            #self.Bind(wx.EVT_MENU, self.OnModelSelect, item)
            action=menuModels.addAction(dd[id][0])#add text in the menu
            
            item=dd[id][1]
            self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.callModel(item))
        self.ui.menuFit.addAction(menuModels.menuAction())
        '''    
        self.numberOfModels=id
        supermodelsDict=listOfModels.listOfSuperModels() #get {'Spheres Monodisperse': 'MonoSphere', 'Gaussian': 'Gaussian'}
        dd=supermodelsDict.items()#[('Spheres Monodisperse', 'MonoSphere'), ('Gaussian', 'Gaussian')]
        dd=self.sortDictByKey(supermodelsDict)
        self.supermodelsDictId={}
        for ids in range(len(dd)):
            #construct a dictionary of models with id item
            #{0,('Spheres Monodisperse', 'MonoSphere') : 1,('Gaussian', 'Gaussian')}
            self.supermodelsDictId[ids]=dd[ids]
            item = submenu.Append(self.numberOfModels+ids, "SUPER : "+dd[ids][0])
            self.Bind(wx.EVT_MENU, self.OnSuperModelSelect, item)

        item = menuModels.AppendMenu(wx.ID_ANY, 'Models',submenu)
        self.mainmenu.Append(menuModels, 'Compute') # Add the file menu to the menu bar.
        '''
        
        #---- menu doc
        self.docs=self.getListOfDocs()
        i=0
        for name in self.docs:
           action = self.ui.menuDocuments.addAction(path.basename(name))
           item=name
           self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnOpenDocument(item))
        
        
    def callPlugin(self,obj):
        label=self.getCurrentSelectedItem()
        child=obj(self,label)
        child.execute()
    
    def callModel(self,modelname):
        #start model dlg
        label=self.getCurrentSelectedItem()
        M=getattr(pySAXS.models,modelname)()#create a new model
        if M.WarningForCalculationTime:
            ret=QtGui.QMessageBox.question(self,"pySAXS", "Computation time can be high for this model. Continue ?", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if ret!=QtGui.QMessageBox.Yes:
                return
        self.openModel(M, label)
    
    def openModel(self,M,label):
            if label is None:
                '''
                no data checked
                add a new dataset with an empty model
                '''
                data_selected_for_model=M.name
                self.data_dict[data_selected_for_model]=dataset(data_selected_for_model,
                                                                     M.q,
                                                                     M.getIntensity(),
                                                                     "",
                                                                     True,
                                                                     M,
                                                                     type="model")#new data set checked
                self.childmodel=dlgModel.dlgModel(self,data_selected_for_model,type="model")
            else:
                ''' data is checked '''
                
                data_selected_for_model=label
                new_dataname=data_selected_for_model+"-"+M.name+" model"
                q=self.data_dict[data_selected_for_model].q
                M.q=q
                i=M.getIntensity() #intensity by default
                filename=self.data_dict[data_selected_for_model].filename
                self.data_dict[new_dataname]=dataset(new_dataname,copy(q),
                                                        copy(i),
                                                        filename,
                                                        True,
                                                        M,#reference to model
                                                        parent=[data_selected_for_model],
                                                        rawdata_ref=data_selected_for_model,
                                                        type="model")#reference to original datas
                self.childmodel=dlgModel.dlgModel(self,new_dataname,type="data")
            
            self.redrawTheList()
            self.Replot()
            #self.childmodel.exec_()
            self.childmodel.show()
            #return self.childmodel
        
    def sortDictByKey(self,d):
        '''
        return list of couple sorted by key
        '''
        l=[]
        for key in sorted(d.iterkeys()):
            l.append((key, d[key]))
        return l
        
    def popup(self, pos):
        '''
        display the Edit menu on popup
        '''
        menu = self.ui.menuEdit
        action = menu.exec_(self.mapToGlobal(pos))
        

    def closeEvent(self, event):
        '''
        whan window is closed
        '''
        try:
            self.plotframe.close()
        except:
            pass
    
    def createPlotframe(self):
        '''
        create the plotframe
        '''
        space=15
        self.plotframe=QtMatplotlib.QtMatplotlib(self)
        
        #self.plotframe=Qtguiqwt.QtGuiqwt()
        x=self.width()+self.x() + space
        y=self.y()
        self.plotframe.move(x, y)
        self.plotframe.resize(self.width()*1.5,self.height())
        self.plotframe.setWindowTitle("Guisaxs Plot")
        self.plotframe.setScaleLabels('$q(\AA^{-1})$', 'I',size=10)
        self.plotframe.setAxesFormat(QtMatplotlib.LOGLOG)
        self.plotframe.show()
        '''
        self._matplotlib = True
        '''
    def OnPlotframeClosed(self):
        '''
        when plotframe is closed
        '''
        self.plotframe=None

    def createFilters(self):
        '''
        create file filters
        '''
        self.filterList=''
        #wc = ''
        #self.filterList = QtCore.QStringList()
        self.filterDict = {}
        for k in typefile_list:
            filterName = typefile[k][0] + ' (*.' + typefile[k][1] + ')'
            self.filterList+=filterName+';;'
            #self.filterList.append(QtCore.QString(filterName))
            self.filterDict[filterName] = k
            #wc += typefile[k][0] + ' (*.' + typefile[k][1] + ');;'
        #return wc

    def OnRecentFile(self,name):
        '''
        user clicked on recent file
        '''
        #print "open", name
        extension=filetools.getExtension(name) #now we use the extension
        if extension!='xml':
            #data file
            for type in typefile_list:
                if typefile[type][1]==extension:
                    #self.printTXT('type of '+name+ 'is :', type)
                    self.OnFileOpen([name],type)
                    return
            self.printTXT('Don\'t know the type of :', name)
            self.OnFileOpen([name])
        else:
            #dataset
            if len(self.data_dict)>0:
                reply=QtGui.QMessageBox.question(self, 'pySAXS error',\
                                             'There is already an open dataset. Do you want to overwrite ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
                if reply == QtGui.QMessageBox.No:
                    return
            self.OnFileOpenDataset(name)
            
        

    def OnFileOpen(self,filenames=None,file_type=None):
        '''
        Load datas
        '''
        '''if self.data_dict.has_key('exp'):
            msgBox=QtGui.QMessageBox()
            msgBox.setText("Dataset is not empty. ")
            msgBox.setInformativeText("Do you want to reset active sample datas before loading new ?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok |QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
            ret = msgBox.exec_()
            print ret
            if ret!=QtGui.QMessageBox.Ok:
                return
        '''
        if filenames is None:
            #call the dialog box
            fd = QtGui.QFileDialog(self)
            #get the filenames, and the filter
            filenames,filter=fd.getOpenFileNamesAndFilter(filter=self.filterList,initialFilter=('*.*'),directory=self.workingdirectory)
            #print "filter selected: ",filter
            if len(filenames)<=0:
                return
            #filter_key=typefile_list[filter_index]
            file_type=self.filterDict[str(filter)]
            #print "file_type : ",file_type
        
        for datafilename in filenames:
                self.printTXT("opening " + datafilename) 
                datafilename=str(datafilename)
                #extension=filetools.getExtension(datafilename) #now we use the extension
                self.ReadFile(datafilename,file_type)
        #save in preferences
        self.setWorkingDirectory(datafilename)
        #redraw
        self.redrawTheList()
        self.Replot()
    
    def OnFileOpenDataset(self,filename=None):
        '''
        open the data set
        '''
        if len(self.data_dict)>0:
            #print "hello"
            reply=QtGui.QMessageBox.question(self, 'pySAXS error',\
                                                'There is already an open dataset. Do you want to overwrite ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
            if reply == QtGui.QMessageBox.No:
                return
        if filename is None:
            #-- open dialog for parameters
            fd = QtGui.QFileDialog(self)
            #get the filenames, and the filter
            wc = "dataset  xml file (*.xml);;dataset file(*.dst)"
            filenames,filter=fd.getOpenFileNamesAndFilter(filter=wc,initialFilter=('*.dst'),directory=self.workingdirectory)
            #print "filter selected: ",filter
            if len(filenames)<=0:
                return
            filename=str(filenames[0])
        ext=filetools.getExtension(filename)             
        if str(ext).find('dst')>=0:
            self.data_dict=getDataDictRaw(filename)
            #for compatibility with new dataset
            for name in self.data_dict:
                self.data_dict[name].parent=None
                
        else:
            self.data_dict=getDataDictFromXMLFile(filename)
        
        #check the colors
        colors=pySaxsColors.pySaxsColors()
        l=[]
        for name in self.data_dict:
            l.append(name)
            if self.data_dict[name].type=='reference':
                self.referencedata=name
        l.sort()
        i=0
        for name in l:
            if self.data_dict[name].color is None:
                #set a color
                col=colors.getColor(i)
                self.data_dict[name].color=col
                i+=1
                
        self.setWorkingDirectory(filename)
        self.redrawTheList()
        self.Replot()
        self.setWindowTitle(filename)
        self.DatasetFilename=filename
        self.printTXT("open dataset : ",filename)
    
    def OnFileAppendDataset(self):
        '''
        append a data set
        '''
        #-- open dialog for parameters
        fd = QtGui.QFileDialog(self)
        #get the filenames, and the filter
        wc = "dataset  xml file (*.xml);;dataset file(*.dst)"
        filenames,filter=fd.getOpenFileNamesAndFilter(filter=wc,initialFilter=('*.dst'),directory=self.workingdirectory)
        #print "filter selected: ",filter
        filename=str(filenames[0])
        self.setWorkingDirectory(filename)
        if len(filenames)<=0:
            return
        ext=filetools.getExtension(filename)             
        if str(filter).find('dst')>=0:
            new_data_dict=getDataDictRaw(filename)
            #for compatibility with new dataset
            for name in self.data_dict:
                new_data_dict[name].parent=None
                
        else:
            new_data_dict=getDataDictFromXMLFile(filename)
        #append
        for name in new_data_dict:
            if self.data_dict.has_key(name):
                    newname=name+" "+self.giveMeANewName()
                    self.printTXT(name+" dataset already exist, renamed as "+newname)
                    new_data_dict[name].name=newname
                    self.data_dict[newname]=new_data_dict[name]
            else:
                    self.data_dict[name]=new_data_dict[name]
        self.redrawTheList()
        self.Replot()
        self.printTXT("open dataset : ",filename)
        
        
    def OnFileSave(self):
        '''
        save the dataset in the same file
        '''
        #when dataset filename is empty file save as
        if self.DatasetFilename=="":
            if len(self.data_dict)>0:
                self.OnFileSaveAs()
            return
        
        filename=self.DatasetFilename
        saveDataDictOnXMLFile(filename,self.data_dict)
        self.DatasetFilename=filename
        self.setWindowTitle(filename)
        self.printTXT("datas saved in file "+filename)
    
    def OnFileSaveAs(self):
        '''
        save the checked datas
        '''
        #-- open dialog for parameters
        fd = QtGui.QFileDialog(self)
        #get the filenames, and the filter
        wc = "dataset  xml file (*.xml)"
        filename=fd.getSaveFileName (filter=wc,directory=self.workingdirectory)
        filename=str(filename)
        self.setWorkingDirectory(filename) #set working dir
        if  filename!="":
            #check if file exist already
            if filetools.fileExist(filename):
                reply=QtGui.QMessageBox.question(self, 'pySAXS Question',\
                                                'File exist. Do you want to replace ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
                if reply == QtGui.QMessageBox.No:
                    self.printTXT("file "+str(filename)+" exist. Datas were NOT replaced")
                    return
                
            saveDataDictOnXMLFile(filename,self.data_dict)
            self.setWindowTitle(filename)
            self.DatasetFilename=filename
            self.printTXT("datas saved in file "+filename)
    
    def OnFileExport(self):
        '''
        save the checked datas in txt
        '''
        #-- open dialog for parameters
        fd = QtGui.QFileDialog(self)
        #get the filenames, and the filter
        wc = "txt file (*.txt);"
        filename=fd.getSaveFileName(filter=wc,directory=self.workingdirectory)
        filename=str(filename)
        self.setWorkingDirectory(filename) #set working dir
        if  filename!="":
            #check if file exist already
            if filetools.fileExist(filename):
                reply=QtGui.QMessageBox.question(self, 'pySAXS Question',\
                                                'File exist. Do you want to replace ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
                if reply == QtGui.QMessageBox.No:
                    self.printTXT("file "+str(filename)+" exist. Datas were NOT replaced")
                    return
                
            self.SaveAsTXT(filename)
            self.setWindowTitle(filename)
            self.DatasetFilename=filename
            

    def SaveAsTXT(self,filename):
        '''
        save the checked datas
        '''
        self.printTXT("-------------------")
        self.printTXT("Saving data as txt in " + filename) 
        l=self.ListOfDatasChecked()
        f=open(filename,mode='w')
        #--- header
        header1='#'
        header2='#'
        nrows=0
        for name in l:
            self.printTXT( name)
            header1+=name+'\t\t'
            header2+='q\t i\t'
            if self.data_dict[name].error<>None:
                header1+='\t'
                header2+='error\t'
            if len(self.data_dict[name].q)>nrows:
                nrows=len(self.data_dict[name].q)
        header1+='\n'
        header2+='\n'
        f.write(header1)
        f.write(header2)
        self.printTXT(str( nrows)+" rows will be saved")
        #-- datas
        for n in range(nrows):
            dat=''
            for name in l:
                if n<len(self.data_dict[name].q):
                    dat+=str(self.data_dict[name].q[n])+'\t'
                    dat+=str(self.data_dict[name].i[n])+'\t'
                    if self.data_dict[name].error<>None:
                         dat+=str(self.data_dict[name].error[n])+'\t'
                else:
                    dat+='\t\t'
                    if self.data_dict[name].error<>None:
                        dat+='\t'
            dat+='\n'
            f.write(dat)
        self.printTXT("data are saved")
        self.printTXT("-------------------")
        f.close()

    
    def OnFileResetDatas(self):
        '''
        clear the datas
        '''
        self.setWindowTitle("pySAXS")
        self.DatasetFilename=""
        self.data_dict.clear()
        self.redrawTheList()
        self.Replot()
        
        
    def OnEditSelectAll(self):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=True
        self.redrawTheList()
        self.Replot()
        
    
    def OnEditUnselectAll(self):
        '''
        when the user want to select all
        '''
        for label in self.data_dict:
            self.data_dict[label].checked=False
        self.redrawTheList()
        self.Replot()
    
    def OnEditRefresh(self):
        '''
        refresh data from file (is exist)
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        filename=self.data_dict[label].filename
        type=self.data_dict[label].type
        if type!=None:
            self.printTXT("refresh "+ filename)
            self.ReadFile(filename,type)
            self.Replot()
        else:
            self.printTXT('type of data unknown -> not possible to refresh datas ')
    
    def OnEditRename(self):
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        newlabel, ok = QtGui.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:',text=label)
        newlabel=str(newlabel)
        if ok:
            newlabel=self.cleanString(newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtGui.QMessageBox.question(self, 'pySAXS Question', 'There is already a data set with this name ! Replace ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
                if reply == QtGui.QMessageBox.No:
                    return
            #print newlabel
            self.printTXT("Rename  "+label+" into : ",newlabel)
            self.data_dict[newlabel]=self.data_dict[label]
            self.data_dict[newlabel].name=newlabel
            self.data_dict.pop(label)
            self.redrawTheList()
            self.Replot()
    
    def OnEditRemove(self):
        '''
        remove a data set
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        reply=QtGui.QMessageBox.question(self, 'pySAXS Question', 'Are you sure you want to remove this data set : '+label+' ?', QtGui.QMessageBox.No | QtGui.QMessageBox.Yes )
        if reply == QtGui.QMessageBox.Yes:
            #remove
            self.printTXT("removing ",label)
            self.data_dict.pop(label)
            self.redrawTheList()
            self.Replot()
            
    def OnEditDuplicate(self):
        '''
        duplicate a data set
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        newlabel, ok = QtGui.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:',text=label)
        newlabel=str(newlabel)
        if ok:
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtGui.QMessageBox.warning(self, 'pySAXS Error', 'There is already a data set with this name !')
                return
            self.data_dict[newlabel]=self.data_dict[label]._deepcopy()
            self.data_dict[newlabel].name=newlabel
            self.redrawTheList()
            self.RePlot()
    
    def OnEditDuplicateWLinks(self):
        '''
        duplicate a data set without links
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        newlabel, ok = QtGui.QInputDialog.getText(self, 'pySAXS', 'Enter the new name:')
        newlabel=str(newlabel)
        if ok:
            self.printTXT('duplicate dataset : '+label+' to '+ newlabel)
            if self.data_dict.has_key(newlabel):
                reply=QtGui.QMessageBox.warning(self, 'pySAXS Error', 'There is already a data set with this name !')
                return
            self.data_dict[newlabel]=self.data_dict[label]._deepcopy()
            self.data_dict[newlabel].parent=None
            self.data_dict[newlabel].name=newlabel
            self.redrawTheList()
            self.RePlot()
            
    def OnEditClipQRange(self):
        '''
        clip q range
        '''
        dataset_name=self.getCurrentSelectedItem()
        if dataset_name is None:
            self.noDataErrorMessage()
            return
        
                
        datas=self.data_dict[dataset_name]
        qmin=datas.q.min()
        qmax=datas.q.max()
        nbpoints=len(datas.q)
        '''
        dlg=dlgClipQRange.dlgClipQRange(dataset_name,qmin,qmax)
        if dlg.exec_():
            qmin, qmax= dlg.getValues()
        '''
        #here we use guidata to generate a dialog box
        items = {
         "dataname": dataitems.StringItem("datas :",dataset_name).set_prop("display", active=False),
         "qmin" : dataitems.FloatItem("qmin :",qmin),
         "qmax" : dataitems.FloatItem("qmax :",qmax)
         }
        clz = type("Clip q range :", (datatypes.DataSet,), items)
        dlg = clz()
        dlg.edit()  
        qmin=dlg.qmin
        qmax=dlg.qmax  
        #end of dialog box
        
        q=numpy.array(self.data_dict[dataset_name].q)
        i=numpy.array(self.data_dict[dataset_name].i)
        error=self.data_dict[dataset_name].error
        #clip q min
        if self.data_dict[dataset_name].error<>None:
            error=numpy.repeat(error,q>=qmin)
        i=numpy.repeat(i,q>=qmin)
        q=numpy.repeat(q,q>=qmin)
        #clip q max
        if self.data_dict[dataset_name].error<>None:
            error=numpy.repeat(error,q<=qmax)
        i=numpy.repeat(i,q<=qmax)
        q=numpy.repeat(q,q<=qmax)
        #clip q min
        self.data_dict[dataset_name].q=q
        self.data_dict[dataset_name].i=i
        self.data_dict[dataset_name].error=error
        #replot
        self.Replot()
        
    def OnEditScaleQ(self):
        '''
        user want to scale q with a formula
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #message box for entry
        formula, ok = QtGui.QInputDialog.getText(self, 'Formula for q scaling :', "specify a formula for q scaling",text="1*q")
        formula=str(formula)
        #add a data set
        newdataset=label+ " scaled with "+str(formula)
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        try :
                qout=eval(formula,{"q":q})
        except :
            self.printTXT("error on evaluation of "+formula)
            return
        qout=numpy.array(qout)
        self.data_dict[newdataset]=dataset(newdataset,qout,i,parent=[label])
        self.redrawTheList()
        self.Replot()
    
    def OnEditConcatenate(self):
        '''
        user want to concatenate different dataset
        '''
        #label=self.getCurrentSelectedItem()
        '''if label is None:
            return
            '''
        #create a new data set
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)<=0:
            self.noDataErrorMessage()
        #print listofdata
        newdatasetname=listofdata[0]+' new'
        '''print newdatasetname
        self.data_dict[newdatasetname]=copy(self.data_dict[listofdata[0]])
        self.data_dict[newdatasetname].name=newdatasetname'''
        dlg=dlgConcatenate.dlgConcatenate(self,newdatasetname)
        
        dlg.exec_()
        #dlg.getValues()
        #create a new data set
        #newdatasetname=listofdata[0]+' new'
        #self.data_dict[newdatasetname]=copy(self.data_dict[listofdata[0]])
        #self.data_dict[newdatasetname].name=newdatasetname
            
    def OnEditSmooth(self):
        '''
        user want to smooth dataset
        ref http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        pp, ok = QtGui.QInputDialog.getText(self, 'pySAXS Smooth parameter :', 'Smooth parameter:')
        if ok:
            if not(isNumeric.isNumeric(pp)):
                self.printTXT("value : "+str(pp)+" is not a valid numeric")
                return
            pp=float(str(pp))
            newdatasetname=label+' smooth'
            self.data_dict[newdatasetname]=self.data_dict[label]._deepcopy()
            self.data_dict[newdatasetname].parent=[label]
            self.data_dict[newdatasetname].name=newdatasetname
            q=self.data_dict[newdatasetname].q
            i=self.data_dict[newdatasetname].i
            tck = interpolate.splrep(q,i,s=pp)
            ysmooth = interpolate.splev(q,tck,der=0)
            self.data_dict[newdatasetname].i=ysmooth
            self.redrawTheList()
            self.Replot()
            
    def OnEditCalculator(self):
        '''
        show the calculator dialog box
        '''
        '''
        feedback from evaluator dialog box
        #formula="i1+i0+i2"
        #variableDict={'i0':'data1','i1':'data2',...}
        #listofdata=['data1',data2'...]
        '''
        listofdata=self.ListOfDatasChecked()
        if len(listofdata)==0:
            QtGui.QMessageBox.information(self,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return None
        newdataset=self.giveMeANewName()
        
        dlg=dlgCalculator.dlgCalculator(self,listofdata,newdataset)
        dlg.exec_()
        #dlg.show()
        '''    newdatasetname,formula,variableDict=dlg.getValues()
        else:
            return
        newdatasetname=self.cleanString(newdatasetname)
        qref=copy(self.data_dict[listofdata[0]].q)
        
        #--
        print newdatasetname,formula,variableDict
        formulaForComment=formula
        for var in variableDict.keys():
            formulaForComment=formulaForComment.replace(var,variableDict[var])
            self.printTXT(formulaForComment)
        newdict={}
        newerror=numpy.zeros(numpy.shape(qref))
        
        #--convert variableDict
        for var in variableDict:
            name=variableDict[var]
            #print name
            if not(self.data_dict.has_key(name)):
                print "error on mainGuisaxs.OnEditCalculator"
                return
            #variableDict contain variable name and dataset name
            i=self.data_dict[name].i
            q=self.data_dict[name].q
            if str(q)<>str(qref):
                self.printTXT("trying interpolation for ",name)
                newf=interpolate.interp1d(q,i,kind='linear',bounds_error=0)
                newi=newf(qref)
            else:
                newi=i
                #addition for errors
                error=self.data_dict[name].error
                if error!=None and newerror!=None:
                    newerror+=error
                else:
                    newerror=None
            newdict[var]=newi
        #--evaluate
        self.printTXT("trying evaluation of ",formula)
        
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', \
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',\
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'] #use the list to filter the local namespace safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        for k in safe_list:
            newdict[k]=locals().get(k)
        
        iout=numpy.array(eval(formula,newdict))
        self.data_dict[newdatasetname]=dataset(newdatasetname,qref,iout,comment=formulaForComment,type='calculated',error=newerror)#[data[0], data[1], datafilename, True]
        self.redrawTheList()
        self.Replot()
        '''
    def OnEditRemoveDependencies(self):
        '''
        remove all dependencies on datasets
        '''
        label=self.getCurrentSelectedItem()
        selectedDatas=self.ListOfDatasChecked()
        for name in selectedDatas:
            self.data_dict[name].parent=None
            self.data_dict[name].child=None
            self.data_dict[name].parentformula=None
            self.data_dict[name].variableDict=None
        self.redrawTheList()
        self.Replot()
    
    def OnEditChangeColor(self):
        '''
        user want to change the color
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        initial=self.data_dict[label].color
        if initial is None:
            initial="#ffffff"
        col = QtGui.QColorDialog.getColor(QtGui.QColor(initial))
        self.data_dict[label].color=str(col.name())
        print col.name()
        self.Replot()
            
    def OnEditStat(self):
        '''
        user want statistical information
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        
        #message box 
        info=""
        info+="Statistical information for "+label+" : \n"
        info+="Number of points : "+str(len(q))+"\n"
        info+="x min : "+str(q[0])+", x max : "+str(q[len(q)-1])+"\n"
        info+="y min : "+str(min(i))+" at "+str(q[numpy.argmin(i)])+", y max : "+str(max(i))+" at "+str(q[numpy.argmax(i)])+"\n"
        info+="Mean of y : "+str(numpy.mean(i))+" with standard deviation : "+str(numpy.std(i))+"\n"
        info+="The signal-to-noise ratio( defined as the ratio between the mean and the standard deviation): "+str(stats.signaltonoise(i))+"\n"
        dlg=QtGui.QMessageBox.information(self,"pySAXS",info, buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
    
    def OnEditGenerateNoise(self):
        '''
        user want generate a noise from the data
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        #message box for entry
        #here we use guidata to generate a dialog box
        percent=10.0
        items = {
         "percent": dataitems.FloatItem("Percent of random noise around the data value :",percent),
         }
        clz = type("Noise generator :\nspecify a percent of random noise around the data value", (datatypes.DataSet,), items)
        dlg = clz()
        if not dlg.edit():
            return  
        percent=dlg.percent
        percent=int(percent)/100.0
        #add a data set
        newdataset=label+ " noised with "+str(percent*100)+"%"
        q=self.data_dict[label].q
        i=self.data_dict[label].i
        randomarray=(numpy.random.rand(len(i))*2)-1 #randoms numbers between -1 and +1
        i=i+i*percent*randomarray
        self.data_dict[newdataset]=dataset(newdataset,q,i,label,type="calculated",parent=[label])
        self.redrawTheList()
        self.Replot()
        

    def OnEditAddReference(self):
        '''
        user want to add a reference value
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #message box for entry
        value=1.0
        items = {
         "value": dataitems.FloatItem("Reference value :",value),
         }
        clz = type("Add a reference value", (datatypes.DataSet,), items)
        dlg = clz()
        if not dlg.edit():
            return  
        value=dlg.value
        #add a data set
        newdataset="reference "+str(value)
        q=self.data_dict[label].q
        ilist=[value]*len(q)
        i=numpy.array(ilist)
        self.data_dict[newdataset]=dataset(newdataset,q,i,label,type='referenceVal')
        self.redrawTheList()
        self.Replot()
        
    def OnEditSetAsReference(self):
        '''
        user want to set a reference 
        '''
        #check if a data set is selected
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #print 'set as reference : ',label
        self.data_dict[label].type='reference'
        self.referencedata=label
        self.redrawTheList()
    #----------------------------------------------------------------------------------------------------------------
        
    def redrawTheList(self):
        '''
        redraw the listbox
        '''
        #print "redraw the list"
        l=[]
        for name in self.data_dict:
            l.append(name)
            
        l.sort()
        #print l
        #qt tree widget    
        self.ui.treeWidget.clear()
        self.ui.treeWidget.setHeaderLabels(["Datas"])
        treedict={}
        for name in l:  
            #print name
            item=QtGui.QTreeWidgetItem([name])
            item.label=name
            item.internalType='data'
            treedict[name]=item
            #item.setIcon(0, QtGui.QIcon(ICON_PATH+'chart_curve.png'))
            if self.data_dict[name].checked:
                item.setCheckState(0,QtCore.Qt.Checked)
                item.setBackgroundColor(0,QtGui.QColor('#FFEFD5'))#QtCore.Qt.gray)##C0C0C0
                if self.data_dict[name].color is not None:
                    item.setForeground(0,QtGui.QColor(self.data_dict[name].color))
            else:
                item.setCheckState(0,QtCore.Qt.Unchecked)
                item.setBackgroundColor(0,QtCore.Qt.white)
                #item.setForeground(0,QtCore.Qt.black)
                if self.data_dict[name].color is not None:
                    item.setForeground(0,QtGui.QColor(self.data_dict[name].color))
            if name==self.referencedata:
                item.setBackgroundColor(0,QtGui.QColor('#FFB6C1'))#FFB6C1    
        #print "test", len(treedict),len(self.data_dict)            
        for name, item in treedict.items():
            #print name
            parent=self.data_dict[name].parent
            #print parent
            if parent is not None:
                #print "parent :",parent
                pere=parent[0]
                if treedict.has_key(pere):
                    #print pere
                    #print "parent found"
                    treedict[pere].addChild(item)
                    treedict[pere].setExpanded(True)
                    item.setExpanded(True)
                    item.setIcon(0, QtGui.QIcon(ICON_PATH+'arrow_join.png'))
                    self.ui.treeWidget.expandItem(item)
                    
                else:
                    self.ui.treeWidget.addTopLevelItem(item)
            else:
                item.setExpanded(True)
                self.ui.treeWidget.addTopLevelItem(item)
            
            #if item has parameters 
            if self.data_dict[name].parameters is not None:
                lbl='Scaling parameters'
                item=QtGui.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='parameters'
                item.setIcon(0, QtGui.QIcon(ICON_PATH+'chart_params.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)
            
            if self.data_dict[name].model is not None:
                lbl='Model :'+self.data_dict[name].model.name
                item=QtGui.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='model'
                item.setIcon(0, QtGui.QIcon(ICON_PATH+'fit.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)
                
            if self.data_dict[name].image is not None:
                lbl=self.data_dict[name].image
                item=QtGui.QTreeWidgetItem([lbl])
                item.label=lbl
                item.internalType='image'
                item.setIcon(0, QtGui.QIcon(ICON_PATH+'image.png'))
                treedict[name].addChild(item)
                treedict[name].setExpanded(True)
                item.setExpanded(True)
                self.ui.treeWidget.expandItem(item)
                
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.sortByColumn(0,0)
           
       
    def ReadFile(self,datafilename,file_type=None):
        '''
        read file depending of type of file
        '''
        name = filetools.getFilename(datafilename)
        if file_type=='usaxs':
            #if extension=="txt": #it is a txt file
            #data = LSusaxs.ReadUSAXSData(datafilename)
            self.ImportData(datafilename,usecols = (0,2),name=name,type=file_type) #here we get (2theta , I)
            #self.data_dict[name]=dataset(datafilename,data[:,0],data[:,1],datafilename+ ' raw data',type=file_type)#[data[:,0],data[:,1],datafilename,True]
            #self.data_dict[name].q=LSusaxs.QtoTheta(self.data_dict[name].q,self.wavelength)# Should be masked if the data is already in theta
        elif file_type=='usaxsrck':
            #a USAXS rocking curve
            self.ImportData(datafilename,usecols = (0,2),name='rock',type=file_type)
            #datarock = LSusaxs.ReadUSAXSData(datafilename)
            #self.data_dict['rock']=dataset('rock',datarock[:,0],datarock[:,1],datafilename,type=file_type)#[datarock[:,0],datarock[:,1],datafilename,True]
            #self.data_dict['rock'].q=LSusaxs.QtoTheta(self.data_dict['rock'].q,self.wavelength)# Should be masked if the data is already in theta
        elif file_type=='usaxsdsm':
            #elif extension=="dsm": #it is a dsm file
            #data = LSusaxs.ReadUSAXSData(datafilename)
            self.ImportData(datafilename,usecols = (0,2),name='dec',type=file_type)
            #self.data_dict['dec']=dataset('dec',data[:,0],data[:,1],datafilename,type=file_type)#[data[:,0],data[:,1],datafilename,True]
            self.data_dict['InterpolForFit']=dataset('InterpolForFit',data[:,0],data[:,1],datafilename)#[data[:,0],data[:,1],datafilename]
        elif file_type=='fit2d':
            #elif extension=="chi": #it is a chi file from fit2D
            self.ImportData(datafilename,'  ',name=name,type=file_type )
        elif file_type=='saxs':
            #it is a rgr file
            self.ImportData(datafilename,'\t',name=name,type=file_type ,errorcol=2)
        elif file_type=='txttab':
            #it is a txt file
            self.ImportData(datafilename,name=name,type=file_type)
        elif file_type=='txtcomma':
            #it is a txt file
            self.ImportData(datafilename,name=name,delimiter=',',type=file_type)
        elif file_type=='resfunc':
            #it is a dat file
            self.ImportData(datafilename,name='resfunc',delimiter=',',type=file_type)
        else:
            #don't know
            self.ImportData(datafilename,name=name,type=file_type)
    

    def OnItemChanged(self,item,column):
        '''
        what's happen when the user chek a box
        '''
        #print 'on item changed'
        label=str(item.text(0))
        if item.internalType!='data':
            return
        '''
        if label=='Scaling parameters' or label=="Image":
            return
        '''
        state=item.checkState(0) #state can be 0 or 2 not boolean
        if self.data_dict[label].checked==state:
            #state didn't changed, don't replot
            return
        self.ui.treeWidget.setCurrentItem(item)
        #print "item changed : ",label,state,self.data_dict[label].checked
        if state:
            self.data_dict[label].checked=True
            #item.setBackgroundColor(0,QtCore.Qt.gray)
            item.setBackgroundColor(0,QtGui.QColor('#FFEFD5'))
            if self.data_dict[label].color is not None:
                item.setForeground(0,QtGui.QColor(self.data_dict[label].color))
        else:
            self.data_dict[label].checked=False
            item.setBackgroundColor(0,QtCore.Qt.white)
            #item.setForeground(0,QtCore.Qt.black)
        
            
        self.Replot()
        
        if self.DatasetFilename!="":
            self.setWindowTitle("*"+self.DatasetFilename)
        
    def OnItemDoubleClicked(self,item,column):
        '''
        user double clicked on item
        '''
        #print "ddclicked"
        label=str(item.text(0))
        #print item.internalType
        if item.internalType=='parameters':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            #print self.data_dict[labelParent].parameters
            self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=self.data_dict[labelParent].parameters,datasetname=labelParent,printout=self.printTXT,referencedata=self.referencedata)
            self.childSaxs.show()
            return
        if item.internalType=='model':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            self.childmodel=dlgModel.dlgModel(self,labelParent,type="data")
            self.childmodel.show()
            return
        
        '''
        if label=='Scaling parameters':
            itemParent=item.parent()
            labelParent=str(itemParent.text(0))
            self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=self.data_dict[labelParent].parameters,datasetname=labelParent,printout=self.printTXT)
            self.childSaxs.show()
            return
        
        if self.data_dict[label].type=="model":
            self.childmodel=dlgModel.dlgModel(self,label,type="data")
            self.childmodel.show()
        '''
            
        
    
    def Replot(self):
        #print "replot on main"
        l=self.ListOfDatasChecked()
        if len(l)==0:
            return
        #check if data have parents
        for name in l:
            if hasattr(self.data_dict[name], 'parent'):
                if self.data_dict[name].parent!=None:
                    #print "#parent, need to be recalculated"
                    r=self.data_dict[name]._evaluateFromParent(self.data_dict)
                    if r!="" and r is not None:
                        self.printTXT(r)
        
        #   plot the qt frame
        i=0
        if self.plotframe is None:
            self.createPlotframe()
        try:
            self.plotframe.clearData()
        except :
            #PyDeadObjectError
            self.createPlotframe()
            print "DeadObjectError"
        l=[]
        for name in self.data_dict:
            l.append(name)
            l.sort()
        for name in l:
            qexp=self.data_dict[name].q
            iexp=self.data_dict[name].i
            
            if self.data_dict[name].checked:
                #print name, ' is checked'
                if self.data_dict[name].color!=None:
                    col=self.data_dict[name].color#pySaxsColors.getColorRGB(self.data_dict[name].color)
                else:
                    col=self.colors.getColor() #get a new color
                    self.data_dict[name].color=col
                    
                '''print name
                print self.data_dict[name].i
                print self.data_dict[name].q
                print iexp[0]    '''
                if self.data_dict[name].error<>None:
                    #print self.data_dict[name].error
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,error=self.data_dict[name].error,color=col)
                else:
                    self.plotframe.addData(qexp,iexp,self.data_dict[name].name,id=i,color=col)
            i=i+1
        self.plotframe.replot()
        #print "end replotFrame on main"
    
    def ListOfDatasChecked(self):
        '''
        check if there are data checked
        return list of dataset checked
        '''
        l=[]
        for name in self.data_dict:
            if self.data_dict[name].checked:
                #data are checked
                l.append(name)
        return l
    
    def ImportData(self, datafilename,lineskip=0,delimiter='\t',usecols=None,type=None,name=None,errorcol=2):
        '''
        extract data from file
        '''
        if name==None:
            name = filetools.getFilename(datafilename)
        
        #----- file -> data
        #data = importArray(datafilename, lineskip, dataSeparator,cols)
        data=numpy.loadtxt(datafilename, comments='#', skiprows=0, usecols=usecols)# Load data from a text file.
        data=numpy.transpose(numpy.array(data))
        #print data
        #----- data -> dataset
        name=self.cleanString(name)
        self.data_dict[name] = dataset(name,data[0], data[1], datafilename,type=type)#[data[0], data[1], datafilename, True]
        if errorcol is not None and len(data)>2:
            self.data_dict[name].error=data[errorcol]#/data[1]#1/numpy.sqrt(abs(data[1]*data[2]))
        self.data_dict[name].color=self.colors.getColor() #set a random color
            
    def cleanString(self,s):
        """Removes all accents from the string"""
        if isinstance(s,str):
            s = unicode(s,"utf8","replace")
            s=unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')
    
    def printTXT(self,txt="",par=""):
        '''
        print on comment ctrl
        '''
        self.ui.multitxt.append(str(txt)+str(par))
    
    def getCurrentSelectedItem(self):
        '''
        return the current item selected
        if no item is selected return None
        '''
        item=self.ui.treeWidget.currentItem()
        if item is None:
            return None
        if not item.isSelected():
            return None
        label=str(item.text(0))
        if not self.data_dict.has_key(label):
            return None
        return label
    
    def noDataErrorMessage(self):
        QtGui.QMessageBox.information(self,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
        
    
    def OnEditFindPeaks(self):
        '''
        find peaks
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        
        i=self.data_dict[label].i
        q=self.data_dict[label].q
        newq=None
        newi=None
        pp=20
        
        #here we use guidata to generate a dialog box
        items = {
         "pp": dataitems.IntItem("Window for scan:",pp),
         "percent" : dataitems.IntItem("Peaks height from the background (in percent)",100.0)
         }
        clz = type("Find peaks", (datatypes.DataSet,), items)
        dlg = clz()
        dlg.edit()  
        pp=dlg.pp
        percent=dlg.percent/100.0
        #end of dialog box    
        
        #call find peaks
        founds, newq,newi=DetectPeaks.findPeaks(q,i,pp,percent,self)
        n=len(founds)
        if n>0:
            for res in founds:
                #[height,fwhm,center]
                self.printTXT(  "found peak at q="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1]))
                #--- plot in matplotlib
                self.plotframe.annotate(res[2], res[0],"peak at q="+str(res[2])+"\t i="+str(res[0])+ "\t fwhm="+str(res[1])) 
            self.data_dict[label+" peaks"]=dataset(label+" peaks",numpy.array(newq),numpy.array(newi),comment=label+" peaks",type='calculated',parent=[label])#[data[0], data[1], datafilename, True]
        self.printTXT(str(n)+" peaks found ---------")    
        #self.plotframe.draw()
        self.redrawTheList()
        #self.Replot()

    def OnEditDerivate(self):
        '''
        user want to derivate dataset
        '''
        label=self.getCurrentSelectedItem()
        if label is None:
            self.noDataErrorMessage()
            return
        #create a new data set
        newdatasetname=label+' derivate'
        self.data_dict[newdatasetname]=self.data_dict[label]._deepcopy()
        self.data_dict[newdatasetname].name=newdatasetname
        q=self.data_dict[newdatasetname].q
        i=self.data_dict[newdatasetname].i
        tck = interpolate.splrep(q,i,s=0)
        yder = interpolate.splev(q,tck,der=1)
        self.data_dict[newdatasetname].i=yder
        self.data_dict[newdatasetname].parent=[label]
               
        self.redrawTheList()
        self.Replot()
        
    def NotYetImplemented(self):
        QtGui.QMessageBox.information(self,"PySAXS","Not yet implemented", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
    
    
        
    def giveMeANewName(self):
        '''
        return a new name for a data set
        '''
        newname='newdata'
        i=0
        while self.data_dict.has_key(newname):
            newname='newdata'+str(i)
            i+=1
        return newname
    
    def plugins_list(self, plugins_dirs):
        """ List all python modules in specified plugins folders """
        l=[]
        for path in plugins_dirs.split(os.pathsep):
            for filename in os.listdir(path):
                name, ext = os.path.splitext(filename)
                #print name
                if ext.endswith(".py") and name.startswith('plugin'):
                    if name!='plugin':
                        l.append(name)
        return l
    
    def my_import(self,name):
        m = __import__(name)
        for n in name.split(".")[1:]:
            m = getattr(m, n)
        return m

    def setWorkingDirectory(self,filename):
        self.workingdirectory=os.path.dirname(filename)
        self.pref.set('defaultdirectory', self.workingdirectory)
        self.pref.addRecentFile(filename)
        self.pref.save()
        action=self.ui.menuRecents.addAction(filename)#add text in the menu
        item=filename
        self.connect(action,QtCore.SIGNAL('triggered()'), lambda item=item: self.OnRecentFile(item))
        self.ui.menuFile.addAction(self.ui.menuRecents.menuAction())
    
    def getWorkingDirectory(self):
        return self.workingdirectory
    
    def getListOfDocs(self):
        p=path.dirname(pySAXS.__file__)
        l=filetools.listFiles(p+os.sep+"doc",'*.*')
        return l
    
    def OnOpenDocument(self,name):
        '''
        start the default application for the doc file
        '''
        
        if os.name == "nt":
            os.startfile("%s" % name)
        elif os.name == "posix":
            os.system("/usr/bin/xdg-open %s" % name)
    
    def OnHelpChanges(self):
        '''
        start the changes dlg
        '''
        self.showSplash()
        file=pySAXS.__path__[0]+ os.sep+"CHANGELOG.txt"
        child=dlgTextView.ViewMessage(file,'Changes '+pySAXS.__version__+pySAXS.__subversion__,parent=self)
        child.exec_()
        
    def OnHelpAbout(self):
        '''
        start the about dlg
        '''
        self.showSplash()
        file=pySAXS.__path__[0]+ os.sep+"ABOUT.txt"
        child=dlgTextView.ViewMessage(file,'About '+pySAXS.__version__+pySAXS.__subversion__,parent=self)
        child.exec_()
    
    def OnHelpLicense(self):
        '''
        start the about dlg
        '''
        self.showSplash()
        file=pySAXS.__path__[0]+ os.sep+"LICENSE.txt"
        child=dlgTextView.ViewMessage(file,'License',parent=self)
        child.exec_()

    def OnToolsAbsorption(self):
        '''
        start the absorption tool with XRlib
        '''
        dlg=dlgAbsorption.dlgAbsorption(self,printout=self.printTXT)
        dlg.exec_()
    
    def showSplash(self):
        '''
        show the spalsh screen
        '''
        splash_pix = QtGui.QPixmap('splash.png')
        self.splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        self.splash.setMask(splash_pix.mask())
        self.splash.show()
        self.splash.showMessage('  pySAXS version : '+pySAXS.__version__+pySAXS.__subversion__,alignment=QtCore.Qt.AlignLeading)

        
    def dragEnterEvent(self, event):
        #self.setText("<drop content>")
        #print "drag"
        #self.ui.listWidget.setBackgroundRole(QtGui.QPalette.Highlight)
        event.acceptProposedAction()
        #self.changed.emit(event.mimeData())
    
    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            filenames=[]
            #print mimeData.urls()
            url=QtCore.QUrl()
            
            for url in mimeData.urls():
                #print url.encodedPath()
                f=str(url.path())[1:]
                filenames.append(f)
                #li=QtGui.QListWidgetItem(f)
                #self.ui.listWidget.addItem(li)
            #print str("\n".join([url.path() for url in mimeData.urls()]))
            self.OnFileOpen(filenames)

if __name__ == "__main__":
      app = QtGui.QApplication(sys.argv)
      myapp = mainGuisaxs()
      myapp.show()
      sys.exit(app.exec_())
