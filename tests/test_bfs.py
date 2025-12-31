"""
Unit tests for bfs algorithm
"""

import pytest
from pathos.searching.uniformed import bfs, reconstruct_path
from test_core_board import Grid

def test_bfs_simple_path():
    """Test BFS on a simple grid."""
    problem = Grid(rows=5, cols=5, initial_state=(1, 1))
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