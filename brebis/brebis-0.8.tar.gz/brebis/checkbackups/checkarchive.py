# -*- coding: utf-8 -*-
# Copyright © 2013 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Check an archive
'''Check an archive'''

import os
import stat
from logging import warn

import brebis.checkhashes

class CheckArchive(object):
    '''Check an archive'''

    def __init__(self, _cfgvalues, _options):
        '''The constructor of the CheckArchive class.

        _cfgvalues -- the expected values for the archive

        '''
        self._missing_files = []
        self._missing_equality = []
        self._missing_bigger_than = []
        self._missing_smaller_than = []
        self._unexpected_files = []
        self._mismatched_uids = []
        self._mismatched_gids = []
        self._mismatched_modes = []
        self._mismatched_types = []
        self._mismatched_targets = []
        self._mismatched_hashes = []
        self.__fileinfo = False
        self._main(_cfgvalues, _options)

    def _check_path(self, __arcinfo, _data):
        '''Check if the expected path exists in the archive'''
        for _ind, _file in enumerate(_data):
            if __arcinfo['path'] == _file['path']:
                # Tests of files in the archive and expected ones
                ### Compare the sizes of the file in the archive and the
                ### expected file
                self._compare_sizes(__arcinfo['size'], __arcinfo['path'], _file)
                ### Check if an unexpected file is in the archive
                self._check_unexpected_files(__arcinfo['path'], _file)
                ### Compare the uid of the file in the archive and the
                ### expected one
                if 'uid' in __arcinfo and 'uid' in _file:
                    self.__check_uid(__arcinfo['uid'], _file)
                ### Compare the gid of the file in the archive and the
                ### expected one
                if 'gid' in __arcinfo and 'gid' in _file:
                    self.__check_gid(__arcinfo['gid'], _file)
                ### Compare the filemode and the mode of the expected file
                if 'mode' in __arcinfo and 'mode' in _file:
                    self._check_mode(__arcinfo['mode'], _file)
                ### Compare the file type and the type of the expected file 
                if 'type' in __arcinfo and 'type' in _file:
                    self._check_type(__arcinfo['type'], _file)
                if 'target' in __arcinfo and 'target' in _file:
                    self._check_target(__arcinfo['target'], _file)
                ### Compare the hash of the file and the one of the expected file
                if 'hash' in _file:
                        self._check_hash(__arcinfo['path'], _file)
                # We reduce the number of files to work with
                del(_data[_ind])
        return _data

    def __extract_archive_info(self, __arcpath):
        '''Extract the archive file system information'''
        if not self.__fileinfo:
            try:
                self.__fileinfo = os.stat(__arcpath)
            except (OSError, IOError) as __msg:
                logging.warning(__msg)
        return self.__fileinfo

    def __find_archive_size(self, __arcpath):
        '''Find the size of the archive'''
        __fileinfo = self.__extract_archive_info(__arcpath)
        return __fileinfo.st_size

    def __find_archive_mode(self, __arcpath):
        '''Find the mode of the archive'''
        __fileinfo = self.__extract_archive_info(__arcpath)
        __mode= stat.S_IMODE(__fileinfo.st_mode)
        return __mode

    def __find_archive_uid_gid(self, __arcpath):
        '''Find the uid of the archive'''
        __fileinfo = self.__extract_archive_info(__arcpath)
        return __fileinfo.st_uid, __fileinfo.st_gid

    def _compare_sizes(self, _arcsize, _arcname, _file):
        '''Compare the sizes of the files in the archive and the expected
        files
        '''
        if 'equals' in _file and _arcsize != _file['equals']:
            self.missing_equality.append({'path': _arcname,
                'size': _arcsize, 'expected': _file['equals']})
        elif 'biggerthan' in _file and _arcsize < _file['biggerthan']:
            self.missing_bigger_than.append({'path': _arcname,
                'size': _arcsize, 'expected': _file['biggerthan']})
        elif 'smallerthan' in _file and _arcsize > _file['smallerthan']:
            self.missing_smaller_than.append({'path': _arcname,
                'size': _arcsize, 'expected': _file['smallerthan']})

    def _normalize_path(self, __path):
        '''Remove last slash of a directory path if present'''
        if __path.endswith('/'):
            return __path[:-1]
        else:
            return __path

    def _check_unexpected_files(self, __arcname, __file):
        '''Check if an unexpected file exists in the archive'''
        if 'unexpected' in __file:
            self.unexpected_files.append(__arcname)

    def __check_uid(self, __arcuid, __file):
        '''Check if the file uid in the archive matches the expected
        one
        '''
        if __file['uid'] != __arcuid:
            self.mismatched_uids.append({'path':__file['path'], 'expecteduid':__file['uid'], 'uid':__arcuid})

    def __check_gid(self, __arcgid, __file):
        '''Check if the file gid in the archive matches the expected
        one
        '''
        if __file['gid'] != __arcgid:
            self.mismatched_gids.append({'path':__file['path'], 'expectedgid':__file['gid'], 'gid':__arcgid})

    def _check_mode(self, __arcmode, __file):
        '''Check if the file mode in the archive matches the expected
        one
        '''
        __arcmode = oct(__arcmode).split('o')[-1]
        # if the file has no right, need to manipulate the output - solving #15
        if __arcmode == '0':
            __arcmode = '000'
        if __file['mode'] != __arcmode:
            self.mismatched_modes.append({'path': __file['path'], 'expectedmode': __file['mode'], 'mode': __arcmode})

    def _check_type(self, __arctype, __file):
        '''Check if the file type in the archive matches the expected
        one
        '''
        if __file['type'] != __arctype:
            self.mismatched_types.append({'path': __file['path'], 'expectedtype': __file['type'], 'type': __arctype})

    def _check_hash(self, __arcpath, __file):
        '''Check if the file hash in the archive matches the expected
        one
        '''
        __arcfile = self._extract_stored_file(__arcpath)
        __arcfilehash = brebis.checkhashes.get_hash(__arcfile, __file['hash']['hashtype'])
        self._report_hash(__file['path'], __file['hash']['hashvalue'],
            __arcfilehash)

    def _report_hash(self, __arcpath, __expectedhash, __archash):
        '''Check if the hashes are different and report the fact'''   
        if __expectedhash != __archash:
            self._mismatched_hashes.append({'path': __arcpath,
                'expectedhash': __expectedhash, 'hash': __archash})

    def _check_target(self, __arctarget, __file):
        '''Check if the target field in the archive matches the
        expected one
        '''
        if __file['target'] != __arctarget:
            self._mismatched_targets.append({'path': __file['path'], 'expectedtarget' : __file['target'], 'target': __arctarget})

    def _archive_checks(self, __arcdata, __arcpath):
        '''Launch the checks for the archive itself'''
        if __arcdata:
            # Store the path into archive data
            __arcdata['path'] = __arcpath
            # archive size
            if 'equals' in __arcdata or 'biggerthan' in __arcdata or 'smallerthan' in __arcdata:
                __arcsize = self.__find_archive_size(__arcdata['path'])
                self._compare_sizes(__arcsize, __arcdata['path'], __arcdata)
            # archive hash
            if 'hash' in __arcdata:
                with open(__arcdata['path'], 'rb') as __archive:
                    __archash = brebis.checkhashes.get_hash(__archive, __arcdata['hash']['hashtype'])
                    self._report_hash(__arcdata['path'], __arcdata['hash']['hashvalue'], __archash)
            # archive mode
            if 'mode' in __arcdata:
                __arcmode = self.__find_archive_mode(__arcdata['path'])
                self._check_mode(__arcmode, __arcdata)
            # archive uid and gid
            if 'uid' in __arcdata:
                __arcuid, _ = self.__find_archive_uid_gid(__arcdata['path'])
                self.__check_uid(__arcuid, __arcdata)
            if 'gid' in __arcdata:
                _, __arcgid = self.__find_archive_uid_gid(__arcdata['path'])
                self.__check_gid(__arcgid, __arcdata)

    @property
    def missing_equality(self):
        '''A list containing the paths of the files missing the
        equality parameters in the archive
        '''
        return self._missing_equality

    @property
    def missing_files(self):
        '''A list containing the paths of the missing files in the
        archive
        '''
        return self._missing_files

    @property
    def missing_bigger_than(self):
        '''A list containing the path and the size of the files missing
        the bigger than parameter in the archive
        '''
        return self._missing_bigger_than

    @property
    def missing_smaller_than(self):
        '''A list containing the path and the size of the files
        missing the smaller than parameter in the archive
        '''
        return self._missing_smaller_than

    @property
    def unexpected_files(self):
        ''' A list containing the unexpected files in the archive'''
        return self._unexpected_files

    @property
    def mismatched_uids(self):
        '''A list containing a {path,uid,expecteduid} of the files in the archive with
        an unexpected uid
        '''
        return self._mismatched_uids

    @property
    def mismatched_gids(self):
        '''A list containing a {path,gid,expectedgid} of the files in the archive with
        an unexpected gid
        '''
        return self._mismatched_gids

    @property
    def mismatched_modes(self):
        '''A list containing {path,mode,expectedmode} of the files in the archive with
        an unexpected mode
        '''
        return self._mismatched_modes

    @property
    def mismatched_types(self):
        '''A list containing {path,type,expectedtype} of the files in the archive with
        an unexpected type
        '''
        return self._mismatched_types

    @property
    def mismatched_hashes(self):
        '''A list containing {path,hash,expectedhash} of the files in the archive with
        an unexpected hash
        '''
        return self._mismatched_hashes

    @property
    def mismatched_targets(self):
        '''A list containing {target,expectedtarget} of the targets of the links in the 
        archive with an unexpected target
        '''
        return self._mismatched_targets
