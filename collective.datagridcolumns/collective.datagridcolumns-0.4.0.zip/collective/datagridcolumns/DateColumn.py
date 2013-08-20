# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.DataGridField.Column import Column


class DateColumn(Column):
    """ Defines column with calendar DataGridField """

    def __init__(self, label, default=None, default_method=None, label_msgid=None, date_format="yy/mm/dd"):
        Column.__init__(self, label, default, default_method, label_msgid)
        self.date_format = date_format

    security = ClassSecurityInfo()

    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_date_cell"

# Initializes class security
InitializeClass(DateColumn)
