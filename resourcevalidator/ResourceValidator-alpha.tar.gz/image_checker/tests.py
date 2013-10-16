from selenium import webdriver
from twisted.trial import unittest

import requests

from image_checker.core import get_urls, check_url

class ValidateImages(unittest.TestCase):
    '''This is an example case that will check a single URL to assure that there are no dead images contained therein.'''

    def setUp(self):
        '''Set self.url to the URL of the single page to be checked.'''
        self.url = 'http://example.com'

    def test_valid_links(self):
        driver = webdriver.Firefox()
        driver.get(self.url)
        image_urls = get_urls(driver)
        failed_urls = []
        for url in image_urls:
            if not check_url(url):
                failed_urls.append(url)
        msg = "Page contains invalid URLs. Use the `image_check` utility manually on {} for a full listing.".format(self.url)
        self.fail(msg)
