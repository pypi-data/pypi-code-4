#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitaires du parser principal
"""
import unittest
from parser import Wiki2XhtmlParser
from testcases.default import *

class ParserTestCase(unittest.TestCase):
    def test_001_Inline(self):
        """Test des mises en forme en ligne"""
        W2Xobject = Wiki2XhtmlParser()
        self.assertEquals(W2Xobject.transform(INLINE_TEST_CASE), INLINE_TEST_ATTEMPT)

    def test_002_Block(self):
        """Test simple des blocs"""
        W2Xobject = Wiki2XhtmlParser()
        self.assertEquals(W2Xobject.transform(SIMPLE_BLOCK_TEST_CASE), SIMPLE_BLOCK_TEST_ATTEMPT)

    def test_003_BulletList(self):
        """Test des imbrications des listes à puces"""
        W2Xobject = Wiki2XhtmlParser()
        self.assertEquals(W2Xobject.transform(BULLETLIST_TEST_CASE), BULLETLIST_TEST_ATTEMPT)

    def test_004_Title(self):
        """Test des titres"""
        W2Xobject = Wiki2XhtmlParser()
        self.assertEquals(W2Xobject.transform(TITLE_TEST_CASE), TITLE_TEST_ATTEMPT)

    def test_005_Wikiword(self):
        """Test des wikiword"""
        # Désactivés
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('active_wikiwords', False)
        self.assertEquals(W2Xobject.transform(WIKIWORDS_TEST_CASE), WIKIWORDS_TEST_ATTEMPT_DISABLED1)
        # Désactivés par l'absence de words_pattern
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('active_wikiwords', True)
        W2Xobject.setOpt('words_pattern', None)
        W2Xobject.setOpt('published_wikipage', WIKIWORDS_ENABLED_PAGE)
        self.assertEquals(W2Xobject.transform(WIKIWORDS_TEST_CASE), WIKIWORDS_TEST_ATTEMPT_DISABLED2)
        # Activés mais sans aucune page publié
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('active_wikiwords', True)
        W2Xobject.setOpt('published_wikipage', {})
        self.assertEquals(W2Xobject.transform(WIKIWORDS_TEST_CASE), WIKIWORDS_TEST_ATTEMPT_EMPTYPUBLISHED)
        # Activés avec des pages publiés
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('active_wikiwords', True)
        W2Xobject.setOpt('published_wikipage', WIKIWORDS_ENABLED_PAGE)
        self.assertEquals(W2Xobject.transform(WIKIWORDS_TEST_CASE), WIKIWORDS_TEST_ATTEMPT_ENABLED)

    def test_006_Fulldocument(self):
        """Test d'un document complet"""
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('active_wikiwords', True)
        W2Xobject.setOpt('published_wikipage', WIKIWORDS_ENABLED_PAGE)
        self.assertEquals(W2Xobject.transform(FULLDOCUMENT_TEST_CASE), FULLDOCUMENT_TEST_ATTEMPT)

    def test_100_SettingsKwargs(self):
        """Changement des settings par lot"""
        W2Xobject = Wiki2XhtmlParser()
        newsettings = {
            'active_title': False,       # Activation des titres !!!
            'active_em': False,      # Activation du <em> ''...''
            'active_strong': False,  # Activation du <strong> __...__
            'active_code': False,        # Activation du <code> @@...@@
            'active_ins': False,     # Activation des ins ++..++
            'active_del': False,     # Activation des del --..--
        }
        W2Xobject.kwargsOpt(newsettings)
        for name,value in newsettings.items():
            self.assertEquals(W2Xobject.getOpt(name), value)

    def test_101_SettingsUnits(self):
        """Changement des settings à l'unité"""
        W2Xobject = Wiki2XhtmlParser()
        newsettings = {
            'active_title': False,       # Activation des titres !!!
            'active_em': False,      # Activation du <em> ''...''
            'active_strong': False,  # Activation du <strong> __...__
            'active_code': False,        # Activation du <code> @@...@@
            'active_ins': False,     # Activation des ins ++..++
            'active_del': False,     # Activation des del --..--
        }
        for name,value in newsettings.items():
            W2Xobject.setOpt(name, value)
        for name,value in newsettings.items():
            self.assertEquals(W2Xobject.getOpt(name), value)

    def test_102_TitleLevel(self):
        """Settings de la limite des niveaux de titres"""
        W2Xobject = Wiki2XhtmlParser()
        W2Xobject.setOpt('first_title_level', 2)
        self.assertEquals(W2Xobject.transform(TITLE_TEST_CASE), TITLE_TEST_ATTEMPT2)

if __name__ == "__main__":
    unittest.main()
    #W2Xobject = Wiki2XhtmlParser()
    #W2Xobject.setOpt('active_wikiwords', True)
    #W2Xobject.setOpt('published_wikipage', WIKIWORDS_ENABLED_PAGE)
    #print W2Xobject.transform(WIKIWORDS_TEST_CASE)
