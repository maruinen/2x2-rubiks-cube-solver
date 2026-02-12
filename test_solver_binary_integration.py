#!/usr/bin/env python3
"""Integration test: run the compiled C `solver` binary on a reproduced input
and assert it returns a solution within a short timeout.
"""
import subprocess
import tempfile
import os


def test_solver_binary_reproduced_state():
    # Reproduced state that previously caused timeouts: U, F, R, U, F
    content = """GW
WY
GBGWOYGY
OROWBBBR
OR
YR
"""

    solver_path = os.path.join(os.path.dirname(__file__), "solver")
    assert os.path.exists(solver_path) and os.access(solver_path, os.X_OK), "solver binary not found or not executable"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        tmpname = f.name

    try:
        # Run solver with a reasonable timeout (10s)
        result = subprocess.run([solver_path, tmpname], capture_output=True, text=True, timeout=10)

        # Basic sanity checks
        assert result.returncode == 0, f"solver exited with non-zero code: {result.returncode}, stderr: {result.stderr}"
        stdout = result.stdout or ""
        assert "Solution" in stdout, f"solver did not print a solution; stdout:\n{stdout}\nstderr:\n{result.stderr}"

    finally:
        try:
            os.unlink(tmpname)
        except Exception:
            pass
