import base64
import pickle
try:
    import mailer.models
except:
    pass
else:

    def _get_email(self):
        if self.message_data == "":
            return None
        else:
            return pickle.loads(base64.b64decode(self.message_data))
    mailer.models.Message._get_email = _get_email

    def _set_email(self, val):
        self.message_data = base64.b64encode(pickle.dumps(val))
    mailer.models.Message._set_email = _set_email
    mailer.models.Message.email = property(_get_email, _set_email, doc=
                         """EmailMessage object. If this is mutated, you will need to set the attribute again to cause the underlying serialised data to be updated.""")
