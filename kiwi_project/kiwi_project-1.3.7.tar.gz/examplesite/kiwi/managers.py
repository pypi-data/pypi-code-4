# -*- coding: utf-8 -*-
from django.db import models
from django.core.cache import cache

WIKI_WIKIPAGES_ALLACTIVE_TIMELIFE = 60 * 60
WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY = 'kiwi___wiki_wikipage_active_menu'
WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY = 'kiwi___wiki_wikipage_active_dict'

class WikipageManager(models.Manager):
    def get_active_menu(self):
        """
        Récupération de toute les pages actives, mais limitée à certaines 
        colonnes du modèle, donc destiné pour des menus.
        Cette méthode utilise un cache.
        """
        object_list = cache.get(WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY)
        if not object_list:
            object_list = self.filter(in_sitemap=True, active=True).order_by('title').values('id','parent','uri','title','order',)
            cache.set(WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY, [item for item in object_list], WIKI_WIKIPAGES_ALLACTIVE_TIMELIFE)
        
        return object_list
    
    def get_active_dict(self):
        """
        Récupération de toute les pages actives, dans un dictionnaire à plat.
        Ceci est utilisé pour passer la liste des Wikiword au parser de syntaxe wiki.
        Cette méthode utilise un cache.
        """
        object_dict = cache.get(WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY)
        if not object_dict:
            object_dict = {}
            for k in self.get_active_menu():
                object_dict[k['uri']] = k['title']
            cache.set(WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY, object_dict, WIKI_WIKIPAGES_ALLACTIVE_TIMELIFE)
        
        return object_dict
