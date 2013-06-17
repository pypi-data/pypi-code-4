#!/usr/bin/env python

"""Igloo: a command line scp client.

Usage:
  igloo put [-t] [-f FOLDER] [FILE]
  igloo get [-s | -t] [-f FOLDER] [FILE]
  igloo config [-u URL] [-d DEFAULT] [-a ALIAS]
  igloo -h | --help | --version

Examples:
  igloo put my_file.txt
  igloo put -f private < my_code.py
  echo 'hello world!' | igloo put

Arguments:
  FILE                          File to copy. If no file is specified standard
                                input will be used instead.

Options:
  -h --help                     Show this screen.
  --version                     Show version.
  -f FOLDER --folder=FOLDER     Folder to save/fetch the file to/from.
  -s --stream                   Stream the file to stdout instead of saving it 
                                to a file.
  -t --track                    Track progress.
  -u URL --url=URL              SSH URL.
  -a ALIAS --alias=ALIAS        Url alias.
  -d DEFAULT --default=DEFAULT  Default folder [default: public].

"""

__version__ = '0.0.14'


from contextlib import contextmanager
from getpass import getuser
from json import dump, load
from os import fdopen, makedirs, remove
from os.path import exists, expanduser, join
from sys import stdin, stdout

try:
  from docopt import docopt
  from paramiko import SSHClient
except ImportError:
  pass # probably in setup.py


class Client(object):

  """API client."""

  config_folder = join(expanduser('~'), '.config', 'igloo')
  default_folder = 'public'

  def __init__(self, url=None, default=None, alias=None):
    self.config = self.load_config()
    if url:
      if '@' in url:
        self.config['user'], url = url.split('@', 1)
      else:
        self.config['user'] = getuser()
      self.config['host'], root = url.split(':', 1)
      self.config['root'] = expanduser(root)
    if default:
      self.config['default'] = default
    if alias:
      self.config['alias'] = alias

  @contextmanager
  def get_sftp_client(self, folder=None):
    self.ssh = SSHClient()
    self.ssh.load_host_keys(join(expanduser('~'), '.ssh', 'known_hosts'))
    self.ssh.connect(
      self.config['host'],
      username=self.config['user']
    )
    self.sftp = self.ssh.open_sftp()
    if not folder:
      folder = self.config.get('folder', self.default_folder)
    self.sftp.chdir(join(self.config['root'], folder))
    yield self.sftp
    self.sftp.close()
    self.ssh.close()

  def load_config(self):
    if not exists(self.config_folder):
      makedirs(self.config_folder)
    try:
      with open(join(self.config_folder, 'config')) as config_file:
        return load(config_file)
    except (IOError, ValueError):
      return {}

  def save_config(self):
    with open(join(self.config_folder, 'config'), 'w') as config_file:
      dump(self.config, config_file)

  def get_callback(self):
    def callback(transferred, total):
      progress = 100 * float(transferred) / total
      stdout.write('Progress: %.1f%%\r' % (progress, ))
      stdout.flush()
    return callback

  def put(self, filename, folder, track):
    with self.get_sftp_client(folder) as sftp:
      if filename:
        if track:
          callback = self.get_callback()
        else:
          callback = None
        sftp.put(filename, filename, callback)
      else:
        filename = 'streamed'
        remote_file = sftp.file(filename, 'wb')
        remote_file.set_pipelined(True)
        try:
          while True:
            data = stdin.read(32768)
            if not len(data):
              break
            remote_file.write(data)
        finally:
          remote_file.close()
      if self.config['alias']:
        folder = folder or self.config.get('folder', self.default_folder)
        return '/'.join([self.config['alias'], folder, filename])

  def get(self, filename, folder, stream, track):
    if not stream:
      if track:
        callback = self.get_callback()
      else:
        callback = None
      with self.get_sftp_client(folder) as sftp:
        sftp.get(filename, filename, callback)
        return filename
    else:
      with self.get_sftp_client(folder) as sftp:
        remote_file = sftp.file(filename, 'rb')
        file_size = sftp.stat(filename).st_size
        remote_file.prefetch()
        try:
          size = 0
          while True:
            data = remote_file.read(32768)
            if not len(data):
              break
            stdout.write(data)
            size += len(data)
            stdout.flush()
        finally:
          remote_file.close()

  def list(self, folder):
    with self.get_sftp_client(folder) as sftp:
      return [
        filename
        for filename in sftp.listdir()
        if not filename.startswith('.')
      ]


def main():
  """Command line parser. Docopt is amazing."""
  arguments = docopt(__doc__, version=__version__)
  client = Client(
    url=arguments['--url'],
    default=arguments['--default'],
    alias=arguments['--alias']
  )
  if arguments['config']:
    client.save_config()
    print 'Current configuration:\n'
    for key, value in client.config.items():
      print '%15s: %s' % (key, value)
  elif arguments['put']:
    url = client.put(
      filename=arguments['FILE'],
      folder=arguments['--folder'],
      track=arguments['--track'],
    )
    if url:
      print url
  elif arguments['get']:
    if arguments['FILE']:
      filename = client.get(
        filename=arguments['FILE'],
        folder=arguments['--folder'],
        stream=arguments['--stream'],
        track=arguments['--track'],
      )
      if filename:
        print filename
    else:
      print '\n'.join(client.list(folder=arguments['--folder']))

if __name__ == '__main__':
  main()
