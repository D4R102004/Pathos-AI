import pytest
from pathos.core import Node, SearchDomain, GoalOriented, CostSensitive
from pathos.examples.free_grid import Grid




     
def test_grid_initialization():
    # Test that expand and initialize gets correct nodes
    problem = Grid(cost = 2.0)
    assert problem.initial_state == (1, 1)
    root = Node(state = problem.initial_state)

    children = root.expand(problem)

    # There should be 2 directions if we start in (1, 1)
    assert len(children) == 2

    # First movement available is down if you are at the beggining
    child_down = children[0]
    assert child_down.parent == root
    assert child_down.state == (2, 1)
    assert child_down.action == 'down'
    assert child_down.depth == 1
    assert child_down.path_cost == 2.0

    # Second movement should be right if you are at the beggining
    child_right = children[1]
    assert child_right.action == 'right'
    assert child_right.state == (1, 2)

    # From the right ([1, 2]) we should have three movements available: left, down, right
    second_children = child_right.expand(problem)

    assert len(second_children) == 3

    # Check that the the down node is correct
    assert second_children[0].parent == child_right
    assert second_children[0].state == (2, 2)
    assert second_children[0].action == 'down'
    assert second_children[0].depth == 2
    assert second_children[0].path_cost == 4.0 

def test_goal():
    # The goal is [10][10] by default.
    problem = Grid()
    root = Node(state = (10, 10))
    goal_reached = problem.is_goal(root.state)
    assert goal_reached == True
    

