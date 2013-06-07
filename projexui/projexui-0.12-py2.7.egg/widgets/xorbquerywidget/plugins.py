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

from orb import ColumnType, Query

from projexui.qt.QtGui import QCheckBox,\
                              QDateEdit,\
                              QTimeEdit,\
                              QDateTimeEdit,\
                              QSpinBox,\
                              QDoubleSpinBox

from projexui.widgets.xlineedit       import XLineEdit
from projexui.widgets.xorbrecordbox   import XOrbRecordBox
from projexui.widgets.xorbquerywidget import XOrbQueryPlugin

# B
#----------------------------------------------------------------------

class BoolPlugin(XOrbQueryPlugin):
    def __init__(self):
        super(BoolPlugin, self).__init__()
        
        self.registerEditor('is', Query.Op.Is, QCheckBox)
        self.registerEditor('is not', Query.Op.IsNot, QCheckBox)


# D
#----------------------------------------------------------------------

class DateTimePlugin(XOrbQueryPlugin):
    def __init__(self, cls=None):
        super(DateTimePlugin, self).__init__()
        
        if cls is None:
            cls = QDateTimeEdit
        
        self.registerEditor('is', Query.Op.Is, cls)
        self.registerEditor('is not', Query.Op.IsNot, cls)
        self.registerEditor('after', Query.Op.After, cls)
        self.registerEditor('before', Query.Op.Before, cls)
        #self.registerEditor('Between', Query.Op.Between, cls)
    
    def createEditor(self, parent, column, operator, value):
        """
        Creates a new editor for the given parent and operator.
        
        :param      parent      | <QWidget>
                    operator    | <str>
                    value       | <variant>
        """
        editor = super(DateTimePlugin, self).createEditor(parent,
                                                            column,
                                                            operator,
                                                            value)
        
        if isinstance(editor, QDateTimeEdit) or isinstance(editor, QDateEdit):
            editor.setCalendarPopup(True)
        
        return editor

# F
#----------------------------------------------------------------------

class ForeignKeyPlugin(XOrbQueryPlugin):
    def __init__(self):
        super(ForeignKeyPlugin, self).__init__()
        
        self.registerEditor('is', Query.Op.Is, XOrbRecordBox)
        self.registerEditor('is not', Query.Op.IsNot, XOrbRecordBox)
        self.registerEditor('is none', Query.Op.Is)
        self.registerEditor('is not none', Query.Op.IsNot)
        self.registerEditor('is in', Query.Op.IsIn, XOrbRecordBox)
        self.registerEditor('is not in', Query.Op.IsNotIn, XOrbRecordBox)
    
    def createEditor(self, parent, column, operator, value):
        """
        Creates a new editor for the given parent and operator.
        
        :param      parent      | <QWidget>
                    operator    | <str>
                    value       | <variant>
        """
        editor = super(ForeignKeyPlugin, self).createEditor(parent,
                                                            column,
                                                            operator,
                                                            value)
        
        if editor:
            model = column.referenceModel()
            if model:
                editor.setRecords(model.select())
                if operator in ('Is in', 'Is not in'):
                    editor.setCheckable(True)
        
        return editor
    
    def operator(self, operatorType, value):
        """
        Returns the best match for the given operator type from the list
        of choices.
        
        :param      operatorType | <Query.Op>
                    value        | <variant>
        
        :return     <str>
        """
        if value is None:
            if operatorType == Query.Op.Is:
                return 'is none'
            else:
                return 'is not none'
        
        return super(ForeignKeyPlugin, self).operator(operatorType, value)
    
# N
#----------------------------------------------------------------------

class NumericPlugin(XOrbQueryPlugin):
    def __init__(self, cls):
        super(NumericPlugin, self).__init__()
        
        self.registerEditor('=', Query.Op.Is, cls)
        self.registerEditor('!=', Query.Op.Is, cls)
        self.registerEditor('<', Query.Op.LessThan, cls)
        self.registerEditor('<=', Query.Op.LessThanOrEqual, cls)
        self.registerEditor('>', Query.Op.GreaterThan, cls)
        self.registerEditor('>=', Query.Op.GreaterThanOrEqual, cls)

# P
#----------------------------------------------------------------------

class PasswordPlugin(XOrbQueryPlugin):
    def __init__(self):
        super(PasswordPlugin, self).__init__()
        
        self.registerEditor('is', Query.Op.Is, XLineEdit)
        self.registerEditor('is not', Query.Op.IsNot, XLineEdit)
    
    def createEditor(self, parent, column, operator, value):
        editor = super(PasswordPlugin, self).createEditor(parent,
                                                          column,
                                                          operator,
                                                          value)
        
        if editor:
            editor.setEchoMode(editor.Password)
        
        return editor

# S
#----------------------------------------------------------------------

class StringPlugin(XOrbQueryPlugin):
    def __init__(self, cls=None):
        super(StringPlugin, self).__init__()
        
        if cls is None:
            cls = XLineEdit
        
        self.registerEditor('is', Query.Op.Is, cls)
        self.registerEditor('is not', Query.Op.IsNot, cls)
        self.registerEditor('contains', Query.Op.Contains, cls)
        self.registerEditor('matches', Query.Op.Matches, cls)
        self.registerEditor('startswith', Query.Op.Startswith, cls)
        self.registerEditor('endswith', Query.Op.Endswith, cls)
        self.registerEditor("doesn't contain", Query.Op.DoesNotContain, cls)
        self.registerEditor("doesn't match", Query.Op.DoesNotMatch, cls)

#----------------------------------------------------------------------

def init(factory):
    # simple types
    factory.register(BoolPlugin(),                  ColumnType.Bool)
    factory.register(NumericPlugin(QDoubleSpinBox), ColumnType.Double)
    factory.register(NumericPlugin(QDoubleSpinBox), ColumnType.Decimal)
    factory.register(NumericPlugin(QSpinBox),       ColumnType.Integer)
    # Enum
    
    # string types
    factory.register(StringPlugin(XLineEdit),       ColumnType.String)
    'Text'         # used for larger string data
    factory.register(StringPlugin(XLineEdit),       ColumnType.String)
    factory.register(StringPlugin(XLineEdit),       ColumnType.String)
    factory.register(PasswordPlugin(),              ColumnType.Password)
    factory.register(StringPlugin(XLineEdit),       ColumnType.String)
    factory.register(StringPlugin(XLineEdit),       ColumnType.String)
    'Xml'          # similar to Text,   but auto-escapse data stored
    'Html'         # similar to Text,   but store rich text data & auto-escape
    'Color'        # similar to String, stores the HEX value of a color (#ff00)
    
    # date/time types
    factory.register(DateTimePlugin(QDateEdit),     ColumnType.Date)
    factory.register(DateTimePlugin(QDateTimeEdit), ColumnType.Datetime)
    factory.register(DateTimePlugin(QTimeEdit),     ColumnType.Time)
    'Interval'
    'UTC_Datetime'
    
    # data types
    'Image'        # stores images in the database as binary
    'ByteArray'    # stores additional binary information
    'Dict'         # stores python dictionary types
    
    # relation types
    factory.register(ForeignKeyPlugin(), ColumnType.ForeignKey)
    
    
    