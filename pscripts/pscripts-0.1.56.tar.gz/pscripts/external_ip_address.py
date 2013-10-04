#!/usr/bin/env python
import re, sys
import logging as log
from pdb import set_trace
import urllib.request
import html.parser

ip_file = '/tmp/.current_external_ip'

#################################
# API
def update_ddns_server(update_url, verbose=False, update=True):
    external_ip = get_external_ip()
    if verbose:
        log.basicConfig(level=log.DEBUG)
    log.debug("External IP address {}".format(str(external_ip)))
    prev_ext_ip = read_ip_addy()
    log.debug("Old IP: {}".format(prev_ext_ip))
    save_ip_addy(external_ip)
    changed = ip_addy_changed(external_ip, prev_ext_ip)
    if changed:
        log.debug("IP changed")
        if update:
            log.debug("Updating IP")
            touch_ddns_server(update_url)

#################################
# HELPERS
def ip_addy_changed(external_ip, prev_ext_ip):
    if prev_ext_ip == None:
        return True
    if prev_ext_ip == external_ip:
        return False
    else:
        return True

def touch_ddns_server(url):
    log.debug("touching url: {}".format(url))
    resp = urllib.request.urlopen(url).read()
    log.debug("Response:\n{}".format(resp))

def save_ip_addy(ip):
    log.debug("Saving IP addy")
    f = open(ip_file, 'w')
    f.write(ip)

def extract_ip(html):
    # set_trace()
    ip_addy_regex = r"Your current IP-Adress:.*>(\d+\.\d+\.\d+\.\d+)"
    matches = re.search(ip_addy_regex, html.decode("utf-8", "ignore"))
    if not matches:
        print("Could not extract IP address from HTML:\n" + html)
        sys.exit(1)
    ip = matches.group(1)
    return ip

def get_external_ip():
    response = urllib.request.urlopen('http://www.ip-secrets.com/')
    html = response.read()
    ip = extract_ip(html)
    return ip

def read_ip_addy():
    try:
        f = open(ip_file, 'r')
    except FileNotFoundError:
        return None
    ip = f.read().strip()
    return ip

#################################
# TESTS

def test_extract_ip():
    set_trace()
    test_html=b'\t\t\t\t<span style="font-size: 1.4em">Your current IP-Adress: <font color="#FFFF33">110.168.32.26</font><br> \t\t\t\t\t\t\t\t<br>'
    ip = extract_ip(test_html)
    assert ip == "110.168.32.26"

if __name__ == '__main__':
    # set_trace()
    update_ddns_server(update_url="", verbose=True, update=False)



