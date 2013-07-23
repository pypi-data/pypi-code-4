from django.contrib import admin
from sparkle.models import Application, Version, SystemProfileReport, SystemProfileReportRecord

class ApplicationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    
admin.site.register(Application, ApplicationAdmin)

class VersionAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'short_version', 'application', 'publish_date',)
    list_display_links = list_display
    list_filter = ('application', 'publish_date',)
    fieldsets = (
        (None, {'fields': ('application', 'title', 'release_notes', 'version', 'short_version', 'update', 'publish_date',)}),
        ('Details', {'fields': ('dsa_signature', 'length', 'minimum_system_version', 'created',), 'classes': ('collapse',)})
    )
    readonly_fields = ('created', )
    ordering = ('-publish_date', )

admin.site.register(Version, VersionAdmin)

class SystemProfileReportRecordInline(admin.TabularInline):
    model = SystemProfileReportRecord
    extra = 0
    max_num = 0
    readonly_fields = ('key', 'value')
    can_delete = False

class SystemProfileReportAdmin(admin.ModelAdmin):
    inlines = [SystemProfileReportRecordInline,]

admin.site.register(SystemProfileReport, SystemProfileReportAdmin)

class SystemProfileReportRecordAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    list_filter = ('key',)

admin.site.register(SystemProfileReportRecord, SystemProfileReportRecordAdmin)

