#!/usr/bin/python
""" This is a simple example of how to query the HearPlanet API.
"""
import sys
from hearplanet.api import HearPlanet

def main():
    api = HearPlanet()
    articles = api.table('article').featured().depth('article').objects()
    for art in articles:
        print "%s (%s, %s)" % (art.title, art.lat, art.lng)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
