#!/usr/bin/env python3
"""
Test C solver with state3 (potentially problematic state)
"""
import subprocess
import tempfile
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
solver_binary = os.path.join(script_dir, "solver")

print(f"Solver binary path: {solver_binary}")
print()

# Create temp file with state3 content
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    temp_file = f.name
    # state3.txt content
    f.write("BW\nOO\nGYGRWBOO\nOYGRGBBR\nBR\nYR")

print(f"Testing with state3.txt")
print(f"Temp file: {temp_file}")
print()

try:
    print("Calling subprocess.run() with 5-second timeout...")
    start_time = time.time()
    
    result = subprocess.run(
        [solver_binary, temp_file],
        capture_output=True,
        text=True,
        timeout=5  # Short timeout to catch hangs
    )
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")
    print()
    print(f"Return code: {result.returncode}")
    print(f"Stdout ({len(result.stdout)} chars):")
    print(result.stdout)
    print()
    print(f"Stderr ({len(result.stderr)} chars):")
    if result.stderr:
        print(result.stderr)
    
except subprocess.TimeoutExpired:
    print("⚠️ TIMEOUT! Solver is hanging on state3!")
    
finally:
    if os.path.exists(temp_file):
        os.unlink(temp_file)
        print(f"\nCleaned up {temp_file}")
