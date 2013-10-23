from datetime import datetime
from tg.i18n import ugettext as _
from tg.validation import TGValidationError

class DateParameterValidator(object):
    def to_python(self, value, state=None):
        try:
            if not value:
                return datetime.utcnow()
            return datetime.strptime(value, '%Y-%m-%d')
        except:
            raise TGValidationError(_('Expected date in format 2013-01-11'))
