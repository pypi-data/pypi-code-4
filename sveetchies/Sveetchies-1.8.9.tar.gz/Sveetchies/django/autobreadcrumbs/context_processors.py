# -*- coding: utf-8 -*-
"""
Context Processor
"""
from django.conf import settings
from django.core.urlresolvers import Resolver404, get_resolver

def AutoBreadcrumbsContext(request):
    """
    Processeur de context de vue qui forme le chemin d'accès des vues parcourues pour 
    arriver à la page courante.
    
    Utilise l'attribut "request.path" pour connaître le chemin de la page courante, le 
    découpe en tronçons additionnés sur les "/" et test l'existence d'une vue pour 
    chaque tronçons pour en retrouver le titre défini le cas échéant.
    
    Pour les titres "dynamiques", on utilise les variables de templates {{var}} dans le 
    titre en utilisant des noms de variables disponibles dans le contexte fournit par la 
    vue.
    
    Le titre est défini soit par un attribut sur la vue (manuellement ou avec le décorateur 
    dédié), soit dans les settings avec un dictionnaire indexé sur les noms des urls. Les 
    deux peuvent être définis et la version dans les settings prendra toujours la main sur 
    le reste si elle y est définie.
    
    Nécessite :
    
    * Un attribut statique "title" (string) ou "titles" (dict) définit sur les 
      méthodes de vue (facilité avec l'usage du décorateur), inutile en règle générale 
      pour les vues qui ne produisent pas une page html complète OU une entrée dans 
      ``settings.AUTOBREADCRUMBS_TITLES`` sous la forme d'un tuple "(url-name, title)";
    * Que toute les urls soit nommées correctement (avec leur attribut "name");
    * Une solide organisation de la map des urls du site, des ressources différentes 
      passant par une meme url peuvent provoquer des problèmes, de même pour des parties de 
      l'url qui ne sont pas disponibles pour tout les utilisateurs (à cause d'une restriction 
      d'accès ou autre) qui s'afficheront dans le chemin d'accès alors 
      qu'elles ne le devraient pas;
    
    Le titre peut être un tuple contenant le titre et une méthode de controle d'accès 
    prenant le request en unique argument et renvoyant True pour accepter l'entrée, 
    False pour l'ignorer.
    
    Exemple dans une vue : ::
    
        @autobreadcrumb_add(u"Mon zuper zindex")
        def index(request):
            ....
    
    Ou : ::
    
        @autobreadcrumb_add({
            "pages-index1": u"Mon zuper zindex",
            "pages-index2": u"My upper index",
        })
        def index(request):
            ....
    
    Ou dans les settings : ::
    
        AUTOBREADCRUMBS_TITLES = {
            "pages-index1": u"Mon zuper zindex",
            "pages-index2": u"My upper index",
        }

    Le chemin d'accès sera présent sous forme de liste dans la variable "autobreadcrumbs_elements" du 
    contexte du template. Chaque élément de la liste est un tuple contenant :
    
        url, title, view_args, view_kwargs
    
    On peut aussi utiliser ``@autobreadcrumb_hide`` pour exclure une vue des miettes, de 
    même indiquer ``None`` en valeur d'un titre l'exclut aussi des miettes.
    
    Les *Class base views* sont actuellement ignorés par autobreadcrumbs, de plus ses 
    décorateurs ne fonctionnent pas dessus, le seul moyen est de passer par la rédaction 
    des associations "urlname:title" dans les settings comme décrit plus haut.
    
    TODO: * Implémenter la recherche sur les vues basés sur des class;
          * Pouvoir exclure des tranches complètes ou non selon une ou des regex (ou quoique 
            ce soit d'autres pour éviter de faire le calcul du pathline dans l'admin);
    """
    relative_url = request.path
    urlresolver = get_resolver(settings.ROOT_URLCONF)
    breadcrumbs_elements = []
    current = None
    
    # Segmente l'url en étapes additionnels
    # eg : Pour /foo/bar/
    #      - /
    #      - /foo
    #      - /foo/bar
    path_segments = ['']
    tmp = ''
    for segment in relative_url.split('/'):
        if segment:
            tmp += segment+'/'
            path_segments.append(tmp)
    
    # Résolution de chaque segment
    for seg in path_segments:
        try:
            resolved = urlresolver.resolve('/'+seg)
        except Resolver404:
            pass
        else:
            title = name = resolved.url_name
            if hasattr(resolved.func, "crumb_hided"):
                continue
            view_control = None
            if hasattr(settings, "AUTOBREADCRUMBS_TITLES") and title in getattr(settings, "AUTOBREADCRUMBS_TITLES", {}):
                title = settings.AUTOBREADCRUMBS_TITLES[title]
            elif hasattr(resolved.func, "crumb_titles"):
                title = resolved.func.crumb_titles.get(title, title)
            elif hasattr(resolved.func, "crumb_title"):
                title = resolved.func.crumb_title
            else:
                continue
            if title is None:
                continue
            # Titre dans un tuple avec sa méthode de controle d'accès, qui si elle 
            # renvoit "False", ignore l'entrée pour construire le chemin d'accès
            if not isinstance(title, basestring):
                title, view_control = title
                if not view_control(request):
                    continue
            breadcrumbs_elements.append( BreadcrumbRessource(seg, name, title, resolved.args, resolved.kwargs) )
        
    if len(breadcrumbs_elements)>0:
        current = breadcrumbs_elements[-1]
    
    return {
        'autobreadcrumbs_elements': breadcrumbs_elements,
        'autobreadcrumbs_current': current,
    }

class BreadcrumbRessource(object):
    def __init__(self, path, name, title, view_args, view_kwargs):
        self.path = path
        self.name = name
        self.title = title
        self.view_args = view_args
        self.view_kwargs = view_kwargs
        
    def __repr__(self):
        return "<BreadcrumbRessource: {0}>".format(self.name)
        
    def __str__(self):
        # TODO: should be __unicode__() because passed paths can be unicode, right ?
        return self.path
