#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Macro 'mediaplayer'

Cette macro est faite uniquement pour le JW-PLAYER_ + JQUERY-FLASH_. Elle permet d'
intégrer un player Flash dans un document pour lire un contenu à la demande ou un stream 
et de configurer ses options.

.. _JW-PLAYER: http://www.longtailvideo.com/players/jw-flv-player/
.. _JQUERY-FLASH: http://jquery.lukelutman.com/plugins/flash/

Le player est censé se trouver par défaut dans 'flash/player.swf'. La macro ne permet 
pas de changer son emplacement par sécurité (empecher d'importer n'importe quel Flash). 

Cependant c'est une option modifiable directement dans la configuration du parser avec 
l'option 'macro_mediaplayer_url'.

Les arguments de la macro se trouvent dans son contenu, en fait chaque argument est 
injecté dans le code html comme flashvar sans limitation, donc il est possible de 
spécifier n'importe quel flashvar du player (et même plus).

Cette macro fonctionne en mode 'post', pour l'ajouter aux macros du parser il suffit de 
la spécifier après l'instanciation du parser tel que : ::

    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)

Exemple de la syntaxe wiki : ::

    {% mediaplayer %}
    file: /site_medias/flash/mediaplayer/video.flv
    {% endmediaplayer %}

Rendu prévu pour l'exemple : ::

    <div class="macro_mediaplayer">
    <div id="mediaplayer_0" class="player_container"></div>
    <script type="text/javascript">
    //<![CDATA[
    $('#mediaplayer_0').flash({
            'width': '320', 'allowfullscreen': 'true', 'src': 'player.swf', 'allowscriptaccess': 'always', 'height': '240',
            'flashvars': { 'file': '/site_medias/flash/mediaplayer/video.flv' }
        },
        { version: '9.0' }
    );
    //]]>
    </script>
    </div>

TODO: 

* Utiliser le module Json de Python qui est maintenant stabilisé;
* Permettre une autre implémentation de player (flash, html5);
* De plus JW PLAYER a évolué depuis le temps et ses attributs flashvars aussi;
* Sécuriser les attributs pour que l'on ne puisse pas casser le javascript et permettre 
  une exploitation "frauduleuse";
"""
def parse_macro_mediaplayer(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
    """
    Méthode de traitement de la macro 'mediaplayer', qui permet d'insérer 
    un mediaplayer Flash.
    
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
    MEDIAPLAYER_TEMPLATE = u"""<div class="macro_mediaplayer">
<div id="mediaplayer_%(serial)s" class="player_container"></div>
<script type="text/javascript">
//<![CDATA[
$('#mediaplayer_%(serial)s').flash({
        %(flashargs)s,
        'flashvars': { %(flashvars)s }
    },
    { version: '9.0' }
);
//]]>
</script>
</div>
"""
    
    mediaplayer_opts_keys = ['width', 'height', 'allowfullscreen', 'allowscriptaccess', 'wmode', 'src']
    # Options par défaut
    flashargs = {
        'width': '320',
        'height': '240',
        'src': opts.get('macro_mediaplayer_url', 'player.swf'),
        'allowfullscreen': 'true',
        'allowscriptaccess': 'always',
    }
    flashvars = {}
    
    for item in macro_value.splitlines():
        try:
            # Si on a pas une ligne vide
            if len(item.strip())>0:
                key = item.split(':')[0].strip()
                value = ":".join([i.strip() for i in item.split(':')[1:]])
                if key in mediaplayer_opts_keys:
                    flashargs[ key ] = value
                else:
                    flashvars[ key ] = value
        except:
            continue
    
    if len(flashvars) == 0:
        # Aucun contenu trouvé, on nettoie
        html = ''
    else:
        # Fait un semblant de transformation en json des arguments et options
        flashargs = ", ".join([ "'%s': '%s'"%(k,v) for k,v in flashargs.items() ])
        flashvars = ", ".join([ "'%s': '%s'"%(k,v) for k,v in flashvars.items() ])
        # Compilation du template html
        html = MEDIAPLAYER_TEMPLATE % { 'serial': macro_serial, 'flashargs': flashargs, 'flashvars': flashvars, }
    
    return source.replace(macro_escaped, html)

# DEMO
if __name__ == "__main__":
    from PyWiki2xhtml.macros.parser import Wiki2XhtmlMacros as Wiki2XhtmlParser
    from PyWiki2xhtml.testcases.macros import MEDIAPLAYER_TEST_CASE, MEDIAPLAYER_TEST_ATTEMPT
    
    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.add_macro('mediaplayer', mode='post', func=parse_macro_mediaplayer)
    
    res = W2Xobject.transform( MEDIAPLAYER_TEST_CASE )
    print "="*60
    
    print "-"*60
    print "SOURCE"
    print "-"*60
    print MEDIAPLAYER_TEST_CASE
    
    print "-"*60
    print "%s lignes" % len(MEDIAPLAYER_TEST_ATTEMPT.splitlines())
    print "."*60
    print "ATTENDU"
    print "-"*60
    print "@%s@" % MEDIAPLAYER_TEST_ATTEMPT
    
    print "-"*60
    print "%s lignes" % len(res.splitlines())
    print "."*60
    print "RENDU"
    print "-"*60
    print "@%s@" % res
    
    print "-"*60
    print "ASSERT EQUAL %s" % (res==MEDIAPLAYER_TEST_ATTEMPT)
    print "-"*60

    print "="*60
