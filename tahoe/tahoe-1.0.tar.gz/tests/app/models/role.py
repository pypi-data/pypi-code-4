from tahoe.models import ModelRegistry
from tahoe.models.mixins.timestampable import TimestampMixin
from flask_security.core import RoleMixin


@ModelRegistry.register()
def create_roles(db, models, app, config, logger, bucket):
    timestamp_mixin = TimestampMixin(db)

    class Role(db.Model, RoleMixin, timestamp_mixin):
        """
        Represents a role
        """
        __tablename__ = 'roles'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255), index=True)
        description = db.Column(db.String(255, convert_unicode=True))

        def __repr__(self):
            return "<Role(id='{}', name='{}')>".format(self.id, self.name)

        @classmethod
        def get_from_name(cls, name):
            return cls.query_active().filter_by(name=name).first()

    return Role
