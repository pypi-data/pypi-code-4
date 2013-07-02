from simplejson import dumps, loads

from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

from raptus.article.core.interfaces import IArticle
from raptus.article.table.interfaces import ITable, ITables, IRows, IDefinitions, IDefinition, IType, IStyles
from raptus.article.table.utils import parseColumn

class Tables(object):
    """ Provider for tables contained in an article
    """
    interface.implements(ITables)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getTables(self, **kwargs):
        """ Returns a list of tables (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Table', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                  'depth': 1}, sort_on='getObjPositionInParent', **kwargs)

class Rows(object):
    """ Provider for rows contained in a table
    """
    interface.implements(IRows)
    component.adapts(ITable)
    
    def __init__(self, context):
        self.context = context
        
    def getRows(self, **kwargs):
        """ Returns a list of rows (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Row', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                'depth': 1}, sort_on='getObjPositionInParent', **kwargs)
        
class Definitions(object):
    """Handles table definitions
    """
    interface.implements(IDefinitions)
    component.adapts(interface.Interface)
    
    def __init__(self, context):
        self.context = context
        props = getToolByName(self.context, 'portal_properties')
        if not 'raptus_article_table' in props:
            props.addPropertySheet('raptus_article_table')
        self.properties = props.raptus_article_table
        
    def getDefinition(self, name):
        """ Returns the definition
        """
        name = normalizeString(name, self.context)
        definition =  loads(self.properties.getProperty(name, dumps({'columns': [],
                                                                     'style': ''})))
        return definition
    
    def getAvailableDefinitions(self):
        """ Returns a dict of definitions available for this article
        """
        definitions = {}
        for name in self.properties.propertyIds():
            try:
                definitions[name] = loads(self.properties.getProperty(name))
            except: # filter out malformed definitions
                pass
        return definitions
    
    def addDefinition(self, name, style, columns, id=None):
        """ Adds a new global definition
        """
        for column in columns:
            column['name'] = normalizeString(column['name'], self.context)
        value = dumps({'columns': columns,
                       'style': style,
                       'name': name})
        if id is None:
            id = normalizeString(name, self.context)
        if self.properties.hasProperty(id):
            self.properties._updateProperty(id, value)
        else:
            self.properties._setProperty(id, value)
    
    def removeDefinition(self, id):
        """ Removes a global definition
        """
        if self.properties.hasProperty(id):
            self.properties._delProperty(id)
    
    def parseColumns(self, columns):
        ignore = 1
        cols = []
        for column in columns:
            try:
                # BBB
                if not isinstance(column, dict):
                    column = parseColumn(column)
                column['ignore'] = ignore > 1
                ignore = max(1, ignore-1)
                if column.get('colspan', 0):
                    ignore = int(column['colspan'])
                utility = component.getUtility(IType, column['type'])
                column['utility'] = utility
                cols.append(column)
            except:
                pass
        return cols
    
class Definition(object):
    """ Definition provider for tables
    """
    interface.implements(IDefinition)
    component.adapts(ITable)
    
    def __init__(self, context):
        self.context = context
        
    def getCurrentDefinition(self):
        """ Returns the definition for this article
        """
        definition = {}
        definitions = IDefinitions(self.context)
        if self.context.getDefinition():
            definition = definitions.getDefinition(self.context.getDefinition())
        columns = self.context.getColumns()
        if columns:
            definition['columns'] = columns
        definition['columns'] = definitions.parseColumns(definition.get('columns', ()))
        style = self.context.getStyle()
        if style:
            definition['style'] = style
        return definition

class Styles(object):
    """ Style provider for tables
    """
    interface.implements(IStyles)
    component.adapts(interface.Interface)
    
    def __init__(self, context):
        self.context = context
    
    def styles(self):
        properties = getToolByName(self.context, 'portal_properties').raptus_article
        return [dict(zip(('value', 'title'), style.split(':'))) for style in properties.getProperty('table_styles', (':None', 'listing:Listing', 'plain:Plain',))]
