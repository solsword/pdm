"""
choice.py

Code for dealing with choice structures.
"""

import random
import json

import utils

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

  def __str__(self):
    # TODO: Better here
    return self.json()

  def __eq__(self, other):
    if not isinstance(other, Outcome):
      return False
    if self.name != other.name:
      return False
    if self.goal_effects != other.goal_effects:
      return False
    if self.salience != other.salience:
      return False
    if self.apparent_likelihood != other.apparent_likelihood:
      return False
    if self.actual_likelihood != other.actual_likelihood:
      return False
    return True

  def __hash__(self):
    h = hash(self.name)
    for i, g in enumerate(self.goal_effects):
      if i % 2:
        h ^= hash(self.goal_effects[g]) + hash(g)
      else:
        h += hash(self.goal_effects[g]) ^ hash(g)

    h += hash(self.salience)
    h ^= hash(self.apparent_likelihood)
    h += hash(self.actual_likelihood)

    return h

  def json(self, indent=None):
    """
    Returns a json representation of this option.

        "leave_it": {
          "dislikes_abandonment": {
            "salience": "explicit",
            "apparent_likelihood": 0.97,
            "effects": {
              "befriend_dragon": "bad"
            }
          },
          "dies": {
            "salience": "hinted",
            "apparent_likelihood": "unlikely",
            "actual_likelihood": "even",
            "effects": {
              "befriend_dragon": "awful"
              "kill_dragon": "great"
            }
          }
        }
    """
    if self.apparent_likelihood == self.actual_likelihood:
      dd = {
        "salience": self.salience.regular_form(),
        "apparent_likelihood": self.apparent_likelihood.regular_form(),
        "effects": {
          g: self.goal_effects[g].regular_form()
            for g in self.goal_effects
        }
      }
    else:
      dd = {
        "salience": self.salience.regular_form(),
        "apparent_likelihood": self.apparent_likelihood.regular_form(),
        "actual_likelihood": self.actual_likelihood.regular_form(),
        "effects": {
          g: self.goal_effects[g].regular_form()
            for g in self.goal_effects
        }
      }
    return json.dumps(
      dd,
      indent=indent,
      sort_keys=True,
      default=lambda obj:json.loads(obj.json())
    )

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

    utils.check_names(
      outcomes,
      "Two outcomes named '{{}}' cannot coexist within Option '{}'.".format(
        self.name
      )
    )

    self.outcomes = { o.name: o for o in outcomes }

  def __str__(self):
    # TODO: Better here?
    return self.json()

  def __eq__(self, other):
    if not isinstance(other, Option):
      return False
    if self.name != other.name:
      return False
    if self.outcomes != other.outcomes:
      return False
    return True

  def __hash__(self):
    h = hash(self.name)
    for i, out in enumerate(self.outcomes):
      if i % 2:
        h ^= hash(self.outcomes[out])
      else:
        h += hash(self.outcomes[out])

    return h


  def json(self, indent=None):
    """
    Returns a json representation of this option.
    """
    return json.dumps(
      self.outcomes,
      indent=indent,
      sort_keys=True,
      default=lambda obj:json.loads(obj.json())
    )

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

    utils.check_names(
      options,
      "Two options named '{{}}' cannot coexist within Choice '{}'.".format(
        self.name
      )
    )

    self.options = { o.name: o for o in options }

  def __str__(self):
    # TODO: Better here
    return self.json()

  def __eq__(self, other):
    if not isinstance(other, Choice):
      return False
    if self.name != other.name:
      return False
    if self.options != other.options:
      return False
    return True

  def __hash__(self):
    h = hash(self.name)
    for i, opt in enumerate(self.options):
      if i % 2:
        h ^= hash(self.options[opt])
      else:
        h += hash(self.options[opt])

    return h

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

  def json(self, indent=None):
    """
    Returns a json representation of this choice.
    """
    return json.dumps(
      { "name": self.name, "options": self.options },
      indent=indent,
      sort_keys=True,
      default=lambda obj:json.loads(obj.json())
    )

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

  def from_json(jin):
    """
    A static method that parses a full choice definition from a json format and
    returns a new Choice object. An example:

    ```
    {
      "name": "Rescue the baby dragon or not?",
      "options": {
        "leave_it": {
          "dies": {
            "actual_likelihood": "even",
            "apparent_likelihood": "unlikely",
            "effects": {
              "befriend_dragon": "awful",
              "kill_dragon": "great"
            },
            "salience": "hinted"
          },
          "dislikes_abandonment": {
            "apparent_likelihood": 0.97,
            "effects": {
              "befriend_dragon": "bad"
            },
            "salience": "explicit"
          }
        },
        "rescue_it": {
          "appreciates_kindness": {
            "apparent_likelihood": "likely",
            "effects": {
              "befriend_dragon": "good"
            },
            "salience": "explicit"
          },
          "bites_your_hand": {
            "apparent_likelihood": "even",
            "effects": {
              "befriend_dragon": "unsatisfactory",
              "health_and_safety": "unsatisfactory"
            },
            "salience": "implicit"
          }
        }
      }
    }
    ```
    Choice(
      "Rescue the baby dragon or not?", 
      [
        Option(
          "rescue_it",
          [
            Outcome(
              "bites_your_hand",
              {
                "health_and_safety": Valence("unsatisfactory"),
                "befriend_dragon": Valence("unsatisfactory"),
              },
              Salience("implicit"),
              Certainty("even"),
            ),
            Outcome(
              "appreciates_kindness",
              { "befriend_dragon": "good" },
              "explicit",
              "likely",
            )
          ]
        ),
        Option(
          "leave_it",
          [
            Outcome(
              "dislikes_abandonment",
              { "befriend_dragon": "bad" },
              "explicit",
              0.97,
            ),
            Outcome(
              "dies",
              {
                "befriend_dragon": "awful",
                "kill_dragon": "great"
              },
              "hinted",
              "unlikely",
              actual_likelihood="even"
            )
          ]
        )
      ]
    )
    ```
    """
    obj = json.loads(jin)
    cn = obj["name"]
    optobj = obj["options"]

    options = []
    for opn in optobj:
      outcomes = []
      outobj = optobj[opn]
      for oun in outobj:
        sal = outobj[oun]["salience"]
        apl = outobj[oun]["apparent_likelihood"]
        if "actual_likelihood" in outobj[oun]:
          acl = outobj[oun]["actual_likelihood"]
        else:
          acl = outobj[oun]["apparent_likelihood"]
        fx = outobj[oun]["effects"]

        outcomes.append(
          Outcome(
            oun,
            { gn: Valence(fx[gn]) for gn in fx },
            Salience(sal),
            Certainty(apl),
            Certainty(acl)
          )
        )

      options.append(Option(opn, outcomes))

    return Choice(cn, options)
