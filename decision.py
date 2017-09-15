"""
decision.py

Code for representing decisions including predicting decisions based on a
player model and assessing goals based on decision information.
"""

import random

import utils

import perception
import choice

class DecisionMethod:
  """
  Decision modes reflect general strategies for making decisions based on
  modes of engagement and prospective impressions.
  """
  def __init__(self, name_or_other="abstract"):
    if isinstance(name_or_other, DecisionMethod):
      self.name = name_or_other.name
    else:
      self.name = name_or_other

  def decide(self, decision):
    """
    Overridden by subclasses to implement decision logic.

    This method takes as input a Decision object which should have
    prospective_impressions and goal_saliences defined (see
    Decision.add_prospective_impressions). Missing goal saliences will be
    treated as ones.

    See also:
      Decision.add_prospective_impressions
      ModeOfEngagement.build_decision_model (engagement.py)
      PriorityMethod.factor_decision_model (engagement.py)
    """
    raise NotImplementedError(
      "Use one of the DecisionMethod subclasses to make decisions, not "
      "DecisionMethod itself!"
    )

@utils.super_class_property()
class Maximizing(DecisionMethod):
  """
  Using a maximizing decision method, options are compared in an attempt to
  find one that's better than all of the rest. Lack of information and/or
  tradeoffs can cause this attempt to fail, in which case resolution proceeds
  arbitrarily.
  """
  def __init__(self):
    super().__init__("maximizing")

  def decide(self, decision):
    """
    See DecisionMethod.decide.

    Computes pairwise rationales for picking each option over others and
    randomly picks from dominating options.
    """
    if not decision.prospective_impressions:
      raise ValueError(
        "Can't make a decision until prospective impressions have been added."
      )

    decision_model = decision.prospective_impressions
    goal_saliences = decision.goal_saliences
    # TODO: Implement this!
    pass

@utils.super_class_property()
class Satisficing(DecisionMethod):
  """
  Using a satisficing decision method, options are inspected to find one that
  achieves some kind of positive outcome, or failing that, a least-negative
  outcome. Barring large differences, positive outcomes are all considered
  acceptable, and an arbitrary decision is made between acceptable options.
  """
  def __init__(self):
    super().__init__("satisficing")

  def decide(self, decision):
    """
    See DecisionMethod.decide.

    Computes risks for each option and picks randomly from options that fall
    into a fuzzy best or least-bad group.
    """
    if not decision.prospective_impressions:
      raise ValueError(
        "Can't make a decision until prospective impressions have been added."
      )
    decision_model = decision.prospective_impressions
    goal_saliences = decision.goal_saliences
    # TODO: Implement this!
    pass

@utils.super_class_property()
class Utilizing(DecisionMethod):
  """
  Using a utilizing decision method, utilities are computed for each option by
  multiplying probabilities and valences and summing across different outcomes
  according to goal priorities. The option with the highest utility is chosen,
  or one is selected randomly if there are multiple.

  Note: this is a bullshit decision method which is numerically convenient but
  not at all accurate.
  """
  def __init__(self):
    super().__init__("utilizing")

  def decide(self, decision):
    """
    See DecisionMethod.decide.

    Computes utilities for each option at a choice and returns a random option
    from those tied for highest perceived utility.
    """
    if not decision.prospective_impressions:
      raise ValueError(
        "Can't make a decision until prospective impressions have been added."
      )

    decision_model = decision.prospective_impressions
    goal_saliences = decision.goal_saliences

    utilities = {}
    for opt in decision_model:
      utilities[opt] = 0
      for goal in decision_model[opt]:
        for pri in decision_model[opt][goal]:
          utilities[opt] += pri.utility() * (
            goal_saliences[goal]
              if goal in goal_saliences
              else 1
          )

    best_utility = sorted(list(utilities.values()))[-1]
    best = [ opt for opt in utilities if utilities[opt] == best_utility ]

    return random.choice(best)

@utils.super_class_property()
class Randomizing(DecisionMethod):
  """
  Using a randomizing decision method, options are selected completely at
  random.
  """
  def __init__(self):
    super().__init__("randomizing")

  def decide(self, decision):
    """
    See DecisionMethod.decide.

    Selects a random option at the given choice, ignoring information about
    perception of the choice.

    This is just a baseline model.
    """
    return random.choice(list(decision.choice.options.keys()))


class Decision:
  """
  A decision is the act of picking an option at a choice, after which one
  experiences an outcome. Note that the handling of extended/hidden/uncertain
  outcomes is not yet implemented.

  Decisions have information on both a player's prospective impressions of the
  choice in question (as a decision model plus goal saliences) and their
  retrospective impressions of the option they chose (as a mapping from goal
  names to Retrospective percepts).

  When a decision is created, it doesn't yet specify outcomes or retrospective
  impressions (although the option that it is a decision for includes outcomes
  that have probabilities). The "roll_outcomes" method can be used to
  automatically sample a set of outcomes for an option.
  """
  def __init__(
    self,
    choice,
    option=None,
    outcomes=None
  ):
    """
    choice:
      The choice that this object focuses on.
    option:
      The option the choosing of which this Decision represents. May be left
      blank at first.
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
      utils.check_names(
        self.outcomes,
        "Two outcomes named '{{}}' cannot coexist within a Decision."
      )
      self.outcomes = {
        o.name: o
          for o in self.outcomes
      }

    self.prospective_impressions = None
    self.goal_saliences = None
    self.retrospective_impressions = None
    self.simplified_retrospectives = None

  def select_option(self, selection):
    """
    Selects a particular option at this choice, either via a string key or the
    object itself.
    """
    if isinstance(selection, str):
      self.option = self.choice.options[selection]
    elif isinstance(selection, choice.Option):
      if selection not in self.choice.options.values():
        raise ValueError(
          "Can't select option {} which isn't part of choice {}.".format(
            selection,
            self.choice
          )
        )
      self.option = self.choice.options[selection]
    else:
      raise TypeError(
        "Can't select invalid option value {} of type {}.".format(
          selection,
          type(selection)
        )
      )

  def roll_outcomes(self):
    """
    Uses the actual_likelihood information from the Outcome objects included in
    this decision's Option to sample a set of Outcomes and assigns those to
    self.outcomes.
    """
    if not self.option:
      raise RuntimeError(
        "Can't roll outcomes for a decision before knowing which option was "
        "selected."
      )
    self.outcomes = self.option.sample_outcomes()

  def add_prospective_impressions(self, priority_method, mode_of_engagement):
    """
    Adds prospective impressions 
    """
    if self.prospective_impressions != None or self.goal_saliences != None:
      raise RuntimeError(
        "Attempted to add prospective impressions to a decision which already "
        "has them."
      )

    self.prospective_impressions = mode_of_engagement.build_decision_model(
      self.choice
    )

    fdms, self.goal_saliences = priority_method.factor_decision_model(
      self.decision_model
    )

  def add_retrospective_impressions(self):
    """
    Adds retrospective impressions based on the prospective impressions and
    actual outcomes. Calls roll_outcomes if necessary.
    """
    if (
      self.retrospective_impressions != None
   or self.simplified_retrospectives != None
    ):
      raise RuntimeError(
        "Attempted to add retrospective impressions to a decision which "
        "already had them."
      )

    self.retrospective_impressions = {}

    if not self.outcomes:
      self.roll_outcomes()

    chosen_prospectives = self.prospective_impressions[self.option]

    # for each goal in prospective impressions for the chosen option
    for goal in chosen_prospectives:
      self.retrospective_impressions[goal] = []

      # for each prospective impression of that goal
      for pri in chosen_prospectives[goal]:

        # sort through actual outcomes to find effects on that goal
        for on in self.outcomes:
          out = self.outcomes[on]
          if goal in out.goal_effects:
            # add a retrospective impression for each prospective/outcome pair
            val = out.goal_effects[goal]
            self.retrospective_impressions[goal].append(
              perception.Retrospective(
                prospective=pri,
                salience=1.0, # TODO: retrospective saliences would hook in here
                valence=val
              )
            )

    # Also create bundled simplified retrospective impressions
    self.simplified_retrospectives = {}
    for goal in self.retrospective_impressions:
      ilist = self.retrospective_impressions[goal]
      self.simplified_retrospectives[goal] = \
        perception.Retrospective.merge_retrospective_impressions(ilist)
