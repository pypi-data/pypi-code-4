from django.contrib import admin
from ci.models import CiProject, TestModule, TestRun, CiBranch, CommandGroup, \
    Command
# from danemco.core.widgets import TextAreaNoMce


class TestRunAdmin(admin.ModelAdmin):
    search_fields = ("name", "module")
    list_display = ("name", "branch", "module", "status")
    list_display_links = ("name",)
    list_filter = ("branch", "module", "status")


class CiProjectAdmin(admin.ModelAdmin):
    pass
#     def formfield_for_dbfield(self, db_field, **kwargs):
#         if db_field.name == "test_commands":
#             kwargs['widget'] = TextAreaNoMce
#         print db_field.name
#         return admin.ModelAdmin.formfield_for_dbfield(self, db_field, **kwargs)


class Command_Inline(admin.TabularInline):
    model = Command
    extra = 0


class CommandGroupAdmin(admin.ModelAdmin):
    inlines = [Command_Inline]


admin.site.register(CiBranch)
admin.site.register(CiProject, CiProjectAdmin)
admin.site.register(TestModule)
admin.site.register(CommandGroup, CommandGroupAdmin)
admin.site.register(TestRun, TestRunAdmin)
