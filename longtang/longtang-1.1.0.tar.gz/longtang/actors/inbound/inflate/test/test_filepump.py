# -*- coding: utf-8 -*-

import unittest
import os
from hamcrest import *

from longtang.actors import actorstestutils, messages
from longtang.actors.inbound.inflate import filepump, messages as fp_messages
from longtang.system.properties import VerbosityLevel

class TestFilePump(unittest.TestCase):
	def test_zip_pump(self):

		test_zip_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data.zip')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileDone)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_zip_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflatedFileAvailable), is_(equal_to(3)), 'Total amount of InflatedFileAvailable messages received is wrong')
		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileDone), is_(equal_to(1)), 'Total amount of PumpFileDone messages received is wrong')

		for message in pump_tester.inspector().all(fp_messages.InflatedFileAvailable):
			assert_that(message.filepath(), is_(not_none()), 'Filepath attribute is empty')

			assert_that(message.filepath(), is_(any_of(contains_string('dummy1.mp3'),\
													   contains_string('dummy2.mp3'),\
													   contains_string('dummy3.mp3'))), 'Filepath attribute might be wrong')

			assert_that(message.parent_filepath(), is_(not_none()), 'Parent inflated filepath attribute is empty')
			assert_that(message.parent_filepath(), is_(equal_to(test_zip_file)), 'Parent inflated filepath attribute is wrong')

		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(not_none()), 'InflateFileDone message attribute ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(equal_to(test_zip_file)), 'InflateFileDone message attribute ''filepath'' is wrong')

	def test_zip_pump_failure(self):
		test_zip_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data_failure.zip')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileFailed)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_zip_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileFailed), is_(equal_to(1)), 'Total amount of InflatedFileFailed messages received is wrong')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(not_none()), 'InflatedFileFailed ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(equal_to(test_zip_file)), 'InflatedFileFailed ''filepath'' is wrong')

	def test_rar_pump(self):
		test_rar_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data.rar')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileDone)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_rar_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflatedFileAvailable), is_(equal_to(3)), 'Total amount of InflatedFileAvailable messages received is wrong')
		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileDone), is_(equal_to(1)), 'Total amount of PumpFileDone messages received is wrong')

		for message in pump_tester.inspector().all(fp_messages.InflatedFileAvailable):
			assert_that(message.filepath(), is_(not_none()), 'Filepath attribute is empty')

			assert_that(message.filepath(), is_(any_of(contains_string('dummy1.mp3'),\
													   contains_string('dummy2.mp3'),\
													   contains_string('dummy3.mp3'))), 'Filepath attribute might be wrong')

			assert_that(message.parent_filepath(), is_(not_none()), 'Parent inflated filepath attribute is empty')
			assert_that(message.parent_filepath(), is_(equal_to(test_rar_file)), 'Parent inflated filepath attribute is wrong')

		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(not_none()), 'InflateFileDone message attribute ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(equal_to(test_rar_file)), 'InflateFileDone message attribute ''filepath'' is wrong')

	def test_rar_pump_failure(self):
		test_rar_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data_failure.rar')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileFailed)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_rar_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileFailed), is_(equal_to(1)), 'Total amount of InflatedFileFailed messages received is wrong')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(not_none()), 'InflatedFileFailed ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(equal_to(test_rar_file)), 'InflatedFileFailed ''filepath'' is wrong')

	def test_7z_pump(self):
		test_7zip_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data.7z')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileDone)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_7zip_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflatedFileAvailable), is_(equal_to(3)), 'Total amount of InflatedFileAvailable messages received is wrong')
		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileDone), is_(equal_to(1)), 'Total amount of PumpFileDone messages received is wrong')

		for message in pump_tester.inspector().all(fp_messages.InflatedFileAvailable):
			assert_that(message.filepath(), is_(not_none()), 'Filepath attribute is empty')

			assert_that(message.filepath(), is_(any_of(contains_string('dummy1.mp3'),\
													   contains_string('dummy2.mp3'),\
													   contains_string('dummy3.mp3'))), 'Filepath attribute might be wrong')

			assert_that(message.parent_filepath(), is_(not_none()), 'Parent inflated filepath attribute is empty')
			assert_that(message.parent_filepath(), is_(equal_to(test_7zip_file)), 'Parent inflated filepath attribute is wrong')

		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(not_none()), 'InflateFileDone message attribute ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileDone).filepath(), is_(equal_to(test_7zip_file)), 'InflateFileDone message attribute ''filepath'' is wrong')		

	def test_7z_pump_failure(self):
		test_7z_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'data_failure.7z')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileFailed)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_7z_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileFailed), is_(equal_to(1)), 'Total amount of InflatedFileFailed messages received is wrong')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(not_none()), 'InflatedFileFailed ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(equal_to(test_7z_file)), 'InflatedFileFailed ''filepath'' is wrong')			

	def test_unrecognized_pump_format(self):
		test_zip_file = os.path.join(actorstestutils.current_dirpath(__file__), 'data', 'unrecognized_format.kk')

		pump_tester = actorstestutils.TestActorBuilder().with_type(filepump.FilePumpActor)\
														.termination_type(fp_messages.InflateFileFailed)\
														.verbosity(VerbosityLevel.DEBUG)\
														.termination_moratorium(2)\
														.build()

		pump_tester.tell(fp_messages.InflateFile(test_zip_file))

		assert_that(pump_tester.inspector().num_instances(fp_messages.InflateFileFailed), is_(equal_to(1)), 'Total amount of InflatedFileFailed messages received is wrong')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(not_none()), 'InflatedFileFailed ''filepath'' is empty')
		assert_that(pump_tester.inspector().first(fp_messages.InflateFileFailed).filepath(), is_(equal_to(test_zip_file)), 'InflatedFileFailed ''filepath'' is wrong')

if __name__ == '__main__':
    unittest.main()		