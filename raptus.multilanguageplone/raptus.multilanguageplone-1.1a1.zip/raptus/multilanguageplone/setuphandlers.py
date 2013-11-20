from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguageplone.extender import folder, document, event, file, image, link, newsitem, topic

from Products.CMFCore.utils import getToolByName

extenders = [folder.FolderExtender,
             document.DocumentExtender,
             event.EventExtender,
             file.FileExtender,
             image.ImageExtender,
             link.LinkExtender,
             newsitem.NewsItemExtender,
             topic.TopicExtender,]

try:
    from raptus.multilanguageplone.extender.file import BlobFileExtender, BlobFileModifier
    extenders.append(BlobFileExtender)
    extenders.append(BlobFileModifier)
    from raptus.multilanguageplone.extender.image import BlobImageExtender, BlobImageModifier
    extenders.append(BlobImageExtender)
    extenders.append(BlobImageModifier)
except ImportError:
    pass

class _extra:
    pass
text_extra = _extra()
text_extra.lexicon_id = 'plone_lexicon'
text_extra.index_type = 'Okapi BM25 Rank'
indexes = (('SearchableText', 'MultilanguageZCTextIndex', 'SearchableText', 'ZCTextIndex', 'SearchableText'),
           ('Subject', 'MultilanguageKeywordIndex', 'Subject', 'KeywordIndex', 'Subject'),
           ('Title', 'MultilanguageZCTextIndex', 'Title', 'ZCTextIndex', 'Title'),
           ('Description', 'MultilanguageZCTextIndex', 'Description', 'ZCTextIndex', 'Description'),
           ('sortable_title', 'MultilanguageFieldIndex', 'multilanguage_sortable_title', 'FieldIndex', 'sortable_title'))

def install(context):
    if context.readDataFile('raptus.multilanguageplone_install.txt') is None:
        return
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    for extender in extenders:
        sm.unregisterAdapter(extender, name='Multilanguage%s' % extender.__name__)
        sm.registerAdapter(extender, name='Multilanguage%s' % extender.__name__)
    
    catalog = getToolByName(portal, 'portal_catalog')
    for id, new, new_field_name, orig, orig_field_name in indexes:
        if id in catalog.indexes():
            index = catalog._catalog.getIndex(id)
            if not index.__class__.__name__ == new:
                catalog.delIndex(id)
        if not id in catalog.indexes():
            extra = _extra()
            if new == 'MultilanguageZCTextIndex':
                extra = text_extra
            setattr(extra, 'field_name', new_field_name)
            catalog.addIndex(id, new, extra)
            catalog.reindexIndex(id, portal.REQUEST)

def uninstall(context):
    if context.readDataFile('raptus.multilanguageplone_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    for extender in extenders:
        try:
            sm.unregisterAdapter(extender, name='Multilanguage%s' % extender.__name__)
        except:
            pass
