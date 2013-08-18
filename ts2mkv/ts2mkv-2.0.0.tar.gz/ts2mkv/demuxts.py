#!/usr/bin/python
import re
import os
import sys
import copy
import shutil

import common
import process
import metadata
import srtadjust

def _generate_Xini(fname, subpicturecolormodel, teletextpages):
    f = open(fname, 'wt')
    f.write('''
# Project-X INI
# ProjectX 0.90.04.00.b32 / 31.10.2009

# SubtitlePanel
SubtitlePanel.SubpictureColorModel=%s
SubtitlePanel.exportTextAsUTF8=1
SubtitlePanel.exportTextAsUnicode=0
SubtitlePanel.SubtitleExportFormat=SRT
SubtitlePanel.SubtitleExportFormat_2=null
SubtitlePanel.exportAsVobSub=1
SubtitlePanel.rebuildPTS=1
''' % (subpicturecolormodel))

    i = 1
    for teletextpage in teletextpages:
        f.write('SubtitlePanel.TtxPage%d=%s\n' % (i, teletextpage))
        i += 1

def demux(info_meta_data, all_tracks=False, gui=False):
    if info_meta_data:
        source_file_name = info_meta_data.source_file_name
        if os.path.exists(source_file_name + '(0).Xcl'):
            cutmarkers = source_file_name + '(0).Xcl'
        elif os.path.exists(source_file_name + '.Xcl'):
            cutmarkers = source_file_name + '.Xcl'
        else:
            cutmarkers = None

        base_name = os.path.abspath(os.path.splitext(os.path.split(source_file_name)[1])[0])
        xini = base_name + '.X.ini'

        if all_tracks:
            track_ids = info_meta_data.track_ids()
        else:
            track_ids = info_meta_data.selected_track_ids()

        subtitle_pages = []
        for track_id in track_ids:
            track = info_meta_data.get_track(track_id)
            if track.additional_information.has_key('teletext_page'):
                subtitle_pages.append(track.additional_information['teletext_page'])

        subtitlecolormodel = info_meta_data.additional_information['subpicture_color_model']
        _generate_Xini(xini, subtitlecolormodel, subtitle_pages)

        meta_data = copy.deepcopy(info_meta_data)
        meta_data.additional_information = {}
        pid = None
        srt_adjust_tasks = []
    else:
        meta_data = metadata.Metadata()
        track_ids = None
        xini = None
        cutmarkers = None
        source_file_name = None

    if os.path.abspath(common.modules_path()) != os.path.abspath(os.getcwd()):
        shutil.copy(os.path.join(common.modules_path(), 'colours.tbl'), os.getcwd())

    cmd = 'java'
    cmd += ' -jar "%s"' % (os.path.join(common.modules_path(), 'ProjectX.jar'))
    if track_ids:
        cmd += ' -id %s' % (",".join(track_ids))
    if xini:
        cmd += ' -ini "%s"' % (xini)
    if cutmarkers:
        cmd += ' -cut "%s"' % (cutmarkers)
    if gui:
        cmd += ' -gui'
        if source_file_name:
            source_file_name = os.path.abspath(source_file_name)
    else:
        cmd += ' -demux'
    if source_file_name:
        cmd += ' "%s"' % (source_file_name)
    cmd += ' -out .'

    for line in process.Process().execute_as_generator(cmd):
        sys.stderr.write(line)
        line = line.rstrip('\r\n')
        r = re.search('\+\+\>.*?PID\W(.+?)\W', line)
        if r:
            pid = "0x%.4X" % (int(r.group(1), 16))
        r = re.search('\-\-\-\> new File: (.+)', line)
        if r:
            track_fname = r.group(1)
            if track_fname.startswith("'") and track_fname.endswith("'"):
                track_fname = track_fname[1:-1]
            track = meta_data.get_track(pid)
            track.selected = True
            track.fname = os.path.abspath(track_fname)
            if track.type == metadata.TRACK_TYPE_SUBTITLE_VOBSUB:
                track.additional_files.append(track.fname)
                track.additional_files.append(track.fname + '.IFO')
                track.additional_files.append(track.fname + '.sub')
                track.fname += '.idx'
            elif track.type == metadata.TRACK_TYPE_SUBTITLE_SRT:
                if track.additional_information.has_key('teletext_time_correction'):
                    offset_ms = track.additional_information['teletext_time_correction']
                    name, ext = os.path.splitext(track.fname)
                    target_fname = '%s_adjusted%s' % (name, ext)
                    srt_adjust_tasks.append((track.fname, target_fname, offset_ms))
                    track.additional_files.append(track.fname)
                    track.fname = target_fname

    if os.path.abspath(common.modules_path()) != os.path.abspath(os.getcwd()):
        meta_data.additional_files.append('colours.tbl')

    if source_file_name:
        for fname, target_fname, offset_ms in srt_adjust_tasks:
            srtadjust.adjust_srt(open(fname), open(target_fname, 'w'), offset_ms)
        meta_data.additional_files.append(base_name + '_log.txt')
        meta_data.additional_files.append(xini)
        meta_data.delete_tracks_without_filename()
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
