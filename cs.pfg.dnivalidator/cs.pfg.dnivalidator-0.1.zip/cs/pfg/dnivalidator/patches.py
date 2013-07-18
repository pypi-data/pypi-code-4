from logging import getLogger
log = getLogger('cs.pfg.dnivalidator')


def ourStringValidatorsDL(self):
    """ return a display list of string validators
    """
    
    if not getattr(self, 'stringValidators', False):
        # on-demand migration from PFG < 1.2
        self._initStringValidators()
        
    # self._initStringValidators()
    self.stringValidators['dni'] = {'title': 'Is a valid DNI',
                                    'i18nid': 'Is a valid DNI',
                                    'errmsg': 'Not a valid DNI',
                                    'errid': 'Not a valid DNI',
                                    'id': 'dni',
                                    }
    self.stringValidatorsDL.add('dni', u'Is a valid DNI', 'Is a valid DNI')
    return self.stringValidatorsDL
    

try:
    from Products.PloneFormGen.tools import formGenTool
    formGenTool.FormGenTool._oldStringValidatorsDL = formGenTool.FormGenTool.getStringValidatorsDL
    formGenTool.FormGenTool.getStringValidatorsDL = ourStringValidatorsDL

except ImportError:
    log.info('Import error: Products.PloneFormGen is not installed, nothing to patch')

