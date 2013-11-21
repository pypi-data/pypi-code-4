""" Sets up the Qt environment to work with various Python Qt wrappers """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import logging
import re

from PyQt4 import QtCore,\
                  QtGui,\
                  QtXml,\
                  QtWebKit,\
                  QtNetwork,\
                  uic

logger = logging.getLogger(__name__)
try:
    from PyQt4 import Qsci
except ImportError:
    logger.debug('PyQt4.Qsci is not installed.')
    Qsci = None

try:
    from PyQt4 import QtDesigner
except ImportError:
    logger.debug('PyQt4.QtDesigner is not installed.')
    QtDesigner = None

SIGNAL_BASE = QtCore.SIGNAL

def SIGNAL(signal):
    match = re.match(r'^(?P<method>\w+)\(?(?P<args>[^\)]*)\)?$', str(signal))
    if not match:
        return SIGNAL_BASE(signal)
    
    method = match.group('method')
    args   = match.group('args')
    args   = re.sub(r'\bobject\b', 'PyQt_PyObject', args)
    
    new_signal = '%s(%s)' % (method, args)
    return SIGNAL_BASE(new_signal)

def createMap(qt):
    # helpers
    qt['uic']      = uic
    qt['PyObject'] = 'PyQt_PyObject'
    
    # modules
    qt['QtCore']        = QtCore
    qt['QtDesigner']    = QtDesigner
    qt['QtGui']         = QtGui
    qt['Qsci']          = Qsci
    qt['QtWebKit']      = QtWebKit
    qt['QtNetwork']     = QtNetwork
    qt['QtXml']         = QtXml
    
    # variables
    qt['SIGNAL']   = SIGNAL
    qt['SLOT']     = QtCore.SLOT
    qt['Signal']   = QtCore.pyqtSignal
    qt['Slot']     = QtCore.pyqtSlot
    qt['Property'] = QtCore.pyqtProperty
    qt['QStringList'] = QtCore.QStringList
    
    # update the module itself
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    QtCore.SIGNAL = SIGNAL
    
    # map additional options
    QtCore.QDate.toPython = lambda x: x.toPyDate()
    QtCore.QDateTime.toPython = lambda x: x.toPyDateTime()
    QtCore.QTime.toPython = lambda x: x.toPyTime()