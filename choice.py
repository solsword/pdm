"""
choice.py

Code for dealing with choice structures.
"""

import random

from base_types import Certainty
from base_types import Valence
from base_types import Salience

class Outcome:
  """
  An outcome models a consequence of an option including salience to the
  player before making the decision, probability of occurrence once a decision
  is made, and effects on various goals. Outcomes are included in Option
  objects to model choice structures.

  Note: differential outcome salience can also be modeled through manipulating
  player goals.
  """
  def __init__(
    self,
    name,
    goal_effects,
    salience,
    apparent_likelihood,
    actual_likelihood=None,
  ):
    """
    name:
      The name for this outcome. Must be unique within an option.

    goal_effects:
      How this outcome affects various goals. Should be a mapping from goal
      names to Valences (or just raw numbers; see base_types.py).

    salience:
      The Salience level of this outcome for prospective considerations (or
      just a raw number; see base_types.py).
      TODO: Split into prospective/retrospective salience? Retroactive salience
      distrbutions over time?

    apparent_likelihood:
      Pre-decision likelihood of this outcome as apparent to the player. Should
      be a Certainty object or it may be given as a probability value (see
      base_types.py)

    actual_likelihood:
      Actual likelihood of this outcome based on internal game logic. Uses the
      same values as apparent_likelihood. If not given, defaults to the value
      of apparent_likelihood.
    """
    self.name = name
    self.goal_effects = {k: Valence(v) for k, v in goal_effects.items()}
    self.salience = Salience(salience)
    self.apparent_likelihood = Certainty(apparent_likelihood)
    if actual_likelihood is None:
      self.actual_likelihood = Certainty(self.apparent_likelihood)
    else:
      self.actual_likelihood = Certainty(actual_likelihood)

class Option:
  """
  An option is one of several discrete options at a choice. It includes a set
  of outcomes that specify how it appears to the player and what will happen
  once it's chosen. Choices are made of Option objects.
  """
  def __init__(self, name, outcomes):
    """
    name:
      Name of this option. Must be unique within a Choice.

    outcomes:
      A collection of outcomes that define this option. Their names must be
      unique within the collection (otherwise a ValueError will result).
    """
    self.name = name

    check_names(
      outcomes,
      "Two outcomes named '{{}}' cannot coexist within Option '{}'.".format(
        self.name
      )
    )

    self.outcomes = { o.name: o for o in outcomes }

  def add_outcome(self, outcome):
    """
    Adds an outcome to this option, raising a KeyError if this option already
    has an outcome with the given outcome's name.
    """
    if outcome.name in self.outcomes:
      raise KeyError(
        "Option '{}' already contains an outcome '{}'.".format(
          self.name,
          outcome.name
        )
      )

    self.outcomes[outcome.name] = outcome

  def remove_outcome(self, outcome_name):
    """
    Removes an outcome from this option, raising a KeyError if no outcome with
    the given name can be found.
    """
    if outcome_name not in self.outcomes:
      raise KeyError(
        "Option '{}' doesn't contain any outcome '{}'.".format(
          self.name,
          outcome_name
        )
      )

    del self.outcomes[outcome_name]

  def sample_outcomes(self):
    """
    Returns a sample of outcomes for this option according to their actual
    likelihoods. The sample is returned as a dictionary mapping outcome names
    to Outcome objects. The dictionary is fresh but the Outcome objects aren't
    copies, so they shouldn't be modified. Note that it's almost always
    possible for the outcomes list to be empty.
    """
    results = {}

    for o in self.outcomes:
      out = self.outcomes[o]
      r = random.uniform(0.0, 1.0)
      if r < out.probability:
        results[o] = out

    return results


class Choice:
  """
  A Choice is a collection of Options, each of which contains one or more
  outcomes.
  """
  def __init__(self, name, options):
    """
    name:
      The name of this choice.

    options:
      A collection of options. Their names must be unique, or a ValueError will
      be generated.
    """
    self.name = name

    check_names(
      options,
      "Two options named '{{}}' cannot coexist within Choice '{}'.".format(
        self.name
      )
    )

    self.options = { o.name: o for o in options }

  def add_option(self, option):
    """
    Adds the given option to this choice. Raises a KeyError if an option with
    that name is already part of this choice.
    """
    if option.name in self.options:
      raise KeyError(
        "Choice '{}' already contains an option '{}'.".format(
          self.name,
          option.name
        )
      )

    self.options[option.name] = option

  def remove_option(self, option_name):
    """
    Removes the given option (by name) from this choice. Raises a KeyError if
    that option isn't present.
    """
    if option_name not in self.options:
      raise KeyError(
        "Choice '{}' doesn't contain an option '{}'.".format(
          self.name,
          option_name
        )
      )
    del self.options[option_name]


def parse_choice(json):
  """
  Parses a full choice definition from a json format. An example:

  {
    name: "Rescue the baby dragon or not?",
    options: {
      rescue_it: {
        bites_your_hand: {
          salience: "implicit",
          apparent_likelihood: "even",
          effects: {
            health_and_safety: "unsatisfactory",
            befriend_dragon: "unsatisfactory",
          }
        },
        appreciates_kindness: {
          salience: "explicit",
          apparent_likelihood: "likely",
          effects: {
            befriend_dragon: "good"
          }
        }
      },

      leave_it: {
        dislikes_abandonment: {
          salience: "explicit",
          apparent_likelihood: "certain",
          effects: {
            befriend_dragon: "bad"
          }
        },
        dies: {
          salience: "hinted",
          apparent_likelihood: "unlikely",
          actual_likelihood: "even",
          effects: {
            befriend_dragon: "awful"
            kill_dragon: "great"
          }
        }
      }
    }
  }

  """
  # TODO: Implement this!
