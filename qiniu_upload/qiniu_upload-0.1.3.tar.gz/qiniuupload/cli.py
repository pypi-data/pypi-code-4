#-*- coding: utf-8 -*-
import sys
import optparse
from os import path
from remove import Remove
from upload import Upload
from qiniuupload import __version__

def remove():
    program = optparse.OptionParser(
        usage = 'qiniu_upload remove [OPTIONS]',
        add_help_option = False
    )
    program.add_option('--config', '-c', help = 'set config path')
    program.add_option('--prefix', '-p', help = 'prefix of remote files which you want to remove')

    options, arguments = program.parse_args()
    if options.config:
        if not path.exists(options.config):
            program.error('config file `%s` not found' % options.config)

        remove = Remove(options.config, options.prefix)
        remove.run()
    else:
        program.print_help()

def upload():
    program = optparse.OptionParser(
        usage = 'qiniu_upload upload [OPTIONS]',
        add_help_option = False
    )
    program.add_option('--config', '-c', help = 'set config path')
    program.add_option('--source', '-s', help = 'set local file(directory) path')

    options, arguments = program.parse_args()
    if options.config and options.source:
        if not path.exists(options.config):
            program.error('config file `%s` not found' % options.config)

        if not path.exists(options.source):
            program.error('local file(directory) `%s` not found' % options.source)

        upload = Upload(options.source, options.config)
        upload.run()
    else:
        program.print_help()

def main():
    program = optparse.OptionParser(
        usage = 'qiniu_upload COMMAND [OPTIONS]',
        add_help_option = False
    )
    program.add_option('--version', '-v', help = 'show version number', action = 'store_true')
    program.add_option('--help', '-h', help = 'show help message', action = 'store_true')

    options, arguments = program.parse_args()

    if options.version == True:
        print(__version__)
    else:
        program.print_help()
        print('\nCommands available:')
        print('upload: upload files to remote storage')
        print('remove: remove remote files\n')

def run():
    argv = sys.argv[1:]
    if 'upload' in argv:
        upload()
    elif 'remove' in argv:
        remove()
    else:
        main()