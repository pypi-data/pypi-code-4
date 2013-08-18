#!/usr/bin/python
import sys
import os
import ConfigParser
from string import Template
import copy

import common
import metadata
import process
import multiprocessing

def _get_commands(config, preset):
    return [value for key, value in config.items(preset) if key.startswith('command')]

def encode(meta_data, audio_preset=None, video_preset=None):
    audio_config = ConfigParser.ConfigParser()
    audio_config.read(common.config_files('audiopresets.ini'))
    video_config = ConfigParser.ConfigParser()
    video_config.read(common.config_files('videopresets.ini'))

    meta_data = copy.deepcopy(meta_data)
    for track in meta_data.tracks():
        if audio_preset and track.type == metadata.TRACK_TYPE_AUDIO:
            config = audio_config
            preset = audio_preset
        elif video_preset and track.type == metadata.TRACK_TYPE_VIDEO:
            config = video_config
            preset = video_preset
        else:
            continue
        encoded_fname = '%s.%s' % (os.path.splitext(track.fname)[0], config.get(preset, 'extension'))
        substitutes = {
            'input_file': '%s' % (track.fname),
            'cpu_count': '%s' % (multiprocessing.cpu_count()),
            'output_file': '%s' % (encoded_fname),
        }
        track.additional_files.append(track.fname)
        track.fname = encoded_fname
        for command in _get_commands(config, preset):
            cmd = Template(command).safe_substitute(substitutes)
            process.Process().execute(cmd)
        if config.has_option(preset, 'extramkvparameters'):
            track.extra_mkv_parameters = config.get(preset, 'extramkvparameters')
        if config.has_option(preset, 'cleanup_files'):
            cleanup_files = eval(Template(config.get(preset, 'cleanup_files')).safe_substitute(substitutes))
            track.additional_files.extend(cleanup_files)
    return meta_data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-mi', metavar='METADATA_INPUT', dest='metadata_input_file', help='metadata input file name')
    parser.add_argument('-mo', metavar='METADATA_OUTPUT', dest='metadata_output_file', help='metadata output file name')
    parser.add_argument('-a', '--audio-preset', help='audio preset')
    parser.add_argument('-v', '--video-preset', help='video preset')
    args = parser.parse_args()

    meta_data_input = metadata.Metadata.load(args.metadata_input_file)
    meta_data_output = encode(meta_data_input, args.audio_preset, args.video_preset)
    meta_data_output.dump(args.metadata_output_file)
