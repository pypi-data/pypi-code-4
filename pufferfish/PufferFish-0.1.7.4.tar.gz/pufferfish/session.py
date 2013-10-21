from elixir.statements import Statement
import logging
from sqlalchemy.orm import SessionExtension
from sqlalchemy.orm import sessionmaker, scoped_session

__all__ = [ 'HookableSessionExtension', 'add_session_hooks', 'HookableSession' ]

log = logging.getLogger(__name__)

def HookableSession(**kwargs):
    """ Create the session with the HookableSessionExtension extension.
        Refer to the sessionmaker doc for parameters:
        http://www.sqlalchemy.org/docs/reference/orm/sessions.html
    """
    extensions=[ HookableSessionExtension() ]
    if "extension" in kwargs:
        ext_param = kwargs["extension"]
        if hasattr(ext_param, "__iter__"):
            extensions.extend([ e for e in ext_param])
        else:
            extensions.append(ext_param)
        del kwargs["extension"]
    return scoped_session(sessionmaker(extension=extensions,
                                       **kwargs)) 

class SessionHook(object):
    """ This is the stament that does the magic: it inspects the class 
        it is called on and register callbacks with the HookableSessionExtension SQLAlchemy
        session extension.
    """
    def __init__(self, entity):
        for hook in HookableSessionExtension.valid_callbacks:
            e_clb_name = "__%s__" % hook
            if hasattr(entity, e_clb_name):
                log.debug("entity %s: installing hook %s", entity, hook)
                HookableSessionExtension.add_callback(hook, getattr(entity, e_clb_name))

# trasform SessionHook in a Statement
add_session_hooks = Statement(SessionHook)

class HookableSessionExtension(SessionExtension):
    """ SQLAlchemy Session Extension that calls hooks on session events for
        registered classes.

        from pufferfish.session import HookableSession add_session_hooks
        import elixir
        elixir.session = HookableSession()
        
        # bind the session, as usual
        # ...

        class Example(Entity):
            name = Field(Unicode(30), required=True)
            add_session_hooks()

            @classmethod
            def __after_commit__(cls, session):
                # this will be called after a commit is successfull

        See the __main__ for a working example

        Further doc on session extension:
        # See http://www.sqlalchemy.org/docs/reference/orm/interfaces.html#sqlalchemy.orm.interfaces.SessionExtension
    """

    valid_callbacks = ( 'after_attach', 'after_begin', 'after_bulk_delete',
                        'after_bulk_update', 'after_commit', 'after_flush',
                        'after_flush_postexec', 'after_rollback', 'before_commit',
                        'before_flush')
    callbacks = {}

    @classmethod
    def add_callback(cls, hook, value):
        if not hook in HookableSessionExtension.callbacks:
            HookableSessionExtension.callbacks[hook] = []
        HookableSessionExtension.callbacks[hook].append(value)

    def __handle_callback(self, hook, *args):
        if not hook in HookableSessionExtension.callbacks:
            return
        for c in HookableSessionExtension.callbacks[hook]:
            c(*args)
    
    def after_attach(self, session, instance):
        self.__handle_callback("after_attach", session, instance)

    def after_begin(self, session, transaction, connection):
        self.__handle_callback("after_begin", session, transaction, connection)

    def after_bulk_delete(self, session, query, query_context, result):
        self.__handle_callback("after_bulk_delete", session, query,
                                                    query_context, result )

    def after_bulk_update(self, session, query, query_context, result):
        self.__handle_callback("after_bulk_update",session, query, 
                                                   query_context, result )
        
    def after_commit(self, session):
        self.__handle_callback("after_commit", session)

    def after_flush(self, session, flush_context):
        self.__handle_callback("after_flush", session, flush_context)
    
    def after_flush_postexec(self, session, flush_context):
        self.__handle_callback("after_flush_postexec", session, flush_context)

    def after_rollback(self, session):
        self.__handle_callback("after_rollback", session)

    def before_commit(self, session):
        self.__handle_callback("before_commit", session)

    def before_flush(self, session, flush_context, instances):
        self.__handle_callback("before_flush", session, flush_context, instances)
    
