import customtkinter as ctk
import random
import time

# --- Theme Configuration ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

TEST_DURATION = 60

SENTENCES = [
    "Technology is the most effective way to change the world.",
    "Innovation is the ability to see change as an opportunity, not a threat.",
    "Artificial Intelligence is not a threat to creativity; it is a catalyst for innovation.",
    "Data is the canvas, and AI is the brush that paints the picture of insights.",
    "Artificial Intelligence: where innovation meets computation in the pursuit of a smarter tomorrow."
]

class TypingSpeedTest(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("Typing Speed Test Pro")
        self.geometry("700x700")  # Increased height for history
        self.resizable(False, False)

        # --- Variables ---
        self.start_time = None
        self.current_sentence = ""
        self.time_left = TEST_DURATION
        self.timer_running = False
        self.total_paused_time = 0
        self.paused = False
        self.pause_start = None
        self.timer_id = None
        self.history = []  # <-- WPM history

        # --- UI Elements ---
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

        self.feedback_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12, "bold"))
        self.feedback_label.pack()

        # --- Buttons ---
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

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="⏸ Pause",
            font=("Helvetica", 14, "bold"),
            command=self.toggle_pause,
            state="disabled",
            height=40,
            fg_color="#FFA500",
            hover_color="#cc8400"
        )
        self.pause_button.grid(row=0, column=2, padx=10)

        self.result_label = ctk.CTkLabel(self, text="", font=("Helvetica", 18, "italic"))
        self.result_label.pack(pady=10)

        # --- WPM History Panel ---
        self.history_title = ctk.CTkLabel(self, text="WPM History", font=("Helvetica", 18, "bold"))
        self.history_title.pack(pady=(10,5))

        self.history_box = ctk.CTkTextbox(self, width=400, height=120, font=("Helvetica", 14))
        self.history_box.pack()
        self.history_box.configure(state="disabled")

    # =========================
    # START TEST
    # =========================
    def start_test(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)

        self.timer_running = True
        self.paused = False
        self.total_paused_time = 0
        self.start_time = time.time()
        self.time_left = TEST_DURATION

        self.current_sentence = random.choice(SENTENCES)
        self.sentence_label.configure(text=self.current_sentence, text_color="white")
        # make sure the textbox is writable and empty for a fresh start
        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.focus()
        self.feedback_label.configure(text="")
        self.result_label.configure(text="")

        self.start_button.configure(state="disabled")
        self.result_button.configure(state="normal", fg_color="#3B8ED0")
        self.pause_button.configure(state="normal", text="⏸ Pause")

        self.update_timer()

    # =========================
    # TIMER
    # =========================
    def update_timer(self):
        if self.timer_running and not self.paused:
            if self.time_left > 0:
                self.time_left -= 1
                self.timer_label.configure(text=f"Time Remaining: {self.time_left}s")
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.check_result(timeout=True)

    # =========================
    # PAUSE / RESUME
    # =========================
    def toggle_pause(self):
        if not self.timer_running:
            return
        if not self.paused:
            # Pause
            self.paused = True
            self.pause_start = time.time()
            self.input_textbox.configure(state="disabled")
            self.pause_button.configure(text="▶ Resume")
            self.timer_label.configure(text=f"Paused at {self.time_left}s", text_color="#FFA500")
        else:
            # Resume
            self.paused = False
            self.total_paused_time += time.time() - self.pause_start
            self.input_textbox.configure(state="normal")
            self.input_textbox.focus()
            self.pause_button.configure(text="⏸ Pause")
            self.timer_label.configure(text=f"Time Remaining: {self.time_left}s", text_color="#3B8ED0")
            self.update_timer()

    # =========================
    # HANDLE INPUT
    # =========================
    def handle_input(self, event):
        if not self.current_sentence or self.paused:
            return
        typed_text = self.input_textbox.get("1.0", "end-1c")
        if typed_text.strip() == self.current_sentence:
            self.check_result()

    # =========================
    # CHECK RESULT
    # =========================
    def check_result(self, event=None, timeout=False):
        if not self.start_time:
            return

        self.timer_running = False
        self.pause_button.configure(state="disabled")

        elapsed_time = TEST_DURATION if timeout else (time.time() - self.start_time - self.total_paused_time)

        typed_text = self.input_textbox.get("1.0", "end-1c").strip()
        chars_typed = len(typed_text)
        wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0

        if typed_text == self.current_sentence:
            self.result_label.configure(text=f"Well done! Your typing speed: {wpm:.2f} WPM", text_color="#3B8ED0")
        else:
            self.result_label.configure(text=f"Test Finished! Your typing speed: {wpm:.2f} WPM", text_color="#3B8ED0")

        # Save to history
        self.history.append(round(wpm, 2))
        self.update_history_panel()

        # Disable input
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="normal")
        self.result_button.configure(state="disabled", fg_color="gray")

    # =========================
    # UPDATE HISTORY PANEL
    # =========================
    def update_history_panel(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        for i, score in enumerate(self.history, start=1):
            self.history_box.insert("end", f"Attempt {i}: {score:.2f} WPM\n")
        self.history_box.configure(state="disabled")


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()