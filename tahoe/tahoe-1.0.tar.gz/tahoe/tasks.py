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


class TaskRegistry(object):
    task_callbacks = []

    def __init__(self, app, celery, models, db, logger, config, bucket):
        self.celery = celery
        self.models = models
        self.db = db
        self.app = app
        self.logger = logger
        self.config = config
        self.bucket = bucket

    @classmethod
    def register(cls):
        def inner(callback):
            cls.task_callbacks.append(callback)
        return inner

    def __getattr__(self, task_name):
        task = self.get_tasks().get(task_name)
        if not task:
            raise ValueError('No such task registered as {}'.format(task_name))
        return task

    def get_tasks(self):
        return self.celery.tasks

    def setup(self):
        for task_callback in self.task_callbacks:
            task_callback(
                celery=self.celery,
                models=self.models,
                db=self.db,
                app=self.app,
                logger=self.logger,
                config=self.config,
                bucket=self.bucket)

    def __repr__(self):
        return u"<TasksRegistry tasks='{}' />".format(self.get_tasks().keys())
