import sys

from selenium import webdriver
from selenium.webdriver.common.by import By

import requests

def validate_urls(urls):
    '''Accepts a list of URLs and returns a list of URLs for which check_url() returns False.'''
    failed_urls = []
    for url in urls:
        if not check_url(url):
            failed_urls.append(url)
    return failed_urls

def get_urls(driver):
    '''Accepts a URL and returns a list of all src attributes on all img tags in the page.'''
    images = driver.find_elements(By.XPATH, "//img")
    image_urls = [i.get_attribute('src') for i in images]
    return image_urls

def check_url(url):
    '''Returns True if a URL is valid and accessible.'''
    res = requests.head(url)
    return res.status_code in [200] + range(300, 400)
