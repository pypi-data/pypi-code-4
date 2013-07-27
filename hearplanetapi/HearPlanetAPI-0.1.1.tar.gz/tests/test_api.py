#!/usr/bin/python
import sys
import re
import unittest
import logging as log
from hearplanet.api import HearPlanet, APIException

class HPTestCase(unittest.TestCase):
    def setUp(self):
        self.api = HearPlanet()

class Format(HPTestCase):
    """ Loop over valid section format values
    """
    def test_formats(self):
        valid_values = ('HTML', 'HTML-RAW', 'XHTML', 'PLAIN', 'AS-IS',)
        for v in valid_values:
            req = self.api.table('article').fetch(999999).format(v)
            obj = req.objects()[0]
            self.assertEqual(obj.title, 'Puducherry', 'incorrect article format')
            if v == 'HTML':
                self.assertTrue(re.match(
                    '<img', obj.sections[0].section_text), 'bad format')
            elif v == 'HTML-RAW':
                self.assertTrue(re.match(
                    '<p>', obj.sections[0].section_text), 'bad format')
            elif v == 'XHTML':
                self.assertTrue(re.match(
                    '<!DOCTYPE html', obj.sections[0].section_text),
                    'bad format')
            elif v == 'PLAIN':
                self.assertTrue(re.match(
                    'Puducherry', obj.sections[0].section_text), 'bad format')
            elif v == 'AS-IS': # WikiMarkup
                self.assertTrue(re.match(
                    "'''Puducherry'''", obj.sections[0].section_text),
                    'bad format')

class Depth(HPTestCase):
    """ Loop over valid depth values, and make sure what should be there
        is there, and what shouldn't be there is not there.
    """
    def test_depths(self):
        valid_values = ('min', 'poi', 'article', 'section',
            'section_text', 'all',)
        for v in valid_values:
            req = self.api.table('poi').fetch(999999).depth(v)
            obj = req.objects()[0]
            self.assertEqual(obj.title, 'Puducherry', 'incorrect poi')
            if v == 'min':
                self.assertTrue(obj.has_articles_with_audio, 'bad depth')
                try: assert obj.articles
                except AttributeError: pass
            elif v == 'poi':
                self.assertTrue(obj.articles, 'bad depth')
                self.assertTrue(len(obj.articles), 'bad depth')
                try: assert obj.articles[0].section_count
                except AttributeError: pass
            elif v == 'article':
                self.assertTrue(obj.articles[0].section_count, 'bad depth')
                try: assert obj.articles[0].sections
                except AttributeError: pass
            elif v == 'section':
                self.assertTrue(obj.articles[0].sections, 'bad depth')
                self.assertTrue(obj.articles[0].sections[0].section_title, 'bad depth')
                try: assert obj.articles[0].sections[0].section_text
                except AttributeError: pass
            elif v in ('section_text', 'all'):
                self.assertTrue(obj.articles[0].sections[0].section_text, 'bad depth')

class Language(HPTestCase):
    def test_fetch(self):
        req = self.api.table('language').fetch(1)
        obj = req.objects()[0]
        self.assertTrue(obj.code == 'af', 'missing language')

    def test_list(self):
        req = self.api.table('language').short().limit(0)
        objects = req.objects()
        self.assertTrue(len(objects) >= 10, 'missing language')
        for obj in objects:
            self.assertTrue(obj.code, 'missing language code')

class Category(HPTestCase):
    def test_fetch(self):
        req = self.api.table('category').fetch(2)
        obj = req.objects()[0]
        self.assertTrue(obj.name == 'Food', 'missing category')

    def test_list(self):
        req = self.api.table('category').limit(0)
        objects = req.objects()
        self.assertTrue(len(objects) >= 10, 'missing category')
        for obj in objects:
            self.assertTrue(obj.display_name, 'missing display name')


class Article(HPTestCase):
    def test_fetch(self):
        req = self.api.table('article').fetch(999999)
        obj = req.objects()[0]
        self.assertEqual(obj.title, 'Puducherry', 'incorrect article')

    def test_fetch_missing(self):
        try:
            req = self.api.table('article').fetch(999999999999999)
            obj = req.objects()[0]
        except APIException, e:
            self.assertEqual(e.status_code, 410, 'should be missing article')

    def test_search_term(self):
        req = self.api.table('article').search().term('Golden')
        obj = req.objects()[0]
        self.assertTrue(re.search('Golden', obj.title), 'incorrect article')

    def test_search_point(self):
        lat = 37.4
        lng = -122.9
        req = self.api.table('article').search().point({'lat':str(lat), 'lng':str(lng)})
        obj = req.objects()[0]
        self.assertTrue(obj.title, 'missing article')

    def test_search_location(self):
        req = self.api.table('article').search().location('San Francisco, CA')
        objects = req.objects()
        self.assertTrue(len(objects) >= 10)
        obj = objects[0]
        self.assertTrue(obj.title, 'missing article')

    def test_featured(self):
        req = self.api.table('article').featured()
        objects = req.objects()
        self.assertTrue(len(objects) >= 10)
        obj = objects[0]
        self.assertTrue(obj.title, 'missing article')

    def test_filter_channel(self):
        req = self.api.table('article').search().location('San Francisco, CA')
        req = req.filters({'ch':'hearplanet'})
        for obj in req.objects():
            self.assertTrue(obj.channel.name == 'hearplanet', 'missing article')

    """ Note that this may fail (response content = '') if there are
        no published articles in the given language.
    """
    def test_filter_language(self):
        req = self.api.table('article').search().location('Paris, France')
        req = req.filters({'lang':'fr'})
        obj = req.objects()[0]
        self.assertTrue(obj.language_code == 'fr', 'missing article')

    def test_filter_bbox(self):
        req = self.api.table('article').search()
        req = req.filters({'bbox':'(37.3,-122.8)(37.6,-120.0)'})
        obj = req.objects()[0]
        self.assertTrue(obj.title, 'missing article')

class Poi(HPTestCase):
    def test_fetch(self):
        req = self.api.table('poi').fetch(999999)
        obj = req.objects()[0]
        self.assertEqual(obj.title, 'Puducherry', 'incorrect poi')
    
    def test_fetch_missing(self):
        try:
            req = self.api.table('poi').fetch(999999999999999)
            obj = req.objects()[0]
        except APIException, e:
            self.assertEqual(e.status_code, 410, 'should be missing poi')

    def test_search_term(self):
        req = self.api.table('poi').search().term('Golden')
        obj = req.objects()[0]
        self.assertTrue(re.search('Golden', obj.title), 'incorrect poi')

    def test_search_point(self):
        lat = 37.4
        lng = -122.9
        req = self.api.table('poi').search().point({'lat':str(lat), 'lng':str(lng)})
        obj = req.objects()[0]
        self.assertTrue(obj.title, 'missing poi')

    def test_search_location(self):
        req = self.api.table('poi').search().location('San Francisco, CA')
        obj = req.objects()[0]
        self.assertTrue(obj.title, 'missing poi')



if __name__ == '__main__':
    try:
        unittest.main()
    except KeyboardInterrupt:
        sys.exit(0)
