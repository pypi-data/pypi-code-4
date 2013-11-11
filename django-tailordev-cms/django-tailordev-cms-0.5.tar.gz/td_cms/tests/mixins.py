# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.utils.translation import activate

from ..factories import CategoryFactory, PageFactory
from ..models import Page

TEST_CATEGORIES = (
    (u'Django books', (u'Testing in Django', u'Jazz with Django')),
    (u'Django tee', (u'Keep calm', u'Poney ride')),
    (u'Django stickers', (u'Poney mascotte', u'Django logo')),
)


class TDCMSTestMixin(object):
    """
    A mixin for category model and views testing.
    """
    def _set_user(self):
        """
        Create a default author for pages
        """
        User = get_user_model()
        self.user = User.objects.create(
            username="johndoe",
            first_name="John",
            last_name="Doe",
        )

    def _set_category(self):
        """
        Create a category and make it an attribute
        """
        # Force the default language
        activate('en')
        self.category = CategoryFactory.create(name=u"Category 1")

    def _set_page(self, categories=None):
        """
        Create a page and make it an attribute. This page is linked to the
        categories list argument.
        """
        # Force the default language
        activate('en')
        self.page = PageFactory.create(title=u"Title 1", categories=categories)

    def _add_pages(self, category=None):
        """
        Add pages to the default category
        """
        if category is None:
            category = self.category

        if not hasattr(self, 'user'):
            self._set_user()

        # Counter start
        n = Page.objects.count()

        # Create pages for the default category
        for num in xrange(n + 1, n + 7):
            title = u"Django book (vol. %(num)d)" % {'num': num}
            status = 'draft'
            highlighted = False
            if not num % 2:
                status = 'published'
            if not num % 8:
                highlighted = True

            PageFactory(title=title,
                        categories=(category,),
                        status=status,
                        is_highlighted=highlighted,
                        author=self.user)

    def _set_category_tree(self):
        """
        Set a typical category tree
        """
        for parent_category, subcategories in TEST_CATEGORIES:
            parent = CategoryFactory.create(name=parent_category)

            for subcategory in subcategories:
                sc = CategoryFactory.create(name=subcategory, parent=parent)
                self._add_pages(category=sc)
