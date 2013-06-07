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
import re
import time

import projexui

from projexui.qt import Signal, Slot, Property, PyObject
from projexui.qt.QtCore import Qt,\
                               QMimeData,\
                               QByteArray,\
                               QObject,\
                               QThread,\
                               QTimer

from projexui.qt.QtGui import QTreeWidgetItem,\
                              QColor,\
                              QApplication

from projexui.qt import QtGui

from projexui.xcolorset                             import XColorSet
from projexui.widgets.xtreewidget                   import XTreeWidget,\
                                                           XTreeWidgetDelegate
from projexui.widgets.xorbtreewidget.xorbrecorditem import XOrbRecordItem
from projexui.widgets.xorbtreewidget.xorbgroupitem  import XOrbGroupItem
from projexui.widgets.xloaderwidget                 import XLoaderWidget
from projexui.widgets.xurlwidget                    import XUrlWidget
from projexui.widgets.xfilepathedit                 import XFilepathEdit
from projexui.xorblookupworker                      import XOrbLookupWorker

logger = logging.getLogger(__name__)

try:
    from orb import RecordSet, Orb, Query as Q, ColumnType

except ImportError:
    logger.warning('The XOrbTreeWidget will not work without the orb package.')
    RecordSet = None
    Orb = None
    Q = None

#----------------------------------------------------------------------

class XOrbEditorPlugin(object):
    def __init__(self, editorClass=None):
        self._editorClass = editorClass
        
    def createEditor(self, parent, record, column):
        if self._editorClass:
            return self._editorClass(parent)
        return None
    
    def setEditorValue(self, editor, record, column):
        value = record.recordValue(column.name(), autoInflate=True)
        projexui.setWidgetValue(editor, value)
    
    def setRecordValue(self, editor, record, column):
        value, success = projexui.widgetValue(editor)
        if success:
            record.setRecordValue(column.name(), value)

#----------------------------------------------------------------------

class ForeignKeyPlugin(XOrbEditorPlugin):
    def createEditor(self, parent, record, column):
        editor = super(ForeignKeyPlugin, self).createEditor(parent,
                                                            record,
                                                            column)
        
        if editor:
            model = column.referenceModel()
            if model:
                editor.setRequired(column.required())
                editor.setRecords(model.select())
        
        return editor

#----------------------------------------------------------------------

class NumericPlugin(XOrbEditorPlugin):
    def createEditor(self, parent, record, column):
        editor = super(NumericPlugin, self).createEditor(parent,
                                                         record,
                                                         column)
        
        if editor:
            editor.setMaximum(1000000)
            editor.setMinimum(-1000000)
        
        return editor

#----------------------------------------------------------------------

class XOrbTreeWidgetDelegate(XTreeWidgetDelegate):
    def __init__(self, *args, **kwds):
        super(XOrbTreeWidgetDelegate, self).__init__(*args, **kwds)
        
        self._plugins = {}
        
        # register default plugins
        self.registerPlugin(XOrbEditorPlugin(QtGui.QDateEdit),
                            ColumnType.Date)
        
        self.registerPlugin(XOrbEditorPlugin(QtGui.QDateTimeEdit),
                            ColumnType.Datetime)
        
        self.registerPlugin(XOrbEditorPlugin(QtGui.QTimeEdit),
                            ColumnType.Time)
        
        for typ in (ColumnType.String, ColumnType.Password):
            self.registerPlugin(XOrbEditorPlugin(QtGui.QLineEdit), typ)
        
        self.registerPlugin(XOrbEditorPlugin(XFilepathEdit),
                            ColumnType.Filepath)
        
        self.registerPlugin(NumericPlugin(QtGui.QSpinBox),
                            ColumnType.Integer)
        
        for typ in (ColumnType.Double, ColumnType.Decimal):
            self.registerPlugin(NumericPlugin(QtGui.QDoubleSpinBox), typ)
        
        from projexui.widgets.xorbrecordbox import XOrbRecordBox
        self.registerPlugin(XOrbEditorPlugin(XUrlWidget), ColumnType.Url)
        self.registerPlugin(ForeignKeyPlugin(XOrbRecordBox),
                            ColumnType.ForeignKey)
    
    def column(self, index):
        tree = self.parent()
        tableType = tree.tableType()
        column_name = tree.columnOf(index.column())
        
        if not tableType:
            return None
        
        return tableType.schema().column(column_name)
    
    def createEditor( self, parent, option, index ):
        """
        Creates a new editor for the given index parented to the inputed widget.
        
        :param      parent | <QWidget>
                    option | <QStyleOption>
                    index  | <QModelIndex>
        
        :return     <QWidget> || None
        """
        # determine the editor to use for the inputed index based on the
        # table column
        item   = self.parent().itemFromIndex(index)
        column = self.column(index)
        
        # edit based on column preferences
        if column and isinstance(item, XOrbRecordItem):
            plugin = self.plugin(column)
            if not plugin:
                return None
            
            return plugin.createEditor(parent, item.record(), column)
        
        return super(XOrbTreeWidgetDelegate, self).createEditor(parent,
                                                                option,
                                                                index)
        
    def plugin(self, column):
        if not column:
            return None
        
        a = (column.columnType(), column.name())
        b = (column.columnType(), None)
        c = (None, column.name())
        d = (None, None)
        
        for typ in (a, b, c, d):
            try:
                return self._plugins[typ]
            except:
                continue
        
        return None
    
    def registerPlugin(self, plugin, columnType=None, columnName=None):
        self._plugins[(columnType, columnName)] = plugin

    def setEditorData(self, editor, index):
        item   = self.parent().itemFromIndex(index)
        column = self.column(index)
        
        # edit based on column preferences
        if column and isinstance(item, XOrbRecordItem):
            plugin = self.plugin(column)
            if not plugin:
                return
            
            plugin.setEditorValue(editor, item.record(), column)
        else:
            super(XOrbTreeWidgetDelegate, self).setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        item   = self.parent().itemFromIndex(index)
        column = self.column(index)
        
        # edit based on column preferences
        if column and isinstance(item, XOrbRecordItem):
            plugin = self.plugin(column)
            if not plugin:
                return
            
            record = item.record()
            plugin.setRecordValue(editor, record, column)
            item.updateRecordValues()
        
        # edit standard mechanism
        else:
            super(XOrbTreeWidgetDelegate, self).setModelData(editor, model, index)

#------------------------------------------------------------------------------

class XOrbTreeWidget(XTreeWidget):
    """ """
    __designer_group__ = 'ProjexUI - ORB'
    
    _loadRequested = Signal(object)
    
    currentPageChanged      = Signal(int)
    pageCountChanged        = Signal(int)
    pageSizeChanged         = Signal(int)
    queryChanged            = Signal()
    recordClicked           = Signal(object)
    recordDoubleClicked     = Signal(object)
    recordCountChanged      = Signal(int)
    recordsChanged          = Signal()
    tableTypeChanged        = Signal()
    
    def __init__( self, parent = None ):
        super(XOrbTreeWidget, self).__init__( parent, XOrbTreeWidgetDelegate )
        
        # define table information
        self._tableTypeName     = ''
        self._tableType         = None
        
        # define lookup information
        self._query             = None
        self._order             = None
        self._groupBy           = None
        self._searchTerms       = ''
        self._baseHint          = ''
        self._loaderThreshold   = 100
        self._columnsInitialized = False
        self._groupingEnabled   = True
        
        # define record information
        self._recordSet         = None  # defines the base record set
        self._currentRecordSet  = None  # defines the current working set
        
        # define paging information
        self._currentPage       = 1
        self._pageCount         = None
        self._pageSize          = 0
        
        # define refresh timer - delays when the records will be loaded until
        # necessary
        self._refreshTimer      = QTimer(self)
        self._refreshTimer.setInterval(500)
        self._refreshTimer.setSingleShot(True)
        
        # define worker thread
        self._worker            = XOrbLookupWorker()
        self._workerThread      = QThread()
        self._worker.moveToThread(self._workerThread)
        self._workerThread.start()
        
        # define column information
        self._columnMappers     = {}
        self._columnOrderNames  = {}
        
        # define UI information
        self._editColumn        = None
        self._recordItemClass   = XOrbRecordItem
        self._recordGroupClass  = XOrbGroupItem
        self._colored           = True
        
        self._colorSet          = XColorSet()
        self._colorSet.setColor('RecordNew',      QColor('green'))
        self._colorSet.setColor('RecordRemoved',  QColor('red'))
        self._colorSet.setColor('RecordModified', QColor('blue'))
        
        # create connections
        self.queryChanged.connect(self.refreshQueryRecords)
        self.sortingChanged.connect(self.reorder)
        
        # create threading connections
        QApplication.instance().aboutToQuit.connect(self.__cleanupWorker)
        
        self._loadRequested.connect(self._worker.loadRecords)
        
        self._worker.loadingStarted.connect(self.markLoadingStarted)
        self._worker.loadingFinished.connect(self.markLoadingFinished)
        self._worker.loadedRecord.connect(self.createRecordItem)
        self._worker.loadedGroup.connect(self.createGroupItem)
        
        self.itemExpanded.connect(      self.loadItem )
        self.itemExpanded.connect(      self.updateItemIcon )
        self.itemCollapsed.connect(     self.updateItemIcon )
        self.itemClicked.connect(self.emitRecordClicked)
        self.itemDoubleClicked.connect(self.emitRecordDoubleClicked)
        self._refreshTimer.timeout.connect(self.refresh)
    
    def __del__(self):
        self.__cleanupWorker()
    
    def __commitToSelected(self, item, columnIndex):
        if columnIndex != self._editColumn:
            return
        
        tableType = self.tableType()
        if not tableType:
            return
        
        if not isinstance(item, XOrbRecordItem):
            return
        
        schema = tableType.schema()
        columnTitle = self.columnOf(columnIndex)
        column = schema.column(columnTitle)
        if not column:
            return
        
        columnName = column.name()
        value = item.record().recordValue(columnName)
        
        self.blockSignals(True)
        for sel_item in self.selectedItems():
            if not isinstance(sel_item, XOrbRecordItem):
                continue
            
            if sel_item != item:
                sel_item.record().setRecordValue(columnName, value)
                sel_item.updateRecordValues()
        self.blockSignals(False)
    
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
    
    def clearAll( self ):
        """
        Clears the tree and record information.
        """
        # clear the tree information
        self.clear()
        
        # clear table information
        self._tableTypeName  = ''
        self._tableType      = None
        
        # clear the records information
        self._recordSet         = None
        self._currentRecordSet  = None
        
        # clear lookup information
        self._query             = None
        self._order             = None
        self._groupBy           = None
        
        # clear paging information
        self._currentPage       = 1
        self._pageCount         = None
        
        if ( not self.signalsBlocked() ):
            self.recordsChanged.emit()
    
    def clearSearch( self ):
        """
        Clears the serach information for this tree.
        """
        self._currentRecordSet = None
        
        if ( not self.signalsBlocked() ):
            self.recordsChanged.emit()
    
    def colorSet( self ):
        """
        Returns the color set linked with this tree.
        
        :return     <XColorSet>
        """
        return self._colorSet
    
    def columnOrderName( self, columnName ):
        """
        Returns the order name that will be used for this column when
        sorting the database model.
        
        :param      columnName     | <str>
        
        :return     <str> | orderName
        """
        return self._columnOrderNames.get(str(columnName), '')
    
    def columnMapper( self, columnName ):
        """
        Returns the callable method that is associated with the inputed
        column name.
        
        :param      columnName | <str>
        
        :sa         setColumnMapper
        
        :return     <method> || <function> || <lambda> || None
        """
        return self._columnMappers.get(str(columnName))
    
    def columnMappers( self ):
        """
        Returns the dictionary of column mappers linked with this tree.
        
        :sa         setColumnMapper
        
        :return     {<str> columnName: <callable>, ..}
        """
        return self._columnMappers
    
    def commit( self ):
        """
        Commits the changes for all the items in the tree.
        
        :return     <bool> | success
        """
        remove_items = []
        commit_items = []
        
        # remove all the items
        commit_state = XOrbRecordItem.State.Modified | XOrbRecordItem.State.New
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            remove_items += item.findItemsByState(XOrbRecordItem.State.Removed)
            commit_items += item.findItemsByState(commit_state)
        
        # make sure we can remove the records
        for item in remove_items:
            record = item.record()
            try:
                record.remove(dryRun = True)
            except orb.errors.CannotRemoveError, err:
                QMessageBox.information(self,
                                        'Cannot Remove',
                                        str(err))
                return False
        
        # remove the records
        remove_set = RecordSet([item.record() for item in remove_items])
        remove_set.remove()
        
        for item in remove_items:
            parent = item.parent()
            if ( parent ):
                index = parent.indexOfChild(item)
                parent.takeChild(index)
            else:
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)
        
        # commit the new records
        for item in commit_items:
            item.record().commit()
            item.setRecordState( XOrbRecordItem.State.Normal )
        
        return True
    
    def commitData(self, widget):
        """
        Commits the data from the widget to the model.
        
        :param      widget | <QWidget>
        """
        self._editColumn = self.currentColumn()
        self.itemChanged.connect(self.__commitToSelected)
        super(XOrbTreeWidget, self).commitData(widget)
        self.itemChanged.disconnect(self.__commitToSelected)
        self._editColumn = None
    
    def createRecordItem(self, record, parent=None):
        """
        Creates the record item instance for the given record.
        
        :param      parent      | <QTreeWidgetItem> || <QTreeWidget>
                    record      | <orb.Table>
        
        :return     <QTreeWidgetItem>
        """
        if parent is None:
            parent=self
        
        return self.recordItemClass()(parent, record)
    
    def createRecordItems(self, records, parent=None):
        """
        Creates the record item instance for the given record.
        
        :param      records     | [<orb.Table>, ..]
                    parent      | <QTreeWidgetItem> || <QTreeWidget>
        
        :return     <QTreeWidgetItem>
        """
        if parent is None:
            parent=self
            
        cls = self.recordItemClass()
        blocked = self.signalsBlocked()
        self.blockSignals(True)
        self.setUpdatesEnabled(False)
        for record in records:
            cls(parent, record)
        
        if not blocked:
            self.blockSignals(False)
            self.setUpdatesEnabled(True)
    
    def createGroupItem(self, groupName, records, parent=None):
        """
        Creates the grouping item instance for the group with the given record
        information.
        
        :param      groupName   | <str>
                    record      | [<orb.Table>, ..] || <dict>
                    parent      | <QTreeWidgetItem> || <QTreeWidget>
        
        :return     <QTreeWidgetItem>
        """
        if parent is None:
            parent = self
        
        return self.recordGroupClass()(parent, groupName, records)
    
    def currentPage( self ):
        """
        Returns the current page that this tree is displaying.
        
        :return     <int>
        """
        return self._currentPage
    
    def currentRecord( self ):
        """
        Returns the current record from the tree view.
        
        :return     <orb.Table> || None
        """
        item = self.currentItem()
        if ( isinstance(item, XOrbRecordItem) ):
            return item.record()
        return None
    
    def currentRecordSet( self ):
        """
        Returns the current record set for this widget, after all searching,
        paging, refining, etc. that has occurred from the base record set.
        
        :sa     refine, search, setCurrentPage, records
        
        :return     <orb.RecordSet>
        """
        if self._currentRecordSet is None:
            return self.recordSet()
        
        return self._currentRecordSet
    
    @Slot()
    def disableGrouping(self):
        """
        Disables the grouping system for this widget.
        """
        self.setGroupingEnabled(False)
    
    def groupBy( self ):
        """
        Returns the group by information for this tree.
        
        :return     [<str>, ..]
        """
        return self._groupBy
    
    @Slot()
    def groupByHeaderIndex(self):
        """
        Assigns the grouping to the current header index.
        """
        index = self.headerMenuColumn()
        columnTitle = self.columnOf(index)
        tableType = self.tableType()
        
        if not tableType:
            return
        
        column = tableType.schema().column(columnTitle)
        if not column:
            return
        
        self.setGroupBy(column.name())
        self.setGroupingEnabled(True)
    
    def emitRecordClicked(self, item):
        """
        Emits the record clicked signal for the given item, provided the
        signals are not currently blocked.
        
        :param      item | <QTreeWidgetItem>
        """
        if isinstance(item, XOrbRecordItem) and not self.signalsBlocked():
            self.recordClicked.emit(item.record())
    
    def emitRecordDoubleClicked(self, item):
        """
        Emits the record clicked signal for the given item, provided the
        signals are not currently blocked.
        
        :param      item | <QTreeWidgetItem>
        """
        if isinstance(item, XOrbRecordItem) and not self.signalsBlocked():
            self.recordDoubleClicked.emit(item.record())
    
    @Slot()
    def enableGrouping(self):
        """
        Enables the grouping system for this widget.
        """
        self.setGroupingEnabled(True)
    
    def findRecordItem(self, record, parent=None):
        """
        Looks through the tree hierarchy for the given record.
        
        :param      record | <orb.Record>
                    parent | <QTreeWidgetItem> || None
        
        :return     <XOrbRecordItem> || None
        """
        if not parent:
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                
                try:
                    found = item.record() == record
                except:
                    found = False
                
                if found:
                    return item
                
                output = self.findRecordItem(record, item)
                if output:
                    return output
        else:
            for c in range(parent.childCount()):
                item = parent.child(c)
                
                try:
                    found = item.record() == record
                except:
                    found = False
                
                if found:
                    return item
                
                output = self.findRecordItem(record, item)
                if output:
                    return output
        
        return None
    
    def initializeColumns( self ):
        """
        Initializes the columns that will be used for this tree widget based \
        on the table type linked to it.
        """
        tableType = self.tableType()
        if not tableType:
            return
        elif self._columnsInitialized:
            return
        
        # set the table header information
        tschema = tableType.schema()
        columns = tschema.columns()
        
        self.setColumns(sorted([col.displayName() for col in columns]))
        self.resizeToContents()
    
    def isColored( self ):
        """
        Returns whether or not this widget should color its records.
        
        :return     <bool>
        """
        return self._colored
    
    def isGroupingEnabled(self):
        """
        Returns whether or not the grouping system is enabled for this
        widget.
        
        :return     <bool>
        """
        return self._groupingEnabled
    
    def loaderThreshold(self):
        """
        Returns the number of records that should be required before showing
        the loader.  You can alter this number if you know certain records
        or tables take longer than others to load.
        
        :return     <int>
        """
        return self._loaderThreshold
    
    def loadItem( self, item ):
        """
        Prompts the item to use its lazy loading logic.
        
        :param      item | <QTreeWidgetItem>
        """
        item.load()
    
    def markLoadingStarted(self):
        self.setCursor(Qt.WaitCursor)
        self._baseHint = self.hint()
        
        self.setHint('Loading records...')
        
        self.setUpdatesEnabled(False)
        self.blockAllSignals(True)
        
        # clear the tree widget items
        self.clear()
    
    def markLoadingFinished(self):
        self.smartResizeColumnsToContents()
        self.setUpdatesEnabled(True)
        self.blockAllSignals(False)
        
        self.setHint(self._baseHint)
        
        self.unsetCursor()
        XLoaderWidget.stop(self, force=True)
    
    def mimeData( self, items ):
        """
        Returns the mime data for dragging for this instance.
        
        :param      items | [<QTreeWidgetItem>, ..]
        """
        func = self.dataCollector()
        if ( func ):
            return func(self, items)
        
        # extract the records from the items
        records = []
        for item in self.selectedItems():
            if isinstance(item, XOrbRecordItem):
                records.append(item.record())
        
        # create the mime data
        data = QMimeData()
        self.dataStoreRecords(data, records)
        return data
    
    def order( self ):
        """
        Returns the order for this instance.
        
        :return     [(<str> column, <str> order), ..] || None
        """
        return self._order
    
    def query( self ):
        """
        Returns the query that will be used for the records for this tree.
        
        :return     <orb.Query>
        """
        return self._query
    
    def pageCount( self ):
        """
        Returns the page count information for this widget.
        
        :return     <int>
        """
        if self._pageCount is None:
            self._pageCount = self.currentRecordSet().pageCount(self.pageSize())
        return self._pageCount
    
    def pageSize( self ):
        """
        Returns the page size for this widget.  If the page size is set to -1,
        then there is no sizing and all records are displayed.
        
        :return     <int>
        """
        return self._pageSize
    
    def recordGroupClass( self ):
        """
        Returns the record group class instance linked with this tree widget.
        
        :return     <XObrGroupItem>
        """
        return self._recordGroupClass
    
    def recordItemClass( self ):
        """
        Returns the record item class instance linked with this tree widget.
        
        :return     <XObrRecordItem>
        """
        return self._recordItemClass
    
    def records(self):
        """
        Returns the record set instance linked with this tree.
        
        :sa         recordSet
        
        :return     <orb.RecordSet>
        """
        return self.recordSet()
    
    def recordSet( self ):
        """
        Returns the record set instance linked with this tree.
        
        :return     <orb.RecordSet>
        """
        # define the base record set
        if not self._recordSet:
            return RecordSet()
            
        return self._recordSet
    
    def registerEditorPlugin(self, plugin, columnType=None, columnName=None):
        self.itemDelegate().registerPlugin(plugin, columnType, columnName)
    
    def reorder( self, index, order ):
        """
        Reorders the data being displayed in this tree.  It will check to
        see if a server side requery needs to happen based on the paging
        information for this tree.
        
        :param      index | <column>
                    order | <Qt.SortOrder>
        
        :sa         setOrder
        """
        column    = self.columnOf(index)
        orderName = self.columnOrderName(column)
        
        if ( not orderName ):
            return
        
        order = {Qt.AscendingOrder: 'asc', Qt.DescendingOrder: 'desc'}[order]
        self.setOrder([(orderName, order)])
        
        if ( self.pageCount() > 1 ):
            self.refresh()
    
    def refresh(self, reloadData=False):
        """
        Refreshes the record list for the tree.
        """
        if not self.isVisible():
            self._refreshTimer.start()
            return
        
        # cancel out the previous worker
        while self._worker.isRunning():
            self._worker.cancel()
            time.sleep(0.25)
        
        # grab the record set
        currset = self.currentRecordSet()
        
        # group the information
        if self._searchTerms:
            currset.setGroupBy(None)
            pageSize = 0
            pageCount = 1
        
        # work with groups
        elif self.groupBy() and self.isGroupingEnabled():
            currset.setGroupBy(self.groupBy())
            pageSize = 0
            pageCount = 1
        
        # work with pages
        elif 1 < self.pageSize():
            currset.setGroupBy(None)
            self._worker.setBatched(False)
            currset = currset.page(self.currentPage(), self.pageSize())
            pageSize = self.pageSize()
            pageCount = self.pageCount()
        
        # work with batching
        else:
            currset.setGroupBy(None)
            self._worker.setBatched(True)
            pageSize = self.pageSize()
            pageCount = self.pageCount()
        
        total = len(currset)
        
        # order the information
        if self.order():
            currset.setOrdered(True)
            currset.setOrder(self.order())
        
        # for larger queries, run it through the thread
        if self.loaderThreshold() < total:
            loader = XLoaderWidget.start(self)
            
            self._worker.progressMessageLogged.connect(loader.setMessage)
            self._worker.progressTotalChanged.connect(loader.setTotal)
            self._worker.progressIncremented.connect(loader.increment)
        
        if not self.signalsBlocked():
            self.pageSizeChanged.emit(pageSize)
            self.pageCountChanged.emit(pageCount)
            self.recordCountChanged.emit(total)
        
        if currset.isThreadEnabled():
            self._loadRequested.emit(currset)
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self._worker.loadRecords(currset)
            QApplication.restoreOverrideCursor()
    
    def refreshQueryRecords( self ):
        """
        Refreshes the query results based on the tree's query.
        """
        recordSet = RecordSet(self.tableType())
        recordSet.setQuery(self.query())
        self.setRecordSet(recordSet)
    
    @Slot('QString')
    def searchRecords( self, search ):
        """
        Creates a search for the inputed records by joining the search terms
        and query from the inputed search string by using the 
        Orb.Query.fromSearch method.
        
        :param      search  | <str>
                    refined | <orb.Query> || None
        
        :return     <bool> | success
        """
        # take the base record set
        self._currentRecordSet  = None
        self._pageCount         = None
        self._searchTerms       = str(search)
        
        # if we don't have a search, then go back to the default records
        if not search:
            if not self.signalsBlocked():
                if self._recordSet:
                    self._recordSet.clear()
                
                self.refresh()
                self.recordsChanged.emit()
                self.pageCountChanged.emit(self.pageCount())
                return False
        
        # start from our default record set
        rset = self.recordSet()
        
        # if the set is empty, then search the whole table set
        if rset.isEmpty():
            rset = self.tableType().select()
        
        self._currentRecordSet = rset.search(search)
        
        # update widget and notify any listeners
        if not self.signalsBlocked():
            self.refresh()
            self.recordsChanged.emit()
            self.pageCountChanged.emit(self.pageCount())
        
        return True
    
    def selectedRecords( self ):
        """
        Returns a list of all the selected records for this widget.
        
        :return     [<orb.Table>, ..]
        """
        output = []
        for item in self.selectedItems():
            if ( isinstance(item, XOrbRecordItem) ):
                output.append(item.record())
        return output
    
    def setColored( self, state ):
        """
        Sets the colored state for this tree.
        
        :param      state | <bool>
        """
        self._colored = state
    
    def setColorSet( self, colorSet ):
        """
        Sets the color set linked with this tree.
        
        :param     colorSet | <XColorSet>
        """
        self._colorSet = colorSet
    
    def setColumns(self, columns):
        """
        Sets the columns for this widget, and marks the system as having
        been initialized.
        
        :param      columns | [<str>, ..]
        """
        super(XOrbTreeWidget, self).setColumns(columns)
        self.setFilteredColumns(range(len(columns)))
        self._columnsInitialized = True
    
    def setColumnMapper( self, columnName, callable ):
        """
        Sets the mapper for the given column name to the callable.  The inputed
        callable should accept a single argument for a record from the tree and
        return the text that should be displayed in the column.
        
        :param      columnName | <str>
                    callable   | <function> || <method> || <lambda>
        """
        columnName = str(columnName)
        if ( callable is None and columnName in self._columnMappers ):
            self._columnMappers.pop(columnName)
            return
        
        self._columnMappers[str(columnName)] = callable
    
    def setGroupBy( self, groupBy ):
        """
        Sets the grouping information for this tree.
        
        :param      groupBy | [<str> group level, ..] || None
        """
        if groupBy and not type(groupBy) in (list, tuple):
            groupBy = [str(groupBy)]
        
        elif not groupBy:
            groupBy = None
        
        self._groupBy = groupBy
        
        if not self.signalsBlocked():
            self.recordsChanged.emit()
    
    def setGroupingEnabled(self, state, autoRefresh=True):
        """
        Sets whether or not grouping is enabled for this system.
        
        :param      state | <bool>
        """
        self._groupingEnabled = state
        
        self.setRootIsDecorated(state)
        
        if autoRefresh:
            self.refresh()
    
    def setColumnOrderName( self, columnName, orderName ):
        """
        Sets the database name to use when ordering this widget by the 
        given column.  When set, this will trigger a server side reorder
        of information rather than a client side reorder if the information
        displayed is paged - as it will modify what to show for this page
        based on the order.
        
        :param      columnName | <str>
                    orderName  | <str>
        """
        self._columnOrderNames[str(columnName)] = str(orderName)
    
    @Slot(int)
    def setCurrentPage( self, pageno, autoRefresh=True ):
        """
        Sets the current page for this widget to the inputed page number.
        
        :param      pageno | <int>
        """
        # make sure we have a valid page number
        pageno = min(pageno, self.pageCount())
        pageno = max(1, pageno)
        
        # make sure the page number changes
        if ( self._currentPage == pageno ):
            return
        
        # store the new page number and emit the signal if necessary
        self._currentPage = pageno
        
        if not self.signalsBlocked():
            self.currentPageChanged.emit(pageno)
            self.recordsChanged.emit()
        
        if autoRefresh:
            self.refresh()
    
    def setLoaderThreshold(self, threshold):
        self._loaderThreshold = threshold
    
    def setOrder( self, order ):
        """
        Sets the order for the query to the inputed order.
        
        :param      order | [(<str> columName, <str> order), ..]
        """
        self._order = order
    
    @Slot(int)
    def setPageSize(self, pageSize, autoRefresh=True):
        """
        Sets the page size for this widget.  If the page size is set to -1,
        then there is no sizing and all records are displayed.
        
        :return     <int>
        """
        if pageSize == self._pageSize:
            return
        
        self._pageCount = None
        self._pageSize  = pageSize
        
        if not self.signalsBlocked():
            self.pageSizeChanged.emit(pageSize)
            self.pageCountChanged.emit(self.pageCount())
            self.recordsChanged.emit()
        
        if autoRefresh:
            self.refresh()
    
    @Slot(PyObject)
    def setQuery( self, query ):
        """
        Sets the query instance for this tree widget to the inputed query.
        
        :param      query | <orb.Query>
        """
        self._query             = query
        self._currentRecordSet  = None
        
        if ( not self.signalsBlocked() ):
            self.queryChanged.emit()
            self.recordsChanged.emit()
    
    def setRecords( self, records ):
        """
        Manually sets the list of records that will be displayed in this tree.
        
        This is a shortcut method to creating a RecordSet with a list of records
        and assigning it to the tree.
        
        :param      records | [<orb.Table>, ..]
        """
        if not isinstance(records, RecordSet):
            records = RecordSet(records)
        self.setRecordSet(records)
    
    def setRecordGroupClass( self, groupClass ):
        """
        Sets the record group class that will be used for this tree instance.
        
        :param      groupClass | <subclass of XOrbGroupItem>
        """
        self._recordGroupClass = groupClass
    
    def setRecordItemClass( self, itemClass ):
        """
        Sets the record item class that will be used for this tree instance.
        
        :param      itemClass | <subclass of XOrbRecordItem>
        """
        self._recordItemClass = itemClass
    
    @Slot(PyObject)
    def setRecordSet( self, recordSet ):
        """
        Defines the record set that will be used to lookup the information for
        this tree.
        
        :param      records | [<Table>, ..] || None
        """
        if not self.tableType():
            self.setTableType(recordSet.table())
        
        self._currentRecordSet = None
        self._pageCount        = None
        self._recordSet        = recordSet
        
        if not self.signalsBlocked():
            self.refresh()
            
            self.recordsChanged.emit()
            self.pageCountChanged.emit(self.pageCount())
    
    @Slot(PyObject)
    def setTableType( self, tableType ):
        """
        Defines the table class type that this tree will be displaying.
        
        :param      table | <subclass of orb.Table>
        """
        if tableType == self._tableType:
            return
        
        # clear all the information
        blocked = self.signalsBlocked()
        
        self.blockAllSignals(True)
        
        # only clear if necessary
        if self._tableType:
            self.clearAll()
        
        # update the table type data
        self._tableType = tableType
        
        if ( tableType ):
            self._tableTypeName = tableType.__name__
        else:
            self._tableTypeName = ''
            
        self.initializeColumns()
        self.blockAllSignals(blocked)
        
        if ( not self.signalsBlocked() ):
            self.tableTypeChanged.emit()
            self.recordsChanged.emit()
    
    @Slot(str)
    def setTableTypeName( self, tableTypeName ):
        """
        Defines the table type name that this tree will be displaying.
        
        :param      tableTypeName | <str>
        """
        self._tableTypeName = tableTypeName
        if ( not Orb ):
            return
        
        self.setTableType(Orb.instance().model(str(tableTypeName)))
    
    @Slot(PyObject)
    def setTableSchema( self, schema ):
        """
        Sets the table schema for this tree to the inputed schema.
        
        :param      schema | <orb.TableSchema>
        """
        if ( schema ):
            self.setTableType(schema.model())
    
    def tableType( self ):
        """
        Returns the table class type that is linked with this tree widget.
        
        :return     <subclass of orb.Table>
        """
        return self._tableType
    
    def tableTypeName( self ):
        """
        Returns the table type name for this instance.
        
        :return     <str>
        """
        return self._tableTypeName
    
    @Slot()
    def toggleGroupingEnabled(self):
        """
        Toggles whether or not grouping is enabled.
        """
        self.setGroupingEnabled(not self.isGroupingEnabled())
    
    def toggleSelectedItemState( self, state ):
        """
        Toggles the selection for the inputed state.
        
        :param      state | <XOrbRecordItem.State>
        """
        items           = self.selectedItems()
        for item in items:
            if ( item.hasRecordState(state) ):
                item.removeRecordState(state)
            else:
                item.addRecordState(state)
    
    def toggleSelectedRemovedState( self ):
        """
        Toggles the selection for the removed state.
        """
        self.toggleSelectedItemState(XOrbRecordItem.State.Removed)
    
    def updateItemIcon( self, item ):
        """
        Updates the items icon based on its state.
        
        :param      item | <QTreeWidgetItem>
        """
        item.updateIcon()
        
        # update the column width
        self.setUpdatesEnabled(False)
        colwidth = self.columnWidth(0)
        self.resizeColumnToContents(0)
        new_colwidth = self.columnWidth(0)
        
        if ( new_colwidth < colwidth ):
            self.setColumnWidth(0, colwidth)
        self.setUpdatesEnabled(True)
    
    @staticmethod
    def dataHasRecords(mimeData):
        """
        Returns whether or not the inputed mime data has orb record
        data.
        
        :param      mimeData | <QMimeData>
        
        :return     <bool>
        """
        return mimeData.hasFormat('x-application/orb-records')
    
    @staticmethod
    def dataRestoreRecords(mimeData):
        """
        Extracts the records from the inputed drag & drop mime data information.
        This will lookup the models based on their primary key information and
        generate the element class.
        
        :param      mimeData | <QMimeData>
        
        :return     [<orb.Table>, ..]
        """
        if not mimeData.hasFormat('x-application/orb-records'):
            return []
        
        from orb import Orb
        
        repros = str(mimeData.data('x-application/orb-records'))
        repros = repros.split(';')
        
        output =[]
        for repro in repros:
            cls, pkey = re.match('^(\w+)\((.*)\)$', repro).groups()
            pkey = eval(pkey)
            
            model = Orb.instance().model(cls)
            if not model:
                continue
            
            record = model(pkey)
            if record.isRecord():
                output.append(record)
        
        return output
    
    @staticmethod
    def dataStoreRecords(mimeData, records):
        """
        Adds the records to the inputed mime data as a text representation
        under the x-application/orb-records
        
        :param      mimeData | [<orb.Table>, ..]
        """
        record_data = []
        for record in records:
            repro = '%s(%s)' % (record.schema().name(), record.primaryKey())
            record_data.append(repro)
        
        if not record_data:
            return
        
        record_data = ';'.join(record_data)
        mimeData.setData('x-application/orb-records', QByteArray(record_data))
    
    x_loaderThreshold = Property(int, loaderThreshold, setLoaderThreshold)
    x_tableTypeName = Property(str, tableTypeName, setTableTypeName)