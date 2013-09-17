from configurati import required, optional


frontend = optional(
  type={
    'port': required(type=int),
    'host': required(type=str),
    'prefix': optional(default=None),
  },
  default={
    'port': 8000,
    'host': '0.0.0.0',
    'prefix': None
  }
)

db = {
  'uri': required(type=str)
}
