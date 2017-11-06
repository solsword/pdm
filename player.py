"""
player.py

PlayerModel code.
"""

import copy

import utils

import engagement
import perception
import decision

from packable import pack, unpack
from diffable import diff

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
    priority_method=engagement.PriorityMethod.softpriority,
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
      must still be included in a constituent mode of engagement, though, and
      mode rankings take priorities over goal overrides. So if you have a goal
      with override priority 1, it will still be lower priority than all goals
      from modes of engagement which don't include it that are ranked higher in
      the mode ranking.
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

    self.mode_ranking = copy.deepcopy(mode_ranking) or {
      m: engagement.DEFAULT_PRIORITY
        for m in all_mode_names
    }
    utils.conform_keys(
      all_mode_names,
      self.mode_ranking,
      engagement.DEFAULT_PRIORITY,
      "Ranking for mode '{}' discarded (no matching mode)."
    )

    self.mode_adjustments = copy.deepcopy(mode_adjustments) or {
      m: 0 for m in all_mode_names
    }
    utils.conform_keys(
      all_mode_names,
      self.mode_adjustments,
      0,
      "Adjustment for mode '{}' discarded (no matching mode)."
    )

    all_goal_names = set()
    for k in all_mode_names:
      all_goal_names.update(self.modes[k].goals.keys())

    self.goal_adjustments = copy.deepcopy(goal_adjustments) or {
      g: 0 for g in all_goal_names
    }
    utils.conform_keys(
      all_goal_names,
      self.goal_adjustments,
      0,
      "Adjustment for goal '{}' discarded (no matching goal in any mode)."
    )

    self.goal_overrides = copy.deepcopy(goal_overrides) or {}
    utils.conform_keys(
      all_goal_names,
      self.goal_overrides,
      utils.NoDefault,
      "Override for goal '{}' discarded (no matching goal in any mode)."
    )

    self._synthesize_moe()

  def __str__(self):
    # TODO: Different here?
    return "PlayerModel('{}')".format(self.name)

  def __eq__(self, other):
    if type(other) != PlayerModel:
      return False
    if self.name != other.name:
      return False
    if self.decision_method != other.decision_method:
      return False
    if self.modes != other.modes:
      return False
    if self.priority_method != other.priority_method:
      return False
    if self.mode_ranking != other.mode_ranking:
      return False
    if self.mode_adjustments != other.mode_adjustments:
      return False
    if self.goal_adjustments != other.goal_adjustments:
      return False
    if self.goal_overrides != other.goal_overrides:
      return False
    return True

  def __hash__(self):
    result = hash(self.name) + hash(self.decision_method)
    for moe in self.modes.keys():
      result ^= hash(moe)
    result += hash(self.priority_method)
    for mn in self.mode_ranking:
      result ^= (self.mode_ranking[mn] + 17) * hash(mn)
    for mn in self.mode_adjustments:
      result ^= (self.mode_adjustments[mn] + 4039493) * hash(mn)
    for gn in self.goal_adjustments:
      result ^= (self.goal_adjustments[gn] + 6578946) * hash(gn)
    for gn in self.goal_overrides:
      result ^= (self.goal_overrides[gn] + 795416) * hash(gn)
    return result

  def _diff_(self, other):
    """
    Reports differences (see diffable.py).
    """
    result = []
    if self.name != other.name:
      result.append("names: '{}' != '{}'".format(self.name, other.name))
    result.extend([
      "decision_methods: {}".format(d)
        for d in diff(self.decision_method, other.decision_method)
    ])
    result.extend([
      "modes: {}".format(d)
        for d in diff(self.modes, other.modes)
    ])
    result.extend([
      "priority_methods: {}".format(d)
        for d in diff(self.priority_method, other.priority_method)
    ])
    result.extend([
      "mode_rankings: {}".format(d)
        for d in diff(self.mode_ranking, other.mode_ranking)
    ])
    result.extend([
      "mode_adjustments: {}".format(d)
        for d in diff(self.mode_adjustments, other.mode_adjustments)
    ])
    result.extend([
      "goal_adjustments: {}".format(d)
        for d in diff(self.goal_adjustments, other.goal_adjustments)
    ])
    result.extend([
      "goal_overrides: {}".format(d)
        for d in diff(self.goal_overrides, other.goal_overrides)
    ])
    return result

  def _pack_(self):
    """
    Returns a simple representation of this option suitable for direct
    conversion to JSON.

    Example:
      (Note that this example's use of mode/goal rankings/adjustments is a bit
      silly as the mode rankings are enough to affectively achieve the desired
      priorities alone.)

    ```
    PlayerModel(
      "aggressive",
      DecisionMethod.utilizing,
      {
        "defensive": ModeOfEngagement(
          "defensive",
          [ "attack", "defend" ],
          { "attack": 3, "defend": 2 }
        ),
        "aggressive": ModeOfEngagement(
          "aggressive",
          [ "attack", "defend" ],
          { "attack": 2, "defend": 3 }
        )
      },
      SoftPriority(0.6),
      mode_ranking={ "defensive": 2, "aggressive": 1 },
      mode_adjustments={ "defensive": 1 },
      goal_adjustments={ "defend": 1 },
      goal_overrides={ "attack": 1 }
    )
    ```
    {
      "name": "aggressive",
      "decision_method": "utilizing",
      "modes": {
        "defensive": {
          "name": "defensive",
          "goals": [
            { "name": "attack", "type": "PlayerGoal" },
            { "name": "defend", "type": "PlayerGoal" }
          ],
          "priorities": { "attack": 3, "defend": 2 }
        },
        "aggressive": {
          "name": "aggressive",
          "goals": [
            { "name": "attack", "type": "PlayerGoal" },
            { "name": "defend", "type": "PlayerGoal" }
          ],
          "priorities": { "attack": 2, "defend": 3 }
        }
      },
      "priority_method": [ "softpriority", 0.6 ],
      "mode_ranking": { "defensive": 2, "aggressive": 1 },
      "mode_adjustments": { "defensive": 1 },
      "goal_adjustments": { "defend": 1 },
      "goal_overrides": { "attack": 1 }
    }
    ```
    """
    result = {
      "name": self.name,
      "decision_method": pack(self.decision_method),
      "modes": { key: pack(val) for (key, val) in self.modes.items() }
    }
    if self.priority_method != engagement.PriorityMethod.softpriority:
      result["priority_method"] = pack(self.priority_method)

    nondefault_mode_rankings = {
      mn: self.mode_ranking[mn]
        for mn in self.mode_ranking
        if self.mode_ranking[mn] != engagement.DEFAULT_PRIORITY
    }
    if nondefault_mode_rankings:
      result["mode_ranking"] = nondefault_mode_rankings

    nonzero_adjustments = {
      mn: self.mode_adjustments[mn]
        for mn in self.mode_adjustments
        if self.mode_adjustments[mn] != 0
    }
    if nonzero_adjustments:
      result["mode_adjustments"] = nonzero_adjustments

    nonzero_adjustments = {
      gn: self.goal_adjustments[gn]
        for gn in self.goal_adjustments
        if self.goal_adjustments[gn] != 0
    }
    if nonzero_adjustments:
      result["goal_adjustments"] = nonzero_adjustments

    if self.goal_overrides:
      result["goal_overrides"] = self.goal_overrides

    return result

  def _unpack_(obj):
    """
    The inverse of `_pack_`; constructs an instance from a simple object (e.g.,
    one produced by json.loads).
    """
    return PlayerModel(
      obj["name"],
      unpack(obj["decision_method"], decision.DecisionMethod),
      {
        key: unpack(val, engagement.ModeOfEngagement)
          for (key, val) in obj["modes"].items()
      },
      unpack(obj["priority_method"], engagement.PriorityMethod) \
        if "priority_method" in obj else engagement.PriorityMethod.softpriority,
      mode_ranking=obj["mode_ranking"] if "mode_ranking" in obj else None,
      mode_adjustments=obj["mode_adjustments"] \
        if "mode_adjustments" in obj else None,
      goal_adjustments=obj["goal_adjustments"] \
        if "goal_adjustments" in obj else None,
      goal_overrides = obj["goal_overrides"] \
        if "goal_overrides" in obj else None
    )

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
        mg = self.modes[mn].goals
        madj = self.mode_adjustments[mn]
        for gn in mg:
          if gn in self.goal_overrides:
            adjp = self.goal_overrides[gn]
          else:
            adjp = (
              current_base_prioity
            + self.modes[mn].get_priority(gn)
            + madj
            + self.goal_adjustments[gn]
            )

          if gn in self._synthesized_mode_of_engagement.goals:
            if adjp < self._synthesized_mode_of_engagement.get_priority(gn):
              self._synthesized_mode_of_engagement.set_priority(gn, adjp)
            # else do nothing
          else:
            self._synthesized_mode_of_engagement.add_goal(mg[gn], adjp)

          if max_priority_so_far == None or max_priority_so_far < adjp:
            max_priority_so_far = adjp

      # adjust base priority and continue to the next rank
      current_base_prioity = max_priority_so_far + 1

  def make_decision(self, choice):
    """
    Given a choice, creates a Decision object by building a decision model
    using an updated-if-necessary full mode of engagement and then deciding on
    an option using this player's DecisionMethod. Rolls outcomes and adds
    retrospective impressions to the created decision as well.
    """
    # TODO: Some way to model cognitive dissonance + regret when a reveal
    # changes goals and/or brings new facts to light about an old decision?
    self._synthesize_moe()
    dec = decision.Decision(choice)
    dec.add_prospective_impressions(
      self.priority_method,
      self._synthesized_mode_of_engagement
    )
    selection = self.decision_method.decide(dec)
    dec.select_option(selection)
    dec.roll_outcomes()
    dec.add_retrospective_impressions()

    return decision

  def assess_decision(self, choice, option):
    """
    Takes a Choice and an option at that choice, and assesses how consistent
    that decision is with this player model from a prospective standpoint,
    returning a number between 0 (completely inconsistent) and 1 (perfectly
    consistent).
    """
    self._synthesize_moe()
    dec = decision.Decision(choice)
    dec.add_prospective_impressions(
      self.priority_method,
      self._synthesized_mode_of_engagement
    )
    dec.select_option(option)
    return self.decision_method.consistency(dec)
