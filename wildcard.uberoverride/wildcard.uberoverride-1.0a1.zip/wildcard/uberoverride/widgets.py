from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_base
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget, \
     UberMultiSelectionWidget
from OFS.interfaces import IItem
from Products.CMFCore.utils import getToolByName
try:
    import json
except ImportError:
    import simplejson as json


def _is_item(context):
    try:
        return IItem.providedBy(context)
    except:
        return False


class TreeWidgetMixin(object):

    def __init__(self, field, request):
        self.site = getSite()
        self.site_path = '/'.join(self.site.getPhysicalPath())

        pprops = getToolByName(self.site, 'portal_properties')
        site_props = pprops.site_properties
        self.folder_types = site_props.getProperty(
            'typesLinkToFolderContentsInFC', ['Folder', 'Large Plone Folder'])

        limit = 4
        count = 0
        realcontext = self.context
        while not _is_item(realcontext) and realcontext and count < limit:
            realcontext = getattr(realcontext, 'context', None)
            count += 1
        self.realcontext = realcontext
        self.current_path = '/'.join(
            self.realcontext.getPhysicalPath())[len(self.site_path) + 1:]

        base_query = self.source.base_query.copy()
        query = base_query.copy()
        if 'portal_type' in query:
            if type(query['portal_type']) in (list, tuple, set):
                query['portal_type'] = list(query['portal_type'])
                query['portal_type'].extend(list(self.folder_types))
            else:
                pt = query['portal_type']
                query['portal_type'] = list(self.folder_types)
                query['portal_type'].append(pt)

        self.base_query = base_query
        self.query = query
        self.jqid = '%s-tree-container' % self.name.replace('.', '-')

        self.includejs = request.environ.get('should-include-tree', True)
        request.environ['should-include-tree'] = False

    def get_folder_html(self, folder):
        results = folder.getFolderContents(contentFilter=self.base_query)
        html = '<ul class="jqueryFileTree">'
        for item in folder.getFolderContents(contentFilter=self.query):
            path = item.getPath()[len(self.site_path) + 1:]
            klass = ''
            if aq_base(item) not in results:
                klass = 'unselectable'
            if item.portal_type in self.folder_types:
                html += '<li class="directory collapsed %s">' % klass + \
                        '<a class="item" href="#" rel="%s">%s</a>' % (
                    path + '/',
                    item.Title
                )
                if path in self.current_path:
                    html += self.get_folder_html(item.getObject())
                html += '</li>'
            else:
                html += '<li class="file ext_txt %s">' % klass + \
                        '<a class="item" href="#" rel="%s">%s</a></li>' % (
                    path,
                    item.Title
                )
        html += "</ul>"
        return html

    def initial_data(self):
        return self.get_folder_html(self.site)


class MultiChoiceTreeWidget(UberMultiSelectionWidget, TreeWidgetMixin):
    template = ViewPageTemplateFile('tree-multi-widget.pt')

    def __init__(self, field, request):
        super(MultiChoiceTreeWidget, self).__init__(field, request)
        TreeWidgetMixin.__init__(self, field, request)

    def _value(self):
        if self._renderedValueSet():
            value = self._data
        else:
            tokens = self.request.form.get(self.name)

            if tokens is not None:
                value = []
                for token in tokens:
                    try:
                        v = self.terms.getValue(str(token))
                    except LookupError:
                        pass  # skip invalid values
                    else:
                        value.append(v)
            else:
                if self.name + '.displayed' in self.request:
                    value = []
                else:
                    value = self.context.missing_value
        if value is None:
            value = []
        return value

    def javascript(self):
        return """
$(document).ready(function(){
        $("#%(jqid)s").fileTree({
            base_query : %(query)s
        }, function(link) {
          link = $(link);
          if(link.parent().hasClass('unselectable')){
            return false;
          }
          var file = link.attr('rel');
          if(file.charAt(file.length) == '/'){
            file = file.substring(0, file.length-1);
          }
          var fieldset = $('#%(jqid)s').siblings('fieldset');
          fieldset.append(
                '<div class="sortable-tree-item">' +
                '<input type="checkbox" checked="checked" ' +
                        'name="%(name)s:list" value="/' + file + '" />' +
                '<span>' + link.html() + '</span>' +
                ' <a href="#" class="up">&#x2191;</a> ' +
                ' <a href="#" class="down">&#x2193;</a> '
          );
          return false;
        });
})
        """ % {'name': self.name, 'query': json.dumps(self.base_query),
               'jqid': self.jqid}


class ChoiceTreeWidget(UberSelectionWidget, TreeWidgetMixin):
    template = ViewPageTemplateFile('tree-select-widget.pt')

    def __init__(self, field, request):
        super(ChoiceTreeWidget, self).__init__(field, request)
        TreeWidgetMixin.__init__(self, field, request)

    def javascript(self):
        return """
$(document).ready(function(){
        $("#%(jqid)s").fileTree({
            base_query : %(query)s
        }, function(link) {
          link = $(link);
          if(link.parent().hasClass('unselectable')){
            return false;
          }
          var file = link.attr('rel');
          if(file.charAt(file.length-1) == '/'){
            file = file.substring(0, file.length-1);
          }
          var fieldset = $('#%(jqid)s').siblings('fieldset');
          if(fieldset.find('input[value="/' + file + '"]').size() == 0){
            fieldset.find("div").remove();
            fieldset.append(
                '<div><input type="checkbox" checked="checked" ' +
                    'name="%(name)s" value="/' + file + '" />' +
                '<span>' + link.html() + '</span>'
            );
          }
          return false;
        });
});
        """ % {'name': self.name, 'query': json.dumps(self.base_query),
               'jqid': self.jqid}
