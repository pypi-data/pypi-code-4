from django.contrib import admin

from player.crawler.models import CrawlerCollection, Report


class CrawlerCollectionAdmin(admin.ModelAdmin):
    change_form_template = 'admin/crawler/collection_change_form.html'


admin.site.register(CrawlerCollection, CrawlerCollectionAdmin)
admin.site.register(Report)
