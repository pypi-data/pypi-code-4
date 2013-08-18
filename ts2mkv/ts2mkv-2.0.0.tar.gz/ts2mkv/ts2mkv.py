#!/usr/bin/python
import sys
import os
import ConfigParser

import commonargparse
import common
import tsinfo
import demuxts
import encodetracks
import muxmkv
import process

def main():
    config = ConfigParser.ConfigParser()
    config.read(common.config_files('ts2mkv.ini'))

    argument_parser = commonargparse.CommonArgumentParser(config, '.ts')
    argument_parser.add_argument('-p', '--projectx', help='launch ProjectX', action="store_true")
    args = argument_parser.parse_args()

    if args.projectx and args.info:
        argument_parser.error('Illegal parameter combination: --info and --projectx both given')

    matching_files = common.expand_wildcards(args.file)
    if len(matching_files) == 0:
        if args.projectx:
            meta_data_demux = demuxts.demux(None, gui=True)
            meta_data_demux.delete_additional_files()
        else:
            argument_parser.error('No matching file(s) found')

    p = process.Process()
    for fname in matching_files:
        if os.path.exists(fname):
            if args.logging_enabled:
                p.reset_log(os.path.split(os.path.splitext(fname)[0] + '.log')[1])
            meta_data_ts = tsinfo.get_info(fname)
            if meta_data_ts.type is None:
                print "Error: File doesn't seem to be a valid DVB Transport Stream file:", fname
                continue
            if args.projectx:
                meta_data_demux = demuxts.demux(meta_data_ts, gui=True)
                if not args.no_cleanup:
                    meta_data_demux.delete_track_files()
                    meta_data_demux.delete_additional_files()
            elif args.info:
                meta_data_ts.print_media_info()
            else:
                meta_data_demux = demuxts.demux(meta_data_ts)
                meta_data_encode = encodetracks.encode(meta_data_demux, args.audio_preset, args.video_preset)
                mkv_out_fname = os.path.split(os.path.splitext(fname)[0] + '.mkv')[1]
                muxmkv.mux_mkv(mkv_out_fname, meta_data_encode)
                if not args.no_cleanup:
                    meta_data_encode.delete_track_files()
                    meta_data_encode.delete_additional_files()
        else:
            print 'Warning: File no longer found:', fname

if __name__ == '__main__':
    main()
