#!/usr/bin/env
"""ec2util performs common ec2 tasks on the command line. Written in Python, based on boto.

Usage:
  ec2util print (instances|snapshots|amis|sgroups)
  ec2util print volumes [<instance_id>]
  ec2util (start|stop) <instance_id>
  ec2util attach <volume_id> <instance_id> <mapping>
  ec2util detach <volume_id>
  ec2util enlarge <volume_id> <size>
  ec2util delete volume <volume_id>
  ec2util create snapshot <volume_id> <name>
  ec2util create volume <size> <zone> [<snapshot_id>]
  ec2util config
  ec2util (-h | --help)
  ec2util --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import os
import aws
import docopt
import ConfigParser

configLocation = "/etc/ec2util/config.cfg"
myAws = None

def getConfigSectionMap(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def config():
	parser = ConfigParser.SafeConfigParser()
	
	old_key = ""
	old_secret = ""
	old_region = "us-east-1"

	if not os.path.exists("/etc/ec2util"):
		os.mkdir("/etc/ec2util")
	if os.path.exists(configLocation):
		parser.read([configLocation])
		config = getConfigSectionMap(parser, 'main')

		old_key = config['aws_key']
		old_secret = config['aws_secret']
		old_region = config['aws_region']

	key = raw_input("Please provide the AWS Access Key[" + old_key + "]: ")
	secret = raw_input("Please provide the AWS Access Secret[" + old_secret + "]: ")
	region = raw_input("Please set the default region[" + old_region + "]: ")

	if key == "":
		key = old_key
	if secret == "":
		secret = old_secret
	if region == "":
		region = old_region

	cfgfile = open(configLocation,'w')
	if not parser.has_section('main'):
		parser.add_section('main')

	parser.set('main','aws_key', key)
	parser.set('main','aws_secret', secret)
	parser.set('main','aws_region', region)
	parser.write(cfgfile)
	cfgfile.close()

def connectToAws():
	parser = ConfigParser.SafeConfigParser()
	parser.read([configLocation])
	if not parser.has_section('main'):
		config()
		parser.read([configLocation])

	conf = getConfigSectionMap(parser, 'main')

	myAws = aws.aws(conf['aws_key'], conf['aws_secret'], conf['aws_region'])
	return myAws

def cli():
	
	args = docopt.docopt(__doc__, version='ec2util 0.1.5')

	if(args['config']):
		config()
		return

	global myAws
	myAws = connectToAws()

	if(args['detach']):
		myAws.detachVolume(args['<volume_id>'])
	if(args['attach']):
		myAws.attachVolume(args['<volume_id>'], args['<instance_id>'], args['<mapping>'])
	if(args['delete']):
		if args['volume']:
			myAws.deleteVolume(args['<volume_id>'])
	if(args['enlarge']):
		myAws.enlargeVolume(args['<volume_id>'], args['<size>'])

	if(args['create']):
		if(args['snapshot']):
			myAws.createSnapshot(args['<volume_id>'], args['<name>'])
		if(args['volume']):
			myAws.createVolume(args['<size>'], args['<zone>'], args['<snapshot_id>'])

	if(args['start']):
		myAws.startInstanceById(args['<instance_id>'])

	if(args['stop']):
		myAws.stopInstanceById(args['<instance_id>'])

	if(args['print']):
		if(args['volumes']):
			if(args['<instance_id>']):
				myAws.printVolumesForInstance(args['<instance_id>'])
			else:
				myAws.printVolumes()
		if(args['instances']):
			myAws.printInstances()
		if(args['snapshots']):
			myAws.printSnapshots()
		if(args['amis']):
			myAws.printImages()
		if(args['sgroups']):
			myAws.printSecurityGroups()


def main():
    try:
        cli()
    except KeyboardInterrupt :
        print ""
        sys.exit()

if __name__ == "__main__" :
    main()
