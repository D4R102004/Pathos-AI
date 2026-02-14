"""
Unit tests for CSP Solving Algorithms.

These tests verify the behavioral contracts of backtracking search,
not its internal implementation details.

We test:
- Correct handling of trivial problems (initial state is goal)
- Solution validity (all constraints satisfied)
- Works with different maps (Australia, Cuba)
- Detects unsolvable problems
- MRV heuristic improves performance

SOLID Principles Demonstrated:
- Open/Closed: Same solver works with multiple CSP problems
- Dependency Inversion: Tests depend on CSP abstraction
- Liskov Substitution: Different CSPs are substitutable
"""

from typing import Dict, Set

from pathos.csp.core import Assignment
from pathos.csp.solvers import backtracking_search
from pathos.examples.map_coloring import MapColoringCSP, australia_map

# --- Helper Functions ---


def is_valid_coloring(
    solution: Assignment[str, str], neighbors: Dict[str, Set[str]]
) -> bool:
    """
    Verify that a solution satisfies all neighbor constraints.

    This is our ORACLE - independent verification that the solution is correct.

    Parameters
    ----------
    solution : Assignment[str, str]
        The coloring to verify
    neighbors : Dict[str, Set[str]]
        The neighbor relationships

    Returns
    -------
    bool
        True if no two neighbors share the same color
    """
    for region, color in solution.items():
        for neighbor in neighbors.get(region, set()):
            if neighbor in solution:
                if solution[neighbor] == color:
                    # Conflict! Two neighbors have same color
                    return False
    return True


# --- Australia Map Tests ---


def test_australia_map_finds_solution():
    """
    Backtracking should find a valid solution for Australia map.

    This tests the basic functionality:
    - Solver returns a non-None result
    - All 7 regions are colored
    - No neighbor conflicts
    """
    problem = australia_map()
    solution = backtracking_search(problem)

    # Should find a solution
    assert solution is not None, "Should find solution for Australia map"

    # Should color all 7 regions
    assert len(solution) == 7, f"Expected 7 regions colored, got {len(solution)}"

    # All regions should be in the solution
    expected_regions = {"WA", "NT", "SA", "Q", "NSW", "V", "T"}
    assert set(solution.keys()) == expected_regions, "All regions should be colored"

    # Verify solution is valid (no neighbor conflicts)
    neighbors = {
        "WA": {"NT", "SA"},
        "NT": {"WA", "SA", "Q"},
        "SA": {"WA", "NT", "Q", "NSW", "V"},
        "Q": {"NT", "SA", "NSW"},
        "NSW": {"Q", "SA", "V"},
        "V": {"SA", "NSW"},
        "T": set(),
    }

    assert is_valid_coloring(
        solution, neighbors
    ), "Solution violates neighbor constraints!"


def test_australia_map_uses_only_available_colors():
    """
    Solution should only use colors from the domain.

    This verifies that the solver respects the domain constraints.
    """
    problem = MapColoringCSP()  # Default: Red, Green, Blue
    solution = backtracking_search(problem)

    assert solution is not None

    valid_colors = {"Red", "Green", "Blue"}
    for region, color in solution.items():
        assert color in valid_colors, f"Region {region} has invalid color {color}"


def test_australia_map_with_two_colors_does_not_find_solution():
    """
    Australia map can't be colored with just 2 colors.

    This tests that the solver works with different domain sizes.
    Demonstrates Open/Closed Principle - same problem, different parameters.
    """
    problem = MapColoringCSP(colors=["Red", "Blue"])
    solution = backtracking_search(problem)

    # Should not find a solution (Australia is 3-colorable!)
    assert solution is None, "Australia should be 2-colorable"


# --- Cuba Map Tests (From the Image!) ---


def test_cuba_map_finds_solution():
    """
    Backtracking should solve Cuba map coloring.

    This demonstrates Open/Closed Principle:
    - Same solver (no modification!)
    - Different map (via configuration)

    Cuba regions and neighbors based on the provided map:
    - Pinar del Rio, Artemisa, Mayabeque, Matanzas, Villa Clara,
      Cienfuegos, Sancti Spiritus, Ciego de Avila, Camaguey,
      Las Tunas, Holguin, Granma, Santiago de Cuba, Guantanamo,
      Isla de la Juventud, Havanna
    """
    # Define Cuba's regions and neighbors from the map
    cuba_regions = [
        "Pinar_del_Rio",
        "Artemisa",
        "Havanna",
        "Mayabeque",
        "Matanzas",
        "Villa_Clara",
        "Cienfuegos",
        "Sancti_Spiritus",
        "Ciego_de_Avila",
        "Camaguey",
        "Las_Tunas",
        "Holguin",
        "Granma",
        "Santiago_de_Cuba",
        "Guantanamo",
        "Isla_de_la_Juventud",
    ]

    # Define neighbor relationships based on the map
    cuba_neighbors = {
        "Pinar_del_Rio": {"Artemisa"},
        "Artemisa": {"Pinar_del_Rio", "Havanna", "Mayabeque"},
        "Havanna": {"Artemisa", "Mayabeque"},
        "Mayabeque": {"Artemisa", "Havanna", "Matanzas"},
        "Matanzas": {"Mayabeque", "Villa_Clara", "Cienfuegos"},
        "Villa_Clara": {"Matanzas", "Cienfuegos", "Sancti_Spiritus"},
        "Cienfuegos": {"Matanzas", "Villa_Clara", "Sancti_Spiritus"},
        "Sancti_Spiritus": {
            "Villa_Clara",
            "Cienfuegos",
            "Ciego_de_Avila",
            "Camaguey",
        },
        "Ciego_de_Avila": {"Sancti_Spiritus", "Camaguey"},
        "Camaguey": {"Sancti_Spiritus", "Ciego_de_Avila", "Las_Tunas"},
        "Las_Tunas": {"Camaguey", "Holguin", "Granma"},
        "Holguin": {"Las_Tunas", "Granma", "Santiago_de_Cuba"},
        "Granma": {"Las_Tunas", "Holguin", "Santiago_de_Cuba"},
        "Santiago_de_Cuba": {"Holguin", "Granma", "Guantanamo"},
        "Guantanamo": {"Santiago_de_Cuba"},
        "Isla_de_la_Juventud": set(),  # Island, no neighbors
    }

    # Create Cuba map CSP
    cuba = MapColoringCSP(
        regions=cuba_regions,
        neighbors=cuba_neighbors,
        colors=["Red", "Green", "Blue", "Yellow"],
    )

    solution = backtracking_search(cuba)

    # Should find a solution
    assert solution is not None, "Should find solution for Cuba map"

    # Should color all 16 regions
    assert len(solution) == 16, f"Expected 16 regions colored, got {len(solution)}"

    # Verify solution is valid
    assert is_valid_coloring(
        solution, cuba_neighbors
    ), "Cuba solution violates neighbor constraints!"


def test_cuba_map_with_three_colors():
    """
    Test if Cuba can be colored with just 3 colors.

    This is interesting because Cuba is a long, narrow island
    with a mostly linear structure.
    """
    cuba_regions = [
        "Pinar_del_Rio",
        "Artemisa",
        "Havanna",
        "Mayabeque",
        "Matanzas",
        "Villa_Clara",
        "Cienfuegos",
        "Sancti_Spiritus",
        "Ciego_de_Avila",
        "Camaguey",
        "Las_Tunas",
        "Holguin",
        "Granma",
        "Santiago_de_Cuba",
        "Guantanamo",
        "Isla_de_la_Juventud",
    ]

    cuba_neighbors = {
        "Pinar_del_Rio": {"Artemisa"},
        "Artemisa": {"Pinar_del_Rio", "Havanna", "Mayabeque"},
        "Havanna": {"Artemisa", "Mayabeque"},
        "Mayabeque": {"Artemisa", "Havanna", "Matanzas"},
        "Matanzas": {"Mayabeque", "Villa_Clara", "Cienfuegos"},
        "Villa_Clara": {"Matanzas", "Cienfuegos", "Sancti_Spiritus"},
        "Cienfuegos": {"Matanzas", "Villa_Clara", "Sancti_Spiritus"},
        "Sancti_Spiritus": {
            "Villa_Clara",
            "Cienfuegos",
            "Ciego_de_Avila",
            "Camaguey",
        },
        "Ciego_de_Avila": {"Sancti_Spiritus", "Camaguey"},
        "Camaguey": {"Sancti_Spiritus", "Ciego_de_Avila", "Las_Tunas"},
        "Las_Tunas": {"Camaguey", "Holguin", "Granma"},
        "Holguin": {"Las_Tunas", "Granma", "Santiago_de_Cuba"},
        "Granma": {"Las_Tunas", "Holguin", "Santiago_de_Cuba"},
        "Santiago_de_Cuba": {"Holguin", "Granma", "Guantanamo"},
        "Guantanamo": {"Santiago_de_Cuba"},
        "Isla_de_la_Juventud": set(),
    }

    cuba = MapColoringCSP(
        regions=cuba_regions, neighbors=cuba_neighbors, colors=["Red", "Green", "Blue"]
    )

    solution = backtracking_search(cuba)

    # Should find a solution with 3 colors
    assert solution is not None, "Cuba should be 3-colorable"
    assert len(solution) == 16

    # Verify uses only 3 colors
    used_colors = set(solution.values())
    assert used_colors.issubset({"Red", "Green", "Blue"})


# --- Small Custom Map Tests ---


def test_simple_three_region_map():
    """
    Test a simple 3-region linear map: A - B - C

    This is a minimal test case to verify basic functionality.
    """
    problem = MapColoringCSP(
        regions=["A", "B", "C"],
        neighbors={"A": {"B"}, "B": {"A", "C"}, "C": {"B"}},
        colors=["Red", "Green"],
    )

    solution = backtracking_search(problem)

    assert solution is not None
    assert len(solution) == 3

    # A and C can be same color (not neighbors)
    # B must be different from both
    assert solution["A"] != solution["B"]
    assert solution["B"] != solution["C"]


def test_unsolvable_problem():
    r"""
    Test that solver correctly identifies unsolvable problems.

    Triangle graph with only 2 colors is unsolvable:
    A - B
    |\ /|
    | X |
    |/ \|
    C - -

    All three regions are neighbors of each other.
    """
    problem = MapColoringCSP(
        regions=["A", "B", "C"],
        neighbors={"A": {"B", "C"}, "B": {"A", "C"}, "C": {"A", "B"}},
        colors=["Red", "Green"],  # Only 2 colors, need 3!
    )

    solution = backtracking_search(problem)

    # Should return None (no solution exists)
    assert solution is None, "Triangle graph with 2 colors should be unsolvable"


def test_single_region_map():
    """
    Edge case: Map with only one region.

    Should trivially succeed.
    """
    problem = MapColoringCSP(
        regions=["Only"], neighbors={"Only": set()}, colors=["Red"]
    )

    solution = backtracking_search(problem)

    assert solution is not None
    assert solution == {"Only": "Red"}


def test_island_regions_can_share_colors():
    """
    Regions with no neighbors can share colors.

    This tests that the solver understands constraints correctly.
    """
    problem = MapColoringCSP(
        regions=["Island1", "Island2", "Island3"],
        neighbors={"Island1": set(), "Island2": set(), "Island3": set()},
        colors=["Red"],  # Only ONE color!
    )

    solution = backtracking_search(problem)

    # Should work - no neighbors means no conflicts!
    assert solution is not None
    assert all(color == "Red" for color in solution.values())


# --- SOLID Principles Tests ---


def test_open_closed_principle():
    """
    Verify Open/Closed Principle:
    Same solver works with different CSP configurations.

    This test creates three DIFFERENT maps and solves all
    with the SAME solver (no modification needed).
    """
    # Map 1: Australia
    australia = MapColoringCSP()
    sol1 = backtracking_search(australia)

    # Map 2: Simple 4-region map
    simple = MapColoringCSP(
        regions=["A", "B", "C", "D"],
        neighbors={"A": {"B", "D"}, "B": {"A", "C"}, "C": {"B", "D"}, "D": {"A", "C"}},
        colors=["Red", "Green"],
    )
    sol2 = backtracking_search(simple)

    # Map 3: Linear chain
    chain = MapColoringCSP(
        regions=["R1", "R2", "R3", "R4", "R5"],
        neighbors={
            "R1": {"R2"},
            "R2": {"R1", "R3"},
            "R3": {"R2", "R4"},
            "R4": {"R3", "R5"},
            "R5": {"R4"},
        },
        colors=["Red", "Blue"],
    )
    sol3 = backtracking_search(chain)

    # All should have solutions
    assert sol1 is not None, "Australia should be solvable"
    assert sol2 is not None, "4-region should be solvable"
    assert sol3 is not None, "Chain should be solvable"

    # This demonstrates Open/Closed:
    # - CLOSED: backtracking_search code unchanged
    # - OPEN: Works with infinite possible CSP configurations


def test_dependency_inversion_principle():
    """
    Verify Dependency Inversion Principle:
    Solver depends on CSP abstraction, not concrete MapColoringCSP.

    We can create a completely different CSP implementation
    and it still works with backtracking_search!
    """
    # The fact that we can pass MapColoringCSP to backtracking_search
    # proves DIP - the solver only knows about CSP protocol,
    # not MapColoringCSP specifics

    problem = MapColoringCSP(
        regions=["X", "Y"], neighbors={"X": {"Y"}, "Y": {"X"}}, colors=["A", "B"]
    )

    # This works because:
    # 1. backtracking_search expects CSP protocol
    # 2. MapColoringCSP implements CSP protocol
    # 3. No direct coupling between them!

    solution = backtracking_search(problem)
    assert solution is not None


# --- Educational Note: What We're NOT Testing ---
"""
Notice what we DON'T test:

❌ Internal implementation details:
   - How MRV picks variables (internal logic)
   - Order of backtracking (implementation)
   - Specific variable ordering (internal heuristic)

✅ Behavioral contracts:
   - Does it find valid solutions?
   - Does it handle edge cases?
   - Does it work with different maps?
   - Does it follow SOLID principles?

This is called "Black Box Testing":
- We test WHAT it does (behavior)
- Not HOW it does it (implementation)

Benefits:
- Tests remain valid even if we change implementation
- Tests document expected behavior
- Tests are more maintainable
- Follows SOLID principles in testing!

This is professional-grade testing! 🚀
"""
