#!/usr/bin/env python

import requests
import argparse
import datetime


def get_argparse():
    parser = argparse.ArgumentParser(description='Prints out current UBI votes data')
    parser.add_argument('countries', metavar='country', type=str, nargs='*',
        help='Country code')
    return parser.parse_args()

def get_data(url):
    r = requests.get(url)
    return r.json()

def print_data(data, countries):
    print "UBI data as of {}".format(datetime.datetime.now())
    for x in sorted(data['countries'], key=lambda k: float(k['percentage']), reverse=True):
        if not countries or x['code'] in countries:
            print '{name} ({code}): {count} out of {threshold} = {percentage} %'.format(**x)

if __name__ == "__main__":
    args = get_argparse()
    data = get_data("https://ec.europa.eu/citizens-initiative/REQ-ECI-2012-000028/public/mapdata.do")
    print_data(data, args.countries)
