from Acquisition import aq_inner
from OFS.ObjectManager import checkValidId

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.table.interfaces import IRows, IDefinition
from raptus.article.table.config import ADD_PERMISSION

try:
    # Plone 4 and higher
    import plone.app.upgrade
    GIF = False
except ImportError:
    GIF = True

class Table(BrowserView):
    """Renders the table of a table content type
    """
    template = ViewPageTemplateFile('table.pt')
    gif = GIF
    
    def __call__(self):
        context = aq_inner(self.context)
        if self.request.form.get('%s.row.add' % context.UID(), None) is not None and \
           self.can_add:
            position = self.request.form.get('%s.row.position' % context.UID(), None)
            typestool = getToolByName(context, 'portal_types')
            added, failed = 0, 0
            for row in self.request.form.get('%s.rows' % context.UID(), []):
                try:
                    title = row.get('title', 'row')
                    id = self._create_id(title, context)
                    typestool.constructContent(type_name='Row', container=context, id=id)
                    object = context[id]
                    object.update(**dict(row))
                    if position is not None:
                        context.moveObjectToPosition(id, int(position)+added)
                    object.reindexObject()
                    added += 1
                except:
                    failed += 1
            if position is not None and added > 0:
                getToolByName(context, 'plone_utils').reindexOnReorder(context)
            statusmessage = IStatusMessage(self.request)
            if added == 1:
                statusmessage.addStatusMessage(_(u'Successfully added new row'), 'info')
            if added > 1:
                statusmessage.addStatusMessage(_(u'Successfully added ${number} rows', mapping=dict(number=added)), 'info')
            if failed == 1:
                statusmessage.addStatusMessage(_(u'Adding one new row failed'), 'error')
            if failed > 1:
                statusmessage.addStatusMessage(_(u'Adding ${number} rows failed', mapping=dict(number=failed)), 'error')
            self.request.form['%s.row.add' % context.UID()] = None
        return self.template()
    
    def _create_id(self, id, container):
        id = normalizeString(id, container)
        if not id:
            id = 'row'
        if self._check_id(id, container):
            return id
        new_id = id + '-%s'
        i = 1
        while not self._check_id(new_id % i, container):
            i += 1
        return new_id % i
    
    def _check_id(self, id, container):
        if container.check_id(id, 1, container) is not None:
            return False
        try:
            checkValidId(container, id)
            return True
        except:
            pass
        return False
    
    def _class(self, i, l):
        cls = []
        if i == 0:
            cls.append('first')
        if i == l-1:
            cls.append('last')
        if i % 2 == 0:
            cls.append('odd')
        if i % 2 == 1:
            cls.append('even')
        return ' '.join(cls)
    
    @property
    @memoize
    def can_add(self):
        context = aq_inner(self.context)
        mship = getToolByName(context, 'portal_membership')
        return not self.request.get('raptus_article_viewing', 0) and mship.checkPermission(ADD_PERMISSION['Row'], context)
    
    @property
    @memoize
    def definition(self):
        context = aq_inner(self.context)
        return IDefinition(context).getCurrentDefinition()
        
    @property
    @memoize
    def rows(self):
        if not self.definition['columns']:
            return
        context = aq_inner(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(IRows(context).getRows())
        i = 0
        l = len(items)
        self.manageable = self.can_add
        for item in items:
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'class': self._class(i, l)})
            if item['up'] or item['down'] or item['edit'] or item['delete']:
                self.manageable = True
            for col in self.definition['columns']:
                item[col['name']] = col['utility'].modifier(item['obj'].Schema()[col['name']].get(item['obj']), item['obj'], col)
            i += 1
        return items
