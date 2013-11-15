# -*- coding: utf-8 -*-
"""
Django TailorDev CMS

Test models.
"""
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify
from django.utils.translation import activate

from ..factories import PageFactory
from ..models import Category, Page
from .mixins import TDCMSTestMixin


class CategoryModelTests(TDCMSTestMixin, TestCase):
    """
    Tests for the Category model
    """
    def setUp(self):
        self._set_category()

    def test_unicode(self):
        """
        Test __unicode__ method
        """
        self.assertEqual(unicode(self.category), self.category.name)

    def test_saving_and_retrieving_items(self):
        """
        Test saving and retrieving two categories with different names
        """
        name_1 = self.category.name

        name_2 = u"Category 2"
        category_2 = Category()
        category_2.name = name_2
        category_2.save()

        categories = Category.objects.all()
        self.assertEqual(categories.count(), 2)

        saved_category_1 = categories[0]
        saved_category_2 = categories[1]
        self.assertEqual(saved_category_1.name, name_1)
        self.assertEqual(saved_category_2.name, name_2)

    def test_slug_unicity(self):
        """
        Test saving two categories with the same name
        """
        category_2 = Category()
        category_2.name = self.category.name
        self.assertRaisesMessage(
            IntegrityError,
            'column slug_en is not unique',
            category_2.save
        )

    def test_multilingual_slug(self):
        """
        Test multilingual slugification
        """
        name_en = u"Django books"
        name_fr = u"Livres de Django"

        category = Category()
        category.name_en = name_en
        category.name_fr = name_fr

        category.slugify('name')
        self.assertEqual(category.slug_en, slugify(name_en))
        self.assertEqual(category.slug_fr, slugify(name_fr))

    def test_get_absolute_url(self):
        """
        Test the get_absolute_url method (with multilingual support)
        """
        url = reverse('category_detail_en', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), url)

        # Set a new language
        activate('fr')
        url = reverse('category_detail_fr', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), url)

    def test_category_mptt_order(self):
        """
        Test Category tree ordering
        """
        self.category.position = 1
        self.category.save()

        name_1 = self.category.name

        name_2 = u"Must be the first"
        category_2 = Category()
        category_2.name = name_2
        category_2.position = 0
        category_2.save()

        categories = Category.objects.all()

        first_position_category = categories[0]
        second_position_category = categories[1]
        self.assertEqual(first_position_category.name, name_2)
        self.assertEqual(second_position_category.name, name_1)

    def test_get_pages(self):
        """
        Test the get_pages method
        """
        self._add_pages()

        pages = self.category.get_pages()
        self.assertEqual(len(pages), 3)

    def test_get_pages_with_subcategories(self):
        """
        Test the get_pages method when the main category has no linked pages
        but one of its sub-categories has linked pages.
        """
        # Create two sub-categories with 6 pages (3 highlighted pages)
        for num in range(1, 3):
            subcategory = Category.objects.create(
                name=u"Category 1.%(num)d" % {'num': num},
                parent=self.category
            )
            self._add_pages(subcategory)

        pages = self.category.get_pages()
        self.assertEqual(len(pages), 6)

    def test_get_highlighted_pages(self):
        """
        Test the get_highlighted_pages method
        """
        self._add_pages()
        page = self.category.page.all()[0]
        page.is_highlighted = True
        page.status = 'published'
        page.save()

        pages = self.category.get_highlighted_pages()
        self.assertEqual(len(pages), 1)

    def test_visible_category_manager(self):
        """
        Test the visible category manager
        """
        self._set_category_tree()
        categories = Category.objects.all()
        visible_categories = Category.visible_objects.all()

        # By default a category is visible
        self.assertEqual(categories.count(), visible_categories.count())

        # Toggle all categories visibility status
        Category.objects.all().update(visible_in_menu=False)
        visible_categories = Category.visible_objects.all()
        self.assertEqual(visible_categories.count(), 0)


class PageModelTests(TDCMSTestMixin, TestCase):
    """
    Tests for the Category model
    """
    def setUp(self):
        self._set_category()
        self._set_page(categories=[self.category])

    def test_unicode(self):
        """
        Test __unicode__ method
        """
        self.assertEqual(unicode(self.page), self.page.title)

    def test_page_factory(self):
        """
        Test the PageFactory with no linked categories
        """
        page = PageFactory.build(title=u"This is a title")
        self.assertIsNot(page, None)

    def test_saving_and_retrieving_items(self):
        """
        Test saving and retrieving two categories with different names
        """
        title_1 = self.page.title

        title_2 = u"Title 2"
        page_2 = Page()
        page_2.title = title_2
        page_2.save()

        pages = Page.objects.all()
        self.assertEqual(pages.count(), 2)

        saved_page_1 = pages[0]
        saved_page_2 = pages[1]
        self.assertEqual(saved_page_1.title, title_1)
        self.assertEqual(saved_page_2.title, title_2)

    def test_get_absolute_url(self):
        """
        Test the get_absolute_url method (with multilingual support)
        """
        page_slug = self.page.slug
        category_slug = self.page.categories.all()[0].slug

        url = reverse('page_detail_en', args=[category_slug, page_slug])
        self.assertEqual(self.page.get_absolute_url(), url)

        # Set a new language
        activate('fr')
        url = reverse('page_detail_fr', args=[category_slug, page_slug])
        self.assertEqual(self.page.get_absolute_url(), url)

    def test_get_current_site(self):
        """
        Test the get_current_site method from the SiteMixin
        """
        site = self.page.get_current_site()
        self.assertEqual(site.domain, 'example.com')
        self.assertEqual(site.name, 'example.com')

    def test_get_image_full_url(self):
        """
        Test the get_image_full_url method
        """
        # No image has been defined
        image_full_url = self.page.get_image_full_url()
        self.assertEqual(image_full_url, '')

        # Define an image
        image_relative_url = '/media/upload/foo/test.jpg'
        self.page.image = image_relative_url
        self.page.save()
        image_full_url = self.page.get_image_full_url()

        site = self.page.get_current_site()
        url = "http://%(domain)s%(image)s" % {
            'domain': site.domain,
            'image': image_relative_url,
        }
        self.assertEqual(url, image_full_url)

    def test_published_page_manager(self):
        """
        Test the published page manager
        """
        self._set_category_tree()
        published_pages = Page.published_objects.all()

        self.assertEqual(published_pages.count(), 18)

    def test_highlighted_page_manager(self):
        """
        Test the highlighted page manager
        """
        self._set_category_tree()
        highlighted_pages = Page.highlighted_objects.all()

        self.assertEqual(highlighted_pages.count(), 4)
