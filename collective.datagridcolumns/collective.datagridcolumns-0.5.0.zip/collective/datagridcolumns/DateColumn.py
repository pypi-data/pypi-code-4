# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.DataGridField.Column import Column


class DateColumn(Column):
    """ Defines column with calendar DataGridField """

    def __init__(self, label, col_description=None, default=None, default_method=None,
                 date_format="yy/mm/dd", required=False):
        if required or col_description:
            # sorry for this trick, but we are using this product with a custom DataGridField 1.6.4
            # see https://github.com/RedTurtle/Products.DataGridField/tree/1.6
            Column.__init__(self, label, col_description=col_description, default=default,
                            default_method=default_method, required=required)
        else:
            Column.__init__(self, label, default=default, default_method=default_method)
        self.date_format = date_format

    security = ClassSecurityInfo()

    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_date_cell"

# Initializes class security
InitializeClass(DateColumn)
