# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django
"""
from django.contrib import admin

from models import *

class AttachAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'author', 'archived', 'is_public')
    list_filter = ('created', 'archived', 'is_public')
    ordering = ('-created',)
    search_fields = ('title',)
    readonly_fields = ('author',)
    fieldsets = [
        (u'Contenu', {'fields': ('title', 'file')}),
        (u'Options', {'classes': ('collapse closed',), 'fields': ('description', 'archived', 'is_public')}),
    ]
    
    def save_model(self, request, obj, form, change):
        """
        Surclasse la méthode de sauvegarde de l'admin du modèle pour y 
        rajouter automatiquement l'auteur qui créé un nouvel objet ou effectue 
        une modification
        """
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        form.save_m2m()

        return instance

admin.site.register(Attach, AttachAdmin)
