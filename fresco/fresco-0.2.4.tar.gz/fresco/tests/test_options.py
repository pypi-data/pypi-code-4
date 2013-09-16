from tempfile import NamedTemporaryFile
from fresco.options import Options


class TestOptions(object):

    def test_options_dictionary_access(self):
        options = Options()
        options['x'] = 1
        assert options['x'] == 1

    def test_options_attribute_access(self):
        options = Options()
        options.x = 1
        assert options.x == 1

    def test_options_update_from_object(self):

        class Foo:
            a = 1
            b = 2

        options = Options()
        options.update_from_object(Foo())
        assert options['a'] == 1
        assert options['b'] == 2

    def test_options_update_from_file(self):

        with NamedTemporaryFile() as tmpfile:
            tmpfile.write("a = 1\nb = 2\n")
            tmpfile.flush()

            options = Options()
            options.update_from_file(tmpfile.name)
            assert options['a'] == 1
            assert options['b'] == 2
