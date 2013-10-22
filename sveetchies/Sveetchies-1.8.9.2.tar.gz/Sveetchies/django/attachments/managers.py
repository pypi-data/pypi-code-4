# -*- coding: utf-8 -*-
from django.db import models

class AttachManager(models.Manager):
    """
    TODO: inutile en l'état, nécessiterait une option pour rechercher les fichiers à 
    partir d'un objet qui y ferait référence
    """
    def get_attachments(self, user=None, orders=['title']):
        """
        Renvoi une liste de fichiers optionnellement limitée aux 
        droits d'un objet utilisateur
        """
        query_kwargs = {
            'archived': False,
        }
        if user and not user.is_staff:
            query_kwargs['is_public'] = True
            
        queryset = self.filter(**query_kwargs).order_by(*orders)
        
        return queryset
