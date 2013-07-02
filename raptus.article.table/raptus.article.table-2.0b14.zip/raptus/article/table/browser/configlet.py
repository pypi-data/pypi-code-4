import transaction
from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _p

from Products.statusmessages.interfaces import IStatusMessage

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.table.interfaces import IDefinitions, IStyles, ITable
from raptus.article.table.utils import parseColumn

class Configlet(BrowserView):
    """ Manage table definitions
    """
    template = ViewPageTemplateFile('configlet.pt')

    def __call__(self):
        self.request.set('disable_border', True)

        self.styles = IStyles(self.context).styles()
        self._definitions = IDefinitions(self.context)

        if self.request.form.has_key('raptus_article_table_save'):
            self.setProperties()

        self.definitions = []
        raw_definitions = self._definitions.getAvailableDefinitions()
        for name, definition in raw_definitions.iteritems():
            if not len(definition['columns']) or self.request.form.has_key('definition_columns_%s_add_column' % definition['name']):
                definition['columns'].append({})
            definition['blocked'] = self.checkBlocked(name)
            definition['id'] = name
            self.definitions.append(definition)
        
        self.new_definition = {
            'name': self.request.form.get('new_definition_name', ''),
            'columns': self.request.form.get('new_definition_columns', []),
            'style': self.request.form.get('new_definition_style', '')
        }
        
        if not len(self.new_definition['columns']) or self.request.form.has_key('new_definition_columns_add_column'):
            self.new_definition['columns'].append({})
        
        return self.template()
    
    def _formatColumns(self, columns):
        formatted = []
        for column in columns:
            if not column['name'].strip() or column.get('delete', 0):
                continue
            column = column.copy()
            formatted.append(column)
        return formatted

    def setProperties(self):
        context = aq_inner(self.context)
        new = self.request.form.get('new_definition', None)
        columns = self.request.form.get('new_definition_columns', [])
        error = 0
        if new and new['name']:
            try:
                self._definitions.addDefinition(new['name'], new['style'], self._formatColumns(columns))
            except:
                transaction.abort()
                error = _(u'Unable to parse the columns field of the definition to be added')
        modify = self.request.form.get('definitions', [])[:]
        for definition in modify:
            if definition.has_key('delete'):
                self._definitions.removeDefinition(definition['id'])
            if definition.has_key('delete'):
                continue
            try:
                columns = self.request.form.get('definition_columns_%s' % definition['origname'], [])
                self._definitions.addDefinition(definition['name'], definition['style'], self._formatColumns(columns), definition['id'])
            except:
                transaction.abort()
                error = _(u'Unable to parse the columns field of one of the definitions to be modified')
        statusmessage = IStatusMessage(self.request)
        if error:
            statusmessage.addStatusMessage(error, 'error')
        else:
            statusmessage.addStatusMessage(_p(u'Changes saved.'), 'info')


    def checkBlocked(self, definition):
        """ check if a table has already this definition
            and we ban the user to make some modifications.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return len(catalog.unrestrictedSearchResults(object_provides=ITable.__identifier__, getDefinition=definition)) > 0



