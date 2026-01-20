import customtkinter as ctk
from PIL import Image, ImageTk
import os

class OracleCanvasWindow(ctk.CTkToplevel):
    """
    A dedicated window for Oracle to show her 'Digital Studio' work.
    """
    def __init__(self, parent, image_path=None):
        super().__init__(parent)
        self.title("Oracle Digital Studio - Live Canvas")
        self.geometry("850x650")
        self.attributes("-topmost", True)
        
        self.label = ctk.CTkLabel(self, text="Oracle's Masterpiece", font=("Arial", 20, "bold"))
        self.label.pack(pady=10)
        
        self.canvas_frame = ctk.CTkFrame(self, width=800, height=500)
        self.canvas_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.image_label = ctk.CTkLabel(self.canvas_frame, text="")
        self.image_label.pack(fill="both", expand=True)
        
        if image_path and os.path.exists(image_path):
            self.display_image(image_path)
        else:
            self.image_label.configure(text="No artwork loaded yet.")

    def display_image(self, image_path):
        """Loads and displays an image on the canvas."""
        try:
            img = Image.open(image_path)
            
            # Resize to fit the window while maintaining aspect ratio
            max_size = (780, 480)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.image_label.configure(image=ctk_img, text="")
            self.image_label.image = ctk_img # Keep a reference
        except Exception as e:
            self.image_label.configure(text=f"Error loading image: {e}")
