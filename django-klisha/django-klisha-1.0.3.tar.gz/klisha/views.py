# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from datetime import datetime
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from pure_pagination.mixins import PaginationMixin
from .models import Picture, Category, Tag
from .settings import KLISHA_PAGINATE_BY, KLISHA_RELATED_PICTURE_NUMBER


class PictureDetailView(DetailView):
    """
    Display picture detail, increase view counter and return random pictures
    """
    template_name = "klisha/picture_detail.html"

    def get_queryset(self):
        return Picture.published_objects.all()

    def get_context_data(self, **kwargs):
        self.object.views_counter += 1
        self.object.save()
        context = super(PictureDetailView, self).get_context_data(**kwargs)
        context['object_list'] = Picture.published_objects.order_by('?')[:KLISHA_RELATED_PICTURE_NUMBER]
        return context

picture_detail = PictureDetailView.as_view()


class PictureListView(PaginationMixin, ListView):
    template_name = "klisha/picture_list.html"
    paginate_by = KLISHA_PAGINATE_BY

    def get_queryset(self):
        query = Q()

        if 'year' in self.kwargs:
            query &= Q(published_at__year=self.kwargs['year'])
        if 'month' in self.kwargs:
            query &= Q(published_at__month=self.kwargs['month'])

        return Picture.published_objects.filter(query)

picture_list = PictureListView.as_view()


class TagDetailView(DetailView):
    template_name = "klisha/tag_detail.html"

    def get_queryset(self):
        return Tag.objects.all()

tag_detail = TagDetailView.as_view()


class TagListView(PaginationMixin, ListView):
    template_name = "klisha/tag_list.html"
    queryset = Tag.objects.all()

tag_list = TagListView.as_view()


class CategoryDetailView(DetailView):
    template_name = "klisha/category_detail.html"

    def get_queryset(self):
        return Category.objects.all()

category_detail = CategoryDetailView.as_view()


class CategoryListView(PaginationMixin, ListView):
    template_name = "klisha/category_list.html"
    queryset = Category.objects.all()

category_list = CategoryListView.as_view()


class ArchiveView(TemplateView):
    """
    Display list of archive
    """
    template_name = "klisha/archive_list.html"

    def get_context_data(self, **kwargs):
        context = super(ArchiveView, self).get_context_data(**kwargs)

        pictures = Picture.published_objects.all().order_by("published_at")
        dates = Picture.published_objects.dates("published_at", "month")

        archives = {}

        for date in dates:
            year = date.year
            try:
                archives[year].append(date)
            except KeyError:
                archives[year] = [date]

        context['archive'] = archives
        return context

archive_list = ArchiveView.as_view()


class PopularListView(PaginationMixin, ListView):
    """
    Display list of the most popular picture all the time
    """
    template_name = "klisha/popular_list.html"
    paginate_by = KLISHA_PAGINATE_BY

    def get_queryset(self):
        return Picture.published_objects.all().order_by("-views_counter")

popular_list = PopularListView.as_view()
