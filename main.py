"""
TypeSprint - Modern Typing Speed Tracker & Tester
Built with Python Tkinter, Object-Oriented Programming, and File Handling.
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

from sentences import SENTENCES
from history_manager import HistoryManager


# ==========================================
# THEME & PALETTE (Modern Dark Palette)
# ==========================================
THEME = {
    "bg_dark": "#181825",
    "bg_card": "#1e1e2e",
    "bg_input": "#313244",
    "bg_input_focus": "#45475a",
    "text_primary": "#cdd6f4",
    "text_secondary": "#a6adc8",
    "text_muted": "#585b70",
    "accent_blue": "#89b4fa",
    "accent_cyan": "#89dceb",
    "accent_purple": "#cba6f7",
    "accent_green": "#a6e3a1",
    "accent_red": "#f38ba8",
    "accent_yellow": "#f9e2af",
    "font_family": "Segoe UI",
    "mono_family": "Consolas"
}


class TypingSpeedTracker(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("⚡ TypeSprint - Typing Speed Tracker")
        self.geometry("960x720")
        self.minsize(840, 600)
        self.configure(bg=THEME["bg_dark"])

        # History backend
        self.history = HistoryManager()

        # State Variables
        self.difficulty_var = tk.StringVar(value="Medium")
        self.mode_var = tk.StringVar(value="Sentence")  # "Sentence", "30s", "60s"
        self.target_text = ""
        self.is_running = False
        self.test_completed = False
        self.start_time = None
        self.timer_job = None
        self.time_limit = None  # None for sentence mode, or 30/60 for timed
        self.elapsed_seconds = 0
        self.total_errors = 0

        # Build UI
        self._init_styles()
        self._create_widgets()
        self._load_new_sentence()

        # Keyboard shortcuts
        self.bind("<Control-r>", lambda event: self.restart_test())
        self.bind("<Control-R>", lambda event: self.restart_test())

    def _init_styles(self):
        """Configure ttk styles for clean modern appearance."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Combobox style
        style.configure(
            "Dark.TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            arrowcolor=THEME["accent_cyan"],
            bordercolor=THEME["bg_card"],
            lightcolor=THEME["bg_card"],
            darkcolor=THEME["bg_card"],
            padding=5
        )

        # Treeview style for history
        style.configure(
            "History.Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            fieldbackground=THEME["bg_card"],
            rowheight=28,
            font=(THEME["font_family"], 10)
        )
        style.configure(
            "History.Treeview.Heading",
            background=THEME["bg_input"],
            foreground=THEME["accent_cyan"],
            font=(THEME["font_family"], 10, "bold")
        )
        style.map(
            "History.Treeview",
            background=[("selected", THEME["bg_input_focus"])],
            foreground=[("selected", THEME["accent_yellow"])]
        )

    def _create_widgets(self):
        """Build the complete layout."""
        # Main container with padding
        main_frame = tk.Frame(self, bg=THEME["bg_dark"], padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header Frame
        header_frame = tk.Frame(main_frame, bg=THEME["bg_dark"])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="⚡ TypeSprint",
            font=(THEME["font_family"], 22, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_dark"]
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_frame,
            text="Typing Speed & Accuracy Tracker",
            font=(THEME["font_family"], 11),
            fg=THEME["text_secondary"],
            bg=THEME["bg_dark"]
        )
        subtitle_label.pack(side=tk.LEFT, padx=(12, 0), pady=(7, 0))

        # History button in header
        history_btn = tk.Button(
            header_frame,
            text="📊 History & Stats",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["bg_input"],
            fg=THEME["accent_purple"],
            activebackground=THEME["bg_input_focus"],
            activeforeground=THEME["accent_yellow"],
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
            command=self.show_history_window
        )
        history_btn.pack(side=tk.RIGHT)

        # 2. Controls Bar (Difficulty & Mode selector)
        ctrl_frame = tk.Frame(main_frame, bg=THEME["bg_card"], padx=20, pady=12)
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        # Difficulty
        tk.Label(
            ctrl_frame,
            text="Difficulty:",
            font=(THEME["font_family"], 10, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"]
        ).pack(side=tk.LEFT, padx=(0, 8))

        diff_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=10,
            style="Dark.TCombobox"
        )
        diff_combo.pack(side=tk.LEFT, padx=(0, 25))
        diff_combo.bind("<<ComboboxSelected>>", lambda e: self.restart_test())

        # Mode
        tk.Label(
            ctrl_frame,
            text="Mode:",
            font=(THEME["font_family"], 10, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"]
        ).pack(side=tk.LEFT, padx=(0, 8))

        mode_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.mode_var,
            values=["Sentence", "30s Sprint", "60s Challenge"],
            state="readonly",
            width=14,
            style="Dark.TCombobox"
        )
        mode_combo.pack(side=tk.LEFT)
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self.restart_test())

        # Shortcut tip on right
        tip_label = tk.Label(
            ctrl_frame,
            text="Press Ctrl+R or Restart button to reload",
            font=(THEME["font_family"], 9, "italic"),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        tip_label.pack(side=tk.RIGHT)

        # 3. Live Stats Dashboard (Cards)
        stats_frame = tk.Frame(main_frame, bg=THEME["bg_dark"])
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.wpm_card = self._create_stat_card(stats_frame, 0, "🚀 WPM", "0", THEME["accent_cyan"])
        self.accuracy_card = self._create_stat_card(stats_frame, 1, "🎯 Accuracy", "100%", THEME["accent_green"])
        self.time_card = self._create_stat_card(stats_frame, 2, "⏱ Time", "0.0s", THEME["accent_yellow"])
        self.errors_card = self._create_stat_card(stats_frame, 3, "❌ Errors", "0", THEME["accent_red"])

        # 4. Target Text Box (Highlighted display)
        prompt_label = tk.Label(
            main_frame,
            text="Prompt Text:",
            font=(THEME["font_family"], 11, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_dark"]
        )
        prompt_label.pack(anchor="w", pady=(0, 6))

        self.prompt_text_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            height=4,
            font=(THEME["mono_family"], 13),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            bd=0,
            padx=16,
            pady=14,
            cursor="arrow",
            state=tk.DISABLED
        )
        self.prompt_text_widget.pack(fill=tk.X, pady=(0, 15))

        # Text highlight tags
        self.prompt_text_widget.tag_configure("correct", foreground=THEME["accent_green"])
        self.prompt_text_widget.tag_configure("incorrect", foreground=THEME["accent_red"], underline=True)
        self.prompt_text_widget.tag_configure("current", background=THEME["bg_input_focus"], foreground=THEME["accent_yellow"])
        self.prompt_text_widget.tag_configure("remaining", foreground=THEME["text_muted"])

        # 5. User Typing Input Box
        input_label = tk.Label(
            main_frame,
            text="Type here to start:",
            font=(THEME["font_family"], 11, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_dark"]
        )
        input_label.pack(anchor="w", pady=(0, 6))

        self.input_entry = tk.Text(
            main_frame,
            wrap=tk.WORD,
            height=4,
            font=(THEME["mono_family"], 13),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_cyan"],
            bd=0,
            padx=16,
            pady=14
        )
        self.input_entry.pack(fill=tk.X, pady=(0, 15))
        self.input_entry.bind("<KeyRelease>", self._on_key_release)
        # Prevent pasting to ensure genuine typing test
        self.input_entry.bind("<<Paste>>", lambda e: "break")

        # 6. Action Buttons Bar & Feedback Message
        actions_frame = tk.Frame(main_frame, bg=THEME["bg_dark"])
        actions_frame.pack(fill=tk.X)

        self.status_msg = tk.Label(
            actions_frame,
            text="Start typing when you are ready. The timer will trigger automatically!",
            font=(THEME["font_family"], 10, "italic"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_dark"]
        )
        self.status_msg.pack(side=tk.LEFT)

        restart_btn = tk.Button(
            actions_frame,
            text="🔄 Restart (Ctrl+R)",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["accent_blue"],
            fg=THEME["bg_dark"],
            activebackground=THEME["accent_cyan"],
            activeforeground=THEME["bg_dark"],
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            command=self.restart_test
        )
        restart_btn.pack(side=tk.RIGHT)

    def _create_stat_card(self, parent, col, title, initial_val, color):
        """Helper to create a dashboard stat card widget."""
        card = tk.Frame(parent, bg=THEME["bg_card"], padx=15, pady=12)
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        title_lbl = tk.Label(
            card,
            text=title,
            font=(THEME["font_family"], 9, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"]
        )
        title_lbl.pack(anchor="w")

        val_lbl = tk.Label(
            card,
            text=initial_val,
            font=(THEME["font_family"], 20, "bold"),
            fg=color,
            bg=THEME["bg_card"]
        )
        val_lbl.pack(anchor="w", pady=(4, 0))

        return val_lbl

    def _load_new_sentence(self):
        """Pick a new random sentence based on selected difficulty."""
        diff = self.difficulty_var.get()
        choices = SENTENCES.get(diff, SENTENCES["Medium"])
        self.target_text = random.choice(choices)

        # Update prompt text widget
        self.prompt_text_widget.config(state=tk.NORMAL)
        self.prompt_text_widget.delete("1.0", tk.END)
        self.prompt_text_widget.insert(tk.END, self.target_text)
        self.prompt_text_widget.tag_add("remaining", "1.0", tk.END)
        self.prompt_text_widget.config(state=tk.DISABLED)

    def _on_key_release(self, event=None):
        """Handle real-time typing input, live metrics, and character highlighting."""
        if self.test_completed:
            return

        user_text = self.input_entry.get("1.0", "end-1c")

        # Automatically start timer on first keypress
        if not self.is_running and len(user_text) > 0:
            self._start_timer()

        if not self.is_running:
            return

        # Update character-by-character highlights in target prompt
        self._highlight_prompt(user_text)

        # Compute metrics
        self._update_live_metrics(user_text)

        # Check for test completion
        # In Sentence mode: finish when typed text matches or exceeds length
        mode = self.mode_var.get()
        if mode == "Sentence" and len(user_text) >= len(self.target_text):
            self._finish_test()

    def _highlight_prompt(self, user_text):
        """Dynamically color correct/incorrect/current characters in prompt widget."""
        self.prompt_text_widget.config(state=tk.NORMAL)

        # Clear existing tags
        for tag in ["correct", "incorrect", "current", "remaining"]:
            self.prompt_text_widget.tag_remove(tag, "1.0", tk.END)

        errors = 0
        user_len = len(user_text)
        target_len = len(self.target_text)

        for i in range(target_len):
            char_idx = f"1.0 + {i} chars"
            next_idx = f"1.0 + {i + 1} chars"

            if i < user_len:
                if user_text[i] == self.target_text[i]:
                    self.prompt_text_widget.tag_add("correct", char_idx, next_idx)
                else:
                    self.prompt_text_widget.tag_add("incorrect", char_idx, next_idx)
                    errors += 1
            elif i == user_len:
                # Active cursor character
                self.prompt_text_widget.tag_add("current", char_idx, next_idx)
            else:
                self.prompt_text_widget.tag_add("remaining", char_idx, next_idx)

        # Extra errors if typed beyond target length
        if user_len > target_len:
            errors += (user_len - target_len)

        self.total_errors = errors
        self.errors_card.config(text=str(errors))
        self.prompt_text_widget.config(state=tk.DISABLED)

    def _start_timer(self):
        """Start test session timer."""
        self.is_running = True
        self.start_time = time.time()
        mode = self.mode_var.get()

        if "30s" in mode:
            self.time_limit = 30
        elif "60s" in mode:
            self.time_limit = 60
        else:
            self.time_limit = None

        self.status_msg.config(text="🔥 Test in progress! Keep going...", fg=THEME["accent_yellow"])
        self._tick_timer()

    def _tick_timer(self):
        """Timer callback loop executing every 100ms."""
        if not self.is_running:
            return

        now = time.time()
        self.elapsed_seconds = now - self.start_time

        if self.time_limit is not None:
            # Countdown mode
            time_remaining = max(0.0, self.time_limit - self.elapsed_seconds)
            self.time_card.config(text=f"{time_remaining:.1f}s")

            if time_remaining <= 0:
                self._finish_test()
                return
        else:
            # Elapsed count up
            self.time_card.config(text=f"{self.elapsed_seconds:.1f}s")

        # Update metrics periodically
        user_text = self.input_entry.get("1.0", "end-1c")
        self._update_live_metrics(user_text)

        self.timer_job = self.after(100, self._tick_timer)

    def _update_live_metrics(self, user_text):
        """Calculate and display WPM and Accuracy in real time."""
        if self.elapsed_seconds <= 0:
            return

        total_typed = len(user_text)
        if total_typed == 0:
            return

        # Calculate correct characters
        correct_chars = sum(
            1 for i, c in enumerate(user_text)
            if i < len(self.target_text) and c == self.target_text[i]
        )

        # Standard definition: 1 word = 5 keystrokes
        minutes = max(0.01, self.elapsed_seconds / 60.0)
        wpm = round((correct_chars / 5.0) / minutes)
        accuracy = round((correct_chars / total_typed) * 100, 1)

        self.wpm_card.config(text=str(max(0, wpm)))
        self.accuracy_card.config(text=f"{accuracy}%")

    def _finish_test(self):
        """End the test, disable typing, calculate final results, and record in history."""
        self.is_running = False
        self.test_completed = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        self.input_entry.config(state=tk.DISABLED)

        # Calculate final stats
        user_text = self.input_entry.get("1.0", "end-1c")
        total_typed = len(user_text)
        correct_chars = sum(
            1 for i, c in enumerate(user_text)
            if i < len(self.target_text) and c == self.target_text[i]
        )

        elapsed = max(1.0, self.elapsed_seconds)
        minutes = elapsed / 60.0
        final_wpm = round((correct_chars / 5.0) / minutes) if total_typed > 0 else 0
        final_acc = round((correct_chars / total_typed) * 100, 1) if total_typed > 0 else 0.0

        # Save to history
        self.history.save_record(
            wpm=final_wpm,
            accuracy=final_acc,
            difficulty=self.difficulty_var.get(),
            duration_sec=round(elapsed),
            errors=self.total_errors
        )

        self.status_msg.config(
            text=f"🎉 Test Complete! WPM: {final_wpm} | Accuracy: {final_acc}%",
            fg=THEME["accent_green"]
        )

        # Show Results Modal
        self._show_results_dialog(final_wpm, final_acc, round(elapsed), correct_chars, self.total_errors)

    def _show_results_dialog(self, wpm, accuracy, duration, correct_chars, errors):
        """Pop up a stylized score card modal."""
        modal = tk.Toplevel(self)
        modal.title("Test Results")
        modal.geometry("420x460")
        modal.resizable(False, False)
        modal.configure(bg=THEME["bg_card"])
        modal.transient(self)
        modal.grab_set()

        # Center relative to parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 460) // 2
        modal.geometry(f"+{x}+{y}")

        pad_frame = tk.Frame(modal, bg=THEME["bg_card"], padx=25, pady=25)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        # Trophy / Headline
        tk.Label(
            pad_frame,
            text="🏆 Test Results",
            font=(THEME["font_family"], 18, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_card"]
        ).pack(pady=(0, 5))

        # Performance summary rating
        if wpm >= 70 and accuracy >= 95:
            remark = "🔥 Pro Typist! Incredible speed & accuracy."
            remark_col = THEME["accent_green"]
        elif wpm >= 45 and accuracy >= 90:
            remark = "👍 Great Job! Fast and solid typing."
            remark_col = THEME["accent_cyan"]
        else:
            remark = "🌱 Keep practicing! Regular sprints build speed."
            remark_col = THEME["accent_yellow"]

        tk.Label(
            pad_frame,
            text=remark,
            font=(THEME["font_family"], 10),
            fg=remark_col,
            bg=THEME["bg_card"]
        ).pack(pady=(0, 20))

        # Metrics Table / Box
        stats_box = tk.Frame(pad_frame, bg=THEME["bg_input"], padx=18, pady=15)
        stats_box.pack(fill=tk.X, pady=(0, 25))

        metrics = [
            ("Words Per Minute (WPM)", f"{wpm} WPM", THEME["accent_cyan"]),
            ("Accuracy", f"{accuracy}%", THEME["accent_green"]),
            ("Time Taken", f"{duration} seconds", THEME["text_primary"]),
            ("Correct Keystrokes", str(correct_chars), THEME["accent_green"]),
            ("Errors Made", str(errors), THEME["accent_red"]),
            ("Difficulty Level", self.difficulty_var.get(), THEME["accent_purple"]),
        ]

        for i, (label, val, col) in enumerate(metrics):
            row = tk.Frame(stats_box, bg=THEME["bg_input"])
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row,
                text=label,
                font=(THEME["font_family"], 10),
                fg=THEME["text_secondary"],
                bg=THEME["bg_input"]
            ).pack(side=tk.LEFT)
            tk.Label(
                row,
                text=val,
                font=(THEME["font_family"], 10, "bold"),
                fg=col,
                bg=THEME["bg_input"]
            ).pack(side=tk.RIGHT)

        # Action Buttons
        btn_box = tk.Frame(pad_frame, bg=THEME["bg_card"])
        btn_box.pack(fill=tk.X)

        again_btn = tk.Button(
            btn_box,
            text="Take Another Test",
            font=(THEME["font_family"], 10, "bold"),
            bg=THEME["accent_blue"],
            fg=THEME["bg_dark"],
            activebackground=THEME["accent_cyan"],
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            command=lambda: [modal.destroy(), self.restart_test()]
        )
        again_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        close_btn = tk.Button(
            btn_box,
            text="Close",
            font=(THEME["font_family"], 10),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            activebackground=THEME["bg_input_focus"],
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            command=modal.destroy
        )
        close_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

    def restart_test(self):
        """Reset all metrics and pick a fresh test sentence."""
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        self.is_running = False
        self.test_completed = False
        self.start_time = None
        self.elapsed_seconds = 0
        self.total_errors = 0

        # Reset metric cards
        self.wpm_card.config(text="0")
        self.accuracy_card.config(text="100%")
        mode = self.mode_var.get()
        if "30s" in mode:
            self.time_card.config(text="30.0s")
        elif "60s" in mode:
            self.time_card.config(text="60.0s")
        else:
            self.time_card.config(text="0.0s")

        self.errors_card.config(text="0")

        # Reload sentence & reset input
        self._load_new_sentence()
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.delete("1.0", tk.END)
        self.input_entry.focus_set()

        self.status_msg.config(
            text="Start typing when you are ready. The timer will trigger automatically!",
            fg=THEME["accent_cyan"]
        )

    def show_history_window(self):
        """Open History and Statistics Dashboard modal window."""
        hist_win = tk.Toplevel(self)
        hist_win.title("Typing History & Performance Tracker")
        hist_win.geometry("680x520")
        hist_win.minsize(580, 420)
        hist_win.configure(bg=THEME["bg_dark"])
        hist_win.transient(self)

        container = tk.Frame(hist_win, bg=THEME["bg_dark"], padx=25, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        top_bar = tk.Frame(container, bg=THEME["bg_dark"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            top_bar,
            text="📊 Typing History & Analytics",
            font=(THEME["font_family"], 16, "bold"),
            fg=THEME["accent_cyan"],
            bg=THEME["bg_dark"]
        ).pack(side=tk.LEFT)

        # Summary statistics badges
        summary = self.history.get_summary()

        badges_frame = tk.Frame(container, bg=THEME["bg_dark"])
        badges_frame.pack(fill=tk.X, pady=(0, 15))
        badges_frame.columnconfigure((0, 1, 2, 3), weight=1)

        def add_badge(col, label, val, color):
            box = tk.Frame(badges_frame, bg=THEME["bg_card"], padx=10, pady=10)
            box.grid(row=0, column=col, padx=4, sticky="nsew")
            tk.Label(box, text=label, font=(THEME["font_family"], 8, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card"]).pack()
            tk.Label(box, text=str(val), font=(THEME["font_family"], 16, "bold"), fg=color, bg=THEME["bg_card"]).pack(pady=(2, 0))

        add_badge(0, "TOTAL TESTS", summary["total_tests"], THEME["accent_purple"])
        add_badge(1, "BEST WPM", f"{summary['best_wpm']}", THEME["accent_cyan"])
        add_badge(2, "AVG WPM", f"{summary['avg_wpm']}", THEME["accent_green"])
        add_badge(3, "AVG ACCURACY", f"{summary['avg_accuracy']}%", THEME["accent_yellow"])

        # History Treeview Table
        table_frame = tk.Frame(container, bg=THEME["bg_card"])
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        cols = ("Timestamp", "WPM", "Accuracy", "Difficulty", "Duration", "Errors")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="History.Treeview")

        tree.heading("Timestamp", text="Date & Time")
        tree.heading("WPM", text="WPM")
        tree.heading("Accuracy", text="Accuracy")
        tree.heading("Difficulty", text="Difficulty")
        tree.heading("Duration", text="Duration")
        tree.heading("Errors", text="Errors")

        tree.column("Timestamp", width=140, anchor="center")
        tree.column("WPM", width=70, anchor="center")
        tree.column("Accuracy", width=90, anchor="center")
        tree.column("Difficulty", width=90, anchor="center")
        tree.column("Duration", width=80, anchor="center")
        tree.column("Errors", width=70, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate rows
        for rec in self.history.records:
            tree.insert("", tk.END, values=(
                rec["timestamp"],
                f"{rec['wpm']} wpm",
                f"{rec['accuracy']}%",
                rec["difficulty"],
                f"{rec['duration']}s",
                rec["errors"]
            ))

        # Bottom Bar: Clear and Close buttons
        bottom_bar = tk.Frame(container, bg=THEME["bg_dark"])
        bottom_bar.pack(fill=tk.X)

        def clear_action():
            if messagebox.askyesno("Clear History", "Are you sure you want to clear all typing test history?"):
                self.history.clear()
                hist_win.destroy()
                self.show_history_window()

        clear_btn = tk.Button(
            bottom_bar,
            text="🗑 Clear History",
            font=(THEME["font_family"], 9),
            bg=THEME["bg_input"],
            fg=THEME["accent_red"],
            activebackground=THEME["bg_input_focus"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
            command=clear_action
        )
        clear_btn.pack(side=tk.LEFT)

        close_btn = tk.Button(
            bottom_bar,
            text="Close",
            font=(THEME["font_family"], 9, "bold"),
            bg=THEME["accent_blue"],
            fg=THEME["bg_dark"],
            activebackground=THEME["accent_cyan"],
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
            command=hist_win.destroy
        )
        close_btn.pack(side=tk.RIGHT)


if __name__ == "__main__":
    app = TypingSpeedTracker()
    app.mainloop()
