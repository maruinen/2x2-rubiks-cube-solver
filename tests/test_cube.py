import unittest
from src.app import Cube, SOLVED_STATE_STR

class TestCube(unittest.TestCase):

    def test_initial_solved_state(self):
        cube = Cube()
        self.assertTrue(cube.is_solved())
        self.assertEqual(str(cube), SOLVED_STATE_STR)

    def test_R_move(self):
        cube = Cube()
        # Apply R move to a solved cube
        moved_cube = cube.apply_move('R')
        
        # After R move on solved:
        # Original: U1=W, U3=W, F1=G, F3=G, D1=Y, D3=Y, B1=B, B3=B
        # Expected:
        # U1 should be B (from B3)
        # U3 should be B (from B1)
        # F1 should be W (from U1)
        # F3 should be W (from U3)
        # D1 should be G (from F1)
        # D3 should be G (from F3)
        # B3 should be Y (from D1)
        # B1 should be Y (from D3)
        
        self.assertEqual(str(moved_cube)[1], 'B') # U1
        self.assertEqual(str(moved_cube)[3], 'B') # U3
        self.assertEqual(str(moved_cube)[5], 'W') # F1
        self.assertEqual(str(moved_cube)[7], 'W') # F3
        self.assertEqual(str(moved_cube)[21], 'G') # D1
        self.assertEqual(str(moved_cube)[23], 'G') # D3
        self.assertEqual(str(moved_cube)[15], 'Y') # B3
        self.assertEqual(str(moved_cube)[13], 'Y') # B1

        # Check that applying R three more times returns to solved
        restored_cube = moved_cube.apply_move('R').apply_move('R').apply_move('R')
        self.assertTrue(restored_cube.is_solved())

    def test_R_prime_move(self):
        cube = Cube()
        moved_cube = cube.apply_move("R'")
        # R' is equivalent to R three times.
        # This test checks if R' correctly inverts R.
        restored_cube = moved_cube.apply_move('R')
        self.assertTrue(restored_cube.is_solved())

    def test_R2_move(self):
        cube = Cube()
        moved_cube = cube.apply_move("R2")
        # R2 is equivalent to R twice.
        restored_cube = moved_cube.apply_move('R2')
        self.assertTrue(restored_cube.is_solved())

    def test_U_move(self):
        cube = Cube()
        moved_cube = cube.apply_move('U')
        
        # Affected cross-face stickers (F, R, B, L)
        # Original: F0=G, F1=G, R0=R, R1=R, B0=B, B1=B, L0=O, L1=O
        # Expected:
        # F0 should be R (from R0)
        # F1 should be R (from R1)
        # R0 should be B (from B0)
        # R1 should be B (from B1)
        # B0 should be O (from L0)
        # B1 should be O (from L1)
        # L0 should be G (from F0)
        # L1 should be G (from F1)

        self.assertEqual(str(moved_cube)[4], 'R') # F0
        self.assertEqual(str(moved_cube)[5], 'R') # F1
        self.assertEqual(str(moved_cube)[8], 'B') # R0
        self.assertEqual(str(moved_cube)[9], 'B') # R1
        self.assertEqual(str(moved_cube)[12], 'O') # B0
        self.assertEqual(str(moved_cube)[13], 'O') # B1
        self.assertEqual(str(moved_cube)[16], 'G') # L0
        self.assertEqual(str(moved_cube)[17], 'G') # L1

    def test_F_move(self):
        cube = Cube()
        moved_cube = cube.apply_move('F')

        # Affected cross-face stickers (U, R, D, L)
        # Original: U2=W, U3=W, R0=R, R2=R, D0=Y, D1=Y, L1=O, L3=O
        # Expected:
        # U2 should be O (from L3)
        # U3 should be O (from L1)
        # R0 should be W (from U2)
        # R2 should be W (from U3)
        # D0 should be R (from R0)
        # D1 should be R (from R2)
        # L3 should be Y (from D1)
        # L1 should be Y (from D0)

        self.assertEqual(str(moved_cube)[2], 'O') # U2
        self.assertEqual(str(moved_cube)[3], 'O') # U3
        self.assertEqual(str(moved_cube)[8], 'W') # R0
        self.assertEqual(str(moved_cube)[10], 'W') # R2
        self.assertEqual(str(moved_cube)[20], 'R') # D0
        self.assertEqual(str(moved_cube)[21], 'R') # D1
        self.assertEqual(str(moved_cube)[19], 'Y') # L3
        self.assertEqual(str(moved_cube)[17], 'Y') # L1
