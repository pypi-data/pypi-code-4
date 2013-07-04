"""
project : pySAXS
description : function to print a message from a txt file to a dialog box
authors : Olivier Tache

"""
from PyQt4 import QtGui, QtCore
from pySAXS.guisaxs.qt import dlgTextViewui
import os
import sys
import pySAXS

class ViewMessage(QtGui.QDialog,dlgTextViewui.Ui_dlgTextView):
    def __init__(self,file,title='test',parent=None):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        f = open(file, "r")
        msg = f.read()
        f.close()
        msgu=unicode(msg,errors='replace')
        self.textBrowser.setText(msgu)
        self.setWindowTitle(title)
        if parent is not None:
            self.move(parent.x(),parent.y())
            

#------------------------------------------
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    file=os.path.dirname(pySAXS.__file__)+os.sep+'LICENSE.txt'
    myapp = ViewMessage(file,'LICENCE')
    myapp.show()
    sys.exit(app.exec_())