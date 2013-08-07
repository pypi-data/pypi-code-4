from django.contrib import admin
from ci.models import CiProject, TestModule, TestRun
from danemco.core.widgets import TextAreaNoMce


class TestRunAdmin(admin.ModelAdmin):
    search_fields = ("name", "module")
    list_display = ("name", "project", "module", "status")
    list_display_links = ("name",)
    list_filter = ("project", "module", "status")


class CiProjectAdmin(admin.ModelAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "test_commands":
            kwargs['widget'] = TextAreaNoMce
        print db_field.name
        return admin.ModelAdmin.formfield_for_dbfield(self, db_field, **kwargs)


admin.site.register(CiProject, CiProjectAdmin)
admin.site.register(TestModule)
admin.site.register(TestRun, TestRunAdmin)
