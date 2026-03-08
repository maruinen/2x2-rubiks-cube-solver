# 2x2 Rubik's Cube Solver

A Streamlit-based web application for computing solutions for a 2x2 Rubik's Cube.

## Project Overview
This repository contains a 2x2 Rubik's Cube Solver with:
- **Frontend**: Streamlit-based web UI for cube state input and visualization
- **Backend**: C solver engine for computing solutions
- **Logic Layer**: Python wrapper for state management and move validation

## Directory Structure
```
/
├── .github/
│   └── copilot-instructions.md
├── bin/                 # Compiled solver binaries
├── docs/
│   ├── design.md        # Technical architecture and ADRs
│   └── todo.md          # Project roadmap and task status
├── src/
│   ├── app.py           # Main Streamlit application
│   └── solver.c         # C implementation of the solver algorithm
├── tests/               # Unit and integration tests
├── GEMINI.md            # AI-specific context and task state
├── Makefile             # Build automation
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

## Installation
1. Clone the repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Compile the C solver (requires `gcc` and `make`):
   ```bash
   make
   ```

## Usage
1. Start the Streamlit application:
   ```bash
   streamlit run src/app.py
   ```
2. Input the current state of your 2x2 cube in the web interface.
3. Click "Solve Cube" to receive step-by-step instructions.

## Development
- Unit tests: `pytest` or `python3 -m unittest discover`
- Contribution guidelines are managed via `docs/todo.md`.
- AI assistant context is maintained in `GEMINI.md`.
