import re

tag_strip_expression = re.compile(r'<[^<]+?>')


def unsafe_strip_tags(text):
    """ Unsafely removes the tags from a given text. Unsafe meaning that it
    can be tricked and should not be used for validating user input.

    It's mostly useful to find out if a text without tags acutally contains
    any content.

    """
    return re.sub(tag_strip_expression, '', text)
