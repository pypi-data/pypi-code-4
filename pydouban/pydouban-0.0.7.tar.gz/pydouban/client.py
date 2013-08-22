#encoding:utf-8
"""
Copyright 2013 TY<tianyu0915@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import logging
from hashlib import md5
import lxml.html
from exceptions import *
from http import HttpHanlder

logger = logging.getLogger(__name__)

class DoubanClient():

    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.user_key = md5(self.username).hexdigest()
        headers = { 
            'Host': 'www.douban.com',
            'User-Agent':  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:17.0) Gecko/17.0 Firefox/17.0',
            'Referer': 'http://www.douban.com',
        }
        self.http     = HttpHanlder(session_key=self.username,headers=headers)

    def is_loggedin(self,html=None):
        """ Check the account whether loggedin

        :param html: html string
        :return: True or False
        """

        return 'nav-user-account' in html

    def login_with_captcha(self,captcha):
        form_data = self.login_form_data
        form_data['captcha-solution'] = captcha

        html = self.http.post('https://www.douban.com/accounts/login',form_data)
        if not html:
            raise LoginError('http response is empty!')

        tree = lxml.html.fromstring(html)
        try:
            message = tree.xpath('.//p[@class="error"]')[0].text
        except:
            pass
        else:
            with open('error.html','wb') as f:
                f.write(html)
            raise LoginError(message)
        
        if self.is_loggedin(html):
            self.http.save_session()
            return True
        return False

    def login(self):
        """ Start login account. 

        Raise `LoginException` if can not login
        :return : True or False
        
        """
        html  = self.http.get('https://www.douban.com/')
        if self.is_loggedin(html):
            return True
        
        self.http.clear_tmp_db()
        html  = self.http.get('https://www.douban.com/accounts/login/')
        tree  = lxml.html.fromstring(html)

        def get_value(name,default=None):
            return tree.xpath('.//input[@name="{0}"]'.format(name))[0].get('value',default)

        form_data = {}
        form_data['source'] = get_value('source','')
        form_data['redir'] =  get_value('redir','')
        form_data['form_email'] = self.username
        form_data['form_password'] = self.password
        form_data['user_login'] = u'登录'
        form_data['remember']   = 'on'
        
        try:
            form_data['captcha-id'] = get_value('captcha-id')
        except:
            pass
        else:
            captcha_url = 'http://www.douban.com/misc/captcha?id={0}&size=s'.format(form_data['captcha-id'])
            self.login_form_data = form_data
            raise NeedCaptcha(captcha_url)

        html = self.http.post('https://www.douban.com/accounts/login',form_data)
        if not html:
            raise LoginError('http response is empty!')

        tree = lxml.html.fromstring(html)
        try:
            message = tree.xpath('.//p[@class="error"]')[0].text_content()
        except:
            pass
        else:
            raise LoginError(message)
        
        if self.is_loggedin(html):
            self.http.save_session()
            return True

        return False

    def get_doumails(self,unread=True):
        """ get doumails 
        
        """
        html = self.http.get('http://www.douban.com/doumail/')
        if not self.is_loggedin(html):
            self.login()
            return False

        tree = lxml.html.fromstring(html)
        if unread: 
            links = tree.xpath('.//div[@class="doumail-list"]//li[@class="state-unread"]//a[@class="url"]')
        else:
            links = tree.xpath('.//div[@class="doumail-list"]//li//a[@class="url"]')
        
        results = []
        for link in links:
            title = link.text_content()
            url   = link.get('href')
            results.append((url,title))

        return results

    def reply_doumail(self,url,content):
        html = self.http.get(url)
        if not self.is_loggedin(html):
            self.login()
            return False

        tree = lxml.html.fromstring(html)
        form_data = {}
        form_data['m_text'] = content
        form_data['ck'] = tree.xpath('.//form//input[@name="ck"]')[0].get('value')
        form_data['action'] = 'm_reply'
        form_data['captcha-id'] = ''
        form_data['captcha-solution'] = ''

        html = self.http.post(url,form_data)
        if html:
            return True

    def get_topics(self,url='http://www.douban.com/group/',is_new=False):
        """ Return a list that contains url and title
        
        exp:
            [
              ('http://douban.com/a/b/c/','abc')
              ('http://douban.com/d/e/f/','def')
            ]
        
        """
        url  = 'http://www.douban.com/group/'
        html = self.http.get(url)

        if not self.is_loggedin(html):
            self.login()
            return []

        try:
            tree = lxml.html.fromstring(html)
        except Exception,e:
            raise ValueError(e)

        urls = []
        for tr in tree.xpath('.//tr'):
            tds = tr.xpath('./td')
            if len(tds) <> 4:
                continue

            a      = tds[0].xpath('./a')[0]
            url    = a.get('href')
            title  = a.text
            if is_new and tds[1].text_content()== u'0回应':
                urls.append((url,title))
            elif not is_new:
                urls.append((url,title))

        return urls

    def reply_topic(self,url,content,sofa=False):
        """ Reply one topic 

        :param url: the topic url
        :param content: content you want to be posted
        :param sofa: occupy sofa
        :return : True or False
        
        """
        if not url:
            return
        html = self.http.get(url)
        if not self.is_loggedin(html):
            self.login()
            return False

        tree = lxml.html.fromstring(html)
        comment_list = tree.xpath('.//ul[@id="comments"]/li')
        if sofa and len(comment_list) >= 1:
            return False

        #title = tree.xpath('.//title')[0].text_content()
        form_data = {}
        form_data['rv_comment'] = content

        # need captcha ?
        for img in tree.xpath('.//img'):
            if img.get('src','').startswith('http://www.douban.com/misc/captcha?id='):
                captcha_url = img.get('src','')
                raise NeedCaptcha(captcha_url)
                
        for input in tree.xpath('.//input[@type="hidden"]'):
            k = input.get('name')
            v = input.get('value')
            form_data[k] = v
        
        html = self.http.post(url + 'add_comment#last',form_data)
        try:
            tree = lxml.html.fromstring(html)
        except:
            pass
        else:
            error = tree.xpath('.//div[@class="attn"]')
            if error:
                logger.error('error',error[0].text_content())
                return False

        if html:
            return True
        return False
        

