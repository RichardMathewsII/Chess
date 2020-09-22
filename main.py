"""
Runs chess match through command line
"""
from match import Match


def main():
    match = Match()
    promotions = ['queen', 'rook', 'bishop', 'knight']
    print('Welcome to Chess!')
    print('This Chess program supports en passant moves and pawn promotion, but does NOT support castling')
    print()
    match.white = input('Enter the name of player 1 (controls white): ')
    match.black = input('Enter the name of player 2 (controls black): ')
    print('White goes first.')
    while not match.checkmate:
        print('-' * 30)
        print()
        print("{}'s turn ({}-{})".format(match.white, match.turn, match.notation[match.turn])) \
            if match.turn == 'white' \
            else print("{}'s turn ({}-{})".format(match.black, match.turn, match.notation[match.turn]))
        match.chessboard.print()
        move = 'back'
        while move == 'back':
            # loop for when player wants to select different piece
            if match.incheck:
                # player's king is in check
                print('{}\'s king is in check'.format(match.white if match.turn == 'white' else match.black))
                match.incheck = False
            position = input('Select a piece to move using algebraic notation (ex. \'a1\'): ')
            while not match.select_piece(position):
                # loop to ensure player inputs valid board position in algebraic notation
                position = input('Select a piece to move using algebraic notation (ex. \'a1\'): ')
            move = input('Enter a move in algebraic notation (ex. \'a1\') or enter "back" to pick a different piece: ')
            while move != 'back' and not match.move(move):
                # loop to ensure player is making a valid move
                move = input('Enter a move in algebraic notation (ex. \'a1\') '
                             'or enter "back" to pick a different piece: ')
        if match.is_pawn_promotion():
            # player is eligible to promote a pawn
            print("{} is eligible to promote a pawn to one of {}.".format(match.turn, promotions))
            promotion = input('Enter desired promotion from list above: ')
            while promotion not in promotions:
                promotion = input('INVALID entry. Please choose promotion from {}: '.format(promotions))
            match.promote_pawn(promotion)
        match.check()  # determine check or checkmate exists
        match.switch_turns()  # switch turns


if __name__ == '__main__':
    main()
