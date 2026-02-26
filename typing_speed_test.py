import customtkinter as ctk
import random
import time
import threading
import urllib.request
import json

# --- Theme Configuration ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

FALLBACK_SENTENCES = [
    "Technology is the most effective way to change the world.",
    "Innovation is the ability to see change as an opportunity, not a threat.",
    "Artificial Intelligence is not a threat to creativity; it is a catalyst for innovation.",
    "Data is the canvas, and AI is the brush that paints the picture of insights.",
    "Artificial Intelligence: where innovation meets computation in the pursuit of a smarter tomorrow."
]

QUOTE_API_URL = "http://api.quotable.io/random"

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
        self.paused = False
        self.pause_start = None
        self.total_paused_time = 0
        self.scores = []
        self.mode = "60s"
        self.current_theme = "Ocean"

        # --- UI ---
        self.title_label = ctk.CTkLabel(self, text="Typing Speed Test",
                                        font=("Helvetica", 28, "bold"))
        self.title_label.pack(pady=20)

        self.timer_label = ctk.CTkLabel(self,
                                        text="Time Remaining: 60s",
                                        font=("Helvetica", 16, "bold"),
                                        text_color="#3B8ED0")
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

        self.input_textbox = ctk.CTkTextbox(self,
                                            font=("Helvetica", 16),
                                            width=550,
                                            height=100,
                                            border_width=2)
        self.input_textbox.pack(pady=10)
        self.input_textbox.bind("<KeyRelease>", self.handle_input)

        self.feedback_label = ctk.CTkLabel(self,
                                           text="",
                                           font=("Helvetica", 12, "bold"))
        self.feedback_label.pack()

        # Buttons
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

        # 🔥 NEW PAUSE BUTTON
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

        self.result_label = ctk.CTkLabel(self,
                                         text="",
                                         font=("Helvetica", 18, "italic"))
        self.result_label.pack(pady=10)

    # ==============================
    # START TEST
    # ==============================
    def start_test(self):
        self.result_label.configure(text="")
        self.feedback_label.configure(text="")
        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")

        self.current_sentence = random.choice(FALLBACK_SENTENCES)
        self.sentence_label.configure(text=self.current_sentence, text_color="white")

        duration = 60 if self.mode == "60s" else 15
        self.time_left = duration
        self.timer_running = True
        self.paused = False
        self.total_paused_time = 0

        self.start_time = time.time()
        self.timer_label.configure(text=f"Time Remaining: {duration}s")
        self.pause_button.configure(state="normal", text="⏸ Pause")
        self.start_button.configure(state="disabled")
        self.result_button.configure(state="normal")

        self.update_timer()

    # ==============================
    # TIMER
    # ==============================
    def update_timer(self):
        if not self.timer_running:
            return

        if self.paused:
            self.after(1000, self.update_timer)
            return

        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.configure(text=f"Time Remaining: {self.time_left}s")
            self.after(1000, self.update_timer)
        else:
            self.check_result()

    # ==============================
    # PAUSE / RESUME
    # ==============================
    def toggle_pause(self):
        if not self.timer_running:
            return

        if not self.paused:
            # PAUSE
            self.paused = True
            self.pause_start = time.time()
            self.input_textbox.configure(state="disabled")
            self.pause_button.configure(text="▶ Resume")
            self.timer_label.configure(text=f"Paused at {self.time_left}s",
                                       text_color="#FFA500")
        else:
            # RESUME
            self.paused = False
            pause_duration = time.time() - self.pause_start
            self.total_paused_time += pause_duration
            self.input_textbox.configure(state="normal")
            self.input_textbox.focus()
            self.pause_button.configure(text="⏸ Pause")
            self.timer_label.configure(text=f"Time Remaining: {self.time_left}s",
                                       text_color="#3B8ED0")

    # ==============================
    # HANDLE INPUT
    # ==============================
    def handle_input(self, event):
        if not self.current_sentence or self.paused:
            return

        typed_text = self.input_textbox.get("1.0", "end-1c")
        if typed_text.strip() == self.current_sentence:
            self.check_result()

    # ==============================
    # RESULT
    # ==============================
    def check_result(self, event=None):
        if not self.start_time:
            return

        self.timer_running = False
        self.pause_button.configure(state="disabled")

        elapsed_time = (time.time() - self.start_time) - self.total_paused_time
        typed_text = self.input_textbox.get("1.0", "end-1c")

        chars_typed = len(typed_text)
        wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0

        self.result_label.configure(
            text=f"Test Finished! Speed: {wpm:.2f} WPM"
        )

        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="normal")
        self.start_time = None

if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()