# -*- coding: utf-8 -*-

from django.db import models

from enumerify import fields

from .enums import ExamStatus

class Exam(models.Model):
    ''' A test model in order to test the Enum functionality '''
    status = fields.SelectIntegerField(blueprint=ExamStatus, default=ExamStatus.FAIL)

    def passed(self):
        self.status = ExamStatus.PASS
        self.save()

    def failed(self):
        self.status = ExamStatus.FAIL
        self.save()

    def has_passed(self):
        return self.status == ExamStatus.PASS

    def has_failed(self):
        return self.status == ExamStatus.FAIL