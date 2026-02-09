from pathos.core import GoalOriented


# --- 1. The Dummy Problem ---
# We create a fake problem to test the Node.
# A simple "Number Line" from 0 to 10 by default: You can step Left (-1) or Right (+1).
class NumberLine(GoalOriented[int, str]):
    def __init__(
        self, initial_state: int = 0, leftBound: int = 0, rightBound: int = 10
    ):
        self._leftBound = leftBound
        self._rightBound = rightBound
        self._initial_state = initial_state

    @property
    def initial_state(self) -> int:
        return self._initial_state

    @property
    def left_bound(self) -> int:
        return self._leftBound

    @property
    def right_bound(self) -> int:
        return self._rightBound

    def actions(self, state: int):
        leftBound, rightBound = self.left_bound, self.right_bound
        actions = []

        if state > leftBound:
            actions.append("-1")
        if state < rightBound:
            actions.append("+1")

        return actions

    def result(self, state: int, action: str) -> int:
        if action == "+1":
            return state + 1
        elif action == "-1":
            return state - 1
        return state

    def is_goal(self, state: int) -> bool:
        return state == self.right_bound
