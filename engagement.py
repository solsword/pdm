"""
engagement.py

Models for modes of engagement. For now a mode of engagement is just defined as
a collection of goals, with priorities for each.

Although goal priorities can be treated as a strict hierarchy, they can also be
blended using a "relative importance factor" which determines the relative
value of goals of different priorities. For example, with a RIF of 2/3, a goal
with priority 5 would be evaluated as 2/3 as impactful as a goal with priority
4, and that goal as 2/3 as impactful as a goal with priority 3, and so on.

Globals:

DEFAULT_PRIORITY:
  The default priority for goals whose priority is not specified.
"""

import utils

import perception

DEFAULT_PRIORITY = 5

class PriorityMode:
  """
  Types for specifying how priorities should be handled.
  """
  pass

@super_class_property()
class Soft(PriorityMode):
  """
  In Soft mode, priorities represent relative importance, with each integer
  difference in priority representing being 'falloff' less important.
  """
  def __init__(self, falloff=2/3):
    self.falloff = falloff

@super_class_property()
class Hard(PriorityMode):
  """
  In Hard mode, priorities represent absolute precedence, so decisions are
  made at the highest available priority level (lowest priority value) and
  lower levels are only considered in order to break ties.
  """
  pass

class ModeOfEngagement:
  def __init__(self, name, goals=None, priorities=None):
    """
    name:
      The name for this mode of engagement.

    goals:
      A list of PlayerGoal objects. If left unspecified, it will default to an
      empty list.

    priorities:
      A dictionary mapping goal names to priority integers (smaller integers
      representing higher priorities). Any unmapped goals are given the
      DEFAULT_PRIORITY, and any spurious priorities which don't match the name
      of a given goal are removed with a warning.
    """
    self.name = name
    self.goals = { g.name: g for g in goals } if goals else {}
    self.priorities = priorities or {}
    utils.conform_keys(
      self.goals.keys(),
      self.priorities,
      DEFAULT_PRIORITY,
      (
        "ModeOfEngagement '{}' constructed with priority for goal '{}', "
        "but that goal is not one of the goals given."
      ).format(self.name)
    )

    for tr in toremove:
      del self.priorities[tr]

  def get_goals(self):
    """
    Returns dictionary mapping goal names to goals. The return value is not a
    copy, and shouldn't be modified.
    """
    return self.goals

  def add_goal(self, goal, priority=DEFAULT_PRIORITY):
    """
    Adds the given goal with the given priority. Raises a ValueError if a goal
    with the given goal's name already exists.
    """
    if goal.name in self.goals:
      raise ValueError(
        (
          "Can't add goal named '{}' to mode '{}' because a goal with that name"
          " is already part of that mode."
        ).format(goal.name, self.name)
      )
    self.goals[goal.name]
    self.priorities[goal.name] = priority

  def remove_goal(self, goal_name):
    """
    Removes the given goal (by name). Raises a KeyError if there is no such
    goal. If there are multiple goals with that name
    """
    if goal_name not in self.goals:
      raise KeyError(
        "Attempted to remove goal '{}' which isn't part of mode '{}'.".format(
          goal_name,
          self.name
        )
      )
    del self.goals[goal_name]
    del self.priorities[goal_name]

  def get_priority(self, goal_name):
    """
    Returns the current priority of the goal with the given name. Raises a
    KeyError if there is no such goal.
    """
    if goal_name in self.priorities:
      return self.priorities[goal_name]
    else:
      raise KeyError(
        (
          "Attempted to get priority of goal '{}' which is not included in "
          "mode '{}'."
        ).format(
          goal_name,
          self.name
        )
      )

  def set_priority(self, goal_name, priority):
    """
    Sets the priority for the goal with the given name. Raises a KeyError if no
    goal by that name exists within this mode of engagement. Returns the old
    priority for that goal.
    """
    if goal_name in self.priorities:
      old = self.priorities[goal_name]
      self.priorities[goal_name] = priority
      return old
    else:
      raise KeyError(
        (
          "Attempted to set priority of goal '{}' which is not included in "
          "mode '{}'."
        ).format(
          goal_name,
          self.name
        )
      )

  def build_prospective_option_model(self, choice, option):
    """
    Builds a mapping from goal names to lists of prospective Percepts for the
    given Option (at the given choice) based on its outcomes and the goals
    represented in this mode of engagement.
    """
    result = {}
    for o in option.outcomes:
      out = option.outcomes[o]
      if out.visibility * out.apparent_likelihood > 0: # otherwise ignore
        for g in out.goal_effects:
          if g in self.goals:

            # add a result entry if necessary
            if g not in result:
              result[g] = []

            # add the appropriate percept
            result[g].append(
              perception.Prospective(
                goal=g,
                choice=choice,
                option=option,
                valence=out.goal_effects[g],
                certainty=out.apparent_likelihood * out.visibility,
              )
            )
          # otherwise ignore this effect as this mode of engagement doesn't
          # care about that goal.
      # otherwise ignore this outcome as its either zero-likelihood or
      # zero-visibility. Note the difference between Inconceivable and
      # Impossible, and don't use Impossible unless really warranted!

    return result

  def build_decision_model(self, choice):
    """
    Builds a decision model for the given choice based on the goals and
    priorities specified in this mode of engagement. A decision model maps from
    option names to maps from goal names to prospective impression lists, and
    is based on the visibility, certainty, and apparent likelihood of outcomes
    plus the valences of their goal effects.
    """
    result = {}
    for o in choice.options:
      result[o] = self.build_prospective_option_model(choice, choice.options[o])

    return result
