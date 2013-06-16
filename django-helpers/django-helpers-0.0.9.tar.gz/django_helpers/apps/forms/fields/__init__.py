# coding=utf-8
from django.db.models.fields.files import ImageFieldFile
from lib.thumbnail import ImageWithThumbsFieldFile, ImageWithThumbsField

try:
    from django_helpers.storages.flickr import FlickrStorage
except:
    FlickrStorage = None

__author__ = 'ajumell'

__all__ = ['ThumbnailImageFieldFile', 'ThumbnailImageField']


class ThumbnailImageFieldFile(ImageWithThumbsFieldFile):
    def _get_thumbnail(self):
        storage = self.storage
        if hasattr(storage, 'thumbnail'):
            return self.storage.thumbnail(self.name)
        sizes = self.field.sizes
        w, h = sizes[0]
        return getattr(self, 'url_%sx%s' % (w, h))

    thumbnail = property(_get_thumbnail)

    def save(self, name, content, save=True):
        storage = self.storage
        # In Flickr storage there is no need for making thumbnails
        # manually. It will be done automatically.
        if FlickrStorage is not None and isinstance(storage, FlickrStorage):
            ImageFieldFile.save(self, name, content, save)
        else:
            ImageWithThumbsFieldFile.save(self, name, content, save)


class ThumbnailImageField(ImageWithThumbsField):
    attr_class = ThumbnailImageFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, sizes=None, **kwargs):
        if sizes is None:
            sizes = ((150, 150), )
        ImageWithThumbsField.__init__(self, verbose_name, name, width_field, height_field, sizes, **kwargs)
