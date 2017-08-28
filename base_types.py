"""
base_types.py

Common base types for player decision modelling.
"""

class Certianty:
  """
  Represents different certainty levels. The argument should be either a number
  between 0 and 1 or a Certainty (which will be copied).
  """
  def __init__(self, prob_or_other):
    if isinstance(prob_or_other, Certainty):
      self.probability = prob_or_other.probability
    elif isinstance(prob_or_other, float) or isinstance(prob_or_other, int):
      if 0 <= prob_or_other <= 1:
        self.probability = float(prob_or_other)
      else:
        raise ValueError("Invalid probability value {}.".format(prob_or_other))
    else:
      raise TypeError(
        (
          "Can't construct a certainty using '{}' of type {}. A number between "
          "0 and 1 is required."
        ).format(
          prob_or_other,
          type(prob_or_other)
        )
      )

@super_class_property()
class Impossible(Certainty):
  """
  Represents an event that's extremely unlikely.
  """
  def __init__(self):
    super().__init__(self, 0.001)

@super_class_property()
class Unlikely(Certainty):
  """
  Represents an event that's fairly unlikely.
  """
  def __init__(self):
    super().__init__(self, 0.2)

@super_class_property()
class Even(Certainty):
  """
  Represents an event that's 50% likely.
  """
  def __init__(self):
    super().__init__(self, 0.5)

@super_class_property()
class Likely(Certainty):
  """
  Represents an event that's fairly likely.
  """
  def __init__(self):
    super().__init__(self, 0.8)

@super_class_property()
class Certain(Certainty):
  """
  Represents an event that's almost completely certain.
  """
  def __init__(self):
    super().__init__(self, 0.999)


class Valence:
  """
  Represents goodness or badness, on an abstract scale from -1 to 1.
  """
  def __init__(self, val_or_other=0):
    if isinstance(val_or_other, Valence):
      self.value = val_or_other.value
    elif isinstance(val_or_other, float) or isinstance(val_or_other, int):
      if -1 <= val_or_other <= 1:
        self.value = float(val_or_other)
      else:
        raise ValueError("Invalid valence value {}.".format(val_or_other))
    else:
      raise TypeError(
        (
          "Can't construct a valence using '{}' of type {}. A number between "
          "-1 and 1 is required."
        ).format(
          val_or_other,
          type(val_or_other)
        )
      )

@super_class_property()
class Awful(Valence):
  """
  A really bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.95, **kwargs)

@super_class_property()
class Bad(Valence):
  """
  A pretty bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.6, **kwargs)

@super_class_property()
class Unpleasant(Valence):
  """
  A slightly bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.2, **kwargs)

@super_class_property()
class Neutral(Valence):
  """
  The perfectly neutral value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0, **kwargs)

@super_class_property()
class Okay(Valence):
  """
  A slightly positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.2, **kwargs)

@super_class_property()
class Good(Valence):
  """
  A reasonably positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.6, **kwargs)

@super_class_property()
class Wonderful(Valence):
  """
  A really positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.95, **kwargs)
