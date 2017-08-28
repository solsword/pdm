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

  def abstract(certainty):
    """
    Takes an arbitrary Certainty object (or just a probability between 0 and 1)
    and returns an approximation in terms of the fixed certainty objects
    defined below.
    """
    p = certainty
    if isinstance(p, Certainty):
      p = p.probability

    # TODO: Add certainty grades "rare" and "expected"?
    if 0 <= p < 0.05:
      return Certainty.impossible
    elif 0.05 <= p < 0.45:
      return Certainty.unlikely
    elif 0.45 <= p <= 0.55:
      return Certainty.even
    elif 0.55 < p <= 0.95:
      return Certainty.likely
    elif 0.95 < p <= 1.0:
      return Certainty.certain
    else:
      raise ValueError(
        "Can't find an abstract certainty from invalid probability {:.3f}."
        .format(p)
      )

@super_class_property()
class Impossible(Certainty):
  """
  Represents an event that can actually never occur.
  """
  def __init__(self):
    super().__init__(self, 0.0)

@super_class_property()
class Inconceivable(Certainty):
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

@super_class_property()
class Inviolable(Certainty):
  """
  Represents an event that's actually certain.
  """
  def __init__(self):
    super().__init__(self, 1.0)


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

  def abstract(valence):
    """
    Takes an arbitrary Valence object (or just a valence between -1 and 1) and
    returns an approximation in terms of the fixed valence objects defined
    below.
    """
    v = valence
    if isinstance(v, Valence):
      v = v.value

    # TODO: Add certainty grades "rare" and "expected"?
    if -1 <= v < -0.8:
      return Valence.awful
    elif -0.8 <= v < -0.35:
      return Valence.bad
    elif -0.35 <= v < -0.05:
      return Valence.unpleasant
    elif -0.05 <= v <= 0.05:
      return Valence.neutral
    elif 0.05 < v <= 0.35:
      return Valence.okay
    elif 0.35 < v <= 0.8:
      return Valence.good
    elif 0.8 < v <= 1.0:
      return Valence.wonderful
    else:
      raise ValueError(
        "Can't find an abstract valence from invalid value {:.3f}."
        .format(v)
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


class Visibility:
  """
  Visibility indicates how apparent/relevant an outcome seems before a choice
  is made.
  """
  def __init__(self, val_or_other=1.0):
    if isinstance(val_or_other, Visibility):
      self.value = val_or_other.value
    elif isinstance(val_or_other, float) or isinstance(val_or_other, int):
      if 0 <= val_or_other <= 1:
        self.value = float(val_or_other)
      else:
        raise ValueError("Invalid visibility value {}.".format(val_or_other))
    else:
      raise TypeError(
        (
          "Can't construct a visibility using '{}' of type {}. A number "
          "between 0 and 1 is required."
        ).format(
          val_or_other,
          type(val_or_other)
        )
      )

  def is_visible(self):
    """
    Returns whether or not this outcome has any visibility to the player.
    """
    return self.value > 0

  def abstract(visibility):
    """
    Takes an arbitrary Visibility object (or just a number between 0 and 1) and
    returns an approximation in terms of the fixed visibility objects defined
    below.
    """
    v = visibility
    if isinstance(v, Visibility):
      v = v.value

    if 0 <= v < 0.05:
      return Visibility.invisible
    elif 0.05 <= v < 0.5:
      return Visibility.hinted
    elif 0.5 <= v < 0.9:
      return Visibility.implicit
    elif 0.9 <= v <= 1.0:
      return Visibility.explicit
    else:
      raise ValueError(
        "Can't find an abstract visibility from invalid value {:.3f}."
        .format(v)
      )

@super_class_property()
class Invisible(Visibility):
  """
  An outcome which is completely non-apparent.
  """
  def __init__(self):
    super().__init__(self, 0.0)

@super_class_property()
class Hinted(Visibility):
  """
  An outcome which is hinted at but not fully implied.
  """
  def __init__(self):
    super().__init__(self, 0.3)

@super_class_property()
class Implicit(Visibility):
  """
  An outcome which is implicit and thus apparent with some thinking.
  """
  def __init__(self):
    super().__init__(self, 0.7)

@super_class_property()
class Explicit(Visibility):
  """
  An outcome which is explicit and thus obvious.
  """
  def __init__(self):
    super().__init__(self, 1.0)
