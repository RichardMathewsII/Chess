"""
Defines class for chessboard
"""
from pieces import *
import copy


class Board:
    # dicts that map algebraic notation to matrix indices (rank -> row, file -> column)
    alg_row_to_idx = {8: 0, 7: 1, 6: 2, 5: 3, 4: 4, 3: 5, 2: 6, 1: 7}
    alg_col_to_idx = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def __init__(self):
        self.active_pieces = {'white': [], 'black': []}  # holds pieces in play for both players
        # self.board is a 2D matrix and holds current state of chessboard, empty spaces are zeros
        # white starts on bottom rows (row index 6 and 7) and black starts on top rows (row index 0 and 1)
        self.board = self.initialize_board()
        self.selected = None  # points to the chess piece the player has selected to move
        self.kings = {'white': self.board[7][4], 'black': self.board[0][4]}  # holds both king instances
        self.turn = 1  # specifies turn of match

    def initialize_board(self):
        """ Initialize the chessboard """
        board = [[0 for i in range(8)] for j in range(8)]  # empty spaces represented as zeros

        # assign and place Pawns on board
        for i in range(8):
            board[6][i] = Pawn((6, i), 'white')
            board[1][i] = Pawn((1, i), 'black')
            self.active_pieces['white'].append(board[6][i])
            self.active_pieces['black'].append(board[1][i])

        # assign and place non-Pawn pieces on board
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i in range(8):
            board[7][i] = pieces[i]((7, i), 'white')
            board[0][i] = pieces[i]((0, i), 'black')
            self.active_pieces['white'].append(board[7][i])
            self.active_pieces['black'].append(board[0][i])

        return board

    def print(self):
        """ Prints the current state of the chessboard, sides are annotated according to algebraic notation """
        print('    a b c d e f g h ')
        print('   ----------------- ')
        for row in range(8, 0, -1):
            print(row, end=' | ')
            for col in range(8):
                val = self.board[self.alg_row_to_idx[row]][col]
                print(val, end=' ') if val != 0 else print('*', end=' ')
            print('|', end=' ')
            print(row)
        print('   ----------------- ')
        print('    a b c d e f g h ')

    def algebraic_to_index(self, alg_position):
        """
        Converts board position from algebraic notation to list indices
        :param alg_position: string, algebraic notation of chessboard position (ex. 'a1')
        :return: Tuple(row, col), index position in 2D list
        """
        return tuple([self.alg_row_to_idx[int(alg_position[1])], self.alg_col_to_idx[alg_position[0]]])

    def execute_move(self, final_alg_position):
        """
        Attempts to execute move for selected chess piece
        :param final_alg_position: string, position to move selected piece to in algebraic notation (ex. 'a1')
        :return: boolean, True if move executed successfully, False otherwise
        """
        final_position = self.algebraic_to_index(final_alg_position)  # convert final position to matrix indices
        king = self.kings[self.selected.player]  # get king
        if self.selected.is_move_valid(final_position, self.board, turn=self.turn):
            # move is valid not accounting for possible check
            curr_position = self.selected.position

            # simulate board state if move were made
            board, active_pieces = self.simulate_move(self.selected, final_position)

            # determine if move results in king being left in check using simulated board state
            king_position = final_position if self.selected.name == 'king' else king.position
            if king.is_checked(king_position, board, active_pieces):
                # if move were made, the king would be in check, therefore the move is invalid
                print('INVALID: You can not leave your own king in check.')
                if self.selected.name == 'pawn':
                    self.selected.enpassant = False
                return False

            # determine if an opponent's piece occupies final position
            occupant = self.board[final_position[0]][final_position[1]]
            if occupant != 0:
                # square is not empty, therefore there is an opponent's piece in final position
                occupant.eliminated()
                self.active_pieces[occupant.player].remove(occupant)  # remove opponent piece from play
            # update current board state
            self.board[final_position[0]][final_position[1]] = self.selected  # point final position to piece
            self.board[curr_position[0]][curr_position[1]] = 0  # set initial position to empty
            self.selected.update_position(final_position)  # update board position of piece

            # special pawn case
            if self.selected.name == 'pawn':
                if self.selected.enpassant:
                    # pawn is making an en passant move
                    pawn_elim = self.board[curr_position[0]][final_position[1]]  # pawn to be eliminated
                    pawn_elim.eliminated()
                    self.board[curr_position[0]][final_position[1]] = 0
                    self.active_pieces[pawn_elim.player].remove(pawn_elim)  # remove opponent pawn from play
                    self.selected.enpassant = False  # turn enpassant off
                    print('{} pawn captures {} pawn en passant!'.format(self.selected.player, pawn_elim.player))
                # update pawn's attributes
                self.selected.move(curr_position, final_position, self.turn)

            self.turn += 1  # move executed successfully, next turn
            return True
        else:
            print('INVALID. That move is invalid. Please try again.')
            return False

    def select(self, alg_position):
        """
        Select chess piece to move
        :param alg_position: string, position of chess piece to move in algebraic notation (ex. 'a1')
        """
        position = self.algebraic_to_index(alg_position)
        self.selected = self.board[position[0]][position[1]]

    def get_piece(self, alg_position):
        """
        Get chess piece at board position
        :param alg_position: string, position of chess piece
        :return: chess piece object located at alg_position
        """
        position = self.algebraic_to_index(alg_position)
        return self.board[position[0]][position[1]]

    def check(self, player):
        """
        Determines if current board state is check or checkmate
        :param player: string, specify which king
        :return: string or boolean, string if board state is check or checkmate, False otherwise
        """
        king = self.kings[player]  # get king
        # see if king is in check, if so, get opponent's piece that has placed king in check
        threat = king.is_checked(king.position, self.board, self.active_pieces, bool_only=False)
        if threat:
            # if king is in check, see if there is checkmate
            if self.checkmate(king, threat, self.active_pieces[player]):
                # checkmate, match is over
                return 'checkmate'
            # board state is check, but not checkmate
            return 'check'
        return False

    def checkmate(self, king, threat, pieces):
        """
        Determines if current board state is checkmate
        :param king: King, look at if this king is in checkmate
        :param threat: chess piece that has placed king in check
        :param pieces: list, friendly pieces in play
        :return: boolean, True if king is in checkmate, False otherwise
        """
        moves = king.generate_possible_moves(self.board, king.directions, turn=self.turn)  # get king's possible moves

        # first see if king can move into a safe square
        for move in moves:
            board, active_pieces = self.simulate_move(king, move)  # simulate board state as if move were made
            if not king.is_checked(move, board, active_pieces):
                # a king move exists that would not result in check, not checkmate
                return False

        # next see if friendly piece can block or eliminate threat
        attack_path = threat.get_path(king.position)[:-1]  # get attack path to king of threatening opponent piece
        for piece in pieces:
            # iterate over all player's pieces except king
            if piece.name == 'king':
                continue
            # get possible moves of friendly piece
            elif piece.name == 'pawn':
                # special pawn case
                possible_moves, _ = piece.generate_possible_moves(self.board, piece.directions, turn=self.turn)
            else:
                possible_moves = piece.generate_possible_moves(self.board, piece.directions, turn=self.turn)
            # look for overlap of friendly piece's possible moves and positions in attack path
            for opp_move in attack_path:
                next_piece = False
                for move in possible_moves:
                    if opp_move == move:
                        # friendly piece can block or eliminate threatening opponent piece
                        # simulate board state as if move were made
                        board, active_pieces = self.simulate_move(piece, move)
                        if king.is_checked(king.position, board, active_pieces):
                            # moving this piece will still result in king in check
                            next_piece = True  # go to next chess piece
                            break
                        # moving this piece will result in king not in check, no checkmate
                        return False
                if next_piece:
                    break

        # there is no move the player can make that will not result in an unchecked king, therefore it is checkmate
        return True

    def simulate_move(self, piece, end_position):
        """
        Simulates resulting board state if a chess piece were moved
        :param piece: chess piece to move
        :param end_position: Tuple(row, col), board position to move piece to
        :return: (Board, Dict[str:list]), simulated board matrix with active pieces
        """
        board = copy.deepcopy(self.board)
        occupant = board[end_position[0]][end_position[1]]  # see if opponent piece occupies end position
        if occupant not in [piece.player, 0]:
            # eliminate opponent piece form play
            active_pieces = self.active_pieces_copy(exclude=occupant)
        else:
            active_pieces = copy.deepcopy(self.active_pieces)
        # update board matrix
        board[end_position[0]][end_position[1]] = piece
        board[piece.position[0]][piece.position[1]] = 0
        return board, active_pieces

    def is_pawn_promotion(self):
        """ Determine if player is eligible for pawn promotion """
        piece = self.selected
        if piece.name == 'pawn':
            if piece.player == 'white' and piece.position[0] == 0:
                # white pawn can be promoted
                return True
            elif piece.player == 'black' and piece.position[0] == 7:
                # black pawn can be promoted
                return True
            return False
        return False

    def promote_pawn(self, promotion):
        """ Promote pawn """
        player = self.selected.player
        pawn = self.selected
        promotions = [Queen, Rook, Bishop, Knight]
        for piece in promotions:
            if promotion == piece.name:
                new_piece = piece(pawn.position, player)  # set new piece position to pawn position
        pawn.eliminated()
        self.active_pieces[player].append(new_piece)  # new piece is in play
        self.active_pieces[player].remove(pawn)  # pawn is out of play
        self.board[pawn.position[0]][pawn.position[1]] = new_piece  # update board with new piece
        print('{} has promoted a pawn to {}'.format(player, promotion))  # inform player of promotion

    def active_pieces_copy(self, exclude):
        """
        Return active pieces that excludes a piece. Used to exclude an opponent in simulate_move().
        :param exclude: chess piece to exclude
        :return: Dict[str:list], active pieces
        """
        active_pieces = {'white': [], 'black': []}
        for piece in self.active_pieces['white']:
            if piece.position == exclude.position:
                continue
            active_pieces['white'].append(piece)
        for piece in self.active_pieces['black']:
            if piece.position == exclude.position:
                continue
            active_pieces['black'].append(piece)
        return active_pieces
