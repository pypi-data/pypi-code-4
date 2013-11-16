from __future__ import print_function

import datetime
import argparse
import urllib
import os.path

import gdata
import gdata.data
import gdata.photos
import gdata.photos.service

# from gdata.photos.service import GPHOTOS_INVALID_ARGUMENT, GPHOTOS_INVALID_CONTENT_TYPE, GooglePhotosException

def download(username, password, directory, limit=None, force=False, delete_age=None):

    client = gdata.photos.service.PhotosService()
    client.email = username
    client.password = password
    client.source = 'picasa-fetcher'
    client.ProgrammaticLogin()

    now = datetime.datetime.utcnow()
    keep_going = True

    for photo in client.GetUserFeed(user=username, kind="photo", limit=limit).entry:
        url = photo.GetMediaURL()
        name = "%s.jpg" % photo.timestamp.isoformat().replace(':', '-')
        path = os.path.join(directory, name)
        
        if os.path.exists(path) and not force and keep_going:
            print(path, "already exists. Stopping downloads.")
            keep_going = False
        
        if keep_going:
            print("Downloading", url, "as", name)
            urllib.urlretrieve(url, path)
        elif delete_age is None:
            # Nothing more to download and we won't be deleting anything, so stop
            break

        if delete_age is not None:
            age = now - photo.timestamp.datetime()
            if age.days >= delete_age:
                print("WARNING: Deleting", url, "as age was", age.days, "and time stamp was", photo.timestamp.datetime())
                client.Delete(photo)

        print()

def run():
    
    parser = argparse.ArgumentParser(description='Download images from Picasa')
    parser.add_argument('--username', dest='username', help='Picasa user name')
    parser.add_argument('--password', dest='password', help='Picasa password')
    parser.add_argument('--delete', metavar="DAYS", dest='delete_age', type=int, help='Delete pictures older than DAYS days')
    parser.add_argument('--limit', type=int, help='Download at most this many photos')
    parser.add_argument('--force', action="store_const", const=True, help='By default, the script stops as soon it finds a photo with a timestamp that was seen already. Set --force to always download everything.')
    
    parser.add_argument(metavar='images/', dest='directory', help='Directory to store images in')

    args = parser.parse_args()

    if not args.username or not args.password or not args.directory:
        parser.print_usage()
        return 1

    if args.delete_age:
        print("WARNING: Deleting all pictures older than", args.delete_age, "days")

    download(args.username, args.password, os.path.abspath(args.directory), args.limit, args.force, args.delete_age)

    print("Done")

    return 0
