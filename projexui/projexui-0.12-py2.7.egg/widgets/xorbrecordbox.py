#!/usr/bin/python

""" [desc] """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'


#------------------------------------------------------------------------------

import logging

from projexui.qt import Signal,\
                        Property,\
                        PyObject,\
                        Slot,\
                        wrapVariant,\
                        unwrapVariant

from projexui.qt.QtCore import QPoint, Qt, QObject, QThread
from projexui.qt.QtGui import QApplication
from projexui.widgets.xcombobox import XComboBox
from projexui.widgets.xloaderwidget import XLoaderWidget
from projexui.widgets.xtreewidget import XTreeWidget
from projexui.widgets.xorbtreewidget import XOrbRecordItem
from projexui.xorblookupworker import XOrbLookupWorker

logger = logging.getLogger(__name__)

try:
    from orb import Orb, RecordSet
except ImportError:
    logger.warning('Could not import the ORB library.')
    Orb = None

#----------------------------------------------------------------------

class XOrbRecordBox(XComboBox):
    __designer_group__ = 'ProjexUI - ORB'
    
    """ Defines a combo box that contains records from the ORB system. """
    _loadRequested = Signal(PyObject)
    
    loadingStarted = Signal()
    loadingFinished = Signal()
    currentRecordChanged = Signal(PyObject)
    
    def __init__( self, parent = None ):
        # needs to be defined before the base class is initialized or the
        # event filter won't work
        self._treePopupWidget   = None
        
        super(XOrbRecordBox, self).__init__( parent )
        
        # define custom properties
        self._currentRecord     = None # only used while loading
        
        self._tableTypeName     = ''
        self._tableLookupIndex  = ''
        self._baseHints         = ('', '')
        self._tableType         = None
        self._query             = None
        self._iconMapper        = None
        self._labelMapper       = str
        self._required          = True
        self._loaded            = False
        self._showTreePopup     = False
        self._autoInitialize    = True
        
        # create threading options
        self._worker            = XOrbLookupWorker()
        self._workerThread      = QThread()
        self._worker.moveToThread(self._workerThread)
        self._workerThread.start()
        
        # create connections
        QApplication.instance().aboutToQuit.connect(self.__cleanupWorker)
        
        self._loadRequested.connect(self._worker.loadRecords)
        
        self._worker.loadingStarted.connect(self.markLoadingStarted)
        self._worker.loadingFinished.connect(self.markLoadingFinished)
        self._worker.loadedRecords.connect(self.__addRecordsFromThread)
        
        self.currentIndexChanged.connect(self.emitCurrentRecordChanged)
    
    def __addRecordsFromThread(self, records):
        """
        Adds the given record to the system.
        
        :param      records | [<orb.Table>, ..]
        """
        label_mapper    = self.labelMapper()
        icon_mapper     = self.iconMapper()
        
        tree = None
        if self.showTreePopup():
            tree = self.treePopupWidget()
        
        # add the items to the list
        start = self.count()
        
        # update the item information
        for i, record in enumerate(records):
            index = start + i
            self.addItem(label_mapper(record))
            self.setItemData(index, wrapVariant(records[i]), Qt.UserRole)
            
            if icon_mapper:
                self.setItemIcon(index, icon_mapper(records[i]))
            
            if record == self._currentRecord:
                self.setCurrentIndex(self.count() - 1)
            
            if tree:
                XOrbRecordItem(tree, record)
            
            QApplication.sendPostedEvents(self, -1)
    
    def __del__(self):
        self.__cleanupWorker()
    
    def __cleanupWorker(self):
        if not self._workerThread:
            return
        
        thread = self._workerThread
        worker = self._worker
        
        self._workerThread = None
        self._worker = None
        
        worker.deleteLater()
        
        thread.finished.connect(thread.deleteLater)
        thread.quit()
        thread.wait()
    
    def addRecord(self, record):
        """
        Adds the given record to the system.
        
        :param      record | <str>
        """
        label_mapper    = self.labelMapper()
        icon_mapper     = self.iconMapper()
        
        self.addItem(label_mapper(record))
        self.setItemData(self.count() - 1, wrapVariant(record), Qt.UserRole)
        
        # load icon
        if icon_mapper:
            self.setItemIcon(self.count() - 1, icon_mapper(record))
        
        if self.showTreePopup():
            XOrbRecordItem(self.treePopupWidget(), record)
    
    def addRecords(self, records):
        """
        Adds the given record to the system.
        
        :param      records | [<orb.Table>, ..]
        """
        label_mapper    = self.labelMapper()
        icon_mapper     = self.iconMapper()
        
        # create the items to display
        tree = None
        if self.showTreePopup():
            tree = self.treePopupWidget()
            tree.blockSignals(True)
            tree.setUpdatesEnabled(False)
        
        # add the items to the list
        start = self.count()
        self.addItems(map(label_mapper, records))
        
        # update the item information
        for i, record in enumerate(records):
            index = start + i
            
            self.setItemData(index, wrapVariant(records[i]), Qt.UserRole)
            
            if icon_mapper:
                self.setItemIcon(index, icon_mapper(records[i]))
            
            if tree:
                XOrbRecordItem(tree, record)
        
        if tree:
            tree.blockSignals(False)
            tree.setUpdatesEnabled(True)
    
    def acceptRecord(self, item):
        """
        Closes the tree popup and sets the current record.
        
        :param      record | <orb.Table>
        """
        record = item.record()
        self.treePopupWidget().close()
        self.setCurrentRecord(record)
    
    def autoInitialize(self):
        """
        Returns whether or not this record box should auto-initialize its
        records.
        
        :return     <bool>
        """
        return self._autoInitialize
    
    def batchSize(self):
        """
        Returns the batch size to use when processing this record box's list
        of entries.
        
        :return     <int>
        """
        return self._worker.batchSize()
    
    def checkedRecords( self ):
        """
        Returns a list of the checked records from this combo box.
        
        :return     [<orb.Table>, ..]
        """
        indexes = self.checkedIndexes()
        return map(self.recordAt, indexes)
    
    def currentRecord( self ):
        """
        Returns the record found at the current index for this combo box.
        
        :rerturn        <orb.Table> || None
        """
        if self._currentRecord is not None:
            return self._currentRecord
        
        index = self.currentIndex()
        data  = self.itemData(index, Qt.UserRole)
        
        return data
    
    def emitCurrentRecordChanged( self ):
        """
        Emits the current record changed signal for this combobox, provided \
        the signals aren't blocked.
        """
        self._currentRecord = None
        if not self.signalsBlocked():
            self.currentRecordChanged.emit(self.currentRecord())
    
    def eventFilter(self, object, event):
        """
        Filters events for the popup tree widget.
        
        :param      object | <QObject>
                    event  | <QEvent>
        
        :retuen     <bool> | consumed
        """
        if object not in (self._treePopupWidget, self.lineEdit()):
            return super(XOrbRecordBox, self).eventFilter(object, event)
        
        if event.type() == event.KeyPress:
            # accept lookup
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                item = object.currentItem()
                text = self.lineEdit().text()
                
                if item and item.isSelected() and not item.isHidden():
                    self.hidePopup()
                    self.setCurrentRecord(object.currentRecord())
                    event.accept()
                    return True
                
                else:
                    self.setCurrentRecord(None)
                    self.hidePopup()
                    self.lineEdit().setText(text)
                    self.lineEdit().keyPressEvent(event)
                    event.accept()
                    return True
                
            # cancel lookup
            elif event.key() == Qt.Key_Escape:
                text = self.lineEdit().text()
                self.setCurrentRecord(None)
                self.lineEdit().setText(text)
                self.hidePopup()
                event.accept()
                return True
            
            # update the search info
            else:
                self.lineEdit().keyPressEvent(event)
        
        elif event.type() == event.KeyRelease:
            self.lineEdit().keyReleaseEvent(event)
        
        elif event.type() == event.MouseButtonPress:
            local_pos = object.mapFromGlobal(event.globalPos())
            in_widget = object.rect().contains(local_pos)
            
            if not in_widget:
                text = self.lineEdit().text()
                self.setCurrentRecord(None)
                self.lineEdit().setText(text)
                self.hidePopup()
                event.accept()
                return True
            
        return super(XOrbRecordBox, self).eventFilter(object, event)
    
    def hidePopup(self):
        """
        Overloads the hide popup method to handle when the user hides
        the popup widget.
        """
        if self._treePopupWidget and self.showTreePopup():
            self._treePopupWidget.close()
        
        super(XOrbRecordBox, self).hidePopup()
    
    def iconMapper( self ):
        """
        Returns the icon mapping method to be used for this combobox.
        
        :return     <method> || None
        """
        return self._iconMapper
    
    def isLoading(self):
        """
        Returns whether or not this combobox is loading records.
        
        :return     <bool>
        """
        return self._worker.isRunning()
    
    def isRequired( self ):
        """
        Returns whether or not this combo box requires the user to pick a
        selection.
        
        :return     <bool>
        """
        return self._required
    
    def labelMapper( self ):
        """
        Returns the label mapping method to be used for this combobox.
        
        :return     <method> || None
        """
        return self._labelMapper
    
    @Slot(PyObject)
    def lookupRecords(self, record):
        """
        Lookups records based on the inputed record.  This will use the 
        tableLookupIndex property to determine the Orb Index method to
        use to look up records.  That index method should take the inputed
        record as an argument, and return a list of records.
        
        :param      record | <orb.Table>
        """
        table_type = self.tableType()
        if not table_type:
            return
        
        index = getattr(table_type, self.tableLookupIndex(), None)
        if not index:
            return
        
        self.setRecords(index(record))
    
    def markLoadingStarted(self):
        """
        Marks this widget as loading records.
        """
#        while self._worker.isRunning():
#            self._worker.cancel()
        
        XLoaderWidget.start(self)
        
        if self.showTreePopup():
            tree = self.treePopupWidget()
            tree.setCursor(Qt.WaitCursor)
            tree.clear()
            tree.setUpdatesEnabled(False)
            tree.blockSignals(True)
            
            self._baseHints = (self.hint(), tree.hint())
            tree.setHint('Loading records...')
            self.setHint('Loading records...')
        else:
            self._baseHints = (self.hint(), '')
            self.setHint('Loading records...')
        
        self.setCursor(Qt.WaitCursor)
        self.blockSignals(True)
        self.setUpdatesEnabled(False)
        
        # prepare to load
        self.clear()
        use_dummy = not (self.isRequired() or self.isCheckable())
        if use_dummy:
            self.addItem('')
        
        self.loadingStarted.emit()
    
    def markLoadingFinished(self):
        """
        Marks this widget as finished loading records.
        """
        XLoaderWidget.stop(self)
        
        hint, tree_hint = self._baseHints
        self.setHint(hint)
        
        # set the tree widget
        if self.showTreePopup():
            tree = self.treePopupWidget()
            tree.setHint(tree_hint)
            tree.unsetCursor()
            tree.setUpdatesEnabled(True)
            tree.blockSignals(False)
        
        self.unsetCursor()
        self.blockSignals(False)
        self.setUpdatesEnabled(True)
        self.loadingFinished.emit()
    
    def query( self ):
        """
        Returns the query used when querying the database for the records.
        
        :return     <Query> || None
        """
        return self._query
    
    def records( self ):
        """
        Returns the record list that ist linked with this combo box.
        
        :return     [<orb.Table>, ..]
        """
        records = []
        for i in range(self.count()):
            record = self.recordAt(i)
            if record:
                records.append(record)
        return records
    
    def recordAt(self, index):
        """
        Returns the record at the inputed index.
        
        :return     <orb.Table> || None
        """
        return unwrapVariant(self.itemData(index, Qt.UserRole))
    
    def refresh(self, records):
        """
        Refreshs the current user interface to match the latest settings.
        """
        self._loaded = True
        
        # load the information
        if RecordSet.typecheck(records):
            table = records.table()
            self.setTableType(table)
            
            # load the records asynchronously
            if table and table.getDatabase().isThreadEnabled():
                # assign ordering based on tree table
                if self.showTreePopup():
                    tree = self.treePopupWidget()
                    if tree.isSortingEnabled():
                        col = tree.sortColumn()
                        colname = tree.headerItem().text(col)
                        column = table.schema().column(colname)
                        
                        if column:
                            if tree.sortOrder() == Qt.AscendingOrder:
                                sort_order = 'asc'
                            else:
                                sort_order = 'desc'
                            
                            records.setOrder([(column.name(), sort_order)])
                
                self._loadRequested.emit(records)
                return
        
        # load the records synchronously
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.markLoadingStarted()
        self.addRecords(records)
        self.markLoadingFinished()
        QApplication.restoreOverrideCursor()
    
    def setAutoInitialize(self, state):
        """
        Sets whether or not this combo box should auto initialize itself
        when it is shown.
        
        :param      state | <bool>
        """
        self._autoInitialize = state
    
    def setBatchSize(self, size):
        """
        Sets the batch size of records to look up for this record box.
        
        :param      size | <int>
        """
        self._worker.setBatchSize(size)
    
    def setCheckedRecords( self, records ):
        """
        Sets the checked off records to the list of inputed records.
        
        :param      records | [<orb.Table>, ..]
        """
        QApplication.sendPostedEvents(self, -1)
        indexes = []
        
        for i in range(self.count()):
            record = self.recordAt(i)
            if record is not None and record in records:
                indexes.append(i)
        
        self.setCheckedIndexes(indexes)
    
    def setCurrentRecord(self, record):
        """
        Sets the index for this combobox to the inputed record instance.
        
        :param      record      <orb.Table>
        
        :return     <bool> success
        """
        # don't reassign the current record
        if record == self.currentRecord():
            return False
        
        # clear the record
        elif record is None:
            self.setCurrentIndex(-1)
            return True
        
        for i in range(self.count()):
            if self.itemData(i, Qt.UserRole) == record:
                self.setCurrentIndex(i)
                return True
        
        self._currentRecord = record
        return False
    
    def setIconMapper( self, mapper ):
        """
        Sets the icon mapping method for this combobox to the inputed mapper. \
        The inputed mapper method should take a orb.Table instance as input \
        and return a QIcon as output.
        
        :param      mapper | <method> || None
        """
        self._iconMapper = mapper
    
    def setLabelMapper( self, mapper ):
        """
        Sets the label mapping method for this combobox to the inputed mapper.\
        The inputed mapper method should take a orb.Table instance as input \
        and return a string as output.
        
        :param      mapper | <method>
        """
        self._labelMapper = mapper
    
    def setQuery( self, query ):
        """
        Sets the query for this record box for generating records.
        
        :param      query | <Query> || None
        """
        tableType = self.tableType()
        if not tableType:
            return False
        
        self.refresh(tableType.select(where = query))
        return True
    
    def setRecords(self, records):
        """
        Sets the records on this combobox to the inputed record list.
        
        :param      records | [<orb.Table>, ..]
        """
        self.refresh(records)
    
    def setRequired( self, state ):
        """
        Sets the required state for this combo box.  If the column is not
        required, a blank record will be included with the choices.
        
        :param      state | <bool>
        """
        self._required = state
    
    def setShowTreePopup(self, state):
        """
        Sets whether or not to use an ORB tree widget in the popup for this
        record box.
        
        :param      state | <bool>
        """
        self._showTreePopup = state
    
    def setTableLookupIndex(self, index):
        """
        Sets the name of the index method that will be used to lookup
        records for this combo box.
        
        :param    index | <str>
        """
        self._tableLookupIndex = str(index)
    
    def setTableType( self, tableType ):
        """
        Sets the table type for this record box to the inputed table type.
        
        :param      tableType | <orb.Table>
        """
        self._tableType     = tableType
        
        if tableType:
            self._tableTypeName = tableType.schema().name()
        else:
            self._tableTypeName = ''
    
    def setTableTypeName(self, name):
        """
        Sets the table type name for this record box to the inputed name.
        
        :param      name | <str>
        """
        self._tableTypeName = str(name)
        self._tableType = None
    
    def showPopup(self):
        """
        Overloads the popup method from QComboBox to display an ORB tree widget
        when necessary.
        
        :sa     setShowTreePopup
        """
        if not self.showTreePopup():
            return super(XOrbRecordBox, self).showPopup()
        
        tree = self.treePopupWidget()
        
        if tree and not tree.isVisible():
            tree.move(self.mapToGlobal(QPoint(0, self.height())))
            tree.resize(self.width(), 250)
            tree.resizeToContents()
            tree.filterItems('')
            tree.show()
    
    def showTreePopup(self):
        """
        Sets whether or not to use an ORB tree widget in the popup for this
        record box.
        
        :return     <bool>
        """
        return self._showTreePopup
    
    def tableLookupIndex(self):
        """
        Returns the name of the index method that will be used to lookup
        records for this combo box.
        
        :return     <str>
        """
        return self._tableLookupIndex
    
    def tableType( self ):
        """
        Returns the table type for this instance.
        
        :return     <subclass of orb.Table> || None
        """
        if not self._tableType:
            if self._tableTypeName:
                self._tableType = Orb.instance().model(str(self._tableTypeName))
            
        return self._tableType
    
    def tableTypeName(self):
        """
        Returns the table type name that is set for this combo box.
        
        :return     <str>
        """
        return self._tableTypeName
    
    def treePopupWidget(self):
        """
        Returns the popup widget for this record box when it is supposed to
        be an ORB tree widget.
        
        :return     <XTreeWidget>
        """
        if not self._treePopupWidget:
            # create the treewidget
            tree = XTreeWidget(self)
            tree.setWindowFlags(Qt.Popup)
            tree.setFocusPolicy(Qt.StrongFocus)
            tree.installEventFilter(self)
            tree.setAlternatingRowColors(True)
            tree.setShowGridColumns(False)
            tree.setRootIsDecorated(False)
            tree.setVerticalScrollMode(tree.ScrollPerPixel)
            
            # create connections
            tree.itemClicked.connect(self.acceptRecord)
            
            self.lineEdit().textEdited.connect(tree.filterItems)
            self.lineEdit().textEdited.connect(self.showPopup)
            
            self._treePopupWidget = tree
        
        return self._treePopupWidget
    
    def worker(self):
        """
        Returns the worker object for loading records for this record box.
        
        :return     <XOrbLookupWorker>
        """
        return self._worker
    
    x_batchSize         = Property(int, batchSize, setBatchSize)
    x_required          = Property(bool, isRequired, setRequired)
    x_tableTypeName     = Property(str, tableTypeName, setTableTypeName)
    x_tableLookupIndex  = Property(str, tableLookupIndex, setTableLookupIndex)
    x_showTreePopup     = Property(bool, showTreePopup, setShowTreePopup)
    
__designer_plugins__ = [XOrbRecordBox]

# register save and load methods
def getWidgetValue(w):
    if w.isCheckable():
        return w.checkedRecords()
    return w.currentRecord()

def setWidgetValue(w, v):
    if w.isCheckable():
        w.setCheckedRecords(v)
    else:
        w.setCurrentRecord(v)

import projexui
projexui.registerWidgetValue(XOrbRecordBox, getWidgetValue, setWidgetValue)