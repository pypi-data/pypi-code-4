"""File related hooks

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import ValidationError
from cubicweb.server import hook
from cubicweb.sobjects.notification import ContentAddedView
from cubicweb.predicates import is_instance

from cubes.file.entities import UnResizeable

class UpdateFileHook(hook.Hook):
    """a file has been updated, check data_format/data_encoding consistency
    """
    __regid__ = 'updatefilehook'
    __select__ = hook.Hook.__select__ & is_instance('File')
    events = ('before_add_entity', 'before_update_entity',)
    order = -1 # should be run before other hooks

    def __call__(self):
        edited = self.entity.cw_edited
        if 'data' in edited:
            self.entity.set_format_and_encoding()
            maxsize = self._cw.vreg.config['image-max-size']
            if maxsize and self.entity.data_format.startswith('image/'):
                iimage = self.entity.cw_adapt_to('IImage')
                try:
                    edited['data'] = iimage.resize(maxsize)
                except UnResizeable:
                    # if the resize fails for some reason, do nothing
                    # (original image will be stored)
                    pass

            if self._cw.vreg.config['compute-sha1hex']:
                data = edited['data']
                if data is not None:
                    data = self.entity.compute_sha1hex(data.getvalue())
                edited['data_sha1hex'] = data

            # thumbnail cache invalidation
            if 'update' in self.event and 'data' in edited:
                thumb = self.entity.cw_adapt_to('IThumbnail')
                if not thumb:
                    return
                thumbpath = thumb.thumbnail_path()
                if thumbpath:
                    try:
                        os.unlink(thumbpath)
                    except Exception, exc:
                        self.warning('could not invalidate thumbnail file `%s` (cause: %s)',
                                     thumbpath, exc)


class FileAddedView(ContentAddedView):
    """get notified from new files"""
    __select__ = is_instance('File')
    content_attr = 'description'
