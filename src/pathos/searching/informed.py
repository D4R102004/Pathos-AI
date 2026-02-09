"""
Informed (Heuristic) Search Algorithms.

This module implements cost-aware search algorithms that use priority
queues to explore the most promising nodes first.

Included algorithms:
- A* Search: Uses f(n) = g(n) + h(n) to find optimal paths efficiently
- Uniform Cost Search: Available via uniformed.py, implemented as A* with h(n)=0

SOLID Principles Applied:
- Open/Closed: Works with any GoalCostOriented problem and any heuristic
- Dependency Inversion: Depends on protocol abstractions, not concrete classes
- Single Responsibility: A* does one thing - finds optimal paths using heuristics
- Interface Segregation: Requires only what it needs (GoalCostOriented)
"""

import heapq
from typing import Optional, Callable, Dict
from pathos.core import Node, GoalCostOriented, S, A


# --- Heuristic Definition ---
# A heuristic is a function that takes a state and returns
# an estimated cost to reach the goal from that state.
Heuristic = Callable[[S], float]


def null_heuristic(state: S) -> float:
    """
    A trivial heuristic that always returns zero.

    Using this heuristic turns A* into Uniform Cost Search,
    since f(n) = g(n) + 0 = g(n).

    This demonstrates the Open/Closed Principle:
    A* is closed to modification but open to extension via heuristics.

    Parameters
    ----------
    state : S
        Any state (not used).

    Returns
    -------
    float
        Always 0.0.

    Example
    -------
    >>> from pathos.examples.maze import Maze
    >>> maze = Maze()
    >>> solution = astar(maze, null_heuristic)  # This is UCS!
    """
    return 0.0


def astar(
    problem: GoalCostOriented[S, A], heuristic: Heuristic[S] = null_heuristic
) -> Optional[Node[S, A]]:
    """
    A* Search Algorithm.

    Finds the lowest-cost path from the initial state to a goal state
    using both:
    - g(n): Actual path cost so far
    - h(n): Heuristic estimate to the goal
    - f(n) = g(n) + h(n): Evaluation function

    Algorithm:
    1. Priority queue ordered by f(n)
    2. Always expand node with lowest f(n)
    3. Track best cost to reach each state
    4. Skip nodes if we've found a cheaper path
    5. Return when goal is expanded (not when added to frontier)

    Optimality Guarantee:
    - If h(n) is admissible (never overestimates), A* finds optimal solution
    - If h(n) is consistent (monotonic), A* is optimally efficient

    Time Complexity: O(b^d) in worst case, often much better with good heuristic
    Space Complexity: O(b^d) - stores nodes in frontier and cost_so_far dict

    Parameters
    ----------
    problem : GoalCostOriented
        A search domain that:
        - Defines an initial state
        - Can test goal states
        - Provides actions and transitions
        - Assigns costs to transitions

    heuristic : Callable[[S], float], optional
        A function that estimates the remaining cost from a state
        to a goal. Must be admissible (never overestimate) for
        optimality guarantees. Defaults to null_heuristic (making this UCS).

    Returns
    -------
    Optional[Node]
        A goal node representing the lowest-cost solution path,
        or None if no solution exists.

    Example
    -------
    >>> from pathos.examples.maze import Maze, manhattan_heuristic
    >>> maze = Maze(length=10, width=10, start=(0,0), goal=(9,9))
    >>> h = manhattan_heuristic(maze._goal_state)
    >>> solution = astar(maze, h)
    >>> if solution:
    ...     print(f"Found path with cost {solution.path_cost}")

    Note
    ----
    To use A* as Uniform Cost Search, simply omit the heuristic:
    >>> solution = astar(problem)  # Uses null_heuristic by default

    See Also
    --------
    pathos.searching.uniformed.uniform_cost_search : Explicit UCS function
    """

    # --- 1. Create the root node ---
    start_node: Node[S, A] = Node(state=problem.initial_state)

    # Early termination: check if initial state is goal
    if problem.is_goal(start_node.state):
        return start_node

    # --- 2. Priority queue (min-heap) ---
    # Stores tuples of the form: (f_score, node)
    #
    # Python's heapq always pops the tuple with the smallest first element.
    # This ensures we always expand the node with lowest f(n) = g(n) + h(n)
    frontier: list[tuple[float, Node[S, A]]] = []

    # Compute initial f-score
    initial_h = heuristic(problem.initial_state)
    initial_f = start_node.path_cost + initial_h
    heapq.heappush(frontier, (initial_f, start_node))

    # --- 3. Cost tracking ---
    # Maps each visited state to the cheapest known cost (g) to reach it.
    #
    # This replaces BFS/DFS's simple 'visited' set.
    # We need to track costs because:
    # - Same state might be reached via different paths
    # - We only want to expand the state via the cheapest path
    cost_so_far: Dict[S, float] = {start_node.state: start_node.path_cost}

    # --- 4. Main A* loop ---
    while frontier:
        # Pop the node with the lowest f(n)
        f_score, node = heapq.heappop(frontier)

        # --- Lazy deletion optimization ---
        # If this node's cost is worse than the best known path
        # to the same state, we can safely ignore it.
        #
        # This handles the case where we added the same state
        # to the frontier multiple times with different costs.
        if node.path_cost > cost_so_far[node.state]:
            continue

        # --- Goal test ---
        # Important: Goal test happens AFTER popping, not when adding to frontier
        # This ensures we've found the optimal path (if heuristic is admissible)
        if problem.is_goal(node.state):
            return node

        # --- Expand node ---
        for child in node.expand(problem):
            new_cost = child.path_cost

            # If the child state has never been visited,
            # or we found a cheaper path to it:
            if child.state not in cost_so_far or new_cost < cost_so_far[child.state]:
                # Update the best known cost to reach this state
                cost_so_far[child.state] = new_cost

                # Calculate f(n) = g(n) + h(n)
                h_score = heuristic(child.state)
                f_score = new_cost + h_score

                # Add to frontier with its f-score
                heapq.heappush(frontier, (f_score, child))

    # No solution found
    return None
