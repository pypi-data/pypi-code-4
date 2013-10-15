import argparse
import logging
import sys

from .config import Config, import_config_module, get_configs_from_module
from .version import __version__

def parse_args(argv):
	parser = argparse.ArgumentParser(prog='configgen', description='generate a config file given a python module and set of options')
	parser.add_argument('--config', '-c', help='if there are multiple Config instances in the class structure, the value of this parameter specifies which one to output')
	parser.add_argument('--module', '-m', action='store_true', help='interpret the input parameter as a module import with dot notation, e.g. my.config.module, must be in python path')
	parser.add_argument('--option', '-o', action='append', help='an option string that will be used to choose between several options in a set (may be passed multiple times)')
	parser.add_argument('--printconfig', '-p', action='store_true', help='print the converted config object to the console')
	parser.add_argument('--squishee', '-s', action='store_false', dest='readable', help='make the converted config output less human-readable')
	parser.add_argument('--no-replace', '-n', action='store_false', dest='replace', help='do not do internal string replacement in the output')
	parser.add_argument('--verbose', '-v', action='store_true', help='increase console output')
	parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
	parser.add_argument('input', help='where to get input class structure, by default this expects a path to a file, also see help text for the --module option')
	parser.add_argument('output', nargs='?', help='optional, file to output generated info to, default prints to console')
	args = parser.parse_args(argv)
	# convert option to a set if passed
	if args.option is not None:
		args.option = frozenset(args.option)
	return args

def main():
	args = parse_args(sys.argv[1:])
	#print args

	# import the config module
	configModule = import_config_module(args.input, nameIsPyFile=not args.module)

	# find all Config instances in configModule, select the right one
	configInstances = get_configs_from_module(configModule)

	if args.config is None:
		keys = configInstances.keys()
		numKeys = len(keys)
		# exit with an error if there was more or less than one Config instance
		if numKeys == 0:
			print 'error: no Config instances found in module: {}'.format(args.input)
			sys.exit(1)
		elif numKeys > 1:
			print 'error: must use --config command line option; multiple Config instances found in module: {}'.format(args.input)
			sys.exit(1)
		else:
			configInstance = configInstances[keys[0]]
	else:
		try:
			configInstance = configInstances[args.config]
		except KeyError:
			print 'error: no config instance named "{}"'.format(args.config)
			sys.exit(1)

	# convert the config module to JSON and print it out
	jsonOutput = configInstance.convertToJson(options=args.option, replaceStrings=args.replace, prettyJson=args.readable)

	if args.printconfig:
		print jsonOutput

	if args.output is not None:
		with open(args.output, 'w') as outputFile:
			outputFile.write(jsonOutput)
