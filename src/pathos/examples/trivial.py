"""
A trivial Goal-Oriented problem.
it's initial state is equal to its goal statw
"""

from pathos.core import GoalOriented


class TrivialProblem(GoalOriented[int, None]):
    """
    A minimal Goal-Oriented problem

    This problem is intentionally trivial:
    - The initial state is already a goal.
    - No actions are available.
    - Any attempt to transition keeps the same state.

    Purpose:
    --------
    This class is used to verify that search algorithms (e.g., BFS)
    correctly handle the edge case where the initial state satisfies
    the goal condition and immediately return the root node without
    performing any exploration.

    This ensures:
    - Proper initial goal checking
    - No unnecessary node expansion
    - Correct handling of empty action spaces
    """

    @property
    def initial_state(self) -> int:
        return 0

    def is_goal(self, s: int) -> bool:
        return True

    def actions(self, s: int):
        return []

    def result(self, s: int, a: None) -> int:
        return s
