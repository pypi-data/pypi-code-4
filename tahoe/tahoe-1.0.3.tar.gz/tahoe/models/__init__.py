"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from . import mixins


class ModelRegistry(object):
    model_callbacks = []
    models = {}

    def __init__(self, app, config, db, logger, bucket):
        """
        A place to gather together all our models for easy access and mass operations
        """
        self.app = app
        self.config = config
        self.db = db
        self.logger = logger
        self.bucket = bucket

    @classmethod
    def destroy_all(cls):
        cls.model_callbacks = []
        cls.models = {}

    @classmethod
    def register(cls):
        def inner(callback):
            cls.model_callbacks.append(callback)
        return inner

    def __getattr__(self, key):
        model_class = self.models.get(key)
        if not model_class:
            raise ValueError('No such model registered as {}'.format(key))
        return model_class

    def _setup_model(self, callback):
        model_class = callback(
            config=self.config,
            db=self.db,
            models=self,
            app=self.app,
            logger=self.logger,
            bucket=self.bucket)
        return model_class.__name__, model_class

    def _update_models(self, model_name, model_class):
        self.models[model_class.__name__] = model_class

    def setup(self):
        for callback in self.model_callbacks:
            model_name, model_class = self._setup_model(callback)
            self._update_models(model_name, model_class)

    def __repr__(self):
        return u"<ModelRegistry models='{}' />".format(self.models.keys())
