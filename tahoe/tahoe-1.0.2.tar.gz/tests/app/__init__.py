import subprocess
import logging

from werkzeug.contrib.cache import MemcachedCache
import ultramemcache

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.mail import Mail

import pyes
import celery

from tahoe.models import ModelRegistry
from tahoe.views import ViewsRegistry
from tahoe.tasks import TaskRegistry

from tahoe.sessions import ItsdangerousSessionInterface
from tahoe.aws import AWS

# Register all the views, models, and tasks
from models import *
from views import *
from tasks import *


class TestTahoeApplication(object):
    """
    A minimal Tahoe Application for testing
    """
    def __init__(self):
        self.config_name = 'tests.app.config.Testing'
        self.environment = 'testing'
        self._app = None
        self._db = None
        self._views = None
        self._models = None
        self._user_datastore = None
        self._security = None
        self._mail = None
        self._aws = None
        self._version = None
        self._elastic_search = None
        self._celery = None
        self._tasks = None
        self._cache = None

    @property
    def cache(self):
        if not self._cache:
            self._cache = self._get_cache()
        return self._cache

    @property
    def celery(self):
        if not self._celery:
            self._celery = self._get_celery()
        return self._celery

    @property
    def tasks(self):
        if not self._tasks:
            self._tasks = self._setup_tasks()
        return self._tasks

    @property
    def elastic_search(self):
        if not self._elastic_search:
            self._elastic_search = self._get_elastic_search()
        return self._elastic_search

    @property
    def version(self):
        if not self._version:
            self._version = self._get_version()
        return self._version

    @property
    def aws(self):
        if not self._aws:
            self._aws = self._get_aws()
        return self._aws

    @property
    def app(self):
        if not self._app:
            self._app = self._setup_app()
        return self._app

    @property
    def config(self):
        return self.app.config

    @property
    def db(self):
        if not self._db:
            self._db = self._setup_db()
        return self._db

    @property
    def models(self):
        if not self._models:
            self._models = self._setup_models()
        return self._models

    def get_user_datastore(self):
        if not self._user_datastore:
            self._user_datastore = self._setup_user_datastore()
        return self._user_datastore

    @property
    def security(self):
        if not self._security:
            self._security = self._setup_security()
        return self._security

    @property
    def mail(self):
        if not self._mail:
            self._mail = self._setup_mail()
        return self._mail

    @property
    def views(self):
        if not self._views:
            self._views = self._setup_views()
        return self._views

    @property
    def views_bucket(self):
        return dict(
            aws=self.aws,
            environment=self.environment,
            tasks=self.tasks,
            cache=self.cache)

    @property
    def model_bucket(self):
        return dict(
            user_datastore=self.get_user_datastore,
            aws=self.aws,
            elastic_search=self.elastic_search,
            environment=self.environment,
            cache=self.cache)

    @property
    def tasks_bucket(self):
        return dict(
            aws=self.aws,
            environment=self.environment,
            cache=self.cache)

    def teardown_request(self, exception=None):
        """
        Do not commit if we encounter an exception in a request.
        """
        if not exception:
            self.db.session.commit()
        if self.environment != 'Testing':
            self.db.session.close()

    def after_request(self, response):
        response.headers['Tahoe-Version'] = self.version
        return response

    def setup(self):
        """
        Execute setup routines which must be run immediately and not defferered
        """
        self.app.logger.handlers[0].setLevel(logging.WARNING)
        return [
            self.views,
            self._setup_session_interface(),
            self.security,
            self.mail,
            self.tasks]

    def _setup_session_interface(self):
        self.app.session_interface = ItsdangerousSessionInterface(
            config=self.config)

    def _setup_app(self):
        """
        Creates the Flask application and sets it up a bit
        """
        app = Flask(__name__)
        app.config.from_object(self.config_name)
        app.teardown_request(self.teardown_request)
        app.after_request(self.after_request)
        return app

    def _setup_db(self):
        """
        Initializes the database connection
        """
        return SQLAlchemy(self.app)

    def _setup_views(self):
        """
        Creates and sets up the applicaton views
        """
        views = ViewsRegistry(
            app=self.app,
            db=self.db,
            config=self.config,
            models=self.models,
            bucket=self.views_bucket,
            logger=self.app.logger)
        views.setup()
        return views

    def _setup_models(self):
        """
        Configures and sets up all of the registered models
        """
        models = ModelRegistry(
            app=self.app,
            db=self.db,
            config=self.config,
            logger=self.app.logger,
            bucket=self.model_bucket)
        models.setup()
        return models

    def _setup_user_datastore(self):
        """
        Configures the "user_datastore" used by Flask-Security
        """
        return SQLAlchemyUserDatastore(
            self.db,
            self.models.Account,
            self.models.Role)

    def _setup_security(self):
        """
        Configures the Security routines supplied by Flask-Security
        """
        return Security(
            self.app,
            self.get_user_datastore(),
            register_blueprint=False)

    def _setup_mail(self):
        """
        Configures Flask-Mail, see options in config.py
        """
        return Mail(self.app)

    def _get_version(self):
        """
        Right now this just nabs the more recent git ref
        """
        cmd = """/usr/bin/git log -n 1 --no-merges --oneline | \
                 /usr/bin/awk '{print $1}'"""
        pr = subprocess.Popen(
            [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        (out, error) = pr.communicate()
        if not error:
            return out.strip()
        return "ERROR GETTING VERSION"

    def _get_aws(self):
        return AWS(self.config)

    def _get_elastic_search(self):
        return pyes.ES(self.config.get('ELASTIC_SEARCH_SERVERS'))

    def _get_celery(self):
        c = celery.Celery()
        c.config_from_object(self.config)
        return c

    def _setup_tasks(self):
        tasks = TaskRegistry(
            models=self.models,
            db=self.db,
            logger=self.app.logger,
            config=self.config,
            app=self.app,
            celery=self.celery,
            bucket=self.tasks_bucket)
        tasks.setup()
        return tasks

    def _get_cache(self):
        server_list = self.config.get('MEMCACHED_SERVERS')
        ultramemcache_client = ultramemcache.Client(server_list)
        return MemcachedCache(ultramemcache_client)

    def drop_all_tables(self):
        self.app.logger.debug("Dropping all tables")
        self.db.drop_all()

    def create_all_tables(self):
        self.app.logger.debug("Creating all tables")
        self.db.create_all()
