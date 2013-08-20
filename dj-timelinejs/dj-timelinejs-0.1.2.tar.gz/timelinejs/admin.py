from django.contrib import admin
from .models import Timeline, TimelineItem

class TimelineItemInline(admin.StackedInline):
    model = TimelineItem
    extra = 3
    exclude = (
            '_headline',
            '_text',
            '_media',
            '_media_caption',
            '_media_credit',
            '_media_thumbnail',
            '_tag',
            )

class TimelineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
            TimelineItemInline,
            ]


admin.site.register(Timeline, TimelineAdmin)
