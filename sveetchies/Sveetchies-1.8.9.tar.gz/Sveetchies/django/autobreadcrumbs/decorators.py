# -*- coding: utf-8 -*-
"""
Décorateurs utiles

NOTE: 1. Ces décorateurs ne fonctionnent pas avec les formulaires de type "Wizard" de 
         Django, qui sont des class enrobés par une méthode "_wrapped_view" qui ne 
         contient donc pas les attributs rajoutés. Actuellement la solution pour les Wizard 
         et de définir leur titre dans les settings, mais il faudrait une solution plus 
         élégantes permettant de le définir dans la vue histoire d'être cohérent avec le 
         principe de "autobreadcrumbs";
      2. Impossible d'utiliser ces décorateurs en l'état pour le système de vue par une 
         class generic. Le problème étant qu'il faudrait décorer ``as_view()`` et donc 
         l'hériter au moins dans chaque class de base, ou peut être joué avec 
         ``*Mixin`` ?;
"""
def autobreadcrumb_add(value):
    """
    Décorateur d'une vue pour lui ajouter son/ses titre(s) possible(s) dans le pathline/breadcrumb
    
    Reçois un argument obligatoire qui peut être :
    
    * Un string, dans ce cas il est définit comme l'unique titre possible de la vue
    * Un dictionnaire, indexé sur le nom des url (tel que définit dans les "urls.py") 
      contenant les titres possibles selon l'url qui l'apelle
    """
    def _set_var(obj):
        if isinstance(value, basestring):
            setattr(obj, "crumb_title", value)
        elif isinstance(value, dict):
            setattr(obj, "crumb_titles", value)
        return obj
    return _set_var

def autobreadcrumb_hide(value):
    """
    Décorateur d'une vue pour la cacher dans le pathline/breadcrumb
    
    TODO: Actuellement il faut utiliser le décorateur de la façon suivante :
            
            @autobreadcrumb_hide('')
            def mafonction(foo):
                ..
        
        Sinon une erreure est levée, c'est due au fait que je n'ai pas tout compris des 
        décorateurs et que je ne sais pas encore comment faire ce qui devrait être :
        
            @autobreadcrumb_hide
            def mafonction(foo):
                ..
    """
    def _set_var(obj):
        setattr(obj, "crumb_hided", True)
        return obj
    return _set_var
