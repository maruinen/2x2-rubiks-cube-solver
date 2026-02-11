#!/usr/bin/env python3
"""
Test C solver with state3 using EXACT app.py state conversion
"""
import subprocess
import tempfile
import os
import time
from app import Cube

# Load state3 with exact app.py parsing method
def load_state3():
    with open('state3.txt') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    parsed_state = [''] * 24
    
    # U face
    parsed_state[0] = lines[0][0]
    parsed_state[1] = lines[0][1]
    parsed_state[2] = lines[1][0]
    parsed_state[3] = lines[1][1]

    # Middle faces (L-F-R-B)
    parsed_state[16] = lines[2][0]  # L0
    parsed_state[17] = lines[2][1]  # L1
    parsed_state[4] = lines[2][2]   # F0
    parsed_state[5] = lines[2][3]   # F1
    parsed_state[8] = lines[2][4]   # R0
    parsed_state[9] = lines[2][5]   # R1
    parsed_state[12] = lines[2][6]  # B0
    parsed_state[13] = lines[2][7]  # B1

    parsed_state[18] = lines[3][0]  # L2
    parsed_state[19] = lines[3][1]  # L3
    parsed_state[6] = lines[3][2]   # F2
    parsed_state[7] = lines[3][3]   # F3
    parsed_state[10] = lines[3][4]  # R2
    parsed_state[11] = lines[3][5]  # R3
    parsed_state[14] = lines[3][6]  # B2
    parsed_state[15] = lines[3][7]  # B3

    # D face
    parsed_state[20] = lines[4][0]
    parsed_state[21] = lines[4][1]
    parsed_state[22] = lines[5][0]
    parsed_state[23] = lines[5][1]

    return ''.join(parsed_state)

script_dir = os.path.dirname(os.path.abspath(__file__))
solver_binary = os.path.join(script_dir, "solver")

print("Testing with EXACT app.py state format conversion")
print()

# Get cube state the exact same way app.py does it
cube_state_str = load_state3()
print(f"Cube state: {cube_state_str}")
cube = Cube(cube_state_str)

# Create temp file WITH THE SAME CONVERSION APP.PY DOES
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    temp_file = f.name
    state_list = list(str(cube))
    lines = [
        f"{state_list[0]}{state_list[1]}",
        f"{state_list[2]}{state_list[3]}",
        f"{state_list[16]}{state_list[17]}{state_list[4]}{state_list[5]}{state_list[8]}{state_list[9]}{state_list[12]}{state_list[13]}",
        f"{state_list[18]}{state_list[19]}{state_list[6]}{state_list[7]}{state_list[10]}{state_list[11]}{state_list[14]}{state_list[15]}",
        f"{state_list[20]}{state_list[21]}",
        f"{state_list[22]}{state_list[23]}"
    ]
    content = "\n".join(lines)
    f.write(content)

print(f"Temp file: {temp_file}")
print(f"File content:")
print(content)
print()

try:
    print("Calling subprocess.run() with 5-second timeout...")
    start_time = time.time()
    
    result = subprocess.run(
        [solver_binary, temp_file],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")
    print()
    print(f"Return code: {result.returncode}")
    print(f"Stdout:")
    print(result.stdout)
    
except subprocess.TimeoutExpired as e:
    print("⚠️ TIMEOUT! Solver hung!")
    print(f"Partial output: {e}")
    
finally:
    if os.path.exists(temp_file):
        os.unlink(temp_file)
