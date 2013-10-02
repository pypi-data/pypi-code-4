#!/usr/bin/env python

import argparse

from s3imageresize import resize_image_folder

parser = argparse.ArgumentParser(description='Upload a file to Amazon S3 and rotate old backups.')
parser.add_argument('bucket', help="Name of the Amazon S3 bucket to save the backup file to.")
parser.add_argument('prefix', help="The prefix to add before the filename for the key.")
parser.add_argument('psize', help="Path to the file to upload.")
args = parser.parse_args()

resize_image_folder(args.bucket, args.prefix, args.psize)
