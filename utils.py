"""
utils.py

Various utility functions.
"""

import inspect

class NoDefault:
  """
  A class to indicate a missing default when None is an acceptable value.
  """
  pass

def conform_keys(
  valid,
  suspect,
  default=NoDefault,
  message="Removed spurious key '{}' from input dictionary."
):
  """
  Takes a collection "valid" and a dictionary "suspect" and removes all keys
  from "suspect" that don't exist in "valid", issuing a warning for each
  composed of the given message formatted with the key in question. Then
  proceeds to add a key for each entry of valid that was missing if "default"
  is given.

  Modifies the given "suspect" dictionary in-place.
  """
  for k in list(suspect.keys()):
    if k not in valid:
      raise RuntimeWarning(message.format(k))
      del suspect[k]

  if default != NoDefault:
    for k in valid:
      if k not in suspect:
        suspect[k] = default


def collision(collection):
  """
  Returns an arbitrary item from the given collection that occurs at least
  twice, or None if there is no such item.
  """
  check = list(collection)
  for i in range(len(check)):
    against = check[i]
    for j in range(i+1, len(check)):
      if against == check[j]:
        return against

  return None


def check_names(collection, message="Two objects share name '{}'."):
  """
  Checks that the .name property of every item in the given collection is
  different, and throws a ValueError using the given message if that's not
  true. Returns True.
  """
  nc = collision([x.name for x in collection])
  if nc:
    raise ValueError(message.format(nc))
  return True

def super_class_property(*args, **kwargs):
  """
  A class decorator that adds the class' name in lowercase as a property of
  it's superclass with a value constructed using the subclass' constructor with
  the given arguments. So for example:

    class A:
      pass

    @super_class_property(foo=5)
    class B(A):
      def __init__(self, foo=3):
        self.foo=foo

  Effectively results in the following, after the definition of B:

    A.b = B(foo=5)

  Can be used multiple times with different arguments if desired.
  """
  def add_superclass_property(cls):
    nonlocal args, kwargs
    mro = inspect.getmro(cls)
    if len(mro) <= 2:
      raise TypeError(
        (
          "Class {} can't be a super_class_property because it has no super "
          "class."
        ).format(cls)
      )
    parent = mro[1]
    print("ARGS:", [repr(a) for a in args])
    print()
    setattr(parent, cls.__name__.lower(), cls(*args, **kwargs))
    return cls

  return add_superclass_property
