# 2 Player Chess
This program was implemented using Python and object-oriented principles.

## Overview
1. [main.py](main.py) - This module contains the script for running the game in a terminal.
2. [match.py](match.py) - This module defines a Match class that uses the Board class to
facilitate game play.
3. [board.py](board.py) - This module defines a Board class that holds the chessboard state
and is able to extract important information from the chessboard state.
4. [pieces.py](pieces.py) - This module defines classes for the fundamental units of the
program, the chess pieces.

### Program Layers
Complexity is abstracted away in the following order:
1. main
2. match (abstracts complexity from main)
3. board (abstracts complexity from match)
4. pieces (abstracts complexity from board)

## How to play
Players can play the game through a command line interface.
All you have to do is clone this repository and run main.py!

## Unit Tests
[test_match.py](test_match.py) holds unit tests for [match.py](match.py)

[test_board.py](test_board.py) holds unit tests for [board.py](board.py)

[test_pieces.py](test_pieces.py) holds unit tests for [pieces.py](pieces.py)