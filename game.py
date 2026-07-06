# game.py — Game State Manager

from board import Board, PLAYER_X, PLAYER_O, EMPTY
from ai import easy_move, medium_move, hard_move, get_hint

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

MODE_PVP   = "PvP"       # Human vs Human
MODE_PVAI  = "PvAI"      # Human vs AI
DIFF_EASY   = "Easy"
DIFF_MEDIUM = "Medium"
DIFF_HARD   = "Hard"

# ---------------------------------------------------------------------------
# GAME CLASS
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        self.board = Board()

        # Game settings
        self.mode       = MODE_PVAI
        self.difficulty = DIFF_HARD
        self.ai_player  = PLAYER_O   # In PvAI, AI plays as O by default
        self.human_player = PLAYER_X

        # Undo / Redo stacks
        # Each entry is a snapshot: (cells_list, current_turn)
        self.undo_stack = []
        self.redo_stack = []

        # Last AI explanation (shown in GUI)
        self.last_explanation = ""

        # Game status
        self.winner     = None   # "X", "O", or None
        self.win_combo  = None   # List of 3 indices forming the winning line
        self.game_over  = False

    # -----------------------------------------------------------------------
    # SETUP
    # -----------------------------------------------------------------------

    def set_mode(self, mode):
        """Set game mode and reset."""
        self.mode = mode
        self.new_game()

    def set_difficulty(self, difficulty):
        """Set AI difficulty (does not reset the game)."""
        self.difficulty = difficulty

    def set_ai_player(self, ai_player):
        """Choose which mark the AI plays as in PvAI mode."""
        self.ai_player = ai_player
        self.human_player = PLAYER_O if ai_player == PLAYER_X else PLAYER_X

    def new_game(self):
        """Reset everything for a fresh game."""
        self.board.reset()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.last_explanation = ""
        self.winner    = None
        self.win_combo = None
        self.game_over = False

    # -----------------------------------------------------------------------
    # MOVE HANDLING
    # -----------------------------------------------------------------------

    def _save_snapshot(self):
        """Push current board state onto the undo stack."""
        snapshot = (self.board.cells[:], self.board.current_turn)
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()   # Any new move wipes the redo history

    def _apply_snapshot(self, snapshot):
        """Restore board state from a snapshot tuple."""
        cells, turn = snapshot
        self.board.cells = cells[:]
        self.board.current_turn = turn
        # Recheck game status after restoring
        self.winner, self.win_combo = self.board.check_winner()
        self.game_over = self.board.is_game_over()

    def human_move(self, index):
        """
        Process a human player's move at `index`.
        Returns True if the move was accepted, False otherwise.
        """
        if self.game_over:
            return False
        if not self.board.is_valid_move(index):
            return False

        # In PvAI, only accept moves on the human's turn
        if self.mode == MODE_PVAI:
            if self.board.current_turn != self.human_player:
                return False

        self._save_snapshot()
        self.board.make_move(index, self.board.current_turn)
        self._update_status()
        if not self.game_over:
            self.board.switch_turn()
        return True

    def ai_move(self):
        """
        Execute one AI move based on the current difficulty.
        Returns the index played, or None if game is already over.
        Also sets self.last_explanation for hard mode.
        """
        if self.game_over:
            return None

        player = self.board.current_turn
        self.last_explanation = ""

        if self.difficulty == DIFF_EASY:
            index, explanation = easy_move(self.board, player)
            self.last_explanation = explanation

        elif self.difficulty == DIFF_MEDIUM:
            index, explanation = medium_move(self.board, player)
            self.last_explanation = explanation

        else:  # DIFF_HARD
            index, explanation = hard_move(self.board, player)
            self.last_explanation = explanation

        if index is None:
            return None

        self._save_snapshot()
        self.board.make_move(index, player)
        self._update_status()
        if not self.game_over:
            self.board.switch_turn()

        return index

    def _update_status(self):
        """Check and update winner / game_over after every move."""
        self.winner, self.win_combo = self.board.check_winner()
        self.game_over = self.board.is_game_over()

    # -----------------------------------------------------------------------
    # UNDO / REDO
    # -----------------------------------------------------------------------

    def undo(self):
        """
        Undo the last move(s).
        - In PvAI: undoes both the AI's move and the human's move (one full round).
        - In PvP: undoes one move at a time.
        Returns True if undo was performed.
        """
        if not self.undo_stack:
            return False

        if self.mode == MODE_PVAI and len(self.undo_stack) >= 2:
            # Pop AI move first, then human move
            redo_snapshot = (self.board.cells[:], self.board.current_turn)
            self.redo_stack.append(redo_snapshot)
            self.undo_stack.pop()            # Remove AI move snapshot
            snapshot = self.undo_stack.pop() # Go back to before human's move
        else:
            redo_snapshot = (self.board.cells[:], self.board.current_turn)
            self.redo_stack.append(redo_snapshot)
            snapshot = self.undo_stack.pop()

        self._apply_snapshot(snapshot)
        self.last_explanation = ""
        return True

    def redo(self):
        """
        Redo a previously undone move.
        Returns True if redo was performed.
        """
        if not self.redo_stack:
            return False

        undo_snapshot = (self.board.cells[:], self.board.current_turn)
        self.undo_stack.append(undo_snapshot)
        snapshot = self.redo_stack.pop()
        self._apply_snapshot(snapshot)
        return True

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0

    # -----------------------------------------------------------------------
    # HINT
    # -----------------------------------------------------------------------

    def request_hint(self):
        """
        Get the best move suggestion for the current human player.
        Returns (index, explanation_string), or (None, "") if unavailable.
        """
        if self.game_over:
            return None, ""

        player = self.board.current_turn

        # In PvAI, only hint for the human
        if self.mode == MODE_PVAI and player != self.human_player:
            return None, ""

        index, explanation = get_hint(self.board, player)
        return index, explanation

    # -----------------------------------------------------------------------
    # STATUS HELPERS (used by GUI)
    # -----------------------------------------------------------------------

    def get_current_turn(self):
        return self.board.current_turn

    def get_cells(self):
        return self.board.cells[:]

    def is_ai_turn(self):
        """Return True if it's currently the AI's turn."""
        if self.mode == MODE_PVAI:
            return self.board.current_turn == self.ai_player and not self.game_over
        return False

    def get_status_message(self):
        """Return a string describing the current game state for the GUI."""
        if self.winner:
            if self.mode == MODE_PVAI:
                if self.winner == self.human_player:
                    return "You win! 🎉"
                else:
                    return "AI wins!"
            return f"Player {self.winner} wins!"
        if self.board.is_draw():
            return "It's a draw!"
        turn = self.board.current_turn
        if self.mode == MODE_PVAI:
            if turn == self.human_player:
                return f"Your turn ({turn})"
            else:
                return f"AI is thinking... ({turn})"
        return f"Player {turn}'s turn"