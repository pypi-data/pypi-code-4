#!/usr/bin/python
import re
import os
import sys
import ConfigParser

import common
import process
import metadata

def _get_demux_config(program, option, pid=None):
    demuxts_config = ConfigParser.ConfigParser()
    demuxts_config.read(common.config_files('tsdemux.ini'))

    section = '%s' % (program)
    if section in demuxts_config.sections():
        suboption = '%s.%s' % (option, pid)
        if demuxts_config.has_option(section, suboption):
            return demuxts_config.get(section, suboption)
        if demuxts_config.has_option(section, option):
            return demuxts_config.get(section, option)
    if demuxts_config.defaults().has_key(option):
        return demuxts_config.defaults()[option]

def get_info(fname):
    meta_data = metadata.Metadata()
    meta_data.source_file_name = fname

    program = None
    service_name = None
    service_provider = None
    cmd = 'avconv -i "%s"' % (fname)
    for line in process.Process().execute_as_generator(cmd, excepted_error_code=1):
        r = re.search('Program (\d+)', line)
        if r:
            meta_data.type = 'ts'
            program = r.group(1)

        r = re.search('service_name\W*\:\W*(.*)', line)
        if r:
            service_name = r.group(1)

        r = re.search('service_provider\W*\:\W*(.*)', line)
        if r:
            service_provider = r.group(1)

        r = re.search('Stream #.*?\[(.*?)\][(]?(.*?)[)]?: (.*?): (.*)', line)
        if r:
            meta_data.additional_information['program'] = program
            if service_name:
                meta_data.additional_information['service_name'] = service_name
            if service_provider:
                meta_data.additional_information['service_provider'] = service_provider
            subpicture_color_model = _get_demux_config(program, 'dvbsubpicturecolormodel')
            if subpicture_color_model:
                meta_data.additional_information['subpicture_color_model'] = subpicture_color_model

            pid, language, streamtype, details = r.groups()
            pid = "0x%.4X" % (int(pid, 16))

            track = meta_data.get_or_create_track(pid)

            if language:
                track.language = language

            track.additional_information['details'] = details

            if streamtype == 'Video':
                track.type = metadata.TRACK_TYPE_VIDEO
            elif streamtype == 'Audio':
                track.type = metadata.TRACK_TYPE_AUDIO
                if language and language in _get_demux_config(program, 'excludedaudiolanguages').split(','):
                    track.selected = False
            elif streamtype == 'Subtitle':
                subtitlemode = _get_demux_config(program, 'subtitlemode')
                if 'dvbsub' in details:
                    track.type = metadata.TRACK_TYPE_SUBTITLE_VOBSUB
                    if subtitlemode not in ['both', 'dvbsub']:
                        track.selected = False
                else:
                    track.type = metadata.TRACK_TYPE_SUBTITLE_SRT
                    teletext_page = _get_demux_config(program, 'teletextpage', pid)
                    if teletext_page:
                        track.additional_information['teletext_page'] = teletext_page
                    teletext_time_correction = _get_demux_config(program, 'teletexttimecorrection', pid)
                    if teletext_time_correction:
                        track.additional_information['teletext_time_correction'] = int(teletext_time_correction)
                    if subtitlemode not in ['both', 'teletext']:
                        track.selected = False
                if track.selected and language and language in _get_demux_config(program, 'excludedsubtitlelanguages').split(','):
                    track.selected = False

            else:
                meta_data.delete_track(pid)

    return meta_data
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file name (.ts)')
    parser.add_argument('-mo', metavar='METADATA_OUTPUT', dest='metadata_output_file', help='metadata output file name')
    args = parser.parse_args()

    meta_data_output = get_info(args.file)
    meta_data_output.dump(args.metadata_output_file)
