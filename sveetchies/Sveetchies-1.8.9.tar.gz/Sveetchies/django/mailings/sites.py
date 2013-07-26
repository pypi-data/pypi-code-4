# -*- coding: utf-8 -*-
"""
Registre des contrôleurs
"""
class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class MailingSite(object):
    """
    Interface du registre des contrôleurs référencés dans une webapp
    """
    def __init__(self):
        self._registry = {} # controler_key string -> controler_module class
        self.global_context = None

    def get_registry(self):
        return self._registry

    def set_context(self, **kwargs):
        """
        Définit un contexte de base identique pour toute les instances de contrôleur
        """
        self.global_context = kwargs

    def get_controler(self, key, **kwargs):
        """
        Méthode pour accéder et instancier un contrôleur inscrit au registre
        
        :type key: string
        :param key: Nom clé d'un contrôleur.
        
        :type kwargs: various
        :param kwargs: Arguments à utiliser dans l'instanciation du contrôleur.
        
        :rtype: object `Sveetchies.django.mailings.interface.BaseMailTemplate`
        :return: Objet du contrôleur
        """
        if key not in self._registry:
            raise NotRegistered('The controler "%s" is not registered' % key)
        
        if self.global_context:
            if 'context' in kwargs:
                kwargs['context'].update(self.global_context)
            else:
                kwargs['context'] = self.global_context
        return self._registry[key](**kwargs)

    def register(self, obj):
        """
        Inscrit un nouveau contrôleur au registre
        
        Si un contrôleur existe déja avec la même clé, une exception 
        ``AlreadyRegistered`` sera levée.
        
        :type obj: object `Sveetchies.django.mailings.interface.BaseMailTemplate`
        :param obj: Contrôleur d'un template de mail (en général un objet héritant de 
                    BaseMailTemplate)
        """
        if obj.key in self._registry:
            raise AlreadyRegistered('The controler "%s" is already registered' % obj.key)
        # Instantiate the admin class to save in the registry
        self._registry[obj.key] = obj

    def unregister(self, obj):
        """
        Désinscrit un contrôleur du registre
        
        Si le contrôleur n'existe pas dans le registre, une exception 
        ``NotRegistered`` sera levée.
        
        :type obj: object `Sveetchies.django.mailings.interface.BaseMailTemplate`
        :param obj: Contrôleur d'un template de mail (en général un objet héritant de 
                    BaseMailTemplate)
        """
        if obj.key not in self._registry:
            raise NotRegistered('The controler "%s" is not registered' % obj.key)
        del self._registry[obj.key]

# This global object represents the default mailings site, for the common case.
# You can instantiate MailingSite in your own code to create a custom admin site.
site = MailingSite()
