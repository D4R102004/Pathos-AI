"""
Uninformed Search Algorithms.

These algorithms explore the search space without any knowledge of the goal's location.
They are 'blind' but systematic.

Includes:
- Breadth-First Search (BFS): Explores level-by-level, finds shortest path
- Depth-First Search (DFS): Explores deeply, memory efficient
- Uniform Cost Search (UCS): Finds cheapest path based on step costs

SOLID Principles Applied:
- Open/Closed: All functions work with ANY GoalOriented problem
- Dependency Inversion: Depend on GoalOriented protocol, not concrete problems
- Single Responsibility: Each function has one search strategy
- Interface Segregation: BFS/DFS need only GoalOriented, not CostSensitive
"""

from collections import deque
from typing import Optional, Set, TypeVar

from pathos.core import GoalOriented, GoalCostOriented, Node, extract_solution_path

S = TypeVar("S")  # State
A = TypeVar("A")  # Action


def bfs(problem: GoalOriented[S, A]) -> Optional[Node[S, A]]:
    """
    Breadth-First Search.

    Explores the search space level-by-level using a FIFO queue.
    Guaranteed to find the shortest path (minimum number of actions)
    for unweighted problems.

    Algorithm:
    1. Start with initial state in frontier
    2. Loop until frontier is empty:
       - Remove shallowest node
       - If goal, return it
       - Otherwise, expand and add children to frontier
    3. Track explored states to avoid cycles

    Time Complexity: O(b^d) where b = branching factor, d = depth
    Space Complexity: O(b^d) - stores all nodes at current level

    Parameters
    ----------
    problem : GoalOriented
        A problem with initial state, actions, transitions, and goal test.

    Returns
    -------
    Optional[Node]
        Goal node with path information, or None if no solution exists.

    Example
    -------
    >>> from pathos.examples.maze import Maze
    >>> maze = Maze(length=5, width=5, start=(0,0), goal=(4,4))
    >>> solution = bfs(maze)
    >>> if solution:
    ...     path = extract_solution_path(solution)
    ...     print(f"Found path with {len(path)} steps")
    """
    # 1. Create root node from initial state
    start_node: Node[S, A] = Node(state=problem.initial_state)

    # Early termination: check if initial state is goal
    if problem.is_goal(start_node.state):
        return start_node

    # 2. FIFO Queue (First In, First Out)
    # This ensures we explore level-by-level
    frontier = deque([start_node])

    # 3. Track explored states to prevent cycles
    explored: Set[S] = {start_node.state}

    while frontier:
        # Remove shallowest node (FIFO)
        node = frontier.popleft()

        # Expand node: generate all children
        for child in node.expand(problem):
            # Only add unexplored states
            if child.state not in explored:
                # Goal test
                if problem.is_goal(child.state):
                    return child

                # Mark as explored and add to frontier
                explored.add(child.state)
                frontier.append(child)

    # No solution found
    return None


def dfs(problem: GoalOriented[S, A]) -> Optional[Node[S, A]]:
    """
    Depth-First Search.

    Explores the search space by going as deep as possible before backtracking.
    Uses a LIFO stack. Memory efficient but not guaranteed to find shortest path.

    Algorithm:
    1. Start with initial state in frontier (stack)
    2. Loop until frontier is empty:
       - Remove deepest node (LIFO)
       - If goal, return it
       - If not explored, mark it and add children
    3. Track explored states to avoid cycles

    Time Complexity: O(b^m) where b = branching factor, m = max depth
    Space Complexity: O(bm) - only stores single path + siblings

    Parameters
    ----------
    problem : GoalOriented
        A problem with initial state, actions, transitions, and goal test.

    Returns
    -------
    Optional[Node]
        Goal node with path information, or None if no solution exists.

    Note
    ----
    DFS may find a suboptimal solution (longer path than necessary).
    Use BFS if you need the shortest path.

    Example
    -------
    >>> from pathos.examples.number_line import NumberLine
    >>> problem = NumberLine(initial_state=0, rightBound=5)
    >>> solution = dfs(problem)
    >>> if solution:
    ...     print(f"Found solution at depth {solution.depth}")
    """
    start_node: Node[S, A] = Node(state=problem.initial_state)

    # Early termination: check if initial state is goal
    if problem.is_goal(start_node.state):
        return start_node

    # LIFO Stack (Last In, First Out)
    # This ensures we explore deeply before backtracking
    frontier = [start_node]

    # Track explored states (starts empty, unlike BFS)
    explored: Set[S] = set()

    while frontier:
        # Remove deepest node (LIFO)
        node = frontier.pop()

        # Goal test (after popping, not before adding)
        if problem.is_goal(node.state):
            return node

        # Only expand if not already explored
        if node.state not in explored:
            explored.add(node.state)

            # Add children to stack (will be explored deeply)
            for child in node.expand(problem):
                if child.state not in explored:
                    frontier.append(child)

    # No solution found
    return None


def uniform_cost_search(problem: GoalCostOriented[S, A]) -> Optional[Node[S, A]]:
    """
    Uniform Cost Search (UCS).

    Finds the least-cost path by always expanding the cheapest node first.
    Uses a priority queue ordered by path cost g(n).

    UCS is a special case of A* where the heuristic h(n) = 0.
    It's optimal for weighted graphs where edge costs vary.

    Algorithm:
    1. Priority queue ordered by path_cost
    2. Always expand cheapest node
    3. Track best cost to reach each state
    4. Update if cheaper path found

    Time Complexity: O(b^(1 + C*/ε)) where C* = optimal cost, ε = min step cost
    Space Complexity: O(b^(1 + C*/ε))

    Parameters
    ----------
    problem : GoalCostOriented
        A problem with costs, initial state, actions, transitions, and goal test.

    Returns
    -------
    Optional[Node]
        Goal node with optimal (least-cost) path, or None if no solution.

    Example
    -------
    >>> from pathos.examples.maze import Maze
    >>> maze = Maze(length=10, width=10)
    >>> solution = uniform_cost_search(maze)
    >>> if solution:
    ...     print(f"Found path with cost {solution.path_cost}")

    Note
    ----
    This is implemented as A* with a null heuristic for code reuse.
    See pathos.searching.informed.astar for the underlying implementation.
    """
    # Import here to avoid circular dependency
    from pathos.searching.informed import astar, null_heuristic

    return astar(problem, null_heuristic)


# --- Backwards Compatibility Alias ---
# The old function name for extracting paths
# Now delegates to core.extract_solution_path


def reconstruct_path(node: Node[S, A]) -> list[A]:
    """
    Legacy function name for extract_solution_path.

    Kept for backwards compatibility with existing code.
    New code should use pathos.core.extract_solution_path directly.

    Parameters
    ----------
    node : Node
        The goal node.

    Returns
    -------
    list[A]
        Sequence of actions from root to goal.
    """
    return extract_solution_path(node)
