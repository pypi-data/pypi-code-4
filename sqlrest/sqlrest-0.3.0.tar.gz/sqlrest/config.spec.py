from configurati import *


frontend = {
  'port'   : optional(type=int, default=8000),
  'host'   : optional(type=str, default='0.0.0.0'),
  'prefix' : optional(type=str, default='')
}

db = {
  'uri': required(type=str)
}

caching = {
  'enabled' : optional(type=bool, default=False),

  # I don't really want to copy/paste all of redis.StrictRedis's
  # arguments, so I'll just leave this as a dict
  'config'  : optional(type=dict, default={}),

  'timeouts' : {
    'tables'    : optional(type=int, default=99999),
    'columns'   : optional(type=int, default=99999),
    'select'    : optional(type=int, default=60 * 5),
    'aggregate' : optional(type=int, default=60 * 60 * 24),
  }
}
