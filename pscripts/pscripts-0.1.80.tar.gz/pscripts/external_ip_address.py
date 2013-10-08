#!/usr/bin/env python
import re, sys, shelve, simpledaemon, time, os, yaml, html.parser, urllib.request
import logging as log
from pdb import set_trace

ip_cache_file = '/tmp/.current_external_ip'
yaml_file = '/etc/external_ip_updater/urls.yaml'

#################################
# ENTRY POINT
def update_ddns_server(updater_urls="/etc/external_ip_updater/urls.yaml", update=True):
    external_ip = get_external_ip()
    log.debug("External IP address {}".format(str(external_ip)))

    ddns_urls = read_yaml_update_urls(updater_urls)
    for domain, update_url in ddns_urls.items():
        log.debug("For domain: {}, use update url: {}".format(domain,update_url))
        prev_ext_ip = read_ip_addy(domain)
        changed = ip_addy_changed(external_ip, prev_ext_ip)
        if changed:
            log.debug("IP changed")
            if update:
                log.debug("Updating domain: {} with IP: {}".format(domain, external_ip))
                touch_ddns_server(update_url)
                save_ip_addy(external_ip,domain)
            else:
                log.debug("Set to NOT update IP.")
        else:
            log.debug("IP not changed, wont DDNS update, or re-cache.")
        log.debug("---------")

def get_refresh_period(updater_urls="/etc/external_ip_updater/urls.yaml"):
    return get_yaml_setting(setting="refresh_period_seconds")

def flush_ip_cache_file():
    log.debug("Removing file: {}".format(ip_cache_file))
    os.remove(ip_cache_file)

#################################
# HELPERS

def get_yaml_setting(setting="urls"):
    f = open(yaml_file)
    url_updater_hash = yaml.load(f, Loader=yaml.CLoader)
    return url_updater_hash[setting]

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

def save_ip_addy(new_ip, domain):
    ip_updates = shelve.open(ip_cache_file)
    ip_updates[domain] = new_ip
    log.debug("Caching IP address: {}, under domain: {}".format(new_ip, domain))
    ip_updates.close

def read_ip_addy(domain):
    ip_updates = shelve.open(ip_cache_file)
    if ip_updates:
        if not domain in ip_updates:
            return None
        else:
            ip = ip_updates[domain]
            log.debug("Cached IP address: {} retrieved for domain: {}".format(ip, domain))
            return ip 

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

def read_yaml_update_urls(yaml_conf="/etc/external_ip_updater/urls.yaml"):
    f = open(yaml_conf)
    url_updater_hash = yaml.load(f, Loader=yaml.CLoader)
    return url_updater_hash["urls"]



#################################
# TESTS

def test_get_update_period():
    period = get_refresh_period()
    log.debug( "refresh period: {}".format(period))

def test_update_ip():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    # set_trace()
    update_ddns_server(updater_urls, update=False)

def test_yaml():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    ddns_urls = read_yaml_update_urls(updater_urls)
    for domain, update_url in ddns_urls.items():
        print("For domain: {}, use update url: {}".format(domain,update_url))
        

def test_extract_ip():
    set_trace()
    test_html=b'\t\t\t\t<span style="font-size: 1.4em">Your current IP-Adress: <font color="#FFFF33">110.168.32.26</font><br> \t\t\t\t\t\t\t\t<br>'
    ip = extract_ip(test_html)
    assert ip == "110.168.32.26"

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    #test_update_ip()
    test_get_update_period()




