# gui.py — Tkinter GUI (clean, resizable, minimal)

import tkinter as tk
from tkinter import font
from game import Game, MODE_PVP, MODE_PVAI, DIFF_EASY, DIFF_MEDIUM, DIFF_HARD
from board import PLAYER_X, PLAYER_O

# ---------------------------------------------------------------------------
# THEME
# ---------------------------------------------------------------------------

BG         = "#f5f5f5"
PANEL_BG   = "#ffffff"
BORDER     = "#e0e0e0"
TEXT       = "#1a1a1a"
MUTED      = "#888888"
ACCENT     = "#4f46e5"
ACCENT_FG  = "#ffffff"
X_COLOR    = "#e53935"
O_COLOR    = "#1e88e5"
WIN_BG     = "#c8e6c9"
WIN_FG     = "#1b5e20"
HINT_BG    = "#fff9c4"
HINT_FG    = "#f57f17"
CELL_BG    = "#ffffff"
CELL_HOVER = "#ede9fe"
CELL_USED  = "#f5f5f5"
BTN_BG     = "#eeeeee"
BTN_DIS    = "#d0d0d0"

# ---------------------------------------------------------------------------
# TOGGLE BUTTON
# ---------------------------------------------------------------------------

class ToggleButton(tk.Button):
    def __init__(self, parent, text, group, value, on_select, **kwargs):
        super().__init__(parent, text=text, relief="flat", bd=0,
                         cursor="hand2", padx=14, pady=5, **kwargs)
        self.group     = group
        self.value     = value
        self.on_select = on_select
        self.active    = False
        self.bind("<Button-1>", self._click)
        self._set_inactive()

    def _click(self, event=None):
        for btn in self.group:
            btn._set_inactive()
        self._set_active()
        self.on_select(self.value)

    def _set_active(self):
        self.active = True
        self.config(bg=ACCENT, fg=ACCENT_FG)

    def _set_inactive(self):
        self.active = False
        self.config(bg=BTN_BG, fg=TEXT)

    def select(self):
        for btn in self.group:
            btn._set_inactive()
        self._set_active()


# ---------------------------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------------------------

class TicTacToeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe — AI")
        self.configure(bg=BG)
        self.minsize(460, 620)
        self.resizable(True, True)

        self.game       = Game()
        self.hint_index = None
        self.ai_delay   = 600

        self.mode_buttons = []
        self.diff_buttons = []

        self._build_fonts()
        self._build_ui()
        self._refresh()

    # -----------------------------------------------------------------------
    # FONTS
    # -----------------------------------------------------------------------

    def _build_fonts(self):
        self.font_title   = font.Font(family="Helvetica", size=15, weight="bold")
        self.font_cell    = font.Font(family="Helvetica", size=32, weight="bold")
        self.font_status  = font.Font(family="Helvetica", size=12, weight="bold")
        self.font_label   = font.Font(family="Helvetica", size=9,  weight="bold")
        self.font_btn     = font.Font(family="Helvetica", size=10, weight="bold")
        self.font_explain = font.Font(family="Helvetica", size=9)

    # -----------------------------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------------------------

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Title
        tk.Label(self, text="Tic Tac Toe", bg=BG, fg=TEXT,
                 font=self.font_title).grid(row=0, column=0, pady=(20, 4))

        # Controls
        ctrl = tk.Frame(self, bg=BG)
        ctrl.grid(row=1, column=0, pady=(0, 8), sticky="ew")
        ctrl.columnconfigure(0, weight=1)
        ctrl.columnconfigure(1, weight=1)
        self._build_controls(ctrl)

        # Status
        self.status_var = tk.StringVar(value="Your turn (X)")
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=ACCENT,
                 font=self.font_status).grid(row=2, column=0, pady=(4, 6))

        # Board
        board_outer = tk.Frame(self, bg=BG)
        board_outer.grid(row=3, column=0, sticky="nsew", padx=30)
        board_outer.columnconfigure(0, weight=1)
        board_outer.rowconfigure(0, weight=1)
        self._build_board(board_outer)

        # Action buttons
        actions = tk.Frame(self, bg=BG)
        actions.grid(row=4, column=0, pady=12)
        self._build_action_buttons(actions)

        # Explanation panel
        exp_outer = tk.Frame(self, bg=BORDER)
        exp_outer.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 20))
        exp_inner = tk.Frame(exp_outer, bg=PANEL_BG)
        exp_inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(exp_inner, text="MOVE EXPLANATION", bg=PANEL_BG, fg=MUTED,
                 font=self.font_label).pack(anchor="w", padx=12, pady=(8, 2))

        self.explain_text = tk.Text(
            exp_inner,
            bg=PANEL_BG, fg=TEXT,
            font=self.font_explain,
            relief="flat", bd=0,
            wrap="word",
            height=3,
            cursor="arrow",
            state="disabled",
            padx=12, pady=6
        )
        self.explain_text.pack(fill="x", expand=True)

    def _build_controls(self, parent):
        # Mode
        mode_frame = tk.Frame(parent, bg=BG)
        mode_frame.grid(row=0, column=0, padx=(30, 8), sticky="w")
        tk.Label(mode_frame, text="MODE", bg=BG, fg=MUTED,
                 font=self.font_label).pack(anchor="w", pady=(0, 4))
        mode_row = tk.Frame(mode_frame, bg=BG)
        mode_row.pack(anchor="w")
        self.mode_buttons = []
        for mode in [MODE_PVP, MODE_PVAI]:
            btn = ToggleButton(mode_row, text=mode, group=self.mode_buttons,
                               value=mode, on_select=self._on_mode_change,
                               font=self.font_btn)
            btn.pack(side="left", padx=(0, 4))
            self.mode_buttons.append(btn)
        self.mode_buttons[1].select()

        # Difficulty
        diff_frame = tk.Frame(parent, bg=BG)
        diff_frame.grid(row=0, column=1, padx=(8, 30), sticky="w")
        tk.Label(diff_frame, text="DIFFICULTY", bg=BG, fg=MUTED,
                 font=self.font_label).pack(anchor="w", pady=(0, 4))
        diff_row = tk.Frame(diff_frame, bg=BG)
        diff_row.pack(anchor="w")
        self.diff_buttons = []
        for diff in [DIFF_EASY, DIFF_MEDIUM, DIFF_HARD]:
            btn = ToggleButton(diff_row, text=diff, group=self.diff_buttons,
                               value=diff, on_select=self._on_diff_change,
                               font=self.font_btn)
            btn.pack(side="left", padx=(0, 4))
            self.diff_buttons.append(btn)
        self.diff_buttons[2].select()

    def _build_board(self, parent):
        board_frame = tk.Frame(parent, bg=BG)
        board_frame.grid(row=0, column=0)
        self.cell_buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            cell_frame = tk.Frame(board_frame, bg=BORDER, width=110, height=110)
            cell_frame.grid(row=row, column=col, padx=3, pady=3)
            cell_frame.grid_propagate(False)
            cell_frame.columnconfigure(0, weight=1)
            cell_frame.rowconfigure(0, weight=1)
            btn = tk.Button(cell_frame, text="", bg=CELL_BG, fg=TEXT,
                            font=self.font_cell, relief="flat", bd=0,
                            cursor="hand2",
                            command=lambda idx=i: self._on_cell_click(idx))
            btn.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
            btn.bind("<Enter>",  lambda e, b=btn:        self._on_cell_enter(b))
            btn.bind("<Leave>",  lambda e, b=btn, idx=i: self._on_cell_leave(b, idx))
            self.cell_buttons.append(btn)

    def _build_action_buttons(self, parent):
        cfg = dict(relief="flat", bd=0, cursor="hand2",
                   padx=16, pady=7, font=self.font_btn)

        self.hint_btn = tk.Button(parent, text="Hint", bg=BTN_BG, fg=TEXT,
                                  command=self._on_hint, **cfg)
        self.hint_btn.grid(row=0, column=0, padx=5)

        self.undo_btn = tk.Button(parent, text="Undo", bg=BTN_BG, fg=TEXT,
                                  command=self._on_undo, **cfg)
        self.undo_btn.grid(row=0, column=1, padx=5)

        self.redo_btn = tk.Button(parent, text="Redo", bg=BTN_BG, fg=TEXT,
                                  command=self._on_redo, **cfg)
        self.redo_btn.grid(row=0, column=2, padx=5)

        tk.Button(parent, text="New Game", bg=ACCENT, fg=ACCENT_FG,
                  command=self._on_new_game, **cfg).grid(row=0, column=3, padx=5)

        for btn in [self.hint_btn, self.undo_btn, self.redo_btn]:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=CELL_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BTN_BG))

    # -----------------------------------------------------------------------
    # EXPLANATION HELPER
    # -----------------------------------------------------------------------

    def _set_explanation(self, text):
        self.explain_text.config(state="normal")
        self.explain_text.delete("1.0", "end")
        self.explain_text.insert("end", text)
        self.explain_text.config(state="disabled")
        self.update_idletasks()
        w = self.explain_text.winfo_width()
        chars_per_line = max(1, w // 6)
        line_count = 0
        for line in text.split("\n"):
            line_count += max(1, (len(line) // chars_per_line) + 1)
        self.explain_text.config(height=max(2, line_count))

    # -----------------------------------------------------------------------
    # REFRESH
    # -----------------------------------------------------------------------

    def _refresh(self):
        cells     = self.game.get_cells()
        win_combo = self.game.win_combo

        for i, btn in enumerate(self.cell_buttons):
            mark = cells[i]
            if win_combo and i in win_combo:
                bg, fg = WIN_BG, WIN_FG
            elif i == self.hint_index:
                bg, fg = HINT_BG, HINT_FG
            elif mark == PLAYER_X:
                bg, fg = CELL_USED, X_COLOR
            elif mark == PLAYER_O:
                bg, fg = CELL_USED, O_COLOR
            else:
                bg, fg = CELL_BG, TEXT

            is_empty = mark == " "
            btn.config(
                text  = mark if not is_empty else "",
                bg    = bg,
                fg    = fg,
                state = "disabled" if (self.game.game_over or not is_empty) else "normal"
            )

        self.status_var.set(self.game.get_status_message())

        if self.game.last_explanation:
            self._set_explanation(self.game.last_explanation)
        elif self.hint_index is not None:
            pass
        elif not self.game.game_over:
            self._set_explanation("Make a move to see the explanation.")

        self.undo_btn.config(state="normal" if self.game.can_undo() else "disabled",
                             bg=BTN_BG if self.game.can_undo() else BTN_DIS)
        self.redo_btn.config(state="normal" if self.game.can_redo() else "disabled",
                             bg=BTN_BG if self.game.can_redo() else BTN_DIS)
        hint_ok = (not self.game.game_over
                   and not self.game.is_ai_turn())
        self.hint_btn.config(state="normal" if hint_ok else "disabled",
                             bg=BTN_BG if hint_ok else BTN_DIS)

    # -----------------------------------------------------------------------
    # EVENT HANDLERS
    # -----------------------------------------------------------------------

    def _on_cell_click(self, index):
        self.hint_index = None
        if not self.game.human_move(index):
            return
        self._refresh()
        if self.game.is_ai_turn():
            self.after(self.ai_delay, self._run_ai_move)

    def _on_hint(self):
        idx, explanation = self.game.request_hint()
        if idx is not None:
            self.hint_index = idx
            self._set_explanation("Hint → " + explanation)
            self._refresh()

    def _on_undo(self):
        self.hint_index = None
        self.game.undo()
        self._refresh()

    def _on_redo(self):
        self.hint_index = None
        self.game.redo()
        self._refresh()
        if self.game.is_ai_turn():
            self.after(self.ai_delay, self._run_ai_move)

    def _on_new_game(self):
        self.hint_index = None
        self.game.new_game()
        self._refresh()

    def _on_mode_change(self, value):
        self.hint_index = None
        self.game.set_mode(value)
        self._refresh()

    def _on_diff_change(self, value):
        self.game.set_difficulty(value)

    # -----------------------------------------------------------------------
    # AI RUNNER
    # -----------------------------------------------------------------------

    def _run_ai_move(self):
        if not self.game.is_ai_turn():
            return
        self.game.ai_move()
        self._refresh()


    # -----------------------------------------------------------------------
    # HOVER EFFECTS
    # -----------------------------------------------------------------------

    def _on_cell_enter(self, btn):
        if btn["state"] == "normal" and btn["text"] == "":
            btn.config(bg=CELL_HOVER)

    def _on_cell_leave(self, btn, index):
        if btn["text"] == "":
            if index == self.hint_index:
                btn.config(bg=HINT_BG)
            else:
                btn.config(bg=CELL_BG)