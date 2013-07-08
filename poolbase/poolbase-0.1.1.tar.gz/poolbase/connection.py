#encoding:utf-8


class Connection(object):
    #pylint: disable=R0921

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def refresh(self):
        raise NotImplementedError()
