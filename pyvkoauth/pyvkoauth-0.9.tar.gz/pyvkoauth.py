# -*- coding: utf-8 -*-
#
# Copyright 2013 Kurbanov A.N. <cordalace@gmail.com>
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import urllib
import urllib2
import urlparse

import lxml.html


def auth(email, password, client_id, scope):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(),
                                  urllib2.HTTPRedirectHandler())
    resp = opener.open('http://oauth.vk.com/oauth/authorize?redirect_uri='
                       'http://oauth.vk.com/blank.html&response_type=token'
                       '&client_id=%s&scope=%s&'
                       'display=wap' % (client_id, scope))
    doc = lxml.html.document_fromstring(resp.read())
    post_dict = {}
    for item in doc.xpath('/html/body//form//input[@type="hidden"]'):
        post_dict[item.attrib['name']] = item.attrib['value']
    post_dict['email'] = email
    post_dict['pass'] = password
    form_action = doc.xpath('/html/body//form')[0].attrib['action']
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    resp = opener.open(form_action, urllib.urlencode(post_dict))
    parsed_url = urlparse.urlparse(resp.geturl())
    if parsed_url.path == '/oauth/authorize':
        doc = lxml.html.document_fromstring(resp.read())
        form_action = doc.xpath('/html/body//form')[0].attrib['action']
        resp = opener.open(form_action, {})
    parsed_url = urlparse.urlparse(resp.geturl())
    if parsed_url.path != "/blank.html":
        raise RuntimeError("Authorization failed")
    answer = urlparse.parse_qs(parsed_url.fragment)
    for k in answer.keys():
        answer[k] = answer[k][0]
    return answer
