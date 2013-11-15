# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import get_language, ugettext as _
from django.views.generic import DetailView

from .models import Category, Page


class TranslatedSlugMixin(object):
    """
    Returns the object the view is displaying, given a translated slug.
    """

    def get_object(self, queryset=None):
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Current language translated slug name
        language = get_language().split('-')[0].lower()
        slug_field = 'slug_%s' % language

        # The translated slug value matching our url pattern
        slug = self.kwargs.get(slug_field, None)

        # Our object
        queryset = queryset.filter(**{slug_field: slug})

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class CategoryDetailView(TranslatedSlugMixin, DetailView):
    model = Category
    template_name = 'td_cms/category_detail.html'


class PageDetailView(TranslatedSlugMixin, DetailView):
    model = Page
    template_name = 'td_cms/page_detail.html'
