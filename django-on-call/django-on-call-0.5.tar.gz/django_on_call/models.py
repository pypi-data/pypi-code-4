import datetime

from django.db import models


class OnCall (models.Model):
    slug = models.SlugField(
        unique=True,
        verbose_name='on-call slot',
        help_text='Identify this among other possible on-call positions')
    description = models.TextField(
        help_text=(
            'A paragraph describing of this position, to help new users '
            'match their problem to the appropriate on-call position.'))
    rule = models.TextField(
        verbose_name='on-call rule',
        help_text=(
            'Python statement for determining the on-call admin.  '
            "Store the selected admin as 'on_call'."))

    def __str__(self):
        return 'on call {}'.format(self.slug)

    def __repr__(self):
        return '<{}.{} {}>'.format(
            type(self).__module__, type(self).__name__, self.slug)

    def get_on_call(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        exec(self.rule)
        if 'on_call' in locals():
            return on_call
