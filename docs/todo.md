# 2x2 Rubik's Cube Solver To-Do List

This document outlines the tasks required to implement the 2x2 Rubik's Cube solver application.

## 1. Project Setup and Dependencies

*   [x] Initialize a new Python project.
*   [x] Install `streamlit` and any other necessary libraries (e.g., for cube state representation).
    *   `pip install streamlit`

## 2. Cube Data Model and Operations

*   [x] Define the `Cube` class or data structure to represent the 2x2 cube's state (e.g., 24 stickers, 6 faces with 4 stickers each).
    *   Use a canonical representation (e.g., array of 24 characters representing colors).
*   [x] Implement basic cube manipulation methods:
    *   [x] `apply_move(move_notation)`: Apply a single move (e.g., 'R', 'U', 'F', 'R'', 'U'', 'F'').
    *   [x] Fix C solver's move application logic (e.g., for inverse and double moves).
    *   [x] `is_solved()`: Check if the current cube state is the solved state.
    *   [x] `get_possible_moves()`: Return a list of all valid moves for a 2x2.
    *   [x] `hash()`: Generate a hash for the cube state for use in BFS.
*   [x] Define color mappings (e.g., 'W' for White, 'Y' for Yellow, 'R' for Red, 'O' for Orange, 'B' for Blue, 'G' for Green).

## 3. Streamlit User Interface (Input)

*   [x] Create the main Streamlit application file (e.g., `app.py`).
*   [x] Design the input section for the 2x2 cube:
    *   [x] Display a visual layout of the 6 faces.
    *   [x] For each of the 24 stickers, provide a text input field for the user to enter the color (e.g., 'W', 'Y', 'R', 'O', 'B', 'G').
    *   [x] Add instructions for users on how to input colors.
*   [x] Implement input validation:
    *   [x] Ensure exactly 24 color inputs are provided.
    *   [x] Check for valid color characters.
    *   [x] Verify the count of each color (e.g., 4 white, 4 yellow, 4 red, etc.).
    *   [ ] Basic check for a valid cube configuration (e.g., each corner piece has 3 distinct colors).
*   [x] Add a "Solve Cube" button.

## 3.1. Streamlit User Interface (Functionality)
*   [x] Implement state save/load feature (via text file)

## 4. Solver Logic Implementation

*   [x] Implement the Breadth-First Search (BFS) algorithm to find the shortest solution path.
    *   [x] Maintain a queue for states to visit.
    *   [x] Maintain a dictionary to store `(cube_state_hash: parent_state_hash, move_from_parent)` to reconstruct the path.
    *   [x] Implement a function to generate all possible next states from a given state by applying each move.
*   [x] Integrate the solver with the `Cube` data model.

## 5. Streamlit User Interface (Output)

*   [x] Display the solution:
    *   [x] If a solution is found, present the sequence of moves step-by-step.
    *   [x] Clearly explain each move in standard notation.
    *   [x] Handle "no solution found" or invalid input scenarios gracefully.

## 6. Testing

*   [x] Write unit tests for the `Cube` class (e.g., `apply_move`, `is_solved`).
*   [x] Write unit tests for the solver algorithm with known simple and complex 2x2 scrambles.
*   [ ] Manually test the Streamlit application with various valid and invalid inputs.

## 7. Refinements and Enhancements

*   [x] Improve the visual appeal of the Streamlit app (e.g., using st.columns, st.beta_columns for better layout, color-coded sticker inputs).
*   [x] Add error handling and user-friendly messages for invalid inputs.
*   [x] Consider adding a feature to reset the cube input.

