# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import logging
from loremipsum import get_sentence

from td_cms.factories import CategoryFactory, PageFactory


LOREM_CATEGORIES = (
    # ('Main Category', ('Related', 'Sub categories'))
    (u'Company', (u'Research & Development', u'Marketing')),
    (u'Activity', (u'Genomics', u'Bioinformatics')),
    (u'News', (u'Scientific News', u'Business News')),
)


class Command(BaseCommand):
    args = ''
    help = 'Generates lorem ipsum fixtures for designers'

    def page(self, logger):
        """
        Page app fixtures
        """

        # Parent categories
        for category in LOREM_CATEGORIES:
            parent_category = CategoryFactory.create(name=category[0])
            logger.info('New parent categories: %s', parent_category)

            # Child categories
            for child_category_name in category[1]:
                child_category = CategoryFactory.create(
                    name=child_category_name,
                    parent=parent_category)
                logger.info('New child categories: %s', child_category)

                for p in range(3):
                    PageFactory(title=unicode(get_sentence()),
                                categories=(child_category,),
                                status='published')
                logger.info('Created %s pages', child_category)

    def handle(self, *args, **options):
        logger = self._get_logger()

        # App fixtures
        self.page(logger)

    def _get_logger(self):
        logger = logging.getLogger('td_cms')
        return logger
