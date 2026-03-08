import collections
import os

# --- Extracted from app.py ---
# Define color mappings
COLOR_MAP = {
    'W': 'white',
    'Y': 'yellow',
    'R': 'red',
    'O': 'orange',
    'B': 'blue',
    'G': 'green'
}

# Color to integer mapping for packing
CHAR_TO_INT_COLOR = {
    'W': 0, 'Y': 1, 'R': 2, 'O': 3, 'B': 4, 'G': 5
}
INT_TO_CHAR_COLOR = {v: k for k, v in CHAR_TO_INT_COLOR.items()}

# Helper for packing/unpacking cube state into a single integer
def _pack_state(state_char_list):
    packed_int = 0
    for i, char_color in enumerate(state_char_list):
        int_color = CHAR_TO_INT_COLOR[char_color]
        packed_int |= (int_color << (i * 3))
    return packed_int

def _unpack_state(packed_int):
    state_char_list = [''] * 24
    for i in range(24):
        int_color = (packed_int >> (i * 3)) & 0b111
        state_char_list[i] = INT_TO_CHAR_COLOR[int_color]
    return "".join(state_char_list)

SOLVED_STATE_STR = (
    'WWWW' +  # U-face (White)
    'GGGG' +  # F-face (Green)
    'RRRR' +  # R-face (Red)
    'BBBB' +  # B-face (Blue)
    'OOOO' +  # L-face (Orange)
    'YYYY'     # D-face (Yellow)
)

SOLVED_STATE_INT = _pack_state(list(SOLVED_STATE_STR))

class Cube:
    def __init__(self, state_str=None, packed_state=None):
        if state_str is not None:
            if len(state_str) != 24:
                raise ValueError("Cube state string must be 24 characters long.")
            if not all(c in CHAR_TO_INT_COLOR for c in state_str):
                raise ValueError("Cube state string contains invalid colors.")
            self.state = _pack_state(list(state_str))
        elif packed_state is not None:
            self.state = packed_state
        else:
            self.state = SOLVED_STATE_INT

    def __eq__(self, other):
        return isinstance(other, Cube) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def __str__(self):
        return _unpack_state(self.state)

    def is_solved(self):
        return self.state == SOLVED_STATE_INT

    def _get_color(self, packed_state, index):
        return (packed_state >> (index * 3)) & 0b111

    def _set_color(self, packed_state, index, color_int):
        packed_state &= ~ (0b111 << (index * 3))
        packed_state |= (color_int << (index * 3))
        return packed_state

    def _rotate_face(self, packed_state, face_start_index):
        s = packed_state
        start = face_start_index
        c0 = self._get_color(s, start)
        c1 = self._get_color(s, start + 1)
        c2 = self._get_color(s, start + 2)
        c3 = self._get_color(s, start + 3)
        s = self._set_color(s, start, c2)
        s = self._set_color(s, start + 2, c3)
        s = self._set_color(s, start + 3, c1)
        s = self._set_color(s, start + 1, c0)
        return s

    def apply_move(self, move):
        new_packed_state = self.state
        def _apply_single_move_packed(packed_state, m):
            temp_packed_state = packed_state
            if m == 'R':
                temp_packed_state = self._rotate_face(temp_packed_state, 8)
                val_U1 = self._get_color(packed_state, 1)
                val_U3 = self._get_color(packed_state, 3)
                val_F1 = self._get_color(packed_state, 5)
                val_F3 = self._get_color(packed_state, 7)
                val_D1 = self._get_color(packed_state, 21)
                val_D3 = self._get_color(packed_state, 23)
                val_B3 = self._get_color(packed_state, 15)
                val_B1 = self._get_color(packed_state, 13)
                temp_packed_state = self._set_color(temp_packed_state, 1, val_B3)
                temp_packed_state = self._set_color(temp_packed_state, 3, val_B1)
                temp_packed_state = self._set_color(temp_packed_state, 5, val_U1)
                temp_packed_state = self._set_color(temp_packed_state, 7, val_U3)
                temp_packed_state = self._set_color(temp_packed_state, 21, val_F1)
                temp_packed_state = self._set_color(temp_packed_state, 23, val_F3)
                temp_packed_state = self._set_color(temp_packed_state, 15, val_D1)
                temp_packed_state = self._set_color(temp_packed_state, 13, val_D3)
            elif m == 'U':
                temp_packed_state = self._rotate_face(temp_packed_state, 0)
                val_F0 = self._get_color(packed_state, 4)
                val_F1 = self._get_color(packed_state, 5)
                val_R0 = self._get_color(packed_state, 8)
                val_R1 = self._get_color(packed_state, 9)
                val_B0 = self._get_color(packed_state, 12)
                val_B1 = self._get_color(packed_state, 13)
                val_L0 = self._get_color(packed_state, 16)
                val_L1 = self._get_color(packed_state, 17)
                set_color_func = self._set_color # Alias for brevity
                temp_packed_state = set_color_func(temp_packed_state, 4, val_R0)
                temp_packed_state = set_color_func(temp_packed_state, 5, val_R1)
                temp_packed_state = set_color_func(temp_packed_state, 8, val_B0)
                temp_packed_state = set_color_func(temp_packed_state, 9, val_B1)
                temp_packed_state = set_color_func(temp_packed_state, 12, val_L0)
                temp_packed_state = set_color_func(temp_packed_state, 13, val_L1)
                temp_packed_state = set_color_func(temp_packed_state, 16, val_F0)
                temp_packed_state = set_color_func(temp_packed_state, 17, val_F1)
            elif m == 'F':
                temp_packed_state = self._rotate_face(temp_packed_state, 4)
                val_U2 = self._get_color(packed_state, 2)
                val_U3 = self._get_color(packed_state, 3)
                val_R0 = self._get_color(packed_state, 8)
                val_R2 = self._get_color(packed_state, 10)
                val_D0 = self._get_color(packed_state, 20)
                val_D1 = self._get_color(packed_state, 21)
                val_L1 = self._get_color(packed_state, 17)
                val_L3 = self._get_color(packed_state, 19)
                set_color_func = self._set_color
                temp_packed_state = set_color_func(temp_packed_state, 2, val_L1)
                temp_packed_state = set_color_func(temp_packed_state, 3, val_L3)
                temp_packed_state = set_color_func(temp_packed_state, 8, val_U2)
                temp_packed_state = set_color_func(temp_packed_state, 10, val_U3)
                temp_packed_state = set_color_func(temp_packed_state, 20, val_R0)
                temp_packed_state = set_color_func(temp_packed_state, 21, val_R2)
                temp_packed_state = set_color_func(temp_packed_state, 17, val_D0)
                temp_packed_state = set_color_func(temp_packed_state, 19, val_D1)
            else:
                raise ValueError(f"Invalid move: {m}")
            return temp_packed_state

        if move.endswith("'"):
            m = move[:-1]
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
        elif move.endswith("2"):
            m = move[:-1]
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
        else:
            new_packed_state = _apply_single_move_packed(new_packed_state, move)
        return Cube(packed_state=new_packed_state)

# Helper function to generate file content string from a 24-char state string
def generate_file_content(state_24_char_str):
    s = list(state_24_char_str)
    lines = [
        f"{s[0]}{s[1]}",
        f"{s[2]}{s[3]}",
        f"{s[16]}{s[17]}{s[4]}{s[5]}{s[8]}{s[9]}{s[12]}{s[13]}",
        f"{s[18]}{s[19]}{s[6]}{s[7]}{s[10]}{s[11]}{s[14]}{s[15]}",
        f"{s[20]}{s[21]}",
        f"{s[22]}{s[23]}"
    ]
    return "
".join(lines)

# --- Main script to generate states ---
if __name__ == "__main__":
    solved_cube = Cube()

    # Generate state1.txt (R move)
    cube_state1 = solved_cube.apply_move("R")
    with open("state1.txt", "w") as f:
        f.write(generate_file_content(str(cube_state1)))
    print("Generated state1.txt (R move)")

    # Generate state2.txt (R then U moves)
    cube_state2 = solved_cube.apply_move("R").apply_move("U")
    with open("state2.txt", "w") as f:
        f.write(generate_file_content(str(cube_state2)))
    print("Generated state2.txt (R U moves)")

    # Generate state3.txt (R then U then F moves)
    cube_state3 = solved_cube.apply_move("R").apply_move("U").apply_move("F")
    with open("state3.txt", "w") as f:
        f.write(generate_file_content(str(cube_state3)))
    print("Generated state3.txt (R U F moves)")