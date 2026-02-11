#!/usr/bin/env python3
"""
Test script to verify C solver moves against Python implementation
"""
import sys
sys.path.insert(0, '/Users/ynomura/tmp/gemini/cli_test3')

from app import Cube, SOLVED_STATE_STR

# Read state2
with open('/Users/ynomura/tmp/gemini/cli_test3/state2.txt', 'r') as f:
    lines = f.readlines()

# Parse state2 to internal format
u_face = lines[0].strip()
u2_face = lines[1].strip()
middle1 = lines[2].strip()
middle2 = lines[3].strip() 
d_face = lines[4].strip()
d2_face = lines[5].strip()

# Convert from file format to cube format
state2_str = (
    u_face[0] + u_face[1] +              # U0, U1
    u2_face[0] + u2_face[1] +            # U2, U3
    middle1[2] + middle1[3] +            # F0, F1
    middle2[2] + middle2[3] +            # F2, F3
    middle1[4] + middle1[5] +            # R0, R1
    middle2[4] + middle2[5] +            # R2, R3
    middle1[6] + middle1[7] +            # B0, B1
    middle2[6] + middle2[7] +            # B2, B3
    middle1[0] + middle1[1] +            # L0, L1
    middle2[0] + middle2[1] +            # L2, L3
    d_face[0] + d_face[1] +              # D0, D1
    d2_face[0] + d2_face[1]              # D2, D3
)

print("State2:")
print(state2_str)
print()

# Convert to proper order (U, F, R, B, L, D)
state2_proper = (
    state2_str[0:4] +      # U
    state2_str[4:8] +      # F
    state2_str[8:12] +     # R
    state2_str[12:16] +    # B
    state2_str[16:20] +    # L
    state2_str[20:24]      # D
)

print("State2 (proper format):")
print(state2_proper)
print()

# Create cube from state2
cube = Cube(state2_proper)
print("Initial state as string:")
print(str(cube))
print()

# Test each single move from initial state
moves = ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2']

print("Testing all single moves from initial state:")
print()

results = {}
for move in moves:
    new_cube = cube.apply_move(move)
    new_state = str(new_cube)
    results[move] = new_state
    print(f"{move:3s}: {new_state}")

print()
print("=" * 80)
print()
print("Now testing sequences to find solution...")
print()

# Try to find solution manually
def find_solution_bfs(initial_state_str, max_depth=6):
    from collections import deque
    
    cube = Cube(initial_state_str)
    if cube.is_solved():
        return []
    
    queue = deque([(cube, [])])
    visited = {str(cube)}
    
    while queue:
        current_cube, path = queue.popleft()
        
        if len(path) > max_depth:
            continue
        
        if len(path) > 0:
            print(f"Depth {len(path)}: {' -> '.join(path)} = {str(current_cube)[:10]}...")
        
        for move in ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2']:
            next_cube = current_cube.apply_move(move)
            next_state = str(next_cube)
            
            if next_state not in visited:
                visited.add(next_state)
                new_path = path + [move]
                
                if next_cube.is_solved():
                    print(f"SOLUTION FOUND: {' -> '.join(new_path)}")
                    return new_path
                
                queue.append((next_cube, new_path))
    
    return None

solution = find_solution_bfs(state2_proper, max_depth=6)
if solution:
    print()
    print(f"Solution: {solution}")
else:
    print("No solution found within max depth")
