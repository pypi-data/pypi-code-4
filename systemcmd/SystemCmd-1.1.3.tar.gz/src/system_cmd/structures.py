from .utils import indent

__all__ = ['CmdResult', 'CmdException']

# class CmdResult(object):
#     def __init__(self, cwd, cmd, ret, stdout, stderr):
#         self.cwd = cwd
#         self.cmd = cmd
#         self.ret = ret
#         self.stdout = stdout
#         self.stderr = stderr
#         
#     def format(self):
#         return result_format(self.cwd, self.cmd, self.ret, self.stdout, self.stderr)



class CmdResult(object):
    def __init__(self, cwd, cmd, ret, rets, interrupted, stdout, stderr):
        self.cwd = cwd
        self.cmd = cmd
        self.ret = ret
        self.rets = rets
        self.stdout = stdout
        self.stderr = stderr
        self.interrupted = interrupted

    def __str__(self):
        msg = ('The command: %s\n'
               '     in dir: %s\n' % (self.cmd, self.cwd))

        if self.interrupted:
            msg += 'Was interrupted by the user\n'
        else:
            msg += 'returned: %s' % self.ret
        if self.rets is not None:
            msg += '\n' + indent(self.rets, 'error>')
        if self.stdout:
            msg += '\n' + indent(self.stdout, 'stdout>')
        if self.stderr:
            msg += '\n' + indent(self.stderr, 'stderr>')
        return msg

    
class CmdException(Exception):
    def __init__(self, cmd_result):
        Exception.__init__(self, str(cmd_result))
        self.res = cmd_result

        