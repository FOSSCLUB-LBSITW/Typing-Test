import customtkinter as ctk
import random
import time


# --- Theme Configuration ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


SENTENCES = [
    "Technology is the most effective way to change the world",
    "Innovation is the ability to see change as an opportunity -not a threat",
    "Artificial Intelligence is not a threat to creativity; it's a catalyst for innovation.",
    "Data is the canvas, and AI is the brush that paints the picture of insights.",
    "Artificial Intelligence: where innovation meets computation in the pursuit of a smarter tomorrow."
]


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


        # --- UI LAYOUT ---
        self.title_label = ctk.CTkLabel(self, text="Typing Speed Test", font=("Helvetica", 28, "bold"))
        self.title_label.pack(pady=20)


        self.timer_label = ctk.CTkLabel(self, text="Time Remaining: 60s", font=("Helvetica", 16, "bold"), text_color="#3B8ED0")
        self.timer_label.pack(pady=5)


        self.sentence_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sentence_frame.pack(pady=20, padx=40)


        self.sentence_label = ctk.CTkLabel(self.sentence_frame, text="Press 'Start Test' to begin", font=("Helvetica", 18),
                                           wraplength=600, justify="center", text_color="gray")
        self.sentence_label.pack()


        self.input_textbox = ctk.CTkTextbox(self, font=("Helvetica", 16), width=550, height=100, border_width=2)
        self.input_textbox.pack(pady=10)
        self.input_textbox.bind("<KeyRelease>", self.handle_input)
       
        # Diagnostic Feedback Label
        self.feedback_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12, "bold"))
        self.feedback_label.pack()


        # Button Container
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=20)


        self.start_button = ctk.CTkButton(self.button_frame, text="Start Test", font=("Helvetica", 14, "bold"),
                                          command=self.start_test, height=40)
        self.start_button.grid(row=0, column=0, padx=10)


        self.result_button = ctk.CTkButton(self.button_frame, text="Display Results", font=("Helvetica", 14, "bold"),
                                           command=self.check_result, state="disabled", height=40, fg_color="gray")
        self.result_button.grid(row=0, column=1, padx=10)


        self.result_label = ctk.CTkLabel(self, text="", font=("Helvetica", 18, "italic"))
        self.result_label.pack(pady=10)


        self.available_sentences = SENTENCES.copy()
        random.shuffle(self.available_sentences)
    def start_test(self):
        self.result_label.configure(text="")
        self.feedback_label.configure(text="")
        self.current_sentence = random.choice(SENTENCES)
        self.sentence_label.configure(text=self.current_sentence, text_color="white")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.configure(state="normal")
        self.input_textbox.focus()
       
        if not self.available_sentences:
            self.available_sentences = SENTENCES.copy()
            random.shuffle(self.available_sentences)
            self.current_sentence = self.available_sentences.pop()
       
        self.sentence_label.configure(text=self.current_sentence, text_color="white")
        # ... rest of start_test code ...
        self.time_left = 60
        self.timer_running = True
        self.timer_label.configure(text="Time Remaining: 60s", text_color="#3B8ED0")
       
        self.start_time = time.time()
        self.start_button.configure(state="disabled")
        self.result_button.configure(state="normal", fg_color="#3B8ED0")
       
        self.update_timer()


    def update_timer(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.timer_label.configure(text=f"Time Remaining: {self.time_left}s")
            if self.time_left <= 10:
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
        elapsed_time = time.time() - self.start_time
        typed_text = self.input_textbox.get("1.0", "end-1c")
       
        # Calculate WPM
        chars_typed = len(typed_text)
        wpm = (chars_typed / 5) / (elapsed_time / 60) if elapsed_time > 0 else 0
       
        self.result_label.configure(text=f"Test Finished! Speed: {wpm:.2f} WPM", text_color="#3B8ED0")
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="normal")
        self.result_button.configure(state="disabled", fg_color="gray")
        self.start_time = None


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()

