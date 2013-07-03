from flask.ext.security.core import UserMixin
from flask.ext.security.registerable import encrypt_password
from flask.ext.security.recoverable import update_password as _update_password
from flask.ext.security.recoverable import generate_reset_password_token \
    as _generate_reset_password_token
from flask.ext.security.recoverable import reset_password_token_status \
    as _reset_password_token_status
from flask.ext.security import utils as security_utils
from flask.ext.security import signals as security_signals

from tahoe import search

from tahoe.models import ModelRegistry
from tahoe.models.mixins.timestampable import TimestampMixin
from tahoe.models.mixins.searchable import SearchableMixin


NOT_ENOUGH_INFO = "Please provide a username, password, and email address"
ALREADY_TAKEN = "An account is already using this username or email address."


@ModelRegistry.register()
def create_account_roles(db, models, app, config, logger, bucket):
    class AccountRole(db.Model, TimestampMixin(db)):
        """
        A mapping of Accounts to Roles. Represents the Roles associated
        with an account.
        """
        __tablename__ = 'account_roles'
        account_id = db.Column(db.Integer, primary_key=True)
        role_id = db.Column(db.Integer, primary_key=True)

        def __repr__(self):
            return "<AccountRole(account_id='{}', role_id='{}')>".format(
                self.account_id,
                self.role_id)

    return AccountRole


@ModelRegistry.register()
def create_accounts(db, models, app, config, logger, bucket):
    searchable_mixin = SearchableMixin(bucket, logger)
    timestamp_mixin = TimestampMixin(db)

    class Account(db.Model, UserMixin, searchable_mixin, timestamp_mixin):
        """
        Represents an Account.
        """
        __tablename__ = 'accounts'
        id = db.Column(db.Integer, primary_key=True)

        username = db.Column(db.String(255))
        email = db.Column(db.String(255))
        password = db.Column(db.String(255))

        active = db.Column(db.Boolean(), default=True)
        last_login_at = db.Column(db.DateTime)
        current_login_at = db.Column(db.DateTime)
        last_login_ip = db.Column(db.String(255))
        current_login_ip = db.Column(db.String(255))
        login_count = db.Column(db.Integer, default=0)

        roles = db.relationship(
            "Role",
            secondary=models.AccountRole.__table__,
            primaryjoin="and_(Account.id==AccountRole.account_id, \
                AccountRole.deleted_at==None)",
            secondaryjoin="and_(Role.id==AccountRole.role_id, \
                Role.deleted_at==None)",
            backref='accounts')

        @classmethod
        def create(cls, **kwargs):
            """
            A wrapper around the Flask-Security's concept for creating
            accounts, does all the jazz of encrypting the password
            and so forth.
            """
            username = kwargs.get('username')
            password = kwargs.get('password')
            email = kwargs.get('email')

            if not (username and password and email):
                raise ValueError(NOT_ENOUGH_INFO)
            if cls.is_valid_username_and_password(username, password):
                if cls.get_from_username_or_email(username=username,
                                                  email=email):
                    raise AccountTaken(ALREADY_TAKEN)
                kwargs['password'] = encrypt_password(kwargs['password'])
                user_datastore = bucket['user_datastore']()
                return user_datastore.create_user(**kwargs)

        @classmethod
        def get_from_username_or_email(cls, username=None, email=None):
            if username:
                account_using_username = cls.get_from_username(username)
                if account_using_username:
                    return account_using_username
            if email:
                account_using_email = cls.get_from_email(email)
                if account_using_email:
                    return account_using_email

        @classmethod
        def get_from_id(cls, id):
            """
            Finds and returns an account associated with an id
            """
            return cls.query_active().filter_by(id=id).first()

        @classmethod
        def get_from_email(cls, email):
            """
            Finds and returns an account associated with a given email address.
            """
            return cls.query_active().filter_by(email=email).first()

        @classmethod
        def get_from_username(cls, username):
            """
            Finds and returns an account associated with a given username.
            """
            return cls.query_active().filter_by(username=username).first()

        @classmethod
        def reset_password_token_status(cls, token):
            """
            Accepts a token generated for resetting a password and
            validates it.

            Returns a tuple of the form:

                (bool:expired, bool:invalid, Account:user)

            - If the token is valid but has expired, `expired` will be True
            - If the token is invalid `invalid` will be True
            - If the token is valid and has not expired, both `expired` and
              `invalid` will be False and the third item of the tuple will be
              the account associated with the token.
            """
            return _reset_password_token_status(token)

        @classmethod
        def _search_index_mapping(cls):
            return dict(properties=dict(
                id=search.EXACT_MATCH_FIELD,
                email=search.CASE_INSENSITIVE_EXACT,
                username=search.CASE_INSENSITIVE_EXACT))

        @classmethod
        def _search_builder_mapping(self):
            return dict(
                id=search.ExactMatch('id'),
                email=search.CaseInsensitiveExact('email'),
                username=search.CaseInsensitivePrefix('username'),
                username_exact=search.CaseInsensitiveExact('username'),
                q=search.StringQuery())

        def __repr__(self):
            fmt = "<Account(id='{}', username='{}', email='{}', deleted='{}')>"
            return fmt.format(
                self.id,
                self.username,
                self.email)

        def generate_reset_password_token(self):
            return _generate_reset_password_token(self)

        def send_reset_password_instructions(self):
            """
            Sends the reset password instructions email for the specified user.

            This is copied out of flask.ext.security.recoverable and modified
            for our own purposes.

            :param user: The user to send the instructions to
            """
            token = self.generate_reset_password_token()
            security_utils.send_mail(
                security_utils.config_value('EMAIL_SUBJECT_PASSWORD_RESET'),
                self.email,
                'reset_instructions',
                user=self,
                reset_token=token)
            security_signals.reset_password_instructions_sent.send(
                dict(user=self, token=token),
                app=app)

        def update_password(self, new_password):
            """
            Hashes the plaintext `new_password` into a format suitable for
            storage in a database.

            See http://pythonhosted.org/Flask-Security/configuration.html for
            configuring how passwords are hashed.
            """
            return _update_password(self, new_password)

        def verify_password(self, password):
            return security_utils.verify_password(password, self.password)

        def add_role(self, role_name):
            """
            Adds a role to this user.
            """
            role = models.Role.query_active().filter_by(name=role_name).first()
            if role:
                return bucket['user_datastore']().add_role_to_user(self, role)
            return False

        def remove_role(self, role_name):
            """
            Removes a role from this user.
            """
            role = models.Role.query_active().filter_by(name=role_name).first()
            if not role:
                return False
            return bucket['user_datastore']().remove_role_from_user(
                self,
                role_name)

        def to_dict(self):
            """
            The representation of this model when jsonified in an API response.
            """
            return dict(
                id=self.id,
                username=self.username,
                email=self.email,
                created_at=self.created_at,
                updated_at=self.updated_at,
                deleted_at=self.deleted_at)

    return Account
