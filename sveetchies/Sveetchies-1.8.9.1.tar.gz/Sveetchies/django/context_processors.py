# -*- coding: utf-8 -*-
"""
Contexts Processors
"""
import re

from django.conf import settings

from Sveetchies.django.utils import get_metas

def site_urls(request, extra={}, extra_metas={}):
    """
    Rajoute au context les urls communes à l'application, appelés les "métas" qui 
    contiennent l'url du site, l'url des médias, le nom du site, etc..
    
    Ces métas sont alors disponibles depuis n'importe quel contexte d'une vue, via le 
    nom "metas" (et donc utilisable aussi dans les templates).

    :type request: object
    :param request: Objet de la requête passé au processor

    :type extra: dict
    :param extra: (optional) Dictionnaire d'éléments supplémentaires à rajouter au 
                  contexte en plus des métas.

    :type extra_metas: dict
    :param extra_metas: (optional) Dictionnaire d'éléments supplémentaires à rajouter 
                        aux métas.

    :rtype: dict
    :return: Le dictionnaire du contexte
    """
    m = get_metas(extra=extra_metas)
    context_dict = { 'metas': m }
    if 'STATIC_URL' in m:
        context_dict['STATIC_URL'] = m.pop('STATIC_URL')
    context_dict.update(extra)
    return context_dict

def AutoMenuContext(request):
    """
    Ajoute deux variables dans le contexte d'un template pour construire 
    automatiquement un menu de navigation principal
    
    * automenu_scheme: tuple de tuples d'entrée du menu sous la forme (pattern, url, 
      key, title) à définir initialement dans la constante ``settings.AUTOMENU_SCHEME``;
    * automenu_active_key: string du nom clé de l'entrée du menu à considérer comme active;
    
    La détermination de l'entrée active se fait à partir d'un regex match à partir de la 
    pattern de l'entrée sur l'url absolu de la page courante (récupéré dans son request).
    
    TODO: précompilation des regex au démarrage comme le fait "django.core.urlresolvers"
    
    Installation
    ------------
    
    Exemple d'un ``settings.AUTOMENU_SCHEME`` à renseigner : ::
        
        AUTOMENU_SCHEME = (
            ('^/$', '/', 'homepage', u'Accueil'),
            ('^/news/(.*)/$', '/news/', 'news', u'Actualités'),
            ('^/about/$', '/about/', 'about', u'À propos'),
        )
        
    Et ajouter ce context_processor vers la fin de ceux déja configuré dans vos settings : ::
        
        TEMPLATE_CONTEXT_PROCESSORS = (
            ...
            'Sveetchies.django.context_processors.AutoMenuContext',
        )
    
    
    """
    scheme = getattr(settings, 'AUTOMENU_SCHEME', [])
    active_key = None
    relative_url = request.path
    for pattern,url,key,title in scheme:
        m = re.match(pattern, relative_url)
        if m:
            active_key = key
            break
    
    context_dict = {
        'automenu_scheme': scheme,
        'automenu_active_key': active_key,
    }
    return context_dict
