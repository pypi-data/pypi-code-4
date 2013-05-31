import re
import hashlib
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from . import app_settings

class Tag(models.Model):

    created = models.DateTimeField(default=now)
    text = models.CharField(max_length=50, unique=True, db_index=True)

    def __unicode__(self):
        return self.text


class Post(models.Model):

    class Meta:
        ordering = ['-id',]

    _post_types = {}
    post_type_name = models.CharField(max_length=35, editable=False)

    created = models.DateTimeField(default=now)
    modified = models.DateTimeField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    title = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True, null=True)

    published = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        self.post_type_name = self.__class__.__name__
        return super(Post, self).save(*args, **kwargs)

    @classmethod
    def register_type(cls):
        if Post._post_types.has_key(cls.__name__):
            raise RuntimeError(
                'A post type named {0} already exists. Choose a unique id for ' \
                'your post type.'.format(cls.__name__))
        Post._post_types[cls.__name__] = cls

    @property
    def post_type(self):
        return self._post_types[self.post_type_name]

    @property
    def downcast(self):
        return self.post_type.objects.get(post_ptr_id=self.id)

    def publish(self):
        Post.objects.filter(pk__lte=self.pk).update(published=True)

    @property
    def template(self):
        def uncamel(class_name):
            return re.sub('(.)([A-Z]{1})', r'\1_\2', class_name).lower()
        return 'rsbp/{0}.html'.format(uncamel(self.__class__.__name__))

    def feed_title(self):
        return self.__unicode__()

    def feed_description(self):
        return ''

    def get_absolute_url(self):
        if self.slug:
            args = (self.id, self.slug)
        else:
            args = (self.id,)
        return reverse('post', args=args)

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return 'Post {0} by {1} on {2}'.format(self.id, self.created_by,
                self.created.strftime('%Y-%m-%d %H:%M:%S'))


class ImagePost(Post):

    image = models.ImageField(upload_to=app_settings.RSBP_IMAGE_UPLOAD_DIR)
    digest = models.CharField(max_length=40, blank=True, null=True, db_index=True)

    def feed_title(self):
        if self.title:
            return self.title
        else:
            return 'Image'

    def feed_description(self):
        return '<img src="{0}">'.format(self.image.url)

    def _calc_digest(self):
        s = hashlib.sha1()
        f = self.image.file
        for chunk in iter(lambda: f.read(128*s.block_size), b''):
            s.update(chunk)
        return s.hexdigest()

    def save(self, *args, **kwargs):
        self.digest = self._calc_digest()
        return super(ImagePost, self).save(*args, **kwargs)


class TextPost(Post):

    text = models.TextField()

    def feed_description(self):
        return self.text

Post.register_type()
ImagePost.register_type()
TextPost.register_type()
