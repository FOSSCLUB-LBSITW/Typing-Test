import customtkinter as ctk
import random
import time
import winsound

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

TEST_DURATION = 60

SENTENCES = [
    "Technology is the most effective way to change the world.",
    "Innovation is the ability to see change as an opportunity.",
    "Artificial Intelligence helps humans solve complex problems.",
    "Data science is transforming industries across the globe.",
    "Programming improves logical thinking and creativity."
]


class TypingSpeedTest(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Typing Speed Test")
        self.geometry("700x520")

        self.current_sentence = ""
        self.start_time = None
        self.time_left = TEST_DURATION
        self.timer_running = False
        self.paused = False
        self.countdown = 3

        # TITLE
        self.title_label = ctk.CTkLabel(
            self,
            text="Typing Speed Test",
            font=("Helvetica", 30, "bold")
        )
        self.title_label.pack(pady=20)

        # TIMER
        self.timer_label = ctk.CTkLabel(
            self,
            text="Time Remaining: 60s",
            font=("Helvetica", 18, "bold")
        )
        self.timer_label.pack()

        # SENTENCE FRAME
        self.sentence_frame = ctk.CTkFrame(self, width=620, height=100)
        self.sentence_frame.pack(pady=20)
        self.sentence_frame.pack_propagate(False)

        # SENTENCE LABEL
        self.sentence_label = ctk.CTkLabel(
            self.sentence_frame,
            text="Press Start to begin",
            wraplength=580,
            justify="left",
            font=("Helvetica", 20, "bold")
        )
        self.sentence_label.pack(padx=10, pady=10)

        # INPUT BOX
        self.input_textbox = ctk.CTkTextbox(
            self,
            width=600,
            height=120,
            font=("Helvetica", 16)
        )
        self.input_textbox.pack(pady=10)
        self.input_textbox.configure(state="disabled")

        # bind key press for sound
        self.input_textbox.bind("<Key>", self.play_typing_sound)

        # RESULT
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=("Helvetica", 20, "bold")
        )
        self.result_label.pack(pady=10)

        # BUTTON FRAME
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        # START BUTTON
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Test",
            command=self.start_test
        )
        self.start_button.grid(row=0, column=0, padx=10)

        # PAUSE BUTTON
        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self.toggle_pause,
            state="disabled"
        )
        self.pause_button.grid(row=0, column=1, padx=10)

        # RESULT BUTTON
        self.result_button = ctk.CTkButton(
            self.button_frame,
            text="Check Result",
            command=self.check_result,
            state="disabled"
        )
        self.result_button.grid(row=0, column=2, padx=10)

    # ======================
    # START TEST
    # ======================
    def start_test(self):

        self.result_label.configure(text="")
        self.countdown = 3
        self.input_textbox.configure(state="disabled")

        self.start_button.configure(state="disabled")

        self.show_countdown()

    # ======================
    # COUNTDOWN
    # ======================
    def show_countdown(self):

        if self.countdown > 0:

            self.sentence_label.configure(
                text=f"Starting in {self.countdown}..."
            )

            self.countdown -= 1

            self.after(1000, self.show_countdown)

        else:

            self.sentence_label.configure(text="GO!")

            self.after(800, self.begin_test)

    # ======================
    # BEGIN TEST
    # ======================
    def begin_test(self):

        self.current_sentence = random.choice(SENTENCES)

        self.sentence_label.configure(text=self.current_sentence)

        self.input_textbox.configure(state="normal")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.focus()

        self.start_time = time.time()
        self.time_left = TEST_DURATION
        self.timer_running = True
        self.paused = False

        self.pause_button.configure(state="normal")
        self.result_button.configure(state="normal")

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

                self.after(1000, self.update_timer)

            else:

                self.check_result()

    # ======================
    # PAUSE / RESUME
    # ======================
    def toggle_pause(self):

        if not self.timer_running:
            return

        if not self.paused:

            self.paused = True
            self.pause_button.configure(text="Resume")

        else:

            self.paused = False
            self.pause_button.configure(text="Pause")
            self.update_timer()

    # ======================
    # PLAY TYPING SOUND
    # ======================
    def play_typing_sound(self, event):

        if not self.timer_running:
            return

        typed = self.input_textbox.get("1.0", "end-1c")
        index = len(typed)

        if event.keysym == "BackSpace":
            winsound.Beep(500, 40)
            return

        if index < len(self.current_sentence):

            expected_char = self.current_sentence[index]

            if event.char == expected_char:
                winsound.Beep(800, 30)  # correct key
            else:
                winsound.Beep(300, 80)  # wrong key

    # ======================
    # RESULT
    # ======================
    def check_result(self):

        if not self.start_time:
            return

        self.timer_running = False

        winsound.Beep(1200, 300)  # completion sound

        typed_text = self.input_textbox.get("1.0", "end-1c")

        elapsed_time = time.time() - self.start_time

        chars = len(typed_text)

        if elapsed_time == 0:
            wpm = 0
        else:
            wpm = (chars / 5) / (elapsed_time / 60)

        self.result_label.configure(
            text=f"Typing Speed: {wpm:.2f} WPM"
        )

        self.input_textbox.configure(state="disabled")
        self.pause_button.configure(state="disabled")
        self.start_button.configure(state="normal")


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()