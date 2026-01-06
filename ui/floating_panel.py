import tkinter as tk
import customtkinter as ctk
from ui.themes import OracleThemes
import math
import random

class OracleUI(ctk.CTk):
    def __init__(self, task_executor):
        super().__init__()
        self.task_executor = task_executor
        
        # State Management
        self.current_theme_name = "Electric Shimmer"
        self.theme = OracleThemes.get_theme(self.current_theme_name)
        self.is_orb_mode = False
        self.original_geometry = "400x500"
        
        # Animation & Resize State
        self.particles = []
        self.angle = 0
        self.border_width = 5
        
        # Window Configuration
        self.title("Oracle AI Assistant")
        self.geometry(self.original_geometry)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.attributes("-alpha", self.theme["transparency"])
        
        self.setup_ui()
        
        # Bindings for dragging and resizing
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<B1-Motion>", self.on_motion)
        self.bind("<Motion>", self.update_cursor)

    def setup_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        if self.is_orb_mode:
            self.setup_orb_ui()
        else:
            self.setup_full_ui()

    def setup_full_ui(self):
        self.configure(fg_color=self.theme["bg"])
        self.attributes("-transparentcolor", "")
        
        # Custom Title Bar
        self.title_bar = ctk.CTkFrame(self, fg_color=self.theme["bg"], height=30)
        self.title_bar.pack(fill="x", side="top")
        
        self.title_label = ctk.CTkLabel(self.title_bar, text="Oracle", font=(self.theme["font"][0], 12, "bold"), text_color=self.theme["accent"])
        self.title_label.pack(side="left", padx=10)

        # Control Buttons
        close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, fg_color="transparent", hover_color="#ff4444", command=self.destroy)
        close_btn.pack(side="right", padx=2)
        
        orb_btn = ctk.CTkButton(self.title_bar, text="🔮", width=30, height=25, fg_color="transparent", command=self.toggle_orb_mode)
        orb_btn.pack(side="right", padx=2)
        
        settings_btn = ctk.CTkButton(self.title_bar, text="⚙️", width=30, height=25, fg_color="transparent", command=self.show_settings)
        settings_btn.pack(side="right", padx=2)

        # Chat Area
        self.output_text = ctk.CTkTextbox(self, fg_color="#000000", text_color=self.theme["text_color"], font=self.theme["font"])
        self.output_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.output_text.insert("0.0", "Oracle: Hey dad, my systems are ready for your instructions.\n")},{find:
        self.output_text.configure(state="disabled")

        # Input Area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Type your command...", fg_color="#121212", text_color="white", border_color=self.theme["accent"])
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.on_send)

        send_btn = ctk.CTkButton(input_frame, text="Send", width=60, fg_color=self.theme["accent"], command=self.on_send)
        send_btn.pack(side="left", padx=2)

        mic_btn = ctk.CTkButton(input_frame, text="🎤", width=35, fg_color="transparent", command=self.on_voice_command)
        mic_btn.pack(side="left", padx=2)

        vision_btn = ctk.CTkButton(input_frame, text="👁️", width=35, fg_color="transparent", command=self.on_vision_command)
        vision_btn.pack(side="left", padx=2)

    def setup_orb_ui(self):
        self.geometry("100x100")
        self.configure(fg_color="black")
        self.attributes("-transparentcolor", "black")
        
        self.orb_canvas = tk.Canvas(self, width=100, height=100, bg="black", highlightthickness=0)
        self.orb_canvas.pack()
        
        self.particles = []
        for _ in range(20):
            self.particles.append({
                "x": 50, "y": 50,
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-1, 1),
                "size": random.uniform(2, 5),
                "color": random.choice(["#00d4ff", "#ffffff", "#007acc"])
            })
        
        self.orb_canvas.bind("<Double-Button-1>", lambda e: self.toggle_orb_mode())
        self.animate_orb()

    def animate_orb(self):
        if not self.is_orb_mode:
            return
        self.orb_canvas.delete("all")
        self.angle += 0.1
        for i in range(3):
            r = 25 + math.sin(self.angle + i) * 5
            x = 50 + math.cos(self.angle * (i+1)) * 5
            y = 50 + math.sin(self.angle * (i+1)) * 5
            self.orb_canvas.create_oval(x-r, y-r, x+r, y+r, outline=self.theme["accent"], width=1)
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            dist = math.sqrt((p["x"]-50)**2 + (p["y"]-50)**2)
            if dist > 30:
                p["vx"] *= -1
                p["vy"] *= -1
            self.orb_canvas.create_oval(p["x"]-p["size"], p["y"]-p["size"], p["x"]+p["size"], p["y"]+p["size"], fill=p["color"], outline="")
        self.after(30, self.animate_orb)

    def toggle_orb_mode(self):
        self.is_orb_mode = not self.is_orb_mode
        self.setup_ui()

    def show_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("Oracle Settings")
        settings_win.geometry("250x200")
        settings_win.attributes("-topmost", True)
        ctk.CTkLabel(settings_win, text="Select Theme", font=("Segoe UI", 12, "bold")).pack(pady=10)
        theme_var = ctk.StringVar(value=self.current_theme_name)
        themes = ["Classic", "Cyber-Glitch", "Electric Shimmer"]
        for t in themes:
            ctk.CTkRadioButton(settings_win, text=t, variable=theme_var, value=t, command=lambda: self.change_theme(theme_var.get())).pack(pady=5)

    def change_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.theme = OracleThemes.get_theme(theme_name)
        self.attributes("-alpha", self.theme["transparency"])
        self.setup_ui()

    # Resizing and Movement Logic
    def update_cursor(self, event):
        if self.is_orb_mode:
            self.config(cursor="fleur")
            return

        x, y = event.x, event.y
        w, h = self.winfo_width(), self.winfo_height()
        
        if x > w - self.border_width and y > h - self.border_width:
            self.config(cursor="size_nw_se")
        elif x > w - self.border_width:
            self.config(cursor="size_we")
        elif y > h - self.border_width:
            self.config(cursor="size_ns")
        else:
            self.config(cursor="arrow")

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()
        
        w, h = self.start_width, self.start_height
        if event.x > w - self.border_width or event.y > h - self.border_width:
            self.resizing = True
        else:
            self.resizing = False

    def on_release(self, event):
        self.resizing = False

    def on_motion(self, event):
        if self.is_orb_mode or not hasattr(self, 'start_x'):
            # Standard move for Orb
            deltax = event.x - self.start_x
            deltay = event.y - self.start_y
            self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")
            return

        if self.resizing:
            new_width = max(300, self.start_width + (event.x - self.start_x))
            new_height = max(200, self.start_height + (event.y - self.start_y))
            self.geometry(f"{new_width}x{new_height}")
        else:
            deltax = event.x - self.start_x
            deltay = event.y - self.start_y
            self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")

    # Functional Hooks
    def on_send(self, event=None):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        if user_input.strip():
            self.append_output(f"You: {user_input}", "white")
            response = self.task_executor.execute_task(user_input)
            self.append_output(f"Oracle: {response}", self.theme["text_color"])

    def on_voice_command(self):
        self.append_output("Oracle: Listening...", "yellow")
        self.update()
        text = self.task_executor.process_voice_input()
        if text:
            self.append_output(f"You (Voice): {text}", "white")
            response = self.task_executor.execute_task(text)
            self.append_output(f"Oracle: {response}", self.theme["text_color"])

    def on_vision_command(self):
        self.append_output("Oracle: Observing screen...", "cyan")
        self.update()
        self.task_executor.process_visual_input()
        self.append_output("Oracle: I see your screen. How can I help?", "cyan")

    def append_output(self, text, color):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{text}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
