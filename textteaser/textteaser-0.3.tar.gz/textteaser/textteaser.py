#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Jeffrey Goettsch and other contributors.
#
# This file is part of py-textteaser.
#
# py-textteaser is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# py-textteaser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with py-textteaser.  If not, see
# <http://www.gnu.org/licenses/>.


import logging
import requests

from . import exceptions
from . import urls


class TextTeaser(object):

    def __init__(self, apikey):
        """Initialize TextTeaser.

        Args:
            apikey: A string containing an API key for the TextTeaser
                API.

        """

        self.logger = logging.getLogger('{0}.{1}'.format(
            self.__module__, self.__class__.__name__))

        self.apikey = apikey

        self.status_code = None
        self.summary_id = None
        self.title = None
        self.sentences = None
        self.message = None

    def _headers(self):

        return {
            'X-Mashape-Authorization:': self.apikey,
        }

    def _parse_response(self, resp):

        self.status_code = resp.status_code

        try:
            rdict = resp.json()
        except ValueError:
            self.summary_id = None
            self.title = None
            self.sentences = None
            self.message = ''
        else:
            self.logger.debug('received response: {0}'.format(rdict))

            self.summary_id = rdict.get('summaryId', None)
            self.title = rdict.get('title', None)
            self.sentences = rdict.get('sentences', None)
            self.message = rdict.get('message', '')

    def _post(self, url, data, headers=None):

        if headers is None:
            headers = self._headers()

        self.logger.debug(
            'posting to url: {0} with data: {1}'.format(url, data))

        return requests.post(url, data, headers=headers)

    def _raise_exception(self, resp):

        if 'invalid mashape key' in self.message.lower():
            raise exceptions.APIKeyError(self.message, self.status_code)
        elif self.status_code == 500:
            raise exceptions.ServerError(self.status_code)
        else:
            resp.raise_for_status()

    def summarize(self, text=None, title=None, url=None, kwargs=None):
        """Summarize the given text.

        Args:
            text: A string containing the article to summarize. If
                empty, url is required. (Default: '')

            title: A string containg a title for the article. If empty,
                url is required. (Default: '')

            url: A string containing the URL whose content you want to
                summarize. If empty, text and title are required.
                (Default: '')

            kwargs: A dictionary with the following possible strings:
                category: A string containing the category of the
                    article.
                blog: A string containing the blog or source of the
                    article.

        Raises:
            textteaser.exceptions.APIKeyError

            textteaser.exceptions.ServerError

            requests.exceptions.HTTPError

        Returns:
            A list of strings, each being a sentence of the summary.

        """

        data = {
            'text': text,
            'title': title,
            'url': url,
        }
        if kwargs:
            data.update(kwargs)

        resp = self._post(urls.SUMMARIZE, data)
        self._parse_response(resp)

        if self.status_code != 200:
            self._raise_exception(resp)

        return self.sentences
