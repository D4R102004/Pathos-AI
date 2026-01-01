from pathos.core import Node, SearchDomain, GoalOriented, CostSensitive


# A simple grid 8x8
class Grid(GoalOriented[tuple[int, int], str], CostSensitive[tuple[int, int], str]):
    # A simple 10x10 grid to have a labyrinth, moving it can cost more than 1.0 per step.
    def __init__(self, rows: int = 10, cols: int = 10, initial_state = (1, 1),cost: float = 1.0):
        self.rows = rows
        self.cols = cols
        self._initial_state = initial_state
        self.cost = cost


    @property
    def initial_state(self) -> tuple[int, int]:
        return self._initial_state

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
