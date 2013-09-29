'''
.. module:: wunderlist
'''

from wunderpy import api
from requests import Session


class Wunderlist(api.APIClient):
    '''A basic Wunderlist client.'''

    def __init__(self):
        api.APIClient.__init__(self)
        self.lists = {}

    def update_lists(self):
        '''Populate the lists with all tasks.

        This must be run right after logging in,
        before doing any operations.
        '''

        request = self.send_requests([api.calls.get_all_tasks(),
                                      api.calls.get_lists()])
        tasks = next(request)
        lists = next(request)

        inbox = {"title": "inbox", "id": "inbox", "created_on": None,
                 "updated_on": None}
        inbox["tasks"] = {t["title"]: t for t in tasks
                          if t["list_id"] == "inbox"}
        self.lists["inbox"] = inbox

        for list in lists:
            list["tasks"] = {t["title"]: t for t in tasks
                             if t["list_id"] == list["id"]}
            self.lists[list["title"]] = list

    def tasks_for_list(self, list_title):
        '''Get all tasks belonging to a list.'''

        return self.lists.get(list_title)["tasks"]

    def id_for_list(self, list_title):
        '''Return the ID for a list'''

        return self.lists.get(list_title)["id"]

    def get_task(self, task_title, list_title):
        '''Return a dict with all a task with the specified title
        in the specified list.
        '''

        tasks = self.lists.get(list_title)["tasks"]
        return tasks.get(task_title)

    def id_for_task(self, task_title, list_title):
        '''Return the ID for a task in a list.'''

        tasks = self.lists.get(list_title)["tasks"]
        return tasks.get(task_title)["id"]

    def add_task(self, title, list="inbox", note=None, due_date=None,
                 starred=False):
        '''Create a new task.

        :param title: The task's name.
        :type title: str
        :param list: The title of the list that the task will go in.
        :type list: str
        :param note: An additional note in the task.
        :type note: str or None
        :param due_date: The due date/time for the task in ISO format.
        :type due_date: str or None
        :param starred: If the task should be starred.
        :type starred: bool
        '''

        list_id = self.lists[list]["id"]
        add_task = api.calls.add_task(title, list_id, due_date=due_date,
                                      starred=starred)
        result = self.send_request(add_task)
        self.lists.get(list)["tasks"][title] = result

        if note:
            self.send_request(api.calls.set_note_for_task(note, result["id"]))

    def complete_task(self, task_title, list_title="inbox"):
        '''Complete a task with the given title in the given list.'''

        task_id = self.id_for_task(task_title, list_title)
        new_task = self.send_request(api.calls.complete_task(task_id))
        self.tasks_for_list(list_title)[task_title] = new_task

    def delete_task(self, task_title, list_title="inbox"):
        '''Delete a task'''

        task_id = self.id_for_task(task_title, list_title)
        new_task = self.send_request(api.calls.delete_task(task_id))
        del self.tasks_for_list(list_title)[task_title]

    def add_list(self, list_title):
        '''Create a new list'''

        new_list = self.send_request(api.calls.add_list(list_title))
        new_list["tasks"] = {}
        self.lists[list_title] = new_list

    def delete_list(self, list_title):
        '''Delete a list.'''

        self.send_request(api.calls.delete_list(self.id_for_list(list_title)))
        del self.lists[list_title]
