import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class OracleImageArtist:
    """
    The 'Photoshop' of Oracle. Handles image creation, editing, and manipulation.
    """
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            # Handle PyInstaller pathing
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.assets_dir = os.path.join(base_path, "assets")
        else:
            self.assets_dir = assets_dir
            
        self.output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        self.current_canvas = None

    def create_blank_canvas(self, width=800, height=600, color="white"):
        """Creates a new blank image."""
        self.current_canvas = Image.new("RGB", (width, height), color)
        return f"Created a {width}x{height} {color} canvas."

    def draw_shape(self, shape_type, coords, fill=None, outline="black", width=1):
        """Draws a shape (rectangle, ellipse) on the current canvas."""
        if not self.current_canvas:
            return "Error: No canvas active. Create one first."
        
        draw = ImageDraw.Draw(self.current_canvas)
        if shape_type == "rectangle":
            draw.rectangle(coords, fill=fill, outline=outline, width=width)
        elif shape_type == "ellipse":
            draw.ellipse(coords, fill=fill, outline=outline, width=width)
        return f"Drew a {shape_type} at {coords}."

    def add_text(self, text, position, font_size=20, color="black"):
        """Adds text to the current canvas."""
        if not self.current_canvas:
            return "Error: No canvas active."
        
        draw = ImageDraw.Draw(self.current_canvas)
        try:
            # Try to find a system font, fallback to default
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        draw.text(position, text, fill=color, font=font)
        return f"Added text '{text}' at {position}."

    def apply_filter(self, filter_type):
        """Applies a filter (BLUR, CONTOUR, DETAIL, etc.) to the canvas."""
        if not self.current_canvas:
            return "Error: No canvas active."
        
        filters = {
            "blur": ImageFilter.BLUR,
            "contour": ImageFilter.CONTOUR,
            "detail": ImageFilter.DETAIL,
            "edge_enhance": ImageFilter.EDGE_ENHANCE,
            "sharpen": ImageFilter.SHARPEN
        }
        
        f = filters.get(filter_type.lower())
        if f:
            self.current_canvas = self.current_canvas.filter(f)
            return f"Applied {filter_type} filter."
        return f"Filter {filter_type} not found."

    def save_canvas(self, filename="oracle_artwork.png"):
        """Saves the current canvas to the output directory."""
        if not self.current_canvas:
            return "Error: No canvas to save."
        
        path = os.path.join(self.output_dir, filename)
        self.current_canvas.save(path)
        return f"Artwork saved to {path}"

    def open_image(self, path):
        """Opens an existing image for editing."""
        if os.path.exists(path):
            self.current_canvas = Image.open(path).convert("RGB")
            return f"Opened image: {path}"
        return f"Error: File {path} not found."

    def resize_image(self, width, height):
        """Resizes the current canvas."""
        if not self.current_canvas:
            return "Error: No canvas active."
        self.current_canvas = self.current_canvas.resize((width, height), Image.LANCZOS)
        return f"Resized image to {width}x{height}."

    def rotate_image(self, degrees):
        """Rotates the current canvas."""
        if not self.current_canvas:
            return "Error: No canvas active."
        self.current_canvas = self.current_canvas.rotate(degrees, expand=True)
        return f"Rotated image by {degrees} degrees."

    def crop_image(self, left, top, right, bottom):
        """Crops the current canvas."""
        if not self.current_canvas:
            return "Error: No canvas active."
        self.current_canvas = self.current_canvas.crop((left, top, right, bottom))
        return f"Cropped image to ({left}, {top}, {right}, {bottom})."
