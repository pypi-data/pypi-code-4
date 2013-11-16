
import warnings
from unittest import TestCase
from mock import patch, call, Mock, DEFAULT

from sqlalchemy.exc import OperationalError, SAWarning

from . import SyncTestCase
from rattail.db import sync
from rattail.db import Session
from rattail.db import model


class SynchronizerTests(SyncTestCase):

    def test_init(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)
        self.assertIs(synchronizer.local_engine, self.local_engine)
        self.assertIs(synchronizer.remote_engines, self.remote_engines)

    def test_loop(self):

        class FakeOperationalError(OperationalError):
            def __init__(self, connection_invalidated):
                self.connection_invalidated = connection_invalidated

        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)
        with patch.object(synchronizer, 'sleep') as sleep:
            with patch.object(synchronizer, 'synchronize') as synchronize:

                synchronize.side_effect = [1, 2, 3, FakeOperationalError(True),
                                                   5, 6, 7, FakeOperationalError(False)]
                self.assertRaises(FakeOperationalError, synchronizer.loop)
                self.assertEqual(synchronize.call_count, 8)
                self.assertEqual(sleep.call_args_list, [
                        call(3), call(3), call(3), call(5), call(3),
                        call(3), call(3), call(3)])

    def test_synchronize(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        with patch.object(synchronizer, 'synchronize_changes') as synchronize_changes:

            # no changes
            synchronizer.synchronize()
            self.assertFalse(synchronize_changes.called)

            # some changes
            local_session = Session(bind=self.local_engine)
            product = model.Product()
            local_session.add(product)
            local_session.flush()
            local_session.add(model.Change(class_name='Product', uuid=product.uuid, deleted=False))
            product = model.Product()
            local_session.add(product)
            local_session.flush()
            local_session.add(model.Change(class_name='Product', uuid=product.uuid, deleted=False))
            local_session.commit()
            synchronizer.synchronize()
            self.assertEqual(synchronize_changes.call_count, 1)
            # call_args is a tuple of (args, kwargs) - first element of args should be our 2 changes
            self.assertEqual(len(synchronize_changes.call_args[0][0]), 2)
            self.assertIsInstance(synchronize_changes.call_args[0][0][0], model.Change)

    def test_synchronize_changes(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        local_session = Session(bind=self.local_engine)
        remote_sessions = {
            'one': Session(bind=self.remote_engines['one']),
            'two': Session(bind=self.remote_engines['two']),
            }

        # no changes; nothing should happen but make sure nothing blows up also
        local_changes = []
        synchronizer.synchronize_changes(local_changes, local_session, remote_sessions)

        # add a product, with change
        product = model.Product()
        local_session.add(product)
        local_session.flush()
        change = model.Change(class_name='Product', uuid=product.uuid, deleted=False)
        local_session.add(change)
        local_session.flush()
        self.assertEqual(local_session.query(model.Product).count(), 1)
        self.assertEqual(local_session.query(model.Change).count(), 1)

        # remote sessions don't have the product yet
        self.assertEqual(remote_sessions['one'].query(model.Product).count(), 0)
        self.assertEqual(remote_sessions['two'].query(model.Product).count(), 0)

        # sync the change
        synchronizer.synchronize_changes([change], local_session, remote_sessions)
        self.assertEqual(local_session.query(model.Product).count(), 1)
        self.assertEqual(local_session.query(model.Change).count(), 0)

        # remote session 'one' has the product
        self.assertEqual(remote_sessions['one'].query(model.Product).count(), 1)
        remote_product_1 = remote_sessions['one'].query(model.Product).one()
        self.assertEqual(remote_product_1.uuid, product.uuid)

        # remote session 'two' has the product
        self.assertEqual(remote_sessions['two'].query(model.Product).count(), 1)
        remote_product_2 = remote_sessions['two'].query(model.Product).one()
        self.assertEqual(remote_product_2.uuid, product.uuid)

        # delete the product (new change)
        local_session.delete(product)
        change = model.Change(class_name='Product', uuid=product.uuid, deleted=True)
        local_session.add(change)
        local_session.flush()
        self.assertEqual(local_session.query(model.Product).count(), 0)
        self.assertEqual(local_session.query(model.Change).count(), 1)

        # sync the change
        synchronizer.synchronize_changes([change], local_session, remote_sessions)
        self.assertEqual(local_session.query(model.Change).count(), 0)

        # remote sessions no longer have the product
        self.assertEqual(remote_sessions['one'].query(model.Product).count(), 0)
        self.assertEqual(remote_sessions['two'].query(model.Product).count(), 0)

    def test_dependency_sort(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        # Product depends on Department, so Department should come first.
        self.assertEqual(synchronizer.dependency_sort('Department', 'Product'), -1)
        self.assertEqual(synchronizer.dependency_sort('Product', 'Department'), 1)

        # Product has dependencies (e.g. Department), so should come after
        # e.g. Store even though there is no direct connection, since Store has
        # no dependencies.
        self.assertEqual(synchronizer.dependency_sort('Store', 'Product'), -1)
        self.assertEqual(synchronizer.dependency_sort('Product', 'Store'), 1)

        # Sometimes the tie can't be broken...
        self.assertEqual(synchronizer.dependency_sort('Store', 'CustomerGroup'), 0)
        self.assertEqual(synchronizer.dependency_sort('Product', 'Product'), 0)

    def test_merge_instance(self):

        class FakeClass(object):
            pass

        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)
        session = Mock()
        instance = FakeClass()

        self.assertFalse(hasattr(synchronizer, 'merge_FakeClass'))
        synchronizer.merge_instance(session, instance)
        session.merge.assert_called_once_with(instance)

        synchronizer.merge_FakeClass = Mock()
        synchronizer.merge_instance(session, instance)
        synchronizer.merge_FakeClass.assert_called_once_with(session, instance)

    def test_merge_Product(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                r'^Dialect sqlite\+pysqlite does \*not\* support Decimal '
                'objects natively\, and SQLAlchemy must convert from floating '
                'point - rounding errors and other issues may occur\. Please '
                'consider storing Decimal numbers as strings or integers on '
                'this platform for lossless storage\.$',
                SAWarning, r'^sqlalchemy\.types$')

            # no prices
            local_session = Session(bind=self.local_engine)
            remote_session = Session(bind=self.remote_engines['one'])
            source_product = model.Product()
            local_session.add(source_product)
            local_session.flush()
            self.assertIsNone(source_product.regular_price_uuid)
            self.assertIsNone(source_product.regular_price)
            self.assertIsNone(source_product.current_price_uuid)
            self.assertIsNone(source_product.current_price)
            target_product = synchronizer.merge_Product(remote_session, source_product)
            self.assertIsNotNone(target_product)
            self.assertIsNot(source_product, target_product)
            self.assertEqual(source_product.uuid, target_product.uuid)
            self.assertIsNone(target_product.regular_price_uuid)
            self.assertIsNone(target_product.regular_price)
            self.assertIsNone(target_product.current_price_uuid)
            self.assertIsNone(target_product.current_price)
            local_session.rollback()
            local_session.close()
            remote_session.rollback()
            remote_session.close()

            # regular price
            local_session = Session(bind=self.local_engine)
            remote_session = Session(bind=self.remote_engines['one'])
            source_product = model.Product()
            regular_price = model.ProductPrice()
            source_product.prices.append(regular_price)
            source_product.regular_price = regular_price
            local_session.add(source_product)
            local_session.flush()
            self.assertIsNotNone(source_product.regular_price_uuid)
            self.assertIsNotNone(source_product.regular_price)
            target_product = synchronizer.merge_Product(remote_session, source_product)
            self.assertEqual(target_product.regular_price_uuid, source_product.regular_price_uuid)
            self.assertIsNotNone(target_product.regular_price)
            local_session.rollback()
            local_session.close()
            remote_session.rollback()
            remote_session.close()

            # current price
            local_session = Session(bind=self.local_engine)
            remote_session = Session(bind=self.remote_engines['one'])
            source_product = model.Product()
            current_price = model.ProductPrice()
            source_product.prices.append(current_price)
            source_product.current_price = current_price
            local_session.add(source_product)
            local_session.flush()
            self.assertIsNotNone(source_product.current_price_uuid)
            self.assertIsNotNone(source_product.current_price)
            target_product = synchronizer.merge_Product(remote_session, source_product)
            self.assertEqual(target_product.current_price_uuid, source_product.current_price_uuid)
            self.assertIsNotNone(target_product.current_price)
            local_session.rollback()
            local_session.close()
            remote_session.rollback()
            remote_session.close()

    def test_delete_instance(self):

        class FakeClass(object):
            pass

        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)
        session = Mock()
        instance = FakeClass()

        self.assertFalse(hasattr(synchronizer, 'delete_FakeClass'))
        synchronizer.delete_instance(session, instance)
        session.delete.assert_called_once_with(instance)

        synchronizer.delete_FakeClass = Mock()
        synchronizer.delete_instance(session, instance)
        synchronizer.delete_FakeClass.assert_called_once_with(session, instance)

    def test_delete_Department(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                r'^Dialect sqlite\+pysqlite does \*not\* support Decimal '
                'objects natively\, and SQLAlchemy must convert from floating '
                'point - rounding errors and other issues may occur\. Please '
                'consider storing Decimal numbers as strings or integers on '
                'this platform for lossless storage\.$',
                SAWarning, r'^sqlalchemy\.types$')

            session = Session(bind=self.local_engine)
            department = model.Department()
            department.subdepartments.append(model.Subdepartment())
            session.add(department)
            session.flush()
            self.assertEqual(session.query(model.Subdepartment).count(), 1)
            subdepartment = session.query(model.Subdepartment).one()
            self.assertEqual(subdepartment.department_uuid, department.uuid)
            synchronizer.delete_Department(session, department)
            self.assertEqual(session.query(model.Subdepartment).count(), 1)
            subdepartment = session.query(model.Subdepartment).one()
            self.assertIsNone(subdepartment.department_uuid)
            session.rollback()
            session.close()

            session = Session(bind=self.local_engine)
            department = model.Department()
            product = model.Product(department=department)
            session.add(product)
            session.flush()
            product = session.query(model.Product).one()
            self.assertEqual(product.department_uuid, department.uuid)
            synchronizer.delete_Department(session, department)
            product = session.query(model.Product).one()
            self.assertIsNone(product.department_uuid)
            session.rollback()
            session.close()

    def test_delete_Subdepartment(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        session = Session(bind=self.local_engine)
        subdepartment = model.Subdepartment()
        product = model.Product(subdepartment=subdepartment)
        session.add(product)
        session.flush()
        product = session.query(model.Product).one()
        self.assertEqual(product.subdepartment_uuid, subdepartment.uuid)
        synchronizer.delete_Subdepartment(session, subdepartment)
        product = session.query(model.Product).one()
        self.assertIsNone(product.subdepartment_uuid)
        session.rollback()
        session.close()

    def test_delete_Family(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        session = Session(bind=self.local_engine)
        family = model.Family()
        product = model.Product(family=family)
        session.add(product)
        session.flush()
        product = session.query(model.Product).one()
        self.assertEqual(product.family_uuid, family.uuid)
        synchronizer.delete_Family(session, family)
        product = session.query(model.Product).one()
        self.assertIsNone(product.family_uuid)
        session.rollback()
        session.close()

    def test_delete_Vendor(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        session = Session(bind=self.local_engine)
        vendor = model.Vendor()
        product = model.Product()
        product.costs.append(model.ProductCost(vendor=vendor))
        session.add(product)
        session.flush()
        cost = session.query(model.ProductCost).one()
        self.assertEqual(cost.vendor_uuid, vendor.uuid)
        synchronizer.delete_Vendor(session, vendor)
        self.assertEqual(session.query(model.ProductCost).count(), 0)
        session.rollback()
        session.close()

    def test_delete_CustomerGroup(self):
        synchronizer = sync.Synchronizer(self.local_engine, self.remote_engines)

        session = Session(bind=self.local_engine)
        group = model.CustomerGroup()
        customer = model.Customer()
        customer.groups.append(group)
        session.add(customer)
        session.flush()
        assignment = session.query(model.CustomerGroupAssignment).one()
        self.assertEqual(assignment.customer_uuid, customer.uuid)
        self.assertEqual(assignment.group_uuid, group.uuid)
        synchronizer.delete_CustomerGroup(session, group)
        self.assertEqual(session.query(model.CustomerGroupAssignment).count(), 0)
        session.rollback()
        session.close()


class ModuleTests(TestCase):

    @patch('rattail.db.sync.edbob')
    def test_get_sync_engines(self, edbob):

        # nothing configured
        edbob.config.get.return_value = None
        self.assertIsNone(sync.get_sync_engines())

        # fake config with 2 out of 3 engines synced
        edbob.engines = {
            'one': 'first',
            'two': 'second',
            'three': 'third',
            }
        edbob.config.get.return_value = 'one, two'
        engines = sync.get_sync_engines()
        self.assertEqual(engines, {'one': 'first', 'two': 'second'})

    @patch.multiple('rattail.db.sync', edbob=DEFAULT, Synchronizer=DEFAULT)
    def test_synchronize_changes(self, edbob, Synchronizer):

        local_engine = Mock()
        remote_engines = Mock()

        # default synchronizer class
        edbob.config.get.return_value = None
        sync.synchronize_changes(local_engine, remote_engines)
        Synchronizer.assert_called_once_with(local_engine, remote_engines)
        Synchronizer.return_value.loop.assert_called_once_with()

        # custom synchronizer class
        edbob.config.get.return_value = 'some_class'
        sync.synchronize_changes(local_engine, remote_engines)
        edbob.load_spec.return_value.assert_called_once_with(local_engine, remote_engines)
        edbob.load_spec.return_value.return_value.loop.assert_called_once_with()
