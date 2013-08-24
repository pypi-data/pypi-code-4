#! /usr/bin/env python

# Notification Center code borrowed from https://github.com/maranas/pyNotificationCenter/blob/master/pyNotificationCenter.py

VERSION =   '1.0.0'

import os, sys, json, re, hashlib, argparse, urllib, time, base64, ConfigParser

# disable import warnings
import warnings
warnings.filterwarnings('ignore')

DEFAULT_COLOR   =   '\033[0;0m'
ERROR_COLOR     =   '\033[01;31m'
ALERT_COLOR     =   '\033[01;33m'

def alert(text, error_code = None, color = None):
    if error_code is not None:
        sys.stderr.write('%s%s%s\n' % (color or ERROR_COLOR, text, DEFAULT_COLOR))
        sys.stderr.flush()
        sys.exit(error_code)
    else:
        sys.stdout.write('%s%s%s\n' % (color or DEFAULT_COLOR, text, DEFAULT_COLOR))
        sys.stdout.flush()

try:
    import pyrax
except ImportError:
    alert("Please install pyrax. `pip install pyrax`", os.EX_UNAVAILABLE)

pyrax.set_setting("identity_type", "rackspace")

try:
    import Foundation, objc
    notifications   =   True
except ImportError:
    notifications   =   False
    
if notifications:
    try:
        NSUserNotification          =   objc.lookUpClass('NSUserNotification')
        NSUserNotificationCenter    =   objc.lookUpClass('NSUserNotificationCenter')
    except objc.nosuchclass_error:
        notifications   =   False
        
def notify(env, text):
    alert(text)
    if notifications:
        notification    =   NSUserNotification.alloc().init()
        notification.setTitle_('rackup')
        notification.setSubtitle_(env)
        notification.setInformativeText_(text)
        notification.setUserInfo_({})
        if os.environ.get('D3PLOY_NC_SOUND'):
            notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(0, Foundation.NSDate.date()))
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)

if '-v' in sys.argv or '--version' in sys.argv:
    # do this here before any of the config checks are run
    alert('rackup %s' % VERSION, os.EX_OK, DEFAULT_COLOR)

config 	=	ConfigParser.ConfigParser()
if os.path.exists('.rackup'):
	config.read('.rackup')

CLOUDFILES_REGIONS 	=	['IAD', 'ORD', 'DFW', 'SYD']
DEFAULT_CONTAINER 	=	config.get('default', 'container') if config.has_section('default') else None
DEFAULT_REGION 		=	config.get('default', 'region') if config.has_section('default') and config.get('default', 'region') in CLOUDFILES_REGIONS else None
EXCLUDES 			=	[x.strip() for x in config.get('default', 'excludes').split(',')] if config.has_section('default') else []
if not '.git' in EXCLUDES:
	EXCLUDES.append('.git')
if not '.svn' in EXCLUDES:
	EXCLUDES.append('.svn')

parser          =   argparse.ArgumentParser()
parser.add_argument('container', help = "Which container to deploy to", nargs = "?", type = str, default = DEFAULT_CONTAINER)
parser.add_argument('-r', '--region', help = "Which region to use. 'ORD' if none is specified.", type = str, default = DEFAULT_REGION, choices = CLOUDFILES_REGIONS)
parser.add_argument('-e', '--environment', help = "Which environment to use. 'default' if none is specified.", type = str, default = 'default')
parser.add_argument('-f', '--force', help = "Upload all files whether they are currently up to date on Rackspace or not", action = "store_true", default = False)
parser.add_argument('--delete', help = "Remove orphaned files from Rackspace", action = "store_true", default = False)
parser.add_argument('-n', '--dry-run', help = "Show which files would be updated without uploading to S3", action = "store_true", default = False)
parser.add_argument('-v', '--version', help = "Print the script version and exit", action = "store_true", default = False)

pyrax.set_credential_file(os.path.expanduser('~/.rackspace'))
pyrax.set_setting('custom_user_agent', 'Rackup Python Script/%s' % VERSION)
pyrax.authenticate()
if not pyrax.identity.authenticated:
	alert('Your credentials failed to authenticate.', os.EX_UNAVAILABLE)

args            =   parser.parse_args()

if not args.environment in pyrax.list_environments():
	alert('"%s" is not a valid environment.' % args.environment, os.EX_UNAVAILABLE)
pyrax.set_environment(args.environment)

if not args.container:
	alert("You must pass a container as the first argument.", os.EX_NOINPUT, ERROR_COLOR)

cf = pyrax.connect_to_cloudfiles(region=args.region)

containers = cf.list_containers()
if not args.container in containers:
	alert('"%s" was not found in this accounts containers.' % args.container, os.EX_UNAVAILABLE, ERROR_COLOR)

def main():
	alert('Syncing files to "%s"' % args.container)
	cf.sync_folder_to_container('.', args.container, ignore = EXCLUDES, delete = args.delete, include_hidden = True)
	notify(args.container, 'Your files have been synced.')

if __name__ == "__main__":
    main()
