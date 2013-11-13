import os
from datetime import datetime
import logging
import re
import urllib2
from urlparse import urlsplit

from BeautifulSoup import BeautifulSoup
from formencode import validators as fev
import html2text
from ming.utils import LazyProperty
from pylons import tmpl_context as c
from pylons import app_globals as g
from tg import (
        expose,
        flash,
        redirect,
        validate,
        )
from tg.decorators import (
        with_trailing_slash,
        without_trailing_slash,
        )

from allura.controllers import BaseController
from allura.lib import helpers as h
from allura.lib.decorators import require_post
from allura.lib.plugin import ImportIdConverter
from allura import model as M

from forgewiki.wiki_main import ForgeWikiApp
from forgewiki import model as WM

from forgeimporters.base import (
        ToolImporter,
        ToolImportForm,
        )
from forgeimporters.google import GoogleCodeProjectExtractor
from forgeimporters.google import GoogleCodeProjectNameValidator

TARGET_APP_ENTRY_POINT_NAME = 'Wiki'
DATE_FORMAT = '%a %b %d %H:%M:%S %Y'

log = logging.getLogger(__name__)

html2text.BODY_WIDTH = 0


class GoogleCodeWikiImportForm(ToolImportForm):
    gc_project_name = GoogleCodeProjectNameValidator()


class GoogleCodeWikiImportController(BaseController):
    def __init__(self):
        self.importer = GoogleCodeWikiImporter()

    @property
    def target_app(self):
        return self.importer.target_app

    @with_trailing_slash
    @expose('jinja:googlecodewikiimporter:templates/index.html')
    def index(self, **kw):
        return dict(importer=self.importer,
                target_app=self.target_app)

    @without_trailing_slash
    @expose()
    @require_post()
    @validate(GoogleCodeWikiImportForm(ForgeWikiApp), error_handler=index)
    def create(self, gc_project_name, mount_point, mount_label, **kw):
        if self.importer.enforce_limit(c.project):
            self.importer.post(
                    project_name=gc_project_name,
                    mount_point=mount_point,
                    mount_label=mount_label,
                    )
            flash('Wiki import has begun. Your new wiki will be available '
                    'when the import is complete.')
        else:
            flash('There are too many imports pending at this time.  Please wait and try again.', 'error')
        redirect(c.project.url() + 'admin/')


class GoogleCodeWikiComment(object):
    def __init__(self, soup):
        self.soup = soup

    @LazyProperty
    def _author(self):
        # class="userlink" could be on an `a` or `span` tag
        return self.soup.find('span', 'author').find(attrs={'class': 'userlink'})

    @LazyProperty
    def author_name(self):
        return self._author.text

    @LazyProperty
    def author_link(self):
        if not self._author.get('href'):
            return None
        return GoogleCodeProjectExtractor.BASE_URL + self._author['href']

    @LazyProperty
    def text(self):
        element = self.soup.find('div', 'commentcontent')
        return html2text.HTML2Text().handle(unicode(element))

    @LazyProperty
    def annotated_text(self):
        author = self.author_name
        if self.author_link:
            author = '[{0}]({1})'.format(self.author_name, self.author_link)
        author_snippet = u'Originally posted by: {0}'.format(author)
        return u'{0}\n\n{1}'.format(author_snippet, self.text)

    @LazyProperty
    def timestamp(self):
        return datetime.strptime(self.soup.find('span', 'date')['title'],
                DATE_FORMAT)


class GoogleCodeWikiPage(object):
    def __init__(self, name, url, project_name):
        self.name = name
        self.url = url
        self.project_name = project_name
        self.page = BeautifulSoup(urllib2.urlopen(self.url))

    def rewrite_wiki_links(self, text):
        wiki_path = os.path.dirname(urlsplit(self.url).path)
        pat = r'\[([^\]]+)\]\({0}/([^\)]+)\)'.format(wiki_path)
        def repl(match):
            return u'[{0}]({1})'.format(match.group(1), match.group(2))
        return re.sub(pat, repl, text)

    def rewrite_issue_links(self, text):
        pat = r'\[([^\]]+)\]\(/p/([^/]+)/issues/detail\?id=([^\)]+)\)'
        def repl(match):
            text, project, issue = match.groups()
            if project == self.project_name:
                repl_pat = u'[{text}](#{issue})'
            else:
                repl_pat = u'[{text}](https://code.google.com/p/{project}/issues/detail?id={issue})'
            return repl_pat.format(text=text, project=project, issue=issue)
        return re.sub(pat, repl, text)

    def rewrite_source_links(self, text):
        pat = r'\[([^\]]+)\]\(/p/([^/]+)/source/detail\?r=([^\)]+)\)'
        def repl(match):
            text, project, rev = match.groups()
            if project == self.project_name:
                repl_pat = u'[r{rev}]'
            else:
                repl_pat = u'[{text}](https://code.google.com/p/{project}/source/detail?r={rev})'
            return repl_pat.format(text=text, project=project, rev=rev)
        return re.sub(pat, repl, text)

    @LazyProperty
    def text(self):
        wiki_content = self.page.find(id='wikimaincol')
        orig = html2text.HTML2Text().handle(unicode(wiki_content))
        orig = self.rewrite_wiki_links(orig)
        orig = self.rewrite_issue_links(orig)
        orig = self.rewrite_source_links(orig)
        return orig

    @LazyProperty
    def timestamp(self):
        return datetime.strptime(self.page.find(id='wikiauthor').span['title'],
                DATE_FORMAT)

    @LazyProperty
    def labels(self):
        return [a.text for a in self.page.find(id='wikiheader').findAll(
            'a', 'label')]

    @LazyProperty
    def author(self):
        return self.page.find(id='wikiauthor').a.text

    @LazyProperty
    def comments(self):
        container = self.page.find(id='commentlist')
        if not container:
            return []
        return [GoogleCodeWikiComment(comment) for comment in
                container.findAll('div', 'artifactcomment')]


class GoogleCodeWikiExtractor(GoogleCodeProjectExtractor):
    PAGE_MAP = GoogleCodeProjectExtractor.PAGE_MAP
    PAGE_MAP.update({
        'wiki_index': GoogleCodeProjectExtractor.BASE_URL + '/p/{project_name}/w/list',
        })

    def get_wiki_pages(self):
        page = self.get_page('wiki_index')
        RE_WIKI_PAGE_URL = r'^/p/{0}/wiki/.*$'.format(self.project_name)
        seen = set()
        for a in page.find(id="resultstable").findAll("a"):
            if re.match(RE_WIKI_PAGE_URL, a['href']) and a['href'] not in seen:
                yield (a.text, self.BASE_URL + a['href'])
                seen.add(a['href'])

    def get_default_wiki_page_name(self):
        page = self.get_page('wiki_index')
        a = page.find(id='mt').find('a', 'active')
        if not a:
            return None
        path = urlsplit(a['href']).path
        if path.split('#')[0].endswith('/w/list'):
            return None
        return path.split('/')[-1].split('#')[0]


class GoogleCodeWikiImporter(ToolImporter):
    target_app = ForgeWikiApp
    source = 'Google Code'
    controller = GoogleCodeWikiImportController
    tool_label = 'Wiki'
    tool_description = 'Import your wiki pages from Google Code'

    def import_tool(self, project, user, project_name=None, mount_point=None,
            mount_label=None, **kw):
        """ Import a Google Code wiki into a new ForgeWiki app.

        """
        extractor = GoogleCodeWikiExtractor(project_name)
        default_wiki_page_name = extractor.get_default_wiki_page_name()
        if default_wiki_page_name is None:
            default_wiki_page_name = 'browse_pages'
        app = project.install_app(
                TARGET_APP_ENTRY_POINT_NAME,
                mount_point=mount_point or 'wiki',
                mount_label=mount_label or 'Wiki',
                import_id={
                        'source': self.source,
                        'project_name': project_name,
                    },
                )
        app.root_page_name = default_wiki_page_name
        try:
            with h.push_context(project._id,
                    mount_point=app.config.options.mount_point):
                has_home = False
                for page in self.get_pages(extractor):
                    self.create_page(page)
                    if page.name == 'Home':
                        has_home = True
                if not has_home:
                    self.delete_page('Home')
            M.AuditLog.log(
                    'import tool %s from %s on %s' % (
                        app.config.options.mount_point,
                        project_name, self.source),
                    project=project, user=user, url=app.url)
            g.post_event('project_updated')
            return app
        except Exception as e:
            h.make_app_admin_only(app)
            raise

    def get_pages(self, extractor):
        for name, url in extractor.get_wiki_pages():
            yield GoogleCodeWikiPage(name, url, extractor.project_name)

    def create_page(self, page):
        global c
        p = WM.Page.upsert(page.name)
        p.viewable_by = ['all']
        p.text = page.text
        p.mod_date = page.timestamp
        p.labels = page.labels
        p.import_id = ImportIdConverter.get().expand(page.name, c.app)
        with h.push_config(c, user=M.User.anonymous()):
            ss = p.commit()
            ss.mod_date = ss.timestamp = page.timestamp
            for comment in page.comments:
                p.discussion_thread.add_post(text=comment.annotated_text,
                        timestamp=comment.timestamp,
                        ignore_security=True,
                        )

    def delete_page(self, page_name):
        global c
        page = WM.Page.query.get(app_config_id=c.app.config._id, title=page_name)
        page.delete()
