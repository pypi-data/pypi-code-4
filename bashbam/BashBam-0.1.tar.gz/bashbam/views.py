#!/usr/bin/env python

from os import system
from optparse import OptionParser
from controllers import add_script, rm_script, run_script, ls_scripts

def main():
	usage = """
bam <script>
bam add <gist path (user/gist_name)>
bam rm <script>
bam ls"""
	version = "0.1"
	parser = OptionParser(usage=usage, version="BashBam v%s" % version)

	parser.add_option("-g", "--global", action="store_true", dest="global_dir", 
		help="Perform action on the global bam scripts. (ignore virtual env)")

	(options, args) = parser.parse_args()

	if len(args) < 1:
		parser.print_version()
		print ""
		parser.print_usage()
		return 0

	if args[0] == 'add':
		if not args[1]:
			print "Please provide a gist path (user/gist_name)."
			return -1
		return add_script(origin=args[1], global_dir=options.global_dir)

	if args[0] == 'rm':
		if not args[1]:
			print "Please provide a script name."
			return -1
		return rm_script(args[1], options.global_dir)

	if args[0] == 'ls':
		return ls_scripts(options.global_dir)

	return run_script(args[0], options.global_dir)


if __name__ == '__main__':
    main()