# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import get_language, ugettext as _
from django.utils.text import slugify

from filebrowser.fields import FileBrowseField
from modeltranslation.settings import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel
from mptt.managers import TreeManager


# Custom Managers
#
class VisibleCategoryManager(models.Manager):
    def get_query_set(self):
        return super(VisibleCategoryManager, self).get_query_set().filter(
            visible_in_menu=True)


class PublishedPageManager(models.Manager):
    def get_query_set(self):
        return super(PublishedPageManager, self).get_query_set().filter(
            status='published')


class HighlightedPageManager(models.Manager):
    def get_query_set(self):
        return super(HighlightedPageManager, self).get_query_set().filter(
            status='published', is_highlighted=True)


# Mixins
#
class SiteMixin(object):
    """
    Add site-framework related features to a model
    """

    def get_current_site(self):
        return Site.objects.get_current()


class TranslatableSlugMixin(object):

    def slugify(self, field, slug_field='slug'):
        """
        Generate slugs given:
        * all available languages
        * a given slugifyable field
        """

        # Generate all languages slugs
        for language_code in AVAILABLE_LANGUAGES:
            src_field = '%s_%s' % (field, language_code)
            aslug_field = '%s_%s' % (slug_field, language_code)

            src_value = getattr(self, src_field, None)

            if not src_value:
                continue

            # Current language slug
            setattr(self, aslug_field, slugify(src_value))

            if not language_code == DEFAULT_LANGUAGE:
                continue

            # Set default language
            setattr(self, slug_field, slugify(src_value))


# Abstract Models
#
class AbstractCategory(TranslatableSlugMixin, MPTTModel):
    """
    Page category model (Hierarchical tree)
    """
    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100,
                            help_text=_("You are not supposed to fill this"),
                            blank=True, unique=True)
    short_description = models.TextField(_("Short description"),
                                         blank=True, null=True)
    description = models.TextField(_("Description"),
                                   help_text=_("Describe this category here"),
                                   blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    position = models.IntegerField(_("Position"),
                                   help_text=_("Used for objects ordering"),
                                   default=0)
    visible_in_menu = models.BooleanField(_("Visible in main menu?"),
                                          default=True)
    # Managers
    objects = TreeManager()
    visible_objects = VisibleCategoryManager()

    class Meta:
        abstract = True
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Generate slugs for all languages before saving
        """
        self.slugify('name')
        super(AbstractCategory, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        language = get_language().split('-')[0]
        return ('category_detail_%s' % language, [self.slug])

    class MPTTMeta:
        order_insertion_by = ['position']

    def get_pages(self):
        # This is an abstract models, hence, various models may
        # be related to the Category model.
        #
        # Return a list, not a queryset
        qss = list()
        for related in self._meta.get_all_related_many_to_many_objects():
            qs = getattr(self, related.var_name).all()
            if not qs and not self.is_leaf_node():
                children = self.get_children()
                qs = related.model.objects.filter(categories__in=children)
            qs = qs.filter(status='published').order_by('-last_modified')
            if len(qs):
                qss += qs
        return qss

    def get_highlighted_pages(self):
        qss = self.get_pages()
        return [p for p in qss if p.is_highlighted]


PAGE_STATUS = (
    ('draft', _("Draft")),
    ('private', _("Private")),
    ('published', _("Published")),
)


class AbstractPage(TranslatableSlugMixin, SiteMixin, models.Model):
    """
    Page model
    """
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200,
                            help_text=_("You are not supposed to fill this"),
                            blank=True, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    synopsis = models.TextField(_("Page synopsis"), blank=True, null=True)
    image = FileBrowseField(_("Page main image"), max_length=250,
                            directory='images/pages/',
                            extensions=['.jpg', '.png', '.gif', '.svg'],
                            blank=True, null=True)
    content = models.TextField(_("Page content"),
                               help_text=_("Describe this category here"),
                               blank=True, null=True)

    categories = TreeManyToManyField('td_cms.Category',
                                     related_name="%(class)s")
    status = models.CharField(_("Status"), choices=PAGE_STATUS,
                              default=PAGE_STATUS[0][0], max_length=50)
    is_highlighted = models.BooleanField(_("Highlighted article?"),
                                         help_text=_("If selected, this "
                                                     "article may be shown on "
                                                     "sidebars or the home "
                                                     "page"),
                                         default=False)
    allow_comments = models.BooleanField(_("Allow comments"), default=False)
    allow_sharing = models.BooleanField(_("Allow social media sharing"),
                                        default=False)
    position = models.IntegerField(_("Position"), default=0)
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Last modified"),
                                         auto_now=True, auto_now_add=True)
    # Managers
    objects = models.Manager()
    published_objects = PublishedPageManager()
    highlighted_objects = HighlightedPageManager()

    class Meta:
        abstract = True
        ordering = ['position', ]
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Generate slugs for all languages before saving
        """
        self.slugify('title')
        super(AbstractPage, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        language = get_language().split('-')[0]
        category = self.categories.all()[0]
        return ('page_detail_%s' % language, [category.slug, self.slug])

    def get_image_full_url(self):
        """
        Return a fully qualified url with domain. If no image has been defined,
        returns None.
        """
        if not self.image:
            return ""

        site = self.get_current_site()
        return "http://%s%s" % (site.domain, self.image.url)
