#!/usr/bin/env python3
"""
Detailed move parameter analysis - comparing Python vs C F move
"""
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')

from app import Cube

# Use state2
state2_str = "WWOGGRGRWBWROOBBGYOYBRYY"

# Convert to array for easy indexing
cube = Cube(state2_str)
state_array = list(str(cube))

print("=" * 80)
print("ANALYZING F MOVE IMPLEMENTATION")
print("=" * 80)
print()

print("INDICES:")
print("  U: 0-3  (U0=0, U1=1, U2=2, U3=3)")
print("  F: 4-7  (F0=4, F1=5, F2=6, F3=7)")
print("  R: 8-11 (R0=8, R1=9, R2=10, R3=11)")
print("  B: 12-15")
print("  L: 16-19 (L0=16, L1=17, L2=18, L3=19)")
print("  D: 20-23 (D0=20, D1=21, D2=22, D3=23)")
print()

print("INITIAL STATE:")
for i in range(24):
    print(f"  sticker[{i:2d}] = {state_array[i]}", end="")
    if (i+1) % 4 == 0:
        print()
    else:
        print("  ", end="")
print()

print("F MOVE - EDGE STICKERS INVOLVED:")
print(f"  U2 (idx 2) = {state_array[2]}")
print(f"  U3 (idx 3) = {state_array[3]}")
print(f"  R0 (idx 8) = {state_array[8]}")
print(f"  R2 (idx 10) = {state_array[10]}")
print(f"  D0 (idx 20) = {state_array[20]}")
print(f"  D1 (idx 21) = {state_array[21]}")
print(f"  L1 (idx 17) = {state_array[17]}")
print(f"  L3 (idx 19) = {state_array[19]}")
print()

print("PYTHON IMPLEMENTATION (CORRECT):")
print("  sticker[2]  = sticker[19]  (U2 <- L3)")  
print("  sticker[3]  = sticker[17]  (U3 <- L1)")
print("  sticker[8]  = sticker[2]   (R0 <- U2)") 
print("  sticker[10] = sticker[3]   (R2 <- U3)")
print("  sticker[20] = sticker[8]   (D0 <- R0)")
print("  sticker[21] = sticker[10]  (D1 <- R2)")
print("  sticker[17] = sticker[20]  (L1 <- D0)")
print("  sticker[19] = sticker[21]  (L3 <- D1)")
print()

print("C IMPLEMENTATION (CURRENT - BUG!):")
print("  sticker[2]  = sticker[17]  (U2 <- L1)  ❌ SHOULD BE <- L3 (sticker[19])")
print("  sticker[3]  = sticker[19]  (U3 <- L3)  ❌ SHOULD BE <- L1 (sticker[17])")
print("  sticker[8]  = sticker[2]   (R0 <- U2)  ✓")
print("  sticker[10] = sticker[3]   (R2 <- U3)  ✓")
print("  sticker[20] = sticker[8]   (D0 <- R0)  ✓")
print("  sticker[21] = sticker[10]  (D1 <- R2)  ✓")
print("  sticker[17] = sticker[20]  (L1 <- D0)  ✓")
print("  sticker[19] = sticker[21]  (L3 <- D1)  ✓")
print()

print("After F move (PYTHON):")
cube_after_f = cube.apply_move('F')
result_array = list(str(cube_after_f))
print(f"  sticker[2] (U2) = {result_array[2]} (was {state_array[2]}, from L3={state_array[19]})")
print(f"  sticker[3] (U3) = {result_array[3]} (was {state_array[3]}, from L1={state_array[17]})")
print(f"  sticker[8] (R0) = {result_array[8]} (was {state_array[8]}, from U2={state_array[2]})")
print(f"  sticker[10] (R2) = {result_array[10]} (was {state_array[10]}, from U3={state_array[3]})")
print(f"  sticker[20] (D0) = {result_array[20]} (was {state_array[20]}, from R0={state_array[8]})")
print(f"  sticker[21] (D1) = {result_array[21]} (was {state_array[21]}, from R2={state_array[10]})")
print(f"  sticker[17] (L1) = {result_array[17]} (was {state_array[17]}, from D0={state_array[20]})")
print(f"  sticker[19] (L3) = {result_array[19]} (was {state_array[19]}, from D1={state_array[21]})")
