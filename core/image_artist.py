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

    def generate_ai_image(self, prompt: str) -> str:
        """
        Generates a real image using local Forge/Automatic1111 if available, otherwise falls back to Pollinations.ai.
        """
        try:
            import requests
            import io
            import random
            import base64
            
            # 1. Try local Forge/Automatic1111 first (NO FILTERS)
            # ANATOMY ENFORCEMENT: Adding technical tags to ensure realism and bypass abstraction
            enhanced_prompt = f"{prompt}, photorealistic, highly detailed, anatomically correct, 8k, raw photo"
            
            local_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
            payload = {
                "prompt": enhanced_prompt,
                "negative_prompt": "abstract, cartoon, blurry, low quality, distorted anatomy, extra limbs",
                "steps": 30,
                "width": 1024,
                "height": 1024,
                "sampler_name": "DPM++ 2M Karras",
                "cfg_scale": 8
            }
            try:
                local_response = requests.post(local_url, json=payload, timeout=5)
                if local_response.status_code == 200:
                    r = local_response.json()
                    image_data = base64.b64decode(r['images'][0])
                    self.current_canvas = Image.open(io.BytesIO(image_data))
                    return "SUCCESS: Unfiltered AI Image generated locally via Forge."
            except:
                pass # Fallback to Pollinations if local is not running

            # 2. Fallback to Pollinations.ai API
            clean_prompt = requests.utils.quote(prompt)
            seed = random.randint(0, 999999)
            url = f"https://image.pollinations.ai/prompt/{clean_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                image_data = response.content
                self.current_canvas = Image.open(io.BytesIO(image_data))
                return "SUCCESS: AI Image generated successfully via Pollinations."
            else:
                return f"FAILURE: API returned status {response.status_code}"
        except Exception as e:
            return f"FAILURE: Error generating AI image: {e}"

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
