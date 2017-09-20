"""
goals.py

Models of player goals. Note that this code mostly doesn't deal with the
relationship between options/outcomes and goals, but instead relies on by-hand
annotation to establish that information.
"""

GOALS_REGISTRY = {}

class PlayerGoal:
  def __new__(cls, name):
    global GOALS_REGISTRY
    if name in GOALS_REGISTRY:
      return GOALS_REGISTRY[name]
    else:
      g = object.__new__(cls)
      g.name = name
      GOALS_REGISTRY[name] = g
      return g

  def __eq__(self, other):
    if not isinstance(other, PlayerGoal):
      return False
    if other.name != self.name:
      return False
    return True

  def __hash__(self):
    return 17 + 31 * hash(self.name)

  def _pack_(self):
    """
    Packs this goal as a simple object, suitable for conversion to JSON.
    """
    return self.name

  def _unpack_(obj):
    """
    Inverse of `_pack_`; creates an instance from a simple object.
    """
    return PlayerGoal(obj)
