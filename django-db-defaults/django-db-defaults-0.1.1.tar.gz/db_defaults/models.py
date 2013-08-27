from django.db.models.signals import post_syncdb
from south.signals import  post_migrate

from db_defaults.creator import process_app_defaults

def sync_defaults(app=None, verbosity=0, interactive=False, db=None, **kwargs):
    from south.db import DEFAULT_DB_ALIAS
    if db is None:
        db  = DEFAULT_DB_ALIAS
    interactive = bool(interactive)
    process_app_defaults(app, db)

post_syncdb.connect(sync_defaults)
post_migrate.connect(sync_defaults)

