import datetime

from django.db import models


class OnCall (models.Model):
    slug = models.SlugField(
        verbose_name='on-call slot',
        help_text='Identify this among other possible on-call positions')
    rule = models.TextField(
        verbose_name='on-call rule',
        help_text=(
            'Python statement for determining the on-call admin.  '
            "Store the selected admin as 'on_call'."))

    def get_on_call(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        exec(self.rule)
        if 'on_call' in locals():
            return on_call
