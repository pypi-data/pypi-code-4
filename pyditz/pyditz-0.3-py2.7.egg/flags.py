"""
Issue, release and status flags.
"""

UNSTARTED = ":unstarted"
PAUSED = ":paused"
IN_PROGRESS = ":in_progress"
CLOSED = ":closed"
STATUS = {UNSTARTED: "unstarted",
          PAUSED: "paused",
          IN_PROGRESS: "in progress",
          CLOSED: "closed"}
FLAGS = {UNSTARTED: "_",
         PAUSED: "=",
         IN_PROGRESS: ">",
         CLOSED: "x"}
SORT = {UNSTARTED: 1,
        PAUSED: 2,
        IN_PROGRESS: 3,
        CLOSED: 0}

BUGFIX = ":bugfix"
FEATURE = ":feature"
TASK = ":task"
TYPE = {BUGFIX: "bugfix",
        FEATURE: "feature",
        TASK: "task"}
TYPE_PLURAL = {BUGFIX: "bugfixes",
               FEATURE: "features",
               TASK: "tasks"}

FIXED = ":fixed"
WONTFIX = ":wontfix"
REORG = ":reorg"
DISPOSITION = {FIXED: "fixed",
               WONTFIX: "won't fix",
               REORG: "reorganized"}

RELEASED = ":released"
UNRELEASED = ":unreleased"
RELSTATUS = {RELEASED: "released",
             UNRELEASED: "unreleased"}
