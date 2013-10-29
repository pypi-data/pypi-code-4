# Copyright 2013, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Josef Skladanka <jskladan@redhat.com>

import requests
import json
import inspect

def __fname():
    frame = inspect.currentframe().f_back
    name = frame.f_code.co_name
    return name

class ResultsDBapiException(Exception):
    pass

class ResultsDBapi(object):
    def __init__(self, api_url):
        self.url = api_url

    def __raise_on_error(self, r):
        if not r.ok:
            try:
                raise ResultsDBapiException(r.json()['message'])
            except KeyError:
                r.raise_for_status()

    def create_job(self, ref_url, status = None, name = None):
        data = dict(ref_url = unicode(ref_url), status = status, name = name)

        url = "%s/jobs"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers = headers)
        self.__raise_on_error(r)

        return r.json()

    def update_job(self, id = None, href = None, status = None):
        """
        id or href required, href has preference if both are set
        """
        url = None
        if id:
            url = "%s/jobs/%s" % (self.url, id)
        if href:
            url = href
        if not url:
            raise TypeError("%s() requires either id or href parameter" % __fname())

        data = dict(status = status)

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.put(url, data=json.dumps(data), headers = headers)
        self.__raise_on_error(r)

        return r.json()


    def get_job(self, id = None, href = None):
        url = None
        if id:
            url = "%s/jobs/%s" % (self.url, id)
        if href:
            url = href
        if not url:
            raise TypeError("%s() requires either id or href parameter" % __fname())

        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_jobs(self, page = None, limit = None, since = None, status = None, name = None, load_results = False, **kwargs):
        url = "%s/jobs" % self.url

        params_all = dict(page = page, limit = limit, since = since, status = status, name = name)
        params = {key:value for key, value in params_all.iteritems() if value is not None}
        for key, value in params.iteritems():
            if type(value) in (list, tuple):
                params[key] = ','.join([unicode(v) for v in value])
            else:
                params[key] = unicode(value)
        if load_results is True:
            params['load_results'] = 'true'
        r = requests.get(url, params = params)
        self.__raise_on_error(r)

        r = r.json()
        return r


    def create_result(self, job_id, testcase_name, outcome, summary = None, log_url = None, **kwargs):
        url = "%s/results" % self.url

        data = dict(job_id = job_id,
                    testcase_name = testcase_name,
                    outcome = outcome,
                    summary = summary,
                    log_url = log_url,
                    result_data = kwargs)

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers = headers)
        self.__raise_on_error(r)

        return r.json()

    def get_result(self, id = None, href = None):
        url = None
        if id:
            url = "%s/results/%s" % (self.url, id)
        if href:
            url = href
        if not url:
            raise TypeError("%s() requires either id or href parameter" % __fname())

        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_results(self, page = None, limit = None, since = None, outcome = None, job_id = None, testcase_name = None, **kwargs):
        url = "%s/results" % self.url
        dirty = False
        params = dict(page = page, limit = limit, since = since, outcome = outcome, job_id = job_id, testcase_name = testcase_name)
        params.update(kwargs)
        params = {key:value for key, value in params.iteritems() if value is not None}
        for key, value in params.iteritems():
            if type(value) in (list, tuple):
                params[key] = ','.join([unicode(v) for v in value])
            else:
                params[key] = unicode(value)


        r = requests.get(url, params = params)
        self.__raise_on_error(r)

        r = r.json()
        return r

    def create_testcase(self, name, url):

        data = dict(name = name, url = url)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.post("%s/testcases" % self.url , data = json.dumps(data), headers = headers)
        self.__raise_on_error(r)

        return r.json()


    def update_testcase(self, name, url):
        data = dict(url = url)

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        rurl = "%s/testcases/%s" % (self.url, name)
        r = requests.put(rurl, data = json.dumps(data), headers = headers)
        self.__raise_on_error(r)

        return r.json()

    def get_testcase(self, name):
        url = "%s/testcases/%s" % (self.url, name)

        r = requests.get(url)
        self.__raise_on_error(r)

        return r.json()

    def get_testcases(self, page = None, limit = None, **kwargs):
        url = "%s/testcases" % self.url

        params = dict(page = page, limit = limit)
        params = {key:value for key, value in params.iteritems() if value is not None}

        r = requests.get(url, params = params)
        self.__raise_on_error(r)

        r = r.json()
        return r

