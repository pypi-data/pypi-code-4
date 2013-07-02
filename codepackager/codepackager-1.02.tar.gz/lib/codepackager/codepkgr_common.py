
# -*- coding: utf-8 -*-

""" 共用物件與函式庫 """

import sys



def convert_to_nonempty_text(v, default_value=None):
	""" 將輸入值轉換為字串，當輸入值為 None 或空字串或是無法轉換的物件時傳回 None
	Argument:
		v - 要轉換的或物件
		default_value - 預設值
	Return:
		非空字串，或是 None 當輸入是空字串或是無法轉換的物件
	"""

	if v is None:
		return default_value

	r = None

	if isinstance(v, unicode):
		r = v
	elif isinstance(v, str):
		r = unicode(v, 'utf-8', 'ignore')
	else:
		try:
			r = str(v)
		except:
			sys.stderr.write("WARN: cannot convert input (%r) to string. @[codepkgr_common.convert_to_nonempty_text]\n" % (v,))
			r = None

	if r is not None:
		r = r.strip()
		if len(r) > 0:
			return r
	return default_value
# ### def convert_to_nonempty_text



# vim: ts=4 sw=4 foldmethod=marker ai nowrap
