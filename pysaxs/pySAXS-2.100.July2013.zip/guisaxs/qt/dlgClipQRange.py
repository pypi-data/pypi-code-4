from PyQt4 import QtGui, QtCore
from pySAXS.guisaxs.qt import dlgClipQRangeui
"""
Show a dialog box for qmin, qmax choice
Is no more used beacause guidata
"""

class dlgClipQRange(QtGui.QDialog,dlgClipQRangeui.Ui_dlgClipQRange):
    def __init__(self,label="",qmin=0.,qmax=1.):
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        #self.ui = dlgClipQRangeui.Ui_dlgClipQRange()
        self.setupUi(self)
        self.labelDataName.setText(label)
        self.qmin.setText(str(qmin))
        self.qmin.setValidator(QtGui.QDoubleValidator())
        self.qmax.setText(str(qmax))
        self.qmax.setValidator(QtGui.QDoubleValidator())
        
        
    def getValues(self):
        return float(self.qmin.text()),float(self.qmax.text())
