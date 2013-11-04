# -*- coding: utf-8 -*-
from jinja2 import Template
from os.path import dirname,normpath,join,exists,abspath
import re,cgi,sys,imp,os,gzip,tempfile
from time import gmtime,strftime
from wsgiref.util import request_uri
from pysite.tools.log import logger,get_traceback
from pysite.tools.httptools import HTTPRequestData
from pysite.localization import localization
from pysite.conf import getConfiguration
from pysite.compat import PORTABLE_STRING, PORTABLE_BYTES
import pysite.wsgi.httpheader

if sys.version_info[0]==2:
	from StringIO import StringIO
	from urlparse import parse_qs, urlparse
elif sys.version_info[0]>=3:
	from urllib.parse import parse_qs, urlparse
	from io import StringIO

#Last-Modified: Thu, 13 Dec 2012 13:13:59 GMT
#Accept-Ranges: bytes
#Vary: Accept-Encoding
#Content-Encoding: gzip
#Content-Length: 2106
#Content-Type: application/javascript


#Last-Modified: Thu, 13 Dec 2012 13:13:57 GMT
#Accept-Ranges: bytes
#Vary: Accept-Encoding
#Content-Encoding: gzip
#Content-Length: 263
#Content-Type: text/css


#Last-Modified: Thu, 13 Dec 2012 13:13:57 GMT
#Accept-Ranges: bytes
#Content-Length: 1722
#Content-Type: image/png



ext_map_content_type = {
	'js': {
		'Content-Type': 'application/javascript',
		'Content-Encoding': 'gzip'
	},
	'html': {
		'Content-Type': 'text/html',
		'Content-Encoding': 'gzip'
	},
	'css': {
		'Content-Type': 'text/css',
		'Content-Encoding': 'gzip'
	},
	'png': {
		'Content-Type': 'image/png'
	},
	'gif': {
		'Content-Type': 'image/gif'
	},
	'jpg': {
		'Content-Type': 'image/jpeg'
	},
	'ico': {
		'Content-Type': 'image/x-icon'
	}
}

def redirect(location,cookies,start_response):
	response_headers = [
		('Content-type', 'text/html; charset=utf-8'),
		('Location',location),
		('Content-Length','0')]
	for c in cookies:
		response_headers += [('Set-Cookie', c)]
	start_response('302 Redirect', response_headers)
	return ['']

	
class PySiteApplication(object):

	def __init__(self,basedir):
		self.basedir = abspath(basedir)
		self.conf = getConfiguration(basedir)
		self.templates_dir = join(basedir,'templates')
		self.subhandlers_dir = join(basedir,'subhandlers')
		self.translations_dir = join(basedir,'translations')
		sys.path.append(basedir)
		self.rx_static_file = re.compile('.+\.(%s)$' % '|'.join(ext_map_content_type.keys()),re.I)
	
	def __call__(self,environ, start_response):
		try:
			log = logger(self.conf)
			status = "200 OK"
			output = ""
			
			content_len = environ.get('CONTENT_LENGTH')
			post_data = ''
			if content_len:
				post_data = environ['wsgi.input'].read(int(content_len))
			query_string = environ['QUERY_STRING']
			cookies = ''
			if 'HTTP_COOKIE' in environ:
				cookies = environ['HTTP_COOKIE']
			req_data = HTTPRequestData(post_data,query_string,cookies)
			
			path = environ['PATH_INFO'][1:]
			# Static files
			m = self.rx_static_file.match(path)
			if m:
				ext = m.groups()[0].lower()
				if exists(join(self.basedir,path)):
					fpath = join(self.basedir,path)
					log.warning(fpath)
					fstat = os.stat(fpath)
					content_size = str(fstat.st_size)
					ftypeinfo = ext_map_content_type[ext]
					response_headers = [
						('Last-Modified',strftime("%a, %d %b %Y %H:%M:%S GMT",gmtime(fstat.st_mtime))),
						('Accept-Ranges', 'bytes'),
						('Content-Type', ftypeinfo['Content-Type']) ]
					tf = None
					if 'Content-Encoding' in ftypeinfo:
						response_headers += [('Content-Encoding',ftypeinfo['Content-Encoding'])]
						tf = tempfile.mktemp()
						zf = gzip.open(tf,'wb')
						ff = open(fpath,'rb')
						data = ff.read(4096)
						while data:
							zf.write(data)
							data = ff.read(4096)
						ff.close()
						zf.close()
						fpath = tf
						content_size = str(os.stat(tf).st_size)
					response_headers += [('Content-Length',content_size)]
					start_response(status, response_headers)
					f = open(fpath,'rb')
					data = f.read(4096)
					while data:
						yield data
						data = f.read(4096)
					if tf:
						os.unlink(fpath)
					raise StopIteration
				else:
					status = "404 Not Found"
					data = b'<h1>404 Not Found</h1>'
					response_headers = [
						('Content-Type', 'text/html; charset=UTF-8'),
						('Content-Length', str(len(data)) )]
					start_response(status, response_headers)
					yield data
					raise StopIteration

			locales = localization(self.translations_dir)
			ls = locales.lang_support()
			lang = None # Default
			default_lang = 'en'
			browser_langs = []
			if 'HTTP_ACCEPT_LANGUAGE' in environ:
				browser_langs = httpheader.parse_accept_language_header(environ['HTTP_ACCEPT_LANGUAGE'])
			for l in browser_langs:
				if lang:
					break
				for lp in l[0].parts:
					if lp in ls:
						lang = lp
						break
			if not lang:
				lang = default_lang
			
			template = environ['PATH_INFO'][1:]
			if template=='':
				template = 'main'
			template_info = {
				'tr':{},
				'tr_common':{},
				'sitename': self.conf.sitename,
				'sitetitle': self.conf.sitetitle
			}
			template_info['supported_countries'] = [
				{'short': 'dk', 'title': u'Danmark'},
				{'short': 'se', 'title': u'Sverige'},
				{'short': 'no', 'title': u'Norge'}
			]
			template_info.update(locales.tr(lang,'common',disambiguation='school'))
			template_info.update(locales.tr(lang,template,disambiguation='school'))
			template_info['tr_common'].update(locales.tr(lang,'common',disambiguation='school'))
			template_info['tr'].update(locales.tr(lang,template,disambiguation='school'))
			
			# Request translator
			def translate(source,context=template,comment=None,lang=lang,locales=locales):
				return locales.tr(lang,context=context,source=source,disambiguation=comment)

			subhandler = None
			subhandler_py = join(self.basedir,'subhandlers','%s.py' % template)
			if exists(subhandler_py):
				subhandler = imp.load_source('subhandlers.%s' % template, subhandler_py)
			
			response_headers = []

			environ['lang_support'] = locales.lang_support
			environ['tr'] = locales.tr
			environ['logger'] = log
			environ['lang'] = lang
			init = getattr(subhandler,'init',None)
			if init:
				init(template_info,response_headers,environ,translate,req_data)
			
			subhandler_redirect = getattr(subhandler,'redirect',None)
			if subhandler_redirect:
				cookies = []
				location = subhandler_redirect(template_info,cookies,environ)
				if location:
					output = redirect(location,cookies,start_response)
			
			template_info['translate'] = translate
			template = join(self.templates_dir,'%s.jinja' % template)
			if exists(template):
				jinja_temp = Template(PORTABLE_STRING(open(template,'rb').read(),'utf-8'))
				output = jinja_temp.render(template_info).encode('utf-8')
			else:
				output = b'Template: "%s" does not exist' % template if type(template)==PORTABLE_BYTES else template.encode('utf-8')
		except Exception as e:
			if type(e)==StopIteration:
				raise e
			log.warning(get_traceback())
			output = b'<h1>501 Internal Server Error</h1>'
			status = '501 Internal Server Error'
			response_headers = []
		
		response_headers += [
			('Content-type', 'text/html; charset=utf-8'),
			('Content-Length', str(len(output)))]
		
		start_response(status, response_headers)
		yield output

