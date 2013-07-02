#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest

sys.path.append('lib')

from codepackager import codepkgrtypes


class TestLoadCodepkgrConfig(unittest.TestCase):
	""" 測試載入設定檔函式 """

	def test_load_1_fulldefined(self):
		""" 讀取完整定義的設定檔 """

		cfg = codepkgrtypes.load_codepkgr_config("test/codepackager-test-1.yaml")
		self.assertNotEqual(None, cfg)
		assert(isinstance(cfg, codepkgrtypes.CodePackageConfig))

		archive_filename = cfg.get_archive_filename(suffix="tar.bz2")
		self.assertEqual(archive_filename, "codepackager-test.tar.bz2")

		archive_filepath = cfg.get_archive_filepath(suffix="tar.bz2")
		self.assertEqual(archive_filepath, "/test_X/archive/codepackager-test.tar.bz2")

		ondevice_filepath = cfg.get_ondevice_filepath(suffix="tar.bz2")
		self.assertEqual(ondevice_filepath, "/test_X/media/MOBILEDISK/codepackager-test.tar.bz2")

		tmp_filepath = cfg.get_tmp_filepath(suffix="tar.bz2")
		self.assertEqual(tmp_filepath, "/tmp/wd/codepackager-test.tar.bz2")

		tmp_folderpath = cfg.get_tmp_folderpath()
		self.assertEqual(tmp_folderpath, "/tmp/wd/codepackager-test")
	# ### def test_load_1_fulldefined

	def test_load_2_partiallydefined(self):
		""" 讀取部份定義的設定檔 """

		cfg = codepkgrtypes.load_codepkgr_config("test/codepackager-test-2.yaml")
		self.assertNotEqual(None, cfg)
		assert(isinstance(cfg, codepkgrtypes.CodePackageConfig))

		archive_filename = cfg.get_archive_filename(suffix="tar.bz2")
		self.assertEqual(archive_filename, "codepackager-test.tar.bz2")

		archive_filepath = cfg.get_archive_filepath(suffix="tar.bz2")
		self.assertEqual(archive_filepath, None)

		ondevice_filepath = cfg.get_ondevice_filepath(suffix="tar.bz2")
		self.assertEqual(ondevice_filepath, "/test_X/media/MOBILEDISK/codepackager-test.tar.bz2")

		tmp_filepath = cfg.get_tmp_filepath(suffix="tar.bz2")
		self.assertEqual(tmp_filepath, "/tmp/codepackager-test.tar.bz2")

		tmp_folderpath = cfg.get_tmp_folderpath()
		self.assertEqual(tmp_folderpath, "/tmp/codepackager-test")
	# ### def test_load_2_partiallydefined

	def test_load_3_merge(self):
		""" 從專案與使用者目錄讀取並合併設定檔 """

		cfg = codepkgrtypes.load_codepkgr_config("test/codepackager-test-3_proj.yaml", "test/codepackager-test-3_user.yaml")
		self.assertNotEqual(None, cfg)
		assert(isinstance(cfg, codepkgrtypes.CodePackageConfig))

		archive_filename = cfg.get_archive_filename(suffix="tar.bz2")
		self.assertEqual(archive_filename, "codepackager-test.tar.bz2")

		archive_filepath = cfg.get_archive_filepath(suffix="tar.bz2")
		self.assertEqual(archive_filepath, "/test_X/archive/codepackager-test.tar.bz2")

		ondevice_filepath = cfg.get_ondevice_filepath(suffix="tar.bz2")
		self.assertEqual(ondevice_filepath, "/test_X/media/MOBILEDISK/codepackager-test.tar.bz2")

		tmp_filepath = cfg.get_tmp_filepath(suffix="tar.bz2")
		self.assertEqual(tmp_filepath, "/tmp/wd/codepackager-test.tar.bz2")

		tmp_folderpath = cfg.get_tmp_folderpath()
		self.assertEqual(tmp_folderpath, "/tmp/wd/codepackager-test")

		self.assertEqual(cfg.with_vcs, "hg")
		self.assertEqual(cfg.vcs_binpath, "/usr/local/bin/hg")
		self.assertEqual(cfg.tar_binpath, "/usr/local/bin/tar")
	# ### def test_load_3_merge
# ### class TestLoadCodepkgrConfig



if __name__ == '__main__':
	unittest.main()

# vim: ts=4 sw=4 ai nowrap
