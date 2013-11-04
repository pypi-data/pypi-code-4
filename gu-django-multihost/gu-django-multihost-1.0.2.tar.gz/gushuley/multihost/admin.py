from . import models, is_database_driven_modules_urls
from django.contrib import admin


class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'host_regexp', 'urls_module', 'order')
    list_display_links = list_display        

admin.site.register(models.Site, SiteAdmin)

if is_database_driven_modules_urls():
    from .models import ModuleUrls
    admin.site.register(ModuleUrls)