import customtkinter as ctk
import random
import time
import threading
import urllib.request
import json

# --- Theme Configuration ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Fallback sentences used when the API is unreachable
FALLBACK_SENTENCES = [
    "Technology is the most effective way to change the world.",
    "Innovation is the ability to see change as an opportunity, not a threat.",
    "Artificial Intelligence is not a threat to creativity; it is a catalyst for innovation.",
    "Data is the canvas, and AI is the brush that paints the picture of insights.",
    "Artificial Intelligence: where innovation meets computation in the pursuit of a smarter tomorrow."
]

QUOTE_API_URL = "http://api.quotable.io/random"

# Predefined color themes: accent, bg, text_on_quote, button_label
THEMES = {
    "Ocean":    {"accent": "#3B8ED0", "bg": "#1a1a2e", "accent_hover": "#2775b3"},
    "Sunset":   {"accent": "#E05C5C", "bg": "#2b1a1a", "accent_hover": "#b84444"},
    "Forest":   {"accent": "#4CAF50", "bg": "#1a2b1a", "accent_hover": "#388E3C"},
    "Candy":    {"accent": "#D45FBF", "bg": "#2b1a2b", "accent_hover": "#a8429b"},
    "Midnight": {"accent": "#A78BFA", "bg": "#0f0f1a", "accent_hover": "#7c5cbf"},
}

class TypingSpeedTest(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Typing Speed Test Pro")
        self.geometry("700x550")
        self.resizable(False, False)

        self.start_time = None
        self.current_sentence = ""
        self.time_left = 60
        self.timer_running = False
        self.scores = []
        self.mode = "60s"  # "60s" or "15s"
        self.current_theme = "Ocean"  # default theme

        # --- UI LAYOUT ---
        self.title_label = ctk.CTkLabel(self, text="Typing Speed Test", font=("Helvetica", 28, "bold"))
        self.title_label.pack(pady=20)

        self.timer_label = ctk.CTkLabel(self, text="Time Remaining: 60s", font=("Helvetica", 16, "bold"), text_color="#3B8ED0")
        self.timer_label.pack(pady=5)

        self.sentence_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sentence_frame.pack(pady=20, padx=40)

        self.sentence_label = ctk.CTkLabel(
            self.sentence_frame,
            text="Press 'Start Test' to begin",
            font=("Helvetica", 18),
            wraplength=600,
            justify="center",
            text_color="gray"
        )
        self.sentence_label.pack()

        self.input_textbox = ctk.CTkTextbox(self, font=("Helvetica", 16), width=550, height=100, border_width=2)
        self.input_textbox.pack(pady=10)
        self.input_textbox.bind("<KeyRelease>", self.handle_input)

        # Diagnostic Feedback Label
        self.feedback_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12, "bold"))
        self.feedback_label.pack()

        # Mode Selector
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.pack(pady=(10, 0))

        self.btn_60s = ctk.CTkButton(
            self.mode_frame,
            text="⏱ 60s Mode",
            font=("Helvetica", 13, "bold"),
            command=lambda: self.set_mode("60s"),
            height=34,
            width=130,
            fg_color="#3B8ED0",
            hover_color="#2775b3"
        )
        self.btn_60s.grid(row=0, column=0, padx=6)

        self.btn_15s = ctk.CTkButton(
            self.mode_frame,
            text="⚡ 15s Mode",
            font=("Helvetica", 13, "bold"),
            command=lambda: self.set_mode("15s"),
            height=34,
            width=130,
            fg_color="gray",
            hover_color="#555555"
        )
        self.btn_15s.grid(row=0, column=1, padx=6)

        # Button Container
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Test",
            font=("Helvetica", 14, "bold"),
            command=self.start_test,
            height=40
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.result_button = ctk.CTkButton(
            self.button_frame,
            text="Display Results",
            font=("Helvetica", 14, "bold"),
            command=self.check_result,
            state="disabled",
            height=40,
            fg_color="gray"
        )
        self.result_button.grid(row=0, column=1, padx=10)

        self.scoreboard_button = ctk.CTkButton(
            self.button_frame,
            text="🏆 Scoreboard",
            font=("Helvetica", 14, "bold"),
            command=self.show_scoreboard,
            height=40,
            fg_color="#5A5A8A",
            hover_color="#3D3D6B"
        )
        self.scoreboard_button.grid(row=0, column=2, padx=10)

        self.result_label = ctk.CTkLabel(self, text="", font=("Helvetica", 18, "italic"))
        self.result_label.pack(pady=10)

        # Theme Selector
        self.theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.theme_frame.pack(pady=(0, 6))
        ctk.CTkLabel(self.theme_frame, text="Theme:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=(0, 6))
        self.theme_buttons = {}
        for col, (name, t) in enumerate(THEMES.items(), start=1):
            btn = ctk.CTkButton(
                self.theme_frame,
                text=name,
                font=("Helvetica", 11, "bold"),
                command=lambda n=name: self.apply_theme(n),
                height=28,
                width=80,
                fg_color=t["accent"],
                hover_color=t["accent_hover"],
                corner_radius=14
            )
            btn.grid(row=0, column=col, padx=4)
            self.theme_buttons[name] = btn

        # Fallback pool (shuffled), used only when API is unavailable
        self.fallback_pool = FALLBACK_SENTENCES.copy()
        random.shuffle(self.fallback_pool)

        # Apply default theme
        self.apply_theme("Ocean")

    def apply_theme(self, name):
        """Apply a named colour theme to all themed widgets."""
        self.current_theme = name
        t = THEMES[name]
        accent = t["accent"]
        hover  = t["accent_hover"]
        bg     = t["bg"]

        self.configure(fg_color=bg)
        self.timer_label.configure(text_color=accent)
        self.result_label.configure(text_color=accent)
        self.start_button.configure(fg_color=accent, hover_color=hover)
        self.scoreboard_button.configure(fg_color="#5A5A8A", hover_color="#3D3D6B")
        # Mode buttons: re-highlight active one
        self.btn_60s.configure(
            fg_color=accent if self.mode == "60s" else "gray",
            hover_color=hover if self.mode == "60s" else "#555555"
        )
        self.btn_15s.configure(
            fg_color=accent if self.mode == "15s" else "gray",
            hover_color=hover if self.mode == "15s" else "#555555"
        )

    def set_mode(self, mode):
        """Switch between '60s' and '15s' modes (only when not mid-test)."""
        if self.timer_running:
            return
        self.mode = mode
        t = THEMES[self.current_theme]
        accent, hover = t["accent"], t["accent_hover"]
        duration = 60 if mode == "60s" else 15
        self.timer_label.configure(text=f"Time Remaining: {duration}s", text_color=accent)
        self.btn_60s.configure(fg_color=accent if mode == "60s" else "gray",
                               hover_color=hover if mode == "60s" else "#555555")
        self.btn_15s.configure(fg_color=accent if mode == "15s" else "gray",
                               hover_color=hover if mode == "15s" else "#555555")

    def fetch_quote(self):
        """Fetch a random quote from the API. Returns the quote string or None on failure."""
        try:
            with urllib.request.urlopen(QUOTE_API_URL, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get("content", "").strip()
        except Exception:
            return None

    def start_test(self):
        # --- Reset everything for a new test ---
        self.result_label.configure(text="")
        self.feedback_label.configure(text="")

        # Clear input field and disable it while loading
        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.configure(state="disabled")

        # Show loading state
        self.sentence_label.configure(text="Loading quote...", text_color="gray")
        self.start_button.configure(state="disabled")
        self.result_button.configure(state="disabled", fg_color="gray")

        # Fetch the quote in a background thread to keep UI responsive
        threading.Thread(target=self._load_quote_and_begin, daemon=True).start()

    def _load_quote_and_begin(self):
        """Background thread: fetch quote, then schedule UI update on main thread."""
        quote = self.fetch_quote()
        if not quote:
            # Fallback to built-in sentences
            if not self.fallback_pool:
                self.fallback_pool = FALLBACK_SENTENCES.copy()
                random.shuffle(self.fallback_pool)
            quote = self.fallback_pool.pop()
        # Schedule the rest of the setup back on the main thread
        self.after(0, lambda q=quote: self._begin_test(q))

    def _begin_test(self, sentence):
        """Called on the main thread once the quote is ready."""
        self.current_sentence = sentence
        self.sentence_label.configure(text=self.current_sentence, text_color="white")

        # Re-enable input and focus
        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.focus()
        self.input_textbox.update()

        # Reset timer based on selected mode
        duration = 60 if self.mode == "60s" else 15
        self.time_left = duration
        self.timer_running = True
        accent = THEMES[self.current_theme]["accent"]
        self.timer_label.configure(text=f"Time Remaining: {duration}s", text_color=accent)
        self.start_time = time.time()

        # Update buttons
        accent = THEMES[self.current_theme]["accent"]
        self.result_button.configure(state="normal", fg_color=accent)

        # Start timer
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.timer_label.configure(text=f"Time Remaining: {self.time_left}s")
            red_zone = 5 if self.mode == "15s" else 10
            if self.time_left <= red_zone:
                self.timer_label.configure(text_color="#FF4C4C")
            self.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.check_result()

    def handle_input(self, event):
        if not self.current_sentence: return
        self.validate_typing()

        # Auto-finish if sentence is complete
        typed_text = self.input_textbox.get("1.0", "end-1c")
        if typed_text.strip() == self.current_sentence:
            self.check_result()

    def validate_typing(self):
        typed_text = self.input_textbox.get("1.0", "end-1c")
        has_case_error = False
        has_char_error = False

        for i, ch in enumerate(typed_text):
            if i < len(self.current_sentence):
                if ch != self.current_sentence[i]:
                    if ch.lower() == self.current_sentence[i].lower():
                        has_case_error = True
                    else:
                        has_char_error = True

        if has_char_error:
            self.feedback_label.configure(text="❌ Character Error", text_color="#FF4C4C")
        elif has_case_error:
            self.feedback_label.configure(text="⚠ Case Mismatch!", text_color="#FFCC00")
        else:
            self.feedback_label.configure(text="✓ Typing...", text_color="#4CAF50")

    def check_result(self, event=None):
        if not self.start_time: return

        self.timer_running = False
        self.feedback_label.configure(text="")  # Clear typing feedback
        elapsed_time = time.time() - self.start_time
        typed_text = self.input_textbox.get("1.0", "end-1c")

        # Calculate WPM
        chars_typed = len(typed_text)
        wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0

        accent = THEMES[self.current_theme]["accent"]
        self.result_label.configure(text=f"Test Finished! Speed: {wpm:.2f} WPM", text_color=accent)
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="normal")
        self.result_button.configure(state="disabled", fg_color="gray")
        self.start_time = None

        # Update in-memory scoreboard (top 5)
        self.scores.append(round(wpm, 2))
        self.scores.sort(reverse=True)
        self.scores = self.scores[:5]

    def show_scoreboard(self):
        win = ctk.CTkToplevel(self)
        win.title("Scoreboard")
        win.geometry("300x320")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="🏆 Top 5 Scores", font=("Helvetica", 20, "bold")).pack(pady=16)

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        if not self.scores:
            ctk.CTkLabel(win, text="No scores yet.\nComplete a test to see results!",
                         font=("Helvetica", 14), text_color="gray", justify="center").pack(pady=20)
        else:
            for i, score in enumerate(self.scores):
                ctk.CTkLabel(
                    win,
                    text=f"{medals[i]}  {score:.2f} WPM",
                    font=("Helvetica", 16)
                ).pack(pady=6)

        ctk.CTkButton(win, text="Close", command=win.destroy, height=36).pack(pady=16)

if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()