from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI
from PyQt4 import QtGui, QtCore

classlist=['pluginSAXSAbsolute']

class pluginSAXSAbsolute(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Absolute Intensities"
    
    def execute(self):
        
        #display the dialog box
        label=self.selectedData
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return
        #print self.data_dict[label].parameters
        #print label
        params=self.data_dict[label].parameters
        if params is not None:
            params.printout=self.printTXT
        reference=self.parent.referencedata
        #print 'reference data ',reference
        self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=params,datasetname=label,printout=self.printTXT,referencedata=reference)
        #self.dlgFAI=dlgQtFAI.FAIDialog(self.parent)
        self.childSaxs.show()