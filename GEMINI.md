# Gemini Instructions

## Project Overview
This repository contains a 2x2 Rubik's Cube Solver with:
- **Frontend**: Streamlit-based web UI for cube state input and visualization
- **Backend**: C solver engine for computing solutions
- **Logic Layer**: Python wrapper for state management and move validation

## Code Organization
- `app.py`: Main Streamlit application, Cube class, and move logic
- `solver.c`: C implementation of the cube solver algorithm
- `requirements.txt`: Python dependencies (streamlit, etc.)
- Tests in `test_*.py` files for validation

## Cube Representation
- **State Format**: 24-character string representing 6 faces × 4 stickers each
  - Face order: U (Up), F (Front), R (Right), B (Back), L (Left), D (Down)
  - Colors: W (White), Y (Yellow), R (Red), O (Orange), B (Blue), G (Green)
  - Example solved state: `WWWWGGGGRRRRBBBBOOOOYYYY`
- **Packed Format**: States are packed into integers for efficient computation
  - Each sticker uses 3 bits (allows 0-5 for 6 colors)
  - Indexing maps to cube sticker positions

## Move Implementation Guidelines
- **Supported Moves**: R, R', R2, U, U', U2, F, F', F2
- **Move Logic**: All moves must be properly invertible
  - Single move (e.g., F): 1 rotation + cyclic permutation
  - Inverse move (e.g., F'): 3 applications of the base move
  - Double move (e.g., F2): 2 applications of the base move
- **Critical**: Moves must form proper 4-cycles for edge stickers to ensure F³ properly inverts F

## Key Functions
- `Cube(initial_state=None)`: Create a cube instance
- `apply_move(move_str)`: Apply a move and return new Cube state
- `_rotate_face(packed_state, face_start_index)`: Clockwise face rotation
- `_pack_state(state_list)` / `_unpack_state(packed_int)`: State conversion utilities

## Testing Requirements
- Unit tests must verify move invertibility (e.g., F + F' returns to original state)
- Complex sequences must properly compose (e.g., U,F,R,F,F' returns to U,F,R state)
- Use `pytest` or `unittest` for test execution

## Bug Fixes & Common Issues
- **Issue #3 Pattern** (Fixed): When applying composite moves, ensure cyclic assignments form proper 4-cycles, not 8-cycles
- Always test with complex move sequences, not just isolated moves
- Verify edge stickers are properly permuted after move implementation

## Code Style
- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Add docstrings for all functions and classes
- Keep functions focused and testable
- Comment complex permutation logic with cycle notation (e.g., `# 2 -> 8 -> 20 -> 17 -> 2`)

## Development Workflow
1. Create a feature branch: `git checkout -b feature/description`
2. Implement changes with tests
3. Verify all tests pass: `pytest` or `python3 -m unittest discover`
4. Create a PR with clear description
5. Merge after review/approval

## Tooling
- We have the `gh` command (GitHub CLI) installed and available.
- Use `gh pr create` to create pull requests from the command line.
