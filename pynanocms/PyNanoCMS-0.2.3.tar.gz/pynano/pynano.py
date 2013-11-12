#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Generate static HTML
'''
import os
import sys
import subprocess
import time
import logging
import json
from md5 import md5
import argparse

from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError

from jinja2 import Environment, FileSystemLoader, Template


logger = logging.getLogger('pyNanoCMS')
handler = logging.StreamHandler()
file_handler = logging.FileHandler('pynano.log', 'w')
formatter = logging.Formatter("%(asctime)s ::%(name)s::%(levelname)s:: %(message)s")
handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


PROJECT_ROOT = os.path.realpath(os.path.dirname('.'))  # __file__))
prjpath = lambda * args: os.path.realpath(os.path.join(PROJECT_ROOT, *args))

TEMPLATE_DIR = prjpath('templates/')
STATIC_DIR = prjpath('static/')
OTHER_DIR = prjpath('other/')
PAGES_JSON = prjpath('pages.json')

STATIC_HTML_DIR = prjpath('site_static/')


class GenHTML(object):
    static_url = 'static'

    def __init__(self, template_dir=None, static_html_dir=None,
                 static_dir=None, other_dir=None, pages=None):
        self.template_dir = os.path.realpath(os.path.dirname(template_dir)) or None
        self.static_dir = os.path.realpath(os.path.dirname(static_dir)) or None
        self.static_html_dir = os.path.realpath(os.path.dirname(static_html_dir)) or None
        self.other_dir = os.path.realpath(os.path.dirname(other_dir)) or None
        self.pages = pages or None

    def render(self, template_path=None, template_string=None, context=None):
        '''
        render page with templates
        '''
        raise  NotImplementedError()

    def load_template(self, path):
        '''
        Load template file
        '''
        if self.template_dir:
            full_path = os.path.realpath(os.path.join(self.template_dir, path))
        else:
            full_path = path
        return open(full_path).read()

    def render_file(self, file_path, context=None):
        '''
        Render template
        '''
        return self.render(template_string=self.load_template(file_path), context=context)

    def _get_path_for_page(self, addr):
        '''
        Get full path for some URI
        '''
        if addr.startswith('/'):
            addr = addr[1:]

        if not addr.endswith('.html') and not addr.endswith('/') and len(addr) > 1:
            addr = addr + '/'

        if addr.endswith('/') or not addr:
            url_path = addr
        else:
            url_path = '/'.join(addr.split('/')[:-1])

        full_path = os.path.realpath(os.path.join(self.static_html_dir, url_path))

        if addr.endswith('/') or not addr:
            full_file_path = os.path.realpath(os.path.join(full_path, 'index.html'))
        else:
            full_file_path = os.path.realpath(os.path.join(full_path, addr.split('/')[-1]))

        return full_path, full_file_path

    def save_HTML_file(self, data, addr):
        '''
        Save generated HTML
        '''
        full_path, full_file_path = self._get_path_for_page(addr)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

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
        static_url = self.static_url
        self._copy_dir(dir, os.path.realpath(os.path.join(self.static_html_dir, static_url)))

    def copy_other(self, dir=None):
        dir = dir or self.other_dir
        self._copy_dir(dir, self.static_html_dir)

    def generate(self, pages=None):
        '''
        Common entry point
        '''
        pages = pages or self.pages or []
        urls = [(i['page_id'], i['url'],) for i in pages]
        urls = dict(urls)
        for page in pages:
            context = page.get('context', {})
            context.update(urls=urls)
            data = self.render(page.get('template', ''), context=context)
            self.save_HTML_file(data, page.get('url', ''))

    def _all_dir_files(self, path, prefix_dir=None):
        all_files = set()
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file).split(path)[1]
                if prefix_dir is not None:
                    file_path = file_path[:1] + os.path.join(prefix_dir, file_path[1:])
                all_files.add(file_path)
        return all_files

    def _all_pages_files(self):
        all_files = set()
        pages = self.pages or []
        urls = [i.get('url') for i in pages]

        for url in urls:
            dir_path, file_path = self._get_path_for_page(url)
            all_files.add(file_path.split(self.static_html_dir)[1])
        return all_files

    def clean(self):
        '''
        Remove trash in site files
        '''
        other = self._all_dir_files(self.other_dir)
        static = self._all_dir_files(self.static_dir, prefix_dir=self.static_url)
        pages = self._all_pages_files()

        static_site = self._all_dir_files(self.static_html_dir)

        trash = static_site - (other | static | pages)

        if trash:
            logger.info('Removing trash files:')
            for i in trash:
                logger.info('\t%s' % i)
                os.unlink(os.path.join(self.static_html_dir, i[1:]))
            logger.info('%d trash files was removed!' % len(trash))


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


def generate():
    '''
    Generate static site
    '''
    try:
        if not TEMPLATE_DIR and not STATIC_HTML_DIR:
            raise Exception('Need TEMPLATE_DIR and STATIC_HTML_DIR')

        pages = json.load(open(PAGES_JSON, 'r'))

        gen_html = GenHTMLJinja2(
            template_dir=TEMPLATE_DIR + '/',
            static_html_dir=STATIC_HTML_DIR + '/',
            static_dir=STATIC_DIR + '/',
            other_dir=OTHER_DIR + '/',
            pages=pages,
        )

        gen_html.generate()
        gen_html.copy_static()
        gen_html.copy_other()
        gen_html.clean()
    except Exception as e:
        logger.error(e, exc_info=1, extra={})


def file_filter(name):
    '''
    Filter for unnecessary files
    '''
    return (not name.endswith(".log")
            and
            not name.endswith(".swp")
            and
            not name.startswith(".")
            )


def file_times(path, static_html_dir):
    '''
    Generator for modified time of files
    '''
    for root, dirs, files in os.walk(path):
        if static_html_dir not in root:
            for file in filter(file_filter, files):
                yield os.stat(os.path.join(root, file)).st_mtime


def print_stdout(process):
    '''
    Print outs of process
    '''
    stdout = process.stdout
    if stdout != None:
        print stdout


def autoreload(command, monitoring_path, static_html_dir):
    '''
    Auto regerate site when some source file was changed
    '''
    # How often we check the filesystem for changes (in seconds)
    wait = 1

    # The process to autoreload
    process = subprocess.Popen(command, shell=True)

    # The current maximum file modified time under the watched directory
    last_mtime = max(file_times(monitoring_path, static_html_dir))

    try:
        while True:
            max_mtime = max(file_times(monitoring_path, static_html_dir))
            print_stdout(process)
            if max_mtime > last_mtime:
                last_mtime = max_mtime
                logger.info('Regenerating site...')
                generate()
            time.sleep(wait)
    except KeyboardInterrupt:
        process.kill()
        logger.info('Exit...')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--serve",
                        help="serve in real time",
                        action="store_true")
    args = parser.parse_args()

    if args.serve:
        logger.info('Generating site...')
        generate()
        logger.info('Start serve...')
        os.chdir(STATIC_HTML_DIR)
        autoreload('python -m SimpleHTTPServer 8000',
                   PROJECT_ROOT, STATIC_HTML_DIR)


    else:
        logger.info('Generating site...')
        generate()
