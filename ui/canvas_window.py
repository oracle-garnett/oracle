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
        
        # Ensure window is on top and visible
        self.attributes("-topmost", True)
        self.after(2000, lambda: self.attributes("-topmost", False)) # Stay on top for 2 secs then behave normally
        self.deiconify()
        self.focus_force()
        
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
            # Ensure the path is absolute
            image_path = os.path.abspath(image_path)
            if not os.path.exists(image_path):
                self.image_label.configure(text=f"Error: File not found at {image_path}\n\nDad, I might have misplaced my drawing. Let me try again!")
                return

            # Add a small delay to ensure the file is fully written to disk
            import time
            time.sleep(0.5)

            img = Image.open(image_path)
            
            # Resize to fit the window while maintaining aspect ratio
            # We use a slightly smaller size to ensure it fits within the frame
            max_width = self.canvas_frame.winfo_width() if self.canvas_frame.winfo_width() > 1 else 780
            max_height = self.canvas_frame.winfo_height() if self.canvas_frame.winfo_height() > 1 else 480
            
            # Calculate aspect ratio
            ratio = min(max_width / img.width, max_height / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)
            self.image_label.configure(image=ctk_img, text="")
            self.image_label._image = ctk_img # Keep a strong reference to prevent garbage collection
            
            self.label.configure(text=f"Oracle's Masterpiece: {os.path.basename(image_path)}")
        except Exception as e:
            self.image_label.configure(text=f"Error loading image: {e}")
