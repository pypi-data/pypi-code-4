#!/usr/bin/python
import pickle
import os
import sys

TRACK_TYPE_VIDEO = 'Video'
TRACK_TYPE_AUDIO = 'Audio'
TRACK_TYPE_SUBTITLE_VOBSUB = 'VobSub'
TRACK_TYPE_SUBTITLE_SRT = 'SRT'
TRACK_TYPE_UNKNOWN = 'Unknown'

class Track(object):
    def __init__(self,
                 id,
                 type=TRACK_TYPE_UNKNOWN,
                 language=None,
                 fname=None,
                 extra_mkv_parameters=None,
                 timecodes_fname=None,
                 selected=True,
                 additional_files=None,
                 additional_information=None
                 ):
        self.id = id
        self.type = type
        self.language = language
        self.fname = fname
        self.extra_mkv_parameters = extra_mkv_parameters
        self.timecodes_fname = timecodes_fname
        self.selected = selected
        self.additional_files = additional_files or []
        self.additional_information = additional_information or {}

    def __repr__(self):
        str = "metadata.Track("
        str += "id='%s'" % (self.id)
        str += ", type='%s'" % (self.type)
        if self.language:
            str += ", language='%s'" % (self.language)
        else:
            str += ", language=%s" % (self.language)
        if self.fname:
            str += ", fname='%s'" % (self.fname)
        else:
            str += ", fname=%s" % (self.fname)
        if self.extra_mkv_parameters:
            str += ", extra_mkv_parameters='%s'" % (self.extra_mkv_parameters)
        else:
            str += ", extra_mkv_parameters=%s" % (self.extra_mkv_parameters)
        if self.timecodes_fname:
            str += ", timecodes_fname='%s'" % (self.timecodes_fname)
        else:
            str += ", timecodes_fname=%s" % (self.timecodes_fname)
        str += ", selected=%s" % (self.selected)
        str += ", additional_files=%s" % (self.additional_files)
        str += ", additional_information=%s" % (self.additional_information)
        str += ")"
        return str

    def __str__(self):
        str = "Track id='%s'" % (self.id)
        str += ", type='%s'" % (self.type)
        if self.language:
            str += ", language='%s'" % (self.language)
        else:
            str += ", language=%s" % (self.language)
        str += ", selected=%s" % (self.selected)
        if self.fname:
            str += ", fname='%s'" % (os.path.split(self.fname)[1])
        else:
            str += ", fname=%s" % (self.fname)
        return str

    def delete_file(self):
        if os.path.exists(self.fname):
            os.remove(self.fname)

    def delete_additional_files(self):
        for fname in self.additional_files:
            if os.path.exists(fname):
                os.remove(fname)
        if self.timecodes_fname and os.path.exists(self.timecodes_fname):
            os.remove(self.timecodes_fname)

    def print_data(self):
        print '  Track ID:', self.id
        print '  Track type:', self.type
        print '  Language:', self.language
        print '  File name:', self.fname
        print '  Extra mkv parameters:', self.extra_mkv_parameters
        print '  Timecodes file name:', self.timecodes_fname
        print '  Selected:', self.selected
        print '  Additional information:'
        for information in self.additional_information:
            print '    %s: %s' % (information, self.additional_information[information])
        print '  Additional files:'
        for fname in self.additional_files:
            print '    %s' % (fname)

    def print_track_info(self):
        print '  Track ID:', self.id
        print '  Track type:', self.type
        print '  Language:', self.language
        print '  File name:', self.fname
        print '  Selected (automatically):', self.selected
        print '  Additional information:'
        for information in self.additional_information:
            print '    %s: %s' % (information, self.additional_information[information])

class Metadata(object):
    def __init__(self):
        self.type = None
        self._tracks = {}
        self.source_file_name = None
        self.chapters_file_name = None
        self.additional_files = []
        self.additional_information = {}

    def tracks(self):
        return self._tracks.values()

    def selected_tracks(self):
        return [track for track in self._tracks.values() if track.selected]

    def track_ids(self):
        return self._tracks.keys()

    def selected_track_ids(self):
        return [track_id for track_id in [track.id for track in self._tracks.values() if track.selected]]

    def get_track(self, track_id):
        return self._tracks[track_id]

    def get_or_create_track(self, track_id):
        if not self._tracks.has_key(track_id):
            self._tracks[track_id] = Track(track_id)
        return self._tracks[track_id]
    
    def delete_track(self, track_id):
        del self._tracks[track_id]
        
    def delete_tracks_without_filename(self):
        for track_id_to_delete in [track.id for track in self._tracks.values() if not track.fname]:
            del self._tracks[track_id_to_delete]

    def delete_track_files(self):
        for track in self._tracks.values():
            track.delete_file()
            track.delete_additional_files()

    def delete_additional_files(self):
        for fname in self.additional_files:
            if os.path.exists(fname):
                os.remove(fname)
        if self.chapters_file_name and os.path.exists(self.chapters_file_name):
            os.remove(self.chapters_file_name)

    def print_data(self, all=True):
        print 'Type:', self.type
        print 'Source file name:', self.source_file_name
        print 'Chapters file name:', self.chapters_file_name
        print 'Additional information:'
        for information in self.additional_information:
            print '  %s: %s' % (information, self.additional_information[information])
        print

        print 'Tracks:'
        for track in self._tracks:
            if self._tracks[track].selected or all:
                self._tracks[track].print_data()
                print

    def print_media_info(self):
        print 'Type:', self.type
        print 'Source file name:', self.source_file_name
        print 'Additional information:'
        for information in self.additional_information:
            print '  %s: %s' % (information, self.additional_information[information])
        print

        print 'Tracks:'
        for track in self._tracks:
            self._tracks[track].print_track_info()
            print

    def dump(self, output_file_name):
        if output_file_name:
            f = open(output_file_name, 'wb')
        else:
            f = sys.stdout
        data = self.type, self.source_file_name, self.chapters_file_name, self.additional_files, self.additional_information, self._tracks
        pickle.dump(data, f)

    @staticmethod
    def load(input_file_name):
        if input_file_name:
            f = open(input_file_name, 'rb')
        else:
            f = sys.stdin
        data = pickle.load(f)
        meta_data = Metadata()
        meta_data.type, meta_data.source_file_name, meta_data.chapters_file_name, meta_data.additional_files, meta_data.additional_information, meta_data._tracks = data
        return meta_data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-mi', metavar='METADATA_INPUT', dest='metadata_input_file', help='metadata input file name')
    parser.add_argument('-s', '--selected', action="store_true", help='Show selected tracks only')
    parser.add_argument('-l', '--list', action="store_true", help='List tracks only instead of full metadata')
    args = parser.parse_args()

    meta_data_input = Metadata.load(args.metadata_input_file)

    if args.list:
        if args.selected:
            for track in meta_data_input.selected_tracks():
                print track
        else:
            for track in meta_data_input.tracks():
                print track
    else:
        meta_data_input.print_data(not args.selected)
