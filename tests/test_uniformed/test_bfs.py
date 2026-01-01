"""
Unit tests for bfs algorithm
"""

import pytest
from pathos.searching.uniformed import bfs, reconstruct_path
from pathos.examples.maze import Maze
from pathos.examples.trivial import TrivialProblem

def test_bfs_simple_path():
    """Test BFS on a simple Maze."""
    problem = Maze(length=5, width=5, start=(1, 1))
    goal_state = (3, 3)

    # Override the is_goal method for this test
    def is_goal(state):
        return state == goal_state

    problem.is_goal = is_goal

    result_node = bfs(problem)
    assert result_node is not None, "BFS did not find a solution when one exists."

    path = reconstruct_path(result_node)
    expected_path_length = 4  # Minimum steps from (1,1) to (3,3) in a grid
    assert len(path) == expected_path_length, f"Expected path length {expected_path_length}, got {len(path)}."


def test_bfs_initial_state_is_goal():
    """
    Test that BFS immediately returns the initial node when it is already a goal.

    This test verifies a critical BFS edge case:
    if the initial state satisfies the goal condition, the algorithm
    must return the root node without expanding any children or
    entering the main search loop.

    Expected behavior:
    ------------------
    - BFS returns a non-None solution.
    - The returned node corresponds to the initial state.
    """
    assert bfs(TrivialProblem()).state == 0
