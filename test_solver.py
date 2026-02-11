import unittest
from app import Cube, solve_cube, SOLVED_STATE_STR

class TestSolver(unittest.TestCase):

    def test_solved_cube(self):
        cube = Cube(SOLVED_STATE_STR)
        solution = solve_cube(cube)
        self.assertEqual(solution, [])

    def test_single_move_R(self):
        # Solved cube, then R' to get to a state that can be solved by R
        scrambled_cube = Cube(SOLVED_STATE_STR).apply_move("R'")
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        # The shortest solution might not be just 'R', but should be short
        self.assertLessEqual(len(solution), 3) # R' is RRR or R'

    def test_single_move_U(self):
        scrambled_cube = Cube(SOLVED_STATE_STR).apply_move("U'")
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        self.assertLessEqual(len(solution), 3)

    def test_single_move_F(self):
        scrambled_cube = Cube(SOLVED_STATE_STR).apply_move("F'")
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        self.assertLessEqual(len(solution), 3)

    def test_two_moves_RU(self):
        scrambled_cube = Cube(SOLVED_STATE_STR).apply_move("R'").apply_move("U'")
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        self.assertLessEqual(len(solution), 6) # R'U' can be solved in 2 moves, but BFS might find slightly longer equivalent paths

    # Add more complex scramble tests here
    def test_complex_scramble_1(self):
        # Example scramble: R U R' U R U2 R'
        scramble_moves = ["R", "U", "R'", "U", "R", "U2", "R'"]
        scrambled_cube = Cube(SOLVED_STATE_STR)
        for move in scramble_moves:
            scrambled_cube = scrambled_cube.apply_move(move)
        
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        # A 2x2 can always be solved in 14 moves or less (quarter turns)
        # Our moves are R, R', R2, U, U', U2, F, F', F2
        # Max moves for these types should be around 7-8
        self.assertLessEqual(len(solution), 8) 
        
        # Verify the solution by applying it to the scrambled cube
        solved_check_cube = scrambled_cube
        for move in solution:
            solved_check_cube = solved_check_cube.apply_move(move)
        self.assertTrue(solved_check_cube.is_solved())

    def test_complex_scramble_2(self):
        # Another scramble: F R U R' U' F'
        scramble_moves = ["F", "R", "U", "R'", "U'", "F'"]
        scrambled_cube = Cube(SOLVED_STATE_STR)
        for move in scramble_moves:
            scrambled_cube = scrambled_cube.apply_move(move)
        
        solution = solve_cube(scrambled_cube)
        self.assertIsNotNone(solution)
        self.assertLessEqual(len(solution), 8) 
        
        solved_check_cube = scrambled_cube
        for move in solution:
            solved_check_cube = solved_check_cube.apply_move(move)
        self.assertTrue(solved_check_cube.is_solved())


if __name__ == '__main__':
    unittest.main()
