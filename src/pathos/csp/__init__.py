"""
Constraint Satisfaction Problem (CSP) Module.

This module provides tools for solving constraint satisfaction problems
using backtracking search with intelligent heuristics.

Main Components:
---------------
- CSP Protocol: Abstract interface for defining CSP problems
- backtracking_search: Solver that works with any CSP
- MapColoringCSP: Example problem implementation

Example Usage:
-------------
>>> from pathos.csp import backtracking_search, MapColoringCSP
>>>
>>> # Create a problem
>>> problem = MapColoringCSP()  # Australia map
>>>
>>> # Solve it
>>> solution = backtracking_search(problem)
>>>
>>> # Custom map
>>> custom = MapColoringCSP(
...     regions=["A", "B", "C"],
...     neighbors={"A": {"B"}, "B": {"A", "C"}, "C": {"B"}},
...     colors=["Red", "Green"]
... )
>>> solution = backtracking_search(custom)

SOLID Principles:
----------------
This module demonstrates:
- Open/Closed: Solver works with ANY CSP without modification
- Dependency Inversion: Solver depends on CSP protocol (abstraction)
- Single Responsibility: Each component has ONE job
- Interface Segregation: Minimal protocol (variables, domains, is_consistent)
- Liskov Substitution: Any CSP implementation is substitutable

Educational Value:
-----------------
This module teaches:
- Backtracking algorithm
- MRV (Minimum Remaining Values) heuristic
- Early constraint checking
- Fail-first principle
- Protocol-based design in Python
"""

# Core CSP types and protocol
from pathos.csp.core import CSP, Assignment

# Solving algorithms
from pathos.csp.solvers import backtracking_search

# Re-export for convenience
__all__ = [
    # Core types
    "CSP",
    "Assignment",
    # Algorithms
    "backtracking_search",
]

# Note: MapColoringCSP is in examples/ not csp/
# Import from pathos.examples.map_coloring if needed
