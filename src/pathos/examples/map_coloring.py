"""
Map Coloring Problem for Constraint Satisfaction.

This module implements a configurable map coloring CSP that follows
SOLID principles and works with any backtracking solver.

The Problem:
-----------
Color regions of a map using a limited set of colors such that
no two neighboring regions share the same color.

Default Example (Australia):
----------------------------
     NT
    ╱ │ ╲
  WA  │  Q
    ╲ │ ╱ ╲
      SA   NSW
       │  ╱
       V

       T (Tasmania - island, no neighbors)

Educational Value:
-----------------
This problem demonstrates:
- How to implement the CSP protocol
- How constraints are checked
- How MRV heuristic prioritizes constrained variables
- The power of backtracking vs brute force
- Open/Closed Principle in action

SOLID Principles Applied:
------------------------
- Single Responsibility: Defines ONLY map coloring problems
- Open/Closed: Configurable for ANY map without modification
- Liskov Substitution: Substitutable for CSP protocol
- Interface Segregation: Implements minimal CSP interface
- Dependency Inversion: Depends on CSP abstraction
"""

from typing import Dict, List, Optional, Set

from pathos.csp.core import Assignment


class MapColoringCSP:
    """
    Map Coloring as a Constraint Satisfaction Problem.

    This class implements the CSP protocol for ANY map coloring problem.
    It follows the Open/Closed Principle by accepting configuration parameters
    while providing sensible defaults (Australia map).

    This class implements the CSP protocol by providing:
    1. variables: The regions to color
    2. domains: The available colors for each region
    3. is_consistent: Check if neighboring regions have different colors

    SOLID Principles:
    ----------------
    - Open/Closed: Can create ANY map without modifying this class
    - Single Responsibility: Handles ONLY map coloring logic
    - Dependency Inversion: Implements CSP protocol abstraction

    Attributes
    ----------
    _variables : List[str]
        The regions to color
    _domains : Dict[str, List[str]]
        Available colors for each region
    _neighbors : Dict[str, Set[str]]
        Which regions border each other

    Example Usage
    -------------
    >>> # Default: Australia map with 3 colors
    >>> from pathos.csp.solvers import backtracking_search
    >>> australia = MapColoringCSP()
    >>> solution = backtracking_search(australia)
    >>>
    >>> # Custom: Different map with 4 colors
    >>> custom = MapColoringCSP(
    ...     regions=["R1", "R2", "R3", "R4"],
    ...     neighbors={
    ...         "R1": {"R2", "R3"},
    ...         "R2": {"R1", "R3", "R4"},
    ...         "R3": {"R1", "R2"},
    ...         "R4": {"R2"}
    ...     },
    ...     colors=["Red", "Green", "Blue", "Yellow"]
    ... )
    >>> solution = backtracking_search(custom)

    Educational Note:
    ----------------
    The default Australia map demonstrates:
    - SA (South Australia) is most constrained with 5 neighbors
    - MRV heuristic will prioritize SA after a few assignments
    - This demonstrates the fail-first principle in action!
    """

    def __init__(
        self,
        regions: Optional[List[str]] = None,
        neighbors: Optional[Dict[str, Set[str]]] = None,
        colors: Optional[List[str]] = None,
    ):
        """
        Initialize a map coloring problem.

        Follows the same pattern as Maze: configurable with sensible defaults.

        Parameters
        ----------
        regions : Optional[List[str]]
            List of region names to color.
            Default: Australia's 7 regions (WA, NT, SA, Q, NSW, V, T)
        neighbors : Optional[Dict[str, Set[str]]]
            Which regions share borders.
            Default: Australia's neighbor relationships
        colors : Optional[List[str]]
            Available colors for coloring.
            Default: 3 colors (Red, Green, Blue)

        Examples
        --------
        >>> # Use defaults (Australia map)
        >>> problem = MapColoringCSP()
        >>>
        >>> # Custom map with 4 colors
        >>> problem = MapColoringCSP(
        ...     regions=["A", "B", "C"],
        ...     neighbors={"A": {"B"}, "B": {"A", "C"}, "C": {"B"}},
        ...     colors=["Red", "Green", "Blue", "Yellow"]
        ... )

        SOLID Analysis:
        --------------
        This design follows Open/Closed Principle:
        - Open for extension: Create any map by passing parameters
        - Closed for modification: Don't need to change this class

        Compare to hardcoded approach:
        - Hardcoded: class AustraliaMapCSP (works ONLY for Australia)
        - Configurable: class MapColoringCSP (works for ANY map)
        """
        # --- VARIABLES: Default to Australia's 7 regions ---
        #
        # WA = Western Australia
        # NT = Northern Territory
        # SA = South Australia (most constrained! 5 neighbors)
        # Q = Queensland
        # NSW = New South Wales
        # V = Victoria
        # T = Tasmania (island, no neighbors)

        if regions is None:
            regions = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]

        self._variables: List[str] = regions

        # --- COLORS: Default to 3 colors (minimum for most maps) ---
        #
        # Why 3 colors? This is the minimum needed for map coloring!
        # (Four Color Theorem: Any planar map needs at most 4 colors)

        if colors is None:
            colors = ["Red", "Green", "Blue"]

        # --- DOMAINS: Each region can use any color ---
        #
        # We use a dict comprehension to create the same domain for all regions.

        self._domains: Dict[str, List[str]] = {
            region: colors.copy() for region in self._variables
        }

        # --- NEIGHBORS: Default to Australia's borders ---
        #
        # This defines our constraints!
        # Two regions are neighbors if they share a border.
        #
        # Constraint: neighbors cannot have the same color.
        #
        # Note: We define neighbors symmetrically:
        # If A is neighbor of B, then B is neighbor of A

        if neighbors is None:
            neighbors = {
                "WA": {"NT", "SA"},  # 2 neighbors
                "NT": {"WA", "SA", "Q"},  # 3 neighbors
                "SA": {"WA", "NT", "Q", "NSW", "V"},  # 5 neighbors (MOST!)
                "Q": {"NT", "SA", "NSW"},  # 3 neighbors
                "NSW": {"Q", "SA", "V"},  # 3 neighbors
                "V": {"SA", "NSW"},  # 2 neighbors
                "T": set(),  # 0 neighbors (island!)
            }

        self._neighbors: Dict[str, Set[str]] = neighbors

    # --- CSP Protocol Implementation ---

    @property
    def variables(self) -> List[str]:
        """
        Return all regions that need to be colored.

        Required by CSP protocol.

        Returns
        -------
        List[str]
            List of region names

        Example
        -------
        >>> problem = MapColoringCSP()
        >>> problem.variables
        ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
        """
        return self._variables

    @property
    def domains(self) -> Dict[str, List[str]]:
        """
        Return the available colors for each region.

        Required by CSP protocol.

        Returns
        -------
        Dict[str, List[str]]
            Mapping of each region to its available colors

        Example
        -------
        >>> problem = MapColoringCSP()
        >>> problem.domains["SA"]
        ['Red', 'Green', 'Blue']
        """
        return self._domains

    def is_consistent(
        self, variable: str, value: str, assignment: Assignment[str, str]
    ) -> bool:
        """
        Check if assigning a color to a region violates neighbor constraints.

        Required by CSP protocol.

        The Constraint:
        --------------
        A region cannot have the same color as any of its neighbors.

        Algorithm:
        ---------
        1. Get the neighbors of the variable (region)
        2. For each neighbor that's already been assigned a color:
           a. If neighbor has the same color we want → CONFLICT!
           b. Return False
        3. If we check all neighbors without conflicts → OK!
           Return True

        Parameters
        ----------
        variable : str
            The region we want to color (e.g., "SA")
        value : str
            The color we want to assign (e.g., "Red")
        assignment : Assignment[str, str]
            Current partial coloring (e.g., {"WA": "Red", "NT": "Green"})

        Returns
        -------
        bool
            True if this assignment doesn't violate constraints,
            False if it conflicts with a neighbor

        Example
        -------
        >>> problem = MapColoringCSP()
        >>> assignment = {"WA": "Red", "NT": "Green"}
        >>>
        >>> # Try to color SA red
        >>> problem.is_consistent("SA", "Red", assignment)
        False  # SA's neighbor WA is already Red!
        >>>
        >>> # Try to color SA blue
        >>> problem.is_consistent("SA", "Blue", assignment)
        True  # No conflicts! Blue is OK for SA

        Educational Trace:
        -----------------
        Let's trace through SA = Red with assignment = {"WA": "Red"}:

        1. neighbors of SA = {"WA", "NT", "Q", "NSW", "V"}
        2. Check each neighbor:
           - "WA" in assignment? YES
             assignment["WA"] = "Red"
             value = "Red"
             "Red" == "Red"? YES → CONFLICT! Return False

        We stop immediately when we find a conflict!
        This is the "early constraint checking" that makes backtracking fast.
        """
        # --- Step 1: Get this region's neighbors ---
        #
        # Example: If variable = "SA"
        # neighbors = {"WA", "NT", "Q", "NSW", "V"}

        neighbors = self._neighbors[variable]

        # --- Step 2: Check each neighbor for conflicts ---
        #
        # We only check neighbors that have ALREADY been assigned.
        # Unassigned neighbors can't conflict (they don't have colors yet!)

        for neighbor in neighbors:
            # Has this neighbor been assigned a color yet?
            if neighbor in assignment:
                # Does the neighbor have the SAME color we want?
                if assignment[neighbor] == value:
                    # CONFLICT! This color violates the constraint
                    # Example:
                    # - neighbor = "WA", assignment["WA"] = "Red"
                    # - value = "Red"
                    # - "Red" == "Red" → True → CONFLICT!
                    return False

        # --- Step 3: No conflicts found ---
        #
        # If we reach here, we checked ALL assigned neighbors
        # and NONE of them have the same color.
        # This assignment is valid!

        return True


# --- Visualization Helper (Following Open/Closed Principle) ---


def print_solution(
    solution: Optional[Assignment[str, str]],
    region_names: Optional[Dict[str, str]] = None,
) -> None:
    """
    Pretty-print a solution to any map coloring problem.

    This function now follows Open/Closed Principle:
    - Works with ANY map (not just Australia)
    - Accepts optional region name mappings
    - Uses solution keys dynamically (no hardcoding)

    This is NOT part of the CSP protocol - it's just a helper function
    for displaying results in a human-readable format.

    Parameters
    ----------
    solution : Optional[Assignment[str, str]]
        The complete color assignment, or None if no solution
    region_names : Optional[Dict[str, str]]
        Mapping of region codes to full names for display.
        Default: Australia region names

        Example: {"CA": "California", "NY": "New York"}

    Examples
    --------
    >>> # Australia map (uses default names)
    >>> problem = MapColoringCSP()
    >>> solution = backtracking_search(problem)
    >>> print_solution(solution)
    Map Coloring Solution:
    ========================================
    NSW (New South Wales   ): Green
    NT  (Northern Territory): Green
    ...

    >>> # Custom map with custom names
    >>> custom = MapColoringCSP(
    ...     regions=["CA", "NY", "TX"],
    ...     neighbors={"CA": set(), "NY": {"TX"}, "TX": {"NY"}},
    ...     colors=["Red", "Blue"]
    ... )
    >>> solution = backtracking_search(custom)
    >>> print_solution(solution, {"CA": "California", "NY": "New York", "TX": "Texas"})
    Map Coloring Solution:
    ========================================
    CA  (California        ): Red
    NY  (New York          ): Red
    TX  (Texas             ): Blue

    SOLID Improvement:
    -----------------
    Previous version hardcoded Australia regions (violated OCP).
    This version works with ANY map (follows OCP).
    """
    if solution is None:
        print("No solution found!")
        return

    # --- Default to Australia region names if not provided ---
    #
    # This provides convenience while maintaining flexibility

    if region_names is None:
        region_names = {
            "WA": "Western Australia",
            "NT": "Northern Territory",
            "SA": "South Australia",
            "Q": "Queensland",
            "NSW": "New South Wales",
            "V": "Victoria",
            "T": "Tasmania",
        }

    # --- Print header ---

    print("\nMap Coloring Solution:")
    print("=" * 40)

    # --- Print each region's color ---
    #
    # Key improvement: Iterate over solution.keys() (dynamic)
    # Not hardcoded list (static)
    #
    # This makes the function work with ANY map!

    for region in sorted(solution.keys()):
        color = solution[region]
        # Get full name if available, otherwise use region code
        full_name = region_names.get(region, region)
        print(f"{region:4} ({full_name:20}): {color}")


# --- Convenience Functions ---


def australia_map() -> MapColoringCSP:
    """
    Create the classic Australia map coloring problem.

    This is a convenience function that returns a MapColoringCSP
    configured with Australia's regions, neighbors, and 3 colors.

    It's equivalent to calling MapColoringCSP() with no arguments,
    but more explicit about what problem you're creating.

    Returns
    -------
    MapColoringCSP
        Australia map with 7 regions and 3 colors

    Example
    -------
    >>> from pathos.csp.solvers import backtracking_search
    >>> problem = australia_map()
    >>> solution = backtracking_search(problem)
    >>> print_solution(solution)

    SOLID Note:
    ----------
    This pattern (convenience function + configurable class) gives us:
    - Ease of use: australia_map() is simple and clear
    - Flexibility: MapColoringCSP(...) for custom maps
    - Best of both worlds!
    """
    return MapColoringCSP()  # Uses default Australia configuration


# --- Educational Note: Why This Design? ---
"""
This module demonstrates several key software engineering principles:

1. **Open/Closed Principle (The Main Achievement!)**
   - BEFORE: Hardcoded AustraliaMapCSP class
     → Can ONLY solve Australia
     → Need to create NEW class for different map

   - AFTER: Configurable MapColoringCSP class
     → Can solve ANY map via parameters
     → No modification needed for new maps

2. **Single Responsibility Principle**
   - MapColoringCSP: Defines map problems
   - backtracking_search: Solves CSP problems
   - print_solution: Displays solutions
   - Each has ONE job!

3. **Dependency Inversion Principle**
   - MapColoringCSP depends on CSP protocol (abstraction)
   - Solver depends on CSP protocol (abstraction)
   - They don't know about each other's internals!

4. **Interface Segregation Principle**
   - CSP protocol has ONLY what's needed: variables, domains, is_consistent
   - No bloat, no unnecessary methods

5. **Liskov Substitution Principle**
   - Any MapColoringCSP can substitute for CSP protocol
   - Solver doesn't care if it's Australia, US, or custom map

Real-World Benefits:
-------------------
- Want to color a US state map? Just pass different parameters!
- Want to solve N-Queens? Implement CSP protocol differently!
- Want to visualize differently? Change print_solution!
- Want a better solver? Keep MapColoringCSP, write new solver!

This is what "maintainable, extensible code" means in practice.

Alternative CSP Problems (all use the SAME solver!):
----------------------------------------------------
- N-Queens: Place N queens on chessboard (no attacks)
- Sudoku: Fill grid with numbers (row/column/box constraints)
- Graph Coloring: Color any graph (no adjacent nodes same color)
- Scheduling: Assign time slots (no conflicts)
- Register Allocation: Assign CPU registers (compiler optimization)

The power of abstraction! 🚀
"""
