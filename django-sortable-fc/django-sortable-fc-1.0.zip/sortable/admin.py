from django.contrib import admin


class SortableAdmin(admin.ModelAdmin):
    # Make instances reorderable
    list_editable = ('weight',)
    list_display = ('weight', )

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js',
            'js/django-admin-sortable.js',)
