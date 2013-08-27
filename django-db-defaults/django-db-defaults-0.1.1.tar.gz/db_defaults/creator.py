import types

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from db_defaults.fields import DefaultProxyField
from db_defaults.settings import DB_DEFAULTS_ENABLE_ALL_MODELS, DB_DEFAULTS_ENABLE_ALL_FIELDS

import logging
logger = logging.getLogger(__name__)

def _get_app_module(app):
    """
    Convert to app module  if its an 'app name' otherwise return as it is.
    """
    if isinstance(app, types.ModuleType):
        app_module = app
    else: #If not a module already, fetch the module
        try:
            app_module = models.get_app(app)
        except ImproperlyConfigured:
            logger.error("There is no enabled application matching '%s'." % app)
            return None
    return app_module

def _get_db_operator(db_alias):
    """
    Use south utility to find out the Database Operations object for current db backend alias.
    """
    #IMPORTANT: explicitly import db module of db_defaults to ensure the patch load
    from db_defaults import db
    from south.db import dbs
    return dbs[db_alias]

def process_app_defaults(app, db_alias):
    """
    Iterate over all  models of the app and process defaults sql for them.
    """
    if app is not None:
        app_module = _get_app_module(app)

    if app_module is not None:
        logger.info("Creating defaults for %s..."%app_module.__name__)
        for model in models.get_models(app_module):
            # Only add if it's not abstract or proxy

            #Check for explicitly defined defaults dict
            db_defaults = getattr(model, 'db_defaults', {})

            #check if db defaults should be added for all models ir-respective of custom defaults
            model_defaults_enabled = DB_DEFAULTS_ENABLE_ALL_MODELS

            #check if db defaults should be added for all fields ir-respective of custom defaults
            #This is always True if DB_DEFAULTS_ENABLE_ALL_MODELS=True
            field_defaults_enabled = DB_DEFAULTS_ENABLE_ALL_MODELS or DB_DEFAULTS_ENABLE_ALL_FIELDS

            # Call for the model if
            # 1- It has either custom defaults or enabled for all models AND
            # 2- It is not a abstract model
            # 3- It is not a proxy model
            if (db_defaults or model_defaults_enabled) and not model._meta.abstract \
                and not getattr(model._meta, "proxy", False):
                logger.debug("Finding defaults for %s"%model.__module__)
                #Set the db backend based on alias
                db_operator = _get_db_operator(db_alias)

                sqls = []
                model_fields = model._meta.fields

                #generate the alter sql queries
                #Iterate over all fields of the model  and process defaults sql for them.
                alter_fields = []
                model_params = {
                    "model_name": model._meta.object_name,
                    "table_name": model._meta.db_table
                }
                for field in model_fields:
                    field_db_default = db_defaults.get(field.name)
                    proxy_field = DefaultProxyField(field, field_db_default, db=db_operator)
                    model_params.update({'type' : db_operator._db_type_for_alter_column(field)})
                    # If the field has alters data, add it to the list of alter fields
                    if proxy_field.has_alters():
                        db_operator.alter_set_db_defaults(proxy_field, proxy_field.name, model_params, sqls)

                logger.debug("    Alter queries - %s "%sqls)

                #Execute sqls for all fields to be altered
                for sql, values in sqls:
                    db_operator.execute(sql, values)

