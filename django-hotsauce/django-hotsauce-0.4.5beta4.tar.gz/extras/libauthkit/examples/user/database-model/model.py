from notmm.utils.sql.session import ScopedSession
import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    scoped_session = ScopedSession(autocommit=False) # transactional=True
    scoped_session.set_session(engine)
    meta.engine = engine
    meta.Session = scoped_session.session

