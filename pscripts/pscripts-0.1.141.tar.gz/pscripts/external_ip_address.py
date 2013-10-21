#!/usr/bin/env python
import re, sys, shelve, simpledaemon, time, os, yaml, html.parser, urllib.request
import logging as log
from pdb import set_trace
from urllib.error import URLError
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth
import requests
from subprocess import check_output

ip_cache_file = '/tmp/.current_external_ip'
yaml_file = '/etc/external_ip_updater/urls.yaml'

#################################
# ENTRY POINT
def update_ddns_server(updater_urls="/etc/external_ip_updater/urls.yaml", update=True):
    try:
        external_ip = get_ip()
        if external_ip == None:
            log.warn("Unable to determine external IP.  This may be temporary or not.  Verify this warning doesn't persist.")
            return
        log.debug("External IP address {}".format(str(external_ip)))            
        ddns_urls = read_yaml_update_urls(updater_urls)
        for domain, update_url in ddns_urls.items():
            log.debug("For domain: {}, the update url is: {}".format(domain,update_url))
            prev_ext_ip = read_ip_addy(domain)
            changed = ip_addy_changed(external_ip, prev_ext_ip)
            if changed:
                log.debug("IP changed")
                if update:
                    log.info("Updating domain: {} with IP: {}".format(domain, external_ip))
                    touch_ddns_server(update_url)
                    save_ip_addy(external_ip,domain)
                else:
                    log.debug("Set to NOT update IP.")
            else:
                log.debug("IP not changed, wont DDNS update, or re-cache.")
                log.debug("---------")
    except Exception as e:
        log.warn(e)
        return

def get_refresh_period(updater_urls="/etc/external_ip_updater/urls.yaml"):
    return get_yaml_setting(setting="refresh_period_seconds")

def flush_ip_cache_file():
    log.debug("Removing file: {}".format(ip_cache_file))
    if os.path.isfile(ip_cache_file):
        os.remove(ip_cache_file)

#################################
# HELPERS

def get_yaml_setting(setting="urls"):
    log.debug("reading file: {}".format(yaml_file))
    f = open(yaml_file)
    url_updater_hash = yaml.load(f)
    log.debug("yaml hash: {}".format(url_updater_hash))
    return url_updater_hash[setting]

def ip_addy_changed(external_ip, prev_ext_ip):
    if prev_ext_ip == None:
        return True
    if prev_ext_ip == external_ip:
        return False
    else:
        return True

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

def get_simple_webpage(url):
    log.debug("getting url: {}".format(url))
    resp = b''
    try:
        resp = urllib.request.urlopen(url).read()
    except URLError:
        log.warn("Unable to reach out to update url: {}".format(url))
        log.warn("Response was: {}".format(resp))
    log.debug("Response:\n{}".format(resp))
    return resp

def touch_ddns_server(url):
    log.debug("touching url: {}".format(url))
    resp = get_simple_webpage(url)
    log.debug("Response:\n{}".format(resp.decode("utf-8", "ignore")))

def read_yaml_update_urls(yaml_conf="/etc/external_ip_updater/urls.yaml"):
    urls = get_yaml_setting("urls")
    return urls

def get_ip():
    cmd = "curl icanhazip.com"
    output = "{}".format(check_output(cmd, shell=True).strip().decode("utf-8", "ignore"))
    return output

#################################
# TESTS

def test_get_ip():
    ip = get_ip()
    log.debug("IP is: {}".format(ip))

def test_get_update_period():
    period = get_refresh_period()
    log.debug( "refresh period: {}".format(period))

def test_update_ip():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    update_ddns_server(updater_urls, update=False)

def test_yaml():
    updater_urls = "/etc/external_ip_updater/urls.yaml"
    ddns_urls = read_yaml_update_urls(updater_urls)
    for domain, update_url in ddns_urls.items():
        print("For domain: {}, use update url: {}".format(domain,update_url))

def test_get_webpage():
    html = get_simple_webpage('http://www.ip-secrets.com/')

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    # test_update_ip()
    # test_get_update_period()
    test_get_ip()
