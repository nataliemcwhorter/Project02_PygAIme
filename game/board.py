import numpy as np
import copy

"""
Connect 4 Board class
creates and defines the connect 4 board
creates the functions that interact with the connect 4 board
"""
class Connect4Board:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        # 0 = empty, 1 = player 1, 2 = player 2

    # resets board to original state
    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = 0

    #checks if move is valid
    def is_valid_move(self, col):
        if col < 0 or col >= self.cols:
            return False
        if self.board[0][col] == 0:
            return True
        return False

    #makes a move, returns row where new piece is
    def make_move(self, col, player):
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = player
                return row
        return -1

    # checks if the last piece put down won the game
    def check_winner(self, player, last_row, last_col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # positive direction
            r, c = last_row + dr, last_col + dc
            while (0 <= r < self.rows and 0 <= c < self.cols and
                   self.board[r][c] == player):
                count += 1
                r += dr
                c += dc
            # negative direction
            r, c = last_row - dr, last_col - dc
            while (0 <= r < self.rows and 0 <= c < self.cols and
                   self.board[r][c] == player):
                count += 1
                r -= dr
                c -= dc
            if count >= 4:
                return True
        return False

    # returns list of valid column numbers
    def get_valid_moves(self):
        valid_moves = []
        for col in range(self.cols):
            if self.is_valid_move(col):
                valid_moves.append(col)
        return valid_moves

    # checks if board is full
    def is_full(self):
        if self.get_valid_moves() == []:
            return True
        return False

    # gets current state of the board for the ai
    def get_board_state(self):
        return self.board.flatten()

    # copies the board so we dont mess it up when checking
    def copy(self):
        new = copy.deepcopy(self)
        return new

    def __str__(self):
        return str(self.board)