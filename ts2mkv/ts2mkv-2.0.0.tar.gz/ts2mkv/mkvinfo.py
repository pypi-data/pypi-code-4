#!/usr/bin/python
import re
import os
import sys

import process
import metadata

def get_info(fname):
    meta_data = metadata.Metadata()
    meta_data.source_file_name = fname

    track_id = None
    subtitle_found = False
    cmd = 'mkvinfo "%s"' % (fname)
    try:
        line_generator = process.Process().execute_as_generator(cmd)
        for line in line_generator:
            line = line.rstrip('\r\n')
            r = re.search('[+] Track number: (\d+)', line)
            if r:
                id = re.search('track ID for mkvmerge & mkvextract: (\d+)', line)
                if id:
                    track_id = int(id.group(1))
                else:
                    track_id = int(r.group(1))
                continue

            r = re.search('[+] Track type: (.+)', line)
            if r:
                track = meta_data.get_or_create_track(track_id)
                track_type = r.group(1)
                if track_type == 'video':
                    track.type = metadata.TRACK_TYPE_VIDEO
                elif track_type == 'audio':
                    track.type = metadata.TRACK_TYPE_AUDIO
                elif track_type == 'subtitles':
                    subtitle_found = True
                continue

            r = re.search('[+] Codec ID: (.+)', line)
            if r:
                track = meta_data.get_or_create_track(track_id)
                codec = r.group(1)
                track.additional_information['codec'] = codec
                if subtitle_found and 'S_TEXT' in codec:
                    track.type = metadata.TRACK_TYPE_SUBTITLE_SRT
                    subtitle_found = False
                elif subtitle_found and 'S_VOBSUB' in codec:
                    track.type = metadata.TRACK_TYPE_SUBTITLE_VOBSUB
                    subtitle_found = False
                continue

            r = re.search('[+] Language: (.+)', line)
            if r:
                track = meta_data.get_or_create_track(track_id)
                language = r.group(1)
                if language != 'und':
                    track.language = language
                continue
        meta_data.type = 'mkv'
    except:
        pass
    return meta_data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file name (.mkv)')
    parser.add_argument('-mo', metavar='METADATA_OUTPUT', dest='metadata_output_file', help='metadata output file name')
    args = parser.parse_args()

    meta_data_output = get_info(args.file)
    meta_data_output.dump(args.metadata_output_file)
