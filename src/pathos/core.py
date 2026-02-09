"""
Core definitions for Pathos AI.

This module defines the foundational types and classes used across the library.
It separates the 'Physics' (SearchDomain) from the 'Bookkeeping' (Node).

SOLID Principles Applied:
- Single Responsibility: Each protocol defines ONE behavioral concern
- Open/Closed: Protocols allow extension without modification
- Liskov Substitution: Protocol composition maintains substitutability
- Interface Segregation: Minimal, focused protocols
- Dependency Inversion: All code depends on protocol abstractions
"""

from typing import (
    Any,
    Generic,
    Iterable,
    List,
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

    You must define:
    - initial_state: Where the search begins
    - actions: What moves are possible from a state
    - result: What happens when you take an action

    This protocol follows Interface Segregation Principle:
    it contains ONLY the essential operations needed for basic search.
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

    Extends SearchDomain with cost calculation capability.
    Required for algorithms like UCS and A*.

    Follows Interface Segregation: Only problems that NEED costs
    must implement this. Simple problems can use SearchDomain alone.
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

    Extends SearchDomain with goal testing capability.
    Required for goal-directed search algorithms like BFS, DFS, A*.

    Follows Interface Segregation: Separates goal-checking from
    other concerns like cost calculation.
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

    This protocol composition demonstrates Liskov Substitution Principle:
    - GoalCostOriented IS-A GoalOriented (can use with BFS)
    - GoalCostOriented IS-A CostSensitive (can use with UCS)
    - GoalCostOriented works with A* (needs both)

    No new methods needed - it's pure composition.
    """

    pass


# --- 3. The Mixins (Helper classes) ---


class MetricProblem:
    """
    Inherit from this mixin if your problem has uniform costs (1.0 per step).

    Useful for simple mazes or logic puzzles where all moves cost the same.

    Example
    -------
    >>> class SimpleMaze(MetricProblem, GoalOriented):
    ...     # step_cost is automatically 1.0 for all moves
    ...     pass

    This mixin follows Single Responsibility Principle:
    Its only job is to provide default uniform cost behavior.
    """

    def step_cost(self, state: Any, action: Any, next_state: Any) -> float:
        """Return uniform cost of 1.0 for all actions."""
        return 1.0


# --- 4. The Universal Node (The Traveler) ---


class Node(Generic[S, A]):
    """
    A Node in the search tree.

    It wraps a 'state' and tracks the path taken to reach it.

    SOLID Principles:
    - Single Responsibility: Only tracks search tree bookkeeping
    - Open/Closed: Works with any SearchDomain via protocols
    - Dependency Inversion: Depends on SearchDomain abstraction

    Memory Optimization:
    - Uses __slots__ to reduce memory footprint
    - Critical for algorithms that generate millions of nodes
    """

    __slots__ = ("state", "parent", "action", "path_cost", "depth")

    def __init__(
        self,
        state: S,
        parent: Optional["Node[S, A]"] = None,
        action: Optional[A] = None,
        path_cost: float = 0.0,
    ):
        """
        Create a search tree node.

        Parameters
        ----------
        state : S
            The state this node represents.
        parent : Optional[Node]
            The parent node (None for root).
        action : Optional[A]
            The action taken to reach this node from parent.
        path_cost : float
            Total cost from root to this node.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

        # Calculate depth automatically:
        self.depth: int = parent.depth + 1 if parent else 0

    def child(self, state: S, action: A, step_cost: float) -> "Node[S, A]":
        """
        Create a child node from this node.

        Parameters
        ----------
        state : S
            The resulting state after taking the action.
        action : A
            The action taken.
        step_cost : float
            The cost of taking this action.

        Returns
        -------
        Node[S, A]
            A new child node.

        Note
        ----
        This method does NOT decide what the cost is.
        It only records the cost it is given.
        Cost calculation is the problem's responsibility.
        """
        return Node(
            state=state,
            parent=self,
            action=action,
            path_cost=self.path_cost + step_cost,
        )

    def __repr__(self):
        """Developer-friendly representation."""
        return f"<Node state={self.state} cost={self.path_cost}>"

    def __lt__(self, other: "Node") -> bool:
        """
        Less-than comparison for priority queues.

        Required for heapq to work with Nodes.
        Compares based on path_cost (g-score).

        In A*, the frontier stores (f_score, node) tuples,
        so this comparison is used as a tiebreaker.
        """
        return self.path_cost < other.path_cost

    def expand(self, problem: SearchDomain[S, A]) -> list["Node[S, A]"]:
        """
        Generate child nodes by applying all valid actions.

        This method demonstrates:
        - Open/Closed Principle: Works with any SearchDomain
        - Dependency Inversion: Depends on protocol, not concrete class
        - Single Responsibility: Just generates children, doesn't search

        Parameters
        ----------
        problem : SearchDomain
            The problem defining valid actions and transitions.

        Returns
        -------
        list[Node[S, A]]
            List of child nodes reachable from this node.
        """
        children = []
        for action in problem.actions(self.state):
            next_state = problem.result(self.state, action)

            # Auto-detect if problem has step_cost (Open/Closed Principle)
            if isinstance(problem, CostSensitive):
                cost = problem.step_cost(self.state, action, next_state)
            else:
                cost = 1.0

            children.append(self.child(next_state, action, cost))

        return children


# --- 5. Utility Functions ---


def extract_solution_path(node: Node[S, A]) -> List[A]:
    """
    Extract the sequence of actions from root to this node.

    This is a utility function, not a Node method, to follow
    Single Responsibility Principle:
    - Node's job: Track tree structure
    - This function's job: Extract information from the tree

    Parameters
    ----------
    node : Node
        The goal node (or any node in the search tree).

    Returns
    -------
    List[A]
        Sequence of actions from root to this node.

    Example
    -------
    >>> path = extract_solution_path(goal_node)
    >>> # path = ['RIGHT', 'DOWN', 'DOWN', 'RIGHT']
    """
    actions: List[A] = []
    current = node

    while current.parent is not None:
        if current.action is not None:
            actions.append(current.action)
        current = current.parent

    return list(reversed(actions))


def extract_state_path(node: Node[S, A]) -> List[S]:
    """
    Extract the sequence of states from root to this node.

    Parameters
    ----------
    node : Node
        The goal node (or any node in the search tree).

    Returns
    -------
    List[S]
        Sequence of states from root to this node.

    Example
    -------
    >>> states = extract_state_path(goal_node)
    >>> # states = [(0,0), (0,1), (1,1), (2,1), (2,2)]
    """
    states: List[S] = []
    current = node

    while current is not None:
        states.append(current.state)
        current = current.parent

    return list(reversed(states))
