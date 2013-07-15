class NoApiTokenProvidedException(Exception):
  def __init__(self, message):
     Exception.__init__(self, message)

class MissingArgumentException(Exception):
  def __init__(self, message):
     Exception.__init__(self, message)