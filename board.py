# board.py — Core Game Logic

EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"

# All possible winning combinations (rows, columns, diagonals)
WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
    [0, 4, 8], [2, 4, 6]              # Diagonals
]

class Board:
    def __init__(self):
        # The board is a flat list of 9 cells, indexed 0–8
        # Visual layout:
        #  0 | 1 | 2
        #  3 | 4 | 5
        #  6 | 7 | 8
        self.cells = [EMPTY] * 9
        self.current_turn = PLAYER_X  # X always goes first

    def reset(self):
        """Reset the board to its initial empty state."""
        self.cells = [EMPTY] * 9
        self.current_turn = PLAYER_X

    def is_valid_move(self, index):
        """Check if a cell is empty and the index is within range."""
        return 0 <= index <= 8 and self.cells[index] == EMPTY

    def make_move(self, index, player):
        """
        Place a player's mark on the board.
        Returns True if the move was successful, False otherwise.
        """
        if self.is_valid_move(index):
            self.cells[index] = player
            return True
        return False

    def undo_move(self, index):
        """Remove a mark from the board (used by AI and undo feature)."""
        self.cells[index] = EMPTY

    def get_available_moves(self):
        """Return a list of all empty cell indices."""
        return [i for i, cell in enumerate(self.cells) if cell == EMPTY]

    def check_winner(self):
        """
        Check if any player has won.
        Returns the winning player ("X" or "O") and the winning combination,
        or (None, None) if no winner yet.
        """
        for combo in WIN_CONDITIONS:
            a, b, c = combo
            if (self.cells[a] != EMPTY and
                self.cells[a] == self.cells[b] == self.cells[c]):
                return self.cells[a], combo  # winner, winning line
        return None, None

    def is_draw(self):
        """Return True if the board is full and there is no winner."""
        winner, _ = self.check_winner()
        return winner is None and len(self.get_available_moves()) == 0

    def is_game_over(self):
        """Return True if the game has ended (win or draw)."""
        winner, _ = self.check_winner()
        return winner is not None or self.is_draw()

    def switch_turn(self):
        """Toggle the current turn between X and O."""
        self.current_turn = PLAYER_O if self.current_turn == PLAYER_X else PLAYER_X

    def get_board_copy(self):
        """Return a fresh Board object with the same cell state (used by AI)."""
        copy = Board()
        copy.cells = self.cells[:]
        copy.current_turn = self.current_turn
        return copy

    def display(self):
        """Print the board to the console (useful for debugging)."""
        print()
        for row in range(3):
            print(" | ".join(self.cells[row * 3: row * 3 + 3]))
            if row < 2:
                print("-" * 9)
        print()
