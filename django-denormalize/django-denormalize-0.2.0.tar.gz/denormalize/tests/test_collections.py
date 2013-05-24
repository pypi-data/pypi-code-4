from pprint import pprint
import os

from ..models import *
from .common import ModelTestCase
from .models import *

# TODO: check if the SQL queries are efficient (all data should be fetched in one query)

class BookCollection(DocumentCollection):
    model = Book
    name = "books"
    select_related = ['publisher', 'extra_info']
    prefetch_related = ['chapter_set', 'authors', 'tags', 'publisher__links',
        'category_set', 'publisher__tags']
    exclude = ['authors__email', 'summary']
    add_model_name = True

    def dump_obj(self, model, obj, path):
        # Customization: for tags, use the name string as the representation
        if model is Tag:
            return obj.name
        # Here only the url
        if model is PublisherLink:
            return obj.url
        return super(BookCollection, self).dump_obj(model, obj, path)


class CollectionTest(ModelTestCase):

    def setUp(self):
        create_test_books()
        #book = Book.objects.get(title=u"Cooking for Geeks")
        #m = book._meta
        #import code; _d = dict(); _d.update(globals()); _d.update(locals()); code.interact(local=_d)

    def test_dump(self):
        bookcol = BookCollection()
        book = Book.objects.get(title=u"Cooking for Geeks")
        doc = bookcol.dump(book)

        # Basic fields
        self.assertTrue('id' in doc)
        self.assertTrue('title' in doc)
        self.assertFalse('summary' in doc, "The summary was not excluded")
        self.assertTrue('year' in doc)
        self.assertTrue('created' in doc)
        self.assertEqual(doc['id'], book.id)

        # Relational fields
        self.assertTrue('publisher' in doc, doc)
        self.assertEqual(doc['publisher']['name'], u"O'Reilly")
        self.assertTrue('authors' in doc, doc)
        self.assertEqual(len(doc['authors']), 1)
        self.assertTrue('chapter_set' in doc, doc)
        self.assertEqual(len(doc['chapter_set']), 7)

        # Other expectations

        # - Tags are pure strings
        self.assertEqual(doc['tags'], [u'cooking', u'geeks', u'technology'])

        # - ForeignKeys not explicitly followed are included as a pure id
        chapter = doc['chapter_set'][0]
        # TODO: we should probably omit it if it's the relation we just followed
        self.assertTrue('book_id' in chapter,
            "If a FK is not followed, its id will be included")

        # - Author emails are excluded
        author = doc['authors'][0]
        self.assertFalse('email' in author, "The author email was not excluded")


    def test_dump_collection(self):
        bookcol = BookCollection()
        docs = list(bookcol.dump_collection())
        self.assertEqual(len(docs), 2)
        if 'pprint' in os.environ:
            pprint(docs)

    def test_get_related_models(self):
        bookcol = BookCollection()
        deps = bookcol.get_related_models()
        for rel in bookcol.select_related + bookcol.prefetch_related:
            # Difference between the filter name and the path name
            if rel == 'chapter_set':
                rel = 'chapter'
            elif rel == 'category_set':
                rel = 'category'
            self.assertTrue(rel in deps, "Relation {0} not found!".format(rel))
        pprint(deps)
        self.assertIs(deps['publisher']['model'], Publisher)
        self.assertIs(deps['extra_info']['model'], ExtraBookInfo)
        self.assertIs(deps['chapter']['model'], Chapter)
        self.assertIs(deps['authors']['model'], Author)
        self.assertIs(deps['tags']['model'], Tag)
        self.assertIs(deps['publisher__links']['model'], PublisherLink)




