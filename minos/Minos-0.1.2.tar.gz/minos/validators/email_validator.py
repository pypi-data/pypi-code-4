from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator

from turbomail.email_validator import EmailValidator as _BaseEmailValidator

_email_validator = _BaseEmailValidator()


# From http://data.iana.org/TLD/tlds-alpha-by-domain.txt, with Unicode domains 'XN--_______' removed
TLD_LIST = [
    'AC', 'AD', 'AE', 'AERO', 'AF', 'AG', 'AI', 'AL', 'AM', 'AN', 'AO', 'AQ',
    'AR', 'ARPA', 'AS', 'ASIA', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD',
    'BE', 'BF', 'BG', 'BH', 'BI', 'BIZ', 'BJ', 'BM', 'BN', 'BO', 'BR', 'BS',
    'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CAT', 'CC', 'CD', 'CF', 'CG', 'CH',
    'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'COM', 'COOP', 'CR', 'CU', 'CV', 'CW',
    'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EDU', 'EE',
    'EG', 'ER', 'ES', 'ET', 'EU', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA',
    'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GOV', 'GP',
    'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 'HN', 'HR', 'HT',
    'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'INFO', 'INT', 'IO', 'IQ', 'IR', 'IS',
    'IT', 'JE', 'JM', 'JO', 'JOBS', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN',
    'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS',
    'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MG', 'MH', 'MIL', 'MK',
    'ML', 'MM', 'MN', 'MO', 'MOBI', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MUSEUM',
    'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NAME', 'NC', 'NE', 'NET', 'NF', 'NG',
    'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'ORG', 'PA', 'PE', 'PF',
    'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'POST', 'PR', 'PRO', 'PS', 'PT', 'PW',
    'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SE', 'SG',
    'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'ST', 'SU', 'SV', 'SX',
    'SY', 'SZ', 'TC', 'TD', 'TEL', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN',
    'TO', 'TP', 'TR', 'TRAVEL', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UK', 'US',
    'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'XXX', 'YE',
    'YT', 'ZA', 'ZM', 'ZW'
]


class EmailValidator(Validator):
    """
    Validates whether a field appears to be an email address.

    For a total list of supported TLD's, please refer to http://data.iana.org/TLD/tlds-alpha-by-domain.txt.
    All listed domains except Unicode domains (i.e. those beginning with "XN") are supported.
    """

    def _validate(self, instance, field, **kwargs):
        """Validate email address.

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validate.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* is not an email address.
        """
        value = getattr(instance, field)
        self.__validate(field, value, **kwargs)

    def __validate(self, key, value, **kwargs):

        if not value:
            return

        if not self.is_email(value):
            msg = 'email_address_invalid'
            raise ValidationError(key, value, msg)

    def is_email(self, email):
        # """Return False if email does not look like a valid email."""

        if not hasattr(email, "split"):  # Duck typing
            return False

        # Check the tld (no more .con)

        # TODO: we should not do that. Confirming an email is the only way is
        # validate it is not mistyped. The list above is not comprehensive, and it
        # will be expensive to maintain it.
        if not email.split('.')[-1].upper() in TLD_LIST:
            return False

        email, err = _email_validator.validate(email)

        # err == '' when no error
        if err:
            return False
        else:
            return True
