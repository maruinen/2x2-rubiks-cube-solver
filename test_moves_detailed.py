#!/usr/bin/env python3
"""
Compare move implementations between Python and C
"""
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')

from app import Cube, SOLVED_STATE_STR

# state2 in proper format
state2_str = "WWOGGRGRWBWROOBBGYOYBRYY"

print("=" * 80)
print("TESTING STATE2 TRANSFORMATIONS")
print("=" * 80)
print()

# Initial state
cube = Cube(state2_str)
print(f"Initial: {str(cube)}")
print()

# Apply F
cube = cube.apply_move('F')
print(f"After F: {str(cube)}")
print()

# Apply F'
cube = cube.apply_move("F'")
print(f"After F': {str(cube)}")
print()

# Apply F'
cube = cube.apply_move("F'")
print(f"After F': {str(cube)}")
print()

# Apply U'
cube = cube.apply_move("U'")
print(f"After U': {str(cube)}")
print()

if cube.is_solved():
    print("✓ SOLVED!")
else:
    print("✗ NOT SOLVED")

print()
print("=" * 80)
print("TESTING MOVE DETAILS - F MOVE")
print("=" * 80)
print()

cube = Cube(state2_str)
print(f"Initial state: {str(cube)}")
print(f"  U: {str(cube)[0:4]}")
print(f"  F: {str(cube)[4:8]}")
print(f"  R: {str(cube)[8:12]}")
print(f"  B: {str(cube)[12:16]}")
print(f"  L: {str(cube)[16:20]}")
print(f"  D: {str(cube)[20:24]}")
print()

# Get values before F move
state_before_f = str(cube)
print(f"Before F move:")
print(f"  U[2:4]: {state_before_f[2:4]}")  # U2, U3 (bottom edge of U)
print(f"  R[0], R[2]: {state_before_f[8:10]}")  # R0, R1 -> need R0, R2
print(f"  D[0:2]: {state_before_f[20:22]}")  # D0, D1 (top edge of D)
print(f"  L[1], L[3]: {state_before_f[17]}, {state_before_f[19]}")  # L1, L3
print()

cube = cube.apply_move('F')
state_after_f = str(cube)

print(f"After F move:")
print(f"  U[2:4]: {state_after_f[2:4]}")  
print(f"  R[0], R[2]: {state_after_f[8]}, {state_after_f[10]}")  
print(f"  D[0:2]: {state_after_f[20:22]}")  
print(f"  L[1], L[3]: {state_after_f[17]}, {state_after_f[19]}")  
print()

# Check F face rotation
print(f"Before F move - F face: {state_before_f[4:8]}")
print(f"After F move - F face: {state_after_f[4:8]}")
print()

# Expected behavior for F move:
# U2, U3 should come from L3, L1
# L1, L3 should come from D0, D1
# D0, D1 should come from R0, R2
# R0, R2 should come from U2, U3
print("Expected from F move:")
print(f"  U2,U3 <- L3,L1: {state_before_f[19]}{state_before_f[17]}")
print(f"  L1,L3 <- D0,D1: {state_before_f[20]}{state_before_f[21]}")
print(f"  D0,D1 <- R0,R2: {state_before_f[8]}{state_before_f[10]}")
print(f"  R0,R2 <- U2,U3: {state_before_f[2]}{state_before_f[3]}")
