from django.contrib import admin

from models import PublicHoliday
from forms import PublicHolidayAdminForm
import simplejson as json

def provinces(obj):
    if not obj.provinces:
        return ""
    return ", ".join(obj.provinces)
provinces.short_description = 'States/Provinces'
provinces.admin_order_field = 'provinces'

class PublicHolidayAdmin(admin.ModelAdmin):
    form = PublicHolidayAdminForm
    date_hierarchy = 'date'
    list_display = ('name','country','date', provinces)
    search_fields = ('name', 'provinces', 'date')
    list_filter = ('country',)

admin.site.register(PublicHoliday, PublicHolidayAdmin)