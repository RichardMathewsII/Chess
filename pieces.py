"""
Defines classes for each chess piece
"""


class ChessPiece:
    # cardinal directions for board matrix (top left is 0, 0), N for North, NE for Northeast, etc.
    cardinal = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1),
                'NE': (-1, 1), 'NW': (-1, -1), 'SE': (1, 1), 'SW': (1, -1)}
    directions = []  # no cardinal directions for base class

    def __init__(self, position, player):
        self.position = position  # Tuple(row, col) location on board
        self.player = player  # string, 'white' or 'black'
        self.status = 'in play'  # string, 'in play' if piece is in play, 'eliminated' if piece is out of play
        self.max_moves = None  # no max number of moves for base class

    def is_move_valid(self, final_position, board, turn=0):
        """
        Checks if a move is valid
        :param final_position: Tuple(row, col), final board position requested by player
        :param board: 2D List, holds current positions on all game pieces
        :return: Boolean, True if move is valid, False if move is invalid
        """
        possible_moves = self.generate_possible_moves(board, self.directions)
        # check if final position exists in the space of possible moves
        return final_position in possible_moves

    def is_move_in_bounds(self, move):
        """
        Checks if a move is in bounds of Chess board
        :param move: Tuple(row, col), new position
        :return: Boolean, True if move is in bounds, False if move is out of bounds
        """
        if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
            # chess board is 8x8, represented as 0-7 indices
            return True
        else:
            return False

    def generate_possible_moves(self, board, directions, turn=0):
        """
        Generates space of possible moves the Chess piece can make
        :param board: 2D List, holds current positions on all game pieces
        :param directions: 1D List of strings, specifies cardinal directions the piece can move
        :return: 1D List of Tuple(row, col), space of possible board positions the piece can take
        """
        possible_moves = []
        for direction in directions:
            ystep = self.cardinal[direction][0]  # vertical step
            xstep = self.cardinal[direction][1]  # horizontal step
            move = (self.position[0] + ystep, self.position[1] + xstep)  # initialize first move
            count = 1
            while self.is_move_in_bounds(move) and count <= self.max_moves:
                # move is in bounds and does not exceed max number of moves
                conflict = self.is_conflict(move, board)
                if conflict == self.player:
                    # player's chess piece is blocking their path
                    break
                elif conflict is not None:
                    # opponent's chess piece is in path
                    possible_moves.append(move)
                    break
                possible_moves.append(move)
                count += 1
                move = (move[0] + ystep, move[1] + xstep)
        return possible_moves

    def is_conflict(self, position, board):
        """
        Checks for a conflict in the position
        :param position: Tuple(row, col), position on Chess board
        :param board: 2D List, holds current positions on all game pieces
        :return: player (string) if there is conflict, None if there is no conflict
        """
        occupant = board[position[0]][position[1]]
        if occupant == 0:
            # no Chess piece in board position
            return None
        else:
            return occupant.player

    def update_position(self, new_position):
        """
        Updates the position of the piece after the player has successfully moved it
        :param new_position: Tuple(row, col), new board position
        """
        self.position = new_position

    def eliminated(self):
        """
        An opponent's Chess piece has eliminated the piece from play
        """
        self.status = 'eliminated'

    def get_path(self, end_position):
        """
        Get linear path from piece's current position to an end position.
        NOTE: This method does not account for obstructions in the path.
        :param end_position: Tuple(row, col), end position on board
        :return: List of Tuple(row, col), square positions from current to end position inclusive, in order
        """
        # compute vertical step
        y = end_position[0] - self.position[0]
        ystep = y // abs(y) if y != 0 else 0
        # compute horizontal step
        x = end_position[1] - self.position[1]
        xstep = x // abs(x) if x != 0 else 0
        path = [(self.position[0], self.position[1])]  # initialize path with current position
        move = (self.position[0] + ystep, self.position[1] + xstep)  # initialize first move toward end position
        while move != end_position:
            path.append(move)
            move = (move[0] + ystep, move[1] + xstep)
        path.append((end_position[0], end_position[1]))
        return path


class Pawn(ChessPiece):
    name = 'pawn'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.moved = False  # special Pawn case for moving forward two spaces on first move
        self.directions = ['N', 'NE', 'NW'] if self.player == 'white' else ['S', 'SE', 'SW']
        self.max_moves = 1
        self.enpassant = False  # True if piece is poised to make an en passant move
        self.first_move = 0  # when the pawn first moves, this attribute is set to the turn it was first moved
        self.two_step = False  # True if piece takes two steps on its first move

    def is_move_valid(self, final_position, board, turn=0):
        possible_moves, enpassant_move = self.generate_possible_moves(board, self.directions, turn)
        # check if final position exists in the space of possible moves
        if final_position == enpassant_move:
            # player is attempting a valid en passant move (does not yet account for possible check)
            self.enpassant = True  # piece is poised to make an en passant move
            return True
        return final_position in possible_moves

    def generate_possible_moves(self, board, directions, turn=0):
        """
        Special case:
        Pawn can only move diagonally one space to eliminate an opponent's piece.
        Pawn can move forward twice on its first move.
        En passant.
        """
        possible_moves = []
        count = 1
        enpassant_move = None
        for direction in self.directions:
            ystep = self.cardinal[direction][0]  # vertical step
            xstep = self.cardinal[direction][1]  # horizontal step
            move = (self.position[0] + ystep, self.position[1] + xstep)  # initialize first move
            enpassant, side = self.en_passant(board, turn)
            if count == 1 and self.is_move_in_bounds(move) and self.is_conflict(move, board) is None:
                # north or south for count == 1
                # pawn can move forward one space
                possible_moves.append(move)
                move = (move[0] + ystep, move[1] + xstep)  # move forward two spaces
                if not self.moved and self.is_conflict(move, board) is None:
                    # if the pawn has not moved yet, it can move forward two spaces
                    possible_moves.append(move)
            if count > 1 and self.is_move_in_bounds(move) and self.is_conflict(move, board) not in [self.player, None]:
                # diagonal for count > 1
                # pawn can only move diagonally one space to eliminate an opponent's piece
                possible_moves.append(move)
            if count > 1 and self.is_move_in_bounds(move) and enpassant:
                # diagonal for count > 1
                # there exists a possible en passant move
                if side == direction[1]:
                    # diagonal direction matches direction of en passant move
                    enpassant_move = move
                    possible_moves.append(enpassant_move)
            count += 1
        return possible_moves, enpassant_move

    def move(self, initial, final, turn):
        """
        Handles class attributes when Pawn is moved.
        :param initial: Tuple(row, col), initial position of Pawn
        :param final: Tuple(row, col), final position of Pawn
        :param turn: int, turn in Chess match
        """
        if self.first_move == 0:
            # Pawn is making its first move
            self.first_move = turn  # specify match turn the first move is made (info used for en passant)
            self.moved = True  # Pawn has moved
            if abs(final[0] - initial[0]) == 2:
                # initial move is a two step
                self.two_step = True

    def en_passant(self, board, turn):
        """
        Determines if an en passant move is available
        :param board: 2D List, holds current positions on all game pieces
        :param turn: int, turn in Chess match
        :return: (boolean, string or NoneType), returns True if en passant move exists (with direction), False otherwise
        """
        if self.is_move_in_bounds((self.position[0], self.position[1] + 1)):
            # look at adjacent square in the east direction
            adj_east = board[self.position[0]][self.position[1] + 1]
            if type(adj_east) is Pawn:
                if self.player != adj_east.player and adj_east.two_step and turn - adj_east.first_move == 1:
                    # east adjacent square holds a Pawn that took a two step move in previous turn
                    return True, 'E'
        if self.is_move_in_bounds((self.position[0], self.position[1] - 1)):
            # look at adjacent square in the west direction
            adj_west = board[self.position[0]][self.position[1] - 1]
            if type(adj_west) is Pawn:
                if self.player != adj_west.player and adj_west.two_step and turn - adj_west.first_move == 1:
                    # west adjacent square holds a Pawn that took a two step move in previous turn
                    return True, 'W'
                return False, None
            return False, None
        return False, None

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "P" if self.player == 'white' else "p"


class Rook(ChessPiece):
    name = 'rook'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.max_moves = 7
        self.directions = ['N', 'S', 'E', 'W']

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "R" if self.player == 'white' else "r"


class Knight(ChessPiece):
    # knights move in L-shaped steps
    knight_steps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    name = 'knight'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.max_moves = 1

    def generate_possible_moves(self, board, directions, turn=0):
        """
        Special case:
        knights only move in L-shaped movements
        """
        possible_moves = []
        for step in self.knight_steps:
            move = (self.position[0] + step[0], self.position[1] + step[1])
            if self.is_move_in_bounds(move) and self.is_conflict(move, board) != self.player:
                possible_moves.append(move)
        return possible_moves

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "N" if self.player == 'white' else "n"


class Bishop(ChessPiece):
    name = 'bishop'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.max_moves = 7
        self.directions = ['NE', 'NW', 'SE', 'SW']

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "B" if self.player == 'white' else "b"


class Queen(ChessPiece):
    name = 'queen'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.max_moves = 7
        self.directions = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "Q" if self.player == 'white' else "q"


class King(ChessPiece):
    name = 'king'

    def __init__(self, position, player):
        ChessPiece.__init__(self, position, player)
        self.max_moves = 1
        self.directions = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']

    def is_checked(self, king_position, board, active_pieces, bool_only=True):
        """
        Determine if King is in check given current or simulated board state
        :param king_position: Tuple(row, col), board position of King
        :param board: 2D List, holds current/simulated positions on all game pieces
        :param active_pieces: Dict of str:list, holds chess pieces in play for each player in current/simulation state
        :param bool_only: boolean, set to False to return opponent piece that has placed King in check
        :return: boolean, True if king is in check or chess piece that places king in check, False otherwise
        """
        opponent = 'white' if self.player == 'black' else 'black'
        for piece in active_pieces[opponent]:
            # iterate through all opponent's active pieces
            if piece.is_move_valid(king_position, board):
                # opponent's piece can move to kings position, indicating check
                if bool_only:
                    return True
                else:
                    # return piece that places king in check
                    return piece
        return False

    def __str__(self):
        # white pieces are uppercase, black pieces are lowercase
        return "K" if self.player == 'white' else "k"
