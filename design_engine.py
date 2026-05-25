"""
Design Suggestion Engine - Color Harmony, Typography, Dark Mode
Pure Python - NO external APIs
"""

import colorsys
import json
from typing import Dict, List, Tuple, Optional

class DesignAnalyzer:
    """Analyze and suggest design improvements"""
    
    def __init__(self):
        self.font_pairs = self._load_font_pairs()
        self.color_theory = ColorTheory()
    
    def _load_font_pairs(self) -> Dict[str, List[Tuple[str, str]]]:
        """Pre-built proven font pairings"""
        return {
            "modern": [
                ("Poppins", "Inter"),
                ("Montserrat", "Lato"),
                ("Raleway", "Open Sans"),
            ],
            "elegant": [
                ("Playfair Display", "Lora"),
                ("Cormorant Garamond", "Merriweather"),
                ("Georgia", "Segoe UI"),
            ],
            "playful": [
                ("Comic Sans MS", "Trebuchet MS"),
                ("Fredoka", "Nunito"),
                ("Quicksand", "Chivo"),
            ],
            "tech": [
                ("IBM Plex Mono", "IBM Plex Sans"),
                ("JetBrains Mono", "Fira Sans"),
                ("Courier Prime", "Space Mono"),
            ],
        }
    
    def analyze_design(self, config: Dict) -> Dict:
        """Analyze design and return suggestions"""
        colors = config.get("colors", {})
        suggestions = []
        
        # Color harmony check
        if colors.get("primary"):
            harmony = self.color_theory.check_harmony(
                colors.get("primary"),
                colors.get("secondary"),
                colors.get("accent"),
            )
            suggestions.append({
                "type": "color_harmony",
                "score": harmony["score"],
                "message": harmony["message"],
                "fix": harmony.get("suggested"),
            })
        
        # Contrast check
        contrast = self.color_theory.check_contrast(
            colors.get("primary", "#2563eb"),
            colors.get("bg", "#ffffff"),
        )
        suggestions.append({
            "type": "contrast",
            "score": contrast["score"],
            "message": contrast["message"],
        })
        
        # Typography suggestions
        vibe = config.get("vibe", "modern")
        fonts = self.suggest_fonts(vibe)
        suggestions.append({
            "type": "typography",
            "message": f"Suggested fonts for {vibe} vibe",
            "suggestions": fonts,
        })
        
        return {
            "suggestions": suggestions,
            "overall_score": self._calculate_score(suggestions),
        }
    
    def suggest_fonts(self, vibe: str) -> List[Tuple[str, str]]:
        """Suggest font pairings based on vibe"""
        return self.font_pairs.get(vibe, self.font_pairs["modern"])
    
    def _calculate_score(self, suggestions: List[Dict]) -> float:
        """Calculate overall design score"""
        scores = [s.get("score", 1.0) for s in suggestions if "score" in s]
        return sum(scores) / max(len(scores), 1) if scores else 0.8
    
    def generate_dark_mode(self, colors: Dict) -> Dict:
        """Generate dark mode variant from light colors"""
        primary = colors.get("primary", "#2563eb")
        secondary = colors.get("secondary", "#1a202c")
        
        # Invert and adjust colors for dark theme
        dark_primary = self._lighten_color(primary, 0.3)
        dark_bg = "#0f172a"
        dark_text = "#f1f5f9"
        
        return {
            "primary": dark_primary,
            "secondary": secondary,
            "bg": dark_bg,
            "text": dark_text,
            "border": "#1e293b",
        }
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a color for dark mode"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        v = min(1, v + factor)  # Increase brightness
        r, g, b = colorsys.hsv_to_rgb(h, max(0, s - 0.2), v)
        
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


class ColorTheory:
    """Color theory and harmony algorithms"""
    
    def check_harmony(self, primary: str, secondary: str, accent: str) -> Dict:
        """Check if colors are harmonious"""
        p_hue = self._hex_to_hue(primary)
        s_hue = self._hex_to_hue(secondary)
        a_hue = self._hex_to_hue(accent)
        
        # Check complementary (opposite on color wheel)
        diff_ps = abs(p_hue - s_hue)
        diff_pa = abs(p_hue - a_hue)
        
        score = 1.0
        message = "✓ Colors are harmonious"
        suggested = None
        
        # Score based on hue difference
        if 120 <= diff_ps <= 180 or 180 <= diff_ps <= 240:
            score = 0.9
            message = "Excellent color harmony (complementary)"
        elif 30 <= diff_ps <= 90:
            score = 0.7
            message = "Good color harmony (analogous)"
        else:
            score = 0.5
            message = "⚠️ Consider adjusting secondary color for better harmony"
            suggested = self._suggest_harmonic_color(p_hue)
        
        return {
            "score": score,
            "message": message,
            "suggested": suggested,
        }
    
    def check_contrast(self, foreground: str, background: str) -> Dict:
        """Check WCAG contrast ratio"""
        fg_lum = self._get_luminance(foreground)
        bg_lum = self._get_luminance(background)
        
        ratio = (max(fg_lum, bg_lum) + 0.05) / (min(fg_lum, bg_lum) + 0.05)
        
        # WCAG standards
        score = 1.0
        if ratio >= 7:
            level = "AAA (Enhanced)"
            score = 1.0
        elif ratio >= 4.5:
            level = "AA (Standard)"
            score = 0.9
        else:
            level = "Fail"
            score = 0.5
        
        return {
            "score": score,
            "ratio": round(ratio, 2),
            "level": level,
            "message": f"Contrast ratio: {ratio:.2f}:1 - {level}",
        }
    
    def _hex_to_hue(self, hex_color: str) -> float:
        """Convert hex to hue (0-360)"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        return h * 360
    
    def _get_luminance(self, hex_color: str) -> float:
        """Get relative luminance for WCAG"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Normalize
        r, g, b = r/255, g/255, b/255
        
        # Apply gamma correction
        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
        
        return 0.2126*r + 0.7152*g + 0.0722*b
    
    def _suggest_harmonic_color(self, base_hue: float) -> str:
        """Suggest a complementary color"""
        # Add 180 degrees for true complement
        complementary_hue = (base_hue + 180) % 360
        h, s, v = complementary_hue/360, 0.7, 0.8
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


class AccessibilityChecker:
    """WCAG 2.1 Level AA/AAA compliance checker"""
    
    def check_site_accessibility(self, html: str) -> Dict:
        """Check HTML for accessibility issues"""
        issues = []
        score = 100
        
        # Check for alt text on images
        import re
        img_tags = re.findall(r'<img[^>]*>', html)
        for img in img_tags:
            if 'alt=' not in img:
                issues.append({
                    "level": "error",
                    "type": "missing_alt_text",
                    "message": "Images must have alt text for screen readers",
                    "fix": 'Add alt="description" to image tags',
                })
                score -= 10
        
        # Check for heading hierarchy
        h1_count = len(re.findall(r'<h1[^>]*>', html))
        if h1_count == 0:
            issues.append({
                "level": "error",
                "type": "missing_h1",
                "message": "Page should have exactly one H1",
                "fix": "Add a main heading (H1) to the page",
            })
            score -= 15
        elif h1_count > 1:
            issues.append({
                "level": "warning",
                "type": "multiple_h1",
                "message": "Page should have only one H1",
                "fix": "Use H2-H6 for subheadings instead",
            })
            score -= 5
        
        # Check for color contrast
        if 'color:' in html and 'background:' in html:
            issues.append({
                "level": "info",
                "type": "manual_contrast_check",
                "message": "Manually verify color contrast meets WCAG AA",
                "fix": "Use contrast checker tool for inline colors",
            })
        
        # Check for form labels
        input_tags = re.findall(r'<input[^>]*>', html)
        label_tags = re.findall(r'<label[^>]*>', html)
        if len(input_tags) > len(label_tags):
            issues.append({
                "level": "warning",
                "type": "missing_labels",
                "message": "Form inputs should have associated labels",
                "fix": "<label for='input-id'>Label</label>",
            })
            score -= 10
        
        # Check for lang attribute
        if '<html' in html and 'lang=' not in html:
            issues.append({
                "level": "warning",
                "type": "missing_lang",
                "message": "HTML should have lang attribute",
                "fix": '<html lang="en">',
            })
            score -= 5
        
        return {
            "score": max(0, score),
            "level": "AAA" if score >= 90 else "AA" if score >= 70 else "Failed",
            "issues": issues,
            "summary": f"Found {len(issues)} accessibility issues",
        }


def get_design_suggestions(config: Dict) -> Dict:
    """Public API: Get design suggestions"""
    analyzer = DesignAnalyzer()
    
    suggestions = analyzer.analyze_design(config)
    
    # Add dark mode variant
    dark_variant = analyzer.generate_dark_mode(config.get("colors", {}))
    suggestions["dark_mode"] = dark_variant
    
    return suggestions


def check_accessibility(html: str) -> Dict:
    """Public API: Check accessibility"""
    checker = AccessibilityChecker()
    return checker.check_site_accessibility(html)
