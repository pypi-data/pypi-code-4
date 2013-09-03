# -*- coding: utf-8 -*-
import datetime
import json
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models.signals import post_delete
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from dirtyfields import DirtyFieldsMixin
from durationfield.db.models.fields.duration import DurationField
from viddler.settings import (PERMISSIONS, get_viddler, KEY_IMAGE_STORAGE,
                              THUMB_SIZE)
from external_img import download_image

EDITABLE_VIDDLER_FIELDS = ('title', 'description', 'tags', 'permalink',
    'age_limit', 'tags', 'view_permission', 'embed_permission',
    'tagging_permission', 'commenting_permission', 'download_permission')

STORAGE = get_storage_class(KEY_IMAGE_STORAGE)


class BaseViddlerVideo(DirtyFieldsMixin, models.Model):
    viddler_id = models.CharField(_('Viddler ID'),
        max_length=50,
        editable=False,
        help_text="The ID assigned by Viddler. Not editable.")
    last_synced = models.DateTimeField(_('Last Synced'),
        blank=True, null=True,
        editable=False)
    status = models.CharField(_("Status"),
        max_length=50,
        editable=False)
    author = models.CharField(_("Author"),
        max_length=50,
        editable=False)
    title = models.CharField(_("Title"),
        max_length=255)
    slug = models.SlugField(_('Slug'),
        max_length=255)
    length = DurationField(_("Length"),
        editable=False)
    description = models.TextField(_("Description"))
    age_limit = models.IntegerField(_("Age Limit"),
        validators=[MinValueValidator(9), MaxValueValidator(99)],
        help_text='A value between 9 and 99 or empty to reset',
        blank=True, null=True)
    url = models.URLField(_("URL"),
        editable=False,
        help_text="Viddler's video URL")
    embed_code = models.TextField(_("Embed Code"),
        editable=False,
        blank=True, null=True)
    thumbnail_url = models.URLField(_("Thumbnail URL"),
        editable=False,
        help_text="The URL of the thumbnail")
    key_image_custom = models.ImageField(_("Key Image"),
        storage=STORAGE(),
        upload_to='viddler/keyimage',
        blank=True, null=True,
        height_field='key_image_custom_height',
        width_field='key_image_custom_width')
    key_image_custom_width = models.IntegerField(blank=True, null=True)
    key_image_custom_height = models.IntegerField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='viddler/thumbnail',
        blank=True,
        null=True,
        width_field='thumb_width',
        height_field='thumb_height',
        editable=False,
        storage=STORAGE())
    thumb_width = models.IntegerField(blank=True, null=True, editable=False)
    thumb_height = models.IntegerField(blank=True, null=True, editable=False)
    permalink = models.URLField(_("Permalink"),
        help_text="The permanent link URL")
    html5_video_source = models.URLField(_("HTML5 Source URL"),
        editable=False)
    audio_only = models.BooleanField(_("Audio Only"),
        editable=False)
    view_count = models.IntegerField(_("View Count"),
        editable=False)
    impression_count = models.IntegerField(_("Impression Count"),
        editable=False)
    upload_time = models.TimeField(_("Upload Time"),
        editable=False)
    made_public_time = models.TimeField(_("Made Public Time"),
        blank=True, null=True,
        editable=False)
    favorite = models.IntegerField(_("Favorite"),
        editable=False)
    comment_count = models.IntegerField(_("Comment Count"),
        editable=False)
    tags = models.CharField(_("Tags"),
        max_length=255,
        blank=True)
    thumbnails_count = models.IntegerField(_("Thumbnails Count"),
        editable=False)
    thumbnail_index = models.IntegerField(_("Thumbnail Index"),
        editable=False)
    view_permission = models.CharField(_("View Permission"),
        max_length=50,
        choices=PERMISSIONS)
    embed_permission = models.CharField(_("Embed Permission"),
        max_length=50,
        choices=PERMISSIONS)
    tagging_permission = models.CharField(_("Tagging Permission"),
        max_length=50,
        choices=PERMISSIONS)
    commenting_permission = models.CharField(_("Commenting Permission"),
        max_length=50,
        choices=PERMISSIONS)
    download_permission = models.CharField(_("Download Permission"),
        max_length=50,
        choices=PERMISSIONS)
    display_aspect_ratio = models.CharField(_("Aspect Ratio"),
        max_length=10,
        editable=False)
    files = models.TextField(_("Files"),
        editable=False)

    UPDATE_PARAM_MAP = {
        'view_permission': 'view_perm',
        'embed_permission': 'embed_perm',
        'tagging_permission': 'tagging_perm',
        'commenting_permission': 'commenting_perm',
        'download_permission': 'download_perm',
    }

    class Meta:
        verbose_name = _('Viddler Video')
        verbose_name_plural = _('Viddler Videos')
        abstract = True

    def __unicode__(self):
        return "%s: %s" % (self.viddler_id, self.title)

    def _generate_thumbnail(self):
        """
        Be aware that this function handle very badly remote backends such as
        s3. You can add in your save() method something like::

            if 's3boto' in settings.DEFAULT_FILE_STORAGE:
                self.external_url = self.image.file.url
        """
        from django.core.files.base import ContentFile
        from PIL import Image as PilImage
        import os
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        image = PilImage.open(self.key_image_custom.path)
        filename = os.path.basename(self.key_image_custom.name)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image.thumbnail(THUMB_SIZE, PilImage.ANTIALIAS)

        destination = StringIO()
        image.save(destination, format='JPEG')
        destination.seek(0)

        self.thumbnail.save(filename, ContentFile(destination.read()))

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # These are reset after save
        changed_fields = (set(self.dirty_fields) &
                          set(EDITABLE_VIDDLER_FIELDS))
        changed_values = dict([(k, v) for k, v in self.get_changed_values().items() if k in changed_fields])
        if not self.slug:
            self.slug = slugify(self.title)

        upload_key_image = (self.key_image_custom and
                            'key_image_custom' in self.dirty_fields)

        if not self.key_image_custom and self.status != "not ready":
            filename, size, imgfile = download_image(self.thumbnail_url)
            self.key_image_custom.save(filename, imgfile)
            self._generate_thumbnail()
        super(BaseViddlerVideo, self).save(*args, **kwargs)
        if upload_key_image and self.status != "not ready":
            viddler = get_viddler()
            viddler.videos.setThumbnail(
                self.viddler_id,
                thumbfile=self.key_image_custom.path)
            self._generate_thumbnail()
        if changed_fields and not force_update:
            set_params = {}
            for key, val in changed_values.items():
                set_params[self.UPDATE_PARAM_MAP.get(key, key)] = val
            viddler = get_viddler()
            result = viddler.videos.setDetails(self.viddler_id, **set_params)
            make_model_from_api(result, self.__class__)

    def get_files(self):
        """
        Return the files as a list of dictionaries
        """
        files = getattr(self, "_files", False)
        if not files:
            self._files = json.loads(self.files)
            files = self._files
        return files

    def get_PROFILE_file(self, profilename):
        """
        Return the source file url
        """
        for f in self.get_files():
            if f['profile_name'] == profilename and f['status'] == 'ready':
                return f
        return ''

    def get_TYPE_files(self, filetype):
        """
        return list of dictionaries of files available for filetype
        """
        output = []
        for f in self.get_files():
            if f[filetype] == u'on' and f['status'] == 'ready':
                output.append(f)
        return output

    def get_source_file(self):
        return self.get_PROFILE_file(u'Source')

    def get_webm_file(self):
        return self.get_PROFILE_file(u'WebM')

    def get_3gp_file(self):
        return self.get_PROFILE_file(u'3gp')

    def get_360p_file(self):
        return self.get_PROFILE_file(u'360p')

    def get_480p_file(self):
        return self.get_PROFILE_file(u'480p')

    def get_720p_file(self):
        return self.get_PROFILE_file(u'720p')

    def get_1080p_file(self):
        return self.get_PROFILE_file(u'1080p')

    def get_flash_files(self):
        """
        get files available for flash
        """
        return self.get_TYPE_files(u"flash")

    def get_ipad_files(self):
        """
        get files available for ipad
        """
        return self.get_TYPE_files(u"ipad")

    def get_iphone_files(self):
        """
        get files available for ipad
        """
        return self.get_TYPE_files(u"iphone")

    def get_itunes_files(self):
        """
        get files available for ipad
        """
        return self.get_TYPE_files(u"itunes")

    def _embed_code(self, **kwargs):
        viddler = get_viddler()
        kwargs['video_id'] = self.viddler_id
        embed_code = viddler.videos.getEmbedCode(**kwargs)
        return embed_code

    def get_embed_code(self, force_update=False, **kwargs):
        """
        width - number - optional
        height - number - optional
        player_type - string - optional (full, simple or mini, defaults to full)
        wmode - string - optional (transparent, opaque, window, defaults to transparent)
        autoplay - boolean - optional
        branding - boolean - optional (show video owner’s branding, defaults to true)
        offset - number - optional (playback offset in seconds)
        embed_code_type - number - optional (embed code type number, listed at viddler.videos.getEmbedCodeTypes)
        flashvar - string - optional (can specify any flashvar as the key and it’s value as value. IE: displayUser=jeff
        """
        if force_update or not self.embed_code:
            self.embed_code = self._embed_code(**kwargs)
            self.save()
        return self.embed_code


class ViddlerVideo(BaseViddlerVideo):
    pass


def make_model_from_api(api_record, videoclass=ViddlerVideo):
    data_dict = dict(
        viddler_id=api_record['id'],
        status=api_record['status'],
        author=api_record['author'],
        title=api_record['title'],
        slug=slugify(api_record['title']),
        length=api_record['length'] and int(api_record['length']) * 1000000 or 0,
        description=api_record['description'],
        age_limit=api_record['age_limit'] and int(api_record['age_limit']) or None,
        url=api_record['url'],
        thumbnail_url=api_record['thumbnail_url'],
        permalink=api_record['permalink'],
        html5_video_source=api_record['html5_video_source'],
        audio_only=api_record.get('audio_only', False),
        view_count=api_record['view_count'] and int(api_record['view_count']) or 0,
        impression_count=api_record['impression_count'] and int(api_record['impression_count']) or 0,
        upload_time=datetime.datetime.utcfromtimestamp(int(api_record['upload_time'])),
        favorite=api_record['favorite'],
        comment_count=api_record['comment_count'],
        thumbnails_count=api_record['thumbnails_count'],
        thumbnail_index=api_record['thumbnail_index'],
        view_permission=api_record['permissions']['view']['level'],
        embed_permission=api_record['permissions']['embed']['level'],
        tagging_permission=api_record['permissions']['tagging']['level'],
        commenting_permission=api_record['permissions']['commenting']['level'],
        download_permission=api_record['permissions']['download']['level'],
        display_aspect_ratio=api_record['display_aspect_ratio'],
        files=json.dumps(api_record['files'])
    )
    if 'slug' in api_record:
        data_dict['slug'] = api_record['slug']
    made_public = api_record['made_public_time'] and int(api_record['made_public_time'])
    if made_public:
        data_dict['made_public_time'] = datetime.datetime.utcfromtimestamp(made_public)
    tags = []
    for tag in api_record.get('tags', []):
        tags.append(tag['text'])
    data_dict['tags'] = ",".join(tags)
    data_dict['last_synced'] = datetime.datetime.now()

    try:
        video = videoclass.objects.get(viddler_id=api_record['id'])
        for key, val in data_dict.items():
            setattr(video, key, val)
        video.save(force_update=True)
    except videoclass.DoesNotExist:
        video = videoclass(**data_dict)
        video.save()
    video.get_embed_code()  # To force it to cache it and save it in the database
    return video


def delete_handler(sender, instance, *args, **kwargs):
    viddler = get_viddler()
    try:
        viddler.videos.delete(instance.viddler_id)
    except viddler.ViddlerAPIException:
        pass

post_delete.connect(delete_handler, sender=ViddlerVideo)
