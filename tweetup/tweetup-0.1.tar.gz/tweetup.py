#!usr/bin/env python

"tweetup module"

import sys	
import argparse
from twython import Twython	#required modules have been imported

parser = argparse.ArgumentParser(description='this is a twitter script to post media with a descrition.')	#creating a parser object
parser.add_argument('-f','--path/of/the/file', help='enter the file destination',required=True) 	
parser.add_argument('-d','--status',help='enter your status', required=True)
args = parser.parse_args() 	#adding the options for parser


APP_KEY='your consumer key' 	
APP_SECRET='your consumer secret'	#these credentials will be fetched post creating a app on https://dev.twitter.com

twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()	#getting the authentic access from twitter

OAUTH_TOKEN        = 'your Access token'
OAUTH_TOKEN_SECRET = 'your token secret'	#Oauth credentials


twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET)	#accessing the twitter profile



photo = open(args.file, 'rb')	#open the required media file from the user machine
twitter.update_status_with_media(status=args.status, media=photo) 	#uploading the status along with the media file


