"""
Core definitions for Pathos AI.

This module defines the foundational types and classes used across the library.
It separates the 'Physics' (SearchDomain) from the 'Bookkeeping' (Node).
"""

from typing import (
    Any,
    Generic,
    Iterable,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# --- 1. Generics ---
# We use S and A as placeholders.
# S = State (Could be an int, a string, a tuple, a huge Numpy array...)
# A = Action (Could be a string 'UP', an int 1, or a function...)
S = TypeVar("S")  # State
A = TypeVar("A")  # Action


# --- 2. The Protocols (The Physics) ---
@runtime_checkable
class SearchDomain(Protocol[S, A]):
    """
    The absolute minimum requirement to be a 'Problem' in Pathos.
    You must define how the world looks (actions) and how it changes (result).
    """

    @property
    def initial_state(self) -> S:
        """
        The initial state of the problem.
        """
        ...

    def actions(self, state: S) -> Iterable[A]:
        """
        Returns a list of valid actions available in this state.
        """
        ...

    def result(self, state: S, action: A) -> S:
        """
        Return the new state that results from taking action in state.
        """
        ...


@runtime_checkable
class CostSensitive(SearchDomain[S, A], Protocol[S, A]):
    """
    A problem where actions have different costs (weights).
    """

    def step_cost(self, state: S, action: A, next_state: S) -> float:
        """
        Returns the cost of taking action in state to reach next_state.
        """
        ...


@runtime_checkable
class GoalOriented(SearchDomain[S, A], Protocol[S, A]):
    """
    A problem that has a specific goal state to reach.
    """

    def is_goal(self, state: S) -> bool:
        """
        Returns True if the given state is a goal state.
        """
        ...


@runtime_checkable
class GoalCostOriented(GoalOriented[S, A], CostSensitive[S, A], Protocol[S, A]):
    """
    A problem that is both goal-oriented and cost-sensitive.
    """

    pass


# --- 3. The mixins (Helper classes) ---


class MetricProblem:
    """
    Inherit from this mixin if your problem has uniform costs (1.0 per step).
    Useful for simple mazes or logic puzzles.
    """

    def step_cost(self, state: Any, action: Any, next_state: Any) -> float:
        return 1.0


# --- 4. The Universal Node (The Traveler) ---


class Node(Generic[S, A]):
    """
    A Node in the search tree.

    It wraps a 'state' and tracks the path taken to reach it.
    """

    __slots__ = ("state", "parent", "action", "path_cost", "depth")

    def __init__(
        self,
        state: S,
        parent: Optional["Node[S, A]"] = None,
        action: Optional[A] = None,
        path_cost: float = 0.0,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

        # Calculate depth automatically:
        self.depth: int = parent.depth + 1 if parent else 0

    def child(self, state: S, action: A, step_cost: float) -> "Node[S, A]":
        """
        Create a child node from this node
        given the resulting state, action taken, and step cost.
        NOTE:
        - This method does NOT decide what the cost is.
        - It only records the cost it is given.
        """
        return Node(
            state=state,
            parent=self,
            action=action,
            path_cost=self.path_cost + step_cost,
        )

    def __repr__(self):
        return f"<Node state = {self.state} cost = {self.path_cost}"

    def __lt__(self, other: "Node") -> bool:
        """
        Less-than comparison.
        REQUIRED for Priority Queues (heapq).
        We compare based on path_cost (g-score) for now.
        Note: In A*, we will wrap this node or compare f-score.
        """
        return self.path_cost < other.path_cost

    def expand(self, problem: SearchDomain[S, A]) -> list["Node[S, A]"]:
        """Generate child nodes by applying all valid actions."""
        children = []
        for action in problem.actions(self.state):
            next_state = problem.result(self.state, action)

            # Auto-detect if problem has step_cost
            if isinstance(problem, CostSensitive):
                cost = problem.step_cost(self.state, action, next_state)
            else:
                cost = 1.0

            children.append(self.child(next_state, action, cost))

        return children
