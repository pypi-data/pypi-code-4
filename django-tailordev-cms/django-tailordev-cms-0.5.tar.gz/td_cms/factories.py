# -*- coding: utf-8 -*-
import factory
import factory.fuzzy
from loremipsum import get_sentence, get_paragraphs

from . import models


def lorem_paragraphs(p):
    s = '<p>'
    s += '</p><p>\n'.join(get_paragraphs(p))
    s += '</p>'
    return s


class CategoryFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Category
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = factory.Sequence(lambda n: u"Category {0}".format(n))
    short_description = lorem_paragraphs(1)
    description = lorem_paragraphs(2)


class PageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Page
    FACTORY_DJANGO_GET_OR_CREATE = ('title',)

    title = unicode(get_sentence())
    synopsis = lorem_paragraphs(1)
    content = lorem_paragraphs(10)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.categories.add(category)
