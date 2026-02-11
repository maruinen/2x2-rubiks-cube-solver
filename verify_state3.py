#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')
from app import Cube

# Manually parse state3.txt
with open('state3.txt') as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

# state3.txt format:
# Line 1-2: U face (2x2)
# Line 3-4: L, F, R, B faces
# Line 5-6: D face (2x2)
u_face = lines[0] + lines[1]
lfr_b = lines[2] + lines[3]
d_face = lines[4] + lines[5]

# Build state string: U (0-3), F (4-7), R (8-11), B (12-15), L (16-19), D (20-23)
# From lfr_b: L0 F0 R0 B0 | L1 F1 R1 B1
state_str = (u_face + 
             lfr_b[1] + lfr_b[4] + lfr_b[2] + lfr_b[5] + lfr_b[3] + lfr_b[6] +  # F, R, B, L at positions 4-7, 8-11, 12-15, 16-19
             lfr_b[0] + lfr_b[7] + lfr_b[8:] + d_face)

cube = Cube(state_str)
print("Initial state3: " + str(cube))

# Apply C solver solution: R' F F' F' U'
moves = ['R\'', 'F', 'F\'', 'F\'', 'U\'']
for move in moves:
    cube = cube.apply_move(move)
    print(f"After {move:3s}: {str(cube)}")

solved = "WWWWGGGGRRRRBBBBLLLLDDDD"
print(f"\nIs solved: {str(cube) == solved}")
