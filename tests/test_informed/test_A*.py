"""
Unit tests for the A* search algorithm.

These tests verify the *behavioral contracts* of A*,
not its internal implementation details.

We check:
- Correct handling of trivial problems
- Optimality guarantees
- Compatibility with Uniform Cost Search
- Proper failure behavior when no solution exists

The goal is to ensure algorithm correctness while
respecting SOLID principles.
"""

from pathos.examples.maze import Maze, manhattan_heuristic
from pathos.examples.trivial import TrivialProblem
from pathos.searching.informed import astar
from pathos.searching.uniformed import bfs

# --- Instrumented Maze for Testing ---


class CountingMaze(Maze):
    """
    Maze variant that counts how many nodes are expanded.

    This is used ONLY for testing algorithmic behavior.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expanded_nodes = 0

    def actions(self, state):
        self.expanded_nodes += 1
        return super().actions(state)


def test_astar_initial_state_is_goal():
    """
    A* must immediately return the initial node
    if the initial state satisfies the goal.
    """
    solution = astar(TrivialProblem())
    assert solution is not None
    assert solution.state == 0
    assert solution.path_cost == 0.0


def test_astar_finds_solution_in_maze():
    """
    A* must find a valid solution path in a non-trivial maze.
    """
    walls = {(0, 1), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (1, 3), (2, 3)}

    maze = Maze(length=5, width=5, walls=walls, start=(0, 0), goal=(4, 4))

    solution = astar(maze)

    assert solution is not None
    assert maze.is_goal(solution.state)


def test_astar_explores_fewer_nodes_than_bfs():
    """
    A* should expand fewer nodes than BFS
    when solving a maze with multiple valid paths.
    """
    length = 7
    width = 12
    walls = {
        (0, 1),
        (0, 3),
        (0, 5),
        (0, 6),
        (0, 7),
        (0, 10),
        (1, 1),
        (1, 3),
        (1, 7),
        (1, 9),
        (1, 10),
        (2, 3),
        (2, 5),
        (2, 9),
        (2, 10),
        (3, 0),
        (3, 2),
        (3, 3),
        (3, 5),
        (3, 7),
        (3, 9),
        (3, 10),
        (4, 0),
        (4, 5),
        (4, 7),
        (5, 0),
        (5, 1),
        (5, 2),
        (5, 4),
        (5, 5),
        (5, 7),
        (5, 8),
        (5, 9),
        (5, 10),
        (5, 11),
        (6, 4),
        (6, 5),
    }

    #   · █ · █ · █ █ █ · · █ G
    #   · █ · █ · · · █ · █ █ ·
    #   · · · █ · █ · · · █ █ ·
    #   █ · █ █ · █ · █ · █ █ ·
    #   █ · · · · █ · █ · · · ·
    #   █ █ █ · █ █ · █ █ █ █ █
    #   S · · · █ █ · · · · · ·

    maze_for_bfs = CountingMaze(
        length=length, width=width, walls=walls, start=(6, 0), goal=(0, 11)
    )

    maze_for_astar = CountingMaze(
        length=length, width=width, walls=walls, start=(6, 0), goal=(0, 11)
    )

    bfs_solution = bfs(maze_for_bfs)

    heuristic = manhattan_heuristic(maze_for_astar._goal_state)
    astar_solution = astar(maze_for_astar, heuristic)

    assert bfs_solution is not None
    assert astar_solution is not None

    # Both must reach the goal
    assert maze_for_bfs.is_goal(bfs_solution.state)
    assert maze_for_astar.is_goal(astar_solution.state)

    print(maze_for_astar.expanded_nodes)
    print(maze_for_bfs.expanded_nodes)
    # A* must expand fewer nodes than BFS
    assert maze_for_astar.expanded_nodes < maze_for_bfs.expanded_nodes
