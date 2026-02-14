"""
Core definitions for Constraint Satisfaction Problems (CSP).

This module defines the foundational Protocol and classes for CSP solving.

SOLID Principles Applied:
- Single Responsibility: CSP defines problems, Solver solves them (separate!)
- Open/Closed: Protocol allows new CSP types without modifying solvers
- Liskov Substitution: Any CSP implementation can substitute for the protocol
- Interface Segregation: CSP protocol contains only what solvers need
- Dependency Inversion: Solvers depend on CSP abstraction, not concrete problems

Educational Notes:
-----------------
CSPs are DIFFERENT from Search Problems:
- Search: "Find a path from A to B" (navigation)
- CSP: "Find an assignment satisfying all constraints" (satisfaction)

Example CSPs:
- Map Coloring: Assign colors to regions (no adjacent regions same color)
- Sudoku: Fill grid with numbers (satisfy row/column/box constraints)
- N-Queens: Place queens on chessboard (no two queens attack each other)
"""

from typing import Dict, List, Protocol, TypeVar, runtime_checkable

# --- Type Variables ---
# V = Variable (what we're assigning to: "WA", "NT", "Cell_1_1", etc.)
# D = Domain value (what we assign: "Red", "Green", 5, etc.)

V = TypeVar("V")  # Variable type (usually str, but could be tuple, etc.)
D = TypeVar("D")  # Domain value type (str, int, etc.)


# --- The Assignment Type ---
# An Assignment is a mapping from variables to their assigned values.
# Example: {"WA": "Red", "NT": "Green", "SA": "Blue"}
#
# This is a PARTIAL assignment during search.
# When all variables are assigned, it becomes a COMPLETE assignment (solution).

Assignment = Dict[V, D]


# --- The CSP Protocol ---


@runtime_checkable
class CSP(Protocol[V, D]):
    """
    Protocol defining what a Constraint Satisfaction Problem must provide.

    This is the ABSTRACTION that solvers depend on (Dependency Inversion Principle).

    Any problem that implements this protocol can be solved by our CSP solvers,
    WITHOUT the solver knowing anything about the specific problem.

    Required Components
    -------------------
    1. variables: List of all variables to assign
    2. domains: Possible values for each variable
    3. is_consistent: Check if an assignment violates constraints

    Why Protocol Instead of Base Class?
    -----------------------------------
    - More flexible: Problems can inherit from other classes
    - Duck typing: If it walks like a CSP and quacks like a CSP, it IS a CSP
    - No forced inheritance: Follows Composition over Inheritance principle
    - Same pattern as our SearchDomain protocol (consistency!)
    """

    @property
    def variables(self) -> List[V]:
        """
        Return all variables that need to be assigned.

        Example (Map Coloring):
            ["WA", "NT", "SA", "Q", "NSW", "V", "T"]

        Example (Sudoku):
            [(0,0), (0,1), ..., (8,8)]  # All 81 cells
        """
        ...

    @property
    def domains(self) -> Dict[V, List[D]]:
        """
        Return the domain (possible values) for each variable.

        Example (Map Coloring):
            {
                "WA": ["Red", "Green", "Blue"],
                "NT": ["Red", "Green", "Blue"],
                ...
            }

        Example (Sudoku):
            {
                (0,0): [1, 2, 3, 4, 5, 6, 7, 8, 9],
                (0,1): [1, 2, 3, 4, 5, 6, 7, 8, 9],
                ...
            }

        Note: Domains can be modified during search (domain reduction).
        """
        ...

    def is_consistent(
        self, variable: V, value: D, assignment: Assignment[V, D]
    ) -> bool:
        """
        Check if assigning {variable = value} is consistent with current assignment.

        This is THE CORE of CSP solving!

        Returns True if:
        - Assigning variable=value doesn't violate any constraints
        - Given the current partial assignment

        Returns False if:
        - This assignment would violate at least one constraint

        Parameters
        ----------
        variable : V
            The variable we want to assign
        value : D
            The value we want to assign to it
        assignment : Assignment[V, D]
            Current partial assignment of OTHER variables

        Returns
        -------
        bool
            True if assignment is valid, False otherwise

        Example (Map Coloring)
        ----------------------
        Current assignment: {"WA": "Red"}
        Check: is_consistent("NT", "Red", {"WA": "Red"})

        Logic:
        - NT is a neighbor of WA
        - WA is Red
        - NT wants to be Red
        - Same color for neighbors? VIOLATION!
        - Return: False

        Example (Sudoku)
        ----------------
        Current assignment: {(0,0): 5, (0,1): 3}
        Check: is_consistent((0,2), 5, {(0,0): 5, (0,1): 3})

        Logic:
        - Cell (0,2) wants value 5
        - Cell (0,0) already has 5 (same row!)
        - Duplicate in row? VIOLATION!
        - Return: False

        Why This Design?
        ----------------
        This method embodies:
        - Single Responsibility: ONLY checks consistency, doesn't solve
        - Open/Closed: Each CSP defines its OWN constraints
        - Dependency Inversion: Solver calls this WITHOUT knowing constraint details
        """
        ...


# --- Educational Note: Why Not Include Constraints Explicitly? ---
"""
You might wonder: "Why don't we have a 'constraints' attribute?"

We COULD design it like:
    constraints: List[Constraint]

But we chose the is_consistent() method instead. Here's why:

Option A (Explicit Constraints):
    constraints = [
        ("WA", "NT", lambda a, b: a != b),
        ("WA", "SA", lambda a, b: a != b),
        ...
    ]

    Pros: Clear, declarative
    Cons:
    - Limited to binary constraints (two variables)
    - Harder to express complex constraints
    - Solver must interpret constraint format

Option B (is_consistent method):
    def is_consistent(self, var, val, assignment):
        # Custom logic for THIS problem
        if var == "NT" and "WA" in assignment:
            return val != assignment["WA"]
        ...

    Pros:
    - Can express ANY constraint (binary, ternary, global, etc.)
    - Problem-specific optimization
    - Clean interface for solver
    Cons:
    - Less declarative (but more flexible!)

We chose Option B following:
- Open/Closed: Each problem can implement constraints its own way
- Single Responsibility: is_consistent() has ONE job
- Flexibility: Works for simple AND complex constraints
"""
