#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests unitaires du parser avec macros

TODO: Le teste complet "test_206_allmacros" ne contient pas le test de la macro 'attach'.
"""
import unittest

from parser import Wiki2XhtmlMacros
from macro_attach import parse_macro_attach
from macro_pygments import parse_macro_pygments
from macro_mediaplayer import parse_macro_mediaplayer

from PyWiki2xhtml.testcases.macros import *

def parse_macro_helloworld(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
    """
    Méthode de traitement de la macro 'helloworld', une méthode bidon pour 
    les tests
    
    :type source: string
    :param source: Source du document complet.
    
    :type opts: dict
    :param opts: Dictionnaire des options en cours du parser.
    
    :type macro_escaped: string
    :param macro_escaped: Version d'échappement de la macro qui sert à sa recherche 
                          pour remplacement.
    
    :type macro_serial: string
    :param macro_serial: Clé unique de la macro.
    
    :type macro_value: string
    :param macro_value: Valeur source de la macro.
    
    :type macro_args: list or None
    :param macro_args: (optional) Liste des arguments inclus dans la macro, None si il 
                       n'y en avait pas.
    
    :rtype: string
    :return: Source du document avec le contenu de la macro remplacée par le rendu de 
             son traitement.
    """
    return source.replace(macro_escaped, u"++Hello World : %s++" % macro_value)

def parse_macro_helloworld2(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
    """
    Méthode de traitement de la macro 'helloworld2', une autre méthode 
    bidon pour les tests
    
    :type source: string
    :param source: Source du document complet.
    
    :type opts: dict
    :param opts: Dictionnaire des options en cours du parser.
    
    :type macro_escaped: string
    :param macro_escaped: Version d'échappement de la macro qui sert à sa recherche 
                          pour remplacement.
    
    :type macro_serial: string
    :param macro_serial: Clé unique de la macro.
    
    :type macro_value: string
    :param macro_value: Valeur source de la macro.
    
    :type macro_args: list or None
    :param macro_args: (optional) Liste des arguments inclus dans la macro, None si il 
                       n'y en avait pas.
    
    :rtype: string
    :return: Source du document avec le contenu de la macro remplacée par le rendu de 
             son traitement.
    """
    return source.replace(macro_escaped, u'<p class="helloworld2">Hello World : %s</p>' % macro_value)

class MacrosParserTestCase(unittest.TestCase):
    """
    Tests unitaires supplémentaires pour les macros
    """
    def test_201_htmlpass(self):
        """Macro 'htmlpass'"""
        W2Xobject = Wiki2XhtmlMacros()
        self.assertEquals(W2Xobject.transform(HTMLPASS_TEST_CASE), HTMLPASS_TEST_ATTEMPT)

    def test_202_attach(self):
        """Macro 'attach'"""
        W2Xobject = Wiki2XhtmlMacros()
        W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
        W2Xobject.setOpt('attached_items', {
            '1': ("http://perdu.com/prout.pdf", "Prout !"),
            '11': "http://perdu.com/plouf.pdf",
            '42': "http://sveetch.net/download.py?coco|file=cocolapin.xls&validate=true",
            'totoz': "http://sveetch.net/download.py?file=totoz.gif",
        })
        self.assertEquals(W2Xobject.transform(ATTACH_TEST_CASE), ATTACH_TEST_ATTEMPT)

    def test_203_mediaplayer(self):
        """Macro 'mediaplayer'"""
        W2Xobject = Wiki2XhtmlMacros()
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        self.assertEquals(W2Xobject.transform(MEDIAPLAYER_TEST_CASE), MEDIAPLAYER_TEST_ATTEMPT)

    def test_204_pygments(self):
        """Macro 'mediaplayer'"""
        W2Xobject = Wiki2XhtmlMacros()
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        self.assertEquals(W2Xobject.transform(PYGMENTS_TEST_CASE), PYGMENTS_TEST_ATTEMPT)

    def test_205_helloworlds(self):
        """Macros 'helloworld' de test du PRE-traitement et POST-traitement"""
        W2Xobject = Wiki2XhtmlMacros()
        W2Xobject.add_macro('helloworld', mode='pre', func=parse_macro_helloworld)
        W2Xobject.add_macro('helloworld2', mode='post', func=parse_macro_helloworld2)
        self.assertEquals(W2Xobject.transform(HELLOWORLDS_TEST_CASE), HELLOWORLDS_TEST_ATTEMPT)

    def test_206_allmacros(self):
        """Test de toute les macros dans un meme document"""
        W2Xobject = Wiki2XhtmlMacros()
        W2Xobject.add_macro('helloworld', mode='pre', func=parse_macro_helloworld)
        W2Xobject.add_macro('helloworld2', mode='post', func=parse_macro_helloworld2)
        W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
        W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)
        self.assertEquals(W2Xobject.transform(ALL_MACROS_TEST_CASE), ALL_MACROS_TEST_ATTEMPT)

if __name__ == "__main__":
    unittest.main()
    # Tests sans unittest
    #obj = Wiki2XhtmlMacros()
    #obj.add_macro('helloworld', mode='pre', func=parse_macro_helloworld)
    #obj.add_macro('helloworld2', mode='post', func=parse_macro_helloworld2)
    #obj.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
    #obj.add_macro('pygments', mode='post', func=parse_macro_pygments)
    #print obj.transform( ALL_MACROS_TEST_CASE )
