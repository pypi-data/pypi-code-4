from system_cmd.utils import result_format

__all__ = ['CmdResult', 'CmdException']

class CmdResult(object):
    def __init__(self, cwd, cmd, ret, stdout, stderr):
        self.cwd = cwd
        self.cmd = cmd
        self.ret = ret
        self.stdout = stdout
        self.stderr = stderr
        
    def format(self):
        return result_format(self.cwd, self.cmd, self.ret, self.stdout, self.stderr)
    
    
class CmdException(Exception):
    def __init__(self, cmd_result):
        Exception.__init__(self, cmd_result.format())
        self.res = cmd_result