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
# WORD BANK — 200+ common English words by category
# ============================================================

WORD_BANK = {
    "nouns": [
        "time", "world", "system", "program", "computer", "network", "data",
        "project", "team", "design", "problem", "solution", "process",
        "development", "technology", "software", "hardware", "engineer",
        "student", "teacher", "market", "company", "product", "service",
        "quality", "method", "approach", "strategy", "result", "experience",
        "knowledge", "science", "research", "language", "history", "future",
        "community", "environment", "industry", "platform", "framework",
        "database", "server", "browser", "keyboard", "algorithm", "function",
        "variable", "library", "module", "interface", "feature", "concept",
        "pattern", "structure", "resource", "challenge", "opportunity",
        "innovation", "progress", "creativity", "performance", "security",
        "analysis", "feedback", "document", "application", "machine",
        "device", "cloud", "energy", "practice", "culture", "leader",
    ],
    "verbs": [
        "build", "create", "develop", "design", "improve", "manage",
        "analyze", "solve", "learn", "teach", "write", "read", "test",
        "deploy", "monitor", "optimize", "transform", "integrate",
        "collaborate", "communicate", "explore", "discover", "implement",
        "generate", "process", "support", "maintain", "update", "deliver",
        "achieve", "understand", "consider", "provide", "require", "enable",
        "produce", "organize", "evaluate", "measure", "enhance", "simplify",
        "automate", "connect", "share", "protect", "strengthen", "inspire",
        "accelerate", "establish", "refactor", "compile", "debug", "execute",
    ],
    "adjectives": [
        "effective", "modern", "complex", "simple", "powerful", "reliable",
        "creative", "innovative", "efficient", "robust", "scalable",
        "flexible", "secure", "dynamic", "practical", "critical", "global",
        "digital", "advanced", "essential", "productive", "responsive",
        "consistent", "sustainable", "intelligent", "comprehensive",
        "strategic", "technical", "functional", "intuitive", "clean",
        "stable", "rapid", "elegant", "maintainable", "collaborative",
        "parallel", "automated", "structured", "modular", "portable",
    ],
    "adverbs": [
        "quickly", "efficiently", "effectively", "carefully", "rapidly",
        "constantly", "frequently", "consistently", "significantly",
        "dramatically", "naturally", "automatically", "successfully",
        "properly", "directly", "easily", "simply", "precisely",
        "thoroughly", "continuously", "increasingly", "fundamentally",
        "reliably", "gracefully", "seamlessly", "independently",
    ],
    "connectors": [
        "and", "but", "while", "because", "although", "since", "when",
        "before", "after", "unless", "however", "therefore", "moreover",
        "furthermore", "meanwhile", "nevertheless", "consequently",
        "additionally", "yet", "so", "then", "also", "instead",
    ],
    "prepositions": [
        "in", "on", "with", "for", "from", "about", "through", "across",
        "between", "within", "beyond", "around", "during", "without",
        "toward", "against", "among", "beneath", "above", "behind",
    ],
    "articles_determiners": [
        "the", "a", "an", "every", "each", "many", "several", "some",
        "most", "this", "that", "these", "those", "numerous", "various",
    ],
}

# ============================================================
# SENTENCE TEMPLATES — structural variety
# ============================================================

SENTENCE_TEMPLATES = [
    "{det} {adj} {noun} {verb}s {adv}.",
    "{det} {noun} can {verb} {det} {adj} {noun}.",
    "{adv}, {det} {adj} {noun} {verb}s {det} {noun}.",
    "{det} {noun} {verb}s {prep} {det} {adj} {noun}.",
    "Every {adj} {noun} must {verb} {det} {noun} {adv}.",
    "{det} {adj} {noun} {verb}s {conn} {det} {noun} {verb}s.",
    "To {verb} {adv} is to {verb} {det} {adj} {noun}.",
    "{det} {noun} {verb}s {det} {noun} {prep} {det} {adj} {noun}.",
    "Many {adj} {noun}s {verb} {adv} {prep} {det} {noun}.",
    "When {det} {noun} {verb}s, {det} {adj} {noun} {verb}s {adv}.",
    "{det} {adj} {noun} helps {det} {noun} {verb} {adv}.",
    "A {adj} {noun} will {verb} {det} {noun} {prep} {det} {noun}.",
    "{adv}, {det} {noun} can {verb} {conn} {verb} {det} {adj} {noun}.",
    "The best {noun}s {verb} {det} {adj} {noun} {adv}.",
    "Without {det} {adj} {noun}, {det} {noun} cannot {verb} {adv}.",
    "{det} {noun} {adv} {verb}s {det} {adj} {noun} {prep} {det} {noun}.",
]


# ============================================================
# TEXT GENERATOR
# ============================================================

def _random_word(category: str) -> str:
    """Pick a random word from the given word bank category."""
    return random.choice(WORD_BANK[category])


def generate_sentence() -> str:
    """Generate a single random sentence from a template."""
    template = random.choice(SENTENCE_TEMPLATES)
    sentence = template.format(
        det=_random_word("articles_determiners"),
        adj=_random_word("adjectives"),
        noun=_random_word("nouns"),
        verb=_random_word("verbs"),
        adv=_random_word("adverbs"),
        conn=_random_word("connectors"),
        prep=_random_word("prepositions"),
    )
    # Capitalize the first letter
    return sentence[0].upper() + sentence[1:]


def generate_text(mode: str) -> str:
    """
    Generate random text based on the selected text length mode.
    - 'Short Sentence': 1 random sentence
    - 'Paragraph': 3-5 random sentences joined
    - 'Long Text': 7-10 random sentences joined
    """
    if mode == "Short Sentence":
        return generate_sentence()
    elif mode == "Paragraph":
        count = random.randint(3, 5)
        return " ".join(generate_sentence() for _ in range(count))
    elif mode == "Long Text":
        count = random.randint(7, 10)
        return " ".join(generate_sentence() for _ in range(count))
    else:
        return generate_sentence()


# ============================================================
# STATIC TEXT POOLS — fallback / classic mode
# ============================================================

STATIC_TEXT_POOLS = {
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

TEXT_LENGTH_OPTIONS = list(STATIC_TEXT_POOLS.keys())

TEXT_SOURCE_OPTIONS = ["Random Generated", "Classic Static"]


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
        self.geometry("780x750")

        self.current_sentence = ""
        self.start_time = None
        self.test_duration = DEFAULT_DURATION
        self.time_left = self.test_duration
        self.timer_running = False
        self.paused = False
        self.countdown = 3
        self.after_id = None
        self.live_wpm_after_id = None

        self.data = load_data()

        # ── TITLE ──────────────────────────────────────────────
        self.title_label = ctk.CTkLabel(
            self,
            text="Typing Speed Test",
            font=("Helvetica", 30, "bold"),
        )
        self.title_label.pack(pady=15)

        # ── SETTINGS FRAME (duration + text length + source) ──
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=(0, 5))

        # Row 0: Duration + Text Length
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

        # Row 1: Text Source selector
        self.text_source_label = ctk.CTkLabel(
            self.settings_frame,
            text="Text Source:",
            font=("Helvetica", 14),
        )
        self.text_source_label.grid(row=1, column=0, padx=(10, 5), pady=5)

        self.text_source_var = ctk.StringVar(value="Random Generated")
        self.text_source_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            variable=self.text_source_var,
            values=TEXT_SOURCE_OPTIONS,
            width=180,
        )
        self.text_source_menu.grid(row=1, column=1, columnspan=2, padx=(0, 20), pady=5)

        # ── STATS FRAME (timer + live WPM side by side) ───────
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(pady=(5, 0))

        self.timer_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"⏱ Time Remaining: {self.test_duration}s",
            font=("Helvetica", 18, "bold"),
        )
        self.timer_label.grid(row=0, column=0, padx=(20, 40))

        self.live_wpm_label = ctk.CTkLabel(
            self.stats_frame,
            text="⌨ Live WPM: 0.00",
            font=("Helvetica", 18, "bold"),
            text_color="#555555",
        )
        self.live_wpm_label.grid(row=0, column=1, padx=(40, 20))

        # ── SENTENCE FRAME ─────────────────────────────────────
        self.sentence_frame = ctk.CTkFrame(self, width=700, height=130)
        self.sentence_frame.pack(pady=15)
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
            width=680,
            height=120,
            font=("Helvetica", 16),
        )
        self.input_textbox.pack(pady=10)
        self.input_textbox.configure(state="disabled")

        self.input_textbox.bind("<KeyRelease>", self.handle_typing)
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

        self.bind("<Return>", self.handle_enter)

    # ======================
    # SETTINGS CALLBACKS
    # ======================

    def on_duration_change(self, choice: str):
        """Update the displayed timer immediately when the user picks a new duration."""
        self.test_duration = DURATION_OPTIONS.get(choice, DEFAULT_DURATION)
        if not self.timer_running:
            self.timer_label.configure(
                text=f"⏱ Time Remaining: {self.test_duration}s"
            )

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
    # TEXT GENERATION
    # ======================

    def get_test_text(self) -> str:
        """
        Return the test text based on the selected source and length mode.
        - 'Random Generated': uses the template-based generator
        - 'Classic Static': picks from the static text pools
        """
        text_length = self.text_length_var.get()
        text_source = self.text_source_var.get()

        if text_source == "Random Generated":
            return generate_text(text_length)
        else:
            pool = STATIC_TEXT_POOLS.get(
                text_length, STATIC_TEXT_POOLS["Short Sentence"]
            )
            return random.choice(pool)

    # ======================
    # CALCULATE CURRENT WPM
    # ======================

    def calculate_current_wpm(self):
        """Return the current WPM based on correct characters typed so far."""
        if not self.start_time:
            return 0.0

        typed_text = self.input_textbox.get("1.0", "end-1c")
        elapsed_time = time.time() - self.start_time

        if elapsed_time <= 0:
            return 0.0

        correct_chars = sum(
            1
            for i, char in enumerate(typed_text)
            if i < len(self.current_sentence) and self.current_sentence[i] == char
        )

        wpm = (correct_chars / 5) / (elapsed_time / 60)
        return wpm

    # ======================
    # LIVE WPM UPDATE LOOP
    # ======================

    def update_live_wpm(self):
        """Scheduled loop that refreshes the live WPM label every second."""
        if not self.timer_running or self.paused:
            return

        current_wpm = self.calculate_current_wpm()
        self.live_wpm_label.configure(text=f"⌨ Live WPM: {current_wpm:.2f}")

        if current_wpm >= 60:
            self.live_wpm_label.configure(text_color="#00AA00")
        elif current_wpm >= 30:
            self.live_wpm_label.configure(text_color="#CC8800")
        else:
            self.live_wpm_label.configure(text_color="#CC0000")

        self.live_wpm_after_id = self.after(1000, self.update_live_wpm)

    # ======================
    # START TEST
    # ======================

    def start_test(self):
        if self.timer_running:
            return

        self.test_duration = DURATION_OPTIONS.get(
            self.duration_var.get(), DEFAULT_DURATION
        )
        self.timer_label.configure(
            text=f"⏱ Time Remaining: {self.test_duration}s"
        )

        self.live_wpm_label.configure(
            text="⌨ Live WPM: 0.00", text_color="#555555"
        )

        self.result_label.configure(text="")
        self.countdown = 3
        self.input_textbox.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.pause_button.configure(text="Pause")

        # Disable all settings while test is in progress
        self.duration_menu.configure(state="disabled")
        self.text_length_menu.configure(state="disabled")
        self.text_source_menu.configure(state="disabled")

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
        # Generate text based on selected source and length
        self.current_sentence = self.get_test_text()

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
        self.update_live_wpm()

    # ======================
    # TIMER (wall-clock based to avoid drift)
    # ======================

    def update_timer(self):
        if not self.timer_running or self.paused:
            return

        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.test_duration - elapsed)
        self.timer_label.configure(text=f"⏱ Time Remaining: {remaining}s")

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
            if self.live_wpm_after_id:
                self.after_cancel(self.live_wpm_after_id)
        else:
            self.pause_button.configure(text="Pause")
            pause_duration = time.time() - self.pause_start
            self.start_time += pause_duration
            self.update_timer()
            self.update_live_wpm()

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
            if index <= len(self.current_sentence) and index > 0:
                expected = self.current_sentence[index - 1]
                if typed[-1] == expected:
                    beep(800, 30)
                else:
                    beep(300, 80)

        self.update_sentence_display()

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

        if self.live_wpm_after_id:
            self.after_cancel(self.live_wpm_after_id)
            self.live_wpm_after_id = None

        if not self.timer_running:
            return

        self.timer_running = False
        beep(1200, 300)

        final_wpm = self.calculate_current_wpm()

        self.live_wpm_label.configure(
            text=f"⌨ Final WPM: {final_wpm:.2f}",
            text_color="#0055CC",
        )

        self.update_streaks(final_wpm)

        self.result_label.configure(text=f"Typing Speed: {final_wpm:.2f} WPM")
        self.streak_label.configure(text=self.get_streak_text())

        self.input_textbox.configure(state="disabled")
        self.pause_button.configure(state="disabled")
        self.start_button.configure(state="normal")

        # Re-enable all settings selectors
        self.duration_menu.configure(state="normal")
        self.text_length_menu.configure(state="normal")
        self.text_source_menu.configure(state="normal")

        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")
        self.sentence_textbox.insert("1.0", "Press Enter or click Start to begin")
        self.sentence_textbox.configure(state="disabled")


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()
