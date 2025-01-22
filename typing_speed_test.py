import tkinter as tk
from tkinter import messagebox
import random
import time

# List of sample sentences
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
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.start_time = None
        self.current_sentence = ""
        
        # Title Label
        self.title_label = tk.Label(root, text="Typing Speed Test", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)
        
        # Instruction Label
        self.instruction_label = tk.Label(root, text="Type the exact sentence below as fast as you can:", font=("Helvetica", 14))
        self.instruction_label.pack(pady=10)
        
        # Sentence Display
        self.sentence_label = tk.Label(root, text="", font=("Helvetica", 16), wraplength=550, justify="center")
        self.sentence_label.pack(pady=10)
        
        # Input Textbox
        self.input_textbox = tk.Entry(root, font=("Helvetica", 14), width=50)
        self.input_textbox.pack(pady=10)
        self.input_textbox.bind("<Return>", self.check_result)  # Bind Enter key to check result
        
        # Start Button
        self.start_button = tk.Button(root, text="Start Test", font=("Helvetica", 14), command=self.start_test)
        self.start_button.pack(pady=20)
        
        # Result Label
        self.result_label = tk.Label(root, text="", font=("Helvetica", 14, "italic"), fg="green")
        self.result_label.pack(pady=10)
    
    def start_test(self):
        """Starts the typing test."""
        self.result_label.config(text="")
        self.current_sentence = random.choice(SENTENCES)
        self.sentence_label.config(text=self.current_sentence)
        self.input_textbox.delete(0, tk.END)
        self.input_textbox.focus()
        self.start_time = time.time()
    
    def check_result(self, event=None):
        """Checks the typing speed and accuracy."""
        if not self.start_time:
            messagebox.showwarning("Warning", "Click 'Start Test' first!")
            return
        
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        
        typed_text = self.input_textbox.get()
        if typed_text.strip() == self.current_sentence:
            word_count = len(self.current_sentence.split())
            wpm = (word_count / elapsed_time) * 60
            self.result_label.config(text=f"Well done! Your typing speed is {wpm:.2f} WPM.")
        else:
            self.result_label.config(text="Incorrect typing! Try again.", fg="red")
        
        # Reset the start time for the next test
        self.start_time = None

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTest(root)
    root.mainloop()
