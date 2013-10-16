from __future__ import absolute_import

import sys
import argparse

from selenium import webdriver

def create_parser():
    p = argparse.ArgumentParser(prog='image_check')
    p.add_argument("url")

    drivers = {'firefox','chrome','ie','opera'}
    p.add_argument("--driver", "-d", choices=drivers, default='firefox')

    return p

def main():
    p = create_parser()
    args = p.parse_args()

    driver = webdriver.Firefox()
    driver.get(args.url)

    page_urls = get_urls(driver)
    failed_urls = validate_urls(page_urls)

    if failed_urls:
        print "FAILED URLs:"
        print '\n'.join(failed_urls)
    else:
        print "All URLs returning 200."

if __name__ == '__main__':
    main()
