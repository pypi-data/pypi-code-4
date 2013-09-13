import os
import sys
import win32api
import win32event
import argparse

from ctypes import *
from _multiprocessing import win32
import win32security, ntsecuritycon, win32con, win32api

def get_last_error():
  '''
  Gets the last error by calling the Windows API GetLastError().
  Returns a human-readable string containing the error code and message.

  '''
  message = win32api.FormatMessage(GetLastError()).rstrip()
  return 'Error (%s): %s' % (GetLastError(), message)


def get_debug_privileges():
  '''
  Give ourselves debug privileges.

  Return value:
    If we succeed, the return value is nonzero.
    To determine whether we adjusted all of the specified privileges, call get_last_error.

  '''
  privs = ((win32security.LookupPrivilegeValue('',ntsecuritycon.SE_DEBUG_NAME), win32con.SE_PRIVILEGE_ENABLED),)
  hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32security.TOKEN_ALL_ACCESS)
  ret = win32security.AdjustTokenPrivileges(hToken, False, privs)
  win32api.CloseHandle(hToken)
  return ret


def get_handle_from_pid(pid):
  '''
  Opens a handle to a given process, from its PID.

  Return value:
    If we succeed, the return value is nonzero.
    To determine whether we adjusted all of the specified privileges, call get_last_error.

  '''
  return windll.kernel32.OpenProcess(win32.PROCESS_ALL_ACCESS, False, pid)

  
def query_memory_info(proc_handle, addr, size):
  '''
  Read the memory information given an address and size.

  Return value:
    If we succeed, the return value is nonzero.
    To determine whether we adjusted all of the specified privileges, call get_last_error.

  '''
  # Define the MEMORY_BASIC_INFO structure
  class MEMORY_BASIC_INFO(Structure):
    _fields_ = [("BaseAddress", c_uint),
                ("AllocationBase", c_uint),
                ("AllocationProtect", c_uint),
                ("RegionSize", c_uint),
                ("State", c_uint),
                ("Protect", c_uint),
                ("Type", c_uint)]

  mem_info = MEMORY_BASIC_INFO()
  ret = windll.kernel32.VirtualQueryEx(proc_handle, addr, pointer(mem_info), size)

  if ret != 0: return mem_info
  else: return None


def print_memory_info(mem_info):
  '''
  Convenience function to print out memory information.

  Return value:
    None.

  '''
  print '    [-] Base address: ' + hex(mem_info.BaseAddress)
  print '    [-] Allocation base address: ' + hex(mem_info.AllocationBase)
  print '    [-] Region size: ' + hex(mem_info.RegionSize)
  print '    [-] Allocation state: ' + hex(mem_info.State)
  print '    [-] Initial protect flags:' + hex(mem_info.AllocationProtect)
  print '    [-] Current protect flags:' + hex(mem_info.Protect) + '  <--'
  print '    [-] Type:' + hex(mem_info.Type)


if __name__ == '__main__':
  '''
  To use this script on the command line.

  '''
  # Import coloring library
  try:
    from termcolor import colored
  except ImportError as e:
    def colored(text, color):
      return text

  # Parse arguments
  def str_to_hex(string):
    return int(string, 16)

  parser = argparse.ArgumentParser(description='Set or query memory protection flags for memory in an arbitrary process.',
                                   epilog='If no flags are specified, then the specified memory is only queried.')
  parser.add_argument('pid'     , metavar='<pid>'     , type=int , help='PID of target process')
  parser.add_argument('address' , metavar='<address>' , type=str_to_hex , help='Base address of memory to read/modify protection')
  parser.add_argument('size'    , metavar='<size>'    , type=str_to_hex , help='Size of memory')
  parser.add_argument('flags'   , metavar='<flags>'   , type=str_to_hex , nargs='?' , help='New memory protection flags (optional)')
  parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

  args = parser.parse_args()

  if args.flags is None: QUERY_ONLY = True
  else: QUERY_ONLY = False

  # Get debug privileges
  print '[+] Getting debug privileges:',
  ret = get_debug_privileges()
  if ret != 0: 
    print colored('Success', 'green')
  else: 
    print colored(get_last_error(), 'red')
    sys.exit(-1)

  # Get target process handle
  print '[+] Getting target process handle:',
  proc_handle = get_handle_from_pid(args.pid)
  if proc_handle != 0: 
    print colored('Success', 'green')
  else: 
    print colored(get_last_error(), 'red')
    sys.exit(-2)

  # Read memory protection flags
  print '[+] Reading memory information:',
  mem_info = query_memory_info(proc_handle, args.address, args.size)
  if mem_info is not None:
    print colored('Success', 'green')
  else: 
    print colored(get_last_error(), 'red')
    sys.exit(-3)

  if QUERY_ONLY:
    # Don't change anything
    print
    print colored('[*] Current memory from 0x%x to 0x%x,' % (mem_info.BaseAddress, mem_info.BaseAddress + mem_info.RegionSize), 'yellow'),
    print colored('has protection flags 0x%x.' % (mem_info.Protect), 'yellow')

  if not QUERY_ONLY:
    # Change memory protection flags
    print '[+] Changing memory information:',

    # VirtualProtect wants the *base* address of the memory that is being changed,
    # and it also must have a valid buffer to write old_flags (last parameter) to.
    ret = windll.kernel32.VirtualProtectEx(proc_handle, mem_info.BaseAddress, args.size, args.flags, create_string_buffer(4))
    mem_info_changed = query_memory_info(proc_handle, args.address, args.size)

    if ret != 0: 
      print colored('Success', 'green')
    else: 
      print colored(get_last_error(), 'red')
      sys.exit(-4)
    
    if args.verbose:
      print_memory_info(mem_info_changed)


    print 
    print colored('[*] Changed memory from 0x%x to 0x%x,' % (mem_info.BaseAddress, mem_info.BaseAddress + mem_info.RegionSize), 'yellow'),
    print colored('from protection flags 0x%x to 0x%x.' % (mem_info.Protect, mem_info_changed.Protect), 'yellow')


