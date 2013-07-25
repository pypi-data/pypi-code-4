from django.contrib import admin

from . import models


class StreamAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Stream, StreamAdmin)
