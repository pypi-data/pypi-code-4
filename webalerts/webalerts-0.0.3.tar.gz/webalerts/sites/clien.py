# -*- coding: UTF-8 -*-
from collections import Iterable, OrderedDict
from datetime import datetime
from itertools import takewhile
from logging import getLogger
from operator import attrgetter
import re

import lxml.html

from webalerts import Browser, Post, ConfigurationError, LoginError, parse_html


class Clien(object):
    """
    Implementation for Clien_. It accepts the following configuration options:
    ``username``, ``password``, ``board_ids``.

    ``username`` and ``password`` are your Clien username and password.
    Some boards in Clien require login to view posts.

    ``board_ids`` is a list of identifiers of boards to watch. The identifier
    of a board can be found in its URL after ``bo_table=``. Currently boards in
    special forms are not supported such as *Photos*.

    As Clien does not provide public API, it works by parsing HTML markup of
    pages returned by the web server. It may not work at any time as the
    site owner has not explicitly granted scripted accesses to the site and
    the markup of the site is subject to change.

    .. _Clien: http://www.clien.net/

    """

    def __init__(self, config):
        self.config = config
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)
        self._api = ClienAPI(config.get('username'), config.get('password'))
        self._last_ids = {}

    def get_new_posts(self):
        posts = []
        board_ids = self.config.get('board_ids', [])
        if not isinstance(board_ids, Iterable):
            raise ConfigurationError('board_ids should be iterable')
        self.logger.debug('board_ids: %s', board_ids)
        for board_id in board_ids:
            for post_id in self._get_new_post_ids(board_id):
                post = self._api.get_post(board_id, post_id)
                if post:
                    self.logger.debug('New post: %s', post.url)
                    posts.append(post)
        posts.sort(key=attrgetter('published'))
        return posts

    def _get_new_post_ids(self, board_id):
        last_id = self._last_ids.get(board_id, None)
        post_ids = []
        page_no = 1
        while True:
            cp_post_ids = self._api.get_post_ids(board_id, page_no)
            post_ids.extend(cp_post_ids)
            if not cp_post_ids:
                # End of pages
                break
            if last_id is None or cp_post_ids[-1] <= last_id:
                # End of new posts
                break
            page_no += 1
        if post_ids:
            self._last_ids[board_id] = post_ids[0]
        if last_id is None:
            return []
        else:
            return list(takewhile(lambda post_id: post_id > last_id, post_ids))


class ClienAPI(object):

    def __init__(self, username=None, password=None):
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)
        self._browser = ClienBrowser(username, password)

    def get_post_ids(self, board_id, page_no):
        """
        Returns the post IDs in order they appear in the markup, which are
        assummed to be in decending order, newest first.

        """
        response = self._browser.get_page('board', board_id=board_id, page_no=page_no)
        doc = parse_html(response.content)
        post_ids = []
        for trow in doc.cssselect('tr.mytr'):
            tcells = trow.findall('td')
            if not tcells:
                self.logger.warning('no td elements in tr.mytr')
                continue
            views = tcells[-1].text_content()
            if views == '-':
                # Deleted post
                continue
            post_id_str = tcells[0].text_content()
            try:
                post_id = int(post_id_str)
            except ValueError:
                self.logger.warning('Post ID is not an integer: %s', post_id_str)
                continue
            post_ids.append(post_id)
        return post_ids

    def get_post(self, board_id, post_id):
        response = self._browser.get_page('post', board_id=board_id, post_id=post_id)
        doc = parse_html(response.content)
        for script in doc.xpath('//script/text()'):
            if u'잘못된접근입니다' in re.sub(r'\s', '', script) and 'history.go(-1)' in script:
                # post is deleted
                return
        try:
            title = doc.cssselect('.board_main > .view_title h4')[0].text_content()
            content_dom = doc.cssselect('.board_main > .view_content #writeContents')[0]
            content = content_dom.text_content()
            content_html = lxml.html.tostring(content_dom, encoding='utf-8').decode('utf-8',
                    errors='replace')
            # author_info is only shown when logged in
            author, author_id = (None, None)
            author_link = doc.cssselect('.board_main > .view_head > p.user_info > a[onclick]')
            if author_link:
                author, author_id = self._get_author_info(author_link[0].attrib['onclick'])
            published_str = doc.cssselect('.board_main > .view_head > p.post_info')[0] \
                    .text_content()
            published = self._get_published_time(published_str)
        except (IndexError, AttributeError):
            self.logger.warning('Markup is not as expected', exc_info=True)
        else:
            return Post(response.url, title, content, content_html, author, author_id, published)

    def _get_author_info(self, script):
        m = re.match(r"showSideView\(this, '(?P<id>[^']*)', '(?P<name>[^']*)'", script)
        if m:
            return m.group('name'), m.group('id')
        else:
            return None, None

    def _get_published_time(self, post_info):
        m = re.match(r' (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', post_info)
        if not m:
            return
        datetime_str = m.group(1)
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            self.logger.warning('Invalid published time: %s', datetime_str)


class ClienBrowser(Browser):

    BASE_URL = 'http://www.clien.net'
    QUERY_PATHS = {
        'board': ('/cs2/bbs/board.php', OrderedDict([
            ('board_id', 'bo_table'),
            ('page_no', 'page')
        ])),
        'post': ('/cs2/bbs/board.php', OrderedDict([
            ('board_id', 'bo_table'),
            ('post_id', 'wr_id')
        ])),
    }
    LOGIN_PATH = '/cs2/bbs/login_check.php'

    def _login(self, username, password):
        data = dict(mb_id=username, mb_password=password, url='/')
        url = ClienBrowser.BASE_URL + ClienBrowser.LOGIN_PATH
        self._request(url, method='post', data=data)
        response = self._request(ClienBrowser.BASE_URL + '/')
        doc = parse_html(response.content)
        if not doc.cssselect('#account .uid'):
            raise LoginError()

    def _login_required(self, response):
        doc = parse_html(response.content)
        scripts = doc.xpath('//script/text()')
        return (len(scripts) >= 2 and
                re.search(ur'alert.*로그인', scripts[0]) and
                re.search(ur'location\.replace', scripts[1]))
