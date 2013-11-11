# -*- coding: utf-8 -*-
"""
Django TailorDev CMS

Test template tags
"""
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured
from django.template import Template, Context
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate

from ..models import Category, Page
from .mixins import TDCMSTestMixin


class TDCMSTemplateTagTests(TDCMSTestMixin, TestCase):
    """
    Tests for the td_cms_tags template tags library
    """
    def setUp(self):
        activate('en')
        self._set_category_tree()

    def test_get_parent_categories(self):
        """
        Retrieve visible categories to display in a (mptt) rendered menu
        """
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_parent_categories as categories %}"
            "{% for category in categories %}"
            "{% if category.is_child_node %}"
            "> {{ category }} "
            "{% else %}"
            "{{ category }} "
            "{% endif %}"
            "{% endfor %}"
        )

        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = "".join(
            "Django books > Testing in Django > Jazz with Django "
            "Django tee > Keep calm > Poney ride "
            "Django stickers > Poney mascotte > Django logo "
        )
        self.assertEqual(out, expected)

        # Test with a hidden category in menu
        Category.objects.filter(name='Keep calm').update(visible_in_menu=False)
        out = Template(template).render(Context())
        expected = "".join(
            "Django books > Testing in Django > Jazz with Django "
            "Django tee > Poney ride "
            "Django stickers > Poney mascotte > Django logo "
        )
        self.assertEqual(out, expected)

    def test_get_highlighted_pages(self):
        """
        Get a queryset of all highlighted pages in templates
        """
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_highlighted_pages as pages %}"
            "{% for page in pages %}"
            "{{ page }} - "
            "{% endfor %}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = "".join(
            "Django book (vol. 8) - "
            "Django book (vol. 16) - "
            "Django book (vol. 24) - "
            "Django book (vol. 32) - "
        )
        self.assertEqual(out, expected)

    def test_get_category(self):
        """
        Get a category object by its slug in a template. We test two different
        languages (fr, en).
        """
        # Add translations for our category of interest
        category = Category.objects.get(name='Jazz with Django')
        category.name_fr = u'Jaser avec Django'
        category.save()

        # Test the english (default) slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_category 'jazz-with-django' as category %}"
            "{{ category }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = category.name
        self.assertEqual(out, expected)

        # Switch to french
        activate('fr')

        # Test the french slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_category 'jaser-avec-django' as category %}"
            "{{ category }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = category.name_fr
        self.assertEqual(out, expected)

    def test_get_category_with_unknown_slug(self):
        """
        Try to get a category with a wrong slug
        """
        # Test the english (default) slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_category 'swing-with-django' as category %}"
            "{{ category }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = u"None"
        self.assertEqual(out, expected)

    def test_get_page(self):
        """
        Get a page object by its slug in a template. We test two different
        languages (fr, en).
        """
        # Add translations for our category of interest
        page = Page.objects.get(title='Django book (vol. 10)')
        page.title_fr = u'Le livre Django (vol. 10)'
        page.save()

        # Test the english (default) slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_page 'django-book-vol-10' as page %}"
            "{{ page }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = page.title
        self.assertEqual(out, expected)

        # Switch to french
        activate('fr')

        # Test the french slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_page 'le-livre-django-vol-10' as page %}"
            "{{ page }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = page.title_fr
        self.assertEqual(out, expected)

    def test_get_page_with_unknown_slug(self):
        """
        Try to get a page with a wrong slug
        """
        # Test the english (default) slug
        template = "".join(
            "{% load td_cms_tags %}"
            "{% get_page 'php-book-vol-1' as page %}"
            "{{ page }}"
        )
        # Test with all categories visible in menu
        out = Template(template).render(Context())
        expected = u"None"
        self.assertEqual(out, expected)

    def test_timestamp_filter(self):
        """
        Get a timestamp from a datetime.datetime object
        """
        date = datetime(year=1980, month=10, day=14, hour=18, minute=30)
        template = "".join(
            "{% load td_cms_tags %}"
            "{{ date|timestamp }}"
        )
        # Test the datetime to timestamp conversion
        out = Template(template).render(Context({'date': date}))
        expected = u"340392600"
        self.assertEqual(out, expected)

    def test_timestamp_filter_without_datetime_instance(self):
        """
        Try to get a timestamp from a non datetime.datetime object, should be
        returned identical.
        """
        date = u"14/10/1980"
        template = "".join(
            "{% load td_cms_tags %}"
            "{{ date|timestamp }}"
        )
        # Test the datetime to timestamp conversion
        out = Template(template).render(Context({'date': date}))
        expected = date
        self.assertEqual(out, expected)

    def test_show_disqus_thread_while_not_configured(self):
        """
        Test the disqus thread inclusion while not configured
        """
        page = Page.objects.get(title='Django book (vol. 10)')
        template = "".join(
            "{% load td_cms_tags %}"
            "{% show_disqus_thread page %}"
        )
        # Raises an error while not configured
        with self.assertRaises(ImproperlyConfigured):
            Template(template).render(Context({'page': page}))

    @override_settings(TD_CMS_DISQUS_SHORTNAME='tailordev')
    def test_aaa_show_disqus_thread(self):
        """
        Test the disqus thread inclusion while not configured
        """
        page = Page.objects.get(title='Django book (vol. 10)')
        template = "".join(
            "{% load td_cms_tags %}"
            "{% show_disqus_thread page %}"
        )
        out = Template(template).render(Context({'page': page}))
        expected = "var disqus_shortname = 'tailordev';"
        self.assertIn(expected, out)
        expected = "var disqus_identifier = '%d-%s';" % (page.id, page.slug)
        self.assertIn(expected, out)
        expected = "var disqus_title = '%s';" % page.title
        self.assertIn(expected, out)
