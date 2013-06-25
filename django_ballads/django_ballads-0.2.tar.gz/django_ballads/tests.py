from django.db import models, IntegrityError
from django.test import TransactionTestCase
from django_ballads import Ballad, BalladException
import os
import os.path
import tempfile


class TestModel(models.Model):
    unique = models.IntegerField(unique=True)


class TestCompensatingActions(TransactionTestCase):
    """
    Can we use ballads to create & manage compensating actions?
    """

    def test_db_rollback(self):
        """A ballad rollback rolls back its db transaction."""
        with Ballad() as ballad:
            t = TestModel.objects.create(unique=1)
            ballad.rollback()
        self.assertEqual(0, TestModel.objects.count())
        self.assertTrue(ballad.rolled_back)

    def test_db(self):
        """A ballad that isn't rolled back commits its db transaction."""
        with Ballad() as ballad:
            t = TestModel.objects.create(unique=1)
        self.assertEqual(1, TestModel.objects.count())
        self.assertFalse(ballad.rolled_back)

    def test_db_integrity_error_rollback(self):
        """Integrity error is recovered within the ballad."""
        # if commit_on_success (under Django < 1.6) or atomic (1.6+)
        # didn't actually work properly, or we invoked them incorrectly
        # when we wrap the context manager, we might end up with a
        # non-functional database connection under postgresql (you must
        # roll back after an IntegrityError).
        t = TestModel.objects.create(unique=1)

        try:
            with Ballad() as ballad:
                t = TestModel.objects.create(unique=1)
            self.fail("Should have raised an IntegrityError out of the ballad.")
        except IntegrityError as e:
            pass
        # test both DML and DQL to ensure we're still good
        self.assertEqual(1, TestModel.objects.count())
        TestModel.objects.create(unique=2)
        self.assertEqual(2, TestModel.objects.count())
        self.assertTrue(ballad.rolled_back)

    def test_db_filesystem_rollback(self):
        """A ballad rollback runs compensating actions."""
        fname = None
        with Ballad() as ballad:
            f = tempfile.NamedTemporaryFile(delete=False)
            fname = f.name
            f.write("hi there")
            f.close()
            ballad.compensation(lambda: os.unlink(fname))

            t = TestModel.objects.create(unique=1)
            ballad.rollback()
        try:
            self.assertFalse(os.path.exists(fname))
            self.assertEqual(0, TestModel.objects.count())
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
        self.assertTrue(ballad.rolled_back)

    def test_db_filesystem(self):
        """A ballad that isn't rolled back does not run compensating actions."""
        fname = None
        with Ballad() as ballad:
            f = tempfile.NamedTemporaryFile(delete=False)
            fname = f.name
            f.write("hi there")
            f.close()
            ballad.compensation(lambda: os.unlink(fname))

            t = TestModel.objects.create(unique=1)

        self.assertTrue(os.path.exists(fname))
        self.assertEqual(1, TestModel.objects.count())
        os.unlink(fname)
        self.assertFalse(ballad.rolled_back)

    def test_compensation_exception(self):
        """Exceptions in rollback get reported specially."""
        try:
            with Ballad() as ballad:
                ballad.compensation(lambda: unknown())
                ballad.rollback()
        except BalladException as e:
            self.assertEqual(1, len(e.exceptions))
            self.assertEqual(None, e.cause)
        except Exception as e:
            self.fail("Unexpected exception %s" % e)
        self.assertTrue(ballad.rolled_back)

    def test_suppress_compensation_exceptions(self):
        """Exceptions in rollback can be suppressed."""
        try:
            with Ballad(ignore_rollback_exceptions=True) as ballad:
                ballad.compensation(lambda: unknown())
                ballad.rollback()
        except BalladException as e:
            self.fail("BalladException was not been suppressed.")
        except Exception as e:
            self.fail("Unexpected exception %s" % e)
        self.assertTrue(ballad.rolled_back)

    def test_exception_in_block(self):
        """Exceptions in the ballad are raised normally."""
        try:
            with Ballad() as ballad:
                raise ValueError
        except ValueError:
            pass
        except Exception as e:
            self.fail("Unexpected exception %s" % e)
        self.assertTrue(ballad.rolled_back)

    def test_exception_in_block_and_suppressed_compensation_exceptions(self):
        """Exceptions in the ballad are raised normally."""
        try:
            with Ballad(ignore_rollback_exceptions=True) as ballad:
                ballad.compensation(lambda: unknown())
                raise ValueError
        except ValueError:
            pass
        except BalladException as e:
            self.fail("BalladException was not been suppressed.")
        except Exception as e:
            self.fail("Unexpected exception %s" % e)
        self.assertTrue(ballad.rolled_back)

    def test_exception_in_block_and_compensation_exceptions(self):
        """Exceptions in the ballad are bundled with rollback exceptions."""
        try:
            with Ballad() as ballad:
                ballad.compensation(lambda: unknown())
                raise ValueError
        except BalladException as e:
            self.assertEqual(1, len(e.exceptions))
            self.assertEqual(3, len(e.cause))
            self.assertEqual(ValueError, e.cause[0])
        except ValueError:
            self.fail("Unbundled ballad exception raised.")
        except Exception as e:
            self.fail("Unexpected exception %s" % e)
        self.assertTrue(ballad.rolled_back)


class TestExplicitStanza(TransactionTestCase):
    """Can we use explicit stanzas to manage compensation actions?"""

    def test_simple_stanza(self):
        test_list = []
        with Ballad() as ballad:
            with ballad.stanza() as stanza:
                test_list.append(0)
                stanza.compensation = lambda: test_list.pop()
            ballad.rollback()

        self.assertEqual(0, len(test_list))
        self.assertTrue(ballad.rolled_back)

    def test_changing_stanza(self):
        test_list = []
        with Ballad() as ballad:
            with ballad.stanza() as stanza:
                test_list.append(0)
                stanza.compensation = lambda: test_list.pop()
                stanza.compensation = lambda: test_list.append(1)
            ballad.rollback()

        self.assertEqual(2, len(test_list))
        self.assertTrue(ballad.rolled_back)

    def test_stanza_causes_rollback(self):
        test_list = []
        with Ballad() as ballad:
            with ballad.stanza() as stanza:
                test_list.append(0)
                stanza.compensation = lambda: test_list.pop()
                ballad.rollback()

        self.assertEqual(0, len(test_list))
        self.assertTrue(ballad.rolled_back)
