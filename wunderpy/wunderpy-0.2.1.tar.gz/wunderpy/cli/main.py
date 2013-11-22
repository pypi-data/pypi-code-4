'''Command line script for wunderpy.'''


import argparse

from wunderpy import Wunderlist
from .storage import get_token, setup
import colors


class WunderlistCLI(object):
    def __init__(self):
        self.wunderlist = None
        self.get_wunderlist()

    def get_wunderlist(self):
        try:
            token = get_token()
        except IOError:  # first run
            setup()
            token = get_token()

        wunderlist = Wunderlist()
        wunderlist.set_token(token)
        wunderlist.update_lists()
        self.wunderlist = wunderlist

    def add(self, task, list):
        '''Add a task or create a list.
        If just --task is used, optionally with --list, add a task.
        If just --list is used, create an empty list.
        '''

        if task and list:  # adding a task to a list
            self.wunderlist.add_task(task, list=list)
        elif list != "inbox":  # creating a list
            self.wunderlist.add_list(list)

    def complete(self, task, list):
        self.wunderlist.complete_task(task, list_title=list)

    def delete_task(self, task, list):
        self.wunderlist.delete_task(task, list)

    def delete_list(self, list):
        self.wunderlist.delete_list(list)

    def overview(self):
        for title, list in self.wunderlist.lists.iteritems():
            tasks = list["tasks"]
            with colors.pretty_output(colors.BOLD, colors.UNDERSCORE) as out:
                out.write(title)

            task_count = 0
            for task_title, info in tasks.iteritems():
                if task_count <= 4:
                    pretty_print_task(task_title, info)
                    task_count += 1
                else:
                    break
            print("")

    def display(self, list_title):
        try:
            list = self.wunderlist.lists[list_title]
        except KeyError:
            print("That list does not exist.")
            exit()

        with colors.pretty_output(colors.BOLD, colors.UNDERSCORE) as out:
            out.write(list_title)

        for task_title, info in list["tasks"].iteritems():
            pretty_print_task(task_title, info)


def pretty_print_task(title, info):
    CHECK = u"\u2713".encode("utf-8")
    STAR = u"\u2605".encode("utf-8")

    is_completed = CHECK  # in other words, True
    if not info["completed_at"]:
        is_completed = " "  # not completed, False

    use_star = STAR  # True
    if not info["starred"]:
        use_star = ""  # False

    line = "[{}] {} {}".format(is_completed, title, use_star)
    print(line)


def main():
    parser = argparse.ArgumentParser(description="A Wunderlist CLI client.")

    parser.add_argument("-a", "--add", dest="add", action="store_true",
                        default=False, help="Add a task or list.")
    parser.add_argument("-c", "--complete", dest="complete",
                        action="store_true", default=False,
                        help="Complete a task.")
    parser.add_argument("-d", "--delete", dest="delete", action="store_true",
                        default=False, help="Delete a task or list.")
    parser.add_argument("-o", "--overview", dest="overview",
                        action="store_true", default=False,
                        help="Display an overview of your "
                        "Wunderlist. Limited to 5 tasks per list.")
    parser.add_argument("--display", dest="display", action="store_true",
                        default=False, help="Display all items in a list "
                        "specified with --list.")
    parser.add_argument("-l", "--list", dest="list", default="inbox",
                        help="Used to specify a list, either for a task in a "
                        "certain list, or for a command that only operates "
                        "on lists. Default is inbox.")
    parser.add_argument("-t", "--task", dest="task",
                        help="Used to specify a task name.")
    args = parser.parse_args()

    cli = WunderlistCLI()

    if args.add:
        cli.add(args.task, args.list)
    elif args.complete:
        cli.complete(args.task, args.list)
    elif args.delete:
        if args.task:
            cli.delete_task(args.task, args.list)
        else:
            cli.delete_list(args.list)
    elif args.overview:
        cli.overview()
    elif args.display:
        cli.display(args.list)
    else:
        cli.overview()
