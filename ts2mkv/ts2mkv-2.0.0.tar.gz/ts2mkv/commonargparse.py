import argparse
import sys

import checkenv

class CommonArgumentParser(argparse.ArgumentParser):
    def __init__(self, config, file_ext):
        argparse.ArgumentParser.__init__(self)
        self.add_argument('file', nargs='*', help='input file name (%s) or search pattern' % (file_ext))
        self.add_argument('-a', '--audio-preset', help='audio preset', default=config.get('encoding', 'audiopreset'))
        self.add_argument('-v', '--video-preset', help='video preset', default=config.get('encoding', 'videopreset'))
        self.add_argument('-i', '--info', help='print media info', action="store_true")
        self.add_argument('-l', '--logging-enabled', help='force logging enabled', action="store_true", default=config.get('logging', 'enabled').lower() == True)
        self.add_argument('-nc', '--no-cleanup', help="don't cleanup files generated during the process", action="store_true")
        self.add_argument('--check-env', help='perform basic check that the environment is ok', action="store_true")
        self.add_argument('--list-presets', help='list available presets', action="store_true")

    def parse_args(self):
        args = argparse.ArgumentParser.parse_args(self)

        if args.check_env:
            checkenv.check_env()
            sys.exit(0)

        if args.list_presets:
            checkenv.print_presets()
            sys.exit(0)

        def raise_error(preset_type, preset_name):
            argparse.ArgumentParser.error(self, '%s preset not found: "%s". Use --list-presets to get the list of available presets.' % (preset_type, preset_name))

        if not checkenv.video_preset_found(args.video_preset):
            raise_error('Video', args.video_preset)
        if not checkenv.audio_preset_found(args.audio_preset):
            raise_error('Audio', args.audio_preset)

        return args
