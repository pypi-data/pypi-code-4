#!/usr/bin/env python

import argparse

from s3imageresize import resize_image_folder

parser = argparse.ArgumentParser(description='Resize all images stored in a folder on Amazon S3.')
parser.add_argument('bucket', help="Name of the Amazon S3 bucket to save the backup file to.")
parser.add_argument('prefix', help="The prefix to add before the filename for the key.")
parser.add_argument('width', type=int, help="Maximum width of the image.")
parser.add_argument('height', type=int, help="Maximum height of the image.")
args = parser.parse_args()

resize_image_folder(args.bucket, args.prefix, (int(args.width), int(args.height)))
