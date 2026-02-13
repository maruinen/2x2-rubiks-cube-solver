import unittest
import subprocess
import os
import tempfile

# --- Cube Logic extracted from src/app.py ---
COLOR_MAP = {
    'W': 'white', 'Y': 'yellow', 'R': 'red', 'O': 'orange', 'B': 'blue', 'G': 'green'
}
CHAR_TO_INT_COLOR = {
    'W': 0, 'Y': 1, 'R': 2, 'O': 3, 'B': 4, 'G': 5
}
INT_TO_CHAR_COLOR = {v: k for k, v in CHAR_TO_INT_COLOR.items()}

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
    'WWWW' + 'GGGG' + 'RRRR' + 'BBBB' + 'OOOO' + 'YYYY'
)
SOLVED_STATE_INT = _pack_state(list(SOLVED_STATE_STR))

class Cube:
    def __init__(self, state_str=None, packed_state=None):
        if state_str is not None:
            self.state = _pack_state(list(state_str))
        elif packed_state is not None:
            self.state = packed_state
        else:
            self.state = SOLVED_STATE_INT

    def __str__(self):
        return _unpack_state(self.state)

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
                temp_packed_state = self._set_color(temp_packed_state, 4, val_R0)
                temp_packed_state = self._set_color(temp_packed_state, 5, val_R1)
                temp_packed_state = self._set_color(temp_packed_state, 8, val_B0)
                temp_packed_state = self._set_color(temp_packed_state, 9, val_B1)
                temp_packed_state = self._set_color(temp_packed_state, 12, val_L0)
                temp_packed_state = self._set_color(temp_packed_state, 13, val_L1)
                temp_packed_state = self._set_color(temp_packed_state, 16, val_F0)
                temp_packed_state = self._set_color(temp_packed_state, 17, val_F1)
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
                temp_packed_state = self._set_color(temp_packed_state, 2, val_L1)
                temp_packed_state = self._set_color(temp_packed_state, 3, val_L3)
                temp_packed_state = self._set_color(temp_packed_state, 8, val_U2)
                temp_packed_state = self._set_color(temp_packed_state, 10, val_U3)
                temp_packed_state = self._set_color(temp_packed_state, 20, val_R0)
                temp_packed_state = self._set_color(temp_packed_state, 21, val_R2)
                temp_packed_state = self._set_color(temp_packed_state, 17, val_D0)
                temp_packed_state = self._set_color(temp_packed_state, 19, val_D1)
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

# --- Test Logic ---

class TestIssue11(unittest.TestCase):
    def setUp(self):
        # Locate the solver binary
        # This file is in tests/, so bin/solver is in ../bin/solver
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.solver_path = os.path.join(os.path.dirname(self.test_dir), "bin", "solver")
        if not os.path.exists(self.solver_path):
            self.fail(f"Solver binary not found at {self.solver_path}. Please run 'make build' first.")

    def run_solver(self, cube):
        state_list = list(str(cube))
        lines = [
            f"{state_list[0]}{state_list[1]}",
            f"{state_list[2]}{state_list[3]}",
            f"{state_list[16]}{state_list[17]}{state_list[4]}{state_list[5]}{state_list[8]}{state_list[9]}{state_list[12]}{state_list[13]}",
            f"{state_list[18]}{state_list[19]}{state_list[6]}{state_list[7]}{state_list[10]}{state_list[11]}{state_list[14]}{state_list[15]}",
            f"{state_list[20]}{state_list[21]}",
            f"{state_list[22]}{state_list[23]}"
        ]
        content = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            tmpname = f.name
        
        try:
            result = subprocess.run([self.solver_path, tmpname], capture_output=True, text=True, timeout=30)
            return result
        finally:
            if os.path.exists(tmpname):
                os.unlink(tmpname)

    def test_working_sequence(self):
        # U, F, R, U, F, R, U (7 moves)
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting working sequence: {moves}")
        result = self.run_solver(cube)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}...")
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_failing_sequence(self):
        # U, F, R, U, F, R, U, F (8 moves)
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
            
        print(f"\nTesting failing sequence (8 moves): {moves}")
        result = self.run_solver(cube)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}...")
        
        self.assertEqual(result.returncode, 0, "Solver failed (non-zero return code)")
        self.assertIn("Solution", result.stdout, "Solver did not find a solution")

    def test_sequence_9_moves(self):
        # U, F, R, U, F, R, U, F, R
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (9 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_sequence_10_moves(self):
        # U, F, R, U, F, R, U, F, R, U
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (10 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_sequence_11_moves(self):
        # U, F, R, U, F, R, U, F, R, U, F
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (11 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_sequence_12_moves(self):
        # U, F, R, U, F, R, U, F, R, U, F, R
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (12 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_sequence_15_moves(self):
        # U, F, R, U, F, R, U, F, R, U, F, R, U, F, R
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (15 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

    def test_sequence_18_moves(self):
        # U, F, R, U, F, R, U, F, R, U, F, R, U, F, R, U, F, R
        moves = ['U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R', 'U', 'F', 'R']
        cube = Cube()
        for m in moves:
            cube = cube.apply_move(m)
        
        print(f"\nTesting sequence (18 moves): {moves}")
        result = self.run_solver(cube)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Solution", result.stdout)

if __name__ == '__main__':
    unittest.main()
