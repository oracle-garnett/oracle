"""
Oracle Vision Module: The Optic Nerve.

This module provides high-performance screen capture, image processing,
and local OCR (Optical Character Recognition) capabilities.
"""

import os
import time
import pyautogui
from PIL import Image, ImageGrab
import pytesseract # For local text extraction from images

class OracleVision:
    """
    Handles all visual sensory input for Oracle.
    """
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'vision')
        
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Note: User will need to install Tesseract-OCR on their machine
        # We will provide instructions for this.
        if os.name == 'nt':
            self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        else:
            self.tesseract_cmd = '/usr/bin/tesseract'
            
        if os.path.exists(self.tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def capture_screen(self) -> str:
        """
        Captures the entire screen and saves it as a temporary file.
        Returns the path to the captured image.
        """
        timestamp = int(time.time())
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(self.storage_path, filename)
        
        # Capture the screen
        screenshot = ImageGrab.grab()
        
        # Optimize: Resize for faster processing while maintaining readability
        # We keep the original aspect ratio
        width, height = screenshot.size
        new_width = 1920 # Standard HD width for processing
        new_height = int((new_width / width) * height)
        screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        screenshot.save(filepath, "PNG")
        return filepath

    def read_screen_text(self, image_path: str) -> str:
        """
        Uses local OCR to extract text from the captured screen image.
        """
        try:
            if not os.path.exists(self.tesseract_cmd):
                return "[Vision Error: Tesseract-OCR not found. Please install it to enable screen reading.]"
            
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception as e:
            return f"[Vision Error: Could not extract text. {str(e)}]"

    def get_visual_context(self) -> dict:
        """
        The main entry point for Oracle to 'see'.
        Captures the screen and extracts text context.
        """
        image_path = self.capture_screen()
        extracted_text = self.read_screen_text(image_path)
        
        return {
            "image_path": image_path,
            "extracted_text": extracted_text,
            "timestamp": time.time()
        }

    def clean_up(self, max_files: int = 10):
        """Keeps the vision folder clean by removing old captures."""
        files = [os.path.join(self.storage_path, f) for f in os.listdir(self.storage_path)]
        files.sort(key=os.path.getmtime)
        
        while len(files) > max_files:
            os.remove(files.pop(0))
