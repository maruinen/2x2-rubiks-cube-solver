#!/usr/bin/env python3
"""
Test the updated app.py with C solver integration
"""
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')

from app import Cube, solve_cube

def load_state(filename):
    with open(filename) as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    parsed_state = [''] * 24
    
    # U face
    parsed_state[0] = lines[0][0]
    parsed_state[1] = lines[0][1]
    parsed_state[2] = lines[1][0]
    parsed_state[3] = lines[1][1]

    # Middle faces (L-F-R-B)
    parsed_state[16] = lines[2][0] # L0
    parsed_state[17] = lines[2][1] # L1
    parsed_state[4] = lines[2][2]  # F0
    parsed_state[5] = lines[2][3]  # F1
    parsed_state[8] = lines[2][4]  # R0
    parsed_state[9] = lines[2][5]  # R1
    parsed_state[12] = lines[2][6] # B0
    parsed_state[13] = lines[2][7] # B1

    parsed_state[18] = lines[3][0] # L2
    parsed_state[19] = lines[3][1] # L3
    parsed_state[6] = lines[3][2]  # F2
    parsed_state[7] = lines[3][3]  # F3
    parsed_state[10] = lines[3][4] # R2
    parsed_state[11] = lines[3][5] # R3
    parsed_state[14] = lines[3][6] # B2
    parsed_state[15] = lines[3][7] # B3

    # D face
    parsed_state[20] = lines[4][0]
    parsed_state[21] = lines[4][1]
    parsed_state[22] = lines[5][0]
    parsed_state[23] = lines[5][1]
    
    return "".join(parsed_state)

# Test 1: state2 (4-move solution)
print("=" * 60)
print("Test 1: state2 (4-move solution)")
print("=" * 60)
state2_str = load_state('state2.txt')
cube = Cube(state2_str)
print(f"Initial: {str(cube)[:40]}...")
solution = solve_cube(cube)
print(f"Solution: {solution}")
print()

# Test 2: state1 (1-move solution)
print("=" * 60)
print("Test 2: state1 (1-move solution)")
print("=" * 60)
state1_str = load_state('state1.txt')
cube = Cube(state1_str)
print(f"Initial: {str(cube)[:40]}...")
solution = solve_cube(cube)
print(f"Solution: {solution}")
print()

# Test 3: Already solved
print("=" * 60)
print("Test 3: Already solved")
print("=" * 60)
cube = Cube()  # Default is solved
print(f"Initial: {str(cube)[:40]}...")
solution = solve_cube(cube)
print(f"Solution: {solution}")
