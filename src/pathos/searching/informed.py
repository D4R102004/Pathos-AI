"""
Informed (Heuristic) Search Algorithms.

This module implements cost-aware search algorithms that use priority
queues to explore the most promising nodes first.

Included algorithms:
- A* Search:
    Uses the evaluation function:
        f(n) = g(n) + h(n)
    where:
        g(n) = cost from start to node n
        h(n) = heuristic estimate from n to the goal

- Uniform Cost Search (UCS):
    A special case of A* where:
        h(n) = 0 for all n
    This causes the algorithm to expand nodes purely in order of path cost.
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
    """
    return 0.0


def astar(
    problem: GoalCostOriented[S, A], heuristic: Heuristic[S] = null_heuristic
) -> Optional[Node[S, A]]:
    """
    A* Search Algorithm.

    Finds the lowest-cost path from the initial state to a goal state
    using both:
    - Actual path cost so far (g)
    - Heuristic estimate to the goal (h)

    Parameters
    ----------
    problem : GoalOriented & CostSensitive
        A search domain that:
        - Defines an initial state
        - Can test goal states
        - Provides actions and transitions
        - Assigns costs to transitions

    heuristic : Callable[[S], float]
        A function that estimates the remaining cost from a state
        to a goal. Must be admissible (never overestimate) for
        optimality guarantees.

    Returns
    -------
    Optional[Node]
        A goal node representing the lowest-cost solution path,
        or None if no solution exists.
    """

    # --- 1. Create the root node ---
    start_node: Node[S, A] = Node(state=problem.initial_state)

    # --- 2. Priority queue (min-heap) ---
    # Stores tuples of the form:
    #   (f_score, node)
    #
    # Python's heapq always pops the tuple with the smallest first element.
    frontier: list[tuple[float, Node[S, A]]] = []

    # Compute initial f-score
    initial_h = heuristic(problem.initial_state)
    heapq.heappush(frontier, (start_node.path_cost + initial_h, start_node))

    # --- 3. Cost tracking ---
    # Maps each visited state to the cheapest known cost (g)
    # needed to reach it from the start.
    #
    # This replaces BFS/DFS's simple 'visited' set.
    cost_so_far: Dict[S, float] = {start_node.state: start_node.path_cost}

    # --- 4. Main A* loop ---
    while frontier:
        # Pop the node with the lowest f(n)
        _, node = heapq.heappop(frontier)

        # --- Lazy deletion optimization ---
        # If this node is more expensive than the best known path
        # to the same state, discard it.
        if node.path_cost > cost_so_far[node.state]:
            continue

        # --- Goal test ---
        if problem.is_goal(node.state):
            return node

        # --- Expand node ---
        for child in node.expand(problem):
            new_cost = child.path_cost

            # If the child state has never been visited,
            # or we found a cheaper path to it:

            if child.state not in cost_so_far or new_cost < cost_so_far[child.state]:
                cost_so_far[child.state] = new_cost
                f_score = new_cost + heuristic(child.state)
                heapq.heappush(frontier, (f_score, child))

    # No solution found
    return None
