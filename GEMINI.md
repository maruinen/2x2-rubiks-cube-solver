# Gemini Instructions (AI Short-term Memory)

## Active Task State
- **Current Focus**: Documentation organization and deduplication using `doc-organizer` skill.
- **Next Task**: Verify the Streamlit input validation logic (item 3 in `docs/todo.md`).

## Project-Specific Coding Rules
- **Move Implementation**: Ensure cyclic assignments form proper 4-cycles (not 8-cycles).
- **Testing**: Always test with complex move sequences. Verify edge stickers are properly permuted.
- **Style**: Follow PEP 8, use type hints, and include docstrings. Comment complex permutation logic with cycle notation (e.g., `# 2 -> 8 -> 20 -> 17 -> 2`).

## Lessons Learned & Common Issues
- **Issue #3 Pattern**: Incorrect mapping of adjacent face stickers during rotations can lead to non-invertible moves.
- **Issue #4 Pattern**: Move permutation bugs in the C solver can cause state space explosion and timeouts.

## Tooling
- `gh` (GitHub CLI) is available for PR creation (`gh pr create`).
- `make` is used for compiling the C solver.

## AI Next Steps
1. Finish documentation refactoring.
2. Address pending items in `docs/todo.md` (e.g., "Basic check for a valid cube configuration").
