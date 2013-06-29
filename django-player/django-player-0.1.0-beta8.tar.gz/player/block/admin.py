from django.contrib import admin

from player.block.forms import PlacedBlockForm
from player.block.models import PlacedBlock


class PlacedBlockAdmin(admin.ModelAdmin):
    form = PlacedBlockForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(PlacedBlockAdmin, self).get_form(request, obj,
                                                      **kwargs)

        return form


admin.site.register(PlacedBlock, PlacedBlockAdmin)
