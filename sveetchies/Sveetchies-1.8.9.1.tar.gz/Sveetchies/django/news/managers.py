# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

class EntryManager(models.Manager):
    def publishable_filter(self):
        """
        Renvoi une liste des entrées publiables
        """
        queryset = self.filter(publish_date__lte=datetime.datetime.now(), visible=True)
        
        return queryset
    
    def get_publishable_or_404(self, **kwargs):
        """
        Renvoi l'objet si il est publiable sinon lève une exception Http404
        """
        try:
            queryset = self.get(publish_date__lte=datetime.datetime.now(), visible=True, **kwargs)
        except ObjectDoesNotExist:
            raise Http404
        
        return queryset
