from PyQt4 import QtGui as gui
import traceback

class BaseWindow(gui.QWidget):
    def __init__(self, parent=None):
        super(gui.QWidget, self).__init__(parent=parent)
        self.initGui()
    
    def callFunction(self, lambdaFunc, successMessage=None):
        success = False
        result = None
        try:
            result = lambdaFunc()
            success = True
        except Exception as exc:
            traceback.print_exc()
            self.showMessage(exc.message, 'Error')

        if success and successMessage is not None:
            self.showMessage(successMessage, 'Success')

        return result, success
    
    def showMessage(self, text, title='Message'):
        messageBox = gui.QMessageBox()
        messageBox.about(self, title, text)