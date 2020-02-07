import unittest
from game import match

class TestMatchMethods(unittest.TestCase):

    def setUp(self):
        self.bizingo_match = match.Match(['P1', 'P2'])

    def test_index_coordinates(self):
        self.assertEqual(self.bizingo_match.get_index_coordinate('A1'),(0, 0))
        self.assertEqual(self.bizingo_match.get_index_coordinate('A2'),(0, 1))
        self.assertEqual(self.bizingo_match.get_index_coordinate('B2'),(1, 1))

    def test_adjacent_triangles(self):
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(0, 0),
            [(0,2), (1,0), (1,2)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(1, 2),
            [(0,0), (0,2), (1,0), (1,4), (2,2), (2,4)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(7, 9),
            [(6,7), (6,9), (7,7), (7,11), (8,9), (8,11)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(8, 0),
            [(7,0), (8,2), (9,1)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(8, 20),
            [(7,18), (8,18), (9,19)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(9, 1),
            [(8,0), (8,2), (9,3), (10,1)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(10, 0),
            [(9,0), (9,2), (10,2)]
        )
        self.assertEqual(
            self.bizingo_match.get_adjacent_triangles(10, 18),
            [(9,18), (9,20), (10,16)]
        )

    def test_not_move_piece(self):
        with self.assertRaises(Exception):
            self.bizingo_match.move_piece('P2', 'A1', 'A2')
            self.bizingo_match.move_piece('P1', 'A1', 'A2')
            self.bizingo_match.move_piece('P1', 'A1', 'A3')
            self.bizingo_match.move_piece('P1', 'H4', 'G2')

        self.bizingo_match.turn = 1
        with self.assertRaises(Exception):
            self.bizingo_match.move_piece('P2', 'F5', 'G5')
            self.bizingo_match.move_piece('P2', 'F5', 'F3')
        self.bizingo_match.turn = 0

    def test_move_piece(self):
        self.bizingo_match.move_piece('P1', 'F5', 'G5')
        self.assertEqual(self.bizingo_match.get_piece_in_coodinate('F5'), 0)
        self.assertEqual(self.bizingo_match.get_piece_in_coodinate('G5'), 10)

if __name__ == '__main__':
    unittest.main()
