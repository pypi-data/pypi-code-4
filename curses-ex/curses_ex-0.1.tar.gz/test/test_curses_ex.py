import curses, curses_ex, pytest

def test_curses_ex():
    with pytest.raises(TypeError):
        curses_ex.define_key('\x1b11', 600)

    with pytest.raises(curses.error):
        # curses is not initialized here.
        curses_ex.define_key(b'\x1b11', 600)

