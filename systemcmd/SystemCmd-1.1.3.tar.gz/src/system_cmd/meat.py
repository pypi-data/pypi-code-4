from .structures import CmdException, CmdResult
from .utils import cmd2args, indent
import subprocess
import sys
import tempfile
import os
import warnings


__all__ = ['system_cmd_result']

def system_cmd_result(cwd, cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=False,
                      display_prefix=None,
                      write_stdin='',
                      capture_keyboard_interrupt=False,
                      display_stream=sys.stderr):  # @UnusedVariable
    ''' 
        Returns the structure CmdResult; raises CmdException.
        Also OSError are captured.
        KeyboardInterrupt is passed through unless specified
        
        :param write_stdin: A string to write to the process.
    '''
    # if display_prefix is not None:
        # warnings.warn('call with display_prefix')
        
    tmp_stdout = tempfile.TemporaryFile()
    tmp_stderr = tempfile.TemporaryFile()

    ret = None
    rets = None
    interrupted = False

    try:
        #stdout = None if display_stdout else 
        stdout = tmp_stdout.fileno()
#        stderr = None if display_stderr else 
        stderr = tmp_stderr.fileno()
        p = subprocess.Popen(
                cmd2args(cmd),
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
                bufsize=0,
                cwd=cwd)

        if write_stdin != '':
            p.stdin.write(write_stdin)
            p.stdin.flush()

        p.stdin.close()
        p.wait()
        ret = p.returncode
        rets = None
        interrupted = False

    except KeyboardInterrupt:
        if capture_keyboard_interrupt:
            ret = 100
            interrupted = True
        else:
            raise 
    except OSError as e:
        interrupted = False
        ret = 200
        rets = str(e)

    # remember to go back
    def read_all(f):
        os.lseek(f.fileno(), 0, 0)
        return f.read().strip()

    captured_stdout = read_all(tmp_stdout)
    captured_stderr = read_all(tmp_stderr)

    if display_stdout and captured_stdout:
        display_stream.write(indent(captured_stdout,'stderr>'))

    if display_stderr and captured_stderr:
        display_stream.write(indent(captured_stderr,'stdout>'))


    res = CmdResult(cwd, cmd, ret, rets, interrupted,
                    stdout=captured_stdout,
                    stderr=captured_stderr)

    if raise_on_error:
        if res.ret != 0:
            raise CmdException(res)

    return res

# 
# def system_cmd_result(
#     cwd, cmd,
#     display_stdout=False,
#     display_stderr=False,
#     raise_on_error=False,
#     display_prefix=None,
#     capture_keyboard_interrupt=False):  
#     ''' 
#         Returns the structure CmdResult; raises CmdException.
#         Also OSError are captured.
#         KeyboardInterrupt is passed through unless specified
#         
#         :param write_stdin: A string to write to the process.
#     '''
#     if display_prefix is None:
#         display_prefix = '%s %s' % (cwd, cmd)
#     
#     try:
#             
#         p = subprocess.Popen(
#                 cmd2args(cmd),
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 cwd=cwd)
#         
#         if 1:  # XXX?
#             stdout, stderr = p.communicate()
#             
#             stdout = stdout.strip()
#             stderr = stderr.strip()
#             
#             prefix = display_prefix + 'err> '
#             if display_stderr and stderr:
#                 print(indent(stderr, prefix))
#                 
#             prefix = display_prefix + 'out> '
#             if display_stdout and stdout:
#                 print(indent(stdout, prefix))
#     
#         else:
#             stdout, stderr = alternative_nonworking(p, display_stderr, display_stdout, display_prefix)
#             
#         p.wait()
#         
#     except KeyboardInterrupt:
#         if not capture_keyboard_interrupt:
#             raise
#         else:
#             if raise_on_error:
#                 raise CmdException('Interrupted')
#             else:
#                 res = CmdResult(cwd=cwd, cmd=cmd,
#                                 ret=None, stdout='Interrupted', stderr='Interrupted')  
#                 return res
# 
#     ret = p.returncode 
#     
#     res = CmdResult(cwd, cmd, ret, stdout, stderr)
#     
#     if raise_on_error:
#         if res.ret != 0:
#             raise CmdException(res)
#     
#     return res
        
        
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
