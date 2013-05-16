import json
from Acquisition import aq_inner, aq_parent, aq_base
from Products.Five import BrowserView
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName


def _decode_dict(dct):
    newdict = {}
    for k, v in dct.iteritems():
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        newdict[k] = v
    return newdict


class TreeValues(BrowserView):

    def get_navigation(self):
        directory = self.request.get('dir', './')
        base_query = json.loads(self.request.get('query', '{}'),
                           object_hook=_decode_dict)
        pprops = getToolByName(self.context, 'portal_properties')
        site_props = pprops.site_properties
        folder_types = site_props.getProperty(
            'typesLinkToFolderContentsInFC', ['Folder', 'Large Plone Folder'])
        query = base_query.copy()
        if 'portal_type' in query:
            if type(query['portal_type']) in (list, tuple, set):
                query['portal_type'] = list(query['portal_type'])
                query['portal_type'].extend(list(folder_types))
            else:
                pt = query['portal_type']
                query['portal_type'] = list(folder_types)
                query['portal_type'].append(pt)

        site = getSite()
        context = aq_inner(self.context)
        if directory == './':
            if IFolderish.providedBy(context):
                context = aq_parent(context)
        elif directory == '/':
            context = site
        else:
            context = site.restrictedTraverse(directory)

        results = context.getFolderContents(contentFilter=base_query)
        html = '<ul class="jqueryFileTree" style="display: none;">'
        site_path = '/'.join(site.getPhysicalPath())
        for item in context.getFolderContents(contentFilter=query):
            path = item.getPath()[len(site_path) + 1:]
            klass = ''
            if aq_base(item) not in results:
                klass = 'unselectable'
            if item.portal_type in folder_types:
                html += """<li class="directory collapsed %s">
    <a class="item" href="#" rel="%s">%s</a></li>""" % (
                    klass,
                    path + '/',
                    item.Title
                )
            else:
                html += """<li class="file ext_txt %s">
    <a class="item" href="#" rel="%s">%s</a></li>""" % (
                    klass,
                    path,
                    item.Title
                )
        html += '</ul>'
        return html
