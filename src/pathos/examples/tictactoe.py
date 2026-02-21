"""
Tic-Tac-Toe as an Adversarial Game Domain.

This module implements a configurable N×N Tic-Tac-Toe game as a
concrete example of the AdversarialGame protocol. It is the canonical
test case for Minimax and Alpha-Beta Pruning.

Configurable by board size (default 3×3):
- 3×3 is classic Tic-Tac-Toe (small, fully searchable)
- 4×4 or 5×5 gives a harder search problem for benchmarking

Why Tic-Tac-Toe?
----------------
It is the simplest non-trivial two-player zero-sum game:
- Small enough to search completely (at most 9! = 362,880 states)
- Complex enough to demonstrate all Minimax concepts
- Has a known perfect strategy: optimal play ALWAYS draws
- This gives us a ground truth for correctness testing —
  if Minimax plays itself and doesn't draw, the algorithm is broken

This makes it the perfect unit test for adversarial algorithms.

Design Decisions:
-----------------
- Board as immutable tuple: enables safe backtracking, hashable for caching
- Players as +1 and -1: connects directly to utility scores (zero-sum math)
- Size configurable: follows same pattern as Maze (sensible defaults,
  open to extension without modification)

SOLID Principles:
-----------------
S - Handles Tic-Tac-Toe rules only. Not rendering, not solving.
O - Minimax works with this without modification. Size is configurable.
L - Fully substitutable for AdversarialGame[Board, int].
I - Implements exactly the 6 methods the protocol requires.
D - Minimax depends on AdversarialGame, never on TicTacToe directly.
"""

from typing import Iterable, List, Optional, Tuple

Board = Tuple[int, ...]  # 9 integers: -1, 0, or +1
Action = int  # cell index: 0 to (size*size - 1)


class TicTacToe:
    """
    A configurable N×N Tic-Tac-Toe game implementing AdversarialGame.

    This class is the 'domain expert' — it knows all the rules.
    Minimax knows nothing about Tic-Tac-Toe; it only knows about
    AdversarialGame. This separation is Dependency Inversion Principle.

    Parameters
    ----------
    size : int
        Board dimension. Default 3 gives classic 3×3 Tic-Tac-Toe.
    win_length : int
        How many in a row to win. Default 3.
        TicTacToe(15, 5) gives you Gomoku — same class, different game.

    Examples
    --------
    >>> game = TicTacToe()           # classic 3×3
    >>> game = TicTacToe(4, 3)       # 4×4 board, 3 in a row wins
    >>> game = TicTacToe(4, 4)       # 4×4 board, 4 in a row wins
    >>> game = TicTacToe(15, 5)      # Gomoku
    """

    def __init__(self, size: int = 3, win_length: int = 3) -> None:
        # Validate inputs — catch mistakes early with clear error messages.
        # This is "fail fast" — better to crash immediately with a clear
        # message than to produce silent wrong results later.
        if win_length > size:
            raise ValueError(
                f"win_length ({win_length}) cannot exceed size ({size}). "
                f"You can't win with {win_length} in a row on a {size}×{size} board."
            )

        self.size = size
        self.win_length = win_length

        # Precompute winning lines ONCE at construction time.
        # Every call to is_terminal() and _winner() needs these.
        # Computing them once here instead of on every call is a
        # simple but meaningful optimization — especially for large boards
        # where Minimax visits hundreds of thousands of states.
        self._winning_lines = self._compute_winning_lines()

    @property
    def initial_state(self) -> Board:
        """
        Return the empty board — all cells set to zero.

        It is a @property because it describes what the game IS
        (its starting point), not something computed with arguments.
        Same pattern as initial_state in GoalOriented and SearchDomain.

        Returns
        -------
        Board
            A tuple of size*size zeros.
        """
        return tuple(0 for _ in range(self.size * self.size))

    def player(self, state: Board) -> int:
        """
        Determine which player's turn it is in the given state.

        We use a simple convention:
        - MAX is +1
        - MIN is -1
        The player to move is determined by counting how many moves have
        been made (non-zero cells) and using that to alternate turns.

        Parameters
        ----------
        state : Board
            The current board state.

        Returns
        -------
        int
            +1 for MAX's turn, -1 for MIN's turn.
        """
        moves_made = sum(1 for cell in state if cell != 0)
        return +1 if moves_made % 2 == 0 else -1

    def actions(self, state: Board) -> Iterable[Action]:
        """
        Return the legal actions (cell indices) available in the given state.

        An action is legal if the corresponding cell is empty (zero).
        We return the indices of all empty cells.

        Parameters
        ----------
        state : Board
            The current board state.

        Returns
        -------
        Iterable[Action]
            A generator of cell indices where moves can be made.
        """
        return (i for i, cell in enumerate(state) if cell == 0)

    def result(self, state: Board, action: Action) -> Board:
        """
        Apply an action and return a brand new board state.

        The word NEW is critical here. This method NEVER modifies
        the existing state — it always returns a fresh tuple.

        Why immutability?
        -----------------
        Minimax explores branches and backtracks constantly.
        When it explores move A, then backtracks to try move B,
        the original state must be completely untouched.

        If we modified the board in place, the original would be
        corrupted — there is no "undo" in Minimax. Every subsequent
        branch would be built on a broken foundation.

        By returning a NEW tuple, the original is guaranteed intact.
        Tuples in Python cannot be modified — that's a language-level
        guarantee, not just a convention.

        Why list then back to tuple?
        ----------------------------
        Tuples are immutable — you cannot do state[4] = 1 on a tuple.
        So we:
            1. Convert to a list (mutable copy)
            2. Apply the move to the list
            3. Convert back to an immutable tuple

        The original tuple is never touched at any point.

        Parameters
        ----------
        state : Board
            The current board state.
        action : Action
            The cell index where the current player places their piece.

        Returns
        -------
        Board
            A new board with the current player's piece at action.
        """
        current_player = self.player(state)

        # Step 1: Copy the immutable tuple into a mutable list
        new_board = list(state)

        # Step 2: Apply the move to the COPY, not the original
        new_board[action] = current_player

        # Step 3: Return as immutable tuple — safe for backtracking
        return tuple(new_board)

    def is_terminal(self, state: Board) -> bool:
        """
        Return True if the game is over at this state.

        A game ends in exactly two ways:
        1. A player has won (win_length pieces in a row)
        2. The board is full and nobody won (draw)

        We check for a winner FIRST, then for a full board.
        Order matters: a full board with a winning line is a WIN,
        not a draw. Checking fullness first would misclassify it.

        This is Minimax's base case — when this returns True,
        we stop recursing and call utility() to get the score.
        Without this stopping condition, Minimax recurses forever.

        Why delegate to _winner()?
        --------------------------
        Single Responsibility Principle at the method level.
        is_terminal() answers ONE question: "is the game over?"
        _winner() answers a different question: "who won?"
        Keeping them separate makes each method simpler and testable.

        Parameters
        ----------
        state : Board
            The current board state.

        Returns
        -------
        bool
            True if the game has ended (win or draw), False otherwise.
        """
        # Check win condition first
        if self._winner(state) is not None:
            return True

        # Check draw: no empty cells remain
        # all() returns True if every cell is non-zero
        return all(cell != 0 for cell in state)

    def utility(self, state: Board, player: int) -> float:
        """
        Return the numeric score of a terminal state for the given player.

        Convention:
            +1.0 → this player won
            -1.0 → this player lost
            0.0 → draw

        Why take player as an argument?
        --------------------------------
        The same terminal state means different things to different players.
        MIN winning is +1.0 for MIN but -1.0 for MAX.

        By passing player, this function answers correctly for whoever
        is asking — critical when Minimax alternates between MAX and MIN
        perspectives deep in the recursion tree.

        If we always scored from MAX's perspective, MIN would evaluate
        its own wins as -1.0 and actively avoid winning. The algorithm
        would be completely broken.

        Why integers for player?
        ------------------------
        Because +1 and -1 are already the scores. When winner == player,
        that player won → return 1.0. One comparison. No strings needed.
        This is the zero-sum property expressed directly in code.

        Important
        ---------
        Only call this when is_terminal(state) is True.
        Calling on a non-terminal state is undefined behavior —
        there is no meaningful score for an unfinished game.

        Parameters
        ----------
        state : Board
            A terminal game state.
        player : int
            +1 for MAX, -1 for MIN. Whose perspective are we scoring from?

        Returns
        -------
        float
            +1.0 (win), -1.0 (loss), or 0.0 (draw).
        """
        winner = self._winner(state)

        if winner is None:
            # No winner — board must be full → draw
            return 0.0

        # winner == player means THIS player won → +1.0
        # winner != player means THIS player lost → -1.0
        # Notice: no string comparison, no if/else for X vs O
        # The integer identity IS the score sign. Zero-sum math.
        return 1.0 if winner == player else -1.0

    def _winner(self, state: Board) -> Optional[int]:
        """
        Check if any player has won and return who it is.

        Uses the precomputed _winning_lines to check every
        possible winning line efficiently.

        The check is elegant: for each line of win_length cells,
        sum their values:
            +win_length → all cells are +1 → MAX won
            -win_length → all cells are -1 → MIN won
            anything else → no winner on this line

        This works because:
            MAX pieces = +1, MIN pieces = -1, empty = 0
            Three MAX in a row: 1+1+1 = 3 → abs(3) == 3 → MAX wins
            Three MIN in a row: -1-1-1 = -3 → abs(-3) == 3 → MIN wins
            Mixed line: sum between -2 and +2 → no winner

        Why Optional[int]?
        ------------------
        This function either finds a winner (+1 or -1) or finds
        nothing (None). Optional[int] is the honest type for
        "this might be an int, or it might be nothing."
        It forces callers to handle BOTH cases explicitly.

        Parameters
        ----------
        state : Board
            The board to check.

        Returns
        -------
        Optional[int]
            +1 if MAX won, -1 if MIN won, None if no winner yet.
        """

        for line in self._winning_lines:
            # Sum the values of all cells in this line
            line_sum = sum(state[i] for i in line)

            # abs(line_sum) == win_length means all cells
            # belong to the same player
            if abs(line_sum) == self.win_length:
                # Positive sum → MAX won (+1)
                # Negative sum → MIN won (-1)
                return 1 if line_sum > 0 else -1

        # Checked every line — no winner found
        return None

    def _compute_winning_lines(self) -> List[Tuple[int, ...]]:
        """
        Generate all winning lines for this board size and win length.

        A winning line is a tuple of cell indices that, if all filled
        by the same player, means that player won.

        We generate four types of lines:
        - Rows: horizontal windows sliding left to right
        - Columns: vertical windows sliding top to bottom
        - Diagonal ↘: top-left to bottom-right windows
        - Diagonal ↙: top-right to bottom-left windows

        Returns
        -------
        List[Tuple[int, ...]]
            All possible winning lines as index tuples.
        """
        lines = []
        size = self.size
        win = self.win_length
        # How many starting positions fit in one dimension?
        # e.g. size=4, win=3 → positions 0,1 → 2 starts
        starts = size - win + 1

        # --- Rows ---
        # For each row r, slide a window of length win across it.
        # Row r starts at index r*size. Column c gives offset c.
        # So cell at (r, c) = r*size + c
        for r in range(size):
            for c in range(starts):
                line = tuple(r * size + c + i for i in range(win))
                lines.append(line)

        # --- Columns ---
        # For each column c, slide a window of length win downward.
        # Cell at (r, c) = r*size + c
        for c in range(size):
            for r in range(starts):
                line = tuple((r + i) * size + c for i in range(win))
                lines.append(line)

        # --- Diagonal ↘ (top-left to bottom-right) ---
        # Cell at (r, c) = r*size + c
        # Window starts at (r, c), goes to (r+win-1, c+win-1)
        # Both r and c must have room: range(starts)
        for r in range(starts):
            for c in range(starts):
                line = tuple((r + i) * size + (c + i) for i in range(win))
                lines.append(line)

        # --- Diagonal ↙ (top-right to bottom-left) ---
        # Cell at (r, c) = r*size + c
        # Window starts at (r, c), goes to (r+win-1, c-win+1)
        # r needs room going down: range(starts)
        # c needs room going left: start from win-1 up to size-1
        for r in range(starts):
            for c in range(win - 1, size):
                line = tuple((r + i) * size + (c - i) for i in range(win))
                lines.append(line)

        return lines

    def display(self, state: Board) -> str:
        """
        Return a human-readable ASCII representation of the board.

        This method is NOT part of the AdversarialGame protocol.
        It exists purely as a debugging and demonstration utility.

        Strictly speaking, display logic should live in a separate
        class (like MazeRenderer in maze.py) following Single
        Responsibility Principle. Here we keep it inline because
        it's small enough that a separate class would be
        over-engineering — a real judgment call in practice.

        Parameters
        ----------
        state : Board
            The board state to display.

        Returns
        -------
        str
            ASCII representation of the board.

        Example
        -------
        >>> game = TicTacToe()
        >>> state = game.result(game.initial_state, 4)
        >>> print(game.display(state))
        . | . | .
        ---------
        . | X | .
        ---------
        . | . | .
        """

        # Map cell values to display symbols
        # 0 = empty, +1 = X (MAX), -1 = O (MIN)
        symbols = {0: ".", 1: "X", -1: "O"}

        rows = []
        for r in range(self.size):
            # Get symbols for each cell in this row
            start = r * self.size
            cells = [symbols[state[start + c]] for c in range(self.size)]
            rows.append(" | ".join(cells))

        # Join rows with a separator line
        separator = "-" * (self.size * 4 - 3)
        return f"\n{separator}\n".join(rows)
