# ai.py — AI Engine (Easy / Medium / Hard)

import random
from board import Board, EMPTY, PLAYER_X, PLAYER_O, WIN_CONDITIONS

# ---------------------------------------------------------------------------
# HEURISTIC EVALUATION
# ---------------------------------------------------------------------------

# Position scores — center is most valuable, corners next, edges least
POSITION_SCORES = {
    4: 10,              # Center
    0: 5, 2: 5,         # Corners
    6: 5, 8: 5,
    1: 0, 3: 0,         # Edges
    5: 0, 7: 0
}

def heuristic_score(board, index, player):
    """
    Score a single move at `index` for `player` based on:
      - Immediate win          → +100
      - Block opponent's win   → +50
      - Position value         → +10 (center), +5 (corner), +0 (edge)
      - Two-in-a-row potential → +20 per line with 2 of player's marks

    Returns (total_score, explanation_string)
    """
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
    reasons = []
    score = 0

    # --- Check: does this move win immediately? ---
    test = board.get_board_copy()
    test.make_move(index, player)
    winner, _ = test.check_winner()
    if winner == player:
        score += 100
        reasons.append("Win in next move (+100)")

    # --- Check: does this move block opponent's win? ---
    test2 = board.get_board_copy()
    test2.make_move(index, opponent)
    winner2, _ = test2.check_winner()
    if winner2 == opponent:
        score += 50
        reasons.append("Blocks opponent's win (+50)")

    # --- Position value ---
    pos_val = POSITION_SCORES.get(index, 0)
    if pos_val > 0:
        label = "Center" if index == 4 else "Corner"
        score += pos_val
        reasons.append(f"{label} position (+{pos_val})")

    # --- Two-in-a-row potential ---
    two_in_row = 0
    for combo in WIN_CONDITIONS:
        if index in combo:
            marks = [board.cells[i] for i in combo if i != index]
            if marks.count(player) == 1 and marks.count(EMPTY) == 1:
                two_in_row += 1
    if two_in_row > 0:
        bonus = two_in_row * 20
        score += bonus
        reasons.append(f"Two-in-a-row potential (+{bonus})")

    explanation = f"Move: {index_to_label(index)} → " + ", ".join(reasons) + f". Total: {score}"
    return score, explanation


def index_to_label(index):
    """Convert a flat board index to a human-readable label."""
    labels = {
        0: "Top-Left",    1: "Top-Center",    2: "Top-Right",
        3: "Mid-Left",    4: "Center",         5: "Mid-Right",
        6: "Bot-Left",    7: "Bot-Center",     8: "Bot-Right"
    }
    return labels.get(index, str(index))


# ---------------------------------------------------------------------------
# EASY MODE — Random moves
# ---------------------------------------------------------------------------

def easy_move(board, player):
    """Pick a random available move. Returns (index, explanation)."""
    moves = board.get_available_moves()
    if not moves:
        return None, ""
    index = random.choice(moves)
    _, explanation = heuristic_score(board, index, player)
    explanation = "Random move. " + explanation
    return index, explanation


# ---------------------------------------------------------------------------
# MEDIUM MODE — Minimax with depth limit (depth 3)
# ---------------------------------------------------------------------------

MEDIUM_DEPTH_LIMIT = 3

def medium_move(board, player):
    """
    Use minimax limited to MEDIUM_DEPTH_LIMIT.
    No alpha-beta pruning — intentionally weaker than hard mode.
    Returns (best_move_index, explanation).
    """
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
    best_score = float("-inf")
    best_move = None

    for move in board.get_available_moves():
        board.make_move(move, player)
        score = _minimax_medium(board, 0, False, player, opponent)
        board.undo_move(move)
        if score > best_score:
            best_score = score
            best_move = move

    _, explanation = heuristic_score(board, best_move, player)
    explanation = "Minimax (depth 3). " + explanation
    return best_move, explanation


def _minimax_medium(board, depth, is_maximizing, player, opponent):
    """Minimax without alpha-beta, stops at MEDIUM_DEPTH_LIMIT."""
    winner, _ = board.check_winner()
    if winner == player:
        return 10 - depth
    if winner == opponent:
        return depth - 10
    if board.is_draw() or depth >= MEDIUM_DEPTH_LIMIT:
        return 0  # Neutral — can't see far enough to decide

    if is_maximizing:
        best = float("-inf")
        for move in board.get_available_moves():
            board.make_move(move, player)
            best = max(best, _minimax_medium(board, depth + 1, False, player, opponent))
            board.undo_move(move)
        return best
    else:
        best = float("inf")
        for move in board.get_available_moves():
            board.make_move(move, opponent)
            best = min(best, _minimax_medium(board, depth + 1, True, player, opponent))
            board.undo_move(move)
        return best


# ---------------------------------------------------------------------------
# HARD MODE — Full Minimax + Alpha-Beta Pruning + Heuristic tiebreak
# ---------------------------------------------------------------------------

def hard_move(board, player):
    """
    Full minimax with alpha-beta pruning.
    Uses heuristic score to break ties between equally scored moves.
    Returns (best_move_index, explanation_string).
    """
    opponent = PLAYER_O if player == PLAYER_X else PLAYER_X
    best_score = float("-inf")
    best_move = None
    best_explanation = ""

    for move in board.get_available_moves():
        board.make_move(move, player)
        score = _minimax_hard(board, 0, False, float("-inf"), float("inf"), player, opponent)
        board.undo_move(move)

        # Tiebreak using heuristic score
        h_score, explanation = heuristic_score(board, move, player)
        combined = score * 1000 + h_score  # Minimax result dominates; heuristic breaks ties

        if combined > best_score:
            best_score = combined
            best_move = move
            best_explanation = "Minimax + Alpha-Beta pruning. " + explanation

    return best_move, best_explanation


def _minimax_hard(board, depth, is_maximizing, alpha, beta, player, opponent):
    """
    Full minimax with alpha-beta pruning.

    Alpha: best score the maximizer can guarantee so far.
    Beta:  best score the minimizer can guarantee so far.
    Pruning: if beta <= alpha, stop exploring this branch (it won't be chosen).
    """
    winner, _ = board.check_winner()
    if winner == player:
        return 10 - depth   # Win sooner = better score
    if winner == opponent:
        return depth - 10   # Lose later = less bad
    if board.is_draw():
        return 0

    if is_maximizing:
        best = float("-inf")
        for move in board.get_available_moves():
            board.make_move(move, player)
            score = _minimax_hard(board, depth + 1, False, alpha, beta, player, opponent)
            board.undo_move(move)
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # ✂️ Beta cut-off — minimizer won't allow this
        return best
    else:
        best = float("inf")
        for move in board.get_available_moves():
            board.make_move(move, opponent)
            score = _minimax_hard(board, depth + 1, True, alpha, beta, player, opponent)
            board.undo_move(move)
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break  # ✂️ Alpha cut-off — maximizer won't allow this
        return best


# ---------------------------------------------------------------------------
# HINT — Best move suggestion for the human player
# ---------------------------------------------------------------------------

def get_hint(board, player):
    """
    Suggest the best move for the human player using hard mode logic.
    Returns (move_index, explanation_string).
    """
    return hard_move(board, player)
