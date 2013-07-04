from PyQt4 import QtGui, QtCore
import sys
 
from pySAXS.guisaxs.qt import dlgQtFAIui
import numpy
import sys
import os.path, dircache
from pySAXS.tools import FAIsaxs
import pyFAI
from pyFAI import azimuthalIntegrator
from pySAXS.tools import filetools
from pySAXS.guisaxs import dataset
import time
from pyFAI import azimuthalIntegrator
import fabio
from pySAXS.guisaxs.qt import QtImageTool

class FAIDialog(QtGui.QMainWindow):
    def __init__(self, parent=None,parameterfile=None,outputdir=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = dlgQtFAIui.Ui_FAIDialog()
        self.setWindowTitle('Radial averaging tool for SAXS')
        if parent is not None:
            #print "icon"
            self.setWindowIcon(parent.windowIcon())
        
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.paramFileButton, QtCore.SIGNAL("clicked()"),self.OnClickparamFileButton)
        QtCore.QObject.connect(self.ui.addButton, QtCore.SIGNAL("clicked()"),self.OnAddButton)
        QtCore.QObject.connect(self.ui.changeOutputDirButton, QtCore.SIGNAL("clicked()"),self.OnClickchangeOutputDirButton)
        QtCore.QObject.connect(self.ui.RADButton, QtCore.SIGNAL("clicked()"),self.OnClickRADButton)
        self.ui.buttonRemove.clicked.connect(self.OnClickRemove)
        self.ui.buttonViewImage.clicked.connect(self.OnClickViewImage)
        self.ui.buttonClearList.clicked.connect(self.OnClickClearList)
        self.ui.listWidget.setAcceptDrops(True)
        self.parent=parent
        self.workingdirectory=None
        if parent is not None:
            self.printout=parent.printTXT
            self.workingdirectory=parent.workingdirectory
        
        if parameterfile is not None:
            self.ui.paramTxt.setText(parameterfile)
        if outputdir is not None:
            self.ui.outputDirTxt.setText(outputdir)
            
        self.imageToolWindow=None
    
    def dragEnterEvent(self, event):
        #self.setText("<drop content>")
        #print "drag"
        #self.ui.listWidget.setBackgroundRole(QtGui.QPalette.Highlight)
        event.acceptProposedAction()
        #self.changed.emit(event.mimeData())
    
    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            #print mimeData.urls()
            for url in mimeData.urls():
                f=str(url.path())
                li=QtGui.QListWidgetItem(f)
                self.ui.listWidget.addItem(li)
            #print str("\n".join([url.path() for url in mimeData.urls()]))
        
        
    def OnClickparamFileButton(self):
        fd = QtGui.QFileDialog(self)
        filename=fd.getOpenFileName(directory=self.workingdirectory)
        self.workingdirectory=filename
        #print filename
        self.ui.paramTxt.setText(filename)
        #self.ui.editor_window.setText(plik)
        
    def OnAddButton(self):
        fd = QtGui.QFileDialog(self)
        filenames=fd.getOpenFileNames(directory=self.workingdirectory)
        #filenames=fd.selectedFiles()
        #print filenames
        for f in filenames:
            #add to list
            li=QtGui.QListWidgetItem(f)
            self.ui.listWidget.addItem(li)
            self.workingdirectory=f
        
            
    def OnClickViewImage(self):
        #test the file
        itemList=self.ui.listWidget.selectedItems()
        if len(itemList)<0:
            return #no item selected
        
        if self.imageToolWindow is None:
            #oprn a new window
            self.imageToolWindow = QtImageTool.MainWindow(self.parent)
        
        for item in itemList:
            filename=str(item.text())
            self.imageToolWindow.open_image(filename)
        
        self.imageToolWindow.show()
    
    def OnClickRemove(self):
        #test the file
        itemList=self.ui.listWidget.selectedItems()
        print itemList
        if len(itemList)<0:
            return #no item selected
        for item in itemList:
            self.ui.listWidget.takeItem(self.ui.listWidget.row(item))
            #self.ui.listWidget.removeItemWidget(item)#don't work
            
        
    def OnClickClearList(self):
        '''
        erase list
        '''
        self.ui.listWidget.clear()
        
    def OnClickchangeOutputDirButton(self):
        fd = QtGui.QFileDialog(self,directory=self.workingdirectory)
        fd.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        if fd.exec_() == 1:
            dir = str(fd.selectedFiles().first())
            #dir=fd.getOpenFileName()
            self.ui.outputDirTxt.setText(dir)
            self.workingdirectory=dir
        
            
            
    def OnClickRADButton(self):
        #get list of files
        items = []
        for index in range(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        l = [str(i.text()) for i in items]
        #print l
        n=len(l)
        self.ui.progressBar.setMaximum(n)
        self.ui.progressBar.setValue(0)
        #prepare 
        fai=FAIsaxs.FAIsaxs()
        filename=self.ui.paramTxt.text()
        if not os.path.exists(filename):
            self.printTXT(filename+' does not exist')
            return
        outputdir=self.ui.outputDirTxt.text()
        fai.setGeometry(filename)
        qDiv=fai.getProperty('user.qDiv')
        if qDiv is None:
            qDiv=1000
        #get the mask defined in parameters
        
        mad=fai.getIJMask()
        maskfilename=fai.getMaskFilename()
        self.printTXT('Image mask opened in ',maskfilename)
        for i in range(len(l)):
            self.ui.progressBar.setValue(i+1)
            #time.sleep(1.1)
            #radial averaging
            t0=time.time()
            #-- opening data
            imageFilename=l[i]
            name=filetools.getFilename(imageFilename)
            newname=outputdir+os.sep+name+".rgr"
            try:
                im=fabio.open(imageFilename)
            except:
                self.printTXT('error in opening ',imageFilename)
                im=None
            if im is not None:
                
                qtemp,itemp,stemp=fai.integrate1d(im.data,qDiv,filename=newname,mask=mad,error_model="poisson")
                q=qtemp[numpy.nonzero(itemp)]
                i=itemp[numpy.nonzero(itemp)]
                s=stemp[numpy.nonzero(itemp)]
                t1=time.time()
                self.printTXT("data averaged in "+str(t1-t0)+" s for "+imageFilename+" and saved as "+newname)
                if self.parent is not None:
                    name = filetools.getFilename(imageFilename)
                    self.parent.data_dict[name]=dataset.dataset(name,q,i, imageFilename,error=s,type='saxs',image="Image")
                    
        self.parent.redrawTheList()
        self.parent.Replot()        
        self.ui.progressBar.setValue(0)
        #save the preferences
        if self.parent is not None:
                self.parent.pref.set("outputdir",section="pyFAI",value=str(self.ui.outputDirTxt.text()))
                self.parent.pref.set("parameterfile",section="pyFAI",value=str(self.ui.paramTxt.text()))
                self.parent.pref.save()
        
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
  myapp = FAIDialog()
  myapp.show()
  sys.exit(app.exec_())