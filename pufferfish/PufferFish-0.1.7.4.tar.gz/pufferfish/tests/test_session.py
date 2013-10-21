
import elixir

from nose.tools import assert_raises
from sqlalchemy import create_engine

from pufferfish.tests.model.car import Car
from pufferfish.tests.model.exc import AfterBeginExc, BeforeCommitExc,\
                                       AfterCommitExc, AfterAttachExc,\
                                       AfterBulkDeleteExc, AfterBulkUpdateExc,\
                                       AfterFlushPostExecExc, AfterRollbackExc,\
                                       BeforeFlushExc
from pufferfish.session import HookableSession
from sqlalchemy.orm import SessionExtension

class DummyExtension(SessionExtension):
    pass

class TestSession(object):
    
    def setup(self):
        Car.raise_exceptions = []

    def teardown(self):
        elixir.drop_all()
        self.session.close()

    def create_session(self, dummys=0):
        engine = create_engine("sqlite:///")
        elixir.metadata.bind = engine
        if dummys > 1:
            # add a bogus extension to test extension passing
            self.session = HookableSession(extension=[ DummyExtension() for x in xrange(dummys)])
        elif dummys == 1:
            self.session = HookableSession(extension=DummyExtension())
        else:
            self.session = HookableSession()
            
        elixir.session = self.session
        elixir.setup_all()
        elixir.create_all()

    def _attach_car(self, model=u"FakeCar"):
        c = Car(model=model)
        elixir.session.add(c)

    def _bulk_update(self, model=u"Updated"):
        elixir.session.query(Car).update(values={Car.model: model})

    def _bulk_delete(self):
        elixir.session.query(Car).delete()

    # FIXME
    #def test_after_begin(self):
    #    Car.raise_exceptions = ["after_begin"]
    #    self.create_session()
    #    self.session.autoflush = False
    #    self.session.rollback()
    #    assert_raises(AfterBeginExc, self.session.rollback)

    def test_before_commit(self):
        self.create_session()
        Car.raise_exceptions = ["before_commit"]
        self._attach_car()
        assert_raises(BeforeCommitExc, self.session.commit)

    def test_extension(self):
        self.create_session(dummys=1)
        self.test_before_commit()

    def test_extensions(self):
        self.create_session(dummys=2)
        self.test_before_commit()

    def test_after_commit(self):
        self.create_session()
        Car.raise_exceptions = ["after_commit"]
        self._attach_car()
        assert_raises(AfterCommitExc, self.session.commit)

    def test_after_attach(self):
        self.create_session()
        Car.raise_exceptions = ["after_attach"]
        assert_raises(AfterAttachExc, self._attach_car)

    def test_after_flush_post_exec(self):
        self.create_session()
        Car.raise_exceptions = ["after_flush_post_exec"]
        self._attach_car()
        assert_raises(AfterFlushPostExecExc, self.session.commit)
    
    def test_after_rollback(self):
        self.create_session()
        Car.raise_exceptions = ["after_rollback"]
        self._attach_car()
        assert_raises(AfterRollbackExc, self.session.rollback)

    def test_before_flush(self):
        self.create_session()
        Car.raise_exceptions = ["before_flush"]
        self._attach_car()
        assert_raises(BeforeFlushExc, self.session.commit)

    def test_after_bulk_update(self):
        self.create_session()
        Car.raise_exceptions = ["after_bulk_update"]
        self._attach_car()
        self._attach_car(u"Fake2")
        assert_raises(AfterBulkUpdateExc, self._bulk_update)
        self.session.rollback()

    def test_after_bulk_delete(self):
        self.create_session()
        Car.raise_exceptions = ["after_bulk_delete"]
        self._attach_car()
        self._attach_car(u"Fake2")
        assert_raises(AfterBulkDeleteExc, self._bulk_delete)
        self.session.rollback()
        
