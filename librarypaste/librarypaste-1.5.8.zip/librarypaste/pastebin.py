# encoding: utf-8
import os
import datetime

import cherrypy
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.util import ClassNotFound
from mako.lookup import TemplateLookup
import imghdr

BASE = os.path.abspath(os.path.dirname(__file__))

lookup = TemplateLookup(directories=[os.path.join(BASE, 'templates')])

class LexerSorter(object):
    """Takes a list of preferred lexers, and sorts them at the top of the list."""
    def __init__(self, favored_languages):
        self.favored_langs = [x.lower().strip() for x in favored_languages]

    def sort_key_lex(self, l):
        key = l[0].lower()
        for f in self.favored_langs:
            if f in key:
                return 'aaaaaaaaaaaaaaaaaa' + key
        return key


class PasteBinPage(object):

    def form(self):
        d = {}
        page = lookup.get_template('entry.html')
        brand_name = cherrypy.request.app.config['branding']['name']
        add_branding(d)
        d['title'] = brand_name + " Paste"

        s = LexerSorter(cherrypy.request.app.config['lexers']['favorites'])
        d['lexers'] = sorted([(l[0], l[1][0]) for l in get_all_lexers()], key=s.sort_key_lex)

        d['pre_nick'] = ('' if not 'paste-nick' in cherrypy.request.cookie
            else cherrypy.request.cookie['paste-nick'].value)
        try:
            d['short'] = bool(int(cherrypy.request.cookie['paste-short'].value))
        except KeyError:
            d['short'] = True
        return page.render(**d)

    @cherrypy.expose
    def index(self, fmt=None, nick='', code=None, file=None, makeshort=None):
        if cherrypy.request.method != 'POST':
            return self.form()
        ds = cherrypy.request.app.config['datastore']['datastore']
        content = dict(
            nick = nick,
            time = datetime.datetime.now(),
            makeshort = bool(makeshort),)
        data = file != None and file.fullvalue()
        if data:
            filename = file.filename
            mime = unicode(file.content_type)
            content.update(
                type = 'file',
                mime = mime,
                filename = filename,
                data = data)
            imagetype = imghdr.what(filename, data)
        else:
            content.update(
                type = 'code',
                fmt = fmt,
                code = code,)
        (uid, shortid) = ds.store(**content)

        if nick:
            cherrypy.response.cookie['paste-nick'] = nick
            cherrypy.response.cookie['paste-nick']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days

        if makeshort:
            redirid = shortid
            cherrypy.response.cookie['paste-short'] = 1
            cherrypy.response.cookie['paste-short']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days
        else:
            redirid = uid
            cherrypy.response.cookie['paste-short'] = 0
            cherrypy.response.cookie['paste-short']['expires'] = 60 * 60 * 24 * 30  # store cookies for 30 days

        if content['type'] == 'file' and not imagetype:
            raise cherrypy.HTTPRedirect(cherrypy.url('file/'+redirid))
        else:
            raise cherrypy.HTTPRedirect(cherrypy.url(redirid))

class PasteViewPage(object):
    @cherrypy.expose
    def default(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        d = {}
        add_branding(d)
        page = lookup.get_template('view.html')
        try:
            paste_data = ds.retrieve(pasteid)
        except Exception, e:
            print e
            raise cherrypy.NotFound("The paste '%s' could not be found." % pasteid)
        if paste_data['type'] == 'file':
            cherrypy.response.headers['Content-Type'] = paste_data['mime']
            cherrypy.response.headers['Content-Disposition'] = 'inline; filename="%s"' % paste_data['filename']
            cherrypy.response.headers['filename'] = paste_data['filename']
            return paste_data['data']

        d['linenums'] = '\n'.join([str(x) for x in xrange(1, paste_data['code'].count('\n') + 2)])
        if paste_data['fmt'] == '_':
            lexer = get_lexer_by_name('text')
        else:
            try:
                lexer = get_lexer_by_name(paste_data['fmt'])
            except ClassNotFound:
                lexer = get_lexer_by_name('text')
        htmlformatter = HtmlFormatter(linenos='table')
        d['code'] = highlight(paste_data['code'], lexer, htmlformatter)
        d['pasteid'] = pasteid
        d['plainurl'] = cherrypy.url('plain/' + pasteid)
        d['homeurl'] = cherrypy.url('')
        d['title'] = 'Paste %s%s%s%s on %s' % (
            '%s aka ' % paste_data['shortid'] if 'shortid' in paste_data else '',
            paste_data['uid'] if 'uid' in paste_data else pasteid,
            ' (%s)' % paste_data['fmt'] if paste_data['fmt'] != '_' else '',
            ' by %s' % paste_data['nick'] if 'nick' in paste_data else '',
        paste_data['time'].strftime('%b %d, %H:%M'))
        return page.render(**d)

    exposed=True

    def __call__(self, pasteid=None):
        return self.default(pasteid)

class LastPage(object):
    @cherrypy.expose
    def default(self, nick=''):
        ds = cherrypy.request.app.config['datastore']['datastore']
        last = ds.lookup(nick)
        if not last:
            raise cherrypy.NotFound(nick)
        raise cherrypy.HTTPRedirect(cherrypy.url('/'+last))

class PastePlainPage(object):
    @cherrypy.expose
    def default(self, pasteid=None):
        ds = cherrypy.request.app.config['datastore']['datastore']
        paste_data = ds.retrieve(pasteid)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return paste_data['code']

class FilePage(object):
    @cherrypy.expose
    def default(self, pasteid=''):
        d = {}
        add_branding(d)
        page = lookup.get_template('file.html')
        d['title'] = "File link for %s" % pasteid
        d['link'] = cherrypy.url('/' + pasteid)
        return page.render(**d)

class AboutPage(object):
    @cherrypy.expose
    def index(self):
        d = {}
        add_branding(d)
        page = lookup.get_template('about.html')
        d['title'] = 'About Library Paste'
        d['about'] = '''
        <p>Library Paste is an open source library paste engine - you're using an example of it right now! It was originally created by Jamie Turner, and modified and open sourced by Chris Mulligan. Right now the closest thing to a home page is its BitBucket account: <a href="http://bitbucket.org/chmullig/librarypaste">http://bitbucket.org/chmullig/librarypaste</a></p>
        <p>Using Library Paste is really simple - it can do just a couple things. You can upload text/code/files, and you can view them. Each paste is identified by a UUID; or optionally by a 5 character short code. Just copy the URL you have and share it with whomever you want. You can view pastes simply by appending the paste ID (either one) to the main URL.</p>
        <p>Library Paste can also take files and share them. It will attempt to serve back the files with whatever MIME type they were uploaded with - so if you attach a picture it will come through as a picture. Although it has a long URL, if you try to download the file or save it the original URL will come through. Right now there are no explicit limits on file size, however the web server and/or client may enforce some.</p>
        <p>There are a few tools created to make pasting easier. They're on bitbucket at <a href="http://bitbucket.org/chmullig/librarypaste-tools">http://bitbucket.org/chmullig/librarypaste-tools</a>. In particularly the command line python script lpaste. It's available under pypi, so all you need to do is run <pre>easy_install lpaste</pre> on a *nix machine with setuptools installed (or pip install lpaste)..
        <p>One "hidden" feature is that you can find the last paste by a given nickname. You simple to go the url last/$username and you'll get redirected to their most recent paste, or given a 404 if it's not found. This is useful for IRC bots, for example.</p>
        <p>If you'd like your own, Library Paste is easy to setup. It's written in python using cherrypy, you can download the code at the bitbucket account listed above. If you have any feedback, questions or comments please send them along, via bitbucket, <a href="http://twitter.com/chmullig" alt="@chmullig on twitter">@chmullig</a> or chmullig@gmail.com.</p>
        '''
        return page.render(**d)

def add_branding(context):
    context.update(
        brand_name = cherrypy.request.app.config['branding']['name'],
        logo_src = cherrypy.request.app.config['branding']['logo source'],
    )
