import random
from app import Cube, SOLVED_STATE_STR, _generate_file_content_from_state # Assuming app.py is in the same directory

# Initialize a solved cube
solved_cube = Cube(SOLVED_STATE_STR)

# Define possible moves
possible_moves = ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2']

# Apply two random moves
# Ensure the second move is not the inverse of the first to avoid cancelling out
move1 = random.choice(possible_moves)
intermediate_cube = solved_cube.apply_move(move1)

# Generate a list of moves that are not the inverse of move1
# This is a simplification; a truly robust check would involve more logic
# For a 2-move solution, just ensure the two moves are different
# and that applying the second one doesn't immediately solve it if the first was a simple inverse
# For now, a simple check that move2 is not the exact inverse of move1
# For example, if move1 is 'R', avoid 'R''
forbidden_move2 = None
if move1.endswith("'"):
    forbidden_move2 = move1[:-1]
elif move1.endswith("2"):
    forbidden_move2 = move1
else:
    forbidden_move2 = move1 + "'"

# Filter out the direct inverse (and itself if it's a 2-move)
filtered_possible_moves = [m for m in possible_moves if m != forbidden_move2 and m != move1]

# If filtering leaves no moves (unlikely for 2x2 with these moves), just pick any
if not filtered_possible_moves:
    filtered_possible_moves = possible_moves

move2 = random.choice(filtered_possible_moves)

# Apply the second move
final_cube = intermediate_cube.apply_move(move2)

# Convert the final cube state to the file format
state_char_list = list(str(final_cube))
file_content = _generate_file_content_from_state(state_char_list)

# Write to state2.txt
with open("state2.txt", "w") as f:
    f.write(file_content)

print(f"Generated state2.txt with 2 moves: {move1}, {move2}")
print("Content of state2.txt:")
print(file_content)
