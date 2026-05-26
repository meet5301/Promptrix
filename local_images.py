"""
Local image generation — pure SVG data URIs, no external APIs.
Seeded per prompt for consistent, unique visuals across hero/cards/gallery/team.
"""

from __future__ import annotations

import base64
import html as html_module
import math
import re
from typing import Dict, List, Tuple


SITE_SHAPES = {
    "ecommerce": ["bag", "star", "box", "tag"],
    "restaurant": ["plate", "fork", "cup", "leaf"],
    "portfolio": ["brush", "grid", "frame", "spark"],
    "saas": ["chart", "bolt", "cloud", "code"],
    "gym": ["dumbbell", "heart", "flame", "target"],
    "blog": ["pen", "book", "quote", "paper"],
    "travel": ["plane", "mountain", "compass", "sun"],
    "hospital": ["cross", "heart", "shield", "pulse"],
    "education": ["book", "cap", "bulb", "board"],
    "realestate": ["house", "key", "door", "tree"],
    "agency": ["rocket", "target", "star", "chart"],
    "default": ["circle", "diamond", "wave", "hex"],
}


def _hue(seed: int, offset: int = 0) -> int:
    return (seed + offset * 47) % 360


def _safe_label(text: str) -> str:
    clean = re.sub(r"[^\w\s\-&]", "", (text or "")[:24])
    return html_module.escape(clean.strip() or "Image")


def _svg_uri(svg: str) -> str:
    """Base64 data URI — works reliably in img src and CSS background (no # fragment issues)."""
    raw = svg.strip().encode("utf-8")
    return "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")


def _gradients(primary: str, accent: str, secondary: str, seed: int) -> Tuple[str, str]:
    h1, h2, h3 = _hue(seed), _hue(seed, 3), _hue(seed, 7)
    g1 = f"linear-gradient(135deg,{primary},{secondary})"
    g2 = f"radial-gradient(circle at 30% 20%,{accent}55,transparent 55%),linear-gradient({h1}deg,{primary},{accent})"
    return g1, g2


def _shape_svg(shape: str, cx: float, cy: float, size: float, fill: str, opacity: float = 0.35) -> str:
    if shape == "circle":
        return f'<circle cx="{cx}" cy="{cy}" r="{size}" fill="{fill}" opacity="{opacity}"/>'
    if shape == "diamond":
        s = size * 1.2
        return (
            f'<polygon points="{cx},{cy-s} {cx+s},{cy} {cx},{cy+s} {cx-s},{cy}" '
            f'fill="{fill}" opacity="{opacity}"/>'
        )
    if shape == "hex":
        pts = []
        for i in range(6):
            ang = math.pi / 3 * i - math.pi / 6
            pts.append(f"{cx + size * math.cos(ang)},{cy + size * math.sin(ang)}")
        return f'<polygon points="{" ".join(pts)}" fill="{fill}" opacity="{opacity}"/>'
    if shape in ("plate", "cup"):
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{size*1.3}" ry="{size*0.8}" fill="{fill}" opacity="{opacity}"/>'
    if shape in ("mountain", "wave"):
        return (
            f'<path d="M{cx-size*2},{cy+size} L{cx},{cy-size} L{cx+size*2},{cy+size} Z" '
            f'fill="{fill}" opacity="{opacity}"/>'
        )
    return f'<rect x="{cx-size}" y="{cy-size}" width="{size*2}" height="{size*2}" rx="{size*0.2}" fill="{fill}" opacity="{opacity}"/>'


class LocalImageGenerator:
    """Generate rich SVG placeholders from site colors + seed."""

    def __init__(self, seed: int, site_type: str, colors: Dict[str, str], image_style: str = "abstract"):
        self.seed = seed
        self.site_type = site_type
        self.colors = colors
        self.image_style = (image_style or "abstract").lower()
        self.primary = colors.get("primary", "#2563eb")
        self.accent = colors.get("accent", "#f59e0b")
        self.secondary = colors.get("secondary", "#1e40af")
        self.shapes = SITE_SHAPES.get(site_type, SITE_SHAPES["default"])

    def _gradient_svg(self, width: int, height: int, idx: int = 0) -> str:
        h = _hue(self.seed, idx)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <defs>
                <linearGradient id="g{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{self.primary}"/>
                    <stop offset="50%" stop-color="{self.secondary}"/>
                    <stop offset="100%" stop-color="{self.accent}"/>
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#g{idx})"/>
        </svg>"""
        return _svg_uri(svg)

    def _pick(self, idx: int, options: List[str]) -> str:
        return options[(self.seed + idx * 13) % len(options)]

    def hero_background(self, width: int = 1920, height: int = 1080) -> str:
        if self.image_style in ("gradient", "none"):
            return self._gradient_svg(width, height, 0) if self.image_style != "none" else ""
        idx = self.seed % 997
        shapes = self.shapes
        decor = ""
        for i in range(8):
            x = (idx * (i + 3) * 17) % width
            y = (idx * (i + 5) * 23) % height
            size = 40 + (idx + i * 11) % 120
            shape = shapes[i % len(shapes)]
            fill = self.accent if i % 2 else self.secondary
            decor += _shape_svg(shape, x, y, size, fill, 0.18 + (i % 3) * 0.08)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <defs>
                <linearGradient id="hg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{self.primary}"/>
                    <stop offset="55%" stop-color="{self.secondary}"/>
                    <stop offset="100%" stop-color="{self.accent}"/>
                </linearGradient>
                <radialGradient id="glow" cx="70%" cy="20%" r="50%">
                    <stop offset="0%" stop-color="{self.accent}" stop-opacity="0.45"/>
                    <stop offset="100%" stop-color="{self.primary}" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#hg)"/>
            <rect width="100%" height="100%" fill="url(#glow)"/>
            {decor}
            <rect width="100%" height="100%" fill="url(#hg)" opacity="0.15"/>
        </svg>"""
        return _svg_uri(svg)

    def card_image(self, idx: int, width: int = 600, height: int = 400, label: str = "") -> str:
        if self.image_style == "gradient":
            return self._gradient_svg(width, height, idx + 1)
        if self.image_style == "none":
            return ""
        shape = self._pick(idx, self.shapes)
        hue_shift = _hue(self.seed, idx)
        bg = self.primary if idx % 2 == 0 else self.secondary
        accent = self.accent
        label_text = _safe_label(label if label else f"Image {idx + 1}")
        decor = _shape_svg(shape, width * 0.72, height * 0.38, min(width, height) * 0.18, accent, 0.55)
        decor += _shape_svg("circle", width * 0.25, height * 0.7, min(width, height) * 0.12, "#ffffff", 0.12)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <defs>
                <linearGradient id="cg{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{bg}"/>
                    <stop offset="100%" stop-color="{accent}"/>
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#cg{idx})"/>
            <rect x="0" y="{height*0.55}" width="100%" height="{height*0.45}" fill="#000" opacity="0.18"/>
            {decor}
            <text x="24" y="{height-24}" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" opacity="0.92">{label_text}</text>
            <text x="24" y="34" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="13" opacity="0.65">#{hue_shift}</text>
        </svg>"""
        return _svg_uri(svg)

    def portrait(self, idx: int, name: str = "", size: int = 240) -> str:
        initials = "".join(w[0].upper() for w in (name or f"Member {idx+1}").split()[:2]) or "PX"
        bg = self.secondary if idx % 2 else self.primary
        ring = self.accent
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <defs>
                <linearGradient id="pg{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{bg}"/>
                    <stop offset="100%" stop-color="{self.accent}"/>
                </linearGradient>
            </defs>
            <circle cx="{size/2}" cy="{size/2}" r="{size/2-4}" fill="url(#pg{idx})"/>
            <circle cx="{size/2}" cy="{size/2}" r="{size/2-8}" fill="none" stroke="{ring}" stroke-width="4" opacity="0.85"/>
            <text x="50%" y="54%" text-anchor="middle" fill="#fff" font-family="Segoe UI,sans-serif" font-size="{size//3}" font-weight="800">{initials}</text>
        </svg>"""
        return _svg_uri(svg)

    def feature_icon(self, idx: int, size: int = 64) -> str:
        shape = self._pick(idx, self.shapes)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <rect width="100%" height="100%" rx="16" fill="{self.primary}22"/>
            {_shape_svg(shape, size/2, size/2, size/4, self.primary, 0.95)}
        </svg>"""
        return _svg_uri(svg)

    def gallery_tile(self, idx: int, width: int = 400, height: int = 300) -> str:
        return self.card_image(idx + 50, width, height, f"Gallery {idx + 1}")

    def container_banner(self, idx: int, width: int = 480, height: int = 160) -> str:
        return self.card_image(idx + 100, width, height, f"Block {idx + 1}")
