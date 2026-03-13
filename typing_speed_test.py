import customtkinter as ctk
import random
import time
import winsound
import json
import os
from datetime import datetime, timedelta

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

TEST_DURATION = 60
DATA_FILE = "streak_data.json"

SENTENCES = [
    "Technology is the most effective way to change the world.",
    "Innovation is the ability to see change as an opportunity.",
    "Artificial Intelligence helps humans solve complex problems.",
    "Data science is transforming industries across the globe.",
    "Programming improves logical thinking and creativity."
]


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
        "last_wpm": 0
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


class TypingSpeedTest(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Typing Speed Test")
        self.geometry("720x580")

        self.current_sentence = ""
        self.start_time = None
        self.time_left = TEST_DURATION
        self.timer_running = False
        self.paused = False
        self.countdown = 3
        self.after_id = None

        self.data = load_data()

        # TITLE
        self.title_label = ctk.CTkLabel(
            self,
            text="Typing Speed Test",
            font=("Helvetica", 30, "bold")
        )
        self.title_label.pack(pady=15)

        # TIMER
        self.timer_label = ctk.CTkLabel(
            self,
            text=f"Time Remaining: {TEST_DURATION}s",
            font=("Helvetica", 18, "bold")
        )
        self.timer_label.pack()

        # SENTENCE FRAME
        self.sentence_frame = ctk.CTkFrame(self, width=620, height=100)
        self.sentence_frame.pack(pady=20)
        self.sentence_frame.pack_propagate(False)

        # Use a CTkTextbox for the sentence to allow highlighting
        self.sentence_textbox = ctk.CTkTextbox(
            self.sentence_frame,
            wrap="word",
            font=("Helvetica", 20, "bold"),
            border_width=0,
            fg_color="transparent"
        )
        self.sentence_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.sentence_textbox.insert("1.0", "Press Enter or click Start to begin")
        self.sentence_textbox.configure(state="disabled")

        # Configure tags for correct and incorrect characters
        self.sentence_textbox.tag_config("correct", foreground="green")
        self.sentence_textbox.tag_config("incorrect", foreground="red")

        # INPUT BOX
        self.input_textbox = ctk.CTkTextbox(
            self,
            width=600,
            height=120,
            font=("Helvetica", 16)
        )
        self.input_textbox.pack(pady=10)
        self.input_textbox.configure(state="disabled")

        self.input_textbox.bind("<KeyRelease>", self.handle_typing)

        # RESULT LABEL
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=("Helvetica", 18, "bold")
        )
        self.result_label.pack(pady=10)

        # STREAK LABEL
        self.streak_label = ctk.CTkLabel(
            self,
            text=self.get_streak_text(),
            font=("Helvetica", 16)
        )
        self.streak_label.pack(pady=5)

        # BUTTON FRAME
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Test",
            command=self.start_test
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            state="disabled"
        )
        self.pause_button.grid(row=0, column=1, padx=10)

        # Bind the Enter key to start the test
        self.bind("<Return>", self.handle_enter_key)

    # ======================
    # HANDLE ENTER KEY
    # ======================

    def handle_enter_key(self, event):
        # Start the test if it's not already running
        if not self.timer_running:
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

        self.result_label.configure(text="")
        self.countdown = 3
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="disabled")

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
        self.current_sentence = random.choice(SENTENCES)
        self.update_sentence_display()  # Initial display of the sentence

        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.focus()

        self.start_time = time.time()
        self.time_left = TEST_DURATION
        self.timer_running = True
        self.paused = False

        self.pause_button.configure(state="normal")

        self.update_timer()

    # ======================
    # TIMER
    # ======================

    def update_timer(self):
        if not self.timer_running:
            return

        if not self.paused:
            if self.time_left > 0:
                self.timer_label.configure(
                    text=f"Time Remaining: {self.time_left}s"
                )
                self.time_left -= 1
                self.after_id = self.after(1000, self.update_timer)
            else:
                self.check_result()

    # ======================
    # PAUSE
    # ======================

    def toggle_pause(self):
        if not self.timer_running:
            return

        self.paused = not self.paused
        if self.paused:
            self.pause_button.configure(text="Resume")
            if self.after_id:
                self.after_cancel(self.after_id)
        else:
            self.pause_button.configure(text="Pause")
            # Recalculate start_time to account for the pause
            self.start_time = time.time() - (TEST_DURATION - self.time_left)
            self.update_timer()

    # ======================
    # HANDLE TYPING
    # ======================

    def handle_typing(self, event):
        if not self.timer_running or self.paused:
            return

        # Play sound for feedback
        if event.keysym == "BackSpace":
            winsound.Beep(500, 40)
        else:
            winsound.Beep(800, 30)

        self.update_sentence_display()

        typed_text = self.input_textbox.get("1.0", "end-1c")
        # Automatically end test when the sentence is typed correctly
        if typed_text == self.current_sentence:
            self.check_result()

    # ======================
    # UPDATE SENTENCE DISPLAY
    # ======================

    def update_sentence_display(self):
        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")

        typed_text = self.input_textbox.get("1.0", "end-1c")

        for i, char in enumerate(self.current_sentence):
            if i < len(typed_text):
                if typed_text[i] == char:
                    self.sentence_textbox.insert(f"1.{i}", char, "correct")
                else:
                    self.sentence_textbox.insert(f"1.{i}", char, "incorrect")
            else:
                # Insert remaining characters without a tag
                self.sentence_textbox.insert(f"1.{i}", char)

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
            self.data["improvement_streak"] = self.data.get("improvement_streak", 0) + 1
        else:
            self.data["improvement_streak"] = 0

        self.data["last_wpm"] = wpm

        if wpm > self.data.get("best_wpm", 0):
            self.data["best_wpm"] = wpm
            self.data["personal_best_streak"] = self.data.get("personal_best_streak", 0) + 1

        save_data(self.data)

    # ======================
    # RESULT
    # ======================

    def check_result(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        if not self.timer_running:
            return

        self.timer_running = False
        winsound.Beep(1200, 300)

        typed_text = self.input_textbox.get("1.0", "end-1c")
        elapsed_time = time.time() - self.start_time

        # Calculate WPM based on correctly typed characters
        correct_chars = 0
        for i, char in enumerate(typed_text):
            if i < len(self.current_sentence) and self.current_sentence[i] == char:
                correct_chars += 1

        wpm = (correct_chars / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0

        self.update_streaks(wpm)

        self.result_label.configure(text=f"Typing Speed: {wpm:.2f} WPM")
        self.streak_label.configure(text=self.get_streak_text())

        self.input_textbox.configure(state="disabled")
        self.pause_button.configure(state="disabled")
        self.start_button.configure(state="normal")

        # Reset the sentence display for the next round
        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")
        self.sentence_textbox.insert("1.0", "Press Enter or click Start to begin")
        self.sentence_textbox.configure(state="disabled")


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()
