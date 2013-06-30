from flask import Flask
from flask.ext.appconfig import HerokuConfig


def create_app(configfile):
    app = Flask('testapp')
    app.config['DIRECT_SETTING'] = True
    HerokuConfig(app, configfile)
    return app
