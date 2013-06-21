from django.contrib import admin
from pwutils.models import Measure


class MeasureAdmin(admin.ModelAdmin):
    model = Measure

admin.site.register(Measure, MeasureAdmin)
