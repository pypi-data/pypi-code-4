#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Macro 'attach'

Exemple de la syntaxe wiki : ::

    {% attach 1 %}{% endattach %}

    {% attach 42 %}Plop de texte{% endattach %}

Chaque macro est alors remplacée par un lien vers le fichier d'attachement qu'elle cible.

Si une macro mentionne un identifiant d'entrée qui n'existe pas dans l'option 
'attached_items', le contenu (entre les balises) de la macro est renvoyée tel quel sans 
aucun ajout ni modification.

Cette macro fonctionne en mode 'pre', pour l'ajouter aux macros du parser il suffit de 
la spécifier après l'instanciation du parser et de lui fournir aussi en tant qu'option 
un dictionnaire Python des attachements disponibles tel que : ::

    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.setOpt('attached_items', {
        '1':'http://perdu.com',
        '42':('http://perdu.com',u'42 is the key'),
    })
    W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)

À noter que chaque entrée du dictionnaire des attachements disponibles peut être soit 
directement un ``string`` contenant une url, soit un ``tuple`` ou ``list`` sous la 
forme ``(url, title)``.

Dans le cas ou une entrée possède un titre il est utilisé, mais seulement si la macro 
n'a pas de contenu, dans ce cas c'est le texte contenu dans la macro qui est utilisé. Si 
aucun titre ou texte n'existe, l'url est alors utilisée comme le titre du lien.

Le titre d'un attachement (que ce soit son titre d'entrée du dictionnaire ou le texte de 
la macro) ne doit pas contenir les caractères suivant ``[``,``]``,``|``, ce serait une 
erreure.

TODO: Échapper [ et ], pour cela il faudra modifier un peu le parser avec macro pour 
qu'il passe comme argument son "self" au lieu de simplement les options, cela ouvrirait 
en plus d'autres possibilités (accès à la syntaxe, méthodes utiles du parser disponibles, 
etc..).
"""
def parse_macro_attach(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
    """
    Méthode de traitement de la macro 'attach'
    
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
    content = macro_value
    # Des arguments sont requis pour le traitement, si il n'y en a pas on renvoit le 
    # contenu de la macro tel quel
    if len(macro_args) > 0:
        attachement_id = macro_args[0]
        # Recherche si l'id de l'attachement est valide
        if attachement_id in opts.get('attached_items', []):
            url = opts['attached_items'][attachement_id]
            title = None
            # Cherche si l'entrée d'attachement est sous la forme (url, title)
            if isinstance(url, tuple) or isinstance(url, list):
                url, title = url
            # Le texte entre les balises prévaut sur tout le titre de l'entrée 
            # d'attachement
            if len(macro_value.strip())>0:
                title = macro_value
            # Le titre de l'entrée d'attachement est utilisé si il n'est pas vide et 
            # qu'il n'y a pas de texte dans entre les balises
            elif title and len(title.strip())>0:
                pass
            # Aucun titre disponible ni texte, l'url devient le titre affiché
            else:
                title = url
            title = title.replace('|', '&#124;')
            url = url.replace('|', '%7C')
            #url = url.replace('|', '%7C').replace('[', '%5B').replace(']', '%5D')
            # Transformation en un lien wiki
            content = "[%s|%s]" % (title, url)
    
    return source.replace(macro_escaped, content)

# DEMO
if __name__ == "__main__":
    from parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
    
    test_source = u"""Foo lorem ipsum salace nec vergiture.

* Moopa
** {% attach 1 %}{% endattach %}
* Moope
* [Moopi|http://sveetch.net/download.py?file=cocolapin.xls&validate=true]
** Moopo
** Moopu

Ceci est un {% attach 42 %}Plop de texte{% endattach %} mégamagique.

Mais ça c'est totalement {% attach 33 %}pas correct{% endattach %} alors que ceci le devrait : {% attach 11 %}{% endattach %}.
"""
    
    attached_items = {
        '1': ("http://perdu.com/prout.pdf", "Prout !"),
        '11': "http://perdu.com/plouf.pdf",
        '42': "http://sveetch.net/download.py?coco|file=cocolapin.xls&validate=true",
        'totoz': "http://sveetch.net/download.py?file=totoz.gif",
    }
    
    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.setOpt('attached_items', attached_items)
    W2Xobject.add_macro('attach', mode='pre', func=parse_macro_attach)
    
    print "="*60
    res = W2Xobject.transform( test_source )
    print test_source
    print "-"*60
    print "@%s@" % res
    print "="*60
