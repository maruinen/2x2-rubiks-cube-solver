import unittest
from app import Cube, SOLVED_STATE_STR

class TestCube(unittest.TestCase):

    def test_initial_solved_state(self):
        cube = Cube()
        self.assertTrue(cube.is_solved())
        self.assertEqual(str(cube), SOLVED_STATE_STR)

    def test_R_move(self):
        cube = Cube()
        # Apply R move to a solved cube
        moved_cube = cube.apply_move('R')
        
        # Manually determine the expected state after an R move from solved.
        # This will be complex, so let's check a few key stickers affected.
        # U face (WWWW)
        # F face (GGGG)
        # R face (RRRR)
        # B face (BBBB)
        # L face (OOOO)
        # D face (YYYY)

        # R face rotates
        # R0 R1   -> R2 R0
        # R2 R3   -> R3 R1
        # Indices 8,9,10,11
        # Original: RRRR
        # Expected new R face: RRRR (same colors, just shifted within the face)
        self.assertEqual(moved_cube.state[8], 'R')
        self.assertEqual(moved_cube.state[9], 'R')
        self.assertEqual(moved_cube.state[10], 'R')
        self.assertEqual(moved_cube.state[11], 'R')

        # Affected cross-face stickers (U, F, D, B)
        # U1 (index 1) moves to F1 (index 5)
        # U3 (index 3) moves to F3 (index 7)
        # F1 (index 5) moves to D1 (index 21)
        # F3 (index 7) moves to D3 (index 23)
        # D1 (index 21) moves to B3 (index 15) -- NOTE: B indices are reversed
        # D3 (index 23) moves to B1 (index 13) -- NOTE: B indices are reversed
        # B1 (index 13) moves to U3 (index 3)
        # B3 (index 15) moves to U1 (index 1)

        # After R move on solved:
        # Original: U1=W, U3=W, F1=G, F3=G, D1=Y, D3=Y, B1=B, B3=B
        # Expected:
        # F1 should be W (from U1) -> moved_cube.state[5] == 'W'
        # F3 should be W (from U3) -> moved_cube.state[7] == 'W'
        # D1 should be G (from F1) -> moved_cube.state[21] == 'G'
        # D3 should be G (from F3) -> moved_cube.state[23] == 'G'
        # B3 should be Y (from D1) -> moved_cube.state[15] == 'Y' (B3 is D1)
        # B1 should be Y (from D3) -> moved_cube.state[13] == 'Y' (B1 is D3)
        # U1 should be B (from B3) -> moved_cube.state[1] == 'B' (U1 is B3)
        # U3 should be B (from B1) -> moved_cube.state[3] == 'B' (U3 is B1)
        
        self.assertEqual(moved_cube.state[5], 'W')
        self.assertEqual(moved_cube.state[7], 'W')
        self.assertEqual(moved_cube.state[21], 'G')
        self.assertEqual(moved_cube.state[23], 'G')
        self.assertEqual(moved_cube.state[15], 'Y') # This is the former D1
        self.assertEqual(moved_cube.state[13], 'Y') # This is the former D3
        self.assertEqual(moved_cube.state[1], 'B')
        self.assertEqual(moved_cube.state[3], 'B')

        # Check that applying R three more times returns to solved
        restored_cube = moved_cube.apply_move('R').apply_move('R').apply_move('R')
        self.assertEqual(str(restored_cube), SOLVED_STATE_STR)

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
        
        # U face rotates
        # U0 U1   -> U2 U0
        # U2 U3   -> U3 U1
        # Indices 0,1,2,3
        # Original: WWWW
        # Expected new U face: WWWW (same colors, just shifted)
        self.assertEqual(moved_cube.state[0], 'W')
        self.assertEqual(moved_cube.state[1], 'W')
        self.assertEqual(moved_cube.state[2], 'W')
        self.assertEqual(moved_cube.state[3], 'W')

        # Affected cross-face stickers (F, R, B, L)
        # F0, F1 (indices 4,5) moves to L0, L1 (indices 16,17)
        # R0, R1 (indices 8,9) moves to F0, F1 (indices 4,5)
        # B0, B1 (indices 12,13) moves to R0, R1 (indices 8,9)
        # L0, L1 (indices 16,17) moves to B0, B1 (indices 12,13)

        # After U move on solved:
        # Original: F0=G, F1=G, R0=R, R1=R, B0=B, B1=B, L0=O, L1=O
        # Expected:
        # L0 should be G (from F0) -> moved_cube.state[16] == 'G'
        # L1 should be G (from F1) -> moved_cube.state[17] == 'G'
        # F0 should be R (from R0) -> moved_cube.state[4] == 'R'
        # F1 should be R (from R1) -> moved_cube.state[5] == 'R'
        # R0 should be B (from B0) -> moved_cube.state[8] == 'B'
        # R1 should be B (from B1) -> moved_cube.state[9] == 'B'
        # B0 should be O (from L0) -> moved_cube.state[12] == 'O'
        # B1 should be O (from L1) -> moved_cube.state[13] == 'O'

        self.assertEqual(moved_cube.state[16], 'G')
        self.assertEqual(moved_cube.state[17], 'G')
        self.assertEqual(moved_cube.state[4], 'R')
        self.assertEqual(moved_cube.state[5], 'R')
        self.assertEqual(moved_cube.state[8], 'B')
        self.assertEqual(moved_cube.state[9], 'B')
        self.assertEqual(moved_cube.state[12], 'O')
        self.assertEqual(moved_cube.state[13], 'O')

    def test_F_move(self):
        cube = Cube()
        moved_cube = cube.apply_move('F')

        # F face rotates
        # F0 F1   -> F2 F0
        # F2 F3   -> F3 F1
        # Indices 4,5,6,7
        # Original: GGGG
        # Expected new F face: GGGG (same colors, just shifted)
        self.assertEqual(moved_cube.state[4], 'G')
        self.assertEqual(moved_cube.state[5], 'G')
        self.assertEqual(moved_cube.state[6], 'G')
        self.assertEqual(moved_cube.state[7], 'G')

        # Affected cross-face stickers (U, R, D, L)
        # U2, U3 (indices 2,3) moves to R0, R2 (indices 8,10)
        # R0, R2 (indices 8,10) moves to D0, D1 (indices 20,21)
        # D0, D1 (indices 20,21) moves to L3, L1 (indices 19,17)
        # L3, L1 (indices 19,17) moves to U2, U3 (indices 2,3)

        # After F move on solved:
        # Original: U2=W, U3=W, R0=R, R2=R, D0=Y, D1=Y, L1=O, L3=O
        # Expected:
        # R0 should be W (from U2) -> moved_cube.state[8] == 'W'
        # R2 should be W (from U3) -> moved_cube.state[10] == 'W'
        # D0 should be R (from R0) -> moved_cube.state[20] == 'R'
        # D1 should be R (from R2) -> moved_cube.state[21] == 'R'
        # L3 should be Y (from D0) -> moved_cube.state[19] == 'Y'
        # L1 should be Y (from D1) -> moved_cube.state[17] == 'Y'
        # U2 should be O (from L3) -> moved_cube.state[2] == 'O'
        # U3 should be O (from L1) -> moved_cube.state[3] == 'O'

        self.assertEqual(moved_cube.state[8], 'W')
        self.assertEqual(moved_cube.state[10], 'W')
        self.assertEqual(moved_cube.state[20], 'R')
        self.assertEqual(moved_cube.state[21], 'R')
        self.assertEqual(moved_cube.state[19], 'Y')
        self.assertEqual(moved_cube.state[17], 'Y')
        self.assertEqual(moved_cube.state[2], 'O')
        self.assertEqual(moved_cube.state[3], 'O')


if __name__ == '__main__':
    unittest.main()
