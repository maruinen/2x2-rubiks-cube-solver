# 2x2 Rubik's Cube Solver Design Document

## 1. Introduction
This document outlines the design for a 2x2 Rubik's Cube solver application built with Python and Streamlit. The application will allow users to input the current state of their 2x2 cube and will then provide step-by-step instructions to solve it.

## 2. User Interface (UI)
The user interface will be built using Streamlit, focusing on simplicity and ease of use.

### 2.1. Cube State Input
*   **Visual Representation:** The cube's state will be represented by six faces (Up, Down, Front, Back, Left, Right). Each face will have 4 stickers.
*   **Color Input:** For each sticker, the user will select a color from a predefined palette (e.g., White, Yellow, Red, Orange, Blue, Green). A simplified approach might use text input for each sticker or color pickers. Initially, text input (e.g., 'W', 'Y', 'R', 'O', 'B', 'G') will be used for simplicity.
*   **Validation:** Input will be validated to ensure a scramble is solvable (e.g., correct number of each color, no duplicate pieces).

### 2.1.1. State Save/Load Feature
Users can save the current cube state to a text file and load a previously saved state. The file format is a plain text file containing 6 lines, representing the unfolded cube faces and their stickers:
```
U0U1
U2U3
L0L1F0F1R0R1B0B1
L2L3F2F3R2R3B2B3
D0D1
D2D3
```
Where 'U', 'L', 'F', 'R', 'B', 'D' refer to the Up, Left, Front, Right, Back, Down faces respectively, and the numbers (0-3) indicate the sticker position on that face according to the general sticker indexing (0-23) used in the application.

### 2.2. Solution Output
*   **Step-by-step Instructions:** The solution will be presented as a sequence of moves (e.g., R, U, R', U', F, F).
*   **Move Notation:** Standard Rubik's Cube notation will be used.
*   **Clear Display:** Each step will be clearly displayed, possibly with an explanation or a diagram of the affected face.

### 2.3. Layout
*   The application will have a clear flow:
    1.  Instructions on how to input the cube state.
    2.  The input grid/color pickers for the 2x2 cube.
    3.  A "Solve" button.
    4.  The output area for the solution steps.

## 3. Data Structures

### 3.1. Cube Representation
The 2x2 cube state will be represented as a list or array of 24 stickers. Each sticker will have a color. A canonical representation will be chosen (e.g., defining the order of stickers for each face).
Example: `['W', 'W', 'W', 'W', 'R', 'R', 'R', 'R', ...]` for a solved cube (Up, Front, Right, Back, Left, Down faces, 4 stickers each).

### 3.2. Move Representation
Moves (e.g., R, U, F, R', U', F') will be represented as functions that transform the cube state data structure.

## 4. Solver Logic

### 4.1. Algorithm Choice
A common and relatively simple algorithm for 2x2 cubes is a two-phase approach:
1.  **Phase 1: Orient Corners:** Get all corners oriented correctly (e.g., white layer on bottom, yellow on top), regardless of their position.
2.  **Phase 2: Permute Corners:** Position the oriented corners correctly.

Alternatively, a simpler, brute-force search (like BFS) on the state space can find optimal solutions for 2x2 due to its small number of possible states. For initial implementation, a simplified layer-by-layer method or a precomputed lookup table (if feasible for 2x2) could be considered. A BFS approach will be initially targeted for its optimality and relative simplicity for 2x2.

### 4.2. Instruction Generation
The solver will return a sequence of moves. These moves will be translated into human-readable instructions.

## 5. Technical Stack
*   **Language:** Python
*   **Frontend/Web Framework:** Streamlit
*   **Core Logic:** Custom Python code for cube state management, moves, and solving algorithm.

## 6. Future Enhancements
*   Interactive 3D cube visualization.
*   Animation of solution steps.
*   More advanced solving algorithms for optimal move counts.
*   Pre-scrambled examples.

## 7. Recent fixes and notes

### Fix: F move cycle ordering (Issue #3)
During development we discovered a bug in the F move implementation where the
edge stickers were permuted as an 8-cycle instead of two 4-cycles. This made
inverse moves (F') behave incorrectly and produced hard-to-diagnose failures
when composing moves.

- Root cause: incorrect assignment of L->U indices when applying the F move.
- Resolution: swap the L assignments so the cycles are:
    - Cycle 1: positions 2 -> 8 -> 20 -> 17 -> 2
    - Cycle 2: positions 3 -> 10 -> 21 -> 19 -> 3

This fix was applied both in `app.py` (Python logic) and in `solver.c` (C
solver). Tests and trace scripts were used to reproduce and verify the issue.

### Fix: C solver timeout on specific sequences (Issue #4)
Symptom: the C solver timed out exploring an excessive number of nodes for the
sequence `U, F, R, U, F`. The solver showed exponential growth at depth 7.

Cause: the same F-move cycle bug (above) existed in `solver.c`, which caused
the search state space to explode in certain branches.

Resolution: corrected the F move permutation in `solver.c`, recompiled the
binary and verified the solver can find a solution quickly for the problematic
state (example solution found: `F' U' R' F' U'`).

### Tests and verification
- `test_issue_3_reproduction.py`, `trace_f_bug.py`, and `debug_f_move.py` were
    used to reproduce and verify the F-move bug and its fix.
- Integration test for the C solver behavior should be added to prevent
    regressions (suggested: add a test invoking the C solver on `state4.txt` or
    the reproduced temporary file and assert it completes within a timeout).

---

If you want, I can add an automated integration test that runs the `solver`
binary on the reproduced input and asserts solution correctness within a
configured timeout.

