# encoding: utf-8
"""
Models for a Django weblog application.

"""
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.markup.templatetags import markup
from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import smart_str

from akismet import Akismet


from weblog import managers


class Category(models.Model):
    """
    A Category a blog enty can belong to. Categories can be organized in a
    hierarchical way.

    # Create some categories
    >>> p1 = Category(name='P1')
    >>> p1.save()
    >>> c1 = p1.subcategories.create(name='C1')

    # Check some attributes
    >>> c1.parent_count
    1
    >>> c1.path_items
    [<Category: P1>, <Category: C1>]
    >>> c1.path
    u'p1/c1/'

    # Children are automatically updateded
    >>> p1.slug = 'foo'
    >>> p1.save()
    >>> c1 = p1.subcategories.all()[0]
    >>> c1.path
    u'foo/c1/'

    # A category cannot be its own parent oder grandparent
    >>> p1.parent = p1
    >>> p1.save()
    Traceback (most recent call last):
        ...
    ValueError: P1 may not be its own parent.

    >>> c1.parent = p1
    >>> c1.save()
    >>> p1.parent = c1
    >>> p1.save()
    Traceback (most recent call last):
        ...
    ValueError: P1 may not be its own parent.

    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,
            help_text=u'Used in the URL for the category. Must be unique.')
    parent = models.ForeignKey('self', blank=True, null=True,
            related_name='subcategories')
    description = models.TextField(blank=True,
            help_text=u'A short description of the category.')
    path = models.CharField(max_length=255, blank=True, editable=False,
            unique=True,
            help_text=u'A path to the category made /-separated slugs.')
    form_display_name = models.CharField(max_length=255, blank=True,
            editable=False,
            help_text=u'The label for this category in drop downs.')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['path']
        unique_together = (('parent', 'name'),)

    def __unicode__(self):
        return self.name

    @property
    def parent_count(self):
        """Get the number of parent categories."""
        count = 0
        current = self
        while current.parent:
            count += 1
            current = current.parent
            if current == self:
                raise RuntimeError(u'Circular reference in %s’s path.' % self)
        return count

    @property
    def path_items(self):
        """Get a list with with all categories in this category’s path."""
        items = [self]
        current = self
        while current.parent:
            items.insert(0, current.parent)
            current = current.parent
            if current == self:
                raise RuntimeError(u'Circular reference in %s’s path.' % self)
        return items

    def _create_path(self):
        """Create a path from all slugs separated by /."""
        if not self.parent:
            return self.slug + u'/'
        return self.parent.path + self.slug + u'/'

    def _create_form_display_name(self):
        """Prepend as many dashes to the cat name, as it has parents."""
        if not self.parent:
            return self.name
        return u'–' * self.parent_count + u' ' + self.name

    def save(self, *args, **kwargs):
        """
        Create path and then save the category. If the path has been updated,
        update any child categories to reflect the new path.

        """
        try:
            if self.parent and (
                    self.parent == self or self in self.parent.path_items):
                self.parent = None
                raise ValueError(u'%s may not be its own parent.' % self)
        except RuntimeError:
            self.parent = None
            raise ValueError(u'%s may not be its own parent.' % self)
        if not self.slug:
            from django.template.defaultfilters import slugify
            self.slug = slugify(self.name)

        old_path = self.path
        self.path = self._create_path()
        self.form_display_name = self._create_form_display_name()
        super(Category, self).save(*args, **kwargs)

        if self.path != old_path:
            for child in self.subcategories.all():
                child.save()

    @models.permalink
    def get_absolute_url(self):
        return ('weblog_category_detail', (), {'path': self.path})


class Post(models.Model):
    """
    A blog post. Posts can be grouped by (hierarchical) categories.

    # Create some posts:
    >>> c = Category(name='spam')
    >>> c.save()
    >>> p1 = Post(title='1', slug='1', body='1', status=Post.STATUS_PUBLISHED,
    ...         pub_date=datetime.datetime(2009, 10, 6), author_id=1)
    >>> p1.save()
    >>> p1.categories.add(c)
    >>> p2 = Post(title='2', slug='2', body='2', status=Post.STATUS_DRAFT,
    ...         pub_date=datetime.datetime(2009, 11, 7), author_id=1)
    >>> p2.save()

    # Some basics:
    >>> p1
    <Post: 1>
    >>> p1.title, p1.slug, p1.body, p1.status
    ('1', '1', '1', 'p')
    >>> p1.year, p1.month, p1.day
    ('2009', '10', '06')

    # Get post counts:
    >>> Post.count.by_year(2008)
    0
    >>> Post.count.by_year('2009')
    1
    >>> Post.count.by_month(2009, 10)
    1
    >>> Post.count.by_month('200912')
    0
    >>> Post.count.by_category(c)
    1
    >>> Post.count.by_category(None)
    0

    """
    STATUS_DRAFT = 'd'
    STATUS_PUBLISHED = 'p'
    STATUS_WITHDRAWN = 'w'
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique_for_date='pub_date',
            help_text=u'Used in the URL for this post. Must be unique.')
    author = models.ForeignKey(User, editable=False)
    pub_date = models.DateTimeField(u'Date posted',
            default=datetime.datetime.now)
    modify_date = models.DateTimeField(u'Modified', auto_now=True)

    body = models.TextField()
    body_html = models.TextField(editable=False, blank=True)
    categories = models.ManyToManyField('Category', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
            default=STATUS_CHOICES[0][0])
    enable_comments = models.BooleanField(default=True)

    objects = models.Manager()
    published = managers.PostManager()
    count = managers.PostCountManager()

    class Meta:
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.title

    @property
    def year(self):
        return self.pub_date.strftime('%Y')

    @property
    def month(self):
        return self.pub_date.strftime('%m')

    @property
    def day(self):
        return self.pub_date.strftime('%d')

    def save(self, *args, **kwargs):
        """Process the markup in `body` and store the html in `body_html`."""
        self.body_html = markup.restructuredtext(self.body)
        super(Post, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('weblog_post_detail', (), {
                'year': self.year,
                'month': self.month,
                'day': self.day,
                'slug': self.slug,
        })

    def get_full_url(self):
        return 'http://%s%s' % (Site.objects.get_current().domain,
                self.get_absolute_url())


class PostModerator(CommentModerator):
    """
    The post moderator checks if comments are allowed for a posting and let’s
    Akismet check it for spam. If the comment will be posted, an email is
    sent.

    """
    email_notification = True
    enable_field = 'enable_comments'

    def moderate(self, comment, content_object, request):
        """Use Akismet to check if the comment is spam."""
        ak = Akismet(key=settings.AKISMET_API_KEY,
                blog_url='http://%s/' % Site.objects.get_current().domain)

        if ak.verify_key():
            data = {
                'user_ip': request.META.get('REMOTE_ADDR', ''),
                'user_agent': request.META.get('BLOG_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', ''),
                'comment_type': 'comment',
                'comment_author': smart_str(comment.user_name),
            }
            if ak.comment_check(smart_str(comment.comment), data=data,
                    build_data=True):
                return True

        return False


moderator.register(Post, PostModerator)
