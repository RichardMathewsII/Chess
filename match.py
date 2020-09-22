"""
Defines class for Chess match
"""
from board import Board


class Match:
    notation = {'white': 'uppercase', 'black': 'lowercase'}  # piece representation in command line

    def __init__(self):
        self.turn = 'white'  # white player moves first
        self.not_turn = 'black'
        self.chessboard = Board()
        self.white = None  # white player's name
        self.black = None  # black player's name
        self.checkmate = False
        self.incheck = False

    def select_piece(self, position):
        """
        Select a Chess piece on the chessboard
        :param position: string, position of Chess square requested by player in algebraic notation
        :return: boolean, True if selection occurred successfully, False otherwise
        """
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # chessboard columns
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']  # chessboard rows

        # ensure position is on the chessboard
        if len(position) != 2:
            print('Incorrect notation. Please try again.')
            return False
        elif position[0] not in files or position[1] not in ranks:
            print('Incorrect notation. Please try again.')
            return False

        piece = self.chessboard.get_piece(position)
        if piece == 0:
            # square is empty
            print('There is no chess piece at that position.')
            return False
        elif self.turn != piece.player:
            # wrong player's piece
            print('That piece is {}. It is {}\'s turn. {} pieces are {}.'.format(piece.player,
                                                                                 self.turn,
                                                                                 self.turn,
                                                                                 self.notation[self.turn])
                  )
            return False
        else:
            # successful selection
            print('You have selected a {} at {}'.format(piece.name, position))
            self.chessboard.select(position)
            return True

    def move(self, position):
        """
        Attempt to execute a move on the chessboard requested by the player
        :param position: string, requested position by player in algebraic notation
        :return: boolean, True if move executed successfully, False otherwise
        """
        if self.chessboard.execute_move(position):
            print('You successfully moved your {} to {}.'.format(self.chessboard.selected.name, position))
            return True
        else:
            return False

    def switch_turns(self):
        """ Switch player turn """
        self.turn, self.not_turn = self.not_turn, self.turn

    def check(self):
        """ Determine if board state is checkmate or king is in check. Informs players of check or checkmate. """
        check = self.chessboard.check(self.not_turn)
        if check == 'check':
            self.incheck = True
            print('{} has checked {}'.format(self.turn, self.not_turn))
        elif check == 'checkmate':
            print("Checkmate! {} wins the game!".format(self.black if self.turn == 'black' else self.white))
            self.checkmate = True

    def is_pawn_promotion(self):
        return self.chessboard.is_pawn_promotion()

    def promote_pawn(self, promotion):
        self.chessboard.promote_pawn(promotion)
