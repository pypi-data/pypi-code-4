__author__ = 'jos'

from pybm.util import enum

Status = enum(OK="ok", WARNING="warning", ERROR="error", UNKNOWN="unknown", BUILDING="building")

class Job():
    def __init__(self, name, status, percentage):
        self.name = name
        self.status = status
        self.percentage = percentage

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status

    def get_percentage(self):
        return self.percentage