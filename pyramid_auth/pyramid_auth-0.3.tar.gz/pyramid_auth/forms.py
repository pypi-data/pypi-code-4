import tw2.forms as twf
import tw2.core as twc


class UserExists(twc.Validator):
    """Validate the user exists in the DB. It's used when we want to
    authentificate it.
    """
    __unpackargs__ = ('login', 'password', 'validate_func', 'request')
    msgs = {
        'mismatch': ('Login failed. Please check your '
                     'credentials and try again.'),
    }

    def _validate_python(self, value, state):
        super(UserExists, self)._validate_python(value, state)
        login = value[self.login]
        password = value[self.password]
        for v in [login, password]:
            try:
                if issubclass(v, twc.validation.Invalid):
                    # No need to validate the password of the user, the login
                    # or password are invalid
                    return
            except TypeError:
                pass

        if not self.validate_func(self.request, login, password):
            raise twc.ValidationError('mismatch', self)


def create_login_form(request, validate_func):
    class LoginForm(twf.TableForm):
        login = twf.TextField(validator=twc.Validator(required=True))
        password = twf.PasswordField(validator=twc.Validator(required=True))
        submit = twf.SubmitButton(id='submit', value='Login')

        validator = UserExists(
            login='login',
            password='password',
            validate_func=validate_func,
            request=request,
        )
    return LoginForm
