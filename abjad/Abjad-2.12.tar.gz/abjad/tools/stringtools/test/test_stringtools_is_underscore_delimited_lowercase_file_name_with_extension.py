from abjad import *


def test_stringtools_is_underscore_delimited_lowercase_file_name_with_extension_01():

    assert stringtools.is_underscore_delimited_lowercase_file_name_with_extension('foo_bar.blah')
    assert stringtools.is_underscore_delimited_lowercase_file_name_with_extension('foo.blah')


def test_stringtools_is_underscore_delimited_lowercase_file_name_with_extension_02():

    assert stringtools.is_underscore_delimited_lowercase_file_name_with_extension('')


def test_stringtools_is_underscore_delimited_lowercase_file_name_with_extension_03():

    assert not stringtools.is_underscore_delimited_lowercase_file_name_with_extension('foo_bar')
    assert not stringtools.is_underscore_delimited_lowercase_file_name_with_extension('foo_bar.')
    assert not stringtools.is_underscore_delimited_lowercase_file_name_with_extension('Foo_bar.blah')
    assert not stringtools.is_underscore_delimited_lowercase_file_name_with_extension('foo_bar.Blah')
