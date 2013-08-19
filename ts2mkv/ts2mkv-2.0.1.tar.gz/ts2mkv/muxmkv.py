#!/usr/bin/python
import os
import sys
import metadata
import process

def mux_mkv(out_file, meta_data):
    cmd = '%s -o "%s"' % ('mkvmerge', out_file)
    if meta_data.chapters_file_name:
        cmd += ' --chapters "%s"' % (meta_data.chapters_file_name)
    for track in meta_data.tracks():
        if track.language:
            cmd += ' --language 0:%s' % (track.language)
        if track.extra_mkv_parameters:
            cmd += ' %s' % (track.extra_mkv_parameters)
        if track.timecodes_fname:
            cmd += ' --timecodes 0:"%s"' % (track.timecodes_fname)
        cmd += ' "%s"' % (track.fname)
    process.Process().execute(cmd, excepted_error_code=None)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', metavar='OUTPUT_FILE', dest='output_file', help='output file name (.mkv)')
    parser.add_argument('-mi', metavar='METADATA_INPUT', dest='metadata_input_file', help='metadata input file name')
    args = parser.parse_args()

    meta_data_input = metadata.Metadata.load(args.metadata_input_file)

    if args.output_file:
        mkv_out_fname = args.output_file
    else:
        mkv_out_fname = os.path.split(os.path.splitext(meta_data_input.source_file_name)[0] + '.mkv')[1]

    mux_mkv(mkv_out_fname, meta_data_input)
