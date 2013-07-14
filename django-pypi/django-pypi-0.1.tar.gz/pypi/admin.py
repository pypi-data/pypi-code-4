from django.contrib import admin
from pypi.models import Release, Package, Version


class ReleaseAdmin(admin.ModelAdmin):
    readonly_fields = Release._meta.get_all_field_names()
    has_add_permission = lambda s, r: False
    has_delete_permission = lambda s, r, o = None: False

    list_display = ('version',
                    'python_version',
                    'packagetype',
                    'upload_time')
    date_hierarchy = 'upload_time'


class PackageAdmin(admin.ModelAdmin):
    readonly_fields = Package._meta.get_all_field_names()
    has_add_permission = lambda s, r: False
    has_delete_permission = lambda s, r, o = None: False

    list_display = ('name',)


class VersionAdmin(admin.ModelAdmin):
    readonly_fields = Version._meta.get_all_field_names()
    has_add_permission = lambda s, r: False
    has_delete_permission = lambda s, r, o = None: False

    list_display=('package', 'version')


admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Release, ReleaseAdmin)