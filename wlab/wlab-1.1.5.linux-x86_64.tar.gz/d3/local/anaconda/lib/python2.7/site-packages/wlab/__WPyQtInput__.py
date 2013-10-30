#-*- coding:utf-8 -*-
#~ #--------------------------------------------------------------------------------
#~ module:wlab
#~ FileName=WPyQtInput.py
#~Class:QInputGroupBox,QInputDialog,QInputBox
#~ author:Wu Xuping
#~ Date:2013-05-06
#~ Email:539688300@qq.com
#~ Remark:based on PyQt4 or PySide
#~ #-------------------------------------------------

try:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
    from PyQt4.QtCore import pyqtSlot
    from PyQt4.QtCore import pyqtSignal
    IsPyQt=True
    IsPySide=False
except ImportError:
    from PySide import QtGui
    from PySide import QtCore
    from PySide.QtCore import Slot as pyqtSlot
    from PySide.QtCore import Signal as pyqtSignal
    IsPyQt=False
    IsPySide=True
#~ #-------------------------------------------------

#~ #-------------------------------------------------
#~ #将字符串一特定的长度输出
def FormatStr(MaxStrLength,s):
    if (len(s)<MaxStrLength):
        for n in range(MaxStrLength-len(s)):
            s=' '+s

    rs=str(s)+':'
    return rs

class IntLineEdit(QtGui.QLineEdit):
    def __init__ (self,num=0):
        '''
        #~ IntLineEdit(num)
        '''
        QtGui.QLineEdit.__init__ (self)
        self.num=num
        self.setText(str(self.num))

    @pyqtSlot(int)
    def setValue(self,n):
        self.setText(str(n))
        return (self.num,n)

class FloatLineEdit(QtGui.QLineEdit):
    def __init__ (self,num=0.0):
        '''
        #~ FloatLineEdit(num)
        '''
        QtGui.QLineEdit.__init__ (self)
        self.num=num
        self.setText(str(self.num))

    @pyqtSlot(int)
    def setValue(self,n):
        if ( self.num>0):
            self.setText(str(self.num+n*self.num/50.0))
        else:
            self.setText(str(self.num-n*self.num/50.0))
        return (self.num,n)
#~ #-------------------------------------------------
class QInputGroupBox(QtGui.QGroupBox):
    def __init__(self, values={'String':'This is String','float':3.5,'int':15},title='Please set values',ntimes=2.0,parent=None):
        '''
        #~#---------------------------------------------------
        #~#Examples:
        #~#---------------------------------------------------
        #~ >>>values={'String':'This is String','float':3.5,'int':15}
        #~ >>>GroupBoxTitle='Please set values'
        #~ >>>self.QIGBox=QInputGroupBox(values=values,title=GroupBoxTitle,ntimes=2.0,parent=self)
        #~ >>>rvalues=self.QIGBox.GetOriginValue()
        #~ >>>rvalues=self.QIGBox.GetModifiedValues()
        #~#---------------------------------------------------
        #~#Parameters:
        #~#---------------------------------------------------
        #~#values={'String':'This is String','float':3.5,'int':15}
        #~#title='Please set values'
        #~#ntimes=2.0
        #~#parent=None
        '''
        QtGui.QGroupBox.__init__ (self, title=title,parent = parent)

        self.OriginValues=values.copy()
        self.ModifiedValues=values.copy()

        MaxStrLength=max([len(str(s)) for s in list(values.keys())])

        layout = QtGui.QGridLayout()
        cnt=0
        for key in self.ModifiedValues:
            label=FormatStr(MaxStrLength,str(key))
            KeyLabel=QtGui.QLabel(label)
            layout.addWidget(KeyLabel, cnt, 0)
            ovk=self.ModifiedValues[key]

            if(type(ovk)==int) :
                valueLineEdit=IntLineEdit(ovk)
                layout.addWidget(valueLineEdit, cnt , 1)
                slider=QtGui.QSlider(orientation= QtCore.Qt.Horizontal)
                if (ovk>0):
                    slider.setRange( ovk/(ntimes+1), ovk*(ntimes+1))
                elif (ovk==0):
                    slider.setRange( -5*(ntimes+1), 5*(ntimes+1))
                else:
                    slider.setRange(ovk*(ntimes+1),ovk/(ntimes+1))
                slider.setValue(ovk)
                QtCore.QObject.connect(slider,QtCore.SIGNAL('valueChanged(int)'),
                            valueLineEdit, QtCore.SLOT('setValue(int)'))
                layout.addWidget(slider, cnt ,2)

            elif(type(ovk)==float) :
                valueLineEdit=FloatLineEdit(ovk)

                layout.addWidget(valueLineEdit, cnt , 1)
                slider=QtGui.QSlider(orientation= QtCore.Qt.Horizontal)
                slider.setRange( -50*ntimes, 50*ntimes)
                QtCore.QObject.connect(slider,QtCore.SIGNAL('valueChanged(int)'),
                            valueLineEdit, QtCore.SLOT('setValue(int)'))
                layout.addWidget(slider, cnt ,2)

            else:
                valueLineEdit=QtGui.QLineEdit(ovk)
                layout.addWidget(valueLineEdit, cnt, 1,1,2)

            #~ #set an object name for QLineEdit,Later we can use findchild() to find it
            valueLineEdit.setObjectName('VLE'+str(cnt))

            layout.setRowStretch(cnt,5)
            cnt=cnt+1

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 5)
        layout.setColumnStretch(2, 10)

        self.setLayout(layout)


    def GetOriginValue(self):
        '''
        #~ if the user click btn_Cancel,then return OriginValues
        '''
        return self.OriginValues

    def GetModifiedValues(self):
        '''
        #~ if the user click btn_OK,then return self.ModifiedValues
        '''
        cnt=0
        for key in self.ModifiedValues:
            keyStr=str(key)
            VLEObjectName='VLE'+str(cnt)
            if (IsPyQt):
                VLE=self.findChild((QtGui.QLineEdit, ),VLEObjectName)
            else:
                VLE=self.findChild(QtGui.QLineEdit,VLEObjectName)
            cnt=cnt+1
            ovk=self.ModifiedValues[key]
            if(type(ovk)==int):
                self.ModifiedValues[key]=int(VLE.text())
            elif(type(ovk)==float):
                self.ModifiedValues[key]=float(VLE.text())
            else:
                self.ModifiedValues[key]=str(VLE.text())

        return self.ModifiedValues
#~ #-------------------------------------------------
class QInputDialog(QtGui.QDialog):
    def __init__(self, values={'String':'This is String','float':3.5,'int':15},GroupBoxTitle='Please set values',title='QInputDialog:',parent=None):
        '''
        #~ >>>values={'String':'This is String','float':3.5,'int':15}
        #~ >>>GroupBoxTitle='Please set values'
        #~ >>>title='QInputDialog:'
        #~ >>>dlg = QInputDialog(values=values,GroupBoxTitle=GroupBoxTitle,title=title,parent=None)
        #~ >>>if ( dlg.exec_() == QtGui.QDialog.Accepted):
         #~ >>>     rvalues = dlg.GetModifiedValues()
        #~ >>>else:
        #~ >>>     rvalues = dlg.GetOriginValue()
        '''
        QtGui.QDialog.__init__(self, parent=parent)
        self.setWindowTitle(title)
        self.QIGBox=QInputGroupBox(values=values,title=GroupBoxTitle,parent=self)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.QIGBox)

        self.btn_OK=QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.btn_Cancel=QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel)

        self.btn_OK.clicked.connect(self.accept )
        self.btn_Cancel.clicked.connect(self.reject)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_OK)
        hbox.addWidget(self.btn_Cancel)
        self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)

    def GetOriginValue(self):
        '''
        #~ if the user click btn_Cancel,then return OriginValues
        '''
        return self.QIGBox.GetOriginValue()

    def GetModifiedValues(self):
        '''
        #~ if the user click btn_OK,then return self.ModifiedValues
        '''
        return self.QIGBox.GetModifiedValues()
#~ #-------------------------------------------------
#~ #Good packaging QInputBox
def QInputBox(values={'String':'This is String','float':3.5,'int':15},GroupBoxTitle='Please set values',title='QInputBox'):
    '''
    #~ >>>values={'String':'This is String','float':3.5,'int':15}
    #~ >>>GroupBoxTitle='Please set values'
    #~ >>>title='QInputBox'
    #~ >>>rvalues=QInputBox(values=values,GroupBoxTitle=GroupBoxTitle,title=title)
    #~ >>>print(rvalues)
    #~ #>>>rvalues=QInputBox(values,GroupBoxTitle)
    #~ #>>>rvalues=QInputBox(values)
    #~ #>>>rvalues=QInputBox()
    '''
    #app = QtGui.QApplication(sys.argv)#已自动创建，无需再创建
    dlg = QInputDialog(values=values,GroupBoxTitle=GroupBoxTitle,title=title)
    if ( dlg.exec_() == QtGui.QDialog.Accepted):
        rvalues = dlg.GetModifiedValues()
    else:
        rvalues = dlg.GetOriginValue()
    return rvalues

#~ #---------------------------------------------------------------------------------------------------------
#~ # main test program for __WPyQtInput__.py
#~ #---------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #----------------------------------------------------------------------------------------
    try:
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        from PyQt4.QtCore import pyqtSlot
        from PyQt4.QtCore import pyqtSignal
        IsPyQt=True
        IsPySide=False
    except ImportError:
        from PySide import QtGui
        from PySide import QtCore
        from PySide.QtCore import Slot as pyqtSlot
        from PySide.QtCore import Signal as pyqtSignal
    #----------------------------------------------------------------------------------------
    import sys
    app = QtGui.QApplication(sys.argv)#创建Qt进程app
    #----------------------------------------------------------------------------------------
    #示例1
    values={'String':'This is String','float':-3.5,'int':-15}
    GroupBoxTitle='Please set values'
    title='the first example of QInputBox '
    rvalues=QInputBox(values=values,GroupBoxTitle=GroupBoxTitle,title=title)
    print(rvalues)
    #>>>{'int': -15, 'float': -3.5, 'String': 'This is String'}
    #----------------------------------------------------------------------------------------
    #示例2
    from collections import OrderedDict
    values=OrderedDict([('c', 1), (2, 2), ('a', 3)])
    rvalues1=QInputBox(values=values)
    print(rvalues1)
    #>>>OrderedDict([('c', 1), (2, 2), ('a', 3)])
    #----------------------------------------------------------------------------------------
    #示例3
    values={'String':'This is String','float':-3.5,'int':-15}
    GroupBoxTitle='Please set values'
    title='QInputBox'
    rvalues2=QInputBox(values=values,GroupBoxTitle=GroupBoxTitle,title=title)
    print(rvalues2)
    #>>>{'int': -15, 'float': -3.5, 'String': 'This is String'}
    #----------------------------------------------------------s------------------------------
    #sys.exit(app.exec_())
