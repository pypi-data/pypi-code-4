from .structures import CmdException, CmdResult
from .utils import cmd2args, indent
import subprocess
import sys


__all__ = ['system_cmd_result']
        
def system_cmd_result(
    cwd, cmd,
    display_stdout=False,
    display_stderr=False,
    raise_on_error=False,
    display_prefix=None,
    capture_keyboard_interrupt=False):  
    ''' 
        Returns the structure CmdResult; raises CmdException.
        Also OSError are captured.
        KeyboardInterrupt is passed through unless specified
        
        :param write_stdin: A string to write to the process.
    '''
    if display_prefix is None:
        display_prefix = '%s %s' % (cwd, cmd)
    
    try:
            
        p = subprocess.Popen(
                cmd2args(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd)
        
        if 1:  # XXX?
            stdout, stderr = p.communicate()
            
            stdout = stdout.strip()
            stderr = stderr.strip()
            
            prefix = display_prefix + 'err> '
            if display_stderr and stderr:
                print(indent(stderr, prefix))
                
            prefix = display_prefix + 'out> '
            if display_stdout and stdout:
                print(indent(stdout, prefix))
    
        else:
            stdout, stderr = alternative_nonworking(p, display_stderr, display_stdout, display_prefix)
            
        p.wait()
        
    except KeyboardInterrupt:
        if not capture_keyboard_interrupt:
            raise
        else:
            if raise_on_error:
                raise CmdException('Interrupted')
            else:
                res = CmdResult(cwd, cmd, ret=None, 'Interrupted', 'Interrupted')  
                return res

    ret = p.returncode 
    
    res = CmdResult(cwd, cmd, ret, stdout, stderr)
    
    if raise_on_error:
        if res.ret != 0:
            raise CmdException(res)
    
    return res
        
        
def alternative_nonworking(p, display_stderr, display_stdout, display_prefix):
    """ Returns stdout, stderr """
    
    # p.stdin.close()
    stderr = ''
    stdout = ''
    stderr_lines = []
    stdout_lines = []
    stderr_to_read = True
    stdout_to_read = True
    
    def read_stream(stream, lines):
        if stream:
            nexti = stream.readline()
            if not nexti:
                stream.close()
                return False
            lines.append(nexti)
            return True
        else:
            stream.close()
            return False
            
    # XXX: read all the lines
    while stderr_to_read or stdout_to_read:
        
        if stderr_to_read:
            stderr_to_read = read_stream(p.stderr, stderr_lines)
#             stdout_to_read = False
    
        if stdout_to_read:
            stdout_to_read = read_stream(p.stdout, stdout_lines)
        
        while stderr_lines:
            l = stderr_lines.pop(0)
            stderr += l
            if display_stderr:
                sys.stderr.write('%s ! %s' % (display_prefix, l))
                
        while stdout_lines:
            l = stdout_lines.pop(0)
            stdout += l
            if display_stdout:
                sys.stderr.write('%s   %s' % (display_prefix, l))
            
    stdout = p.stdout.read()
    return stdout, stderr
