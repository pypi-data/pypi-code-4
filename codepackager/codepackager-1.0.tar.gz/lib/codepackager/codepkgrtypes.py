
# -*- coding: utf-8 -*-

""" 定義型別物件 """

import os
import sys
import yaml

from codepackager import codepkgr_common


DEFAULT_BINPATH_TAR = "tar"	#: 預設的 tar 指令路徑 (執行時期使用 PATH 搜尋)
DEFAULT_BINPATH_HG = "hg"	#: 預設的 hg 指令路徑 (執行時期使用 PATH 搜尋)
DEFAULT_BINPATH_GIT = "git"	#: 預設的 git 指令路徑 (執行時期使用 PATH 搜尋)

CFG_WITH_VCS_MERCURIAL = 'hg'
CFG_WITH_VCS_GIT = 'git'

DEFAULT_VCS_BINPATH_MAP = {CFG_WITH_VCS_MERCURIAL: DEFAULT_BINPATH_HG, CFG_WITH_VCS_GIT: DEFAULT_BINPATH_GIT, }



class CodePackageConfig(object):
	""" 描述設定檔內容的物件 """

	def __init__(self, codepkg_name, device_folder=None, archive_folder=None, with_vcs=None, vcs_binpath=None, tar_binpath=None, tmp_folder="/tmp"):
		self.codepkg_name = codepkg_name
		self.device_folder = device_folder
		self.archive_folder = archive_folder
		self.with_vcs = with_vcs
		self.vcs_binpath = vcs_binpath
		self.tar_binpath = tar_binpath
		self.tmp_folder = tmp_folder
	# ### def __init__

	def get_archive_filename(self, suffix="bin"):
		""" 取得壓縮檔檔案名稱
		Argument:
			suffix="bin" - 檔案附加名稱
		Return:
			檔案路徑
		"""
		return u".".join((self.codepkg_name, suffix,))
	# ### def get_archive_filename

	def get_tmp_filepath(self, suffix="bin"):
		""" 取得暫存檔檔案路徑
		Argument:
			suffix="bin" - 檔案附加名稱
		Return:
			檔案路徑
		"""
		archive_filename = self.get_archive_filename(suffix)
		return os.path.join(self.tmp_folder, archive_filename)
	# ### def get_tmp_filepath

	def get_tmp_folderpath(self):
		""" 取得暫存資料夾路徑
		Return:
			資料夾路徑
		"""
		return os.path.join(self.tmp_folder, self.codepkg_name)
	# ### def get_tmp_folderpath

	def get_ondevice_filepath(self, suffix="bin"):
		""" 取得移動儲存媒體檔案路徑
		Argument:
			suffix="bin" - 檔案附加名稱
		Return:
			檔案路徑
		"""
		archive_filename = self.get_archive_filename(suffix)
		return os.path.join(self.device_folder, archive_filename)
	# ### def get_ondevice_filepath

	def get_archive_filepath(self, suffix="bin"):
		""" 取得保存檔檔案路徑
		Argument:
			suffix="bin" - 檔案附加名稱
		Return:
			檔案路徑，或是 None 當沒有設定保存檔檔案夾路徑
		"""
		if self.archive_folder is None:
			return None
		archive_filename = self.get_archive_filename(suffix)
		return os.path.join(self.archive_folder, archive_filename)
	# ### def get_archive_filepath
# ### class CodePackageConfig



CONFIG_VCS_MAP = {'mercurial': CFG_WITH_VCS_MERCURIAL, 'hg': CFG_WITH_VCS_MERCURIAL, 'git': CFG_WITH_VCS_GIT, }

def load_codepkgr_config(proj_cfg_filepath, user_cfg_filepath=None, sufficient_check=True):
	""" 讀取設定檔
	Argument:
		proj_cfg_filepath - 專案設定擋路徑
		user_cfg_filepath=None - 使用者設定擋路徑
		sufficient_check=True - 檢查是否有一般無參數作業足夠的設定檔
	Return:
		表示設定檔內容的 CodePackageConfig 物件，或是 None 當讀取失敗
	"""

	cmap = {}
	dmap = {}

	try:
		fp = open(proj_cfg_filepath, "rb")
		cmap = yaml.safe_load(fp)
		fp.close()
	except Exception as e:
		sys.stderr.write("ERR: cannot read configuration file for project (%r) - %r\n" % (proj_cfg_filepath, e,))
		if True == sufficient_check:
			return None

	try:
		if user_cfg_filepath is not None:
			fp = open(user_cfg_filepath, "rb")
			dmap = yaml.safe_load(fp)
			fp.close()
	except Exception as e:
		sys.stderr.write("ERR: cannot read configuration file for user (%r) - %r\n" % (user_cfg_filepath, e,))
		dmap = {}

	codepkg_name = codepkgr_common.convert_to_nonempty_text(cmap.get("package-name", cmap.get("pkg-name")))
	device_folder = codepkgr_common.convert_to_nonempty_text(cmap.get("device-folder", cmap.get("package-folder", dmap.get("device-folder"))))
	archive_folder = codepkgr_common.convert_to_nonempty_text(cmap.get("archive-folder", dmap.get("archive-folder")))
	tmp_folder = codepkgr_common.convert_to_nonempty_text(cmap.get("tmp-folder", dmap.get("tmp-folder")), "/tmp")

	cmap_binpath = cmap.get("bin", cmap.get("bin-path"))
	if not isinstance(cmap_binpath, dict):
		cmap_binpath = {}
	dmap_binpath = dmap.get("bin", dmap.get("bin-path"))
	if not isinstance(dmap_binpath, dict):
		dmap_binpath = {}

	with_vcs = codepkgr_common.convert_to_nonempty_text(cmap.get("vcs"))
	vcs_binpath = None
	if with_vcs is not None:
		with_vcs = with_vcs.lower()
		with_vcs = CONFIG_VCS_MAP.get(with_vcs)
	if with_vcs is not None:
		vcs_binpath = codepkgr_common.convert_to_nonempty_text(cmap_binpath.get(with_vcs, dmap_binpath.get(with_vcs)))
		if vcs_binpath is None:
			# set default VCS binary path
			vcs_binpath = DEFAULT_VCS_BINPATH_MAP.get(with_vcs)

	tar_binpath = codepkgr_common.convert_to_nonempty_text(cmap_binpath.get("tar", dmap_binpath.get("tar")), DEFAULT_BINPATH_TAR)

	if (True == sufficient_check) and ((codepkg_name is None) or (device_folder is None)):
		return None

	return CodePackageConfig(codepkg_name, device_folder, archive_folder, with_vcs, vcs_binpath, tar_binpath, tmp_folder)
### def load_codepkgr_config



# vim: ts=4 sw=4 foldmethod=marker ai nowrap
