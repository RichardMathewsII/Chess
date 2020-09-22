"""
Unit tests for board.py
"""
import unittest
import board
from pieces import Knight, Queen, Pawn, Bishop


def generate_scenario(pieces):
    """
    Generates any customizable chessboard scenario. Move any set of chess pieces anywhere on the board.
    :param pieces: Dict['player']->Dict['initialized position', 'final position']->List[positions]->Tuple(row, col)
    :return: Board, a Board instance with customizations
    """
    test_board = board.Board()
    for player in pieces.keys():
        old_positions = pieces[player]['initial']  # positions of chess pieces at initialized board state
        new_positions = pieces[player]['final']  # new positions for each chess piece
        for i in range(len(old_positions)):
            curr = old_positions[i]
            new = new_positions[i]
            piece = test_board.board[curr[0]][curr[1]]  # get piece
            test_board.board[curr[0]][curr[1]] = 0  # set initial position to zero
            test_board.board[new[0]][new[1]] = piece  # set new position equal to piece
            piece.update_position(new)  # update piece position
    return test_board


class TestBoard(unittest.TestCase):
    """ Unit tests for Board class """

    def test_algebraic_to_index(self):
        """ Unit test for Board.algebraic_to_index() method """
        test_board = board.Board()

        # test proper conversion of algebraic notation to board matrix indices
        self.assertEqual(test_board.algebraic_to_index('a8'), (0, 0))
        self.assertEqual(test_board.algebraic_to_index('h1'), (7, 7))
        self.assertEqual(test_board.algebraic_to_index('g5'), (3, 6))

    def test_check(self):
        """ Unit test for Board.check() method """
        # craft scenario where black's king is in check, but not checkmate
        pieces = {'black': {'initial': [(0, 4)], 'final': [(3, 4)]}, 'white': {'initial': [(6, 5)], 'final': [(4, 5)]}}
        test_board = generate_scenario(pieces)
        turn = 'black'
        # test proper detection of a simple check/non-checkmate scenario
        self.assertEqual(test_board.check(turn), 'check')

    def test_checkmate(self):
        """ Unit test for Board.checkmate() method via the Board.check() method """
        # craft simple checkmate scenario (black loses)
        pieces = {'white': {'initial': [(7, 3), (7, 5)], 'final': [(1, 5), (4, 2)]}}
        test_board = generate_scenario(pieces)
        # test proper detection of a simple checkmate scenario
        self.assertEqual(test_board.check('black'), 'checkmate')

        # craft simple check/non-checkmate scenario where the only way to save king is if other piece eliminates threat
        pieces = {
            'white': {'initial': [(7, 3), (7, 2)], 'final': [(3, 4), (4, 1)]},
            'black': {'initial': [(1, 4), (0, 4), (1, 6)], 'final': [(2, 3), (1, 4), (2, 5)]},
        }
        test_board = generate_scenario(pieces)
        turn = 'black'
        # test proper detection of a simple check/non-checkmate scenario that requires non-king move
        self.assertNotEqual(test_board.check(turn), 'checkmate')

        # craft complex checkmate scenario
        pieces = {
            'white': {'initial': [(7, 7), (7, 3), (7, 2)], 'final': [(3, 4), (4, 7), (4, 1)]},
            'black': {'initial': [(1, 4), (0, 4), (1, 6)], 'final': [(2, 3), (1, 4), (2, 5)]},
        }
        test_board = generate_scenario(pieces)
        turn = 'black'
        # test proper detection of complex checkmate scenario
        self.assertEqual(test_board.check(turn), 'checkmate')

        # craft complex check/non-checkmate scenario where the only way to save king is if other piece eliminates threat
        pieces = {'black': {'initial': [(0, 0), (0, 2), (1, 3), (0, 5), (1, 6), (0, 6)],
                            'final': [(4, 0), (2, 4), (2, 3), (2, 7), (4, 6), (1, 6)]},
                  'white': {'initial': [(7, 4), (6, 3), (6, 0)], 'final': [(4, 4), (5, 3), (3, 0)]}}
        test_board = generate_scenario(pieces)
        # test proper detection of a complex check/non-checkmate scenario that requires non-king move
        self.assertNotEqual(test_board.check('white'), 'checkmate')

    def test_execute_move(self):
        """ Unit test for Board.execute_move() method """
        # test basic move execution
        test_board = board.Board()
        test_board.select('b1')  # knight
        test_board.execute_move('a3')
        self.assertIs(type(test_board.board[5][0]), Knight)
        self.assertEqual(test_board.board[7][1], 0)

        # test elimination of opponent piece
        pieces = {'white': {'initial': [(7, 3)], 'final': [(2, 0)]}}
        test_board = generate_scenario(pieces)
        test_board.select('a6')  # queen
        elim = test_board.get_piece('a7')  # pawn
        test_board.execute_move('a7')  # queen takes pawn
        self.assertTrue(elim not in test_board.active_pieces[elim.player])  # assert pawn is no longer in play
        self.assertIs(type(test_board.get_piece('a7')), Queen)  # assert queen now occupies a7

        # test rejection of move that leaves King in check
        pieces = {'white': {'initial': [(6, 4), (7, 4)], 'final': [(4, 4), (4, 5)]},
                  'black': {'initial': [(0, 3)], 'final': [(4, 2)]}}
        test_board = generate_scenario(pieces)
        test_board.select('e4')
        self.assertFalse(test_board.execute_move('e5'))

        # test rejection of King move into a checked position
        pieces = {'white': {'initial': [(7, 4)], 'final': [(5, 5)]},
                  'black': {'initial': [(0, 3)], 'final': [(4, 2)]}}
        test_board = generate_scenario(pieces)
        test_board.select('f3')
        self.assertFalse(test_board.execute_move('f4'))

        # test success of en passant move
        pcs = {'white': {'initial': [(6, 1)], 'final': [(3, 1)]}}
        test_board = generate_scenario(pcs)
        bpawn = test_board.get_piece('c7')
        test_board.select('c7')  # select black pawn
        test_board.execute_move('c5')  # move black pawn forward two spaces on turn 1
        wpawn = test_board.get_piece('b5')
        test_board.select('b5')  # select white pawn in en passant position (turn 2)
        self.assertTrue(test_board.execute_move('c6'))  # execute en passant move
        self.assertEqual(test_board.get_piece('c5'), 0)  # ensure black pawn's previous position on board is now empty
        self.assertIs(type(test_board.get_piece('c6')), Pawn)  # ensure white pawn completed move
        self.assertNotIn(bpawn, test_board.active_pieces['black'])  # ensure black pawn is eliminated from game
        self.assertFalse(wpawn.enpassant)  # enpassant parameter should be set back to False

        # test rejection of en passant move after it is forfeited
        pcs = {'white': {'initial': [(6, 1)], 'final': [(3, 1)]}}
        test_board = generate_scenario(pcs)
        test_board.select('c7')  # select black pawn
        test_board.execute_move('c5')  # move black pawn forward two spaces on turn 1
        test_board.turn = 4  # white forfeits en passant
        test_board.select('b5')  # select white pawn in en passant position (turn 4)
        self.assertFalse(test_board.execute_move('c6'))  # attempt en passant move

    def test_is_pawn_promotion(self):
        """ Unit test for Board.is_pawn_promotion() method """
        # craft pawn promotion scenario for both players
        pcs = {'black': {'initial': [(1, 0)], 'final': [(7, 0)]}, 'white': {'initial': [(6, 0)], 'final': [(0, 0)]}}
        test_board = generate_scenario(pcs)
        # test valid pawn promotion
        test_board.select('a8')
        self.assertTrue(test_board.is_pawn_promotion())
        test_board.select('a1')
        self.assertTrue(test_board.is_pawn_promotion())
        # test invalid pawn promotion
        test_board.select('h7')
        self.assertFalse(test_board.is_pawn_promotion())
        test_board.select('h2')
        self.assertFalse(test_board.is_pawn_promotion())

    def test_promote_pawn(self):
        """ Unit test for Board.promote_pawn() method """
        # craft pawn promotion scenario for both players
        pcs = {'black': {'initial': [(1, 0)], 'final': [(7, 0)]}, 'white': {'initial': [(6, 0)], 'final': [(0, 0)]}}
        test_board = generate_scenario(pcs)

        # test white pawn promotion
        test_board.select('a8')  # select pawn
        pawn = test_board.get_piece('a8')  # get pawn
        test_board.promote_pawn('queen')  # promote pawn
        queen = test_board.get_piece('a8')  # get piece at a8
        self.assertIs(type(queen), Queen)  # assert piece is Queen type
        self.assertEqual(queen.position, (0, 0))  # assert new piece's position is correct
        self.assertEqual(queen.player, 'white')  # assert new piece's is right player
        self.assertNotIn(pawn, test_board.active_pieces['white'])  # assert pawn is no longer in play
        self.assertIn(queen, test_board.active_pieces['white'])  # assert new piece is in play

        # test black pawn promotion
        test_board.select('a1')  # select pawn
        pawn = test_board.get_piece('a1')  # get pawn
        test_board.promote_pawn('bishop')  # promote pawn
        bishop = test_board.get_piece('a1')  # get piece at a8
        self.assertIs(type(bishop), Bishop)  # assert piece is Bishop type
        self.assertEqual(bishop.position, (7, 0))  # assert new piece's position is correct
        self.assertEqual(bishop.player, 'black')  # assert new piece's is right player
        self.assertNotIn(pawn, test_board.active_pieces['black'])  # assert pawn is no longer in play
        self.assertIn(bishop, test_board.active_pieces['black'])  # assert new piece is in play


if __name__ == '__main__':
    unittest.main()
