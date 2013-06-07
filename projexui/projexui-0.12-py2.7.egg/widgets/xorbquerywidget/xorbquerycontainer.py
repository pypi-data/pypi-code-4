""" [desc] """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

from orb import Query, QueryCompound
from projexui.qt import Signal
from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QWidget, QVBoxLayout, QMenu

from projexui.widgets.xorbquerywidget.xorbqueryentrywidget \
              import XOrbQueryEntryWidget

import projexui

class XOrbQueryContainer(QWidget):
    """ """
    entriesUpdated = Signal()
    enterCompoundRequested = Signal(object, object)
    exitCompoundRequested = Signal()
    
    def __init__( self, parent = None ):
        super(XOrbQueryContainer, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._queryWidget   = parent
        self._entryWidget   = QWidget(self)
        self._currentJoiner = QueryCompound.Op.And
        
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.setSpacing(3)
        self._entryWidget.setLayout(layout)
        self.uiQueryAREA.setWidget(self._entryWidget)
        
        # set default properties
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # create connections
        self.uiBackBTN.clicked.connect(self.exitCompoundRequested)
        self.entriesUpdated.connect(self.refreshEntries)
        self.customContextMenuRequested.connect(self.showMenu)
    
    def addEntry(self, query=None, entry=None):
        if query is None:
            query = Query()
        
        layout = self._entryWidget.layout()
        index = layout.count() - 1
        if entry:
            index = layout.indexOf(entry) + 1
        
        widget = XOrbQueryEntryWidget(self, self.tableType())
        layout.insertWidget(index, widget)
        
        widget.setQuery(query)
        
        if not self.signalsBlocked():
            self.entriesUpdated.emit()
        
        return widget
    
    def checkedEntries(self):
        """
        Returns the widgets that are checked for this widget.
        
        :return     [<XOrbQueryEntryWidget>, ..]
        """
        return [entry for entry in self.entries() if entry.isChecked()]
    
    def clear(self):
        """
        Clears out the widgets for this query builder.
        """
        layout = self._entryWidget.layout()
        for i in range(layout.count() - 1):
            widget = layout.itemAt(i).widget()
            widget.close()
            widget.deleteLater()
    
    def createCompoundFromChecked(self):
        """
        Creates a new compound query from the checked entry list.
        
        :return     <orb.QueryCompound>
        """
        checked_entries = self.checkedEntries()
        
        if len(checked_entries) <= 1:
            return QueryCompound()
        
        self.setUpdatesEnabled(False)
        joiner = self.currentJoiner()
        query = Query()
        for entry in checked_entries:
            if joiner == QueryCompound.Op.And:
                query &= entry.query()
            else:
                query |= entry.query()
        
        # clear out the existing containers
        first = checked_entries[0]
        first.setQuery(query)
        first.setChecked(False)
        
        layout = self._entryWidget.layout()
        for i in range(len(checked_entries) - 1, 0, -1):
            w = checked_entries[i]
            layout.takeAt(layout.indexOf(w))
            w.close()
            w.deleteLater()
        
        self.refreshEntries()
        self.setUpdatesEnabled(True)
        
        if not self.signalsBlocked():
            self.enterCompound(first, query)
    
    def currentJoiner(self):
        return self._currentJoiner
    
    def enterCompound(self, entry, query):
        self.enterCompoundRequested.emit(first, query)
    
    def entries(self):
        """
        Returns the entry widgets for this widget.
        
        :return     [<XOrbQueryEntryWidget>, ..]
        """
        layout = self._entryWidget.layout()
        output = []
        for i in range(layout.count() - 1):
            output.append(layout.itemAt(i).widget())
        return output
    
    def moveDown(self, entry):
        """
        Moves the current query down one entry.
        """
        if not entry:
            return
        
        entries = self.entries()
        next = entries[entries.index(entry) + 1]
        
        entry_q = entry.query()
        next_q  = next.query()
        
        next.setQuery(entry_q)
        entry.setQuery(next_q)
    
    def moveUp(self, entry):
        """
        Moves the current query down up one entry.
        """
        if not entry:
            return
        
        entries = self.entries()
        next = entries[entries.index(entry) - 1]
        
        entry_q = entry.query()
        next_q  = next.query()
        
        next.setQuery(entry_q)
        entry.setQuery(next_q)
    
    def pluginFactory(self):
        """
        Returns the plugin factory for this widget.  You can define a custom
        factory for handling specific columns or column types based on your
        table type.
        
        :return     <XOrbQueryPluginFactory>
        """
        return self._queryWidget.pluginFactory()
    
    def query(self):
        """
        Returns the query that is defined by this current panel.
        
        :return     <orb.Query>
        """
        joiner = self.currentJoiner()
        query = Query()
        for entry in self.entries():
            if joiner == QueryCompound.Op.And:
                query &= entry.query()
            else:
                query |= entry.query()
        
        query.setName(self.uiNameTXT.text())
        
        return query
    
    def queryWidget(self):
        """
        Returns the query widget linked with this container.
        
        :return     <XOrbQueryWidget>
        """
        return self._queryWidget
    
    def removeEntry(self, entry):
        if not entry:
            return
        
        layout = self._entryWidget.layout()
        if layout.count() == 2:
            entry.setQuery(Query())
            return
        
        layout.takeAt(layout.indexOf(entry))
        entry.close()
        entry.deleteLater()
        
        if not self.signalsBlocked():
            self.entriesUpdated.emit()
    
    def refreshEntries(self):
        layout = self._entryWidget.layout()
        for i in range(layout.count() - 1):
            widget = layout.itemAt(i).widget()
            widget.setFirst(i == 0)
            widget.setLast(i == (layout.count() - 2))
    
    def setQuery(self, query):
        """
        Sets the query for this wigdet to the inputed query instance.
        
        :param      query | <orb.Query> || <orb.QueryCompound>
        """
        # add entries
        table = self.tableType()
        
        self.setUpdatesEnabled(False)
        self.blockSignals(True)
        self.clear()
        
        if query is None or table is None:
            self.setEnabled(False)
            self.setUpdatesEnabled(True)
            self.blockSignals(False)
            return
        else:
            self.setEnabled(True)
        
        # load the queries for this item
        if QueryCompound.typecheck(query):
            queries = query.queries()
            self.setCurrentJoiner(query.operatorType())
        else:
            queries = [query]
        
        self.uiNameTXT.setText(query.name())
        
        layout = self._entryWidget.layout()
        for index, query in enumerate(queries):
            widget = self.addEntry(query)
            widget.setFirst(index == 0)
            widget.setLast(index == (len(queries) - 1))
            widget.setJoiner(self.currentJoiner())
        
        self.setUpdatesEnabled(True)
        self.blockSignals(False)
    
    def setCurrentJoiner(self, joiner):
        self._currentJoiner = joiner
        layout = self._entryWidget.layout()
        for i in range(layout.count() - 1):
            widget = layout.itemAt(i).widget()
            widget.setJoiner(joiner)
    
    def setShowBack(self, state):
        # check to see if we're working on the current query
        self.uiBackBTN.setVisible(state)
        self.uiNameTXT.setVisible(state)
    
    def showMenu(self, point=None):
        """
        Shows a menu for editing the query objects.
        """
        checked_entries = self.checkedEntries()
        if len(checked_entries) <= 1:
            return
        
        menu = QMenu(self)
        grp_act = menu.addAction('Group Entries')
        
        triggered = menu.exec_(self.mapToGlobal(point))
        
        # group the checked containers together
        if triggered == grp_act:
            self.createCompoundFromChecked()
    
    def tableType(self):
        """
        Returns the table type instance for this widget.
        
        :return     <subclass of orb.Table>
        """
        return self._queryWidget.tableType()