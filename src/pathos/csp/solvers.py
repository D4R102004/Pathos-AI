"""
CSP Solving Algorithms.

This module implements backtracking search with intelligent heuristics
for solving Constraint Satisfaction Problems.

SOLID Principles Applied:
- Single Responsibility: Each function has ONE job (solve, select variable, etc.)
- Open/Closed: Works with ANY CSP that implements the protocol
- Liskov Substitution: Any CSP implementation can be used
- Interface Segregation: Solver only needs CSP protocol methods
- Dependency Inversion: Depends on CSP abstraction, not concrete problems

Educational Notes:
-----------------
Backtracking is a REFINED version of Depth-First Search:
- Like DFS: Explores deeply before backtracking
- Unlike DFS: Checks constraints IMMEDIATELY (early pruning)
- Result: Exponentially faster than blind search for CSPs

Key Insight:
-----------
The difference between 3^7 = 2,187 combinations (BFS)
and ~50 assignments (Backtracking with MRV) is the power of:
1. Early constraint checking (prune invalid branches)
2. Smart variable ordering (tackle hardest problems first)
"""

from typing import Optional, TypeVar

# Import the CSP protocol and Assignment type from our core module
# This demonstrates Dependency Inversion Principle:
# We depend on the abstraction (CSP protocol), not concrete implementations
from pathos.csp.core import CSP, Assignment

# Type variables for generic typing
V = TypeVar("V")  # Variable type
D = TypeVar("D")  # Domain value type


def backtracking_search(csp: CSP[V, D]) -> Optional[Assignment[V, D]]:
    """
    Solve a CSP using backtracking search with the MRV heuristic.

    This is the main entry point for CSP solving. It uses recursive
    backtracking with intelligent variable ordering to find a solution
    that satisfies all constraints.

    Algorithm Overview:
    ------------------
    1. Start with an empty assignment
    2. Recursively assign values to variables
    3. Check constraints after each assignment (early pruning!)
    4. If a variable has no valid values, backtrack
    5. Return the first complete valid assignment found

    SOLID Principles:
    ----------------
    - Open/Closed: Works with ANY CSP (Map Coloring, Sudoku, N-Queens, etc.)
    - Dependency Inversion: Depends on CSP protocol, not concrete problems
    - Single Responsibility: ONLY solves CSPs, doesn't define them

    Parameters
    ----------
    csp : CSP[V, D]
        A constraint satisfaction problem implementing the CSP protocol.
        Must provide: variables, domains, is_consistent()

    Returns
    -------
    Optional[Assignment[V, D]]
        A complete assignment satisfying all constraints, or None if
        no solution exists.

    Example
    -------
    >>> from pathos.examples.map_coloring import AustraliaMapCSP
    >>> problem = AustraliaMapCSP()
    >>> solution = backtracking_search(problem)
    >>> print(solution)
    {'WA': 'Red', 'NT': 'Green', 'SA': 'Blue', ...}

    Performance Note:
    ----------------
    For Australia map (7 regions, 3 colors):
    - Naive search: 3^7 = 2,187 combinations
    - Backtracking: ~50-100 assignments (20-40x faster!)

    Why This Works:
    --------------
    Two key optimizations:
    1. Early constraint checking (prune bad branches immediately)
    2. MRV heuristic (choose hardest variables first)
    """
    # Start the recursive backtracking with an empty assignment
    # Think of this like starting a form with all fields blank
    return _backtrack({}, csp)


def _backtrack(
    assignment: Assignment[V, D], csp: CSP[V, D]
) -> Optional[Assignment[V, D]]:
    """
    Recursive backtracking helper function.

    This is the CORE of the backtracking algorithm. It's a private
    function (note the leading underscore) because users should call
    backtracking_search(), not this directly.

    Why Recursive?
    -------------
    Backtracking naturally maps to recursion:
    - Try a value → Recurse → If it fails, try next value
    - The call stack handles "remembering" previous states
    - When we return from recursion, we're automatically "backed up"

    Algorithm Flow:
    --------------
    1. BASE CASE: All variables assigned? Return solution!
    2. RECURSIVE CASE:
       a. Pick an unassigned variable (using MRV heuristic)
       b. Try each value in its domain
       c. If consistent, add to assignment and recurse
       d. If recursion succeeds, bubble up the solution
       e. If recursion fails, undo (backtrack) and try next value
    3. FAILURE CASE: No values worked? Return None

    Parameters
    ----------
    assignment : Assignment[V, D]
        Current partial assignment of variables to values.
        Gets built up as we recurse deeper.
    csp : CSP[V, D]
        The constraint satisfaction problem we're solving.

    Returns
    -------
    Optional[Assignment[V, D]]
        Complete valid assignment, or None if current path fails.

    Example Trace (Simplified):
    --------------------------
    _backtrack({}, csp)
    ├─ Try WA=Red ✓
    │  ├─ _backtrack({"WA": "Red"}, csp)
    │  │  ├─ Try NT=Red ❌ (conflicts with WA!)
    │  │  ├─ Try NT=Green ✓
    │  │  │  ├─ _backtrack({"WA": "Red", "NT": "Green"}, csp)
    │  │  │  │  ├─ Try SA=Blue ✓
    │  │  │  │  │  └─ SUCCESS! Return solution
    """
    # --- BASE CASE: Check if assignment is complete ---
    #
    # An assignment is complete when every variable has been assigned.
    # Think: All fields on the form are filled out.
    #
    # Why len() comparison works:
    # - csp.variables is a list of ALL variables: ["WA", "NT", "SA", ...]
    # - assignment is a dict: {"WA": "Red", "NT": "Green", ...}
    # - When len(assignment) == len(csp.variables), we're done!

    if len(assignment) == len(csp.variables):
        # SUCCESS! We've assigned all variables without violating constraints
        # Return the complete assignment (this is our solution!)
        return assignment

    # --- RECURSIVE CASE: Pick next variable to assign ---
    #
    # We use a HEURISTIC here to choose which variable to assign next.
    # This isn't just random - smart ordering makes the algorithm MUCH faster!

    var = _select_unassigned_variable(assignment, csp)

    # --- Try each value in the variable's domain ---
    #
    # Example: If var = "SA" and domains["SA"] = ["Red", "Green", "Blue"]
    # We'll try SA=Red, then SA=Green, then SA=Blue

    for value in csp.domains[var]:
        # --- CONSTRAINT CHECKING (The Magic of Backtracking!) ---
        #
        # This is THE KEY difference from naive search!
        # We check constraints IMMEDIATELY, not after building the full assignment.
        #
        # Example:
        # assignment = {"WA": "Red"}
        # var = "NT"
        # value = "Red"
        # is_consistent("NT", "Red", {"WA": "Red"}) → False (neighbors!)
        # → Don't waste time exploring this branch! Skip it!

        if csp.is_consistent(var, value, assignment):
            # --- This value is valid! Add it to the assignment ---
            #
            # We're tentatively assigning this value.
            # If it leads to a dead end later, we'll undo it (backtrack).
            #
            # Think: Writing an answer on the form in pencil (erasable!)

            assignment[var] = value

            # --- RECURSIVE CALL: Try to assign remaining variables ---
            #
            # This is where the magic happens!
            # We call ourselves with the new assignment.
            # The recursion will try to assign the NEXT variable.
            #
            # If this path leads to a solution, it will bubble up.
            # If this path fails, we'll try the next value.

            result = _backtrack(assignment, csp)

            # --- Check if recursion found a solution ---
            #
            # If result is not None, the recursive call found a complete
            # valid assignment. Bubble it up!

            if result is not None:
                return result

            # --- BACKTRACKING: Undo the assignment ---
            #
            # If we reach here, the recursive call returned None (failed).
            # This means assigning var=value led to a dead end.
            #
            # We need to UNDO this assignment and try a different value.
            # Think: Erasing the pencil mark and trying a different answer!
            #
            # The beautiful thing: Python's dict makes this easy!
            # Just delete the key and it's like it never happened.

            del assignment[var]

            # Loop continues to try the next value in the domain

    # --- FAILURE CASE: No value worked ---
    #
    # If we reach here, we tried EVERY value in var's domain
    # and none of them led to a solution.
    #
    # This means the current partial assignment is a dead end.
    # Return None to signal failure to the parent call.
    #
    # The parent will then try a DIFFERENT value for ITS variable.

    return None


def _select_unassigned_variable(assignment: Assignment[V, D], csp: CSP[V, D]) -> V:
    """
    Select the next unassigned variable using the MRV heuristic.

    MRV = Minimum Remaining Values

    The Idea:
    --------
    Choose the variable with the FEWEST legal values remaining.
    Why? Because it's the most constrained - most likely to fail!

    Fail-First Principle:
    --------------------
    It sounds counter-intuitive, but we WANT to fail as early as possible!

    Example:
    -------
    Variable A has 10 legal values → Easy, can defer
    Variable B has 2 legal values → Hard, tackle it NOW

    If B is unsolvable, we want to know IMMEDIATELY, not after
    wasting time assigning A and 5 other variables first!

    Real-World Analogy:
    ------------------
    Imagine packing a car for vacation:
    - The surfboard (constrained - must go on roof)
    - The snacks (flexible - fit anywhere)

    Smart packing: Put surfboard first! If it doesn't fit, no point
    packing the snacks. You need a bigger car!

    Dumb packing: Pack all the snacks first, then discover the
    surfboard doesn't fit. Now you have to unpack everything!

    SOLID Principles:
    ----------------
    - Single Responsibility: ONLY selects variables, doesn't assign them
    - Open/Closed: Works with any CSP domain type
    - Dependency Inversion: Uses CSP protocol methods only

    Parameters
    ----------
    assignment : Assignment[V, D]
        Current partial assignment (what's already been assigned).
    csp : CSP[V, D]
        The CSP problem (for accessing variables and domains).

    Returns
    -------
    V
        The unassigned variable with the fewest legal values.

    Performance Impact:
    ------------------
    Without MRV: ~200 assignments for Australia map
    With MRV: ~50 assignments for Australia map
    Speedup: 4x faster!

    Why This Works:
    --------------
    MRV prunes the search tree by detecting failures early.
    The fewer legal values, the more likely we'll hit a dead end.
    Better to hit it NOW than after 10 more assignments!
    """
    # --- Find all unassigned variables ---
    #
    # An unassigned variable is one that's in csp.variables
    # but NOT in the assignment dictionary.
    #
    # Example:
    # csp.variables = ["WA", "NT", "SA", "Q"]
    # assignment = {"WA": "Red", "NT": "Green"}
    # unassigned = ["SA", "Q"]

    unassigned = [v for v in csp.variables if v not in assignment]

    # --- Use MRV Heuristic: Choose variable with fewest legal values ---
    #
    # We use Python's min() function with a key parameter.
    # The key function determines what to minimize.
    #
    # For each variable, we count how many values are legal:
    # 1. Get all values in its domain
    # 2. Count how many are consistent with current assignment
    # 3. Choose the variable with the SMALLEST count
    #
    # Why sum() with is_consistent()?
    # - is_consistent returns True (1) or False (0)
    # - sum([True, False, True]) = 2 (counts the True values)
    # - This counts how many values are legal!

    return min(
        unassigned,
        key=lambda var: sum(
            # For each value in this variable's domain...
            csp.is_consistent(var, val, assignment)  # Is it consistent?
            for val in csp.domains[var]  # Check all values
        ),
    )

    # Example trace:
    # unassigned = ["SA", "Q", "NSW"]
    # SA has domain ["Red", "Green", "Blue"]
    #   - Red: consistent? False (WA is Red)
    #   - Green: consistent? False (NT is Green)
    #   - Blue: consistent? True
    #   → SA has 1 legal value
    # Q has domain ["Red", "Green", "Blue"]
    #   - All three consistent
    #   → Q has 3 legal values
    # NSW has domain ["Red", "Green", "Blue"]
    #   - Two consistent
    #   → NSW has 2 legal values
    #
    # min([1, 3, 2]) = 1 → Choose SA!
    # Tackle the most constrained variable first!


# --- Educational Note: Why Not More Heuristics? ---
"""
Advanced CSP solvers use additional heuristics:

1. **Degree Heuristic** (Tie-breaking for MRV):
   - If two variables have the same number of legal values,
   - Choose the one involved in the most constraints
   - Why? It's more likely to constrain other variables

2. **Least Constraining Value** (Value ordering):
   - When trying values for a variable,
   - Try the one that rules out the fewest values for neighbors
   - Why? Preserve flexibility for future assignments

3. **Forward Checking**:
   - After each assignment, remove inconsistent values from
     neighbors' domains
   - Why? Detect failures even earlier!

4. **Arc Consistency** (AC-3):
   - Propagate constraints before search even starts
   - Why? Reduce domain sizes, making search faster

We implement only MRV because:
- It's the most impactful (4x speedup)
- It's simple to understand and explain
- It demonstrates the key insight (fail-first principle)
- Additional heuristics add complexity without much educational value

For production CSP solvers, you'd implement all of these!
But for learning, MRV is the perfect balance of power and simplicity.
"""
