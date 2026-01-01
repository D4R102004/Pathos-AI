"""
Core definitions for Pathos AI.

This module defines the foundational types and classes used across the library.
It separates the 'Physics' (SearchDomain) from the 'Bookkeeping' (Node).
"""

from typing import (
    Protocol,
    TypeVar,
    Iterable,
    List,
    Optional,
    runtime_checkable,
    Generic,
    Any,
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

    __slots__ = ('state', 'parent', 'action', 'path_cost', 'depth')

    def __init__(self,
                 state: S,
                 parent: Optional['Node[S, A]'] = None,
                 action: Optional[A] = None,
                 path_cost: float = 0.0,
                ):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

        # Calculate depth automatically:
        if parent:
            self.depth = parent.depth + 1
        else:
            self.depth = 0

    def __repr__(self):
        return f"<Node state = {self.state} cost = {self.path_cost}"
    
    def __lt__(self, other: 'Node') -> bool:
        """
        Less-than comparison.
        REQUIRED for Priority Queues (heapq).
        We compare based on path_cost (g-score) for now.
        Note: In A*, we will wrap this node or compare f-score.
        """
        return self.path_cost < other.path_cost
    
    def expand(self, problem: SearchDomain[S, A]) -> List['Node[S, A]']:
        """
        The Engine of the Search.
        
        Generates the child nodes reachable from this node.
        It handles the bookkeeping of costs and pointers automatically.
        """
        children = []
        for action in problem.actions(self.state):
            next_state = problem.result(self.state, action)

            cost = 1.0
            if isinstance(problem, CostSensitive):
                cost = problem.step_cost(self.state, action, next_state)
            

            next_node = Node(
                state = next_state,
                parent = self,
                action = action,
                path_cost = self.path_cost + cost
            )
            children.append(next_node)
        
        return children

         
        

        