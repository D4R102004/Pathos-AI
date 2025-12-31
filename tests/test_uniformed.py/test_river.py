"""
Simple test for the river problem in src/examples/river.py
"""


import pytest
from pathos.examples.river import RiverPuzzle
from pathos.searching.uniformed import bfs, dfs, reconstruct_path


def test_river_solution():
    """
    Test that both bfs and dfs give the correct solution. Also dfs solution should be higher than bfs
    """
    problem = RiverPuzzle()

    bfs_result_node = bfs(problem)
    assert bfs_result_node is not None, "BFS did not find a solution when one exists."

    dfs_result_node = dfs(problem)
    assert dfs_result_node is not None, "DFS did not find a solution when one exists."

    bfs_path = reconstruct_path(bfs_result_node)
    dfs_path = reconstruct_path(dfs_result_node)


    # The expected minimum number of steps to solve the puzzle is 7
    expected_min_steps = 7
    assert len(bfs_path) == expected_min_steps, f"Expected BFS path length {expected_min_steps}, got {len(bfs_path)}."
    assert len(dfs_path) >= expected_min_steps, f"Expected DFS path length at least {expected_min_steps}, got {len(dfs_path)}."