from django.core.exceptions import ValidationError

from django_auth_policy import settings as dap_settings


def password_min_length(value):
    if dap_settings.PASSWORD_MIN_LENGTH_TEXT is None:
        return

    if len(value) < dap_settings.PASSWORD_MIN_LENGTH:
        msg = dap_settings.PASSWORD_MIN_LENGTH_TEXT.format(
            length=dap_settings.PASSWORD_MIN_LENGTH)
        raise ValidationError(msg, code='password_min_length')


def password_complexity(value):
    if not dap_settings.PASSWORD_COMPLEXITY:
        return

    pw_set = set(value)
    for rule in dap_settings.PASSWORD_COMPLEXITY:
        if not pw_set.intersection(rule['chars']):
            msg = dap_settings.PASSWORD_COMPLEXITY_TEXT.format(
                rule_text=rule['text'])
            raise ValidationError(msg, 'password_complexity')
