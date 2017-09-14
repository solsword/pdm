#!/usr/bin/env python
"""
test.py

Unit tests.
"""

import traceback

all_tests = []
def test(f):
  all_tests.append(f)

@test
def test_types():
  from base_types import Certainty, Valence, Salience
  c = Certainty(0.78)
  assert(Certainty.abstract(c) == Certainty.likely)
  assert(Certainty.abstract(c) == Certainty("likely"))

  c = Certainty("impossible")
  assert(c == 0.0)

  assert(type(c + 0.1) == Certainty)

  return True

def main():
  for t in all_tests:
    try:
      result = t()
    except Exception as e:
      result = e

    if result == True:
      print("{} ... passed".format(t.__name__))
    else:
      print("{} X".format(t.__name__))
      print()
      if isinstance(result, Exception):
        ef = ''.join(
          traceback.format_exception(
            type(result),
            result,
            result.__traceback__
          )
        )
        print(ef)
      else:
        print(result)
      print()


if __name__ == "__main__":
  main()
