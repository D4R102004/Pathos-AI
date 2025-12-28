import pytest
from pathos.core import Node, SearchDomain, GoalOriented, CostSensitive


# A simple grid 8x8
class Grid(GoalOriented[tuple[int, int], str], CostSensitive[tuple[int, int], str]):
    # A simple 10x10 grid to have a labyrinth, moving it can cost more than 1.0 per step.
    def __init__(self, rows: int = 10, cols: int = 10, cost: float = 1.0):
        self.rows = rows
        self.cols = cols
        self.cost = cost

    def actions(self, state: tuple[int, int]):
        # the available movements are up, down, left, right
        """
        Docstring for actions
        
        :param self: Description
        :param state: Description
        :type state: tuple[int, int]
        """
        row, col = state
        actions = []
        if row > 1:
            actions.append('up')
        if row < self.rows:
            actions.append('down')
        if col > 1:
            actions.append('left')
        if col < self.cols:
            actions.append('right')
        return actions
        

    def result(self, state: tuple[int, int], action: str) -> tuple[int, int]:
        """
        Docstring for result
        This function returns the new state after taking an action.
        In this case, in an rowsxcolumns Grid, the actions are up, down, left, right.
        
        :param self: the Grid
        :param state: The current state of the grid
        :type state: tuple[int, int]
        :param action: The action to be taken
        :type action: str
        :return: The new state after taking the action
        :rtype: tuple[int, int]
        """
        row, col = state
        match action:
            case 'up':
                return (row - 1, col)
            case 'down':
                return (row + 1, col)
            case 'left':
                return (row, col - 1)
            case 'right':
                return (row, col + 1)
            
        return state

    def is_goal(self, state: tuple[int, int]) -> bool:
        """
        Docstring for is_goal
        
        If the current state is at the end of the grid, then we have reached the goal.

        :param self: The grid
        :param state: The state we're in currently
        """
        return state == (self.rows, self.cols)
    
    def step_cost(self, state: tuple[int, int], action: str, next_state: tuple[int, int]) -> float:
        """
        Docstring for step_cost
        
        In this simple grid, every movement has the same cost.

        :param self: The grid
        :param state: The current state
        :param action: The action taken
        :param next_state: The resulting state
        :return: The cost of taking the action
        """
        return self.cost
     
def test_grid_initialization():
    # Test that expand and initialize gets correct nodes
    problem = Grid(cost = 2.0)
    root = Node(state = (1, 1))

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
    

