#!/usr/bin/env python3
"""
Check R and U moves for bugs as well
"""
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')

from app import Cube

state2_str = "WWOGGRGRWBWROOBBGYOYBRYY"

print("=" * 80)
print("ANALYZING ALL MOVES (R, U, F)")
print("=" * 80)
print()

# Test R move
print("R MOVE:")
print("-" * 40)
cube = Cube(state2_str)
state_array = list(str(cube))

print(f"Before R: U1={state_array[1]}, U3={state_array[3]}, F1={state_array[5]}, F3={state_array[7]}, D1={state_array[21]}, D3={state_array[23]}, B1={state_array[13]}, B3={state_array[15]}")

cube_after_r = cube.apply_move('R')
result_array = list(str(cube_after_r))

print(f"After R: U1={result_array[1]}, U3={result_array[3]}, F1={result_array[5]}, F3={result_array[7]}, D1={result_array[21]}, D3={result_array[23]}, B1={result_array[13]}, B3={result_array[15]}")
print()

print("Expected R move cycle (clockwise R face rotation):")
print("  U1,U3 <- B3,B1   (B3->U1, B1->U3)")
print("  B3,B1 <- D3,D1   (D3->B3, D1->B1)")
print("  D3,D1 <- F3,F1   (F3->D3, F1->D1)")
print("  F3,F1 <- U3,U1   (U3->F3, U1->F1)")
print()

correct_u1 = state_array[15]  # U1 should get B3
correct_u3 = state_array[13]  # U3 should get B1
correct_f1 = state_array[1]   # F1 should get U1
correct_f3 = state_array[3]   # F3 should get U3
correct_d1 = state_array[5]   # D1 should get F1
correct_d3 = state_array[7]   # D3 should get F3
correct_b3 = state_array[21]  # B3 should get D1
correct_b1 = state_array[23]  # B1 should get D3

print(f"Expected result: U1={correct_u1}, U3={correct_u3}, F1={correct_f1}, F3={correct_f3}, D1={correct_d1}, D3={correct_d3}, B1={correct_b1}, B3={correct_b3}")
print(f"Actual result:   U1={result_array[1]}, U3={result_array[3]}, F1={result_array[5]}, F3={result_array[7]}, D1={result_array[21]}, D3={result_array[23]}, B1={result_array[13]}, B3={result_array[15]}")

if (result_array[1] == correct_u1 and result_array[3] == correct_u3 and 
    result_array[5] == correct_f1 and result_array[7] == correct_f3 and
    result_array[21] == correct_d1 and result_array[23] == correct_d3 and
    result_array[13] == correct_b1 and result_array[15] == correct_b3):
    print("✓ R move is CORRECT")
else:
    print("❌ R move has BUGS")
print()

# Test U move
print("U MOVE:")
print("-" * 40)
cube = Cube(state2_str)
state_array = list(str(cube))

print(f"Before U: F0={state_array[4]}, F1={state_array[5]}, R0={state_array[8]}, R1={state_array[9]}, B0={state_array[12]}, B1={state_array[13]}, L0={state_array[16]}, L1={state_array[17]}")

cube_after_u = cube.apply_move('U')
result_array = list(str(cube_after_u))

print(f"After U: F0={result_array[4]}, F1={result_array[5]}, R0={result_array[8]}, R1={result_array[9]}, B0={result_array[12]}, B1={result_array[13]}, L0={result_array[16]}, L1={result_array[17]}")
print()

print("Expected U move cycle (clockwise U face rotation):")
print("  F0,F1 <- R0,R1   (R0->F0, R1->F1)")
print("  R0,R1 <- B0,B1   (B0->R0, B1->R1)")
print("  B0,B1 <- L0,L1   (L0->B0, L1->B1)")
print("  L0,L1 <- F0,F1   (F0->L0, F1->L1)")
print()

correct_f0 = state_array[8]   # F0 should get R0
correct_f1 = state_array[9]   # F1 should get R1
correct_r0 = state_array[12]  # R0 should get B0
correct_r1 = state_array[13]  # R1 should get B1
correct_b0 = state_array[16]  # B0 should get L0
correct_b1 = state_array[17]  # B1 should get L1
correct_l0 = state_array[4]   # L0 should get F0
correct_l1 = state_array[5]   # L1 should get F1

print(f"Expected result: F0={correct_f0}, F1={correct_f1}, R0={correct_r0}, R1={correct_r1}, B0={correct_b0}, B1={correct_b1}, L0={correct_l0}, L1={correct_l1}")
print(f"Actual result:   F0={result_array[4]}, F1={result_array[5]}, R0={result_array[8]}, R1={result_array[9]}, B0={result_array[12]}, B1={result_array[13]}, L0={result_array[16]}, L1={result_array[17]}")

if (result_array[4] == correct_f0 and result_array[5] == correct_f1 and 
    result_array[8] == correct_r0 and result_array[9] == correct_r1 and
    result_array[12] == correct_b0 and result_array[13] == correct_b1 and
    result_array[16] == correct_l0 and result_array[17] == correct_l1):
    print("✓ U move is CORRECT")
else:
    print("❌ U move has BUGS")
