"""
Floating Panel UI for Oracle using CustomTkinter.

This provides a modern, dark-themed, floating, and collapsible panel.
"""

import customtkinter as ctk
import tkinter as tk
from core.task_executor import TaskExecutor # Import for type hinting

class FloatingPanel(ctk.CTk):
    """
    A floating, collapsible panel for Oracle that stays on top of other windows.
    """
    def __init__(self, task_executor: TaskExecutor, width: int = 400, height: int = 300):
        super().__init__()
        self.task_executor = task_executor
        self.width = width
        self.height = height
        self.is_minimized = False
        self.min_width = 80
        self.min_height = 80
        self.original_geometry = f"{self.width}x{self.height}"

        # Configure window
        self.title("Oracle AI Assistant")
        self.geometry(self.original_geometry)
        self.attributes('-topmost', True) # Keep on top
        self.resizable(True, True)
        self.configure(fg_color="#1e1e1e") # Dark background

        # Set up grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="#2e2e2e")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title Label
        title_label = ctk.CTkLabel(header_frame, text="Oracle", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Minimize Button
        self.minimize_btn = ctk.CTkButton(header_frame, text="—", width=30, command=self.toggle_minimize)
        self.minimize_btn.grid(row=0, column=2, padx=(0, 5), pady=5)

        # Close Button
        close_btn = ctk.CTkButton(header_frame, text="X", width=30, command=self.on_close)
        close_btn.grid(row=0, column=3, padx=(0, 5), pady=5)

        # --- Output Text Area ---
        self.output_text = ctk.CTkTextbox(self, state="disabled", wrap="word", fg_color="#000000", text_color="#00ff00")
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # --- Input Frame ---
        input_frame = ctk.CTkFrame(self, fg_color="#2e2e2e")
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        input_frame.grid_columnconfigure(0, weight=1)

        # Input Entry
        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Type your command or question...", fg_color="#3e3e3e")
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.input_entry.bind("<Return>", self.on_send)

        # Send Button
        send_btn = ctk.CTkButton(input_frame, text="Send", width=70, command=self.on_send)
        send_btn.grid(row=0, column=1, padx=5, pady=5)

        # Voice Button (Placeholder for Whisper)
        self.voice_btn = ctk.CTkButton(input_frame, text="🎤", width=30, command=self.on_voice_command)
        self.voice_btn.grid(row=0, column=2, padx=(0, 5), pady=5)

        # Make window draggable
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

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

    def toggle_minimize(self):
        """Minimizes/restores the window."""
        if self.is_minimized:
            self.geometry(self.original_geometry)
            self.is_minimized = False
            self.minimize_btn.configure(text="—")
        else:
            self.original_geometry = self.geometry() # Save current size/position
            self.geometry(f"{self.min_width}x{self.min_height}")
            self.is_minimized = True
            self.minimize_btn.configure(text="□")

    def on_send(self, event=None):
        """Handles the send button click or Enter key press."""
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        
        if user_input.strip():
            self.append_output(f"You: {user_input}", "white")
            
            # Execute the task (this is where the core logic is called)
            response = self.task_executor.execute_task(user_input)
            self.append_output(f"Oracle: {response}", "#00ff00")
            
            # Text-to-Speech for the response
            self.speak(response)

    def on_voice_command(self):
        """Placeholder for Whisper integration."""
        self.append_output("Oracle: Listening for voice command... (Whisper integration pending)", "yellow")
        # In a full implementation, this would call the Whisper module
        # transcribed_text = self.task_executor.voice_input()
        # self.on_send(transcribed_text)

    def append_output(self, text: str, color: str):
        """Appends text to the output area."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text + "\n", color)
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def speak(self, text: str):
        """Placeholder for Text-to-Speech."""
        # In a full implementation, this would call the pyttsx3 module
        # engine = pyttsx3.init()
        # engine.say(text)
        # engine.runAndWait()
        pass

    def on_close(self):
        """Handles the close button click."""
        self.quit()

    def run(self):
        """Starts the UI event loop."""
        self.mainloop()

# Set the appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
