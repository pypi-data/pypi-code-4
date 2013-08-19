#!/usr/bin/python
import sys
import os
import ConfigParser

import commonargparse
import common
import mkvinfo
import demuxmkv
import encodetracks
import muxmkv
import process
import checkenv

def main():
    config = ConfigParser.ConfigParser()
    config.read(common.config_files('mkvenc.ini'))

    argument_parser = commonargparse.CommonArgumentParser(config, '.mkv')
    args = argument_parser.parse_args()

    matching_files = common.expand_wildcards(args.file)
    if len(matching_files) == 0:
        argument_parser.error('No matching file(s) found')

    p = process.Process()
    for fname in matching_files:
        if os.path.exists(fname):
            mkv_out_base_name = os.path.abspath(os.path.split(os.path.splitext(fname)[0])[1])
            if os.path.abspath(fname) == mkv_out_base_name + '.mkv':
                mkv_out_base_name += '_enc'
            mkv_out_fname = mkv_out_base_name + '.mkv'
            if args.logging_enabled:
                p.reset_log(mkv_out_base_name + '.log')
            meta_data_mkv = mkvinfo.get_info(fname)
            if meta_data_mkv.type is None:
                print "Error: File doesn't seem to be a valid Matroska file:", fname
                continue
            if args.info:
                meta_data_mkv.print_media_info()
            else:
                meta_data_demux = demuxmkv.demux(meta_data_mkv)
                meta_data_encode = encodetracks.encode(meta_data_demux, args.audio_preset, args.video_preset)
                muxmkv.mux_mkv(mkv_out_fname, meta_data_encode)
                if not args.no_cleanup:
                    meta_data_encode.delete_track_files()
                    meta_data_encode.delete_additional_files()
        else:
            print 'Warning: File no longer found:', fname

if __name__ == '__main__':
    main()
