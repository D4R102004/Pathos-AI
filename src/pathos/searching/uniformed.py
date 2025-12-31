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

def bfs(problem: GoalOriented[S, A]) -> Optional[Node[S, A]]:
    """
    Breadth-First Search.
    Guaranteed shortest path for unweighted problems.
    """
    # 1. Access the property we added to the Protocol
    start_node = Node(state=problem.initial_state)
    
    if problem.is_goal(start_node.state):
        return start_node
    
    # 2. FIFO Queue
    frontier = deque([start_node])
    explored: Set[S] = {start_node.state}

    while frontier:
        node = frontier.popleft() # <--- FIFO

        for child in node.expand(problem):
            if child.state not in explored:
                if problem.is_goal(child.state):
                    return child
                explored.add(child.state)
                frontier.append(child)
    return None

def dfs(problem: GoalOriented[S, A]) -> Optional[Node[S, A]]:
    """
    Depth-First Search.
    Not guaranteed to find the shortest path. Memory efficient
    """
    start_node = Node(state=problem.initial_state)
    
    if problem.is_goal(start_node.state):
        return start_node
    
    # LIFO Stack
    frontier = [start_node]
    explored: Set[S] = set()  # START EMPTY

    while frontier:
        node = frontier.pop()

        if problem.is_goal(node.state):
            return node

        if node.state not in explored:
            explored.add(node.state)
            
            # Add children
            for child in node.expand(problem):
                if child.state not in explored:
                    frontier.append(child)
    return None