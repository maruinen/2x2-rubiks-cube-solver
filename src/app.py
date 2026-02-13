import streamlit as st
import collections
import random
import time
import subprocess
import tempfile
import os

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
        # Each color takes 3 bits. Sticker 0 is least significant.
        packed_int |= (int_color << (i * 3))
    return packed_int

def _unpack_state(packed_int):
    state_char_list = [''] * 24
    for i in range(24):
        int_color = (packed_int >> (i * 3)) & 0b111 # Extract 3 bits
        state_char_list[i] = INT_TO_CHAR_COLOR[int_color]
    return "".join(state_char_list) # Return as string for now

# The solved state of a 2x2 cube
# Faces: U, F, R, B, L, D (Up, Front, Right, Back, Left, Down)
# Each face has 4 stickers.
# Example: U-face stickers are indices 0-3, F-face are 4-7, etc.
# This solved state assumes a standard color scheme:
# U: White, D: Yellow
# F: Green, B: Blue
# R: Red, L: Orange
SOLVED_STATE_STR = (
    'WWWW' +  # U-face (White)
    'GGGG' +  # F-face (Green)
    'RRRR' +  # R-face (Red)
    'BBBB' +  # B-face (Blue)
    'OOOO' +  # L-face (Orange)
    'YYYY'     # D-face (Yellow)
)

SOLVED_STATE_INT = _pack_state(list(SOLVED_STATE_STR))

# Sticker indices for each face (relative to their own face)
# U: 0, 1, 2, 3
# F: 4, 5, 6, 7
# R: 8, 9, 10, 11
# B: 12, 13, 14, 15
# L: 16, 17, 18, 19
# D: 20, 21, 22, 23


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

    def __hash__(self,):
        return hash(self.state)

    def __str__(self):
        return _unpack_state(self.state)

    def is_solved(self):
        return self.state == SOLVED_STATE_INT

    def _get_color(self, packed_state, index):
        return (packed_state >> (index * 3)) & 0b111

    def _set_color(self, packed_state, index, color_int):
        # Clear existing color at index
        packed_state &= ~ (0b111 << (index * 3))
        # Set new color
        packed_state |= (color_int << (index * 3))
        return packed_state

    def _rotate_face(self, packed_state, face_start_index):
        """Rotates a single face clockwise (4 stickers) on a packed integer state."""
        s = packed_state
        start = face_start_index

        # Extract colors (c0 = s[start], c1 = s[start+1], c2 = s[start+2], c3 = s[start+3])
        c0 = self._get_color(s, start)
        c1 = self._get_color(s, start + 1)
        c2 = self._get_color(s, start + 2)
        c3 = self._get_color(s, start + 3)

        # Apply rotation logic:
        # s[start] = s[start + 2]
        # s[start + 2] = s[start + 3]
        # s[start + 3] = s[start + 1]
        # s[start + 1] = temp (old s[start])
        s = self._set_color(s, start, c2)
        s = self._set_color(s, start + 2, c3)
        s = self._set_color(s, start + 3, c1)
        s = self._set_color(s, start + 1, c0)
        return s

    def apply_move(self, move):
        new_packed_state = self.state # Start with the current packed state

        # Helper to apply the move to the new_packed_state
        def _apply_single_move_packed(packed_state, m):
            temp_packed_state = packed_state
            if m == 'R':
                # Rotate R face
                temp_packed_state = self._rotate_face(temp_packed_state, 8) # R-face starts at index 8

                # Store all affected stickers before any modifications
                val_U1 = self._get_color(packed_state, 1)
                val_U3 = self._get_color(packed_state, 3)
                val_F1 = self._get_color(packed_state, 5)
                val_F3 = self._get_color(packed_state, 7)
                val_D1 = self._get_color(packed_state, 21)
                val_D3 = self._get_color(packed_state, 23)
                val_B3 = self._get_color(packed_state, 15)
                val_B1 = self._get_color(packed_state, 13)

                # Perform the cyclic assignments
                temp_packed_state = self._set_color(temp_packed_state, 1, val_B3) # U1 gets from B3
                temp_packed_state = self._set_color(temp_packed_state, 3, val_B1) # U3 gets from B1

                temp_packed_state = self._set_color(temp_packed_state, 5, val_U1) # F1 gets from U1
                temp_packed_state = self._set_color(temp_packed_state, 7, val_U3) # F3 gets from U3

                temp_packed_state = self._set_color(temp_packed_state, 21, val_F1) # D1 gets from F1
                temp_packed_state = self._set_color(temp_packed_state, 23, val_F3) # D3 gets from F3

                temp_packed_state = self._set_color(temp_packed_state, 15, val_D1) # B3 gets from D1
                temp_packed_state = self._set_color(temp_packed_state, 13, val_D3) # B1 gets from D3

            elif m == 'U':
                # Rotate U face
                temp_packed_state = self._rotate_face(temp_packed_state, 0) # U-face starts at index 0

                # Store all affected stickers before any modifications
                val_F0 = self._get_color(packed_state, 4)
                val_F1 = self._get_color(packed_state, 5)
                val_R0 = self._get_color(packed_state, 8)
                val_R1 = self._get_color(packed_state, 9)
                val_B0 = self._get_color(packed_state, 12)
                val_B1 = self._get_color(packed_state, 13)
                val_L0 = self._get_color(packed_state, 16)
                val_L1 = self._get_color(packed_state, 17)

                # Perform the cyclic assignments
                temp_packed_state = self._set_color(temp_packed_state, 4, val_R0) # F gets from R
                temp_packed_state = self._set_color(temp_packed_state, 5, val_R1)

                temp_packed_state = self._set_color(temp_packed_state, 8, val_B0) # R gets from B
                temp_packed_state = self._set_color(temp_packed_state, 9, val_B1)

                temp_packed_state = self._set_color(temp_packed_state, 12, val_L0) # B gets from L
                temp_packed_state = self._set_color(temp_packed_state, 13, val_L1)

                temp_packed_state = self._set_color(temp_packed_state, 16, val_F0) # L gets from F (stored earlier)
                temp_packed_state = self._set_color(temp_packed_state, 17, val_F1)
            
            elif m == 'F':
                # Rotate F face
                temp_packed_state = self._rotate_face(temp_packed_state, 4) # F-face starts at index 4

                # Store all affected stickers before any modifications
                val_U2 = self._get_color(packed_state, 2)
                val_U3 = self._get_color(packed_state, 3)
                val_R0 = self._get_color(packed_state, 8)
                val_R2 = self._get_color(packed_state, 10)
                val_D0 = self._get_color(packed_state, 20)
                val_D1 = self._get_color(packed_state, 21)
                val_L1 = self._get_color(packed_state, 17)
                val_L3 = self._get_color(packed_state, 19)

                # Perform the cyclic assignments
                # Forms two separate 4-cycles for proper inverse behavior
                # Cycle 1: 2 -> 8 -> 20 -> 17 -> 2
                # Cycle 2: 3 -> 10 -> 21 -> 19 -> 3
                temp_packed_state = self._set_color(temp_packed_state, 2, val_L1) # U gets from L (fixed!)
                temp_packed_state = self._set_color(temp_packed_state, 3, val_L3)

                temp_packed_state = self._set_color(temp_packed_state, 8, val_U2) # R gets from U
                temp_packed_state = self._set_color(temp_packed_state, 10, val_U3)

                temp_packed_state = self._set_color(temp_packed_state, 20, val_R0) # D gets from R
                temp_packed_state = self._set_color(temp_packed_state, 21, val_R2)

                temp_packed_state = self._set_color(temp_packed_state, 17, val_D0) # L gets from D
                temp_packed_state = self._set_color(temp_packed_state, 19, val_D1)

            else:
                raise ValueError(f"Invalid move: {m}")
            return temp_packed_state

        if move.endswith("'"): # Inverse move
            m = move[:-1]
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
        elif move.endswith("2"): # Double move
            m = move[:-1]
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
            new_packed_state = _apply_single_move_packed(new_packed_state, m)
        else: # Single move
            new_packed_state = _apply_single_move_packed(new_packed_state, move)

        return Cube(packed_state=new_packed_state)

    def get_possible_moves(self):
        """Returns a list of all valid moves for a 2x2 cube."""
        return ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2']

def solve_cube(initial_cube: Cube, max_depth: int = 10, updater_func=None):
    """
    Solves a 2x2 Rubik's cube using the C binary solver.
    Returns a list of moves to solve the cube.
    Raises RuntimeError if C solver fails or is not available.
    """
    print("[DEBUG] solve_cube() called", flush=True)
    print(f"[DEBUG] Cube state: {str(initial_cube)[:40]}...", flush=True)
    result = _try_c_solver(initial_cube)
    print(f"[DEBUG] solve_cube() returning: {result}", flush=True)
    return result


def _try_c_solver(cube: Cube):
    """
    Attempts to solve the cube using the C binary solver.
    Returns a list of moves on success.
    Raises RuntimeError with a descriptive message on failure.
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Look for solver binary in ../bin/solver relative to src/app.py
    solver_binary = os.path.join(os.path.dirname(script_dir), "bin", "solver")
    
    # DEBUG: Log to console
    print(f"[C SOLVER DEBUG] Looking for binary at: {solver_binary}", flush=True)
    print(f"[C SOLVER DEBUG] Binary exists: {os.path.exists(solver_binary)}", flush=True)
    print(f"[C SOLVER DEBUG] Is executable: {os.access(solver_binary, os.X_OK) if os.path.exists(solver_binary) else 'N/A'}", flush=True)
    
    if not os.path.exists(solver_binary):
        raise RuntimeError(f"❌ C solver binary not found at: {solver_binary}")
    
    # Create temporary file with cube state
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        # Convert cube state to file format
        state_list = list(str(cube))
        print(f"[C SOLVER DEBUG] Cube state string: {str(cube)}", flush=True)
        print(f"[C SOLVER DEBUG] State list length: {len(state_list)}", flush=True)
        lines = [
            f"{state_list[0]}{state_list[1]}",
            f"{state_list[2]}{state_list[3]}",
            f"{state_list[16]}{state_list[17]}{state_list[4]}{state_list[5]}{state_list[8]}{state_list[9]}{state_list[12]}{state_list[13]}",
            f"{state_list[18]}{state_list[19]}{state_list[6]}{state_list[7]}{state_list[10]}{state_list[11]}{state_list[14]}{state_list[15]}",
            f"{state_list[20]}{state_list[21]}",
            f"{state_list[22]}{state_list[23]}"
        ]
        print(f"[C SOLVER DEBUG] File content:\n" + "\n".join(lines), flush=True)
        f.write("\n".join(lines))
    
    try:
        try:
            # Call the C solver
            print(f"[C SOLVER DEBUG] Executing: {solver_binary} {temp_file}", flush=True)
            result = subprocess.run(
                [solver_binary, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"[C SOLVER DEBUG] Solver returned code: {result.returncode}", flush=True)
            print(f"[C SOLVER DEBUG] Stdout length: {len(result.stdout or '')}", flush=True)
            print(f"[C SOLVER DEBUG] Stderr length: {len(result.stderr or '')}", flush=True)
        except subprocess.TimeoutExpired:
            print(f"[C SOLVER DEBUG] Timeout!", flush=True)
            raise RuntimeError("❌ C solver timed out after 30 seconds")
        except FileNotFoundError as e:
            print(f"[C SOLVER DEBUG] FileNotFoundError: {e}", flush=True)
            raise RuntimeError(f"❌ C solver binary not executable or not found: {e}")
        
        if result.returncode != 0:
            stderr_snippet = (result.stderr or "")[:500]
            print(f"[C SOLVER DEBUG] Non-zero return code with stderr: {stderr_snippet}", flush=True)
            raise RuntimeError(f"❌ C solver exited with code {result.returncode}. Stderr: {stderr_snippet}")
        
        stdout = result.stdout or ""
        print(f"[C SOLVER DEBUG] Full stdout:\n{stdout}", flush=True)
        # If solver indicates solved with 0 moves
        if "Solution (0 moves)" in stdout:
            print("[C SOLVER DEBUG] Cube already solved, returning empty list", flush=True)
            return []
        
        # Parse output to extract solution moves
        print("[C SOLVER DEBUG] Parsing output lines...", flush=True)
        output_lines = stdout.strip().splitlines()
        print(f"[C SOLVER DEBUG] Output has {len(output_lines)} lines", flush=True)
        for i, line in enumerate(output_lines):
            print(f"[C SOLVER DEBUG] Line {i}: {line}", flush=True)
            if 'Solution' in line and 'moves' in line:
                print(f"[C SOLVER DEBUG] Found solution line at index {i}", flush=True)
                if i + 1 < len(output_lines):
                    moves_line = output_lines[i + 1].strip()
                    print(f"[C SOLVER DEBUG] Moves line: {moves_line}", flush=True)
                    if moves_line:
                        moves = [m.strip() for m in moves_line.split() if m.strip()]
                        print(f"[C SOLVER DEBUG] Parsed {len(moves)} moves: {moves}", flush=True)
                        return moves
                print("[C SOLVER DEBUG] No moves line found, returning empty", flush=True)
                return []
        
        # No recognizable solution output
        print("[C SOLVER DEBUG] No solution line found in output!", flush=True)
        raise RuntimeError(f"C solver returned no solution in stdout. Output: {(stdout or '')[:500]}")
    
    finally:
        if os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass


def _solve_cube_python(initial_cube: Cube, max_depth: int = 18, updater_func=None):
    """
    Solves a 2x2 Rubik's cube using Bidirectional Breadth-First Search (BFS) in Python.
    Returns a list of moves to solve the cube, or None if no solution is found.
    """
    if initial_cube.is_solved():
        return []

    solved_cube = Cube()
    
    # Forward search structures: state -> path
    fwd_visited = {initial_cube.state: []}
    fwd_queue = collections.deque([initial_cube.state])
    
    # Backward search structures: state -> path
    bwd_visited = {solved_cube.state: []}
    bwd_queue = collections.deque([solved_cube.state])

    def get_inverse_move(move):
        if move.endswith("'"): return move[0]
        if move.endswith("2"): return move
        return move + "'"

    def simplify_moves(moves):
        if not moves: return moves
        res = []
        for m in moves:
            if res and res[-1][0] == m[0]:
                # Combine same face moves
                f = m[0]
                m1 = res[-1][1:] or "1"
                m2 = m[1:] or "1"
                def to_val(x): return 2 if x=="2" else (3 if x=="'" else 1)
                val = (to_val(m1) + to_val(m2)) % 4
                res.pop()
                if val == 1: res.append(f)
                elif val == 2: res.append(f + "2")
                elif val == 3: res.append(f + "'")
            else:
                res.append(m)
        return res

    for depth in range((max_depth // 2) + 1):
        if updater_func:
            updater_func(f"Searching at depth: {depth * 2}")

        # Expand forward by one level
        for _ in range(len(fwd_queue)):
            curr_state = fwd_queue.popleft()
            path = fwd_visited[curr_state]
            last_move_face = path[-1][0] if path else None
            
            curr_cube = Cube(packed_state=curr_state)
            for move in curr_cube.get_possible_moves():
                if move[0] == last_move_face: continue
                next_cube = curr_cube.apply_move(move)
                if next_cube.state not in fwd_visited:
                    new_path = path + [move]
                    if next_cube.state in bwd_visited:
                        # Found a solution!
                        bwd_path = bwd_visited[next_cube.state]
                        full_solution = new_path + [get_inverse_move(m) for m in reversed(bwd_path)]
                        return simplify_moves(full_solution)
                    fwd_visited[next_cube.state] = new_path
                    fwd_queue.append(next_cube.state)

        # Expand backward by one level
        for _ in range(len(bwd_queue)):
            curr_state = bwd_queue.popleft()
            path = bwd_visited[curr_state]
            last_move_face = path[-1][0] if path else None

            curr_cube = Cube(packed_state=curr_state)
            for move in curr_cube.get_possible_moves():
                if move[0] == last_move_face: continue
                next_cube = curr_cube.apply_move(move)
                if next_cube.state not in bwd_visited:
                    new_path = path + [move]
                    if next_cube.state in fwd_visited:
                        # Found a solution!
                        fwd_path = fwd_visited[next_cube.state]
                        full_solution = fwd_path + [get_inverse_move(m) for m in reversed(new_path)]
                        return simplify_moves(full_solution)
                    bwd_visited[next_cube.state] = new_path
                    bwd_queue.append(next_cube.state)

    return None



# Helper functions for file I/O
def _generate_file_content_from_state(cube_state_list):
    """Generates the 6-line string content for saving to a file."""
    s = cube_state_list
    lines = [
        f"{s[0]}{s[1]}",
        f"{s[2]}{s[3]}",
        f"{s[16]}{s[17]}{s[4]}{s[5]}{s[8]}{s[9]}{s[12]}{s[13]}",
        f"{s[18]}{s[19]}{s[6]}{s[7]}{s[10]}{s[11]}{s[14]}{s[15]}",
        f"{s[20]}{s[21]}",
        f"{s[22]}{s[23]}"
    ]
    return "\n".join(lines)

def _parse_file_content_to_state(file_content):
    """Parses 6-line file content into a 24-character list."""
    lines = file_content.strip().split('\n')
    if len(lines) != 6:
        raise ValueError("File must contain exactly 6 lines for cube state.")
    
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

    # Validate colors
    for char_color in parsed_state:
        if char_color not in CHAR_TO_INT_COLOR:
            raise ValueError(f"Invalid color character '{char_color}' found in file.")
            
    # Validate total count of each color
    color_counts = collections.Counter(parsed_state)
    for color_char in COLOR_MAP.keys():
        if color_counts[color_char] != 4:
            raise ValueError(f"Invalid cube configuration: There must be exactly 4 '{color_char}' stickers. Found {color_counts[color_char]}.")

    return parsed_state

# Streamlit UI Placeholder
if __name__ == "__main__":
    # Initialize all session state variables
    if 'cube_input_state' not in st.session_state:
        st.session_state.cube_input_state = list(SOLVED_STATE_STR)
    if 'last_uploaded_filename' not in st.session_state:
        st.session_state.last_uploaded_filename = None
    if 'file_uploader_reset_counter' not in st.session_state:
        st.session_state.file_uploader_reset_counter = 0
    if 'show_solution' not in st.session_state:
        st.session_state.show_solution = False
    if 'solution_moves' not in st.session_state:
        st.session_state.solution_moves = None

    # Title with timestamp on the right
    col_title, col_time = st.columns([3, 1])
    with col_title:
        st.title("2x2 Rubik's Cube Solver")
    with col_time:
        from datetime import datetime
        # Get the last modified time of app.py
        app_file_path = os.path.abspath(__file__)
        mtime = os.path.getmtime(app_file_path)
        last_modified = datetime.fromtimestamp(mtime).strftime("%m/%d %H:%M:%S")
        st.markdown(f"<small style='color: gray'>Last update: {last_modified}</small>", unsafe_allow_html=True)
    
    st.write("Enter the current state of your 2x2 cube to get solving instructions.")

    st.sidebar.header("File I/O")
    st.sidebar.write("Load or save your cube state.")

    uploaded_file = st.sidebar.file_uploader("Upload Cube State (.txt)", type=["txt"], key=f"file_uploader_{st.session_state.file_uploader_reset_counter}")
    if uploaded_file is not None:
        print(f"[DEBUG FILE UPLOAD] File uploaded: {uploaded_file.name}", flush=True)
        # Prevent infinite rerun loop by checking if we've already processed this file
        if st.session_state.last_uploaded_filename != uploaded_file.name:
            print(f"[DEBUG FILE UPLOAD] Processing new file: {uploaded_file.name}", flush=True)
            try:
                file_content = uploaded_file.read().decode("utf-8")
                print("[DEBUG FILE UPLOAD] File content read successfully", flush=True)
                loaded_state = _parse_file_content_to_state(file_content)
                print(f"[DEBUG FILE UPLOAD] Parsed state: {' '.join(loaded_state)}", flush=True)
                st.session_state.cube_input_state = loaded_state
                st.session_state.last_uploaded_filename = uploaded_file.name
                st.session_state.show_solution = False  # Clear solution when loading new file
                st.session_state.solution_moves = None
                print("[DEBUG FILE UPLOAD] Session state updated, about to rerun", flush=True)
                st.sidebar.success("Cube state loaded successfully!")
                st.rerun() # Rerun to update the main display with the new state
            except Exception as e:
                print(f"[DEBUG FILE UPLOAD] Error: {e}", flush=True)
                st.sidebar.error(f"Error loading file: {e}")
        else:
            print(f"[DEBUG FILE UPLOAD] File already processed, skipping rerun", flush=True)

    # Generate file content for download - moved after session state initialization
    current_state_for_download = _generate_file_content_from_state(st.session_state.cube_input_state)
    st.sidebar.download_button(
        label="Download Current State",
        data=current_state_for_download,
        file_name="cube_state.txt",
        mime="text/plain",
        key="download_button"
    )
    st.sidebar.markdown("---") # Separator

    st.sidebar.header("Instructions")
    st.sidebar.write("""
        Input the colors for each sticker on your 2x2 Rubik's Cube.
        Use the following single-letter abbreviations for colors:
        - **W**: White
        - **Y**: Yellow
        - **R**: Red
        - **O**: Orange
        - **B**: Blue
        - **G**: Green
        
        Ensure you enter 24 colors in total.

        ---

        **Sticker Index Mapping (Unfolded Cube):**
        This diagram shows the layout of the 24 stickers on the 6 faces.
        Each number corresponds to the sticker index in the input fields.

        ```
            +---+---+
            | 0 | 1 |
            +---+---+
            | 2 | 3 |    (U - Up Face)
            +---+---+
        +---+---+---+---+---+---+---+---+
        |16 |17 | 4 | 5 | 8 | 9 |12 |13 |
        +---+---+---+---+---+---+---+---+
        |18 |19 | 6 | 7 |10 |11 |14 |15 |
        +---+---+---+---+---+---+---+---+
        (L - Left) (F - Front) (R - Right) (B - Back)

            +---+---+
            |20 |21 |
            +---+---+
            |22 |23 |    (D - Down Face)
            +---+---+
        ```
        """)

    # Helper function to create a face input
    def create_face_input(face_name, indices_on_cube_state, current_inputs):
        st.markdown(f'<div class="face-label">{face_name}</div>', unsafe_allow_html=True)
        
        # Use Streamlit columns to create a 2x2 grid-like layout for input fields
        # Each input will have a clear label showing its index
        
        col_row1_1, col_row1_2 = st.columns(2)
        with col_row1_1:
            val0 = st.text_input(label=f'Sticker {indices_on_cube_state[0]}', value=current_inputs[indices_on_cube_state[0]], max_chars=1, key=f'{face_name}_0')
        with col_row1_2:
            val1 = st.text_input(label=f'Sticker {indices_on_cube_state[1]}', value=current_inputs[indices_on_cube_state[1]], max_chars=1, key=f'{face_name}_1')

        col_row2_1, col_row2_2 = st.columns(2)
        with col_row2_1:
            val2 = st.text_input(label=f'Sticker {indices_on_cube_state[2]}', value=current_inputs[indices_on_cube_state[2]], max_chars=1, key=f'{face_name}_2')
        with col_row2_2:
            val3 = st.text_input(label=f'Sticker {indices_on_cube_state[3]}', value=current_inputs[indices_on_cube_state[3]], max_chars=1, key=f'{face_name}_3')
        
        # Update the session state with the new values
        st.session_state.cube_input_state[indices_on_cube_state[0]] = val0
        st.session_state.cube_input_state[indices_on_cube_state[1]] = val1
        st.session_state.cube_input_state[indices_on_cube_state[2]] = val2
        st.session_state.cube_input_state[indices_on_cube_state[3]] = val3

    # Define the layout of faces and their sticker indices in the 24-character string
    # U, F, R, B, L, D
    face_indices = {
        "U (Up)": [0, 1, 2, 3],
        "F (Front)": [4, 5, 6, 7],
        "R (Right)": [8, 9, 10, 11],
        "B (Back)": [12, 13, 14, 15],
        "L (Left)": [16, 17, 18, 19],
        "D (Down)": [20, 21, 22, 23],
    }

    # Arrangement of faces for better visualization (like a cross)

    # U face
    st.markdown("### U (Up) Face") # Add a heading for clarity
    u_cols = st.columns([1, 2, 1]) # Center U face
    with u_cols[1]:
        create_face_input("U (Up)", face_indices["U (Up)"], st.session_state.cube_input_state)

    st.write("---") # Separator

    # L, F, R, B faces
    st.markdown("### Middle Faces (Left, Front, Right, Back)") # Add a heading for clarity
    main_cols = st.columns(4)
    with main_cols[0]:
        create_face_input("L (Left)", face_indices["L (Left)"], st.session_state.cube_input_state)
    with main_cols[1]:
        create_face_input("F (Front)", face_indices["F (Front)"], st.session_state.cube_input_state)
    with main_cols[2]:
        create_face_input("R (Right)", face_indices["R (Right)"], st.session_state.cube_input_state)
    with main_cols[3]:
        create_face_input("B (Back)", face_indices["B (Back)"], st.session_state.cube_input_state)

    st.write("---") # Separator

    # D face
    st.markdown("### D (Down) Face") # Add a heading for clarity
    d_cols = st.columns([1, 2, 1]) # Center D face
    with d_cols[1]:
        create_face_input("D (Down)", face_indices["D (Down)"], st.session_state.cube_input_state)


    # Collect the current input state
    current_cube_state_str = "".join(st.session_state.cube_input_state).upper()



    # --- Standard Face Rotations ---
    st.subheader("Standard Face Rotations")
    st.write("Click a button to apply a standard cube face rotation.")

    def apply_streamlit_move(move_str):
        current_state_str = "".join(st.session_state.cube_input_state).upper()
        current_cube = Cube(current_state_str)
        new_cube = current_cube.apply_move(move_str)
        st.session_state.cube_input_state = list(str(new_cube))
        st.session_state.show_solution = False  # Clear solution when applying moves
        st.session_state.solution_moves = None
        st.rerun()

    # Layout for the rotation buttons
    rot_cols1 = st.columns(3)
    with rot_cols1[0]:
        if st.button("U"):
            apply_streamlit_move('U')
    with rot_cols1[1]:
        if st.button("U'"):
            apply_streamlit_move("U'")
    with rot_cols1[2]:
        if st.button("U2"):
            apply_streamlit_move("U2")

    rot_cols2 = st.columns(3)
    with rot_cols2[0]:
        if st.button("F"):
            apply_streamlit_move('F')
    with rot_cols2[1]:
        if st.button("F'"):
            apply_streamlit_move("F'")
    with rot_cols2[2]:
        if st.button("F2"):
            apply_streamlit_move("F2")

    rot_cols3 = st.columns(3)
    with rot_cols3[0]:
        if st.button("R"):
            apply_streamlit_move('R')
    with rot_cols3[1]:
        if st.button("R'"):
            apply_streamlit_move("R'")
    with rot_cols3[2]:
        if st.button("R2"):
            apply_streamlit_move("R2")

    col_solve, col_reset = st.columns(2)
    with col_solve:
        if st.button("Solve Cube"):
            # 1. Ensure exactly 24 color inputs are provided
            if len(current_cube_state_str) != 24:
                st.error(f"Please enter exactly 24 colors. Currently, {len(current_cube_state_str)} colors are entered.")
            # 2. Check for valid color characters
            elif not all(c in COLOR_MAP for c in current_cube_state_str):
                st.error("Invalid color character(s) detected. Please use W, Y, R, O, B, G.")
            else:
                # 3. Verify the count of each color (e.g., 4 white, 4 yellow, 4 red, etc.)
                color_counts = collections.Counter(current_cube_state_str)
                valid_counts = True
                for color in COLOR_MAP.keys():
                    if color_counts[color] != 4:
                        st.error(f"Invalid cube configuration: There must be exactly 4 '{color}' stickers. Found {color_counts[color]}.")
                        valid_counts = False
                        break
                
                if valid_counts:
                    # 4. Basic check for a valid cube configuration (e.g., each corner piece has 3 distinct colors)
                    # This is a complex check for a 2x2. A simpler initial check can be
                    # if the sum of all colors is correct (which we already did) and that
                    # opposite faces have certain colors (e.g. W opposite Y, R opposite O, G opposite B)
                    # For a rigorous check, one would need to analyze permutations/orientations.
                    # For now, we rely on the total color count as a primary validation.
                    # More advanced validation can be added later if needed.

                    # Attempt to create a Cube object, which also has some internal validation
                    try:
                        initial_cube = Cube(current_cube_state_str)
                        st.success("Cube input is valid. Attempting to solve...")
                        
                        progress_placeholder = st.empty()
                        def update_progress(message):
                            progress_placeholder.write(message)

                        # Call the solver
                        progress_placeholder.info("🔍 Attempting to use C solver...")
                        print("[DEBUG UI] About to call solve_cube()", flush=True)
                        try:
                            print("[DEBUG UI] Calling solve_cube()...", flush=True)
                            solution_moves = solve_cube(initial_cube, updater_func=update_progress)
                            print(f"[DEBUG UI] solve_cube() returned: {solution_moves}", flush=True)
                            progress_placeholder.empty() # Clear the progress message after solving

                            print(f"[DEBUG UI] solution_moves type: {type(solution_moves)}, len: {len(solution_moves) if solution_moves else 'None'}", flush=True)
                            # Store in session state so it persists through reruns
                            st.session_state.solution_moves = solution_moves
                            st.session_state.show_solution = True
                            progress_placeholder.empty()
                            st.rerun()
                        except RuntimeError as e:
                            print(f"[DEBUG UI] RuntimeError caught: {e}", flush=True)
                            progress_placeholder.empty()
                            st.error(f"**C Solver Error:** {e}")
                        except Exception as e:
                            print(f"[DEBUG UI] Exception caught: {type(e).__name__}: {e}", flush=True)
                            progress_placeholder.empty()
                            st.error(f"**Unexpected error:** {type(e).__name__}: {e}")

                    except ValueError as e:
                        st.error(f"Cube configuration error: {e}")

    with col_reset:
        if st.button("Reset Cube"):
            st.session_state.cube_input_state = list(SOLVED_STATE_STR)
            st.session_state.show_solution = False
            st.session_state.solution_moves = None
            st.session_state.last_uploaded_filename = None
            st.session_state.file_uploader_reset_counter += 1
            st.rerun()

    # Display persistent solution if available
    if st.session_state.show_solution and st.session_state.solution_moves is not None:
        st.write("---")
        if len(st.session_state.solution_moves) == 0:
            st.info("✅ The cube is already solved!")
        else:
            st.subheader("✅ Solution Found!")
            st.write(f"**Number of moves:** {len(st.session_state.solution_moves)}")
            st.write(f"**Solution:** {' → '.join(st.session_state.solution_moves)}")

    # TODO: Implement solver logic (BFS) - Partially done with solve_cube function
    # TODO: Display solution