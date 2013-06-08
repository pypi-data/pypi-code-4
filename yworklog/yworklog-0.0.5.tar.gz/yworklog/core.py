#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from cement.core import foundation, handler, hook
from . import controller as ctrl
from .model import init

from xdg.BaseDirectory import save_data_path
from os.path import join

log = logging.getLogger(__name__)

def get_main_db():
    return 'sqlite+pysqlite:///' +join(save_data_path('worklog'), 'db.sqlite')

class WorkLogApp(foundation.CementApp):
    class Meta:
        label = 'WorkLog'
        base_controller = ctrl.WorkLogController
        config_defaults = {
            'main': {
                'db': get_main_db()
            }
        }

def init_db_for_app(app):
    app.session = init(app.config.get('main', 'db'))

def main():
    app = WorkLogApp()
    [handler.register(c) for c in ctrl.export]
    hook.register('post_setup', init_db_for_app)
    app.setup()
    app.run()
