# -*- coding: utf-8 -*-
from django.db import models
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

class PictureManager(models.Manager):
    def publishable_filter(self):
        """
        Renvoi une liste des images publiables
        """
        queryset = self.filter(visible=True)
        
        return queryset
    
    def get_publishable_or_404(self, **kwargs):
        """
        Renvoi l'objet si il est publiable sinon lève une exception Http404
        """
        try:
            queryset = self.get(visible=True, **kwargs)
        except ObjectDoesNotExist:
            raise Http404
        
        return queryset
