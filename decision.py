"""
decision.py

Code for representing decisions including predicting decisions based on a
player model and assessing goals based on decision information.
"""

import random

class DecisionMethod:
  """
  Decision modes reflect general strategies for making decisions based on
  modes of engagement and prospective impressions.
  """
  def __init__(self, name_or_other="abstract"):
    if isinstance(name_or_other, DecisionMethod):
      self.name = name_or_other.name
    else:
      self.name = name

  def decide(self, choice, decision_model):
    """
    Overridden by subclasses to implement decision logic.

    This method takes as input a choice and a decision model, which can be
    constructed using ModeOfEngagement.build_decision_model (see
    engagement.py).
    """
    raise NotImplementedError(
      "Use one of the DecisionMethod subclasses to make decisions, not "
      "DecisionMethod itself!"
    )

@super_class_property()
class Maximizing(DecisionMethod):
  """
  Using a maximizing decision method, options are compared in an attempt to
  find one that's better than all of the rest. Lack of information and/or
  tradeoffs can cause this attempt to fail, in which case resolution proceeds
  arbitrarily.
  """
  def __init__(self):
    super().__init__(self, "maximizing")

  def decide(self, choice, decision_model):
    """
    Computes pairwise rationales for picking each option over others and
    randomly picks from dominating options.
    """
    # TODO: HERE

@super_class_property()
class Satisficing(DecisionMethod):
  """
  Using a satisficing decision method, options are inspected to find one that
  achieves some kind of positive outcome, or failing that, a least-negative
  outcome. Barring large differences, positive outcomes are all considered
  acceptable, and an arbitrary decision is made between acceptable options.
  """
  def __init__(self):
    super().__init__(self, "satisficing")

  def decide(self, choice, decision_model):
    """
    Computes risks for each option and picks randomly from options that fall
    into a fuzzy best or least-bad group.
    """
    # TODO: HERE

@super_class_property()
class Utilizing(DecisionMethod):
  """
  Using a utilizing decision method, utilities are computed for each option by
  multiplying probabilities and valences and summing across different outcomes
  according to goal priorities. The option with the highest utility is chosen,
  or one is selected randomly if there are multiple.
  """
  def __init__(self):
    super().__init__(self, "utilizing")

  def decide(self, choice, decision_model):
    """
    Computes utilities for each option at a choice and returns 
    """
    return random.choice(list(choice.options.keys()))

@super_class_property()
class Randomizing(DecisionMethod):
  """
  Using a randomizing decision method, options are selected completely at
  random.
  """
  def __init__(self):
    super().__init__(self, "utilizing")

  def decide(self, choice, decision_model):
    """
    Selects a random option at the given choice and returns its name, ignoring
    the given decision model.
    """
    return random.choice(list(choice.options.keys()))

class Decision:
  """
  A decision is the act of picking an option at a choice, after which one
  experiences an outcome. Note that the handling of extended/hidden/uncertain
  outcomes is not yet implemented.

  Decisions have information on both a player's prospective impressions of the
  choice in question and their retrospective impressions of the option they
  chose.

  When a decision is created, it doesn't yet specify outcomes (although the
  option that it is a decision for includes outcomes that have probabilities).
  The "roll_outcomes" method can be used to automatically sample a set of
  outcomes for an option.
  """
  def __init__(
    self,
    choice,
    option,
    outcomes=None
  ):
    """
    choice:
      The choice that this object focuses on.
    option:
      The option the choosing of which this Decision represents.
    outcomes:
      A collection of Outcome objects; leave out to create a pre-outcome
      decision. The special string "generate" can be used to automatically
      generate outcomes; it just has the effect of calling roll_outcomes.
    """
    self.choice = choice
    self.option = option
    if isinstance(self.option, str):
      self.option = self.choice.options[self.option] # look up within choice
    self.outcomes = outcomes or {}
    if self.outcomes == "generate":
      self.roll_outcomes()
    elif not isinstance(self.outcomes, dict):
      check_names(
        self.outcomes,
        "Two outcomes named '{{}}' cannot coexist within a Decision."
      )
      self.outcomes = {
        o.name: o
          for o in self.outcomes
      }

  def roll_outcomes(self):
    """
    Uses the actual_likelihood information from the Outcome objects included in
    this decision's Option to sample a set of Outcomes and assigns those to
    self.outcomes.
    """
    self.outcomes = self.option.sample_outcomes()
