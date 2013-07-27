#!/usr/bin/python
""" This is a simple example of how to query the HearPlanet API.
"""
import sys
from hearplanet.api import HearPlanet

def main():
    # Set up the HearPlanet API with valid credentials.
    # They can be set in /etc/hearplanet.cfg or overridden in
    # ~/.hearplanet.cfg
    # ... and create the API object.
    api = HearPlanet()

    # Make a request for POI's located near (the center of) San Francisco
    req = api.table('poi').search().location('San Francisco, CA')

    page_num = 0
    index = 1
    while True:
        page_num += 1
        req = req.page(page_num)
        objects = req.objects()
        for obj in objects:
            _print_obj(index, obj)
            index += 1
        if not req.more():
            break

def _print_obj(index, obj):
    """ Print the representation of the object, which is simply
        the pretty-print version of the Python object.
    """
    print obj.title
    #print '%03d' % index, '-'*60
    #print obj

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
