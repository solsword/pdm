#!/usr/bin/env python
"""
test.py

Unit tests.
"""

import traceback

import utils

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

  assert(str(c) == "Certainty(0.0)")
  assert(c.regular_form() == "impossible")

  return True

@test
def test_choice_json():
  from base_types import Certainty, Valence, Salience
  from choice import Choice, Option, Outcome
  fj = Choice.from_json
  test_stuff = fj.__doc__.split("```")

  tin = utils.dedent(test_stuff[1])
  tcmp = utils.dedent(test_stuff[2])

  c = Choice.from_json(tin)
  calt = eval(tcmp)
  jrec = c.json(indent=2)
  crec = Choice.from_json(jrec)

  assert(c == calt)
  assert("\n" + jrec + "\n" == tin)
  assert(c == crec)

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
