# coding: utf-8
from django.contrib import admin
from search_statistic.forms import SearchQueryForm, VisitForm
from search_statistic.models import SearchQuery, Visit


class SearchQueryAdmin(admin.ModelAdmin):

    search_fields = ['query']
    list_display = ('query', 'confirm', 'visits')
    form = SearchQueryForm

    def has_add_permission(self, request):
        return False


class VisitAdmin(admin.ModelAdmin):

    search_fields = ['query', 'url']
    list_display = ('__unicode__', 'amount', 'timestamp')
    form = VisitForm
    fields = ('query', 'path', 'search_engine', 'amount', 'visited_object')
    readonly_fields = ('visited_object',)

    def has_add_permission(self, request):
        return False


admin.site.register(SearchQuery, SearchQueryAdmin)
admin.site.register(Visit, VisitAdmin)