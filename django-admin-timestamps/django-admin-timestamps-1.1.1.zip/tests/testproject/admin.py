from django.contrib import admin
from models import (TimestampedItem, FakeTimestampedItem,
                    AlternativeTimestampedItem, SingleTimestampedItem,
                    DateStampedItem, NullTimestampedItem)
from admintimestamps import TimestampedAdminMixin


class TimestampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(TimestampedItem, TimestampedAdmin)
admin.site.register(FakeTimestampedItem, TimestampedAdmin)
admin.site.register(DateStampedItem, TimestampedAdmin)
admin.site.register(NullTimestampedItem, TimestampedAdmin)


class SingleTimestampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    timestamp_fields = ('modified',)

admin.site.register(SingleTimestampedItem, SingleTimestampedAdmin)


class AlternativeTimestampedAdmin(TimestampedAdmin):
    timestamp_fields = ('created_at', 'modified_at')

admin.site.register(AlternativeTimestampedItem, AlternativeTimestampedAdmin)
