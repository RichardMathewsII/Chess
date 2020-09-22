"""
Unit tests for match.py
"""
import unittest
from match import Match
from pieces import Pawn
from test_board import generate_scenario


class TestMatch(unittest.TestCase):
    """ Unit tests for Match class """

    def test_select_piece(self):
        """ Unit test for Match.select_piece() method """
        test_match = Match()

        # test rejection of invalid position input by user
        self.assertFalse(test_match.select_piece('aa'))
        self.assertFalse(test_match.select_piece('11'))
        self.assertFalse(test_match.select_piece('1a'))
        self.assertFalse(test_match.select_piece('aaa'))
        self.assertFalse(test_match.select_piece('i1'))
        self.assertFalse(test_match.select_piece('a9'))

        # test rejection of selecting empty space
        self.assertFalse(test_match.select_piece('a4'))

        # test rejection of selecting black piece on white's turn
        self.assertFalse(test_match.select_piece('a8'))

        # test rejection of selecting white piece on black's turn
        test_match.turn = 'black'
        self.assertFalse(test_match.select_piece('a1'))

        # test success of valid position input and selection of black color piece by black
        self.assertTrue(test_match.select_piece('h8'))

        # test success of valid position input and selection of white color piece by white
        test_match.turn = 'white'
        self.assertTrue(test_match.select_piece('a1'))

    def test_move(self):
        """ Unit test for Match.move() method """
        test_match = Match()

        # test success of moving pawn two spaces forward on first turn
        test_match.select_piece('d2')  # select white pawn
        self.assertTrue(test_match.move('d4'))  # move two spaces forward
        pawn = test_match.chessboard.get_piece('d4')  # get occupant at new position
        self.assertIs(type(pawn), Pawn)  # ensure pawn is at the new position
        empty = test_match.chessboard.get_piece('d2')  # get occupant at pawn's old position
        self.assertEqual(empty, 0)  # ensure pawn's old position is empty

        # test rejection of moving pawn two spaces forward after first turn
        self.assertFalse(test_match.move('d6'))

        # test success of moving pawn one space forward after first turn
        self.assertTrue(test_match.move('d5'))

        # craft scenario where moving a white pawn forward one space will result in white's king in check
        pcs = {'black': {'initial': [(0, 0)], 'final': [(4, 0)]},
               'white': {'initial': [(7, 4), (6, 3)], 'final': [(4, 4), (4, 3)]}}
        test_match.chessboard = generate_scenario(pcs)

        # test rejection of moving white pawn forward leaving white king in check
        test_match.select_piece('d4')  # select white pawn
        self.assertFalse(test_match.move('d5'))

    def test_check(self):
        """ Unit test for Match.check() method """
        test_match = Match()

        # craft scenario where black made a move that placed white king in check, but not checkmate
        pcs = {'black': {'initial': [(0, 0)], 'final': [(4, 0)]},
               'white': {'initial': [(7, 4)], 'final': [(4, 4)]}}
        test_match.chessboard = generate_scenario(pcs)
        test_match.turn = 'black'
        test_match.not_turn = 'white'

        # test Match can detect king is in check without checkmate
        test_match.check()
        self.assertTrue(test_match.incheck)
        self.assertFalse(test_match.checkmate)

        # craft complex checkmate scenario where black wins (involves 5 black pieces)
        pcs = {'black': {'initial': [(0, 0), (0, 2), (1, 3), (0, 5), (1, 6), (0, 6)],
                         'final': [(4, 0), (2, 2), (2, 3), (2, 7), (4, 7), (1, 6)]},
               'white': {'initial': [(7, 4), (6, 3)], 'final': [(4, 4), (5, 3)]}}
        test_match.chessboard = generate_scenario(pcs)
        test_match.black = 'black'
        test_match.check()

        # test Match can detect complex checkmate scenario
        self.assertTrue(test_match.checkmate)


if __name__ == '__main__':
    unittest.main()
