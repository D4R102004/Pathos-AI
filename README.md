# Pathos-AI

A personal Python library for studying and implementing classical Artificial Intelligence algorithms from scratch. Built as a learning framework with clean abstractions, real test coverage, and working examples.

## Implemented Algorithms

### Search
- **Uninformed:** BFS, DFS
- **Informed:** A\*, UCS (Uniform Cost Search)

### Adversarial Search
- **Minimax** with Alpha-Beta Pruning

### Constraint Satisfaction Problems (CSP)
- Backtracking solver
- Examples: Map Coloring, River Crossing, Maze, N-Queens variants

## Project Structure

```
src/pathos/
├── searching/       # BFS, DFS, A*, UCS
├── adversarial/     # Minimax, Alpha-Beta
├── csp/             # CSP core + solvers
├── optimization/    # (in progress)
└── examples/        # Runnable demos
```

## Running Tests

```bash
pip install -e .
pytest tests/
```

## Roadmap

- [ ] Genetic Algorithms (GA)
- [ ] Particle Swarm Optimization (PSO)
- [ ] Monte Carlo Tree Search (MCTS)
- [ ] Differential Evolution & Simulated Annealing
- [ ] PyPI release

## Notes

This is an ongoing personal project — algorithms are added incrementally as I study them. The focus is on clean, well-documented implementations over performance.
