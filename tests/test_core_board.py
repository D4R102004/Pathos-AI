from pathos.core import Node
from pathos.examples.maze import Maze


def test_maze_initialization():
    # Test that expand and initialize gets correct nodes
    problem = Maze()
    assert problem.initial_state == (0, 0)
    root = Node(state=problem.initial_state)

    children = root.expand(problem)

    # There should be 2 directions if we start in (0, 0)
    assert len(children) == 2

    # First movement available is down if you are at the beggining
    child_down = children[0]
    assert child_down.parent == root
    assert child_down.state == (1, 0)
    assert child_down.action == "DOWN"
    assert child_down.depth == 1
    assert child_down.path_cost == 1.0

    # Second movement should be right if you are at the beggining
    child_right = children[1]
    assert child_right.action == "RIGHT"
    assert child_right.state == (0, 1)

    # From the right ([0, 1]) we should have three movements available: left, down, right
    second_children = child_right.expand(problem)

    assert len(second_children) == 3

    # Check that the the down node is correct
    assert second_children[0].parent == child_right
    assert second_children[0].state == (1, 1)
    assert second_children[0].action == "DOWN"
    assert second_children[0].depth == 2
    assert second_children[0].path_cost == 2.0


def test_goal():
    # The goal is [9][9] by default.
    problem = Maze()
    root = Node(state=(9, 9))
    goal_reached = problem.is_goal(root.state)
    assert goal_reached is True
