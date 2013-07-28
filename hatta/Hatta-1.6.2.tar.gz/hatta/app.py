# -*- coding: utf-8 -*-

import flask

import hatta.request
import hatta.wiki
import hatta.config


def make_app():
    app = flask.Flask('hatta')
    app.hatta_config = hatta.config.read_config()
    wiki = hatta.wiki.Wiki(app.hatta_config)
    app.hatta_wiki = wiki
    def make_request(*args, **kwargs):
        return hatta.request.WikiRequest(wiki, None, *args, **kwargs)
    app.request_class = make_request
    return app

if __name__ == '__main__':
    app = make_app()
    host = app.hatta_config.get('interface', 'localhost')
    port = int(app.hatta_config.get('port', 8080))
    app.run(host, port)

