from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin

from .models import Autoblock


class AutoblockAdmin(PlaceholderAdmin):
    list_display = ('composite_id', 'site')
    list_filter = ('site',)
    search_fields = ['composite_id']

admin.site.register(Autoblock, AutoblockAdmin)
