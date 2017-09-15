#!/usr/bin/env python
"""
test.py

Unit tests.
"""

import traceback

import utils

from base_types import Certainty, Valence, Salience
from choice import Choice, Option, Outcome
from engagement import PriorityMethod, ModeOfEngagement
from player import PlayerModel
from decision import DecisionMethod, Decision

all_tests = []
def test(f):
  all_tests.append(f)
  return f

@test
def test_types():
  c = Certainty(0.78)
  assert(Certainty.abstract(c) == Certainty.likely)
  assert(Certainty.abstract(c) == Certainty("likely"))

  c = Certainty("impossible")
  assert(c == 0.0)

  assert(type(c + 0.1) == Certainty)

  assert(str(c) == "Certainty(0.0)")
  assert(c.regular_form() == "impossible")

  return True

def mktest_json(cls):
  @test
  def test_json():
    fj = cls.from_json
    test_stuff = fj.__doc__.split("```")

    tin = utils.dedent(test_stuff[1])
    tcmp = utils.dedent(test_stuff[2])

    o = cls.from_json(tin)
    oalt = eval(tcmp)
    jrec = c.json(indent=2)
    orec = cls.from_json(jrec)

    assert(o == oalt)
    assert("\n" + jrec + "\n" == tin)
    assert(o == orec)

    return True

  print(test_json)
  test_json.__name__ = "test_" + cls.__name__.lower() + "_json"

mktest_json(Choice)
mktest_json(ModeOfEngagement)

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
