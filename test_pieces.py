"""
Unit tests for pieces.py
"""
import unittest
import pieces
from test_board import generate_scenario
from board import Board


class TestChessPiece(unittest.TestCase):
    """ Unit tests for ChessPiece class """

    def test_is_move_in_bounds(self):
        """ Unit test for ChessPiece.is_move_in_bounds() method """
        piece = pieces.ChessPiece((0, 0), 'black')  # black rook
        # test for proper detection of in-bounds and out-of-bounds moves
        self.assertTrue(piece.is_move_in_bounds((7, 7)))
        self.assertTrue(piece.is_move_in_bounds((0, 0)))
        self.assertFalse(piece.is_move_in_bounds((8, 7)))
        self.assertFalse(piece.is_move_in_bounds((7, -1)))

    def test_is_conflict(self):
        """ Unit test for ChessPiece.is_conflict() method """
        test_board = Board()
        piece = pieces.ChessPiece((0, 0), 'black')  # black rook
        # test for proper detection of position conflicts
        self.assertIs(piece.is_conflict((3, 3), test_board.board), None)  # assert no conflict
        self.assertEqual(piece.is_conflict((0, 1), test_board.board), 'black')  # assert black piece conflict
        self.assertEqual(piece.is_conflict((6, 1), test_board.board), 'white')  # assert white piece conflict

    def test_get_path(self):
        """ Unit test for ChessPiece.get_path() method """
        pcs = {'white': {'initial': [(7, 0), (7, 2)], 'final': [(3, 3), (3, 4)]}}
        test_board = generate_scenario(pcs)

        # test for vertical/horizontal case
        piece = test_board.get_piece('d5')
        self.assertEqual(piece.get_path((3, 0)), [(3, 3), (3, 2), (3, 1), (3, 0)])
        self.assertEqual(piece.get_path((3, 6)), [(3, 3), (3, 4), (3, 5), (3, 6)])
        self.assertEqual(piece.get_path((0, 3)), [(3, 3), (2, 3), (1, 3), (0, 3)])
        self.assertEqual(piece.get_path((6, 3)), [(3, 3), (4, 3), (5, 3), (6, 3)])

        # test for diagonal case
        piece = test_board.get_piece('e5')
        self.assertEqual(piece.get_path((1, 2)), [(3, 4), (2, 3), (1, 2)])
        self.assertEqual(piece.get_path((1, 6)), [(3, 4), (2, 5), (1, 6)])
        self.assertEqual(piece.get_path((5, 2)), [(3, 4), (4, 3), (5, 2)])
        self.assertEqual(piece.get_path((5, 6)), [(3, 4), (4, 5), (5, 6)])


class TestPawn(unittest.TestCase):
    """ Unit tests for Pawn class """

    def test_is_move_valid(self):
        """ Unit test for Pawn.is_move_valid() method """
        pcs = {'black': {'initial': [(1, 2)], 'final': [(5, 2)]}, 'white': {'initial': [(6, 5)], 'final': [(4, 5)]}}
        test_board = generate_scenario(pcs)

        # test for success of two spaces forward on first move
        pawn = test_board.get_piece('a2')
        self.assertTrue(pawn.is_move_valid((4, 0), test_board.board))

        # test for rejection of two spaces forward after first move
        pawn.moved = True
        self.assertFalse(pawn.is_move_valid((4, 0), test_board.board))

        # test for success of one space forward
        self.assertTrue(pawn.is_move_valid((5, 0), test_board.board))

        # test for rejection of move one space forward when opponent is blocking
        pawn = test_board.get_piece('c2')
        self.assertFalse(pawn.is_move_valid((5, 2), test_board.board))

        # test for rejection of move two spaces forward when opponent is blocking first space but not second
        self.assertFalse(pawn.is_move_valid((4, 2), test_board.board))

        # test for success of diagonal move to eliminate opponent
        pawn = test_board.get_piece('d2')
        self.assertTrue(pawn.is_move_valid((5, 2), test_board.board))

        # test for rejection of diagonal move into an empty square
        self.assertFalse(pawn.is_move_valid((5, 4), test_board.board))

        # test for rejection of move backward
        pawn = test_board.get_piece('f4')
        self.assertFalse(pawn.is_move_valid((5, 5), test_board.board))

        # craft en passant scenario
        pcs = {'black': {'initial': [(1, 2)], 'final': [(3, 2)]}, 'white': {'initial': [(6, 1)], 'final': [(3, 1)]}}
        test_board = generate_scenario(pcs)
        wpawn = test_board.get_piece('b5')  # white pawn in en passant position
        bpawn = test_board.get_piece('c5')  # black pawn
        bpawn.first_move = 2
        bpawn.two_step = True
        # test success of en passant move
        turn = 3  # immediate turn after black pawn moved forward two spaces
        self.assertTrue(wpawn.is_move_valid((2, 2), test_board.board, turn))  # assert en passant move is valid
        self.assertTrue(wpawn.enpassant)  # assert enpassant attribute was turned on
        self.assertFalse(wpawn.is_move_valid((0, 2), test_board.board, turn))  # assert move only goes one direction
        # test rejection of en passant move after it is forfeited
        turn = 5
        self.assertFalse(wpawn.is_move_valid((2, 2), test_board.board, turn))  # assert en passant move is invalid

    def test_en_passant(self):
        """ Unit test for Pawn.en_passant() method """
        # craft en passant scenario
        pcs = {'black': {'initial': [(1, 2)], 'final': [(3, 2)]}, 'white': {'initial': [(6, 1)], 'final': [(3, 1)]}}
        test_board = generate_scenario(pcs)
        wpawn = test_board.get_piece('b5')  # white pawn in en passant position
        bpawn = test_board.get_piece('c5')  # black pawn
        bpawn.first_move = 2
        bpawn.two_step = True
        # test proper detection of en passant move
        turn = 3
        result, side = wpawn.en_passant(test_board.board, turn)
        self.assertTrue(result)  # assert en passant move is valid
        self.assertEqual(side, 'E')  # assert correct direction of en passant move
        # test no detection of valid en passant move
        turn = 5
        result, side = wpawn.en_passant(test_board.board, turn)
        self.assertFalse(result)  # assert move is invalid since en passant move was forfeited
        turn = 3
        bpawn.two_step = False
        result, side = wpawn.en_passant(test_board.board, turn)
        self.assertFalse(result)  # assert move is invalid since black pawn did not use two step


class TestRook(unittest.TestCase):
    """ Unit tests for Rook class """

    def test_is_move_valid(self):
        """ Unit test for Rook.is_move_valid() method """
        pcs = {'white': {'initial': [(7, 7)], 'final': [(5, 7)]}}
        test_board = generate_scenario(pcs)

        # test for rejection of move that is blocked by friendly piece
        rook = test_board.get_piece('a1')
        self.assertFalse(rook.is_move_valid((5, 0), test_board.board))

        # test for success of horizontal move across board
        rook = test_board.get_piece('h3')
        self.assertTrue(rook.is_move_valid((5, 0), test_board.board))

        # test for success of move to eliminate opponent piece
        self.assertTrue(rook.is_move_valid((1, 7), test_board.board))

        # test for rejection of move that is blocked by opponent piece
        self.assertFalse(rook.is_move_valid((0, 7), test_board.board))


class TestKnight(unittest.TestCase):
    """ Unit tests for Knight class """

    def test_is_move_valid(self):
        """ Unit test for Knight.is_move_valid() method """
        pcs = {'white': {'initial': [(7, 6)], 'final': [(2, 6)]}}
        test_board = generate_scenario(pcs)

        # test rejection of move blocked by friendly piece
        knight = test_board.get_piece('b1')
        self.assertFalse(knight.is_move_valid((6, 3), test_board.board))

        # test success of L-shaped move into empty square
        self.assertTrue(knight.is_move_valid((5, 2), test_board.board))

        # test success of L-shaped move to eliminate opponent piece
        knight = test_board.get_piece('g6')
        self.assertTrue(knight.is_move_valid((0, 5), test_board.board))

        # test success of different L-shaped move to eliminate opponent piece
        self.assertTrue(knight.is_move_valid((1, 4), test_board.board))


class TestBishop(unittest.TestCase):
    """ Unit tests for Bishop class """

    def test_is_move_valid(self):
        """ Unit test for Bishop.is_move_valid() method """
        pcs = {'white': {'initial': [(7, 5)], 'final': [(4, 4)]}}
        test_board = generate_scenario(pcs)

        # test rejection of diagonal move into square occupied by friendly piece
        bishop = test_board.get_piece('e4')
        self.assertFalse(bishop.is_move_valid((6, 2), test_board.board))

        # test rejection of diagonal move that is blocked by opponent piece
        self.assertFalse(bishop.is_move_valid((0, 0), test_board.board))

        # test success of diagonal move to eliminate opponent piece
        self.assertTrue(bishop.is_move_valid((1, 7), test_board.board))

        # test success of diagonal move into empty square
        self.assertTrue(bishop.is_move_valid((2, 6), test_board.board))

        # test rejection of non-diagonal move into empty square
        self.assertFalse(bishop.is_move_valid((2, 4), test_board.board))


class TestQueen(unittest.TestCase):
    """ Unit tests for Queen class """

    def test_is_move_valid(self):
        """ Unit test for Queen.is_move_valid() method """
        pcs = {'white': {'initial': [(7, 3)], 'final': [(4, 3)]}}
        test_board = generate_scenario(pcs)

        # test rejection of vertical move blocked by friendly piece
        queen = test_board.get_piece('d4')
        self.assertFalse(queen.is_move_valid((7, 3), test_board.board))

        # test rejection of diagonal move blocked by friendly piece
        self.assertFalse(queen.is_move_valid((7, 0), test_board.board))

        # test rejection of vertical move blocked by opponent piece
        self.assertFalse(queen.is_move_valid((0, 3), test_board.board))

        # test rejection of diagonal move blocked by opponent piece
        self.assertFalse(queen.is_move_valid((0, 7), test_board.board))

        # test success of vertical move to eliminate opponent piece
        self.assertTrue(queen.is_move_valid((1, 3), test_board.board))

        # test success of diagonal move to eliminate opponent piece
        self.assertTrue(queen.is_move_valid((1, 6), test_board.board))

        # test success of horizontal move to empty square
        self.assertTrue(queen.is_move_valid((4, 7), test_board.board))

        # test rejection of L-shaped move to empty square
        self.assertFalse(queen.is_move_valid((2, 4), test_board.board))


class TestKing(unittest.TestCase):
    """ Unit tests for King class """

    def test_is_move_valid(self):
        """ Unit test for King.is_move_valid() method """
        pcs = {'black': {'initial': [(1, 3)], 'final': [(4, 3)]}, 'white': {'initial': [(7, 4)], 'final': [(5, 4)]}}
        test_board = generate_scenario(pcs)

        # test rejection of one-square vertical move blocked by friendly piece
        king = test_board.get_piece('e3')
        self.assertFalse(king.is_move_valid((6, 4), test_board.board))

        # test success of one-square diagonal move to eliminate opponent piece
        self.assertTrue(king.is_move_valid((4, 3), test_board.board))

        # test success of one-square horizontal move to empty square
        self.assertTrue(king.is_move_valid((5, 5), test_board.board))

        # test rejection of multi-square vertical move to empty square
        self.assertFalse(king.is_move_valid((3, 4), test_board.board))

    def test_is_checked(self):
        """ Unit test for King.is_checked() method """
        # test king is not in check at beginning of game
        test_board = Board()
        king = test_board.get_piece('e1')
        self.assertFalse(king.is_checked(king.position, test_board.board, test_board.active_pieces))

        # test king is checked in checked scenario
        pcs = {'black': {'initial': [(0, 3)], 'final': [(3, 0)]}, 'white': {'initial': [(7, 4)], 'final': [(4, 0)]}}
        test_board = generate_scenario(pcs)
        king = test_board.get_piece('a4')
        self.assertTrue(king.is_checked(king.position, test_board.board, test_board.active_pieces))


if __name__ == '__main__':
    unittest.main()
