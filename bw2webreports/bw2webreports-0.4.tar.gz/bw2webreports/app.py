# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, render_template, request, abort
from werkzeug import secure_filename
import json
import os
import sys
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024


@app.errorhandler(404)
def page_not_found(e):
    return "Resource not found", 404


@app.errorhandler(500)
def internal_error(e):
    traceback.print_exc(file=sys.stdout)
    return "Application error", 500


@app.route("/logs", methods=["POST"])
def upload_logs():
    file = request.files['file']
    if file:
        file.save(os.path.join(
            app.config['LOGS_DIR'],
            secure_filename(file.filename)
        ))

        metadata = dict([(k, request.form[k]) for k in request.form])
        KEYS = [
            "X-Real-Ip",
            "User-Agent",
            "Content-Length"
        ]
        for key in KEYS:
            metadata[key] = request.headers.get(key, "")
        with open(os.path.join(
            app.config['LOGS_DIR'],
            secure_filename(file.filename) + ".metadata"
        ), "w") as f:
            json.dump(metadata, f, indent=2)
        return "OK"
    else:
        return "ERROR"


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    if not data or not isinstance(data, dict) or "metadata" not in data \
            or not data["metadata"].get("uuid", None) \
            or not data["metadata"].get("type", None) == \
            u"Brightway2 serialized LCA report":
        abort(400)
    filepath = os.path.join(app.config["DATA_DIR"],
        "%s.json" % data["metadata"]["uuid"])
    with open(filepath, "w") as f:
        json.dump(data, f)
    return "OK"


@app.route('/report/<uuid>')
def report(uuid):
    try:
        data = open(os.path.join(app.config["DATA_DIR"], "%s.json" % uuid)).read()
    except:
        return render_template('404.html'), 404
    return render_template("report.html", data=data)


@app.route('/status')
def status():
    return json.dumps({'reports': len(os.listdir(app.config["DATA_DIR"]))})

# TODO: Prevent overwriting of existing reports
