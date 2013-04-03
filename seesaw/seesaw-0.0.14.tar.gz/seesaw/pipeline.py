import contextlib
import os
import traceback

import tornado.stack_context

from seesaw.event import Event

class Pipeline(object):
  def __init__(self, *tasks):
    self.cwd = os.getcwd()
    self.on_start_item = Event()
    self.on_complete_item = Event()
    self.on_fail_item = Event()
    self.on_cancel_item = Event()
    self.on_finish_item = Event()

    self.items_in_pipeline = set()
    self.tasks = []
    for task in tasks:
      self.add_task(task)

  def add_task(self, task):
    task.on_complete_item += self._task_complete_item
    task.on_fail_item += self._task_fail_item
    self.tasks.append(task)

  def enqueue(self, item):
    self.items_in_pipeline.add(item)
    self.on_start_item(self, item)
    self._enqueue_with_except(self.tasks[0], item)

  def _enqueue_with_except(self, task, item):
    @contextlib.contextmanager
    def handle_item_exception(e_type, e_value, tb):
      item.log_output("Failed %s for %s\n" % (task, item.description()))
      item.log_output("%s\n" % traceback.format_exc())
      item.log_error(self, e_value)
      task.fail_item(item)

    with tornado.stack_context.NullContext():
      with tornado.stack_context.ExceptionStackContext(handle_item_exception):
        task.enqueue(item)

  def _task_complete_item(self, task, item):
    task_index = self.tasks.index(task) 
    if len(self.tasks) <= task_index + 1:
      self._complete_item(item)
    else:
      self._enqueue_with_except(self.tasks[task_index + 1], item)

  def _task_fail_item(self, task, item):
    self._fail_item(item)

  def _cancel_item(self, item):
    item.cancel()
    self.items_in_pipeline.remove(item)
    self.on_cancel_item(self, item)
    self.on_finish_item(self, item)

  def _complete_item(self, item):
    item.complete()
    self.items_in_pipeline.remove(item)
    self.on_complete_item(self, item)
    self.on_finish_item(self, item)

  def _fail_item(self, item):
    item.fail()
    self.items_in_pipeline.remove(item)
    self.on_fail_item(self, item)
    self.on_finish_item(self, item)

  def cancel_items(self):
    cancel_items = [ item for item in self.items_in_pipeline if item.may_be_canceled ]

    for item in cancel_items:
      self._cancel_item(item)

  def ui_task_list(self):
    task_list = []
    for task in self.tasks:
      task.fill_ui_task_list(task_list)
    return task_list

  def __str__(self):
    return "Pipeline:\n -> " + ("\n -> ".join(map(str, self.tasks)))


