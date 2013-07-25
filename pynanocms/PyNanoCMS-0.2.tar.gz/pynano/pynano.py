#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Generate static HTML
'''
import os, logging, json
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from md5 import md5

from django.conf import settings
from django import template
from django.template import Context, loader

from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger('pyNanoCMS')
# Создать обработчик консоли
handler = logging.StreamHandler()
file_handler = logging.FileHandler('pynano.log', 'w')
# Создать форматирование и настроить обработчик на его использование
formatter = logging.Formatter("%(asctime)s ::%(name)s::%(levelname)s:: %(message)s")
handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# Добавить обработчик к модулю ведения журнала
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


PROJECT_ROOT = os.path.realpath(os.path.dirname('.'))  # __file__))
prjpath = lambda * args: os.path.realpath(os.path.join(PROJECT_ROOT, *args))

TEMPLATE_DIR = prjpath('templates/')
STATIC_DIR = prjpath('static/')
OTHER_DIR = prjpath('other/')
PAGES_JSON = prjpath('pages.json')

STATIC_HTML_DIR = prjpath('site_static/')

PAGES = [
    {
    'page_id': 'index',
    'url': '/',
    'template': 'index.html',
    'context': {},
    },
    {
    'page_id': 'about',
    'url': '/about/',
    'template': 'about.html',
    'context': {},
    },
    {
    'page_id': 'faq_sub',
    'url': '/faq/дом.html',
    'template': 'faq.html',
    'context': {},
    },
]

# if __name__ == "__main__":
#    open(PAGES_JSON, 'w').write(json.dumps(PAGES,indent=True))


class GenHTML(object):
    def __init__(self, template_dir=None, static_html_dir=None, static_dir=None, other_dir=None):
        self.template_dir = os.path.realpath(os.path.dirname(template_dir)) or None
        self.static_dir = os.path.realpath(os.path.dirname(static_dir)) or None
        self.static_html_dir = os.path.realpath(os.path.dirname(static_html_dir)) or None
        self.other_dir = os.path.realpath(os.path.dirname(other_dir)) or None

        settings.configure(DEBUG=True, TEMPLATE_DEBUG=True, TEMPLATE_DIRS=(self.template_dir,))

    def render(self, template_path=None, template_string=None, context=None):
        '''
        render page with Django templates
        '''
        context = context or {}

        if template_string:
            t = template.Template(template_string)
        elif template_path:
            t = loader.get_template(template_path)
        else:
            return ''
        return t.render(Context(context))

    def load_template(self, path):
        '''
        '''
        if self.template_dir:
            full_path = os.path.realpath(os.path.join(self.template_dir, path))
        else:
            full_path = path
        return open(full_path).read()

    def render_file(self, file_path, context=None):
        '''
        '''
        return self.render(template_string=self.load_template(file_path), context=context)

    def save_HTML_file(self, data, addr):
        '''
        '''
        if addr.startswith('/'): addr = addr[1:]
        if not addr.endswith('.html') and not addr.endswith('/') and len(addr) > 1: addr = addr + '/'

        if addr.endswith('/') or not addr:
            url_path = addr
        else:
            url_path = '/'.join(addr.split('/')[:-1])
        full_path = os.path.realpath(os.path.join(self.static_html_dir, url_path))

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        if addr.endswith('/') or not addr:
            full_file_path = os.path.realpath(os.path.join(full_path, 'index.html'))
        else:
            full_file_path = os.path.realpath(os.path.join(full_path, addr.split('/')[-1]))

        try:
            file_content = open(full_file_path, 'r').read()
            if md5(file_content).hexdigest() != md5(data.encode("UTF-8")).hexdigest():
                open(full_file_path, 'w').write(data.encode("UTF-8"))
        except IOError:
            open(full_file_path, 'w').write(data.encode("UTF-8"))

    def _copy_dir(self, src, dst):
        try:
            copy_tree(src, dst, update=1)
        except DistutilsFileError as e:
            logger.warning(e)

    def copy_static(self, dir=None):
        dir = dir or self.static_dir
        self._copy_dir(dir, os.path.realpath(os.path.join(self.static_html_dir, 'static')))

    def copy_other(self, dir=None):
        dir = dir or self.other_dir
        self._copy_dir(dir, self.static_html_dir)

    def generate(self, pages=None):
        '''
        '''
        pages = pages or []
        urls = [(i['page_id'], i['url'],) for i in pages]
        urls = dict(urls)
        for page in pages:
            context = page.get('context', {})
            context.update(urls=urls)
            data = self.render(page.get('template', ''), context=context)
            self.save_HTML_file(data, page.get('url', ''))


class GenHTMLJinja2(GenHTML):
    def render(self, template_path=None, template_string=None, context=None):
        '''
        render page with jinja2 templates
        '''
        context = context or {}

        if template_string:
            template = Template(template_string)
        elif template_path:
            jinja2_env = Environment(loader=FileSystemLoader(self.template_dir))
            template = jinja2_env.get_template(template_path)
        else:
            return ''
        return template.render(**context)


if __name__ == "__main__":
    try:
        if not TEMPLATE_DIR and not STATIC_HTML_DIR:
            raise Exception('Need TEMPLATE_DIR and STATIC_HTML_DIR')

        gen_html = GenHTMLJinja2(
                                 template_dir=TEMPLATE_DIR + '/',
                                 static_html_dir=STATIC_HTML_DIR + '/',
                                 static_dir=STATIC_DIR + '/',
                                 other_dir=OTHER_DIR + '/'
                                 )

        pages = json.load(open(PAGES_JSON, 'r'))

        gen_html.generate(pages)
        gen_html.copy_static()
        gen_html.copy_other()
    except Exception as e:
        logger.error(e, exc_info=1, extra={})
