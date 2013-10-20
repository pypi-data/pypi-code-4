# -*- coding: utf-8 -*-
"""
Group of methods easing the creation of command line tools

includes some modules:

ImportDjangoProject.py
    Allows to import a Django project outside its directory. useful mainly
    when Django is used by scripts that do not start Django in its web
    environment

SveePyCLI.py
    Module to be inherited that eases the building of a command line tool.
    The old version is available (although deprecated) as SveePyCLI_Old.py.
    
DjangoCLI.py
    Inherits from SveePyCLI. This class is made to ease the building of a
    online command line tool that will modify a Django project.
    Depends on ImportDjangoProject.

inputs.py
    Set of objects to manage simple command line forms. Based loosely on the forme
    fields in Django.

termcolors.py
    Scripts teched from Django to allow formatting (bold, colors, italic, aso.) of command
    line text without having to install Django.
"""

def ascii_title(title, cols=80, dotted=True, symbol=' ', position='left'):
    """
    Horizontally aligns a non multi-line text.

    If the text is longer than the horizontal space allocated, the text is truncated
    so that the alignment is kept.


    :type title: string
    :param title: Text to be justified
    
    :type cols: int
    :param cols: (optional) Number of characters in the horizontal space on which
                    the justification will be done
    
    :type dotted: bool
    :param dotted: (optional) if set, will add two dots (..) at the end of a truncated
                    text.
    
    :type symbol: string
    :param symbol: (optional) Character to be used for  justification.
    
    :type position: string
    :param position: (optional) Position of the justification : left, center, right.
    
    :rtype: string
    :return: Justified content
    """
    dots = ''
    if dotted:
        dots = '..'
    if len(title) > cols:
        title = '%s%s' % (title[:(cols-len(dots))], dots)
    if position == 'center':
        return title.center( cols, symbol)
    elif position == 'right':
        return title.rjust( cols, symbol)
    else:
        return title.ljust( cols, symbol)

def unquote_string_argument(self, content=None):
    """
    Removes the quotes from a string passed as command argument

    useful for arguments that may contain text that includes spaces.
    optparser accepts quoted arguments but they are not converted into a simple
    character string without quotes.

    If the string is not quoted, no modification is done.

    Quotes can be either ``"`` or ``'``.
    
    TODO: Remove ``self`` attribute, it is not used.

    :type content: string
    :param content: (optional) Text string.
    
    :rtype: string or any
    :return: Un quoted text string. If the content was not a text string 
             (None, bool, int, etc..), returns it as it is.
    """
    if isinstance(content, basestring) and ((content.startswith("'") and content.endswith("'")) or (content.startswith('"') and content.endswith('"'))) and len(content)>2:
        return content[1:-1]
    return content
