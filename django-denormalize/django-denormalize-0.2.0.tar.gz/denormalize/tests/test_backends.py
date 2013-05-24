from pprint import pprint
import os

from django.conf import settings

from ..models import *
from ..backend.locmem import LocMemBackend
from ..context import delay_sync, sync_together

from .common import ModelTestCase
from .models import *
from .test_collections import BookCollection


class BackendTest(ModelTestCase):

    SUPPORTS_SYNC_COLLECTION = True

    def _create_backend(self):
        return LocMemBackend()

    def test_dump(self):
        bookcol = BookCollection()
        backend = self._create_backend()
        backend.register(bookcol)
        with sync_together():
            create_test_books()

        # Test data
        doc = backend.get_doc(bookcol, 1)
        self.assertEqual(doc['id'], 1)
        self.assertTrue('chapter_set' in doc, doc)
        self.assertTrue('extra_info' in doc, doc)
        self.assertTrue('tags' in doc, doc)

        # Change a one to many link
        chapter = Chapter.objects.get(id=1)
        chapter.title += u'!!!'
        chapter.save()
        doc = backend.get_doc(bookcol, 1)
        chapter = doc['chapter_set'][0]
        self.assertTrue(chapter['id'] == 1)
        self.assertTrue(chapter['title'].endswith('!!!'), doc)

        # Change something (m2m)
        author = Author.objects.get(id=1)
        author.name = 'Another Name'
        author.email = 'foo@example.com'
        author.save()
        doc = backend.get_doc(bookcol, 1)
        self.assertEqual(doc['authors'][0]['name'], author.name)

        # Change something that's shared (m2m)
        tag = Tag.objects.get(name="technology")
        tag.name = "tech"
        tag.save()
        doc = backend.get_doc(bookcol, 1)
        self.assertTrue('tech' in doc['tags'])

        # Add a chapter to a book
        book1 = Book.objects.get(id=1)
        chapter = Chapter.objects.create(book=book1, title="Conclusion")
        doc = backend.get_doc(bookcol, 1)
        self.assertTrue("Conclusion" in (x['title'] for x in doc['chapter_set']))

        # Move a chapter to another book (FK change!)
        book2 = Book.objects.get(id=2)
        chapter.book = book2
        chapter.save()
        doc = backend.get_doc(bookcol, 1)
        self.assertFalse("Conclusion" in (x['title'] for x in doc['chapter_set']))
        doc = backend.get_doc(bookcol, 2)
        self.assertTrue("Conclusion" in (x['title'] for x in doc['chapter_set']))

        # Delete the chapter
        chapter.delete()
        doc = backend.get_doc(bookcol, 2)
        self.assertFalse("Conclusion" in (x['title'] for x in doc['chapter_set']))

        # Add a tag (m2m updated!!!) FIXME: not supported yet
        tag = Tag.objects.create(name="foo")
        book2.tags = []
        book2.tags.add(tag)
        # Remove the tag from the book from the other side (reverse=True)
        tag = Tag.objects.get(id=tag.id)
        tag.book_set.remove(book2)
        tag.book_set.add(book2)
        # 'clear' action
        tag.book_set = []
        book2.publisher.tags = [tag]

        if self.SUPPORTS_SYNC_COLLECTION:
            # TODO: This code is fairly LocMemBackend specific, we need a
            #       cleaner way of testing.

            # Finally, test syncing the collection. First without special events.
            backend.sync_collection(bookcol)

            # Next, with dirty records
            def inject_dirty():
                newbook = Book.objects.create(
                    title="Some title", publisher=book2.publisher)
                self.assertTrue(newbook.id in backend._dirty['books'])
                backend._dirty['books'].add(1)
            backend._sync_collection_before_handling_dirty = inject_dirty
            backend.sync_collection(bookcol)

            # Check that we ended up with a new book, even though it was added
            # during the full sync.
            self.assertEqual(len(backend.data['books']), 3)


# The MongoDB database to use for tests (required)
TEST_MONGO_DB = getattr(settings, 'DENORMALIZE_TEST_MONGO_DB', None)
# Optional, defaults to localhost
TEST_MONGO_URI = getattr(settings, 'DENORMALIZE_TEST_MONGO_URI', None)

if TEST_MONGO_DB:
    from ..backend.mongodb import MongoBackend

    class MongoBackendTest(BackendTest):
        SUPPORTS_SYNC_COLLECTION = False # FIXME
        def _create_backend(self):
            return MongoBackend(db_name=TEST_MONGO_DB, connection_uri=TEST_MONGO_URI)

else:
    print "WARNING: skipping MongoDB backend test, because " \
        "settings.DENORMALIZE_TEST_MONGO_DB is not set!"
