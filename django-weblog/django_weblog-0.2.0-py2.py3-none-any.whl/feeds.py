# encoding: utf-8
"""
News feeds for the weblog app.

"""
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed

from weblog.models import Category, Post


class BaseFeed(Feed):
    feed_type = Atom1Feed
    title = Site.objects.get_current().name
    title_template = 'feeds/post_title.html'
    description_template = 'feeds/post_description.html'

    def item_pubdate(self, item):
        return item.modify_date


class LatestPosts(BaseFeed):
    """Atom feed for the 10 latest posts."""

    link = '/'

    def items(self):
        return Post.published.all()[:10]


class CategoryPosts(BaseFeed):
    """All posts in a category."""

    def get_object(self, request, path):
        # if len(bits) == 0:
        #     raise ObjectDoesNotExist

        # path = '/'.join(bits) + '/'
        return Category.objects.get(path__exact=path)

    def title(self, category):
        return super(CategoryPosts, self).title + (u' » Category » ' +
                category.name)

    def subtitle(self, category):
        return u'Posts in category «%s»' % category.name

    def link(self, category):
        if not category:
            raise FeedDoesNotExist
        return category.get_absolute_url()

    def items(self, category):
        return Post.published.in_category(category)


class PostComments(BaseFeed):
    """All comments for a post."""
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def get_object(self, request, year, month, day, slug):
        # if len(bits) != 4:
        #     raise ObjectDoesNotExist
        # try:
        #     year, month, day = map(int, bits[0:3])
        #     slug = bits[3]
        # except ValueError:
        #     raise ObjectDoesNotExist
        return Post.published.by_date_and_slug(int(year), int(month), int(day),
                                               slug)

    def title(self, post):
        return super(PostComments, self).title + (u' » Comments » ' +
                post.title)

    def subtitle(self, post):
        return u'Comments for post «%s»' % post.title

    def link(self, post):
        if not post:
            raise FeedDoesNotExist
        return post.get_absolute_url()

    def items(self, post):
        return Comment.objects.for_model(post).filter(is_public=True,
                is_removed=False).order_by('-submit_date')

    def item_pubdate(self, item):
        return item.submit_date
