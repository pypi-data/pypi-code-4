from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.admin import SimpleListFilter

from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper

from django.db.models import get_model

from django.shortcuts import render

from quiz import models

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'points',)
admin.site.register(models.Quiz, QuizAdmin)

class AnswerInline(admin.TabularInline):
    model = models.Answer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'quiz', 'group', 'choices',)
    list_filter = ('quiz',)
    inlines = (
        AnswerInline,
    )
    def choices(self, obj):
        return obj.answer_set.count()

admin.site.register(models.Question, QuestionAdmin)

class ResponseInline(admin.StackedInline):
    model = models.Response
    readonly_fields = ('question',)
    fieldsets = (
        (None, {
            'fields': ('question', 'choice',),
        }),
    )
    extra = 0

class StudentFilter(SimpleListFilter):
    title = 'Student'
    parameter_name = 'student__id__exact'

    def lookups(self, request, model_admin):
        return get_model('auth', 'User').objects.order_by('username').values_list('id', 'username')

    def queryset(self, request, queryset):
        value = self.value()
        return queryset.filter(student__pk=value)

class SittingAdmin(admin.ModelAdmin):
    list_display = ('date_sat', 'student', 'quiz', 'score', 'out_of',)
    list_filter = ('quiz', StudentFilter)
    date_heirarchy = 'date_sat'
    inlines = (
        ResponseInline,
    )
    def out_of(self, obj):
        return obj.quiz.points()

    # View/Print results view
    def get_urls(self):
        urlpatterns = super(SittingAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'(\d+)/change/$',
                wrap(self.change_view),
                name='%s_%s_change' % info
            ),
            url(r'(\d+)/$',
                wrap(self.print_view),
                name='%s_%s_print' % info
            ),
        ) + urlpatterns
        return urlpatterns

    def print_view(self, request, object_id, extra_context=None):

        obj = self.get_object(request, unquote(object_id))

        context = {
            'object': obj,
        }
        context.update(extra_context or {})

        return render(request, 'admin/quiz/sitting/print_view.html', context,
            current_app=self.admin_site.name,
        )

admin.site.register(models.Sitting, SittingAdmin)
