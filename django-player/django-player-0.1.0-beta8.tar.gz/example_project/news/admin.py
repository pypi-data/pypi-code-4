from django.contrib import admin

from news.models import NewsItem, NewsCategory


class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(NewsCategory, NewsAdmin)
admin.site.register(NewsItem, NewsAdmin)
