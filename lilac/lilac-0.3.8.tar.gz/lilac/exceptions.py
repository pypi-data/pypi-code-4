# coding=utf8

"""all possible exceptions"""

class LilacException(Exception):
    """There was an ambiguous exception that occurred while
    handling lilac process"""
    pass


class SourceDirectoryNotFound(LilacException):
    """Source directory was not found"""
    pass


class ParseException(LilacException):
    """There was an exception occurred while parsing the source"""
    pass


class RenderException(LilacException):
    """There was an exception occurred while rendering to html"""
    pass


class SeparatorNotFound(ParseException):
    """There was no separator found in post's source"""
    pass


class PostDateTimeNotFound(ParseException):
    """There was no datetime found in post's source"""
    pass


class PostTitleNotFound(ParseException):
    """There was no title found in post's source"""
    pass


class PostDateTimeInvalid(ParseException):
    """Invalid datetime format, should like '2012-04-05 10:10'"""
    pass


class PostTagsTypeInvalid(ParseException):
    """Invalid tags datatype, should be a array"""
    pass


class PostHeaderSyntaxError(ParseException):
    """TomlSyntaxError occurred in post's header"""
    pass


class ConfigSyntaxError(LilacException):
    """TomlSyntaxError occurred in config.toml"""
    pass


class JinjaTemplateNotFound(RenderException):
    """Jinja2 template was not found"""
    pass
