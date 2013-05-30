from django.contrib import admin
from .models import *
from .forms import TextPostAdminForm

def publish(modeladmin, request, queryset):
    queryset.update(published=True)
publish.short_description = 'Publish selected posts'

def publish_to(modeladmin, request, queryset):
    to = max([qs.post_ptr for qs in queryset])
    Post.objects.filter(pk__lte=to.pk).update(published=True)
publish_to.short_description = 'Publish all posts up selected post'


class PostAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    actions = (publish, publish_to)
    list_display = ('__unicode__', 'published')
    prepopulated_fields = {'slug': ('title',),}


class TextPostAdmin(PostAdmin):
    form = TextPostAdminForm


admin.site.register(Tag)
admin.site.register(ImagePost, PostAdmin)
admin.site.register(TextPost, TextPostAdmin)
