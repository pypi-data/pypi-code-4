from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from archer.packages.models import Package


class PackageAdmin(GuardedModelAdmin):
    list_display = ('project', 'file', 'status', 'created_at', 'updated_at')

admin.site.register(Package, admin_class=PackageAdmin)
