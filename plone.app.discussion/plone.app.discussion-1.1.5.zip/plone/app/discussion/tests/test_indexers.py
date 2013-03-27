"""Test for the plone.app.discussion indexers
"""

import unittest

from datetime import datetime
from DateTime import DateTime

from zope.component import createObject

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IConversation

from plone.indexer.delegate import DelegatingIndexerFactory

from plone.app.discussion import catalog

LONG_TEXT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit
amet."""

LONG_TEXT_CUT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At [...]"""


class ConversationIndexersTest(PloneTestCase):
    """Conversation Indexer Tests
    """

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='doc1',
                  title='Document 1',
                  type_name='Document')

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment Text'
        comment1.creator = "Jim"
        comment1.author_username = "Jim"
        comment1.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment1.modification_date = datetime(2006, 9, 17, 14, 18, 12)
        self.new_id1 = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment Text'
        comment2.creator = "Emma"
        comment2.author_username = "Emma"
        comment2.creation_date = datetime(2007, 12, 13, 4, 18, 12)
        comment2.modification_date = datetime(2007, 12, 13, 4, 18, 12)
        self.new_id2 = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.text = 'Comment Text'
        comment3.creator = "Lukas"
        comment3.author_username = "Lukas"
        comment3.creation_date = datetime(2009, 4, 12, 11, 12, 12)
        comment3.modification_date = datetime(2009, 4, 12, 11, 12, 12)
        self.new_id3 = conversation.addComment(comment3)

        self.conversation = conversation

    def test_conversation_total_comments(self):
        self.assert_(isinstance(catalog.total_comments,
                                DelegatingIndexerFactory))
        self.assertEquals(catalog.total_comments(self.portal.doc1)(), 3)
        del self.conversation[self.new_id1]
        self.assertEquals(catalog.total_comments(self.portal.doc1)(), 2)
        del self.conversation[self.new_id2]
        del self.conversation[self.new_id3]
        self.assertEquals(catalog.total_comments(self.portal.doc1)(), 0)

    def test_conversation_last_comment_date(self):
        self.assert_(isinstance(catalog.last_comment_date,
                                DelegatingIndexerFactory))
        self.assertEquals(catalog.last_comment_date(self.portal.doc1)(),
                          datetime(2009, 4, 12, 11, 12, 12))
        del self.conversation[self.new_id3]
        self.assertEquals(catalog.last_comment_date(self.portal.doc1)(),
                          datetime(2007, 12, 13, 4, 18, 12))
        del self.conversation[self.new_id2]
        del self.conversation[self.new_id1]
        self.assertEquals(catalog.last_comment_date(self.portal.doc1)(), None)

    def test_conversation_commentators(self):
        pass
        #self.assertEquals(catalog.commentators(self.portal.doc1)(),
        #                  ('Jim', 'Emma', 'Lukas'))
        #self.assert_(isinstance(catalog.commentators,
        #                        DelegatingIndexerFactory))


class CommentIndexersTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='doc1',
                          title='Document 1',
                          type_name='Document')

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the
        # factory to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.text = 'Lorem ipsum dolor sit amet.'
        comment.creator = "Jim"
        comment.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment.modification_date = datetime(2008, 3, 12, 7, 32, 52)

        self.comment_id = conversation.addComment(comment)
        self.comment = comment.__of__(conversation)
        self.conversation = conversation

    def test_title(self):
        self.assertEquals(catalog.title(self.comment)(), 'Jim on Document 1')
        self.assert_(isinstance(catalog.title, DelegatingIndexerFactory))

    def test_description(self):
        self.assertEquals(catalog.description(self.comment)(),
                          'Lorem ipsum dolor sit amet.')
        self.assert_(isinstance(catalog.description, DelegatingIndexerFactory))

    def test_description_long(self):
        # Create a 50 word comment and make sure the description returns
        # only the first 25 words
        comment_long = createObject('plone.Comment')
        comment_long.title = 'Long Comment'
        comment_long.text = LONG_TEXT

        self.conversation.addComment(comment_long)
        self.assertEquals(catalog.description(comment_long)(),
                          LONG_TEXT_CUT.replace("\n", " "))

    def test_dates(self):
        # Test if created, modified, effective etc. are set correctly
        self.assertEquals(catalog.created(self.comment)(),
                          DateTime(2006, 9, 17, 14, 18, 12))
        self.assertEquals(catalog.effective(self.comment)(),
                          DateTime(2006, 9, 17, 14, 18, 12))
        self.assertEquals(catalog.modified(self.comment)(),
                          DateTime(2008, 3, 12, 7, 32, 52))

    def test_searchable_text(self):
        # Test if searchable text is a concatenation of title and comment text
        self.assertEquals(catalog.searchable_text(self.comment)(),
                          ('Lorem ipsum dolor sit amet.'))
        self.assert_(isinstance(catalog.searchable_text,
                                DelegatingIndexerFactory))

    def test_creator(self):
        self.assertEquals(catalog.creator(self.comment)(), ('Jim'))

    def test_in_response_to(self):
        # make sure in_response_to returns the title or id of the content
        # object the comment was added to
        self.assertEquals(catalog.in_response_to(self.comment)(), 'Document 1')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
