"""
decision.py

Code for representing decisions including predicting decisions based on a
player model and assessing goals based on decision information.
"""

import random

import utils

from packable import pack, unpack
from diffable import diff

import perception
import choice

from base_types import Certainty, Valence, Salience

class DecisionMethod:
  """
  Decision modes reflect general strategies for making decisions based on
  modes of engagement and prospective impressions.
  """
  def __new__(cls, name_or_other="abstract"):
    result = object.__new__(cls)

    if isinstance(name_or_other, DecisionMethod):
      result.name = name_or_other.name
    else:
      result.name = name_or_other

    return result

  def _diff_(self, other):
    """
    Reports differences (see diffable.py).
    """
    differences = []
    if not isinstance(other, type(self)):
      differences.append(
        "exact types: {} != {}".format(type(self), type(other))
      )
    if self.name != other.name:
      differences.append("names: '{}' != '{}'".format(self.name, other.name))

    return differences

  def __eq__(self, other):
    if not isinstance(other, type(self)):
      return False
    if other.name != self.name:
      return False
    return True

  def __hash__(self):
    return hash(type(self)) + 7 * hash(self.name)

  def _pack_(self):
    """
    Turns this object into a simple object that can be converted to JSON.

    Example:

    ```
    DecisionMethod.maximizing
    ```
    "maximizing"
    ```
    """
    return self.name

  def _unpack_(obj):
    """
    The inverse of `pack`; creates a DecisionMethod from a simple object. This
    method works for all of the various subclasses.
    """
    if isinstance(obj, str) and hasattr(DecisionMethod, obj):
      result = getattr(DecisionMethod, obj)
      if isinstance(result, DecisionMethod):
        return result

    raise ValueError(
      "Attempted to unpack unknown decision method '{}'.".format(obj)
    )

  def decide(self, decision):
    """
    Overridden by subclasses to implement decision logic.

    This method takes as input a Decision object which should have
    prospective_impressions and goal_relevance defined (see
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

  def consistency(self, decision):
    """
    Overridden by subclasses to implement consistency logic.

    Takes a Decision object that's already been decided, and returns a number
    between 0 and 1 indicating how consistent the decision is with this
    decision method.

    The given decision must have an option specified and must include
    prospective impression values.
    """
    raise NotImplementedError(
      "Use one of the DecisionMethod subclasses to test consistency, not "
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
  def __new__(cls):
    return super().__new__(cls, "maximizing")

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
    goal_relevance = decision.goal_relevance
    # TODO: Implement this!
    pass

  def consistency(self, decision):
    """
    See DecisionMethod.consistency.

    Uses the dominance structure of pairwise rationales to compute consistency.
    """
    if not decision.option:
      raise ValueError(
        "Can't compute decision consistency before an option has been selected."
      )

    if not decision.prospective_impressions:
      raise ValueError(
        "Can't compute decision consistency before prospective impressions are "
        "added."
      )
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
  def __new__(cls):
    return super().__new__(cls, "satisficing")

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
    goal_relevance = decision.goal_relevance
    # TODO: Implement this!
    pass

  def consistency(self, decision):
    """
    See DecisionMethod.consistency.

    Uses option risks to evaluate consistency. TODO: More specific here.
    """
    if not decision.option:
      raise ValueError(
        "Can't compute decision consistency before an option has been selected."
      )

    if not decision.prospective_impressions:
      raise ValueError(
        "Can't compute decision consistency before prospective impressions are "
        "added."
      )
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

  Constants:

    value_resolution:
      determines the resolution at which utilities are considered
      indistinguishable (unless one is positive/zero and the other is
      negative/zero).
  """
  value_resolution = 0.09

  def __new__(cls):
    return super().__new__(cls, "utilizing")

  def rank_options(self, decision):
    """
    Ranks the options at the given decision into multiple equivalence classes
    ordered by preference. Returns an ordered list of pairs of (preference-
    value, list-of-option-names). The given decision must include prospective
    impressions.
    """
    if not decision.prospective_impressions:
      raise ValueError(
        "Can't rank options until prospective impressions have been added."
      )

    decision_model = decision.prospective_impressions
    goal_relevance = decision.goal_relevance

    utilities = {}
    for opt in decision_model:
      # TODO: Does this work for options w/out any impressions?
      utilities[opt] = 0
      for goal in decision_model[opt]:
        for pri in decision_model[opt][goal]:
          utilities[opt] += pri.utility() * (
            goal_relevance[goal]
              if goal in goal_relevance
              else 1
          )

    ulevels = reversed(sorted(list(utilities.values())))

    strict = [
      [u, [ gn for (gn, uv) in utilities.items() if uv == u ]]
        for u in ulevels
    ]

    # Merge levels according to value_resolution
    i = 0
    while i < len(strict) - 1:
      u1 = strict[i][0]
      u2 = strict[i+1][0]

      if u1 > 0 and u2 <= 0 or u1 >= 0 and u2 < 0:
        i += 1
        continue

      if u1 - u2 < self.value_resolution:
        u, ol = strict.pop(i)
        strict[i][0] = (u1 + u2) / 2
        strict[i][1].extend(ol)
        continue # without incrementing i
    
      # increment and continue
      i += 1

    return strict

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


    ranked = self.rank_options(decision)
    best = ranked[0][1]

    return random.choice(best)

  def consistency(self, decision):
    """
    See DecisionMethod.consistency.

    Creates a utility scale based on the highest- and lowest-valued options at
    this choice and interpolates according to the utility of the chosen option.
    """
    if not decision.option:
      raise ValueError(
        "Can't compute decision consistency before an option has been selected."
      )

    if not decision.prospective_impressions:
      raise ValueError(
        "Can't compute decision consistency before prospective impressions are "
        "added."
      )

    ranked = self.rank_options(decision)
    best_utility = ranked[0][0]
    worst_utility = ranked[-1][0]
    lower_bound = -0.5 + worst_utility / 2

    chosen_utility = None
    for u, ol in ranked:
      if decision.option.name in ol:
        chosen_utility = u
        break

    if chosen_utility is None:
      raise RuntimeError(
        "Selected option '{}' wasn't found among ranked options!".format(
          decision.option.name
        )
      )

    # TODO: Something else here?
    # TODO: Note that this isn't quite correct, because there should be more
    # tolerance when the utility range is low, but figuring out what the
    # threshold for "low" is is difficult.

    #denom = float(best_utility) - float(worst_utility)
    denom = float(best_utility) - float(lower_bound)
    if denom == 0:
      return 1.0 # all options are the same, so any choice is compatible
    else:
      # TODO: Which of these?!?
      #return (chosen_utility - worst_utility) / (best_utility - worst_utility)
      return (float(chosen_utility) - float(lower_bound)) / denom

@utils.super_class_property()
class Randomizing(DecisionMethod):
  """
  Using a randomizing decision method, options are selected completely at
  random.
  """
  def __new__(cls):
    return super().__new__(cls, "randomizing")

  def decide(self, decision):
    """
    See DecisionMethod.decide.

    Selects a random option at the given choice, ignoring information about
    perception of the choice.

    This is just a baseline model.
    """
    return random.choice(list(decision.choice.options.keys()))

  def consistency(self, decision):
    """
    See DecisionMethod.consistency.

    Always returns 1, because every option is equally consistent with random
    decision making.
    """
    if not decision.option:
      raise ValueError(
        "Can't compute decision consistency before an option has been selected."
      )

    if not decision.prospective_impressions:
      raise ValueError(
        "Can't compute decision consistency before prospective impressions are "
        "added."
      )

    return 1.0


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
    outcomes=None,
    prospective_impressions=None,
    factored_decision_models=None,
    goal_relevance=None,
    retrospective_impressions=None
  ):
    """
    choice:
      The choice that this object focuses on.
    option:
      The option the choosing of which this Decision represents. May be left
      blank at first by passing in None.
    outcomes:
      A collection of Outcome objects; leave out to create a pre-outcome
      decision. The special string "generate" can be used to automatically
      generate outcomes; it just has the effect of calling roll_outcomes. Note
      that "generate" may not be given when no option is specified (doing so
      will result in a RuntimeError).
    prospective_impressions:
      A mapping from option names to mappings from goal names to prospective
      impression lists, as returned by ModeOfEngagement.build_decision_model.
      Can be created automatically along with the factored_decision_models and
      goal_relevance properties if given as None using the
      add_prospective_impressions method.
    factored_decision_models:
      This is just a list of one or more prospective impressions structures
      (maps from option names to maps from goal names to impression lists).
      The models are arranged such that the first model can be used to make
      decisions, falling back to successive models in the case of a tie at an
      upper level. Normally, this is given as None and assigned when
      add_prospective_impressions is called.
    goal_relevance:
      A mapping from goal names to Salience values. This expresses the relative
      importance of various goals at the moment of the decision, and is usually
      given as None and assigned when add_prospective_impressions is called.
    retrospective_impressions:
      A mapping from goal names to lists of Retrospective impression objects.
      Normally given as None and then assigned using the
      add_retrospective_impressions method. Note that each goal may have
      multiple associated impressions based on the various outcomes that
      occurred. This only makes sense if the option for this Decision has been
      chosen and outcomes have been rolled (see roll_outcomes).
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

    self.prospective_impressions = prospective_impressions
    self.factored_decision_models = factored_decision_models
    self.goal_relevance = goal_relevance
    self.retrospective_impressions = retrospective_impressions
    if retrospective_impressions:
      self.add_simplified_retrospectives()
    else:
      self.simplified_retrospectives = None

  def __str__(self):
    # TODO: Better here
    return str(pack(self))

  def _diff_(self, other):
    """
    Reports differences (see diffable.py).
    """
    return [
      "choices: {}".format(d)
        for d in diff(self.choice, other.choice)
    ] + [
      "options: {}".format(d)
        for d in diff(self.option, other.option)
    ] + [
      "outcomes: {}".format(d)
        for d in diff(self.outcomes, other.outcomes)
    ] + [
      "prospectives: {}".format(d)
        for d in diff(
          self.prospective_impressions,
          other.prospective_impressions
        )
    ] + [
      "factored decision models: {}".format(d)
        for d in diff(
          self.factored_decision_models,
          other.factored_decision_models
        )
    ] + [
      "goal relevance: {}".format(d)
        for d in diff(self.goal_relevance, other.goal_relevance)
    ] + [
      "retrospectives: {}".format(d)
        for d in diff(
          self.retrospective_impressions,
          other.retrospective_impressions
        )
    ] + [
      "simplified retrospectives: {}".format(d)
        for d in diff(
          self.simplified_retrospectives,
          other.simplified_retrospectives
        )
    ]

  def __eq__(self, other):
    if not isinstance(other, Decision):
      return False
    if other.choice != self.choice:
      return False
    if other.option != self.option:
      return False
    if other.outcomes != self.outcomes:
      return False
    if other.prospective_impressions != self.prospective_impressions:
      return False
    if other.factored_decision_models != self.factored_decision_models:
      return False
    if other.goal_relevance != self.goal_relevance:
      return False
    if other.retrospective_impressions != self.retrospective_impressions:
      return False
    if other.simplified_retrospectives != self.simplified_retrospectives:
      return False
    return True

  def __hash__(self):
    h = hash(self.choice)
    h ^= hash(self.option)
    for on in self.outcomes:
      h ^= 583948 + hash(self.outcomes[on])

    if self.prospective_impressions:
      for on in self.prospective_impressions:
        option_impressions = self.prospective_impressions[on]
        oh = hash(on)
        for gn in option_impressions:
          h ^= 874387 + hash(tuple(option_impressions[gn])) + oh

    if self.factored_decision_models:
      for dm in self.factored_decision_models:
        for on in dm:
          option_impressions = dm[on]
          oh = hash(on)
          for gn in option_impressions:
            h ^= 231893 + hash(tuple(option_impressions[gn])) + oh

    if self.goal_relevance:
      for gn in self.goal_relevance:
        h ^= 3321564 + hash(gn) + hash(self.goal_relevance[gn])

    if self.retrospective_impressions:
      for gn in self.retrospective_impressions:
        h ^= 67894 + hash(gn) + hash(tuple(self.retrospective_impressions[gn]))

    if self.simplified_retrospectives:
      for gn in self.simplified_retrospectives:
        h ^= 848846 + hash(gn) + hash(self.simplified_retrospectives[gn])

    return h

  def _pack_(self):
    """
    Packs this Decision into a simple object representation which can be
    converted to JSON.

    Example:

    ```
    Decision(
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
      ),
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
      [
        Outcome(
          "appreciates_kindness",
          { "befriend_dragon": "good" },
          "explicit",
          "likely",
        )
      ],
      prospective_impressions=None,
      factored_decision_models=None,
      goal_relevance=None,
      retrospective_impressions=None
    )
    ```
    {
      "choice": {
        "name": "Rescue the baby dragon or not?",
        "options": {
          "leave_it": {
            "name": "leave_it",
            "outcomes": [
              {
                "actual_likelihood": "even",
                "apparent_likelihood": "unlikely",
                "effects": {
                  "befriend_dragon": "awful",
                  "kill_dragon": "great"
                },
                "name": "dies",
                "salience": "hinted"
              },
              {
                "apparent_likelihood": 0.97,
                "effects": {
                  "befriend_dragon": "bad"
                },
                "name": "dislikes_abandonment",
                "salience": "explicit"
              },
            ]
          },
          "rescue_it": {
            "name": "rescue_it",
            "outcomes": [
              {
                "apparent_likelihood": "likely",
                "effects": {
                  "befriend_dragon": "good"
                },
                "name": "appreciates_kindness",
                "salience": "explicit"
              },
              {
                "apparent_likelihood": "even",
                "effects": {
                  "befriend_dragon": "unsatisfactory",
                  "health_and_safety": "unsatisfactory"
                },
                "name": "bites_your_hand",
                "salience": "implicit"
              }
            ]
          }
        }
      },
      "option": {
        "name": "rescue_it",
        "outcomes": [
          {
            "apparent_likelihood": "likely",
            "effects": {
              "befriend_dragon": "good"
            },
            "name": "appreciates_kindness",
            "salience": "explicit"
          },
          {
            "apparent_likelihood": "even",
            "effects": {
              "befriend_dragon": "unsatisfactory",
              "health_and_safety": "unsatisfactory"
            },
            "name": "bites_your_hand",
            "salience": "implicit"
          }
        ]
      },
      "outcomes": [
        {
          "apparent_likelihood": "likely",
          "effects": {
            "befriend_dragon": "good"
          },
          "name": "appreciates_kindness",
          "salience": "explicit"
        }
      ],
      "prospective_impressions": None,
      "factored_decision_models": None,
      "goal_relevance": None,
      "retrospective_impressions": None,
    }
    ```
    TODO: More examples!
    """
    return {
      "choice": pack(self.choice),
      "option": pack(self.option),
      "outcomes": [ pack(o) for o in self.outcomes.values() ],
      "prospective_impressions": pack(self.prospective_impressions),
      "factored_decision_models": pack(self.factored_decision_models),
      "goal_relevance": pack(self.goal_relevance),
      "retrospective_impressions": pack(self.retrospective_impressions),
      # Note: no need to pack simplified retrospective impressions, as they'll
      # be reconstructed from the full retrospectives.
    }

  def unpack_decision_model(dm):
    """
    Helper method for _unpack_ that unpacks a decision model (a mapping from
    option names to mappings from goal names to lists of Prospective
    impressions).
    """
    return {
      optname: {
        goalname: [
          unpack(pri, perception.Prospective)
            for pri in dm[optname][goalname]
        ]
          for goalname in dm[optname]
      }
        for optname in dm
    } if dm else None

  def _unpack_(obj):
    """
    The inverse of `_pack_`; creates a Decision from a simple object.

    Note that the choice, option, and outcomes of this decision are new,
    disentangled objects, so this it isn't terribly memory efficient to pack
    and unpack Decision objects, and true linkage shouldn't be assumed.
    """
    return Decision(
      unpack(obj["choice"], choice.Choice),
      unpack(obj["option"], choice.Option),
      [ unpack(o, choice.Outcome) for o in obj["outcomes"] ],
      Decision.unpack_decision_model(obj["prospective_impressions"]),
      [
        Decision.unpack_decision_model(dm)
          for dm in obj["factored_decision_models"]
      ] if obj["factored_decision_models"] else None,
      {
        gn: unpack(obj["goal_relevance"][gn], Salience)
          for gn in obj["goal_relevance"]
      } if obj["goal_relevance"] else None,
      {
        gn: [
          unpack(o, perception.Retrospective)
            for o in obj["retrospective_impressions"][gn]
        ]
          for gn in obj["retrospective_impressions"]
      } if obj["retrospective_impressions"] else None
    )


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
    self.outcomes. Will raise a RuntimeError if an option hasn't been chosen.
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
    if self.prospective_impressions != None or self.goal_relevance != None:
      raise RuntimeError(
        "Attempted to add prospective impressions to a decision which already "
        "has them."
      )

    self.prospective_impressions = mode_of_engagement.build_decision_model(
      self.choice
    )


    (
      self.factored_decision_models,
      self.goal_relevance
    ) = mode_of_engagement.get_factored_decision_model(
      self.choice,
      priority_method,
      dm=self.prospective_impressions
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
                goal=goal,
                choice=self.choice.name,
                option=self.option.name,
                outcome=out.name,
                prospective=pri,
                salience=1.0, # TODO: retrospective saliences would hook in here
                valence=val
              )
            )

    # Also create bundled simplified retrospective impressions
    self.add_simplified_retrospectives()

  def add_simplified_retrospectives(self):
    """
    Fills in simplified retrospective impressions from full retrospectives.
    Normally it's not necessary to call this manually, and it's an error to
    call it if simplified retrospectives have already been added.
    """
    if self.simplified_retrospectives:
      raise RuntimeError(
        "Attempted to add simplified retrospectives to a decision which "
        "already had them."
      )

    self.simplified_retrospectives = {}
    for goal in self.retrospective_impressions:
      ilist = self.retrospective_impressions[goal]
      self.simplified_retrospectives[goal] = \
        perception.Retrospective.merge_retrospective_impressions(ilist)
