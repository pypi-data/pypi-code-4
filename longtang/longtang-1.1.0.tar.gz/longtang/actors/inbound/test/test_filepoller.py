# -*- coding: utf-8 -*-

#http://docs.python.org/2/library/unittest.html#unittest.TestCase.assertEqual

import unittest
import os

from hamcrest import *
from longtang.actors.inbound import filepoller, messages as fp_messages
from longtang.actors import actorstestutils, messages
from longtang.system.properties import VerbosityLevel

class TestFilePollerActor(unittest.TestCase):

    def test_polling(self):

    	data_dir = os.path.join(actorstestutils.current_dirpath(__file__), 'data')

        poller_tester = actorstestutils.TestActorBuilder().with_type(filepoller.FilePoller)\
                                                          .verbosity(VerbosityLevel.DEBUG)\
                                                          .build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        assert_that(poller_tester.inspector().num_instances(), is_(equal_to(5)), 'Total amount of messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.AudioFileFound), is_(equal_to(3)), 'Total amount of AudioFileFound messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), is_(equal_to(1)), 'Total amount of FilePollingDone messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(messages.Terminated), is_(equal_to(1)), 'Total amount of Terminated messages received is wrong')

        assert_that(poller_tester.inspector().first(fp_messages.AudioFileFound).filepath(), is_(not_none()),'Filepath attribute is empty or wrong')

    def test_weird_encoded_source_polling(self):

        data_dir = os.path.join(actorstestutils.current_dirpath(__file__), 'anóther_daña')

        poller_tester = actorstestutils.TestActorBuilder().with_type(filepoller.FilePoller)\
                                                          .verbosity(VerbosityLevel.DEBUG)\
                                                          .build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        assert_that(poller_tester.inspector().num_instances(), is_(equal_to(4)), 'Total amount of messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.AudioFileFound), is_(equal_to(2)), 'Total amount of AudioFileFound messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), is_(equal_to(1)), 'Total amount of FilePollingDone messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(messages.Terminated), is_(equal_to(1)), 'Total amount of Terminated messages received is wrong')

        assert_that(poller_tester.inspector().first(fp_messages.AudioFileFound).filepath(), is_(not_none()),'Filepath attribute is empty or wrong')

    def test_compressed_file_polling(self):

        data_dir = os.path.join(actorstestutils.current_dirpath(__file__), 'compressed_data')

        poller_tester = actorstestutils.TestActorBuilder().with_type(filepoller.FilePoller)\
                                                          .verbosity(VerbosityLevel.DEBUG)\
                                                          .termination_type(fp_messages.FilePollingDone)\
                                                          .build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        assert_that(poller_tester.inspector().num_instances(), is_(equal_to(11)), 'Total amount of messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.CompressedAudioFileFound), is_(equal_to(9)), 'Total amount of CompressedAudioFileFound messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), is_(equal_to(1)), 'Total amount of FilePollingDone messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(messages.Terminated), is_(equal_to(1)), 'Total amount of Terminated messages received is wrong')

        assert_that(poller_tester.inspector().first(fp_messages.CompressedAudioFileFound).filepath(), is_(not_none()), 'File path attribute is empty or wrong')
        assert_that(poller_tester.inspector().first(fp_messages.CompressedAudioFileFound).compressed_parent_filepath(), is_(not_none()), 'Compressed parent filepath attribute is empty or wrong')

    def test_compressed_file_polling_failure(self):

        data_dir = os.path.join(actorstestutils.current_dirpath(__file__), 'compressed_data_failure')

        poller_tester = actorstestutils.TestActorBuilder().with_type(filepoller.FilePoller)\
                                                          .verbosity(VerbosityLevel.DEBUG)\
                                                          .termination_type(fp_messages.FilePollingDone)\
                                                          .build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        assert_that(poller_tester.inspector().num_instances(), is_(equal_to(5)), 'Total amount of messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.CompressedFileCouldNotBeOpened), is_(equal_to(3)), 'Total amount of CompressedFileCouldNotBeOpened messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.FilePollingDone), is_(equal_to(1)), 'Total amount of FilePollingDone messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(messages.Terminated), is_(equal_to(1)), 'Total amount of Terminated messages received is wrong')

        assert_that(poller_tester.inspector().first(fp_messages.CompressedFileCouldNotBeOpened).filepath(), is_(not_none()), 'File path attribute is empty or wrong from message type CompressedFileCouldNotBeOpened ')

    def test_mix_content_polling(self):
        data_dir = os.path.join(actorstestutils.current_dirpath(__file__), 'mixed_data')

        poller_tester = actorstestutils.TestActorBuilder().with_type(filepoller.FilePoller)\
                                                          .verbosity(VerbosityLevel.DEBUG)\
                                                          .termination_type(fp_messages.FilePollingDone)\
                                                          .build()

        poller_tester.tell(fp_messages.StartPolling(data_dir))

        assert_that(poller_tester.inspector().num_instances(), is_(equal_to(8)), 'Total amount of messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.CompressedFileCouldNotBeOpened), is_(equal_to(1)), 'Total amount of CompressedFileCouldNotBeOpened messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.CompressedAudioFileFound), is_(equal_to(3)), 'Total amount of CompressedAudioFileFound messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(fp_messages.AudioFileFound), is_(equal_to(2)), 'Total amount of AudioFileFound messages received is wrong')
        assert_that(poller_tester.inspector().num_instances(messages.Terminated), is_(equal_to(1)), 'Total amount of Terminated messages received is wrong')

if __name__ == '__main__':
    unittest.main()    