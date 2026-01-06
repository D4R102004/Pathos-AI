"""
Unit tests for dfs algorithm
"""

from pathos.searching.uniformed import dfs, reconstruct_path
from pathos.examples.number_line import NumberLine


def test_dfs_simple_path():
    """Test DFS on a simple number line."""
    problem = NumberLine(initial_state=0, leftBound=0, rightBound=5)

    result_node = dfs(problem)
    assert result_node is not None, "DFS did not find a solution when one exists."

    path = reconstruct_path(result_node)
    expected_path_length = 5  # Minimum steps from 0 to 5 in NumberLine

    print(f"depth = {result_node.depth}")  # For debugging purposes
    print(f"path_cost = {result_node.path_cost}")  # For debugging purposes
    assert (
        len(path) == expected_path_length
    ), f"Expected path length {expected_path_length}, got {len(path)}."
