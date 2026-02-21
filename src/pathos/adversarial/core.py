"""
Core definitions for Adversarial Games.

This module defines the AdversarialGame protocol that all
two-player, zero-sum games must implement.

Any game satisfying this protocol can be solved by Minimax,
Alpha-Beta Pruning, and MCTS without those algorithms knowing
anything about the specific game rules.

This follows the same pattern as pathos/csp/core.py:
domain-specific protocols live in their own module,
not in the global core.py.

SOLID Principles:
-----------------
S - Defines contract only. Does not solve anything.
O - Algorithms work with ANY game satisfying this. No changes needed.
L - TicTacToe, Chess, Connect4 are all substitutable here.
I - Only the methods adversarial algorithms actually need.
D - Minimax depends on THIS abstraction, never on concrete games.
"""

from typing import Iterable, Protocol, TypeVar, runtime_checkable

S = TypeVar("S")  # Game state (e.g. board as a tuple)
A = TypeVar("A")  # Action (e.g. cell index, chess move)


@runtime_checkable
class AdversarialGame(Protocol[S, A]):
    """
    Protocol defining what a two-player, zero-sum adversarial game must provide.

    This is the abstraction that Minimax, Alpha-Beta, and MCTS depend on.
    Any game implementing this protocol can be solved by our adversarial
    algorithms without those algorithms knowing anything about the game rules.

    This is Dependency Inversion Principle in its purest form:
    the algorithm (high-level) depends on this abstraction,
    not on TicTacToe or Chess (low-level concrete details).

    Why NOT reuse GoalOriented?
    ---------------------------
    GoalOriented asks: "did I reach THE goal?" — True or False.
    It assumes ONE agent, ONE objective, ONE goal state.

    AdversarialGame is fundamentally different:
    - TWO agents with OPPOSITE objectives
    - Multiple terminal states (win, loss, draw)
    - Need to know WHOSE TURN IT IS at every state
    - Terminal states have a numeric score, not just True/False

    Forcing games to implement is_goal() would be meaningless.
    Forcing mazes to implement player() would be absurd.
    That's exactly what Interface Segregation Principle prevents.

    The Zero-Sum Property:
    ----------------------
    In a zero-sum game, one player's gain is exactly the other's loss.
    utility(state, MAX) + utility(state, MIN) = 0, always.

    This is why we use +1 and -1 for BOTH player identity AND scores.
    The math and the identity speak the same language:
        - utility(state, player) == 1.0  means "this player won"
        - utility(state, player) == -1.0 means "this player lost"
    No string comparisons. No if/else for 'X' vs 'O'. Just math.

    Type Parameters:
    ----------------
    S : the type representing a game state (e.g. a board as a tuple)
    A : the type representing a legal action (e.g. a cell index)
    """

    @property
    def initial_state(self) -> S:
        """
        Return the starting state of the game.

        This is where every search begins — the empty board in
        TicTacToe, the opening position in Chess, etc.

        It is a @property because it describes WHAT the game is,
        not something you compute with arguments. Same pattern
        as initial_state in GoalOriented and SearchDomain.
        """
        ...

    def is_terminal(self, state: S) -> bool:
        """
        Return True if the game is over at this state.

        A game ends in two ways:
        - A player has satisfied the win condition (someone won)
        - No moves remain and nobody won (draw)

        This is Minimax's BASE CASE.
        When is_terminal() is True, we stop recursing and call
        utility() instead. Without this, the algorithm recurses forever.

        Think of it like the stopping condition in a while loop —
        absolutely critical to get right.

        Parameters
        ----------
        state : S
            The current game state to evaluate.

        Returns
        -------
        bool
            True if the game has ended, False if play continues.
        """
        ...

    def utility(self, state: S, player: int) -> float:
        """
        Return the numeric score of a terminal state for the given player.

        Convention used throughout Pathos:
            +1.0  → this player won
            -1.0  → this player lost
             0.0  → draw

        Why does this take `player` as an argument?
        --------------------------------------------
        The same terminal state means different things to different players.
        Consider: MIN just won the game.

            utility(state, player=+1) → -1.0  (MAX lost)
            utility(state, player=-1) → +1.0  (MIN won)

        Same board. Opposite scores. If we always scored from MAX's
        perspective, MIN would evaluate its OWN wins as -1.0 and
        actively avoid winning. The entire algorithm breaks.

        By passing `player`, the function answers correctly for
        whoever is asking — critical when Minimax alternates between
        MAX and MIN perspectives deep in the recursion tree.

        Why integers for player?
        ------------------------
        Because +1 and -1 are already the scores. When winner == player,
        that player won → return 1.0. One comparison. No strings.
        This is the zero-sum property expressed directly in code.

        Important
        ---------
        Only call this when is_terminal(state) is True.
        Calling on a non-terminal state is undefined behavior —
        there is no meaningful score for an unfinished game.

        Parameters
        ----------
        state : S
            A terminal game state.
        player : int
            +1 for MAX, -1 for MIN. Whose perspective are we scoring from?

        Returns
        -------
        float
            +1.0 (win), -1.0 (loss), or 0.0 (draw).
        """
        ...

    def player(self, state: S) -> int:
        """
        Return which player is to move in this state.

        Convention: +1 = MAX player, -1 = MIN player.

        Why derive from state rather than storing separately?
        -----------------------------------------------------
        We never store "whose turn it is" as an external variable.
        We DERIVE it from the board itself.

        In TicTacToe for example: count the pieces on the board.
        If MAX and MIN have equal pieces, MAX moves next (goes first).
        If MAX has one more piece than MIN, it's MIN's turn.

        This means the state is SELF-CONTAINED. The board alone tells
        you everything about the game at that moment. No external
        variables can get out of sync with the board. No bugs from
        forgetting to update "current player" after a move.

        This is a functional approach: same board → same player, always.

        Parameters
        ----------
        state : S
            The current game state.

        Returns
        -------
        int
            +1 if it is MAX's turn, -1 if it is MIN's turn.
        """
        ...

    def actions(self, state: S) -> Iterable[A]:
        """
        Return all legal moves available from this state.

        Why Iterable and not List?
        --------------------------
        Minimax only needs to LOOP over the actions — it never
        calls .append(), .pop(), or any list-specific method.

        Iterable is the minimum requirement: "I just need to loop
        over this." It works with lists, sets, tuples, generators —
        whatever the game implementer finds most natural.

        Constraining this to List would be an unnecessary restriction.
        A Chess engine might return a generator for memory efficiency.
        A TicTacToe implementation might return a list.
        Both work with Iterable. Neither works if we demand List.

        Parameters
        ----------
        state : S
            The current game state.

        Returns
        -------
        Iterable[A]
            All legal actions available from this state.
        """
        ...

    def result(self, state: S, action: A) -> S:
        """
        Apply an action and return the resulting NEW state.

        The word NEW is critical here.

        Why must this never modify the existing state?
        -----------------------------------------------
        Minimax explores branches and backtracks constantly.
        Imagine it explores branch A → C, then needs to backtrack
        and explore branch A → D. For that to work, the state after
        move A must still be intact — untouched by the C exploration.

        If result() modified the board in place, we'd need "undo"
        logic after every move — carefully reversing every change
        on backtrack. This is a classic source of subtle bugs.
        Miss one undo, and the entire search is silently corrupted.

        By returning a NEW state (e.g. a new tuple), the original
        is guaranteed untouched. Backtracking is free. No undo needed.
        No bugs. This is why we use immutable tuples for boards.

        Parameters
        ----------
        state : S
            The current game state.
        action : A
            The action to apply.

        Returns
        -------
        S
            A brand new state reflecting the action taken.
        """
        ...
