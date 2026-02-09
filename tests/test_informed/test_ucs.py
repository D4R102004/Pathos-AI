"""
Unit tests for Uniform Cost Search and MetricProblem mixin.

These tests verify:
- UCS finds optimal (least-cost) paths
- MetricProblem mixin provides uniform costs
- Integration with the protocol-based architecture

SOLID Principles Demonstrated:
- Open/Closed: MetricProblem extends problems without modification
- Liskov Substitution: Problems using MetricProblem are substitutable
- Interface Segregation: MetricProblem only adds what's needed (step_cost)
- Dependency Inversion: Tests depend on protocols, not concrete classes
"""

from typing import List

from pathos.core import GoalOriented, MetricProblem, Node
from pathos.examples.number_line import NumberLine
from pathos.searching.uniformed import bfs, uniform_cost_search


class SimpleMetricProblem(MetricProblem, GoalOriented[int, str]):
    """
    A minimal problem using the MetricProblem mixin.

    This demonstrates the Open/Closed Principle:
    - We EXTEND the problem with cost behavior (via mixin)
    - We DON'T MODIFY the base GoalOriented protocol

    The mixin provides step_cost automatically (always 1.0).
    """

    def __init__(self, start: int = 0, goal: int = 5):
        self._start = start
        self._goal = goal

    @property
    def initial_state(self) -> int:
        return self._start

    def actions(self, state: int) -> List[str]:
        """Can move left or right."""
        actions = []
        if state > 0:
            actions.append("LEFT")
        if state < 10:
            actions.append("RIGHT")
        return actions

    def result(self, state: int, action: str) -> int:
        """Apply action to get new state."""
        if action == "LEFT":
            return state - 1
        elif action == "RIGHT":
            return state + 1
        return state

    def is_goal(self, state: int) -> bool:
        return state == self._goal


def test_ucs_finds_optimal_path():
    """
    UCS should find the least-cost path.

    In a uniform-cost problem (all steps cost 1.0),
    UCS should behave like BFS (shortest path).
    """
    problem = SimpleMetricProblem(start=0, goal=5)
    solution = uniform_cost_search(problem)

    assert solution is not None, "UCS should find solution"
    assert solution.state == 5, "Should reach goal state"
    assert solution.path_cost == 5.0, "Should take 5 steps (0→1→2→3→4→5)"
    assert solution.depth == 5, "Should be at depth 5"


def test_ucs_same_as_bfs_for_uniform_costs():
    """
    When all costs are uniform (1.0), UCS should find
    the same path length as BFS.

    This demonstrates Liskov Substitution Principle:
    SimpleMetricProblem (using mixin) is substitutable
    for any GoalOriented problem.
    """
    problem = SimpleMetricProblem(start=0, goal=3)

    ucs_solution = uniform_cost_search(problem)
    bfs_solution = bfs(problem)

    assert ucs_solution is not None, "UCS should find solution"
    assert bfs_solution is not None, "BFS should find solution"

    # For uniform costs, both should find same path length
    assert ucs_solution.path_cost == bfs_solution.path_cost
    assert ucs_solution.depth == bfs_solution.depth


def test_metric_problem_mixin_provides_step_cost():
    """
    MetricProblem mixin should automatically provide
    step_cost method that returns 1.0.

    This demonstrates Interface Segregation Principle:
    The mixin adds ONLY step_cost, nothing else.
    """
    problem = SimpleMetricProblem()

    # Verify mixin provides step_cost
    assert hasattr(problem, "step_cost"), "Should have step_cost method"

    # Verify it always returns 1.0
    cost = problem.step_cost(0, "RIGHT", 1)
    assert cost == 1.0, "MetricProblem should provide uniform cost of 1.0"


def test_ucs_with_number_line():
    """
    UCS should work with NumberLine problem.

    NumberLine doesn't use MetricProblem mixin, but
    UCS should still work (demonstrates protocol flexibility).
    """
    problem = NumberLine(initial_state=0, leftBound=0, rightBound=5)
    solution = uniform_cost_search(problem)

    assert solution is not None, "Should find solution"
    assert solution.state == 5, "Should reach goal"


def test_ucs_initial_state_is_goal():
    """
    UCS should immediately return when initial state is goal.

    This is an important edge case that tests the early
    termination logic.
    """
    problem = SimpleMetricProblem(start=5, goal=5)
    solution = uniform_cost_search(problem)

    assert solution is not None, "Should find solution"
    assert solution.state == 5, "Should be at goal"
    assert solution.path_cost == 0.0, "No movement needed"
    assert solution.depth == 0, "Should be at root"
    assert solution.parent is None, "Should be root node"


def test_ucs_returns_node_with_path_info():
    """
    UCS should return a Node with complete path information.

    This allows us to reconstruct the solution path.
    """
    problem = SimpleMetricProblem(start=0, goal=3)
    solution = uniform_cost_search(problem)

    assert isinstance(solution, Node), "Should return Node"
    assert solution.state == 3, "Should be at goal"
    assert solution.action == "RIGHT", "Last action should be RIGHT"
    assert solution.parent is not None, "Should have parent (not root)"

    # Trace back to root
    current = solution
    depth_check = 0
    while current.parent is not None:
        depth_check += 1
        current = current.parent

    assert depth_check == 3, "Should have 3 steps from root to goal"
    assert current.state == 0, "Root should be initial state"


# Educational Note:
"""
What We Learned from These Tests:
==================================

1. **MetricProblem Mixin (Open/Closed Principle)**
   - Extends problems with cost behavior
   - No modification to existing code
   - Reusable across any problem type

2. **UCS Behavior**
   - Finds optimal (least-cost) paths
   - For uniform costs, behaves like BFS
   - Works with any GoalCostOriented problem

3. **Protocol-Based Design (Dependency Inversion)**
   - UCS works with MetricProblem, Maze, NumberLine
   - All depend on same protocol (GoalCostOriented)
   - Easy to add new problems without changing UCS

4. **Testing Philosophy**
   - Test behaviors, not implementation details
   - Test edge cases (initial state = goal)
   - Test integration (UCS with different problems)
   - Verify SOLID principles in action
"""
