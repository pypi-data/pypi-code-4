__doc__ = """See https://docs.djangoproject.com/en/dev/ref/contrib/admin/"""

from django.contrib import admin
from django.conf import settings
from django.utils.importlib import import_module
import ptree.settings

class TreatmentAdmin(admin.ModelAdmin):
    readonly_fields = ('code', 'link')
    list_display = ('__unicode__', 'link')

    def link(self, instance):
        url = instance.start_url()
        return '<a href="{}" target="_blank">{}</a>'.format(url, instance.__unicode__())

    link.short_description = "Click link to try this treatment in demo mode"
    link.allow_tags = True
    
class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('code', 'link',)
    list_display = readonly_fields + ('has_visited',)

    def link(self, instance):
        url = instance.start_url()
        return '<a href="{}" target="_blank">{}</a>'.format(url, url)

    link.short_description = "Give this link to a single user"
    link.allow_tags = True

class MatchAdmin(admin.ModelAdmin):
    readonly_fields = []
    list_display = readonly_fields + [f.name for f in Match._meta.fields]

for game_label in ptree.settings.get_ptree_experiment_apps(settings.USER_PTREE_EXPERIMENT_APPS):
    module = import_module("{}.models".format(game_label))
    admin.site.register(module.Experiment)
    admin.site.register(module.Treatment, TreatmentAdmin)
    admin.site.register(module.Participant, ParticipantAdmin)

