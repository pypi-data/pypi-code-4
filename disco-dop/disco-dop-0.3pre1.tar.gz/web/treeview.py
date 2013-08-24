""" Web interface to browse through a treebank. Requires Flask. """
# stdlib
import os
import logging
#from functools import wraps
# Flask & co
from flask import Flask
from flask import request, render_template
from flask import send_from_directory
#from werkzeug.contrib.cache import SimpleCache
# disco-dop
#from discodop.treebank import getreader
from discodop.treedraw import DrawTree

APP = Flask(__name__)


def stream_template(template_name, **context):
	""" From Flask documentation. """
	APP.update_template_context(context)
	templ = APP.jinja_env.get_template(template_name)
	result = templ.stream(context)
	result.enable_buffering(5)
	return result


@APP.route('/')
def main():
	""" Entry form to upload file. """
	return render_template('upload.html', form=request.args)


@APP.route('/view')
def view():
	""" Receive uploaded file, store it with timeout, and produce chunk of 100
	trees to display. """
	pass


@APP.route('/draw')
def draw():
	""" Produce a visualization of a tree on a separate page. """
	if 'tree' in request.args:
		return "<pre>%s</pre>" % DrawTree(request.args['tree']).text(
				unicodelines=True, html=True)


@APP.route('/favicon.ico')
def favicon():
	""" Serve the favicon. """
	return send_from_directory(os.path.join(APP.root_path, 'static'),
			'treesearch.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
	logging.basicConfig()
	for log in (logging.getLogger(), APP.logger):
		log.setLevel(logging.DEBUG)
		log.handlers[0].setFormatter(logging.Formatter(
				fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
	APP.run(debug=True, host='0.0.0.0')
