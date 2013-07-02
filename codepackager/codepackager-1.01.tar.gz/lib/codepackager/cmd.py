
# -*- coding: utf-8 -*-

""" 實作命令介面 """

import os
import sys
import subprocess
import shutil

from codepackager import codepkgrtypes



_DEFAULT_CONFIG_FILENAME = u".codepackager.yaml"	#: 預設的設定檔檔名
_ARCHIVE_FILE_SUFFIX = "tar.bz2"	#: 實作所使用的壓縮檔案型式之延伸檔名


def _make_tmp_archive_file(wd, tmp_filepath, tar_binpath):
	""" 建立傳輸用的壓縮檔
	Argument:
		wd - 程式碼目錄
		tmp_filepath - 壓縮檔案暫存檔名
		tar_binpath - Tar 工具程式路徑
	Return:
		True 當成功時，或是 False
	"""

	# {{{ remove old archive
	if os.path.exists(tmp_filepath):
		try:
			os.unlink(tmp_filepath)
		except Exception as e:
			sys.stderr.write("ERR: cannot remove tmp file (%r): %r\n" % (tmp_filepath, e,))
			return False
	# }}} remove old archive

	wspace_wd, folder_wd, = os.path.split(wd)
	if (wspace_wd is None) or (folder_wd is None):
		raise ValueError("have error in folder components (wspace_wd=%r, folder_wd=%r)" % (wspace_wd, folder_wd,))

	os.chdir(wspace_wd)
	retcode = subprocess.call([tar_binpath, "-jcf", tmp_filepath, folder_wd, ])
	if 0 != retcode:
		sys.stderr.write("WARN: have non-zero return code (%r) from archive utility.\n" % (retcode,))

	return os.path.isfile(tmp_filepath)
# ### def _make_tmp_archive_file



def _unpack_ondevice_archive_file(ondevice_filepath, tmp_folderpath, tar_binpath):
	""" 將移動儲存媒體上的檔案解包到暫存資料夾
	Argument:
		ondevice_filepath - 裝置上的檔案路徑
		tmp_folderpath - 暫存資料夾路徑
		tar_binpath - Tar 程式路徑
	Return:
		解包後的資料夾路徑，或是 None 當解包失敗
	"""

	# {{{ remove old unpack
	if os.path.exists(tmp_folderpath):
		try:
			if os.path.isfile(tmp_folderpath) or os.path.islink(tmp_folderpath):
				os.unlink(tmp_folderpath)
			else:
				shutil.rmtree(tmp_folderpath)
		except Exception as e:
			sys.stderr.write("ERR: cannot remove old unpack (%r): %r\n" % (tmp_folderpath, e,))
			return None
	# }}} remove old unpack

	os.mkdir(tmp_folderpath)
	os.chdir(tmp_folderpath)
	retcode = subprocess.call([tar_binpath, "-jxf", ondevice_filepath, ])
	if 0 != retcode:
		sys.stderr.write("WARN: have non-zero return code (%r) from archive utility.\n" % (retcode,))

	l = os.listdir(tmp_folderpath)
	for d in l:
		cfgindpath = os.path.join(tmp_folderpath, d, _DEFAULT_CONFIG_FILENAME)
		if os.path.isfile(cfgindpath):
			return os.path.join(tmp_folderpath, d)
	return None
# ### def _unpack_ondevice_archive_file



def _perform_mercurial_update(wd, unpackcode_folderpath, vcs_binpath):
	""" (註冊到 _VCS_PERFORM_UPDATE 表的函式) 執行 Mercurial 的 hg pull 作業
	Argument:
		wd - 工作路徑
		unpackcode_folderpath - 解包後的程式碼路徑
		vcs_binpath - VCS 程式路徑
	Return:
		成功時傳回 True 否則傳回 False
	"""

	os.chdir(wd)
	retcode = subprocess.call([vcs_binpath, "pull", unpackcode_folderpath, ], stdout=sys.stdout, stderr=sys.stderr)
	if 0 != retcode:
		sys.stderr.write("WARN: have non-zero return code (%r) from mercurial.\n" % (retcode,))
		return False
	return True
# ### def _perform_mercurial_update

def _perform_git_update(wd, unpackcode_folderpath, vcs_binpath):
	""" (註冊到 _VCS_PERFORM_UPDATE 表的函式) 執行 Git 的 git fetch 作業
	Argument:
		wd - 工作路徑
		unpackcode_folderpath - 解包後的程式碼路徑
		vcs_binpath - VCS 程式路徑
	Return:
		成功時傳回 True 否則傳回 False
	"""

	os.chdir(wd)
	retcode = subprocess.call([vcs_binpath, "fetch", unpackcode_folderpath, ], stdout=sys.stdout, stderr=sys.stderr)
	if 0 != retcode:
		sys.stderr.write("WARN: have non-zero return code (%r) from Git.\n" % (retcode,))
		return False
	return True
# ### def _perform_git_update


_VCS_PERFORM_UPDATE = {codepkgrtypes.CFG_WITH_VCS_MERCURIAL: _perform_mercurial_update, codepkgrtypes.CFG_WITH_VCS_GIT: _perform_git_update, }

def _perform_vcs_update(cfg, wd, unpacked_codefolder, enable_vcs_guess=False):
	""" 執行版本控制更新到工作目錄作業
	Argument:
		cfg
		wd
		unpacked_codefolder - 解包後的外來程式碼資料夾路徑
	Return:
		傳回 True 當成功，或是 False 當失敗
	"""

	selected_vcs = cfg.with_vcs
	vcs_binpath = cfg.vcs_binpath
	# {{{ guess VCS if enabled
	if (selected_vcs is None) and (True == enable_vcs_guess):
		if os.path.isdir(os.path.join(unpacked_codefolder, ".hg")):
			selected_vcs = codepkgrtypes.CFG_WITH_VCS_MERCURIAL
			sys.stderr.write("INFO: found .hg/ folder, assume Mercurial.\n")
		elif os.path.isdir(os.path.join(unpacked_codefolder, ".git")):
			selected_vcs = codepkgrtypes.CFG_WITH_VCS_GIT
			sys.stderr.write("INFO: found .git/ folder, assume Git.\n")

		if vcs_binpath is None:
			# get default VCS binary path
			vcs_binpath = codepkgrtypes.DEFAULT_VCS_BINPATH_MAP.get(selected_vcs)
	# }}} guess VCS if enabled

	if selected_vcs is None:
		sys.stderr.write("WARN: no VCS information configurate-ed.\n")
		return False

	vcs_upd_func = _VCS_PERFORM_UPDATE.get(selected_vcs)
	sys.stderr.write("INFO: run VCS pull: %r (with %r)\n" % (selected_vcs, vcs_binpath,))
	if vcs_upd_func is not None:
		vcs_upd_func(wd, unpacked_codefolder, vcs_binpath)
	else:
		sys.stderr.write("ERR: not found VCS perform function\n")

	return True
# ### def _perform_vcs_update



def _get_configuration(sufficient_check=True):
	""" 取得組態資訊
	Argument:
		sufficient_check=True - 檢查是否有一般無參數作業足夠的設定檔
	Return:
		型式為 (程式碼目錄, 設定黨物件,) 的 tuple
	"""

	cpwd = os.getcwdu()
	proj_cfg_filepath = os.path.join(cpwd, u".codepackager.yaml")
	user_cfg_filepath = os.path.expanduser(os.path.join(u"~", u".codepackager.yaml"))
	if not os.path.isfile(user_cfg_filepath):
		user_cfg_filepath = None

	cfg = codepkgrtypes.load_codepkgr_config(proj_cfg_filepath, user_cfg_filepath, sufficient_check)

	if cfg is None:
		raise ValueError("insufficient configuration")

	assert(isinstance(cfg, codepkgrtypes.CodePackageConfig))

	return (cpwd, cfg,)
# ### def _get_configuration



def prep():
	""" 執行準備程式碼壓縮檔放置到移動儲存設備作業
	Return:
		True 當成功時，或 False 當失敗時
	"""

	wd, cfg, = _get_configuration()

	if not os.path.isdir(cfg.device_folder):
		sys.stderr.write("ERR: device folder not found.\n")
		return False

	tmp_filepath = cfg.get_tmp_filepath(suffix=_ARCHIVE_FILE_SUFFIX)

	if not _make_tmp_archive_file(wd, tmp_filepath, cfg.tar_binpath):
		sys.stderr.write("ERR: cannot create archive file.\n")
		return False

	archive_filepath = cfg.get_archive_filepath(suffix=_ARCHIVE_FILE_SUFFIX)
	if archive_filepath is not None:
		shutil.copy(tmp_filepath, archive_filepath)
		sys.stderr.write("INFO: copy %r to %r (for archive).\n" % (tmp_filepath, archive_filepath,))

	ondevice_filepath = cfg.get_ondevice_filepath(suffix=_ARCHIVE_FILE_SUFFIX)
	shutil.move(tmp_filepath, ondevice_filepath)
	sys.stderr.write("INFO: move %r to %r (for transport).\n" % (tmp_filepath, ondevice_filepath,))

	return True
# ### def prep



def recv(transarchive_filepath=None):
	""" 執行從移動儲存解包程式碼包裝並試圖進行 VCS 更新
	Argument:
		transarchive_filepath=None - 指定程式碼包裝檔案路徑
	Return:
		True 當成功時，或 False 當失敗時
	"""

	# {{{ load configuration
	if transarchive_filepath is None:
		wd, cfg, = _get_configuration()

		if not os.path.isdir(cfg.device_folder):
			sys.stderr.write("ERR: device folder not found.\n")
			return False

		ondevice_filepath = cfg.get_ondevice_filepath(suffix=_ARCHIVE_FILE_SUFFIX)
		tmp_folderpath = cfg.get_tmp_folderpath()

		allow_vcs_guess = False
	else:
		wd, cfg, = _get_configuration(sufficient_check=False)

		ondevice_filepath = transarchive_filepath
		item_name = "".join([c if c.isalnum() else "_" for c in os.path.basename(transarchive_filepath)])
		tmp_folderpath = os.path.join(cfg.tmp_folder, item_name)

		allow_vcs_guess = True
	# }}} load configuration

	if not os.path.isfile(ondevice_filepath):
		sys.stderr.write("ERR: archive not found on device.\n")
		return False

	unpacked_codefolder = _unpack_ondevice_archive_file(ondevice_filepath, tmp_folderpath, cfg.tar_binpath)
	if unpacked_codefolder is None:
		sys.stderr.write("ERR: cannot unpack archive file.\n")
		return False

	sys.stderr.write("INFO: unpacked code: %r\n" % (unpacked_codefolder,))

	if (cfg.with_vcs is not None):
		_perform_vcs_update(cfg, wd, unpacked_codefolder, enable_vcs_guess=False)
	elif allow_vcs_guess:
		vcsret = _perform_vcs_update(cfg, wd, unpacked_codefolder, enable_vcs_guess=True)
		if False == vcsret:
			sys.stderr.write("WARN: cannot perform VCS update, unpacked code located at:\n> %r\n" % (unpacked_codefolder,))

	return True
# ### def recv



# vim: ts=4 sw=4 foldmethod=marker ai nowrap
