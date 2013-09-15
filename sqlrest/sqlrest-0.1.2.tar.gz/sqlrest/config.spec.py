from configurati import required, optional


frontend = optional(
  type={
    'port': required(type=int),
    'host': required(type=str),
  },
  default={
    'port': 8000,
    'host': '0.0.0.0',
  }
)

db = {
  'uri': required(type=str)
}
