import customtkinter as ctk
import random
import time
import json
import os
from datetime import datetime, timedelta

# winsound is Windows-only; fail gracefully on other platforms
try:
    import winsound
    def beep(freq, dur):
        winsound.Beep(freq, dur)
except ImportError:
    def beep(freq, dur):
        pass  # Silent fallback on macOS / Linux

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

DEFAULT_DURATION = 60
DATA_FILE = "streak_data.json"

# ============================================================
# TEXT POOLS – keyed by difficulty / length category
# ============================================================

TEXT_POOLS = {
    "Short Sentence": [
        "Technology is the most effective way to change the world.",
        "Innovation is the ability to see change as an opportunity.",
        "Artificial Intelligence helps humans solve complex problems.",
        "Data science is transforming industries across the globe.",
        "Programming improves logical thinking and creativity.",
        "The quick brown fox jumps over the lazy dog.",
        "Every great developer was once a beginner.",
        "Code is like humor: when you have to explain it, it is bad.",
        "Simplicity is the soul of efficiency.",
        "First solve the problem, then write the code.",
    ],
    "Paragraph": [
        (
            "Technology is reshaping every aspect of modern life. From the way "
            "we communicate to the way we work, digital tools have become "
            "indispensable. Embracing change and learning new skills is the key "
            "to staying relevant in a rapidly evolving landscape. Those who "
            "adapt will thrive, while those who resist may be left behind."
        ),
        (
            "Open-source software has revolutionized the technology industry by "
            "allowing developers around the world to collaborate freely. Projects "
            "like Linux, Python, and Firefox demonstrate that community-driven "
            "development can produce software that rivals or surpasses proprietary "
            "alternatives. Contributing to open source is a rewarding experience "
            "that sharpens skills and builds professional networks."
        ),
        (
            "Cloud computing enables businesses to scale their infrastructure on "
            "demand without the need for expensive hardware. Services such as "
            "virtual machines, managed databases, and serverless functions allow "
            "teams to focus on building products rather than managing servers. "
            "The pay-as-you-go model makes cutting-edge technology accessible to "
            "startups and enterprises alike."
        ),
    ],
    "Long Text": [
        (
            "The history of computing stretches back centuries, from the abacus "
            "to Charles Babbage's Analytical Engine. In the twentieth century, "
            "pioneers like Alan Turing and John von Neumann laid the theoretical "
            "groundwork for modern computers. The invention of the transistor in "
            "1947 sparked a revolution that led to integrated circuits, "
            "microprocessors, and eventually the personal computer. Today, "
            "billions of interconnected devices form a global network that "
            "carries virtually all of human knowledge. Machine learning "
            "algorithms sift through enormous datasets to uncover patterns no "
            "human could detect alone. Quantum computing promises to solve "
            "problems that are currently intractable, from drug discovery to "
            "cryptography. As technology continues to advance at an exponential "
            "pace, society must grapple with questions of ethics, privacy, and "
            "equity. Ensuring that the benefits of innovation are shared broadly "
            "is one of the defining challenges of our time. Education systems "
            "must evolve to prepare students not just to use technology, but to "
            "understand and shape it. The future belongs to those who can think "
            "critically, collaborate effectively, and adapt to change with "
            "resilience and creativity."
        ),
        (
            "Software engineering is both an art and a science. Writing clean, "
            "maintainable code requires not only technical skill but also "
            "empathy for the developers who will read and modify it in the "
            "future. Version control systems like Git enable teams to work on "
            "the same codebase without stepping on each other's toes, while "
            "continuous integration pipelines catch bugs before they reach "
            "production. Test-driven development encourages programmers to think "
            "about edge cases early, resulting in more robust software. Code "
            "reviews foster knowledge sharing and help maintain consistent "
            "standards across a project. Documentation, often neglected, is "
            "crucial for onboarding new team members and preserving "
            "institutional knowledge. Agile methodologies break large projects "
            "into manageable sprints, allowing teams to deliver value "
            "incrementally and respond to changing requirements. DevOps "
            "practices blur the line between development and operations, "
            "promoting a culture of shared responsibility for reliability and "
            "performance. Ultimately, great software is not just about "
            "algorithms and data structures; it is about people working together "
            "to solve meaningful problems."
        ),
    ],
}

DURATION_OPTIONS = {
    "15 seconds": 15,
    "30 seconds": 30,
    "60 seconds": 60,
    "120 seconds": 120,
}

TEXT_LENGTH_OPTIONS = list(TEXT_POOLS.keys())


# ======================
# LOAD / SAVE DATA
# ======================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "daily_streak": 0,
        "last_practice_date": "",
        "improvement_streak": 0,
        "personal_best_streak": 0,
        "best_wpm": 0,
        "last_wpm": 0,
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


class TypingSpeedTest(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Typing Speed Test")
        self.geometry("750x680")

        self.current_sentence = ""
        self.start_time = None
        self.test_duration = DEFAULT_DURATION
        self.time_left = self.test_duration
        self.timer_running = False
        self.paused = False
        self.countdown = 3
        self.after_id = None

        self.data = load_data()

        # ── TITLE ──────────────────────────────────────────────
        self.title_label = ctk.CTkLabel(
            self,
            text="Typing Speed Test",
            font=("Helvetica", 30, "bold"),
        )
        self.title_label.pack(pady=15)

        # ── SETTINGS FRAME (duration + text length selectors) ─
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=(0, 10))

        # Duration selector
        self.duration_label = ctk.CTkLabel(
            self.settings_frame,
            text="Duration:",
            font=("Helvetica", 14),
        )
        self.duration_label.grid(row=0, column=0, padx=(10, 5), pady=5)

        self.duration_var = ctk.StringVar(value="60 seconds")
        self.duration_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            variable=self.duration_var,
            values=list(DURATION_OPTIONS.keys()),
            command=self.on_duration_change,
            width=140,
        )
        self.duration_menu.grid(row=0, column=1, padx=(0, 20), pady=5)

        # Text-length / difficulty selector
        self.text_length_label = ctk.CTkLabel(
            self.settings_frame,
            text="Text Length:",
            font=("Helvetica", 14),
        )
        self.text_length_label.grid(row=0, column=2, padx=(10, 5), pady=5)

        self.text_length_var = ctk.StringVar(value="Short Sentence")
        self.text_length_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            variable=self.text_length_var,
            values=TEXT_LENGTH_OPTIONS,
            width=160,
        )
        self.text_length_menu.grid(row=0, column=3, padx=(0, 10), pady=5)

        # ── TIMER ──────────────────────────────────────────────
        self.timer_label = ctk.CTkLabel(
            self,
            text=f"Time Remaining: {self.test_duration}s",
            font=("Helvetica", 18, "bold"),
        )
        self.timer_label.pack()

        # ── SENTENCE FRAME ─────────────────────────────────────
        self.sentence_frame = ctk.CTkFrame(self, width=680, height=120)
        self.sentence_frame.pack(pady=20)
        self.sentence_frame.pack_propagate(False)

        self.sentence_textbox = ctk.CTkTextbox(
            self.sentence_frame,
            wrap="word",
            font=("Helvetica", 20, "bold"),
            border_width=0,
            fg_color="transparent",
        )
        self.sentence_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.sentence_textbox.insert("1.0", "Press Enter or click Start to begin")
        self.sentence_textbox.configure(state="disabled")

        self.sentence_textbox.tag_config("correct", foreground="green")
        self.sentence_textbox.tag_config("incorrect", foreground="red")

        # ── INPUT BOX ──────────────────────────────────────────
        self.input_textbox = ctk.CTkTextbox(
            self,
            width=660,
            height=120,
            font=("Helvetica", 16),
        )
        self.input_textbox.pack(pady=10)
        self.input_textbox.configure(state="disabled")

        self.input_textbox.bind("<KeyRelease>", self.handle_typing)
        # Suppress newline insertion so Enter doesn't add a blank line
        self.input_textbox.bind("<Return>", lambda e: "break")

        # ── RESULT LABEL ───────────────────────────────────────
        self.result_label = ctk.CTkLabel(
            self, text="", font=("Helvetica", 18, "bold")
        )
        self.result_label.pack(pady=10)

        # ── STREAK LABEL ───────────────────────────────────────
        self.streak_label = ctk.CTkLabel(
            self, text=self.get_streak_text(), font=("Helvetica", 16)
        )
        self.streak_label.pack(pady=5)

        # ── BUTTON FRAME ───────────────────────────────────────
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Test",
            command=self.start_test,
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            state="disabled",
        )
        self.pause_button.grid(row=0, column=1, padx=10)

        # Bind Enter to start the test when not typing
        self.bind("<Return>", self.handle_enter)

    # ======================
    # SETTINGS CALLBACKS
    # ======================

    def on_duration_change(self, choice: str):
        """Update the displayed timer immediately when the user picks a new duration."""
        self.test_duration = DURATION_OPTIONS.get(choice, DEFAULT_DURATION)
        if not self.timer_running:
            self.timer_label.configure(text=f"Time Remaining: {self.test_duration}s")

    # ======================
    # HANDLE ENTER KEY
    # ======================

    def handle_enter(self, event=None):
        if self.start_button.cget("state") == "normal":
            self.start_test()

    # ======================
    # STREAK TEXT
    # ======================

    def get_streak_text(self):
        return (
            f"🔥 Daily Streak: {self.data.get('daily_streak', 0)} days\n"
            f"📈 Improvement Streak: {self.data.get('improvement_streak', 0)}\n"
            f"🏆 Personal Best Streak: {self.data.get('personal_best_streak', 0)}\n"
            f"⭐ Best WPM: {self.data.get('best_wpm', 0)}"
        )

    # ======================
    # START TEST
    # ======================

    def start_test(self):
        if self.timer_running:
            return

        # Read user-selected duration
        self.test_duration = DURATION_OPTIONS.get(
            self.duration_var.get(), DEFAULT_DURATION
        )
        self.timer_label.configure(text=f"Time Remaining: {self.test_duration}s")

        self.result_label.configure(text="")
        self.countdown = 3
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.pause_button.configure(text="Pause")

        # Disable settings while a test is in progress
        self.duration_menu.configure(state="disabled")
        self.text_length_menu.configure(state="disabled")

        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")
        self.sentence_textbox.configure(state="disabled")

        self.show_countdown()

    # ======================
    # COUNTDOWN
    # ======================

    def show_countdown(self):
        if self.countdown > 0:
            self.sentence_textbox.configure(state="normal")
            self.sentence_textbox.delete("1.0", "end")
            self.sentence_textbox.insert("1.0", f"Starting in {self.countdown}...")
            self.sentence_textbox.configure(state="disabled")
            self.countdown -= 1
            self.after_id = self.after(1000, self.show_countdown)
        else:
            self.sentence_textbox.configure(state="normal")
            self.sentence_textbox.delete("1.0", "end")
            self.sentence_textbox.insert("1.0", "GO!")
            self.sentence_textbox.configure(state="disabled")
            self.after(800, self.begin_test)

    # ======================
    # BEGIN TEST
    # ======================

    def begin_test(self):
        # Pick text from the selected category
        selected_length = self.text_length_var.get()
        pool = TEXT_POOLS.get(selected_length, TEXT_POOLS["Short Sentence"])
        self.current_sentence = random.choice(pool)

        self.update_sentence_display()

        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.focus()

        self.start_time = time.time()
        self.time_left = self.test_duration
        self.timer_running = True
        self.paused = False

        self.pause_button.configure(state="normal")

        self.update_timer()

    # ======================
    # TIMER (wall-clock based to avoid drift)
    # ======================

    def update_timer(self):
        if not self.timer_running or self.paused:
            return

        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.test_duration - elapsed)
        self.timer_label.configure(text=f"Time Remaining: {remaining}s")

        if remaining == 0:
            self.check_result()
        else:
            self.after_id = self.after(500, self.update_timer)

    # ======================
    # PAUSE
    # ======================

    def toggle_pause(self):
        if not self.timer_running:
            return

        self.paused = not self.paused
        if self.paused:
            self.pause_button.configure(text="Resume")
            self.pause_start = time.time()
            if self.after_id:
                self.after_cancel(self.after_id)
        else:
            self.pause_button.configure(text="Pause")
            # Shift start_time forward by the length of the pause
            pause_duration = time.time() - self.pause_start
            self.start_time += pause_duration
            self.update_timer()

    # ======================
    # HANDLE TYPING + SOUND
    # ======================

    def handle_typing(self, event):
        if not self.timer_running or self.paused:
            return

        typed = self.input_textbox.get("1.0", "end-1c")
        index = len(typed)

        if event.keysym == "BackSpace":
            beep(500, 40)
        elif event.keysym not in (
            "Return", "Shift_L", "Shift_R",
            "Control_L", "Control_R", "Alt_L", "Alt_R",
        ):
            # Per-character correct/incorrect sound from main branch
            if index <= len(self.current_sentence) and index > 0:
                expected = self.current_sentence[index - 1]
                if typed[-1] == expected:
                    beep(800, 30)
                else:
                    beep(300, 80)

        self.update_sentence_display()

        # Finish early if sentence completed
        if typed.strip() == self.current_sentence.strip():
            self.check_result()

    # ======================
    # UPDATE SENTENCE DISPLAY
    # ======================

    def update_sentence_display(self):
        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")

        typed_text = self.input_textbox.get("1.0", "end-1c")

        for i, char in enumerate(self.current_sentence):
            tag = ""
            if i < len(typed_text):
                tag = "correct" if typed_text[i] == char else "incorrect"
            self.sentence_textbox.insert(f"1.{i}", char, tag if tag else ())

        self.sentence_textbox.configure(state="disabled")

    # ======================
    # UPDATE STREAKS
    # ======================

    def update_streaks(self, wpm):
        today = datetime.now().date()
        last_date_str = self.data.get("last_practice_date", "")

        if last_date_str:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            if today == last_date + timedelta(days=1):
                self.data["daily_streak"] += 1
            elif today != last_date:
                self.data["daily_streak"] = 1
        else:
            self.data["daily_streak"] = 1

        self.data["last_practice_date"] = today.strftime("%Y-%m-%d")

        if wpm > self.data.get("last_wpm", 0):
            self.data["improvement_streak"] = (
                self.data.get("improvement_streak", 0) + 1
            )
        else:
            self.data["improvement_streak"] = 0

        self.data["last_wpm"] = wpm

        if wpm > self.data.get("best_wpm", 0):
            self.data["best_wpm"] = wpm
            self.data["personal_best_streak"] = (
                self.data.get("personal_best_streak", 0) + 1
            )

        save_data(self.data)

    # ======================
    # RESULT
    # ======================

    def check_result(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        if not self.timer_running:
            return  # Guard against double-fire

        self.timer_running = False
        beep(1200, 300)

        typed_text = self.input_textbox.get("1.0", "end-1c")
        elapsed_time = time.time() - self.start_time

        correct_chars = sum(
            1
            for i, char in enumerate(typed_text)
            if i < len(self.current_sentence) and self.current_sentence[i] == char
        )

        wpm = (correct_chars / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0

        self.update_streaks(wpm)

        self.result_label.configure(text=f"Typing Speed: {wpm:.2f} WPM")
        self.streak_label.configure(text=self.get_streak_text())

        self.input_textbox.configure(state="disabled")
        self.pause_button.configure(state="disabled")
        self.start_button.configure(state="normal")

        # Re-enable settings selectors
        self.duration_menu.configure(state="normal")
        self.text_length_menu.configure(state="normal")

        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")
        self.sentence_textbox.insert("1.0", "Press Enter or click Start to begin")
        self.sentence_textbox.configure(state="disabled")


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()
