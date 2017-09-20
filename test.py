#!/usr/bin/env python
"""
test.py

Unit tests.
"""

import traceback

import utils

from packable import pack, unpack
from diffable import diff

from base_types import Certainty, Valence, Salience
from choice import Choice, Option, Outcome
from engagement import PriorityMethod, ModeOfEngagement
from player import PlayerModel
from decision import DecisionMethod, Decision
from perception import Percept, Prospective, Retrospective

all_tests = []
def test(f):
  all_tests.append(f)
  return f

@test
def test_types():
  c = Certainty(0.78)
  assert Certainty.abstract(c) == Certainty.likely
  assert Certainty.abstract(c) == Certainty("likely")

  c = Certainty("impossible")
  assert c == 0.0

  assert type(c + 0.1) == Certainty

  assert str(c) == "Certainty(0.0)"
  assert pack(c) == "impossible"

  return True

def mktest_packable(cls):
  @test
  def test_packable():
    test_stuff = cls._pack_.__doc__.split("```")

    tinst = eval(utils.dedent(test_stuff[1]))
    tobj = eval(utils.dedent(test_stuff[2]))

    uinst = unpack(tobj, cls)
    pobj = pack(tinst)
    urec = unpack(pobj, cls)
    prec = pack(uinst)

    assert tinst == uinst, (
      (
        "Unpacked object doesn't match eval'd version:\n```\n{}\n```\n{}\n```"
        "\nDifferences:\n  {}"
      ).format(str(tinst), str(uinst), "\n  ".join(diff(tinst, uinst)))
    )

    assert pobj == tobj, (
      (
        "Packed object doesn't match given:\n```\n{}\n```\n{}\n```"
        "\nDifferences:\n  {}"
      ).format(
        str(tobj),
        str(pobj),
        "\n  ".join(diff(tobj, pobj))
      )
    )
    assert tinst == urec, (
      (
        "Pack/unpacked object doesn't match:\n```\n{}\n```\n{}\n```"
        "\nDifferences:\n  {}"
      ).format(
        str(tinst),
        str(urec),
        "\n  ".join(diff(tinst, urec))
      )
    )
    assert tobj == prec, (
      (
        "Unpack/packed object doesn't match:\n```\n{}\n```\n{}\n```"
        "\nDifferences:\n  {}"
      ).format(
        str(tobj),
        str(prec),
        "\n  ".join(diff(tobj, prec))
      )
    )

    return True

  test_packable.__name__ = "test_" + cls.__name__.lower() + "_packing"

for cls in [
  Outcome, Option, Choice,
  ModeOfEngagement,
  Percept, Prospective, Retrospective,
  DecisionMethod, Decision,
]:
  mktest_packable(cls)

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
