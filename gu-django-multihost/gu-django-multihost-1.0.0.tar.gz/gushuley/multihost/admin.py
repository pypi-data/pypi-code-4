from gushuley.multihost.models import Site
from django.contrib import admin

class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'host_regexp', 'urls_module', 'order')
    list_display_links = list_display        

admin.site.register(Site, SiteAdmin)
