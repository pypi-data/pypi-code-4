"""Common configuration constants
"""
from Products.DataGridField import Column, SelectColumn
try:
    from Products.DataGridField import LinesColumn
    HAS_LINES_COLUMN = True
except ImportError:
    # BBB as soon as DGF 1.7 is out
    HAS_LINES_COLUMN = False

PROJECTNAME = "PFGDataGrid"

ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Content'

SUPPORTED_COLUMN_TYPES_MAPPING = dict()
SUPPORTED_COLUMN_TYPES_MAPPING['String'] = Column
if HAS_LINES_COLUMN:
    SUPPORTED_COLUMN_TYPES_MAPPING['Select'] = SelectColumn
    SUPPORTED_COLUMN_TYPES_MAPPING['SelectVocabulary'] = SelectColumn
    SUPPORTED_COLUMN_TYPES_MAPPING['DynamicVocabulary'] = SelectColumn
