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
      result = GOALS_REGISTRY[name]
      if type(result) != cls:
        raise TypeError(
          "Goal '{}' is already registered, but it's a(n) {}, not a(n) {}."
          .format(
            name,
            type(result).__name__,
            cls.__name__
          )
        )
      return result
    else:
      g = object.__new__(cls)
      g.name = name
      g.type = cls
      GOALS_REGISTRY[name] = g
      return g

  def __eq__(self, other):
    if not isinstance(other, PlayerGoal):
      return False
    if other.name != self.name:
      return False
    if other.type != self.type:
      return False
    return True

  def __hash__(self):
    return 17 + 31 * hash(self.name) + 47 * hash(self.type)

  def _pack_(self):
    """
    Packs this goal as a simple object, suitable for conversion to JSON. Note
    that the _unpack__ method can also handle name strings as long as they're
    in the GOALS_REGISTRY, so full packing may not always be necessary.
    """
    return {
      "name": self.name,
      "type": self.type.__name__
    }

  def _unpack_(obj):
    """
    Inverse of `_pack_`; creates an instance from a simple object. This method
    also handles simple strings if they name a registered goal.
    """
    if isinstance(obj, str) and obj in GOALS_REGISTRY:
      return GOALS_REGISTRY[obj]

    gl = globals()
    if obj.type in gl and issubclass(gl[obj.type], PlayerGoal):
      return gl[obj.type](obj.name)
    else:
      raise TypeError("Unknown goal type '{}'.".format(obj.type))

  def get(key):
    if key not in GOALS_REGISTRY:
      raise IndexError("There is no registered goal '{}'.".format(key))
    return GOALS_REGISTRY[key]

# TODO: implement state modelling so that goal types matter

class AttractionGoal(PlayerGoal):
  """
  An AttractionGoal specifies that there's some condition or event that the
  player is attracted to (or repelled from). Generally speaking, these goals
  tend to persist indefinitely.
  """
  pass

class AccumulationGoal(PlayerGoal):
  """
  An AccumulationGoal represents the desire to accumulate some resource, such a
  points or money. It comes with thresholds that specify how much of the
  resource is sufficient to feel merely insecure (as opposed to urgently
  anxious), content (as opposed to insecure), and blessed (as opposed to merely
  content). For convenience, the scale may be inverted. Note that some of the
  thresholds may be set to infinity (use numpy.inf) to model different hedonic
  outlooks.
  """
  pass

class AchievementGoal(PlayerGoal):
  """
  An AchievementGoal represents a desire to achieve a certain milestone or
  bring about a certain event. Once the achievement has been accomplished, the
  goal is no longer relevant.
  """
  pass

