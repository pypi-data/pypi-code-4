
from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin
from clippings.models import Clipping


class ClippingAdmin(PlaceholderAdmin):

    search_fields = ('identifier',)


admin.site.register(Clipping, ClippingAdmin)
