_target_builder_map = {}
_action_map = {}

def has_builder(tgt):
  return tgt in _target_builder_map
def register_builder(tgt, builder):
  _target_builder_map[tgt] = builder
def get_builder(tgt):
  return _target_builder_map[tgt]

def get_targets():
  return _target_builder_map.keys()

def has_action(name):
  return name in _action_map
def register_action(action):
  _action_map[action.__name__] = action
def get_action(name):
  return _action_map[name]
