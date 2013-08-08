"""\
FoURLth Exception classes.
"""

class FourlthRootFactory(object):

    def __init__(self, request):
        self._req = request

    def __call__(self, *args, **kwargs):
        return FourlthInterpreter()
    


class FourlthSyntaxError(Exception):
    def __init__(self, *args, **kwargs):
        super(FourlthSyntaxError, self).__init__(*args, **kwargs)

class FourlthRuntimeError(Exception):
    def __init__(self, *args, **kwargs):
        super(FourlthRuntimeError, self).__init__(*args, **kwargs)

class FourlthBreak(Exception):
    def __init__(self, *args, **kwargs):
        super(FourlthBreak, self).__init__(*args, **kwargs)

class FourlthAbort(Exception):
    def __init__(self, *args, **kwargs):
        super(FourlthAbort, self).__init__(*args, **kwargs)


def stackTrace(frame):
    while frame is not None:
        print '\t\t -> line {0.tb_lineno} in {0.tb_frame.f_code.co_filename}'.format(frame)
        frame = frame.tb_next

