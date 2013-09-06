from utils import *
import urllib, urllib2, cookielib
import lxml.html
import re
import logging
import datetime

class WPBlog:

    logged_in = False
    upgrade_page_url = "/wp-admin/update-core.php"

    def __init__(self, domain, user, password):
        self.domain = domain
        self.user = user
        self.password = password
        self.cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        self.opener.addheaders = [('User-agent', 'Opera/9.80 (X11; Linux x86_64) Presto/2.12.388 Version/12.16')]

    def login(self):
        login_parameters = urllib.urlencode({'log': self.user, 'pwd': self.password})
        self.opener.open("http://www.%s/wp-login.php"%self.domain, login_parameters).close()
        if self.is_looged_in():
            self.logged_in = True
            return True
        raise LoginException('Login Error')

    def search_for_element_id(self, document_to_parse, element_id):
        document = lxml.html.document_fromstring(document_to_parse)
        doc = document.xpath("//@id=\'%s\'"%element_id)
        if doc:
            return True
        return False

    def find_element_xpath(self, document, xpath_exp):
        document = lxml.html.document_fromstring(document)
        element = document.xpath(xpath_exp)
        if element:
            return element
        return False

    def is_looged_in(self):
        response = self.opener.open('http://www.%s/wp-admin/index.php'%self.domain)
        if self.search_for_element_id(response.read(), 'loginform'):
            self.logged_in = False
            return False
        return True

    def open(self, url):
        return self.opener.open('http://www.%s%s'%(self.domain, url))

    def count_links(self, url='/'):
        document = self.open(url).read()
        data = lxml.html.document_fromstring(document)
        return int(len(list(data.iterlinks())))

    @loggedin
    def admin_open(self, url, data = None):
        return self.opener.open('http://www.%s%s'%(self.domain, url), data)

    @loggedin
    def check_if_upgradeable(self):
        upgrade_page = self.admin_open(self.upgrade_page_url).read()
        form = self.find_element_xpath(upgrade_page, "//form[contains(@action, 'do-core-upgrade')]")
        if not form:
            return False
        return True

    def get_nonce_filed(self, form):
        return form.xpath('//input[@name=\"_wpnonce\"]')[0].value

    def get_upgrade_version(self, form):
        return form.xpath('//input[@name=\"version\"]')[0].value

    @loggedin
    def get_plugin_updates_count(self):
        index_page = self.admin_open('/wp-admin/index.php').read()
        plugin_count = self.find_element_xpath(index_page,"//span[@class=\"plugin-count\"]")
        if len(plugin_count) > 0:
            return plugin_count[0].text
        return None

    @loggedin
    def get_current_version(self):
        index_page = self.admin_open('/wp-admin/index.php').read()
        body_class = self.find_element_xpath(index_page, '//body')[0].attrib['class']
        s = re.search('version-([0-9-]*)',body_class)
        if not s:
            return None
        return s.group(1).replace('-','.')

    @loggedin
    def send_upgrade_form(self, wponce, version):
        upgrade_form_params = {
            '_wpnonce':  wponce,
            'version': version,
            'locale': 'pl_PL',
            '_wp_http_referer': '/wp-admin/update-core.php',
            'upgrade': 'upgrade'
        }
        form_params = urllib.urlencode(upgrade_form_params);
        resp = self.admin_open('/wp-admin/update-core.php?action=do-core-upgrade', form_params)
        resp.read()
        if int(resp.getcode()) == 200:
            return True
        return False

    @loggedin
    def upgrade(self, check=True):
        links_before = self.count_links()
        upgrade_page = self.admin_open(self.upgrade_page_url).read()
        form_to_upgrade = self.find_element_xpath(upgrade_page, "//form[contains(@action, 'do-core-upgrade') and @name=\"upgrade\"]")
        if not form_to_upgrade:
            return False
        self.send_upgrade_form(self.get_nonce_filed(form_to_upgrade[0]), self.get_upgrade_version(form_to_upgrade[0]))
        links_after = self.count_links()
        if links_before == links_after or (links_before0) == links_after or (links_before+1) == links_after:
            return True
        return False

