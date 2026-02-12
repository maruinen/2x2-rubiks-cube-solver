.PHONY: build test clean run help install

# Default target
help:
	@echo "2x2 Rubik's Cube Solver - Available targets:"
	@echo "  make build      - Compile C solver binary"
	@echo "  make test       - Run integration tests"
	@echo "  make run        - Run the Streamlit app"
	@echo "  make clean      - Remove compiled binaries and __pycache__"
	@echo "  make install    - Install Python dependencies"
	@echo "  make lint       - Run code style checks (if configured)"

# Build the C solver
build:
	gcc -O2 -o src/solver src/solver.c
	@echo "✓ Solver binary compiled: src/solver"

# Run integration tests
test: build
	python3 tests/test_solver_binary_integration.py
	@echo "✓ Integration tests passed"

# Launch the Streamlit web app
run:
	streamlit run src/app.py

# Display a list of available Python test files
list-tests:
	@echo "Available legacy test files:"
	@find . -maxdepth 1 -name "test_*.py" -o -name "debug_*.py" -o -name "trace_*.py" | sort

# Install/update Python dependencies
install:
	pip3 install -r requirements.txt

# Clean up: remove binaries, cache, and temp files
clean:
	rm -f src/solver
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -f *.pyc src/*.pyc tests/*.pyc
	rm -f /tmp/issue4_state.txt
	@echo "✓ Directory cleaned"

# Full rebuild
rebuild: clean build
	@echo "✓ Full rebuild complete"
