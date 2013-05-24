from django import test

import logging
log = logging.getLogger(__name__)

class ModelTestCase(test.TestCase):
    # Source:
    # http://stackoverflow.com/questions/502916/django-how-to-create-a-model
    test_models_app = 'denormalize.tests'
    _test_models_initiated = False

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        if not cls._test_models_initiated:
            cls.create_models_from_app(cls.test_models_app)
            cls._test_models_initiated = True
        super(ModelTestCase, cls).setUpClass(*args, **kwargs)

    @classmethod
    def create_models_from_app(cls, app_name):
        """
        Manually create Models (used only for testing) from the specified string app name.
        Models are loaded from the module "<app_name>.models"
        """
        from django.db import connection, DatabaseError
        from django.db.models.loading import load_app

        app = load_app(app_name)
        from django.core.management import sql
        from django.core.management.color import no_style
        sql = sql.sql_create(app, no_style(), connection)
        cursor = connection.cursor()
        for statement in sql:
            try:
                cursor.execute(statement)
            except DatabaseError, excn:
                log.debug("DatabaseError in statement: %s",
                    statement, exc_info=True)
  