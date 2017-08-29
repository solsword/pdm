"""
base_types.py

Common base types for player decision modelling.
"""

import utils

class NumberType(float):
  """
  A numeric type w/ baggage.
  """
  def __new__(cls, val):
    return float.__new__(cls, val)

  def __init__(self, val):
    float.__init__(self, val)

  def __str__(self):
    return repr(self)

  def __repr__(self):
    return "{}({})".format(type(self).__name__, self.real)


class Certianty(NumberType):
  """
  Represents different certainty levels. The argument should be either a number
  between 0 and 1 or a Certainty (which will be copied).
  """
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

  def __init__(self, prob):
    super().__init__(self, prob)
    if not (0 <= self.real <= 1):
      raise ValueError(
        "Invalid certainty value {} (not in [0,1]).".format(prob)
      )


@utils.super_class_property()
class Impossible(Certainty):
  """
  Represents an event that can actually never occur.
  """
  def __init__(self):
    super().__init__(self, 0.0)

@utils.super_class_property()
class Inconceivable(Certainty):
  """
  Represents an event that's extremely unlikely.
  """
  def __init__(self):
    super().__init__(self, 0.001)

@utils.super_class_property()
class Unlikely(Certainty):
  """
  Represents an event that's fairly unlikely.
  """
  def __init__(self):
    super().__init__(self, 0.2)

@utils.super_class_property()
class Even(Certainty):
  """
  Represents an event that's 50% likely.
  """
  def __init__(self):
    super().__init__(self, 0.5)

@utils.super_class_property()
class Likely(Certainty):
  """
  Represents an event that's fairly likely.
  """
  def __init__(self):
    super().__init__(self, 0.8)

@utils.super_class_property()
class Certain(Certainty):
  """
  Represents an event that's almost completely certain.
  """
  def __init__(self):
    super().__init__(self, 0.999)

@utils.super_class_property()
class Inviolable(Certainty):
  """
  Represents an event that's actually certain.
  """
  def __init__(self):
    super().__init__(self, 1.0)


class Valence(NumberType):
  """
  Represents goodness or badness, on an abstract scale from -1 to 1.
  """
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
      return Valence.unsatisfactory
    elif -0.05 <= v <= 0.05:
      return Valence.neutral
    elif 0.05 < v <= 0.35:
      return Valence.okay
    elif 0.35 < v <= 0.8:
      return Valence.good
    elif 0.8 < v <= 1.0:
      return Valence.great
    else:
      raise ValueError(
        "Can't find an abstract valence from invalid value {:.3f}."
        .format(v)
      )

  def __init__(self, val=0):
    super().__init__(self, val)
    if not (-1 <= val <= 1):
      raise ValueError(
        "Invalid valence value {} (not in [-1, 1]).".format(val)
      )


@utils.super_class_property()
class Awful(Valence):
  """
  A really bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.95, **kwargs)

@utils.super_class_property()
class Bad(Valence):
  """
  A pretty bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.6, **kwargs)

@utils.super_class_property()
class Unsatisfactory(Valence):
  """
  A slightly bad value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=-0.2, **kwargs)

@utils.super_class_property()
class Neutral(Valence):
  """
  The perfectly neutral value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0, **kwargs)

@utils.super_class_property()
class Okay(Valence):
  """
  A slightly positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.2, **kwargs)

@utils.super_class_property()
class Good(Valence):
  """
  A reasonably positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.6, **kwargs)

@utils.super_class_property()
class Great(Valence):
  """
  A really positive value.
  """
  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, value=0.95, **kwargs)


class Salience(NumberType):
  """
  Salience indicates how apparent/relevant an outcome seems before a choice is
  made.
  """
  def abstract(visibility):
    """
    Takes an arbitrary Salience object (or just a number between 0 and 1) and
    returns an approximation in terms of the fixed visibility objects defined
    below.
    """
    v = visibility
    if isinstance(v, Salience):
      v = v.value

    if 0 <= v < 0.05:
      return Salience.invisible
    elif 0.05 <= v < 0.5:
      return Salience.hinted
    elif 0.5 <= v < 0.9:
      return Salience.implicit
    elif 0.9 <= v <= 1.0:
      return Salience.explicit
    else:
      raise ValueError(
        "Can't find an abstract visibility from invalid value {:.3f}."
        .format(v)
      )

  def __init__(self, val=0):
    super().__init__(self, val)
    if not (0 <= val <= 1):
      raise ValueError(
        "Invalid salience value {} (not in [0, 1]).".format(val)
      )

  def is_visible(self):
    """
    Returns whether or not this outcome has any visibility to the player.
    """
    return self.value > 0


@utils.super_class_property()
class Invisible(Salience):
  """
  An outcome which is completely non-apparent.
  """
  def __init__(self):
    super().__init__(self, 0.0)

@utils.super_class_property()
class Hinted(Salience):
  """
  An outcome which is hinted at but not fully implied.
  """
  def __init__(self):
    super().__init__(self, 0.3)

@utils.super_class_property()
class Implicit(Salience):
  """
  An outcome which is implicit and thus apparent with some thinking.
  """
  def __init__(self):
    super().__init__(self, 0.7)

@utils.super_class_property()
class Explicit(Salience):
  """
  An outcome which is explicit and thus obvious.
  """
  def __init__(self):
    super().__init__(self, 1.0)
