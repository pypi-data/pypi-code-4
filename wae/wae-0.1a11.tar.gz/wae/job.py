#coding: utf-8
import types
from wae.context import Context

class Job(object):
    "批处理作业"
    NAME = ""
    DESCR = ""

    def __init__(self, ctx):
        assert isinstance(ctx, Context)
        self.ctx = ctx
        self.initialize()

    def initialize(self):
        "初始化(执行前)"
        pass

    def finalize(self):
        "结束(执行后)"
        pass

    def run(self, **kwargs):
        "执行作业"
        raise NotImplementedError


class JobExecutor(object):
    "任务执行器"

    def load_job(self, ctx, name):
        "加载任务"
        try:
            mod = "jobs.%s" % name
            m = __import__(mod, fromlist=[mod])
            jclass = getattr(m, "%sJob" % name, None)
            if type(jclass)==types.TypeType:
                if issubclass(jclass, Job):
                    return jclass(ctx)
        except:
            pass

        logging.info("cannot load job '%s'" % name)
        return None

    def execute(self, ctx, name, **kwargs):
        "执行指定任务"
        j = self.load_job(ctx, name)
        if j!=None:
            logging.info("execute job '%s'" % name)
            j.run(**kwargs)
            j.finalize()

