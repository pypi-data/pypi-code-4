#!/usr/bin/env python
import re
from pdb import set_trace
import urllib.request

def test_extract_ip():
    # set_trace()
    test_html='\t\t\t\t<span style="font-size: 1.4em">Your current IP-Adress: <font color="#FFFF33">110.168.32.26</font><br> \t\t\t\t\t\t\t\t<br>'
    ip = extract_ip(test_html)
    assert ip == "110.168.32.26"

def extract_ip(html):
# setup_version_pattern = r"(\w+=')(\d+.\d+.)(\d+)('.*)"
    ip_addy_regex = r"Your current IP-Adress:.*>(\d+\.\d+\.\d+\.\d+)"
    matches = re.search(ip_addy_regex, html)
    ip = matches.group(1)
    return ip

def get_external_ip():
    response = urllib.request.urlopen('http://www.ip-secrets.com/')
    html = response.read()
    ip = extract_ip(html)

    
    return html

if __name__ == '__main__':
    test_extract_ip()

def human_test_check_ip():
    external_ip = get_external_ip()
    print ("Checking in from IP#: %s " % external_ip) 

