import logging

from elixir import Field, Unicode, Entity

from pufferfish import add_session_hooks
from pufferfish.tests.model.exc import AfterBeginExc, BeforeCommitExc,\
                                       AfterCommitExc, AfterAttachExc,\
                                       AfterBulkDeleteExc, AfterBulkUpdateExc,\
                                       AfterFlushPostExecExc, AfterRollbackExc,\
                                       BeforeFlushExc

__session__ = None
log = logging.getLogger(__name__)

class Car(Entity):
    model = Field(Unicode(30))
    add_session_hooks()

    @classmethod
    def __after_begin__(cls, session, transaction, connection):
        if hasattr(cls, "raise_exceptions") and \
           "after_begin" in cls.raise_exceptions:
            raise AfterBeginExc()

    @classmethod
    def __before_commit__(cls, session):
        if hasattr(cls, "raise_exceptions") and \
           "before_commit" in cls.raise_exceptions:
            raise BeforeCommitExc()

    @classmethod
    def __after_commit__(cls, session):
        if hasattr(cls, "raise_exceptions") and \
           "after_commit" in cls.raise_exceptions:
            raise AfterCommitExc()

    @classmethod
    def __after_attach__(cls, session, instance):
        if hasattr(cls, "raise_exceptions") and \
           "after_attach" in cls.raise_exceptions:
            raise AfterAttachExc()

    @classmethod
    def __after_bulk_delete__(cls, session, query, query_context, result):
        if hasattr(cls, "raise_exceptions") and \
           "after_bulk_delete" in cls.raise_exceptions:
            raise AfterBulkDeleteExc()

    @classmethod
    def __after_bulk_update__(cls, session, query, query_context, result):
        if hasattr(cls, "raise_exceptions") and \
           "after_bulk_update" in cls.raise_exceptions:
            raise AfterBulkUpdateExc()

    @classmethod
    def __after_flush_postexec__(cls, session, flush_context):
        if hasattr(cls, "raise_exceptions") and\
           "after_flush_post_exec" in cls.raise_exceptions:
            raise AfterFlushPostExecExc()

    @classmethod
    def __after_rollback__(cls, session):
        if hasattr(cls, "raise_exceptions") and \
           "after_rollback" in cls.raise_exceptions:
            raise AfterRollbackExc()
    
    @classmethod
    def __before_flush__(cls, session, flush_context, instances):
        if hasattr(cls, "raise_exceptions") and \
           "before_flush" in cls.raise_exceptions:
            raise BeforeFlushExc()


