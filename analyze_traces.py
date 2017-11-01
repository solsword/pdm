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

def analyze_trace(models, choices, trace):
  """
  Takes a list of player.PlayerModels, a list of choice.Choices, and a list of
  {name: choice_name, decision: option_name} objects representing a player's
  sequential decisions over the course of one or more play sessions.

  Analyzes how well each decision agrees with each player model, and records
  along-trace, per-choice, and overall statistics about consistency.
  """

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

  # TODO: More formatting here
  for res in results:
    print(res)
    print('-'*80)


if __name__ == "__main__":
  args = sys.argv[1:]
  if len(args) < 3:
    print(
      "Error: At least 3 arguments are required.\n\n{}".format(USAGE)
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
