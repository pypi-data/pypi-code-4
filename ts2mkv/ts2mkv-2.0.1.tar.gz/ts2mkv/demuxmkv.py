#!/usr/bin/python
import os
import sys
import copy

import process
import metadata

def demux(info_meta_data, all_tracks=False, gui=False):
    source_file_name = info_meta_data.source_file_name

    if all_tracks:
        track_ids = info_meta_data.track_ids()
    else:
        track_ids = info_meta_data.selected_track_ids()

    meta_data = copy.deepcopy(info_meta_data)
    meta_data.additional_information = {}

    base_name = os.path.splitext(os.path.split(source_file_name)[1])[0]

    chapters_file_name = '%s_chapters.xml' % (base_name)
    process.Process().execute(r'mkvextract chapters "%s" >"%s"' % (source_file_name, chapters_file_name))
    if os.path.getsize(chapters_file_name) > 0:
        meta_data.chapters_file_name = chapters_file_name
    else:
        os.remove(chapters_file_name)

    cmd = 'mkvextract timecodes_v2 "%s" ' % (source_file_name)
    for track_id in track_ids:
        track = meta_data.get_track(track_id)
        if track.type == metadata.TRACK_TYPE_VIDEO:
            track_timecodes_fname = '%s_track_%d_%s_timecodes' % (base_name, track_id, track.type)
            cmd += '%d:"%s" ' % (track_id, track_timecodes_fname)
            track.timecodes_fname = track_timecodes_fname
    cmd += ' 1>&2'
    process.Process().execute(cmd)


    cmd = 'mkvextract tracks "%s" ' % (source_file_name)
    for track_id in track_ids:
        track = meta_data.get_track(track_id)
        track_fname = '%s_track_%d.%s' % (base_name, track_id, track.type)
        cmd += '%d:"%s" ' % (track_id, track_fname)
        if track.type == metadata.TRACK_TYPE_SUBTITLE_VOBSUB:
            track_base_name = os.path.splitext(os.path.split(track_fname)[1])[0]
            track.fname = track_base_name + '.idx'
            track.additional_files.append(track_base_name + '.sub')
        else:
            track.fname = track_fname
    cmd += ' 1>&2'
    process.Process().execute(cmd)

    return meta_data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-mi', metavar='METADATA_INPUT', dest='metadata_input_file', help='metadata input file name')
    parser.add_argument('-mo', metavar='METADATA_OUTPUT', dest='metadata_output_file', help='metadata output file name')
    parser.add_argument('-a', '--all', action="store_true", help='Demux all tracks')
    args = parser.parse_args()

    meta_data_input = metadata.Metadata.load(args.metadata_input_file)
    meta_data_output = demux(meta_data_input, args.all)
    meta_data_output.dump(args.metadata_output_file)
