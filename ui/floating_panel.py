import tkinter as tk
import customtkinter as ctk
from ui.themes import OracleThemes
import math

class OracleUI(ctk.CTk):
    def __init__(self, task_executor):
        super().__init__()
        self.task_executor = task_executor
        
        # State Management
        self.current_theme_name = "Electric Shimmer"
        self.theme = OracleThemes.get_theme(self.current_theme_name)
        self.is_orb_mode = False
        self.original_geometry = "400x500"
        
        # Window Configuration
        self.title("Oracle AI Assistant")
        self.geometry(self.original_geometry)
        self.attributes("-topmost", True)
        self.overrideredirect(True) # Remove title bar for custom look
        self.attributes("-alpha", self.theme["transparency"])
        
        self.setup_ui()
        
        # Dragging support
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

    def setup_ui(self):
        # Clear existing UI if any
        for widget in self.winfo_children():
            widget.destroy()

        if self.is_orb_mode:
            self.setup_orb_ui()
        else:
            self.setup_full_ui()

    def setup_full_ui(self):
        self.configure(fg_color=self.theme["bg"])
        
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
        self.output_text.insert("0.0", "Oracle: Systems active. Ready for your command, partner.\n")
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
        self.geometry("60x60")
        self.configure(fg_color="transparent")
        self.attributes("-transparentcolor", "black") # Make black transparent for orb effect
        
        # The Ghost Orb
        self.orb_canvas = tk.Canvas(self, width=60, height=60, bg="black", highlightthickness=0)
        self.orb_canvas.pack()
        
        # Draw the shimmering orb
        self.draw_orb()
        self.orb_canvas.bind("<Double-Button-1>", lambda e: self.toggle_orb_mode())

    def draw_orb(self):
        self.orb_canvas.delete("all")
        color = self.theme["accent"]
        # Simple shimmering effect using circles
        for i in range(5):
            alpha = 0.2 + (i * 0.1)
            size = 20 + (i * 5)
            self.orb_canvas.create_oval(30-size, 30-size, 30+size, 30+size, outline=color, width=2)
        
        self.orb_canvas.create_text(30, 30, text="O", fill=color, font=("Segoe UI", 14, "bold"))

    def toggle_orb_mode(self):
        self.is_orb_mode = not self.is_orb_mode
        if self.is_orb_mode:
            self.original_geometry = self.geometry()
            self.setup_ui()
        else:
            self.geometry("400x500")
            self.attributes("-transparentcolor", "") # Reset transparency
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

    # Movement Logic
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

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
