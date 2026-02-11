#!/usr/bin/env python3
"""
Direct test of C solver subprocess call
"""
import subprocess
import tempfile
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
solver_binary = os.path.join(script_dir, "solver")

print(f"Solver binary path: {solver_binary}")
print(f"Exists: {os.path.exists(solver_binary)}")
print(f"Executable: {os.access(solver_binary, os.X_OK)}")
print()

# Create temp file with state1 (1-move solution)
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    temp_file = f.name
    # state1.txt content
    f.write("WW\nWW\nGGRRBBOO\nOOGGRRBB\nYY\nYY")

print(f"Temp file: {temp_file}")
print()

try:
    print("Calling subprocess.run()...")
    print(f"Command: [{solver_binary}, {temp_file}]")
    print()
    
    result = subprocess.run(
        [solver_binary, temp_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"Return code: {result.returncode}")
    print(f"Stdout ({len(result.stdout)} chars):")
    print(result.stdout)
    print()
    print(f"Stderr ({len(result.stderr)} chars):")
    print(result.stderr)
    
finally:
    if os.path.exists(temp_file):
        os.unlink(temp_file)
        print(f"Cleaned up {temp_file}")
