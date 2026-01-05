"""
Oracle Theme Engine: The Aesthetic Core.
Defines the visual styles for the Oracle AI Assistant.
"""

class OracleThemes:
    CLASSIC = {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "accent": "#007acc",
        "text_color": "#00ff00",
        "font": ("Segoe UI", 10),
        "transparency": 1.0
    }
    
    CYBER_GLITCH = {
        "bg": "#000000",
        "fg": "#00ff41",
        "accent": "#ff003c",
        "text_color": "#00ff41",
        "font": ("Consolas", 10),
        "transparency": 0.9
    }
    
    ELECTRIC_SHIMMER = {
        "bg": "#0a0a1a",
        "fg": "#e0e0ff",
        "accent": "#00d4ff",
        "text_color": "#00d4ff",
        "font": ("Segoe UI Light", 10),
        "transparency": 0.85,
        "shimmer": True
    }

    @staticmethod
    def get_theme(name):
        themes = {
            "Classic": OracleThemes.CLASSIC,
            "Cyber-Glitch": OracleThemes.CYBER_GLITCH,
            "Electric Shimmer": OracleThemes.ELECTRIC_SHIMMER
        }
        return themes.get(name, OracleThemes.CLASSIC)
