class MethodCalledException(Exception):
    pass

class AfterBeginExc(MethodCalledException):
    pass

class BeforeCommitExc(MethodCalledException):
    pass

class AfterCommitExc(MethodCalledException):
    pass

class AfterAttachExc(MethodCalledException):
    pass

class AfterBulkDeleteExc(MethodCalledException):
    pass

class AfterBulkUpdateExc(MethodCalledException):
    pass

class AfterFlushPostExecExc(MethodCalledException):
    pass

class AfterRollbackExc(MethodCalledException):
    pass

class BeforeFlushExc(MethodCalledException):
    pass

class CreateThumbnailExc(MethodCalledException):
    pass

class RenameThumbnailExc(MethodCalledException):
    pass

