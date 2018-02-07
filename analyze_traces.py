#!/usr/bin/env python3
"""
analyze_traces.py

Script for analyzing a player behavior trace accompanied by a set of choices
and a list of player models.

For each decision made in the trace, consistency is calculated with the
decision model contained in each given player model, and stats on per-model
consistency-over-time, consistency-per-decision, and overall trace consistency
are produced.

The format for player models is:

  A JSON string containing a list at the top level where each entry is
  unpackable into a player.PlayerModel object (see player.py and specifically
  PlayerModel._unpack_).

The format for choices is:
  
  A single JSON string which contains a list at the top level, where each entry
  is unpackable as a choice.Choice object (see choice.py and specifically
  Choice._unpack_).

The format for a trace is:

  A JSON string containing a list at the top level representing an ordered
  record of player decisions. Each decision is recorded as an object with
  attributes "name" and "decision" specifying the name of a choice and the name
  of an option at that choice respectively. Other attributes, such as
  timestamps, may be present but will be ignored.
"""

USAGE = """\
Usage:
  analyze_traces.py MODELS CHOICES TRACE1 [TRACE2 ...]

Analyzes which player model(s) a player trace (or set of traces) is consistent
with. Reports on along-trace, per-choice, and overall consistency for each
trace. See docstring in file for more details.
"""

import sys
import json

import choice
import player

from packable import pack, unpack

def combine_per_choice(*args):
  """
  Combines two or more per-choice analytics results into one.
  """
  args = list(args)
  result = args.pop()
  new_weight = None
  new_averages = None
  while args:
    other = args.pop()
    for key in other:
      if key not in result:
        result[key] = other[key]
      else:
        old_weight, old_averages = result[key]
        other_weight, other_averages = other[key]
        if (
          new_averages
      and set(old_averages.keys()) != set(new_averages.keys())
        ):
          raise ValueError(
            "Can't combine per-choice results which used different sets of "
            "player models."
          )
        new_weight = old_weight + other_weight
        new_averages = {}
        for pmn in old_averages:
          new_averages[pmn] = (
            old_averages[pmn] * old_weight
          + other_averages[pmn] * other_weight
          ) / new_weight
        result[key] = (new_weight, new_averages)

  return result


def analyze_trace(models, choices, trace):
  """
  Takes a list of player.PlayerModels, a list of choice.Choices, and a list of
  {name: choice_name, decision: option_name} objects representing a player's
  sequential decisions over the course of one or more play sessions.

  Analyzes how well each decision agrees with each player model, and records
  along-trace, per-choice, and overall statistics about consistency.
  """
  choices = {
    ch.name: ch
      for ch in choices
  }
  agreements = []
  by_cname = {}
  for cname, decision in trace:
    agreement = {
      pm.name: pm.assess_decision(choices[cname], decision)
        for pm in models
    }
    agreements.append(agreement)
    if cname not in by_cname:
      by_cname[cname] = []
    by_cname[cname].append(agreement)

  trajectories = {
    pm.name: [ agr[pm.name] for agr in agreements ]
      for pm in models
  }

  averages = {
    pm.name: sum(trajectories[pm.name]) / len(trajectories[pm.name])
      for pm in models
  }

  # TODO: This correctly HERE
  per_choice = {
    cname: (
      len(by_cname[cname]),
      {
        pm: sum(
          [ agr[pm.name] for agr in by_cname[cname] ]
        ) / len(by_cname[cname])
          for pm in models
      }
    )
      for cname in by_cname
  }

  return averages, trajectories, per_choice


def main(models_str, choices_str, trace_strings):
  """
  Takes JSON strings specifying models and choices and a list of JSON strings
  specifying traces and runs analyze_trace on each trace before summarizing
  results.
  """
  packed_models = json.loads(models_str)
  models = []
  for i, obj in enumerate(packed_models):
    try:
      models.append(unpack(obj, player.PlayerModel))
    except Exception as e:
      raise ValueError(
        "Failed to unpack player model #{}".format(i)
      ) from e

  packed_choices = json.loads(choices_str)
  choices = []
  for i, obj in enumerate(packed_choices):
    try:
      choices.append(unpack(obj, choice.Choice))
    except Exception as e:
      raise ValueError(
        "Failed to unpack choice #{}".format(i)
      ) from e

  traces = [json.loads(st) for st in trace_strings]

  results = [analyze_trace(models, choices, tr) for tr in traces]

  all_decisions = {}
  for ch in choices:
    cn = ch.name
    if cn not in all_decisions:
      all_decisions[cn] = {}
  for tr in traces:
    for tch in tr:
      add_to = all_decisions[tch[0]]
      if tch[1] in add_to:
        add_to[tch[1]] += 1
      else:
        add_to[tch[1]] = 1

  overall_per_choice = combine_per_choice(*[res[2] for res in results])

  # TODO: More formatting here
  for res in results:
    print("Averages:\n", res[0])
    print('-'*80)

  for cn in overall_per_choice:
    times, agreements = overall_per_choice[cn]
    print("Choice: '{}' (seen {} times)".format(cn, times))
    print("Decisions:")
    for dc in all_decisions[cn]:
      print("  {}: {}".format(dc, all_decisions[cn][dc]))
    print("Model agreement:")
    for pmn in agreements:
      print("  {}: {:.3f}".format(pmn, agreements[pmn]))
    print('-'*80)


if __name__ == "__main__":
  args = sys.argv[1:]
  if len(args) < 3:
    print(
      "Error: At least 3 arguments are required.\n\n{}".format(USAGE),
      file=sys.stderr
    )
    exit(1)

  models_file = sys.argv[1]
  choices_file = sys.argv[2]
  trace_files = sys.argv[3:]

  with open(models_file, 'r') as fin:
    models_str = fin.read()

  with open(choices_file, 'r') as fin:
    choices_str = fin.read()

  trace_strings = []
  for f in trace_files:
    with open(f, 'r') as fin:
      trace_strings.append(fin.read())

  main(models_str, choices_str, trace_strings)
