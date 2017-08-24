"""
goals.py

Models of player goals. Note that this code mostly doesn't deal with the
relationship between options/outcomes and goals, but instead relies on by-hand
annotation to establish that information.
"""

class PlayerGoal:
  def __init__(self, name):
    self.name = name
