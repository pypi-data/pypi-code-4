""":mod:`crosspop.image.watermark` --- Watermarked images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It additionally appends the watermark caption to the image.
Its :class:`Image`, :class:`ImageSet`, and :func:`image_attachment()`
are mostly compatible to :class:`crosspop.image.entity.Image`,
:class:`crosspop.image.entity.ImageSet`, and
:func:`crosspop.image.entity.image_attachment()`.

You can give optional caption values like ``'url'`` for the watermark e.g.::

    fiction.watermarked_cover.from_file(
        file_,
        values={
            'url': 'https://crosspop.in/fictions/1234',
            'title': u'Comic Title',
            'number': 123
        }
    )

Also :class:`Image` has two more metadata about the watermark:

- :attr:`Image.watermark_height`
- :attr:`Image.watermark_values`

"""
import cgi
import collections
import io
import pickle
import re

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import text, tuple_
from sqlalchemy.types import Integer, PickleType
from pkg_resources import resource_filename
from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image as WandImage

from ..docstring import append_docstring_attributes
from .context import current_store
from .entity import (Image as BaseImage,
                     ImageSet as BaseImageSet,
                     image_attachment as base_image_attachment)

__all__ = ('BORDER_COLOR', 'Image', 'ImageSet', 'draw_watermark',
           'image_attachment')


#: (:class:`wand.color.Color`) The watermark border color.
BORDER_COLOR = Color('#5fc4e1')

#: (:class:`wand.color.Color`) The watermark caption text color.
CAPTION_COLOR = Color('rgb(51,51,51)')


def draw_watermark(image, values):
    """Appends the watermark caption with ``values`` to the ``image``.

    Caption values can constain the following keys:

    ``'url'``
        Permalink to the related entity web page.
        The leading scheme e.g. ``'https://'`` will be omitted.
        If it has trailing slash it also weill be omitted.

    ``'title'``
        Title of the related entity.

    ``'number'``
        Sequential number of the realted entity e.g. chapter number.
        Sharp character also will be prepanded to the number.

    :param image: the original image
    :type image: :class:`wand.image.Image`
    :param values: mapping of caption strings to write
                   e.g. ``{'url': 'http://...', 'title': '...'}``
    :type values: :class:`collections.Mapping`
    :returns: the watermarked image
    :rtype: :class:`wand.image.Image`

    """
    if not isinstance(image, WandImage):
        raise TypeError('image must be an instance of wand.image.Image, not '
                        + repr(image))
    elif not isinstance(values, collections.Mapping):
        raise TypeError('values must be mapping, not ' + repr(values))
    supersample = 2
    border = 2
    margin = 35
    caption_top = border + 10
    caption_left = 10
    caption_right = 10
    title_number_margin = 5
    url_title_margin = 10
    with WandImage(width=supersample * image.width,
                   height=supersample * (border + margin),
                   background=Color('white')) as watermark:
        with WandImage(width=supersample * image.width,
                       height=supersample * border,
                       background=BORDER_COLOR) as border_image:
            watermark.composite(border_image, left=0, top=0)
        regular_font = Font(
            path=resource_filename('crosspop', 'fonts/NanumGothic.ttf'),
            size=supersample * 11,
            color=CAPTION_COLOR
        )
        bold_font = Font(
            path=resource_filename('crosspop', 'fonts/NanumGothicBold.ttf'),
            size=supersample * 11,
            color=CAPTION_COLOR
        )
        extrabold_font = Font(
            path=resource_filename('crosspop',
                                   'fonts/NanumGothicExtraBold.ttf'),
            size=supersample * 14,
            color=BORDER_COLOR
        )
        draw_logo = True
        logo_left = supersample * (image.width - 70)
        url = (values.get('url') or '').strip()
        title = unicode(values.get('title') or u'').strip()
        number = str(values.get('number') or '').strip()
        with Drawing() as draw:
            caption_top *= supersample
            caption_left *= supersample
            caption_right *= supersample
            draw.text_antialias = True
            draw.text_encoding = 'utf-8'
            draw.font = regular_font.path
            draw.font_size = regular_font.size
            if url:
                paths = re.sub(r'^[^:/]+://|/+$', '', url).split('/', 2)
                if len(paths) > 1:
                    paths[0] += '/'
                if caption_left < watermark.width:
                    draw.font = regular_font.path
                    watermark.caption(paths[0],
                                      left=caption_left, top=caption_top,
                                      font=regular_font)
                    caption_left += int(
                        draw.get_font_metrics(watermark, paths[0]).text_width
                    )
                if len(paths) > 1 and caption_left < watermark.width:
                    draw.font = bold_font.path
                    watermark.caption(paths[1], font=bold_font,
                                      left=caption_left, top=caption_top)
                    caption_left += int(
                        draw.get_font_metrics(watermark, paths[1]).text_width
                    )
                if len(paths) > 2 and caption_left < watermark.width:
                    paths[2] = '/' + paths[2]
                    draw.font = regular_font.path
                    watermark.caption(paths[2], font=regular_font,
                                      left=caption_left, top=caption_top)
                    caption_left += int(
                        draw.get_font_metrics(watermark, paths[2]).text_width
                    )
            if title:
                draw.font = bold_font.path
                title_width = draw.get_font_metrics(
                    watermark,
                    title.encode(draw.text_encoding)
                ).text_width
            else:
                title_width = 0
            if number:
                draw.font = regular_font.path
                number = '#' + number
                number_width = draw.get_font_metrics(watermark,
                                                     number).text_width
            else:
                number_width = 0
            if title or number:
                text_width = title_width + (
                    title_width and number_width and
                    number_width + supersample * title_number_margin
                )
                remain_width = logo_left - caption_left
                if remain_width > text_width + (url_title_margin if url else 0):
                    if url:
                        caption_left += int((remain_width - text_width) / 2)
                else:
                    remain_width = (watermark.width - caption_left -
                                    caption_right)
                    draw_logo = False
                    if remain_width > text_width:
                        caption_left = int(watermark.width - text_width -
                                           caption_right)
                    else:
                        caption_left += url_title_margin * supersample
            if title and caption_left < watermark.width:
                watermark.caption(title.encode('utf-8'), font=bold_font,
                                  left=caption_left, top=caption_top)
                caption_left += int(title_width +
                                    supersample * title_number_margin)
            if number and caption_left < watermark.width:
                watermark.caption(number, font=regular_font,
                                  left=caption_left, top=caption_top)
        if draw_logo and logo_left < watermark.width:
            watermark.caption('Crosspop', font=extrabold_font,
                              left=logo_left, top=supersample * (border + 7))
        watermark.resize(width=image.width, height=border + margin)
        result = WandImage(width=image.width,
                           height=image.height + watermark.height,
                           background=Color('white'))
        result.composite(watermark, left=0, top=image.height)
        result.composite(image, left=0, top=0)
    if image.format in ('PNG', 'GIF'):
        result.format = image.format
    else:
        result.format = 'JPEG'
        result.compression_quality = 99
    return result


def image_attachment(*args, **kwargs):
    """Almost the same to :func:`crosspop.image.entity.image_attachment()`
    except it's for :mod:`crosspop.image.watermark` instead of
    :mod:`crosspop.image.entity`.

    :param \*args: the same arguments as
                   :func:`crosspop.image.entity.image_attachment()`
    :param \*\*kwargs: the same keyword arguments as
                       :func:`crosspop.image.entity.image_attachment()`
    :returns: the relationship property
    :rtype: :class:`sqlalchemy.orm.properties.RelationshipProperty`

    """
    return base_image_attachment(*args, query_class=ImageSet, **kwargs)


class Image(BaseImage):
    """Almost the same to :func:`crosspop.image.entity.Image` class
    except it's for :mod:`crosspop.image.watermark` instead of
    :mod:`crosspop.image.entity`.

    The :attr:`height` column represents still its logical image height
    without watermark area.  For the height of the full image which
    contains watermark area, use :attr:`physical_height` or
    :attr:`physical_size`.

    """

    __abstract__ = True

    @hybrid_property
    def watermark_width(self):
        """(:class:`numbers.Integral`) The width of the watermark caption.
        It's actually fixed and equivalent to :attr:`physical_width`
        but for pairing to :attr:`watermark_height` property.

        """
        return self.width

    @declared_attr
    def watermark_height(cls):
        """(:class:`numbers.Integral`) The height of the watermark caption."""
        return Column(Integer, nullable=False,
                      default=0, server_default=text('0'))

    @declared_attr
    def watermark_values(cls):
        """(:class:`collections.Mapping`) The mapping of additional caption
        values.

        """
        return Column(PickleType, nullable=False,
                      default={}, server_default=pickle.dumps({}))

    @hybrid_property
    def physical_width(self):
        """(:class:`numbers.Integral`) The width of the full image
        which contains watermark area.  It's actually equivalent to
        :attr:`~crosspop.image.entity.Image.width` but for pairing
        to :attr:`physical_height` property.

        """
        return self.width

    @hybrid_property
    def physical_height(self):
        """(:class:`numbers.Integral`) The height of the full image
        which contains watermark area.

        """
        return self.height + self.watermark_height

    @hybrid_property
    def physical_size(self):
        """(:class:`tuple`) The size pair of the full image which
        contains watermark area.

        """
        return self.width, self.physical_height

    @physical_size.expression
    def physical_size(cls):
        return tuple_(cls.width, cls.physical_height)

    def __html__(self):
        return '<img src="{0}" width="{1}" height="{2}">'.format(
            cgi.escape(self.locate()),
            self.width,
            self.height + self.watermark_height
        )

    __doc__ = append_docstring_attributes(
        __doc__,
        dict((k, v) for k, v in locals().iteritems()
                    if isinstance(v, declared_attr))
    )


class ImageSet(BaseImageSet):
    """Almost the same to :func:`crosspop.image.entity.ImageSet`
    except it's for :mod:`crosspop.image.watermark` instead of
    :mod:`crosspop.image.entity`.

    Its :meth:`from_blob()` and :meth:`from_file()` methods additionally
    takes ``values`` parameter (which is optional and empty dictionary by
    default).

    """

    def from_blob(self, blob, values={}, store=current_store):
        return self.from_file(io.BytesIO(blob), values=values, store=store)

    def from_file(self, file, values={}, store=current_store):
        data = io.BytesIO()
        with WandImage(file=file) as wand:
            size = wand.size
            with draw_watermark(wand, values) as watermarked:
                mimetype = watermarked.mimetype
                watermarked.save(file=data)
                height = watermarked.height
        data.seek(0)
        image = self.from_raw_file(
            data,
            store=store,
            size=size,
            mimetype=mimetype,
            original=True
        )
        image.watermark_height = height - size[1]
        image.watermark_values = values
        return image

    def generate_thumbnail(self, ratio=None, width=None, height=None,
                           filter='undefined', store=current_store,
                           _preprocess_image=None, _postprocess_image=None):
        original = self.require_original()
        watermark_height = [0]
        def preprocess_image(img):
            img = img[:, :original.height]
            if _preprocess_image is None:
                return img
            with img:
                return _preprocess_image(img)
        def postprocess_image(img):
            processed = draw_watermark(img, original.watermark_values)
            watermark_height[0] = processed.height - img.height
            if _postprocess_image is None:
                return processed
            with processed:
                return _postprocess_image(processed)
        image = super(ImageSet, self).generate_thumbnail(
            ratio=ratio, width=width, height=height,
            filter=filter, store=store,
            _preprocess_image=preprocess_image,
            _postprocess_image=postprocess_image
        )
        image.watermark_height, = watermark_height
        image.watermark_values = original.watermark_values
        return image

    def __html__(self):
        if not self:
            return ''
        original = self.require_original()
        return '<img src="{0}" width="{1}" height="{2}">'.format(
            cgi.escape(self.locate()),
            original.width,
            original.height + original.watermark_height
        )
