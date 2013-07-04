'''
execute this file for opening guiSAXS qt (the graphic user interface for pySAXS)
'''
from PyQt4 import QtGui,QtCore
import os
import sys
import pySAXS
app = QtGui.QApplication(sys.argv)
splash_file=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'qt'+os.sep+'splash.png'
splash_pix = QtGui.QPixmap(splash_file)
splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
splash.setMask(splash_pix.mask())
splash.show()
app.processEvents()
      
from pySAXS.guisaxs.qt import mainGuisaxs    
myapp = mainGuisaxs.mainGuisaxs()
myapp.show()
splash.destroy()
sys.exit(app.exec_())