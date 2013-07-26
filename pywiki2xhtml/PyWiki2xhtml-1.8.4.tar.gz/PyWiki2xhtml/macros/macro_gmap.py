#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Macro 'googlemap'

TODO: * Pouvoir insérer plusieurs marqueurs dans une même carte;

Requires :

* jQuery >=1.4.x et son plugin Gmap3 >= 1.1 sur la page destinée à afficher le contenu 
  généré;
* Cette macro génère un contenu qui nécessite une lib JS externe, le système de macro 
  aurait besoin d'une possibilité que les macros exposent les médias dont ils peuvent 
  avoir besoin si ils sont utilisés, de façon à ce que les documents intègre 
  conditionnellement les médias qu'ils ont vraiment besoin;
"""
import json
from PyWiki2xhtml.parser import Wiki2XhtmlParser

WIDGET_TEMPLATE = u"""<script type="text/javascript">
    //<![CDATA[
    $(document).ready(function(){{
        $("#{id}").gmap3({json});
    }});
    //]]>
    </script>
    <div id="{id}" class="macro_map_container"></div>
"""
def parse_macro_googlemap(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
    """
    Méthode de traitement de la macro 'googlemap', qui permet d'insérer 
    une google-map sur une destination précise
    
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
    # Options par défaut
    map_opts_global = {
        'action': 'addMarker',
        'address': "",
        'map':{
            'center': True,
            'zoom': 14,
        },
        'marker':{
            'options':{
                'draggable': False,
            },
        },
    }
    
    html = ''
    if macro_value and len(macro_value.strip())>0:
        W2Xobject = Wiki2XhtmlParser()
        
        res = W2Xobject.transform( macro_value )
        map_opts_global['infowindow'] = {
            'options':{
                'content': u'<div class="map_infowindow_container">{0}</div>'.format(res),
            },
        }
    if macro_args and isinstance(macro_args, basestring):
        map_opts_global['address'] = macro_args
        html = WIDGET_TEMPLATE.format(id="doc_map_"+str(macro_serial), json=json.dumps(map_opts_global))
    
    return source.replace(macro_escaped, html)

# DEMO
if __name__ == "__main__":
    from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
    from PyWiki2xhtml.testcases.macros import GMAP_TEST_CASE, GMAP_TEST_ATTEMPT
    
    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.add_macro('googlemap', mode='post', func=parse_macro_googlemap)
    
    res = W2Xobject.transform( GMAP_TEST_CASE )
    #print "="*60
    
    #print "-"*60
    #print "SOURCE"
    #print "-"*60
    #print MEDIAPLAYER_TEST_CASE
    
    #print "-"*60
    #print "%s lignes" % len(res.splitlines())
    #print "."*60
    #print "RENDU"
    #print "-"*60
    print "@%s@" % res
    
    #print "="*60
