def test_compile():
    try:
        import tiddlywebplugins.mapuser

        assert True
    except ImportError, exc:
        assert False, exc
