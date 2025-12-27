

## Issue 2 Core Structure and Node Architecture

## 🧠 Concept: State vs. Node

This is the most critical distinction in Discrete Search.

### 1. The State (The "What")
A **State** is a representation of the world at a single moment in time. It is static. It has no history.
* *Example:* In a Maze, the state is `(x=2, y=3)`.
* *Analogy:* A page number in a book.

### 2. The Node (The "How")
A **Node** is a data structure used by the Search Algorithm to keep track of its exploration. It is a "wrapper" around a State.
* *Example:* A Node contains:
    * State: `(x=2, y=3)`
    * Parent: `Node<(x=2, y=2)>` (Where did we come from?)
    * Action: `"SOUTH"` (How did we get here?)
    * Cost: `5.0` (How much energy did we spend?)
* *Analogy:* A bookmark that also has a sticky note saying "I got to page 42 by reading page 41."

> **Why the difference?**
> In a search graph, you might reach the *same state* via multiple *different paths*.
> The State is the same, but the Nodes are different (because they have different parents and different costs).