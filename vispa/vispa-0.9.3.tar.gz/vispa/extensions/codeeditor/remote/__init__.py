import os,sys

class DummyRpc:
    def dummy(self):
        return ",".join(sys.path)