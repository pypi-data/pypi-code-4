#!/usr/bin/python

""" Defines a widget for editing orb records within a grid. """

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

from xml.etree import ElementTree

from projexui.qt.QtCore import Qt, QSize
from projexui.qt.QtGui import QWidget, QAction
from projexui.widgets.xorbquerywidget import XOrbQueryWidget
from projexui.widgets.xorbtreewidget import XOrbRecordItem
from projexui.widgets.xpopupwidget import XPopupWidget

import projexui


try:
    from orb import Query as Q

except ImportError:
    logger.warning('The XOrbGridEdit will not work without the orb package.')
    RecordSet = None
    Orb = None
    Q = None

#----------------------------------------------------------------------

class XOrbGridEdit(QWidget):
    """ """
    __designer_group__ = 'ProjexUI - ORB'
    
    def __init__( self, parent = None ):
        super(XOrbGridEdit, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._queryWidget = XOrbQueryWidget(self)
        
        self.uiSearchTXT.setIconSize(QSize(28, 28))
        self.uiSearchTXT.addButton(self.uiQueryBTN)
        
        self.uiQueryBTN.setCentralWidget(self._queryWidget)
        self.uiQueryBTN.setDefaultAnchor(XPopupWidget.Anchor.TopRight)

        # set default properties
        self.uiRecordTREE.setGroupingEnabled(False)
        self.uiRecordTREE.setEditable(True)
        self.uiRecordTREE.setPageSize(25, autoRefresh=False)
        self.uiRecordTREE.setTabKeyNavigation(True)
        
        # create connections
        self.uiRefreshBTN.clicked.connect(self.uiRecordTREE.refresh)
        self.uiSaveBTN.clicked.connect(self.uiRecordTREE.commit)
        self.uiQueryBTN.popupAboutToShow.connect(self.loadQuery)
        self.uiQueryBTN.popupAccepted.connect(self.assignQuery)
        self.uiRecordTREE.headerMenuAboutToShow.connect(self.updateMenu)
    
    def assignQuery(self):
        """
        Assigns the query from the query widget to the edit.
        """
        self.uiRecordTREE.setQuery(self._queryWidget.query())
    
    def loadQuery(self):
        """
        Loads the query for the query widget when it is being shown.
        """
        self._queryWidget.setQuery(self.query())
    
    def updateMenu(self, menu, index):
        tree = self.uiRecordTREE
        
        first_action = menu.actions()[1]
        column = tree.columnOf(index)
        
        grp_action = QAction(menu)
        grp_action.setText('Group by "%s"' % column)
        
        ungrp_action = QAction(menu)
        ungrp_action.setText('Ungroup all')
        
        menu.insertSeparator(first_action)
        menu.insertAction(first_action, grp_action)
        menu.insertAction(first_action, ungrp_action)
        
        grp_action.triggered.connect(self.uiRecordTREE.groupByHeaderIndex)
        ungrp_action.triggered.connect(self.uiRecordTREE.disableGrouping)
    
    def records(self):
        """
        Returns the records that are currently assigned to this widget.
        
        :return     <orb.RecordSet>
        """
        return self.uiRecordTREE.records()
    
    def pagesWidget(self):
        """
        Returns the pages edit for this grid edit.
        
        :return     <XPagesWidget>
        """
        return self.uiPagesEDIT
    
    def query(self):
        """
        Returns the query that is being represented by the current results.
        
        :return     <orb.Query>
        """
        return self.uiRecordTREE.query()
    
    def restoreXml(self, xml):
        """
        Restores the settings for this edit from xml.
        
        :param      xml | <xml.etree.ElementTree>
        """
        # restore grouping
        grps = xml.get('grouping')
        if grps:
            self.uiRecordTREE.setGroupingEnabled(True)
            self.uiRecordTREE.setGroupBy(grps.split(','))
        
        grp_enabled = xml.get('groupingEnabled') == 'True'
        self.uiRecordTREE.setGroupingEnabled(grp_enabled, autoRefresh=False)
        
        # restore hidden columns
        hidden = xml.get('hidden')
        if hidden:
            self.uiRecordTREE.setHiddenColumns(hidden.split(','))
        
        # restore the query
        xquery = xml.find('query')
        if xquery is not None:
            self.setQuery(Q.fromXml(xquery[0]))
    
    def saveXml(self, xml):
        """
        Saves the settings for this edit to the xml parent.
        
        :param      xparent | <xml.etree.ElementTree>
        """
        # save grouping
        tree = self.uiRecordTREE
        
        xml.set('groupingEnabled', str(tree.isGroupingEnabled()))
        if tree.groupBy():
            xml.set('grouping', ','.join(tree.groupBy()))
        
        if tree.hiddenColumns():
            xml.set('hidden', ','.join(tree.hiddenColumns()))
        
        # save the query
        query = self.query()
        if query:
            query.toXml(ElementTree.SubElement(xml, 'query'))
    
    def searchWidget(self):
        """
        Returns the search text edit for this grid edit.
        
        :return     <XLineEdit>
        """
        return self.uiSearchTXT
    
    def setQuery(self, query):
        """
        Sets the query for this edit to the inputed query.
        
        :param      query | <orb.Query>
        """
        self.uiRecordTREE.setQuery(query)
    
    def setTableType(self, tableType, autoRefresh=True):
        """
        Sets the table type associated with this edit.
        
        :param      tableType | <subclass of orb.Table>
        """
        self.uiRecordTREE.setTableType(tableType)
        self._queryWidget.setTableType(tableType)
        
        if autoRefresh:
            self.setQuery(Q())
    
    def setRecords(self, records):
        """
        Sets the records for this widget to the inputed records.
        
        :param      records | [<orb.Table>, ..] || <orb.RecordSet>
        """
        self.uiRecordTREE.setRecords(records)
    
    def tableType(self):
        """
        Returns the table type associated with this edit.
        
        :return     <subclass of orb.Table>
        """
        return self.uiRecordTREE.tableType()
    
    def treeWidget(self):
        """
        Returns the tree widget that is for editing records for this grid.
        
        :return     <XOrbTreeWidget>
        """
        return self.uiRecordTREE