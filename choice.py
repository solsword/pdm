"""
choice.py

Code for dealing with choice structures.
"""

class Outcome:
  """
  An outcome models a consequence of an option including visibility to the
  player before making the decision, probability of occurrence once a decision
  is made, and effects on various goals. Outcomes are included in Option
  objects to model choice structures.

  Note: differential outcome visibility can also be modeled through
  manipulating player goals.
  """
  def __init__(
    self,
    name,
    goal_effects,
    visibility,
    apparent_likelihood,
    actual_likelihood=None,
  ):
    """
    name:
      The name for this outcome. Must be unique within an option.

    goal_effects:
      How this outcome affects various goals. Should be a mapping from goal
      names to effects, which should each be one of "awful", "bad", "neutral",
      "good", or "wonderful".

    visibility:
      Whether this outcome is "full"y visible, "partial"ly visible, or
      "invisible" to the player. May also be specified as a number between 0.0
      and 1.0.

    apparent_likelihood:
      Pre-decision likelihood of this outcome as apparent to the player. Should
      be one of "impossible", "unlikely", "even", "likely", or "certain", or
      may be given as a probability between 0.0 and 1.0.

    actual_likelihood:
      Actual likelihood of this outcome based on internal game logic. Uses the
      same values as apparent_likelihood. If not given, defaults to the value
      of apparent_likelihood.
    """
    self.name = name
    self.goal_effects = goal_effects
    self.visibility = visibility
    self.apparent_likelihood = apparent_likelihood
    if actual_likelihood is None:
      self.actual_likelihood = self.apparent_likelihood
    else:
      self.actual_likelihood = actual_likelihood

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
