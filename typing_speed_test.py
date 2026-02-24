import tkinter as tk
from tkinter import messagebox
import random
import time

SENTENCES = [
    "Technology is the most effective way to change the world",
    "Innovation is the ability to see change as an opportunity -not a threat",
    "Artificial Intelligence is not a threat to creativity; it's a catalyst for innovation.",
    "Data is the canvas, and AI is the brush that paints the picture of insights.",
    "Artificial Intelligence: where innovation meets computation in the pursuit of a smarter tomorrow."
]

class TypingSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("600x520") # Increased height to accommodate the new button
        self.root.resizable(False, False)
        
        self.start_time = None
        self.current_sentence = ""
        
        self.title_label = tk.Label(root, text="Typing Speed Test", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        self.timer_label = tk.Label(root, text="⏱ Time: 00:00", font=("Helvetica", 14, "bold"), fg="blue")
        self.timer_label.pack(pady=5)
        
        self.instruction_label = tk.Label(root, text="Type the exact sentence below as fast as you can:", font=("Helvetica", 14))
        self.instruction_label.pack(pady=10)
        
        self.sentence_label = tk.Label(root, text="", font=("Helvetica", 16), wraplength=550, justify="center")
        self.sentence_label.pack(pady=10)
        
        self.input_textbox = tk.Text(root, font=("Helvetica", 14), width=50, height=2)
        self.input_textbox.pack(pady=5)
        
        self.error_feedback_label = tk.Label(root, text="", font=("Helvetica", 10, "bold"), fg="orange")
        self.error_feedback_label.pack()

        self.input_textbox.bind("<Return>", self.check_result)
        self.input_textbox.bind("<KeyRelease>", self.validate_typing)
        self.input_textbox.bind("<KeyRelease>", self.enable_button_after_typing, add="+")
        self.input_textbox.tag_configure("correct", foreground="green")
        self.input_textbox.tag_configure("incorrect", foreground="red")
        self.timer_running = False
        self.elapsed_seconds = 0
        # --- BUTTON SECTION ---
        # The Start/Restart Button
        self.start_button = tk.Button(root, text="Start Test", font=("Helvetica", 14), command=self.start_test)
        self.start_button.pack(pady=10)

        # NEW: Dedicated Display Results Button
        self.result_button = tk.Button(root, text="Display Results", font=("Helvetica", 14), command=self.check_result, state=tk.DISABLED)
        self.result_button.pack(pady=10)
        
        self.result_label = tk.Label(root, text="", font=("Helvetica", 14, "italic"), fg="green")
        self.result_label.pack(pady=10)
    
    def start_test(self):
        self.timer_running = False
        self.elapsed_seconds = 0
        self.timer_label.config(text="⏱ Time: 00:00")
        self.result_label.config(text="")
        self.error_feedback_label.config(text="")
        self.current_sentence = random.choice(SENTENCES)
        self.sentence_label.config(text=self.current_sentence)
        self.input_textbox.delete("1.0", tk.END)
        self.input_textbox.focus()
        self.start_button.config(text="Restart Test", state=tk.NORMAL)
        self.result_button.config(state=tk.NORMAL) # Enable result button when test starts

    def enable_button_after_typing(self, event=None):
        self.start_button.config(state=tk.NORMAL)
    
    def validate_typing(self, event=None):
        if not self.current_sentence:
            return
        if not self.timer_running and self.current_sentence:
            self.start_time = time.time()
            self.elapsed_seconds = 0
            self.timer_label.config(text="⏱ Time: 00:00")
            self.timer_running = True
            self.update_timer()
        typed_text = self.input_textbox.get("1.0", "end-1c")
        self.input_textbox.tag_remove("correct", "1.0", "end")
        self.input_textbox.tag_remove("incorrect", "1.0", "end")
        
        has_case_error = False
        
        for i, ch in enumerate(typed_text):
            start = f"1.0+{i}c"
            end = f"1.0+{i+1}c"
            
            if i < len(self.current_sentence):
                if ch == self.current_sentence[i]:
                    self.input_textbox.tag_add("correct", start, end)
                else:
                    self.input_textbox.tag_add("incorrect", start, end)
                    if ch.lower() == self.current_sentence[i].lower():
                        has_case_error = True
        
        if has_case_error:
            self.error_feedback_label.config(text="⚠ Case Mismatch! Check Caps Lock", fg="orange")
        elif "incorrect" in self.input_textbox.tag_ranges("incorrect"):
            self.error_feedback_label.config(text="❌ Character Error", fg="red")
        else:
            self.error_feedback_label.config(text="")
    
    def check_result(self, event=None):
        if not self.start_time:
            messagebox.showwarning("Warning", "Click 'Start Test' first!")
            return "break"
        
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        
        typed_text = self.input_textbox.get("1.0", "end-1c")
        if typed_text.strip() == self.current_sentence:
            word_count = len(self.current_sentence.split())
            wpm = (word_count / elapsed_time) * 60
            self.result_label.config(text=f"Well done! Your typing speed is {wpm:.2f} WPM.", fg="green")
            self.error_feedback_label.config(text="")
        else:
            self.result_label.config(text="Incorrect typing! Try again.", fg="red")
        self.timer_running = False
        self.start_time = None
        self.result_button.config(state=tk.DISABLED) # Disable until next test starts
        return "break"
    def update_timer(self):
        if self.timer_running:
            self.elapsed_seconds += 1
            minutes = self.elapsed_seconds // 60
            seconds = self.elapsed_seconds % 60
            self.timer_label.config(text=f"⏱ Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTest(root)
    root.mainloop()