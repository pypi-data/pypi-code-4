
from unittest import TestCase
from mock import patch, DEFAULT, Mock, MagicMock, call

from rattail.db import changes
from rattail.db.model import Change, Batch, BatchColumn, BatchRow, Role, UserRole, Product
from sqlalchemy.orm import RelationshipProperty


class TestChanges(TestCase):

    @patch.multiple('rattail.db.changes', listen=DEFAULT, ChangeRecorder=DEFAULT)
    def test_record_changes(self, listen, ChangeRecorder):
        session = Mock()
        ChangeRecorder.return_value = 'whatever'

        changes.record_changes(session)
        ChangeRecorder.assert_called_once_with(True)
        listen.assert_called_once_with(session, 'before_flush', 'whatever')

        ChangeRecorder.reset_mock()
        listen.reset_mock()
        changes.record_changes(session, ignore_role_changes=False)
        ChangeRecorder.assert_called_once_with(False)
        listen.assert_called_once_with(session, 'before_flush', 'whatever')


class TestChangeRecorder(TestCase):

    def test_init(self):
        recorder = changes.ChangeRecorder()
        self.assertTrue(recorder.ignore_role_changes)
        recorder = changes.ChangeRecorder(False)
        self.assertFalse(recorder.ignore_role_changes)

    def test_call(self):
        recorder = changes.ChangeRecorder()
        recorder.record_change = Mock()

        session = MagicMock()
        session.deleted.__iter__.return_value = ['deleted_instance']
        session.new.__iter__.return_value = ['new_instance']
        session.dirty.__iter__.return_value = ['dirty_instance']
        session.is_modified.return_value = True

        recorder(session, Mock(), Mock())
        self.assertEqual(recorder.record_change.call_count, 3)
        recorder.record_change.assert_has_calls([
                call(session, 'deleted_instance', deleted=True),
                call(session, 'new_instance'),
                call(session, 'dirty_instance'),
                ])

    def test_record_change(self):
        session = Mock()
        recorder = changes.ChangeRecorder()
        recorder.ensure_uuid = Mock()

        # don't record changes for changes
        self.assertFalse(recorder.record_change(session, Change()))

        # don't record changes for batch data
        self.assertFalse(recorder.record_change(session, Batch()))
        self.assertFalse(recorder.record_change(session, BatchColumn()))
        self.assertFalse(recorder.record_change(session, BatchRow()))

        # don't record changes for objects with no uuid attribute
        self.assertFalse(recorder.record_change(session, object()))

        # don't record changes for role data if so configured
        recorder.ignore_role_changes = True
        self.assertFalse(recorder.record_change(session, Role()))
        self.assertFalse(recorder.record_change(session, UserRole()))

        # none of the above should have involved a call to `ensure_uuid()`
        self.assertFalse(recorder.ensure_uuid.called)

        # make sure role data is *not* ignored if so configured
        recorder.ignore_role_changes = False
        self.assertTrue(recorder.record_change(session, Role()))
        self.assertTrue(recorder.record_change(session, UserRole()))

        # so far no *new* changes have been created
        self.assertFalse(session.add.called)

        # mock up session to force new change creation
        session.query.return_value = session
        session.get.return_value = None
        with patch('rattail.db.changes.Change') as MockChange:
            new_change = Mock()
            MockChange.return_value = new_change
            self.assertTrue(recorder.record_change(session, Product()))
            session.add.assert_called_once_with(new_change)

    @patch.multiple('rattail.db.changes', get_uuid=DEFAULT, object_mapper=DEFAULT)
    def test_ensure_uuid(self, get_uuid, object_mapper):
        recorder = changes.ChangeRecorder()
        uuid_column = Mock()
        object_mapper.return_value.columns.__getitem__.return_value = uuid_column

        # uuid already present
        product = Product(uuid='some_uuid')
        recorder.ensure_uuid(product)
        self.assertEqual(product.uuid, 'some_uuid')
        self.assertFalse(get_uuid.called)

        # no uuid yet, auto-generate
        uuid_column.foreign_keys = False
        get_uuid.return_value = 'another_uuid'
        product = Product()
        self.assertIsNone(product.uuid)
        recorder.ensure_uuid(product)
        get_uuid.assert_called_once_with()
        self.assertEqual(product.uuid, 'another_uuid')

        # some heavy mocking for following tests
        uuid_column.foreign_keys = True
        remote_side = MagicMock(key='uuid')
        prop = MagicMock(__class__=RelationshipProperty, key='foreign_thing')
        prop.remote_side.__len__.return_value = 1
        prop.remote_side.__iter__.return_value = [remote_side]
        object_mapper.return_value.iterate_properties.__iter__.return_value = [prop]
        
        # uuid fetched from existing foreign key object
        get_uuid.reset_mock()
        instance = Mock(uuid=None, foreign_thing=Mock(uuid='secondary_uuid'))
        recorder.ensure_uuid(instance)
        self.assertFalse(get_uuid.called)
        self.assertEqual(instance.uuid, 'secondary_uuid')

        # foreign key object doesn't exist; uuid generated as fallback
        get_uuid.return_value = 'fallback_uuid'
        instance = Mock(uuid=None, foreign_thing=None)
        recorder.ensure_uuid(instance)
        get_uuid.assert_called_once_with()
        self.assertEqual(instance.uuid, 'fallback_uuid')
