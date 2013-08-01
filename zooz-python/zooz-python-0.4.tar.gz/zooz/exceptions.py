# coding=utf-8


class ZoozException(Exception):
    """
        Extends Exception class adding:

            message: error message returned by ZooZ
            status_code: response status returned by ZooZ
    """
    def __init__(self, message, status_code):
        Exception.__init__(self, message)
        self.status_code = status_code
