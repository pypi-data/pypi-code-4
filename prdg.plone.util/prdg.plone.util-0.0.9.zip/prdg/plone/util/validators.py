#coding=utf8
"""Provide some useful validators."""
from os.path import splitext
from Products.validation.validators.RegexValidator import RegexValidator
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

DINHEIRO_REGEX = \
    r'^(\d{1,3}\.?(\d{3}\.?)*\d{3}(,\d{0,2})?|\d{1,3}(,\d{0,2})?|,\d{1,2}?)$'

DINHEIRO_VALIDATOR = RegexValidator(
    'dinheiro', 
    DINHEIRO_REGEX,
    errmsg=u'Entre com uma quantidade válida em reais. '
        'Exemplos: "100,23", "1.000,05"',
)

class FileExtensionValidator(object):    
    implements(IValidator)
    
    name = 'file_extension'
    title = 'File extension'
    description = 'Constraint the file extensions accepted by the field.'        
    
    extensions = set()
    error_msg = 'File extension should be one of: '
    
    def __init__(self, extensions, error_msg=None):
        """
        Arguments:
        extensions -- a set of file extensions. Those must be in lower case
            and contain the leading dot. Eg.: set(['.txt', '.doc']).
        error_msg -- Custom error message. If not given a default is used.
        """
        self.extensions = extensions
        if error_msg:
            self.error_msg = error_msg
        
    def __call__(self, value, *args, **kwargs):
        """Implement: IValidator"""                
        extension = splitext(value.filename)[1].lower()        
        return (extension in self.extensions) or self._get_error_msg()
    
    def _get_error_msg(self):
        extensions_str = ', '.join(self.extensions)
        return self.error_msg + extensions_str   
    