# Checkers

**Course:** Foundations of Artificial Intelligence  
**Author:** Valentina Dermenzhy

A classic **Checkers** (Draughts) game built with **Python + Pygame**, featuring an AI opponent powered by **Minimax** with **alpha–beta pruning**, mandatory captures, multi-jump sequences, and king promotion.

---

## AI Overview

**Minimax with Alpha–Beta Pruning**

- The AI searches a game tree where nodes are board states and edges are legal moves.
- Max player = **WHITE** (human), Min player = **BLACK** (bot) or vice versa depending on your code convention. The evaluation is from WHITE’s perspective.
- **Alpha–beta pruning** skips branches that can’t affect the final decision, making deeper search feasible.
- **Mandatory captures + multi-jump** are encoded in the move generator. After a capture, the same piece is checked for **additional captures**; if any exist, the search **keeps the turn** with that same piece (so a multi-jump is taken as one turn in the tree).

**Heuristic (Evaluate):**
- +100 base value per piece
- +120 for kings
- Advancement bonus (further advanced men are more valuable)
- +5 for center squares (2..5 rows/cols)
- +15 on top/bottom edges (anchor)
- −10 isolation penalty (no friendly diagonals)

**Time-Bounded Search**

- A soft time limit can terminate the current search early and return the best found score so far.
- This is practical for interactive play and demonstrates balancing time vs. depth in real AI systems.
