# -*- coding: utf-8 -*-
from django.contrib import admin
from Sveetchies.django.TreeMaker import TemplatedTree

from kiwi import WIKIPAGE_ENABLE_ARCHIVE
from kiwi.models import Attach, Template, Wikipage, Version

WIKIPAGE_PROTECTED_ADMIN = True

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

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'included')
    list_filter = ('date','included',)
    ordering = ('date',)

class WikipageAdmin(admin.ModelAdmin):
    list_display = ('uri', 'order', 'title', 'active', 'in_sitemap', 'last_date', 'author')
    list_filter = ('template__included',)
    ordering = ('order', 'uri')
    prepopulated_fields = {"uri": ("title",)}
    search_fields = ()
    raw_id_fields = ('parent',)
    readonly_fields = ('author',)
    fieldsets = [
        (u'Paramètres', {'classes': ('collapse open',), 'fields': ('author', 'parent', 'order', 'uri')}),
        (u'Contenu', {'fields': ('title', 'text')}),
        (u'Archivage', {'classes': ('collapse open',), 'fields': ('archived',)}),
        (u'Options', {'classes': ('collapse open',), 'fields': ('template', 'in_sitemap', 'active', 'display_attachs')}),
        (u'Attachements', {'fields': ('attached_files',)}),
    ]
    # Cache la partie Archivage si l'option pour la désactiver est utilisée
    fieldsets = [f for f in fieldsets if (f[0]!='Archivage' or WIKIPAGE_ENABLE_ARCHIVE)]

    #def get_form(self, request, obj=None, **kwargs):
        #if WIKIPAGE_PROTECTED_ADMIN:
            #self.fieldsets[3][1]['fields'] = tuple([item for item in self.fieldsets[3][1]['fields'] if item != 'active'])
        
        #return super(WikipageAdmin, self).get_form(request, obj, **kwargs)
    
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

    def changelist_view(self, request, extra_context=None):
        """
        Modifie le contexte de la vue de liste des objets
        
        Seulement les filtres implémentés par cette vue sont fonctionnelles. L'ordre 
        est toujours fixée sur l'ordre numérique des objets.
        """
        # Lecture "hardcoded" des paramètres
        is_popup = bool(request.GET.get('pop', 0))
        template_included = int(request.GET.get('template__included__exact', 0))
        # Requête de liste des objets ordonnée sur leur ordre numérique et prépare 
        # les objets à la construction de l'arborescence
        queryset = Wikipage.objects.all()
        if template_included and template_included>0:
            queryset = queryset.filter(template__included__exact=template_included)
        seq = [self.wikipage_object_for_tree(item, {'in_popup':is_popup}) for item in queryset.order_by('order')]
        
        # Calcule l'arborescence
        treeobject = TemplatedTree(seq=seq, order_key='order')
        treeobject.get_tree()

        context = {
            #'wikipages_list': Wikipage.objects.all().order_by('order'),
            'wikipages_rows': treeobject.render(recursed_template="admin/kiwi/wikipage/change_list_recursive_rows.html"),
        }
        context.update(extra_context or {})
        change_list = super(WikipageAdmin, self).changelist_view(request, context)

        return change_list
    
    def wikipage_object_for_tree(self, wikipage_object, extra_context={}):
        d = {
            'id': wikipage_object.id,
            'parent': wikipage_object.parent_id,
            'uri': wikipage_object.uri,
            'order': wikipage_object.order,
            'object': wikipage_object,
        }
        d.update(extra_context)
        return d
    
    #class Media:
        #css = {
            #"all": ("kiwi/foo.css",)
        #}

class VersionAdmin(admin.ModelAdmin):
    list_display = ('title', 'rev_number', 'wikipage', 'active', 'in_sitemap', 'date', 'author')
    list_filter = ('date', 'active', 'in_sitemap')
    ordering = ('title', 'rev_number')
    search_fields = ('title', 'text', 'template')
    raw_id_fields = ('wikipage', 'parent', 'author',)
    fieldsets = (
        (u'Paramètres', {'fields': ('wikipage','parent', 'order', 'uri', 'author')}),
        (u'Contenu', {'fields': ('title', 'text')}),
        (u'Options', {'fields': ('in_sitemap', 'active', 'template')}),
    )

#class ReleaseAdmin(admin.ModelAdmin):
    #list_display = ('title', 'rev_number', 'date')
    #list_filter = ('date',)
    #ordering = ('rev_number',)

admin.site.register(Attach, AttachAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Wikipage, WikipageAdmin)
if WIKIPAGE_ENABLE_ARCHIVE:
    admin.site.register(Version, VersionAdmin)
#admin.site.register(Release, ReleaseAdmin)
