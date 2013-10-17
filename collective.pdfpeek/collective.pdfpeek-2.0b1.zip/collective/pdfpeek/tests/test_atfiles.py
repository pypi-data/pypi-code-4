# -*- coding: utf-8 -*-
from Products.ATContentTypes.interface.file import IATFile

from collective.pdfpeek import testing
from collective.pdfpeek.interfaces import IPDFDataExtractor
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import logout
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase


class TestATDataExtraction(TestCase):
    """Unit tests for the transformation and metadata extraction of PDF files
       stored in ATFile objects.
    """

    layer = testing.PDFPEEK_AT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        # Create files
        for uri in self.layer['pdf_files']:
            content_id = uri.split('/').pop()
            new_id = self.portal.invokeFactory('File', content_id)

            atfile = self.portal[new_id]
            atfile.setFile(open(uri, 'r').read())

            self.assertTrue(IATFile.providedBy(atfile))

        self._validate_created_files()
        logout()

    def _validate_created_files(self):
        # Validate created files
        obj_ids = self.portal.objectIds()
        self.assertIn('distutils.pdf', obj_ids)
        self.assertIn('plone.pdf', obj_ids)
        self.assertIn('top-15-questions-about-plone.pdf', obj_ids)

    def test_plone_pdf(self):
        converter = IPDFDataExtractor(self.portal['plone.pdf'])

        self.assertEqual(converter.pages, 1)
        self.assertEqual(converter.metadata, {
            '/Title': u'Plone CMS: Open Source Content Management',
            '/CreationDate': u"D:20090416164855-07'00'",
            '/Producer': u'Acrobat Distiller 9.0.0 (Macintosh)',
            '/Creator': u'firefox-bin: cgpdftops CUPS filter',
            '/ModDate': u"D:20090416164855-07'00'",
            '/Author': u'David Brenneman',
            'height': 792.0,
            'width': 612.0,
            'pages': 1,
        })

        images = converter.get_thumbnails(0, 1)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 1 * 2)  # 2 images each
        self.assertIn('1_preview', images.keys())
        self.assertIn('1_thumb', images.keys())

    def test_top_15_questions_about_plone_pdf(self):
        converter = IPDFDataExtractor(
            self.portal['top-15-questions-about-plone.pdf'])

        self.assertEqual(converter.pages, 2)
        self.assertEqual(converter.metadata, {
            '/Creator': u'Adobe InDesign CS3 (5.0.4)',
            '/Producer': u'Mac OS X 10.5.6 Quartz PDFContext',
            '/CreationDate': u"D:20090420170431Z00'00'",
            '/ModDate': u"D:20090420170431Z00'00'",
            'height': 612.0,
            'width': 792.0,
            'pages': 2,
        })

        # Export first page only
        images = converter.get_thumbnails(0, 1)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 1 * 2)  # 2 images each
        self.assertIn('1_preview', images.keys())
        self.assertIn('1_thumb', images.keys())

        # Export second page only
        images = converter.get_thumbnails(1, 1)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 1 * 2)  # 2 images each
        self.assertIn('2_preview', images.keys())
        self.assertIn('2_thumb', images.keys())

        # Export all pages
        images = converter.get_thumbnails(0, converter.pages)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 2 * 2)  # 2 images each
        self.assertIn('1_preview', images.keys())
        self.assertIn('1_thumb', images.keys())
        self.assertIn('2_preview', images.keys())
        self.assertIn('2_thumb', images.keys())

    def test_distutils_pdf(self):
        converter = IPDFDataExtractor(self.portal['distutils.pdf'])

        self.assertEqual(converter.pages, 98)
        self.assertEqual(converter.metadata, {
            'height': 792.0,
            'width': 612.0,
            'pages': 98,
        })

        images = converter.get_thumbnails(0, converter.pages)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 98 * 2)  # 2 images each

    def test_limit_pages_through_registry(self):
        converter = IPDFDataExtractor(self.portal['distutils.pdf'])
        converter.settings.page_limit = 1

        self.assertEqual(converter.pages, 1)
        self.assertEqual(converter.metadata, {
            'height': 792.0,
            'width': 612.0,
            'pages': 98,
        })

        images = converter.get_thumbnails(0, converter.pages)
        self.assertIsNotNone(images)
        self.assertEqual(type(images), dict)
        self.assertEqual(len(images.keys()), 1 * 2)  # 2 images each


