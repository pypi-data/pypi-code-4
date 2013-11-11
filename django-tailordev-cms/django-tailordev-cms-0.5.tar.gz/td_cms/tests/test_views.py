# -*- coding: utf-8 -*-
"""
Django TailorDev CMS

Test views
"""
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Page
from .mixins import TDCMSTestMixin


class CategoryDetailViewTests(TDCMSTestMixin, TestCase):
    """
    Tests for the CategoryDetailView
    """
    def setUp(self):
        self._set_category()
        self._add_pages()

    def test_get(self):
        """
        Test the CategoryDetailView get method
        """
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], self.category)

    def test_get_unknown_slug(self):
        """
        Test the CategoryDetailView get method with an unknown object
        """
        kwargs = {
            'slug_en': 'this-is-a-wrong-slug',
        }
        url = reverse('category_detail_en', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class PageDetailViewTests(TDCMSTestMixin, TestCase):
    """
    Tests for the CategoryDetailView
    """
    def setUp(self):
        self._set_category()
        self._add_pages()

    def test_get(self):
        """
        Test the PageDetailView get method
        """
        page = Page.objects.get(id=1)
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], page)

    def test_get_unknown_slug(self):
        """
        Test the PageDetailView get method with an unknown object
        """
        kwargs = {
            'category_slug': self.category.slug,
            'slug_en': 'this-is-a-wrong-slug',
        }
        url = reverse('page_detail_en', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
