from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy as reverse
from radpress import settings as radpress_settings
from radpress.models import Article, Tag


class ArticleFeed(Feed):
    def __init__(self):
        self.title = radpress_settings.TITLE
        self.description = radpress_settings.DESCRIPTION
        self.link = reverse('radpress-article-list')

    def get_object(self, request, tags=None):
        objects = Article.objects.filter(is_published=True)

        if tags:
            tag_list = []
            for name in tags.split('/'):
                try:
                    tag = Tag.objects.get(name=name)
                    tag_list.append(tag)
                except Tag.DoesNotExist:
                    pass

            objects = objects.filter(tags__in=tag_list).distinct()

        return objects

    def items(self, obj):
        return obj

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_author_email(self, item):
        if radpress_settings.HIDE_EMAIL:
            email = None

        else:
            email = item.author.email

        return email

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_at

    def item_description(self, item):
        return item.content_body
