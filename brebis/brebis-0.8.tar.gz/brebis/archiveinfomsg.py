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

# Generate the information message about an archive
'''Generate the information message about an archive'''

import logging

class ArchiveInfoMsg(object):
    '''Generate the information message about an archive'''

    def __init__(self, __bck, __cfgvalues):
        '''The constructor for the ArchiveInfoMsg class.

        __bck -- the retrieved value for the archive
        __cfgvalues -- the expected values for the archive

        '''
        self.__main(__bck, __cfgvalues)

    def __main(self, __bck, __cfgvalues):
        '''The main for the ArchiveInfoMsg class'''
        if __cfgvalues['type'] == 'archive' or __cfgvalues['type'] == 'tree':
            self.__missing_files(__bck.missing_files, __cfgvalues['path'])
            self.__unexpected_files(__bck.unexpected_files, __cfgvalues['path'])
            self.__classify_differences(__bck, __cfgvalues['path'])
            self.__uid_gid_mismatches(__bck, __cfgvalues['path'])
            self.__mode_mismatches(__bck, __cfgvalues['path'])
            self.__type_mismatches(__bck, __cfgvalues['path'])
            self.__hash_mismatches(__bck, __cfgvalues['path'])
            self.__target_mismatches(__bck, __cfgvalues['path'])

    def __missing_files(self, __missing, __archivepath):
        '''Warn about the missing files in an archive'''
        if __missing:
            __msg= 'file'
            if len(__missing) > 1:
                __msg = 'files'
            logging.warning('{} {} missing in {}: '.format(
                len(__missing), __msg, __archivepath))
            for __path in __missing:
                logging.warning('{}'.format(__path))

    def __unexpected_files(self, __unexpected, __archivepath):
        '''Warn about the unexpected files in the archive'''
        if __unexpected:
            __msg= 'file'
            if len(__unexpected) > 1:
                __msg = 'files'
            logging.warning('{} unexpected {} checking {}: '.format(
                len(__unexpected), __msg, __archivepath))
            for __path in __unexpected:
                logging.warning('{}'.format(__path))

    def __classify_differences(self, __bck, __archivepath):
        '''Report differences between expected files and files in the
        archive
        '''
        if __bck.missing_equality:
            __topic = '{} {} with unexpected size while checking {}: '
            self.__log_differences(
                __bck.missing_equality, __archivepath, __topic)
        if __bck.missing_smaller_than:
            __topic = '{} {} bigger than expected while checking {}: '
            self.__log_differences(
                __bck.missing_smaller_than, __archivepath,
                    __topic, 'smaller than')
        if __bck.missing_bigger_than:
            __topic = '{} {} smaller than expected while checking {}: '
            self.__log_differences(
                __bck.missing_bigger_than, __archivepath,
                    __topic, 'bigger than')

    def __log_differences(self, __files, __archivepath, __topic, __qty=''):
        '''Log the differences between the expected files and the files
        in the archive
        '''
        __fileword = 'file'
        if len(__files) > 1:
            __fileword = 'files'
        logging.warning(__topic.format(len(__files), __fileword, __archivepath))
        if __qty:
            for __file in __files:
                logging.warning('{} size is {}. Should have been {} {}.'.format(
                    __file['path'], __file['size'], __qty, __file['expected']))
        else:
            for __file in __files:
                logging.warning('{} size is {}. Should have been {}.'.format(
                    __file['path'], __file['size'], __file['expected']))

    def __uid_gid_mismatches(self, __bck, __archivepath):
        '''Log the uids and gids mismatches'''
        # Uid
        if __bck.mismatched_uids:
            __errnb = len(__bck.mismatched_uids)
            __fileword = 'file'
            __uidword = 'uid'
            if __errnb > 1:
                __fileword = 'files'
                __uidword = 'uids'
            logging.warning('{} {} with unexpected {} while checking {}:'.format(__errnb, __fileword, __uidword, __archivepath))
            for __file in __bck.mismatched_uids:
                logging.warning('{} uid is {!s}. Should have been {!s}.'.format(__file['path'], __file['uid'], __file['expecteduid']))
        # Gid
        if __bck.mismatched_gids:
            __errnb = len(__bck.mismatched_gids)
            __fileword = 'file'
            __gidword = 'gid'
            if __errnb > 1:
                __fileword = 'files'
                __gidword = 'gids'
            logging.warning('{} {} with unexpected {} while checking {}:'.format(__errnb, __fileword, __gidword, __archivepath))
            for __file in __bck.mismatched_gids:
                logging.warning('{} gid is {!s}. Should have been {!s}.'.format(__file['path'], __file['gid'], __file['expectedgid']))

    def __mode_mismatches(self, __bck, __archivepath):
        '''Log the file mode mismatches'''
        if __bck.mismatched_modes:
            __errnb = len(__bck.mismatched_modes)
            __fileword = 'file'
            __modeword = 'mode'
            if __errnb > 1:
                __fileword = 'files'
                __modeword = 'modes'
            logging.warning('{} {} with unexpected {} while checking {}:'.format( __errnb, __fileword, __modeword, __archivepath, ))
            for __file in __bck.mismatched_modes:
                logging.warning('{} mode is {}. Should have been {}.'.format(__file['path'], __file['mode'], __file['expectedmode']))
        
    def __target_mismatches(self, __bck, __archivepath):
        '''Log the targe mismatches'''
        if __bck.mismatched_targets:
            __errnb = len(__bck.mismatched_targets)
            __fileword = 'link'
            __modeword = 'target'
            if __errnb > 1:
                __fileword = 'links'
                __modeword = 'targets'
            logging.warning('{} {} with unexpected {} while checking {}:'.format( __errnb, __fileword, __modeword, __archivepath, ))
            for __file in __bck.mismatched_targets:
                logging.warning('{} target is {}. Should have been {}.'.format(__file['path'], __file['target'], __file['expectedtarget']))
        
    def __type_mismatches(self, __bck, __archivepath):
        '''Log the file type mismatches'''
        __types = {'f': 'regular file',
                    'c': 'character',
                    'd': 'directory',
                    's': 'symbolic link',
                    'l': 'hard link',
                    'b': 'block',
                    'o': 'fifo',
                    'k': 'socket'}
        if __bck.mismatched_types:
            __errnb = len(__bck.mismatched_types)
            __fileword = 'file'
            __typeword = 'type'
            if __errnb > 1:
                __fileword = 'files'
                __typeword = 'types'
            logging.warning('{} contains {} {} with unexpected {}:'.format(__archivepath, __errnb, __fileword, __typeword))
            for __file in __bck.mismatched_types:
                logging.warning('{} is a {}. Should have been a {}.'.format(__file['path'], __types[__file['type']], __types[__file['expectedtype']]))

    def __hash_mismatches(self, __bck, __archivepath):
        '''Log the file hash mismatches'''
        if __bck.mismatched_hashes:
            __errnb = len(__bck.mismatched_hashes)
            __fileword = 'file'
            __hashword = 'hash'
            if __errnb > 1:
                __fileword = 'files'
                __hashword = 'hashes'
            logging.warning('{} {} with unexpected {} while checking {}:'.format(__errnb, __fileword, __hashword, __archivepath))
            for __file in __bck.mismatched_hashes:
                logging.warning('{} hash is {}. Should have been {}.'.format(__file['path'], __file['hash'], __file['expectedhash']))
