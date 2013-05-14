def test_compile():
	try:
		import tiddlywebplugins.jsondispatcher
		assert True
	except ImportError, exc:
		assert False, exc
