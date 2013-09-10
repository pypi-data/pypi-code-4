# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.DataGridField.Column import Column

class TextAreaColumn(Column):
    """ Textarea column """

    security = ClassSecurityInfo()

    def __init__(self, label, col_description=None, default=None, default_method=None,
                       rows=3, cols=0, required=False):

        if required or col_description:
            # sorry for this trick, but we are using this product with a custom DataGridField 1.6.4
            # see https://github.com/RedTurtle/Products.DataGridField/tree/1.6
            Column.__init__(self, label, col_description=col_description, default=default,
                            default_method=default_method, required=required)
        else:
            Column.__init__(self, label, default=default, default_method=default_method)

        self.rows = rows
        self.cols = cols

    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_textarea_cell"


# Initializes class security
InitializeClass(TextAreaColumn)
