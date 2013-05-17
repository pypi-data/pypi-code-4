# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template, url_for, redirect, jsonify
from flask import request, abort, Response, flash
from flask import make_response

from werkzeug import Headers
from gevent.wsgi import WSGIServer

app = Flask(__name__)

app.debug=True

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')




if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    app.run(use_reloader=False, use_debugger=True)
