# -*- coding: utf-8 -*-
from breq import Breq


class Reddit(Breq):

    def set_next(self):
        self.payload['after'] = self.response_content['data']['after']

    def is_last(self):
        if not self.response_content['data']['after']:
            return True
        return False