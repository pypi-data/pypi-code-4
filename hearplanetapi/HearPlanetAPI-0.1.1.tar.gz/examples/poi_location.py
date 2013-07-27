#!/usr/bin/python
""" This is a simple example of how to query the HearPlanet API.
"""
import sys
from hearplanet.api import HearPlanet

def main():
    device_location = { 'lat':10.0, 'lng':5.5 }
    search_center = 'San Francisco, CA'

    api = HearPlanet()
    request = api.table('poi').search().depth('all')
    request = request.location(search_center)
    request = request.point(device_location)

    # limit to citysearch channel
    request = request.filters({'ch':'citysearch'})

    # get the first three pages (10 POI's per page) in three requests
    for page in (1, 2, 3):
        request = request.page(page)
        pois = request.objects()
        for poi in pois:
            # print the poi title and latitude and longitude.
            # distance is in meters, distance_str is formatted per locale.
            print "%s (%s, %s) %s" % (poi.title, poi.lat,
                poi.lng, poi.distance_str)

            # loop over the articles associated with the poi
            # if they have addresses, web sites or phone numbers
            # print them.
            for art in poi.articles:
                print "\t%s" % art.title
                for addr in getattr(art, 'addresses', []):
                    print '\tAddress:', addr.address
                for site in getattr(art, 'websites', []):
                    print '\tWebsite:', site.url
                for phone in getattr(art, 'phones', []):
                        print '\tPhone:', phone.phone


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
