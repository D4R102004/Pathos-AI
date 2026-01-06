"""
Unit tests for the Core Architecture (Issue #2).
"""

from pathos.core import Node
from pathos.examples.number_line import NumberLine

# --- 2. The Tests ---


def test_node_initialization():
    """Test that a root node is created correctly."""
    root = Node(state=0)
    assert root.state == 0
    assert root.parent is None
    assert root.action is None
    assert root.path_cost == 0.0
    assert root.depth == 0


def test_node_expansion():
    """Test that expand() generates correct children."""
    problem = NumberLine(initial_state=1)
    root = Node(state=problem.initial_state)

    children = root.expand(problem)

    # We expect 2 children: 0 and 2
    assert len(children) == 2

    # Check Child 1 (Action -1 -> State 0)
    child_up = children[0]
    assert child_up.state == 0
    assert child_up.parent == root
    assert child_up.action == "-1"
    assert child_up.depth == 1
    assert child_up.path_cost == 1.0  # Default cost

    # Check Child 2 (Action +1 -> State 2)
    child_down = children[1]
    assert child_down.state == 2
    assert child_down.depth == 1


def test_node_comparison():
    """Test that nodes can be sorted by cost (for Priority Queues)."""
    n1 = Node(state="A", path_cost=10)
    n2 = Node(state="B", path_cost=5)

    # n2 is 'less than' n1 because it is cheaper
    assert n2 < n1

    # Verify sorting works
    nodes = [n1, n2]
    nodes.sort()
    assert nodes[0] == n2


def test_goal():
    """
    Tests wether a given state is truly a goal. Goal in this case is if the node is at position 10.
    """
    problem = NumberLine()
    root = Node(state=10)
    assert problem.is_goal(root.state)
