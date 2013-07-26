"""console-pb

Copyright (C) 2009 by Trey Stout

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
__author__ = "Trey Stout <treystout@gmail.com>"

import collections
import sys
from datetime import datetime, timedelta

class Timing(object):
  def __init__(self, delta, steps):
    self.delta = delta
    self.steps = steps

class ProgressBar(object):
  SAMPLES = 1000 # number of time deltas to hold (for running ETA)
  MAX_DRAWS_PER_SECOND = 5

  ESC = {
      'reset': '\033[0m',
      'bold': '\033[01m',
      'red': '\033[0;31m',
      'blue': '\033[0;34m',
      'green': '\033[0;32m',
      'grey': '\033[22;39m',
      '0_col': '\033[0G', # moves cursor to column 0
      'kill': '\033[K', # erase entire line
  }

  TEMPLATE = u"%(0_col)s%(kill)s%(blue)s%(label)s %(reset)s%(bold)s["\
      u"%(progress_blocks)s%(empty_blocks)s%(reset)s%(bold)s]%(reset)s "\
      u"%(bold)s%(green)s%(progress)0.1f%% %(reset)s%(msg)s (ETA:%(ETA)s)"

  def __init__(self, label, total_steps, current_step=0, width=80,
      progress_char=u'\u25AA', blank_char=u'\u25AB', debug=True):
    self.label = label
    self.total_steps = total_steps
    self.current_step = current_step
    self.width = width
    self.progress_char = progress_char
    self.blank_char = blank_char
    self.debug = debug
    self.samples = collections.deque(maxlen=ProgressBar.SAMPLES)
    self.last_step_time = datetime.now()
    self.last_step = 0
    self.started = datetime.now()
    self.last_draw_time = datetime.now()
    self.progress = 0

  def _format_ETA(self, ETA):
    if ETA < 0:
      return "?"
    # ETA should come in as microseconds
    days, ETA = divmod(ETA, 60 * 60 * 24)
    hours, ETA = divmod(ETA, 60 * 60)
    minutes, ETA = divmod(ETA, 60)
    out = []
    if days > 0:
      out.append("%ddays" % days)
    elif hours > 0:
      out.append("%02dhours" % hours)
    elif minutes > 0:
      out.append("%02dmin" % minutes)
    elif ETA > 0:
      out.append("%05.2fs" % ETA)
    return ' '.join(out)

  def _compute_ETA(self):
    if len(self.samples) > 5:
      steps_remaining = self.total_steps - self.current_step
      total_steps = 0
      total_time = timedelta(seconds=0)
      for t in self.samples:
        total_steps += t.steps
        total_time += t.delta
      avg_step_speed = 0
      if total_steps != 0:
        avg_step_speed = total_time.total_seconds() / float(total_steps)
      return avg_step_speed * steps_remaining
    else:
      return -1.0 # we have no idea yet

  def _update_counts(self, current_step):
    if current_step is None:
      self.current_step += 1
    else:
      self.current_step = current_step
    if self.current_step == 1:
      self.started = datetime.now()

    self.progress = 0.5
    if self.total_steps != 0:
      self.progress = self.current_step / float(self.total_steps)

    # some housekeeping to store timedeltas so we can have an accurate ETA 
    self.samples.append(
        Timing((datetime.now() - self.last_step_time),
          self.current_step - self.last_step)
    )
    self.last_step_time = datetime.now()
    self.last_step = self.current_step

  def draw(self, msg='', current_step=None):
    # don't draw on non-tty streams
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
      self._update_counts(current_step)

      time_since_last_draw = datetime.now() - self.last_draw_time
      if (time_since_last_draw.seconds > (1/float(self.MAX_DRAWS_PER_SECOND))) \
          or self.current_step == self.total_steps:
        # copute ETA and blocks available to draw the bar
        self.ETA = self._format_ETA(self._compute_ETA())
        self.msg = msg
        w = self.width - len(self.label) - len(str(self.ETA)) - len(msg) - 16

        # compute how many blocks we can draw for progress made and empty blocks
        prog_w = int(w * self.progress)
        empty_w = w - prog_w
        self.progress_blocks = "%s%s" % (self.ESC['green'],
            self.progress_char * prog_w)
        self.empty_blocks = "%s%s" % (self.ESC['grey'], self.blank_char *
            empty_w)

        # write it out, and Don't forget to flush, kids!
        out_vars = self.ESC
        out_vars.update(self.__dict__)
        out_vars['progress'] *= 100
        out = self.TEMPLATE % out_vars
        sys.stdout.write(out.encode('utf8'))
        sys.stdout.flush()
        self.last_draw_time = datetime.now()

      # don't rate limit the last step, show it always
      if self.current_step == self.total_steps and self.debug:
        elapsed = datetime.now() - self.started
        print "\nStarted at %s and completed %d steps in %s" % (self.started,
            self.total_steps,
            self._format_ETA(elapsed.total_seconds()))


if __name__ == "__main__":
  import random
  import string
  import time
  RUNS = 100
  pb = ProgressBar('Computing Pi', RUNS, progress_char=u'X', blank_char='O', width=120)
  #d = timedelta(seconds=20200L)
  #print pb._format_ETA(pb._timedelta_to_microseconds(d))

  for i in xrange(RUNS):
    #time.sleep(0.1)
    time.sleep(random.random() * 0.1)
    #if i % 13 == 0:
    #  pb.draw(current_step=i)
    #pb.draw(''.join(random.sample(string.ascii_letters, random.randint(2, 20))), current_step=i)
    pb.draw(msg="dirname %d" % i)
