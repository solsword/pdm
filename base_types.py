"""
base_types.py

Common base types for player decision modelling.
"""

import utils
import json

class AbstractValueRange:
  """
  Represents an abstract range of values. Designed for use as a class attribute
  of subtypes of NumberType (see NumberType.__new__).
  """
  def __init__(self, mn, val, mx):
    """
    Min, value, and max for this range.
    """
    self.mn = mn
    self.val = val
    self.mx = mx


def infectious_math(cls):
  """
  Class decorator that makes inherited math ops infectious by reconstructing
  results (probably horribly inefficient...).
  """
  for prp in [
    "__add__", "__radd__",
    "__sub__", "__rsub__",
    "__mul__", "__rmul__",
    "__matmul__", "__rmatmul__",
    "__truediv__", "__rtruediv__",
    "__floordiv__", "__rfloordiv__",
    "__mod__", "__rmod__",
    "__divmod__", "__rdivmod__",
    "__pow__", "__rpow__",
    "__lshift__", "__rlshift__",
    "__rshift__", "__rrshift__",
    "__and__", "__rand__",
    "__xor__", "__rxor__",
    "__or__", "__ror__",

    "__neg__", "__rneg__",
    "__pos__", "__rpos__",
    "__abs__", "__rabs__",
    "__invert__", "__rinvert__",
  ]:
    if hasattr(cls, prp):
      def_impl = getattr(cls, prp)
      def augment(method):
        def augmented(self, *args, **kwargs):
          nonlocal method
          result = method.__get__(self).__call__(*args, **kwargs)
          return cls(result)
        return augmented
      replacement = augment(def_impl)
      replacement.__name__ = prp
      setattr(cls, prp, replacement)

  return cls


@infectious_math
class NumberType(float):
  """
  A numeric type w/ baggage.
  """
  def __new__(cls, val):
    if isinstance(val, cls):
      return val
    elif isinstance(val, AbstractValueRange):
      return float.__new__(cls, val.val)
    elif isinstance(val, str) and hasattr(cls, val):
      return getattr(cls, val)
    else:
      nv = float.__new__(cls, val)
      if hasattr(cls, "validate") and not cls.validate(nv):
        raise ValueError(
          "Value {} is out-of-range for type {}.".format(val, cls.__name__)
        )
      return nv

  def __str__(self):
    return repr(self)

  def __repr__(self):
    return "{}({})".format(type(self).__name__, self.real)


def abstractable(cls):
  """
  A class decorator that scoops up AbstractValueRange class properties in order
  to create .validate and .abstract methods for the class. Note that properties
  added after the class is defined aren't counted. Each AbstractValueRange
  found is is also replaced with a class instance constructed from it.
  """
  cls._ranges = []
  for prp in dir(cls):
    a = getattr(cls, prp)
    if isinstance(a, AbstractValueRange):
      cls._ranges.append((prp, a))
      setattr(cls, prp, cls(a.val))

  cls._ranges = sorted(cls._ranges, key=lambda nr: nr[1].mn)

  @classmethod
  def validate(cls, val):
    ovn = min(r.mn for (n, r) in cls._ranges)
    ovx = max(r.mx for (n, r) in cls._ranges)

    return (isinstance(val, float) and val >= ovn and val <= ovx)

  @classmethod
  def abstract(cls, val):
    found = None
    for (n, r) in cls._ranges[:-1]:
      if (
        ( r.mn == r.mx and val == r.mn )
     or (val >= r.mn and val < r.mx)
      ):
        found = r.val
      elif val < r.mn:
        break

    # check final range including top
    if found == None:
      (n, r) = cls._ranges[-1]
      if (r.mn == r.mx and val == r.mn) or (val >= r.mn and val <= r.mx):
        found = r.val

    if found == None:
      raise ValueError(
        "Can't abstract value '{}' as a {}: outside acceptable range.".format(
          val,
          cls.__name__
        )
      )

    return cls(found)

  def regular_form(self):
    for (n, r) in type(self)._ranges:
      if self == r.val:
        return n
    return self

  cls.validate = validate
  cls.abstract = abstract
  cls.regular_form = regular_form
  return cls


@infectious_math
@abstractable
class Certainty(NumberType):
  """
  Represents different certainty levels. The argument should be either a number
  between 0 and 1 or a Certainty (which will be copied).
  """
  impossible = AbstractValueRange(0, 0, 0)
  inconceivable = AbstractValueRange(0, 0.001, 0.01)
  rare = AbstractValueRange(0.01, 0.05, 0.1)
  unlikely = AbstractValueRange(0.1, 0.2, 0.45)
  even = AbstractValueRange(0.45, 0.5, 0.55)
  likely = AbstractValueRange(0.55, 0.8, 0.9)
  expected = AbstractValueRange(0.9, 0.95, 0.99)
  certain = AbstractValueRange(0.99, 0.999, 1.0)
  invioable = AbstractValueRange(1.0, 1.0, 1.0)


@infectious_math
@abstractable
class Valence(NumberType):
  """
  Represents goodness or badness, on an abstract scale from -1 to 1.
  """
  awful = AbstractValueRange(-1, -0.95, -0.8)
  bad = AbstractValueRange(-0.8, -0.6, -0.35)
  unsatisfactory = AbstractValueRange(-0.35, -0.2, -0.05)
  neutral = AbstractValueRange(-0.05, 0, 0.05)
  okay = AbstractValueRange(0.05, 0.2, 0.35)
  good = AbstractValueRange(0.35, 0.6, 0.8)
  great = AbstractValueRange(0.8, 0.95, 1.0)


@infectious_math
@abstractable
class Salience(NumberType):
  """
  Salience indicates how apparent/relevant an outcome seems before a choice is
  made.
  """
  invisible = AbstractValueRange(0, 0, 0.05)
  hinted = AbstractValueRange(0.05, 0.3, 0.5)
  implicit = AbstractValueRange(0.5, 0.7, 0.9)
  explicit = AbstractValueRange(0.9, 1.0, 1.0)

  def is_visible(self):
    """
    Returns whether or not this outcome has any visibility to the player.
    """
    return self.real > 0
