"""
Uninformed Search Algorithms.

These algorithms explore the search space without any knowledge of the goal's location.
They are 'blind' but systematic.
BFS and DFS implementations.
"""

from collections import deque
from typing import Optional, List, Set, TypeVar
from pathos.core import Node, SearchDomain, GoalOriented

S = TypeVar("S")  # State
A = TypeVar("A")  # Action

def reconstruct_path(node: Node[S, A]) -> List[S]:
    """
    Trace back from goal to root to find the action sequence.
    """
    path = []
    current = node
    while current.parent is not None:
        if current.action is not None:
            path.append(current.action)
        current = current.parent
    
    return list(reversed(path))
    

