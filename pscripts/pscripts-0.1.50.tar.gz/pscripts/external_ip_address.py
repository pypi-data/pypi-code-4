#!/usr/bin/env python
import re
from pdb import set_trace
import urllib.request
import html.parser

ip_file = '/tmp/.current_external_ip'

#################################
# API

def update_ddns_server(update_url):
    external_ip = get_external_ip()
    prev_ext_ip = read_ip_addy()
    if prev_ext_ip == None:
        return (True, external_ip, prev_ext_ip)
    if prev_ext_ip == external_ip:
        return
    else:
        return (True, external_ip, prev_ext_ip)
    

#################################
# HELPERS

def touch_ddns_server(url):
    urllib.request.urlopen(url)

def save_ip_addy(ip):
    f = open(ip_file, 'w')
    f.write(ip)

def extract_ip(html):
    # set_trace()
    ip_addy_regex = r"Your current IP-Adress:.*>(\d+\.\d+\.\d+\.\d+)"
    matches = re.search(ip_addy_regex, html.decode("utf-8", "ignore"))
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

def human_test_check_ip():
    changed, external_ip, prev_ip = ip_addy_changed()
    if changed:
        print ("old ip: " + prev_ip)
        print ("new ip: " + external_ip)
    else:
        print ("ip still: " + external_ip)
    # prev_ext_ip = read_ip_addy()
    # if prev_ext_ip == None:
    #     print("No previously saved external IP.")
    # else:
    #     print ("Previous external IP: " + prev_ext_ip)
    # save_ip_addy(external_ip)
    # saved_ext_ip = read_ip_addy()
    # print ("New saved external IP: " + saved_ext_ip)

if __name__ == '__main__':
    human_test_check_ip()


