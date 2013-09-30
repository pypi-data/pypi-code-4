from cubicweb.view import EntityView
from cubicweb.predicates import is_instance, one_line_rset, adaptable
from cubicweb.web import formwidgets as wdgs, httpcache
from cubicweb.web.views import baseviews, uicfg, idownloadable

_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('File', 'title'), 'hidden')
_pvs.tag_attribute(('File', 'data_name'), 'hidden')
_pvs.tag_attribute(('File', 'data_sha1hex'), 'hidden')
_pvs.tag_attribute(('File', 'data_thumbnail'), 'hidden')

uicfg.autoform_section.tag_attribute(('File', 'data_thumbnail'), 'main', 'hidden')

_pvdc = uicfg.primaryview_display_ctrl
_pvdc.tag_attribute(('File', 'description'), {'showlabel': False})

# fields required in the schema but automatically set by hooks. Tell about that
# to the ui
_pvdc = uicfg.autoform_field_kwargs
_pvdc.tag_attribute(('File', 'data_name'), {
    'required': False, 'widget': wdgs.TextInput({'size': 128})})
_pvdc.tag_attribute(('File', 'data_format'), {'required': False})


class FileOneLine(baseviews.OneLineView):
    __select__ = is_instance('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileOneLine, self).cell_call(row, col)


class FileInContext(baseviews.InContextView):
    __select__ = is_instance('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileInContext, self).cell_call(row, col)


class FileOutOfContext(baseviews.OutOfContextView):
    __select__ = is_instance('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileOutOfContext, self).cell_call(row, col)


class FileIcon(EntityView):
    __select__ = is_instance('File')
    __regid__ = 'icon'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<a href="%s" title="%s"><img src="%s" alt="%s"/></a>' % (
            entity.absolute_url(), entity.dc_title(), entity.icon_url(),
            self._cw._('file type icon')))


class ThumbnailView(idownloadable.DownloadView):
    """thumbnail download view """
    __regid__ = 'thumbnail'
    __select__ = one_line_rset() & adaptable('IThumbnail')

    content_type = 'image/png'

    def set_request_content_type(self):
        """overriden to set the correct filetype and filename"""
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to('IThumbnail')
        self._cw.set_content_type(self.content_type,
                                  filename=adapter.thumbnail_file_name(),
                                  disposition='attachment')

    def call(self):
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to('IThumbnail')
        self.w(adapter.thumbnail_data())

