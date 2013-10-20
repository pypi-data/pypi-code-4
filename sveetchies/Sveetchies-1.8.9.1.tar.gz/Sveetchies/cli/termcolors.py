# -*- coding: utf-8 -*-
"""
Gestion des styles de mise en forme de texte de sortie de terminal

Ce système ne doit pas fonctionner sous windows étant donné qu'il n'utilise pas le même 
principe de caractères d'échappements pour marquer la mise en forme.

Stealed from: django.utils.termcolors
See: http://code.djangoproject.com/browser/django/trunk/django/utils/termcolors.py
"""
color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
foreground = dict([(color_names[x], '3%s' % x) for x in range(8)])
background = dict([(color_names[x], '4%s' % x) for x in range(8)])
del color_names

RESET = '0'
# Availables formating option labels
# Careful, not all of them are really available on all systems
opt_dict = {'bold': '1', 'italic': '3', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

def colorize(text, opts=(), **kwargs):
    """
    Returns your text, enclosed in ANSI graphics codes.

    Depends on the keyword arguments 'fg' and 'bg', and the contents of
    the opts tuple/list.

    Returns the RESET code if no parameters are given.

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

    Valid options:
        'bold'
        'underscore'
        'blink'
        'reverse'
        'conceal'
        'noreset' - string will not be auto-terminated with the RESET code

    Examples:
        colorize('hello', fg='red', bg='blue', opts=('blink',))
        colorize()
        colorize('goodbye', opts=('underscore',))
        print colorize('first line', fg='red', opts=('noreset',))
        print 'this should be red too'
        print colorize('and so should this')
        print 'this should not be red'
    
    :type text: string
    :param text: (optional) Text to enclose. Empty string by default (make it so 
                 useless).
    
    :type opts: tuple
    :param opts: (optional) Formating options (like bold, italic, underscore, etc..).
    
    :rtype: string
    :return: The text string with enclosures for colors and formating
    """
    if not isinstance(text, basestring):
        text = str(text)
    code_list = []
    if text == '' and len(opts) == 1 and opts[0] == 'reset':
        return '\x1b[%sm' % RESET
    for k, v in kwargs.iteritems():
        if k == 'fg':
            code_list.append(foreground[v])
        elif k == 'bg':
            code_list.append(background[v])
    for o in opts:
        if o in opt_dict:
            code_list.append(opt_dict[o])
    if 'noreset' not in opts:
        text = text + '\x1b[%sm' % RESET
    return ('\x1b[%sm' % ';'.join(code_list)) + text

def make_style(opts=(), **kwargs):
    """
    Returns a function with default parameters for colorize()

    Example:
        bold_red = make_style(opts=('bold',), fg='red')
        print bold_red('hello')
        KEYWORD = make_style(fg='yellow')
        COMMENT = make_style(fg='blue', opts=('bold',))
    
    :type opts: tuple
    :param opts: (optional) Formating options (like bold, italic, underscore, etc..).
    
    :rtype: lambda
    :return: Gives a lambda function ready to use with a set of options predefined.
    """
    return lambda text: colorize(text, opts, **kwargs)
