"""
Very simple book model, for test purposes.

A book has:

 * One or more authors, that can also be authors of other books (many-to-many)
 * One publisher (foreign key)
 * One or more chapters, that are always book specific (reverse foreign key)

"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Tag(models.Model):
    name = models.CharField(_("name"), max_length=40)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'


class Author(models.Model):
    name = models.CharField(_("name"), max_length=80)
    email = models.EmailField(_("email"), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'author'
        verbose_name_plural = 'authors'


class Publisher(models.Model):
    name = models.CharField(_("name"), max_length=80)
    email = models.EmailField(_("email"), blank=True)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'publisher'
        verbose_name_plural = 'publishers'


class PublisherLink(models.Model):
    publisher = models.ForeignKey(Publisher, related_name='links')
    url = models.URLField(_("url"))

    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = 'publisher link'
        verbose_name_plural = 'publisher links'


class Book(models.Model):
    title = models.CharField(_("title"), max_length=80)
    year = models.PositiveIntegerField(_("year"), null=True)
    summary = models.TextField(_("summary"), blank=True)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    tags = models.ManyToManyField(Tag)
    created = models.DateTimeField(_('created on'), auto_now_add=True)

    def __unicode__(self):
        return 'Book %s' % (self.id,)

    class Meta:
        verbose_name = 'book'
        verbose_name_plural = 'books'


class Chapter(models.Model):
    # FIXME: if related_name is not set, the right filter query is 'chapter'...
    book = models.ForeignKey(Book)#, related_name='chapter_set')
    title = models.CharField(_("title"), max_length=80)

    def __unicode__(self):
        return 'Chapter %s' % (self.id,)

    class Meta:
        verbose_name = 'chapter'
        verbose_name_plural = 'chapters'


class ExtraBookInfo(models.Model):
    # This is for testing OneToOneField
    book = models.OneToOneField(Book, related_name='extra_info')
    isbn = models.CharField(_("isbn"), max_length=80, blank=True)

    def __unicode__(self):
        return 'ExtraBookInfo %s' % (self.id,)

    class Meta:
        verbose_name = 'extra book info'
        verbose_name_plural = 'extra book info'


class Category(models.Model):
    # To create a reverse m2m relationship for testing
    name = models.CharField(_("name"), max_length=80)
    books = models.ManyToManyField(Book)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'



def create_test_books():
    jeff = Author.objects.create(name=u"Jeff Potter")
    oreilly = Publisher.objects.create(
        name=u"O'Reilly",
        email='orders@oreilly.com',
    )
    PublisherLink.objects.create(publisher=oreilly, url='http://oreilly.com/')
    cooking_for_geeks = Book.objects.create(
        title=u"Cooking for Geeks",
        publisher=oreilly,
        year=2010
    )
    cooking_for_geeks.authors = [jeff]
    cooking_for_geeks.tags = [
        Tag.objects.get_or_create(name="cooking")[0],
        Tag.objects.get_or_create(name="geeks")[0],
        Tag.objects.get_or_create(name="technology")[0],
    ]
    ExtraBookInfo.objects.create(book=cooking_for_geeks, isbn='978-0-596-80588-3')
    chapters = [
        u"Hello, Kitchen!",
        u"Initializing the Kitchen",
        u"Choosing Your Inputs: Flavors and Ingredients",
        u"Time and Temperature: Cooking's Primary Variables",
        u"Air: Baking's Key Variable",
        u"Playing with Chemicals",
        u"Fun with Hardware"
    ]
    for title in chapters:
        Chapter.objects.create(book=cooking_for_geeks, title=title)
    oreilly.tags = [Tag.objects.get_or_create(name="technology")[0]]

    kristina = Author.objects.create(name=u"Kristina Chodorow")
    michael = Author.objects.create(name=u"Michael Dirolf")
    mongodb = Book.objects.create(
        title=u"MongoDB: The Definitive Guide",
        publisher=oreilly,
        year=2010
    )
    mongodb.authors = [kristina, michael]
    mongodb.tags = [
        Tag.objects.get_or_create(name="mongodb")[0],
        Tag.objects.get_or_create(name="databases")[0],
        Tag.objects.get_or_create(name="technology")[0],
    ]
    ExtraBookInfo.objects.create(book=mongodb, isbn='978-1-4493-4468-9')
    chapters = [u"Introduction", u"Getting Started", u"Querying"]
    for title in chapters:
        Chapter.objects.create(book=mongodb, title=title)

    tech = Category.objects.create(name=u"Technology")
    tech.books.add(cooking_for_geeks)
    tech.books.add(mongodb)

