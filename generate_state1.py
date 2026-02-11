import random
from app import Cube, SOLVED_STATE_STR, _generate_file_content_from_state # Assuming app.py is in the same directory

# Initialize a solved cube
solved_cube = Cube(SOLVED_STATE_STR)

# Define possible moves
possible_moves = ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2']

# Apply one random move to get a 1-move state
move = random.choice(possible_moves)
one_move_away_cube = solved_cube.apply_move(move)

# Convert the generated cube state to the file format
state_char_list = list(str(one_move_away_cube))
file_content = _generate_file_content_from_state(state_char_list)

# Write to state1.txt
with open("state1.txt", "w") as f:
    f.write(file_content)

print(f"Generated state1.txt with 1 move: {move}")
print("Content of state1.txt:")
print(file_content)
