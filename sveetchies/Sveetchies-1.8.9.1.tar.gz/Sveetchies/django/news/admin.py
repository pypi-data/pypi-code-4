# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django
"""
from django.contrib import admin

from models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible', )
    list_filter = ('visible',)
    ordering = ('title',)
    search_fields = ('title','description',)
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        (u'Contenu', {'fields': ('title', 'description')}),
        (u'Paramètres', {'classes': ('collapse open',), 'fields': ('slug', 'visible',)}),
    ]

class EntryAdmin(admin.ModelAdmin):
    list_display = ('publish_date', 'title', 'category', 'visible', 'is_collapsed_in_list', )
    list_filter = ('publish_date', 'visible', 'category')
    ordering = ('-publish_date',)
    search_fields = ('title','introduction','content',)
    raw_id_fields = ('category',)
    readonly_fields = ('author',)
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        (u'Contenu', {'fields': ('title', 'introduction', 'content')}),
        (u'Paramètres', {'classes': ('collapse open',), 'fields': ('slug', 'publish_date', 'category', 'visible')}),
        (u'Attachements', {'fields': ('attached_files',)}),
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

admin.site.register(Category, CategoryAdmin)
admin.site.register(Entry, EntryAdmin)
