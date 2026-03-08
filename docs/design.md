# 2x2 Rubik's Cube Solver Design Document

## 1. Introduction
This document outlines the technical architecture and data models for the 2x2 Rubik's Cube solver.

## 2. System Architecture
- **Frontend**: Streamlit-based web UI.
- **Logic**: Python `Cube` class manages state and move permutations.
- **Solver**: Breadth-First Search (BFS) in Python, with a high-performance C engine (`solver.c`) for deeper searches.

## 3. Cube Representation

### 3.1. State Format
The state is a 24-character string representing 6 faces × 4 stickers each.
- **Face order**: U (Up), F (Front), R (Right), B (Back), L (Left), D (Down)
- **Colors**: W (White), Y (Yellow), R (Red), O (Orange), B (Blue), G (Green)
- **Example solved state**: `WWWWGGGGRRRRBBBBOOOOYYYY`

### 3.2. Packed Format (Internal)
States are packed into integers for efficiency:
- Each sticker uses 3 bits (0-5 for 6 colors).
- Indexing maps to cube sticker positions as defined in `src/app.py`.

## 4. Move Implementation

### 4.1. Supported Moves
Standard notation: `R, R', R2, U, U', U2, F, F', F2`.

### 4.2. Permutation Logic
All moves must be properly invertible. 
- Single move (e.g., F): 1 rotation + cyclic permutation.
- **Critical Constraint**: Moves must form proper 4-cycles for stickers to ensure $F^3$ properly inverts $F$.

## 5. User Interface Design

### 5.1. Input & Interaction
- Visual layout of 6 faces.
- State Save/Load Feature: Uses a 6-line plain text format representing unfolded faces. [See docs/todo.md for status](./todo.md).

## 6. Recent fixes and notes (ADRs)

### 6.1. Fix: F move cycle ordering (Issue #3)
Corrected assignment where edge stickers were permuted as an 8-cycle instead of two 4-cycles.
- Resolution: Swapped L assignments to ensure cycles:
    - Cycle 1: positions 2 -> 8 -> 20 -> 17 -> 2
    - Cycle 2: positions 3 -> 10 -> 21 -> 19 -> 3

### 6.2. Fix: C solver timeout (Issue #4)
Exponential growth at depth 7 was caused by the same cycle bug in `solver.c`. Correcting the permutation fixed the state space explosion.

## 7. Future Enhancements
- Interactive 3D cube visualization.
- Animation of solution steps.
