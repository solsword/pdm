"""
player.py

PlayerModel code.
"""

import utils

import engagement
import perception
import decision

class PlayerModel:
  """
  Models a player as having a DecisionMethod, a PriorityMethod, and a
  collection of modes of engagement, each of which includes multiple goals at
  different priorities. The player may have a strict ranking of these different
  modes, or may have per-mode priority modifiers, or may even have per-goal
  priority modifiers or overrides. At any point a player-specific combined mode
  of engagement can be constructed which assigns global priorities to all
  player goals.
  
  Note that priorities for specific goals are endemic to a player model and
  cannot be compared between player models because of arbitrary numbering
  concerns. Priority differences likewise cannot be compared, but priority
  *orderings* can be.

  For the purposes of soft goal priorities, mode ranking stacks goal priorities
  of a lower-priority mode immediately after priorities from a higher-priority
  mode. For best results, avoid combining mode ranking with soft goal
  priorities, and use mode adjustments instead to achieve a precise goal
  priority setup.

  Also note that if modes of engagement define goals with negative priorities
  (they shouldn't) these may break the strict mode-of-engagement hierarchy
  defined here.
  """
  def __init__(
    self,
    name,
    decision_method,
    modes_of_engagement,
    priority_method=engagement.PriorityMethod.soft,
    mode_ranking=None,
    mode_adjustments=None,
    goal_adjustments=None,
    goal_overrides=None
  ):
    """
    Note: Invalid mode/goal names in the following arguments will be pruned and
    generate warnings.

    name:
      The name for this player model.

    decision_method:
      A DecisionMethod object (see decision.py) representing how this player
      makes decisions. Can be updated with set_decision_method.

    modes_of_engagement:
      A dictionary mapping names to ModeOfEngagement objects (see
      engagement.py) that this player will use.

    priority_method:
      A PriorityMethod object (see engagement.py) representing how this player
      prioritizes goals. Can be updated using set_priority_method.

    mode_ranking:
      A strict ranking allowing some modes absolute precedence over others.
      Lower numbers represent higher priorities. This should be a dictionary
      mapping mode names to priority numbers. Priorities not given default to
      engagement.DEFAULT_PRIORITY.

    mode_adjustments:
      A mapping from mode names to priority adjustments (positive or negative
      integers) to be applied to all of the goals from a given mode of
      engagement. This allows controlling how modes interact to some degree
      without necessarily establishing a strict hierarchy. Of course only modes
      given equal ranks will have goal priorities that interact. Modes not
      specified in the adjustments mapping will be assigned the default
      adjustment of 0.

    goal_adjustments:
      A mapping from goal names to priority adjustments for individual goals.
      These are applied within-mode before between-mode effects like mode
      ranking happen. Goals with no specified adjustment will be assigned an
      adjustment of 0.

    goal_overrides:
      A mapping from goal names to new priority values for individual goals.
      These are absolute, and will set a goal's priority independent of goal
      priorities derived from modes of engagement. The goal that they refer to
      must still be included in a constituent mode of engagement, though.
    """
    self.name = name

    self.decision_method = decision_method
    if not isinstance(self.decision_method, decision.DecisionMethod):
      raise TypeError("decision_method must be a DecisionMethod.")

    if not isinstance(modes_of_engagement, dict):
      raise TypeError(
        "modes_of_engagement must be dictionary of ModeOfEngagement objects."
      )
    self.modes = dict(modes_of_engagement)
    if not all(
      isinstance(m, engagement.ModeOfEngagement) for m in self.modes.values()
    ):
      raise TypeError(
        "modes_of_engagement must be dictionary of ModeOfEngagement objects."
      )

    self.priority_method = priority_method
    if not isinstance(self.priority_method, engagement.PriorityMethod):
      raise TypeError("priority_method must be a PriorityMethod.")

    all_mode_names = set(self.modes.keys())

    self.mode_ranking = mode_ranking or {
      m: engagement.DEFAULT_PRIORITY
        for m in all_mode_names
    }
    utils.conform_keys(
      all_mode_names,
      self.mode_ranking,
      engagement.DEFAULT_PRIORITY,
      "Ranking for mode '{}' discarded (no matching mode)."
    )

    self.mode_adjustments = mode_adjustments or { m: 0 for m in all_mode_names }
    utils.conform_keys(
      all_mode_names,
      self.mode_adjustments,
      0,
      "Adjustment for mode '{}' discarded (no matching mode)."
    )

    all_goal_names = set()
    for k in all_mode_names:
      all_goal_names.update(self.modes[k].get_goals().keys())

    self.goal_adjustments = goal_adjustments or { g: 0 for g in all_goal_names }
    utils.conform_keys(
      all_goal_names,
      self.goal_adjustments,
      0,
      "Adjustment for goal '{}' discarded (no matching goal in any mode)."
    )

    self.goal_overrides = goal_overrides
    utils.conform_keys(
      all_goal_names,
      self.goal_overrides,
      utils.NoDefault,
      "Override for goal '{}' discarded (no matching goal in any mode)."
    )

    self._synthesize_moe()

  def set_decision_method(self, dm):
    """
    Updates this player's decision method.
    """
    self.decision_method = dm

  def set_priority_method(self, pm):
    """
    Updates this player's priority method.
    """
    self.priority_method = pm

  def combined_mode_of_engagement(self):
    """
    Returns a ModeOfEngagement representing a synthesis of all of the player's
    current modes of engagement with appropriate rankings, adjustments, and
    overrides applied. Note that if multiple modes define goals with the same
    name, the mode which assigns the highest priority (smallest priority
    number) to that goal will dominate.

    The returned mode is used internally and thus shouldn't be modified.
    """
    self._synthesize_moe()
    return self._synthesized_mode_of_engagement

  def _synthesize_moe(self):
    """
    Internal method for updating the current combined mode of engagement.
    """
    # create a new empty mode of engagement:
    self._synthesized_mode_of_engagement = engagement.ModeOfEngagement(
      "{}-synthesized".format(self.name),
    )

    current_base_prioity = 0

    # iterate according to mode ranks:
    mode_ranks = sorted(list(set(self.mode_ranking.values())))
    for mr in mode_ranks:
      modes_here = [
        mn
          for mn in self.mode_ranking
          if self.mode_ranking[mn] == mr
      ]
      max_priority_so_far = None
      # synthesize each mode at this rank:
      for mn in modes_here:
        mg = self.modes[mn].goals()
        madj = self.mode_adjustments[mn]
        for gn in mg:
          adjp = (
            current_base_prioity
          + mn.get_priority(gn)
          + madj
          + self.goal_adjustments[gn]
          )

          if gn in self._synthesized_mode_of_engagement.goals():
            if adjp < self._synthesized_mode_of_engagement.get_priority(gn):
              self._synthesized_mode_of_engagement.set_priority(gn, adjp)
            # else do nothing
          else:
            self._synthesized_mode_of_engagement.add_goal(mg[gn], adjp)

          if max_priority_so_far == None or max_priority_so_far < adjp:
            max_priority_so_far = adjp

      # adjust base priority and continue to the next rank
      current_base_prioity = max_priority_so_far + 1

  def impute_prospective_impressions(self, choice):
    self._synthesize_moe()

  def impute_retrospective_impressions(self, choice):
    """
    TODO: HERE
    """
    pass


  def make_decision(self, choice, outcomes=None):
    """
    Given a choice, creates a Decision object by building a decision model
    using an updated-if-necessary full mode of engagement and then deciding on
    an option using a DecisionMethod.
    """
    self._synthesize_moe()
    decision = decision.Decision(choice)
    decision.add_prospective_impressions(
      self.priority_method,
      self._synthesized_mode_of_engagement
    )
    selection = self.decision_method.decide(decision)
    decision.select_option(selection)
    decision.roll_outcomes()
    decision.add_retrospective_impressions()

    return decision
