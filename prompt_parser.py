"""
Parse free-text user prompts into structured site generation config.
Every prompt → unique colors, layout, pages, sections, images.
"""

import re
import hashlib
from typing import Any, Dict, List, Optional, Tuple

NAMED_COLORS = {
    "navy": "#0f172a", "dark navy": "#0a1628", "midnight": "#0f172a",
    "blue": "#2563eb", "royal blue": "#1d4ed8", "sky": "#0ea5e9", "ocean": "#0369a1",
    "teal": "#0d9488", "cyan": "#06b6d4", "turquoise": "#14b8a6",
    "green": "#16a34a", "lime": "#84cc16", "emerald": "#059669",
    "gold": "#d4af37", "yellow": "#eab308", "amber": "#f59e0b", "orange": "#ea580c",
    "red": "#dc2626", "crimson": "#b91c1c", "rose": "#e11d48", "pink": "#ec4899",
    "purple": "#7c3aed", "violet": "#8b5cf6", "indigo": "#4f46e5",
    "black": "#0a0a0a", "charcoal": "#1e293b", "gray": "#64748b", "grey": "#64748b",
    "white": "#ffffff", "cream": "#fef3c7", "beige": "#f5f0e8", "ivory": "#fffff0",
    "terracotta": "#c2410c", "brown": "#78350f", "wine": "#7f1d1d", "maroon": "#881337",
    "coral": "#fb7185", "peach": "#fdba74", "mint": "#6ee7b7", "silver": "#c0c0c0",
}

COLOR_NAMES_PATTERN = "|".join(re.escape(k) for k in sorted(NAMED_COLORS.keys(), key=len, reverse=True))

SITE_TYPE_PATTERNS = [
    (r"e[\-\s]?commerce|online\s+store|shop|sneaker|fashion\s+store|product", "ecommerce"),
    (r"restaurant|food\s+blog|cafe|bakery|menu|dining|italian|kitchen", "restaurant"),
    (r"portfolio|designer|ui[\s/]?ux|creative\s+agency|freelanc", "portfolio"),
    (r"saas|software|landing\s+page|startup|app\s+tool|project\s+management", "saas"),
    (r"gym|fitness|yoga|workout|trainer", "gym"),
    (r"blog|magazine|article|newsletter", "blog"),
    (r"travel|tour|destination|vacation|agency", "travel"),
    (r"hospital|clinic|doctor|medical|healthcare", "hospital"),
    (r"education|course|school|learning|coaching", "education"),
    (r"real\s*estate|property|realtor|housing", "realestate"),
    (r"agency|digital\s+marketing|consulting", "agency"),
]

SECTION_KEYWORDS = {
    "products": r"(?:our\s+)?products?\b|online\s+store|shopping\s+cart|sneaker|merchandise|add\s+to\s+cart",
    "menu": r"\bmenu\b|menu\s+item|menu\s+card|dishes|food\s+card|cuisine|restaurant\s+menu",
    "gallery": r"gallery|photo|image\s+grid|showcase|slideshow",
    "pricing": r"pricing|price\s+tier|plan|subscription|₹|\$",
    "testimonials": r"testimonial|review|client\s+say|feedback",
    "team": r"team\s+member|staff|trainer|doctor|chef",
    "faq": r"\bfaq\b|frequently\s+asked",
    "stats": r"stat|counter|number|milestone",
    "features": r"feature|benefit|why\s+choose|service\s+card",
    "containers": r"container|containers|content\s+block|section[s]?\s+\d",
    "cta": r"cta|call\s+to\s+action|sign\s+up|book\s+now",
    "contact": r"contact|appointment|booking|form",
    "newsletter": r"newsletter|subscribe|email\s+list",
    "courses": r"course|lesson|curriculum",
    "packages": r"package|destination|trip",
}

PAGE_ALIASES = {
    "home": "home", "index": "home", "main": "home",
    "shop": "shop", "store": "shop", "products": "shop",
    "menu": "menu", "gallery": "gallery",
    "about": "about", "team": "team", "work": "work", "portfolio": "work",
    "services": "services", "classes": "classes",
    "pricing": "pricing", "plans": "pricing",
    "faq": "faq", "blog": "blog", "articles": "blog",
    "contact": "contact", "booking": "contact",
    "doctors": "doctors", "courses": "courses", "packages": "packages",
}

IMAGE_TOPICS = {
    "ecommerce": "shopping,fashion,product",
    "restaurant": "restaurant,food,dining",
    "portfolio": "design,creative,workspace",
    "saas": "technology,office,startup",
    "gym": "fitness,gym,workout",
    "blog": "writing,desk,laptop",
    "travel": "travel,landscape,adventure",
    "hospital": "hospital,medical,healthcare",
    "education": "education,classroom,books",
    "realestate": "architecture,house,interior",
    "agency": "business,team,office",
    "default": "abstract,texture,color",
}


def _prompt_hash(prompt: str) -> int:
    return int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_light(hex_color: str) -> bool:
    r, g, b = _hex_to_rgb(hex_color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance > 0.55


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    s /= 100
    l /= 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return "#{:02x}{:02x}{:02x}".format(
        int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
    )


def _palette_from_seed(seed: int) -> Tuple[str, str, str]:
    """Unique primary/accent/secondary per prompt hash."""
    h1 = seed % 360
    h2 = (seed * 7) % 360
    h3 = (seed * 13) % 360
    return (
        _hsl_to_hex(h1, 68, 42),
        _hsl_to_hex(h2, 75, 52),
        _hsl_to_hex(h3, 55, 35),
    )


def _find_color_word(text: str, group: int = 1) -> Optional[str]:
    m = re.search(rf"\b({COLOR_NAMES_PATTERN})\b", text, re.I)
    if m:
        name = m.group(1).lower()
        return NAMED_COLORS.get(name)
    return None


def _parse_color_role(lower: str, role: str) -> Optional[str]:
    """e.g. 'red background', 'background color red', 'header is blue'."""
    patterns = [
        rf"\b({COLOR_NAMES_PATTERN})\s+{role}\b",
        rf"{role}\s+(?:color|bg|background)?\s*(?:is|=|:)?\s*({COLOR_NAMES_PATTERN})\b",
        rf"{role}\s*[:=]\s*({COLOR_NAMES_PATTERN})\b",
        rf"{role}\s*[:=]\s*(#[0-9a-fA-F]{{3,8}})",
    ]
    for pat in patterns:
        m = re.search(pat, lower, re.I)
        if m:
            val = m.group(1)
            if val.startswith("#"):
                return val
            return NAMED_COLORS.get(val.lower())
    return None


def _build_color_palette(text: str, site_type: str, seed: int) -> Dict[str, Any]:
    lower = text.lower()
    hexes = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", text)

    roles: Dict[str, Optional[str]] = {
        "background": _parse_color_role(lower, "background") or _parse_color_role(lower, "bg"),
        "header": _parse_color_role(lower, "header") or _parse_color_role(lower, "navbar"),
        "footer": _parse_color_role(lower, "footer"),
        "primary": _parse_color_role(lower, "primary") or _parse_color_role(lower, "main"),
        "accent": None,
    }

    # "red color" / "color red" / "theme red"
    if not roles["primary"]:
        m = re.search(
            rf"(?:theme|color|colour)\s+(?:is\s+)?({COLOR_NAMES_PATTERN})\b|"
            rf"\b({COLOR_NAMES_PATTERN})\s+(?:color|colour|theme)\b",
            lower, re.I,
        )
        if m:
            roles["primary"] = NAMED_COLORS.get((m.group(1) or m.group(2)).lower())

    combo = re.search(
        rf"\b({COLOR_NAMES_PATTERN})\s+and\s+({COLOR_NAMES_PATTERN})\s+theme",
        lower,
    )
    if combo:
        roles["primary"] = NAMED_COLORS.get(combo.group(1).lower())
        roles["background"] = NAMED_COLORS.get(combo.group(2).lower())

    cm = re.search(rf"\b({COLOR_NAMES_PATTERN})\s+colou?r\b", lower)
    if cm and not roles["primary"]:
        roles["primary"] = NAMED_COLORS.get(cm.group(1).lower())

    # First color word in prompt often is the main color user wants
    if not roles["primary"] and not roles["background"]:
        first_color = _find_color_word(lower)
        if first_color:
            if re.search(r"\b(background|bg)\b", lower):
                roles["background"] = first_color
            else:
                roles["primary"] = first_color

    accent_match = re.search(
        rf"(?:({COLOR_NAMES_PATTERN})\s+accent|accent\s+(?:color\s*)?[:=]?\s*({COLOR_NAMES_PATTERN}))",
        lower, re.I,
    )
    if accent_match:
        an = (accent_match.group(1) or accent_match.group(2)).lower()
        roles["accent"] = NAMED_COLORS.get(an)

    if hexes:
        if not roles["primary"]:
            roles["primary"] = hexes[0]
        if len(hexes) > 1 and not roles["accent"]:
            roles["accent"] = hexes[1]

    p_seed, a_seed, s_seed = _palette_from_seed(seed)
    primary = roles.get("primary") or p_seed
    accent = roles.get("accent") or a_seed
    secondary = roles.get("secondary") or s_seed

    # Background: "red background", "red color background", "background green"
    background = roles["background"]
    for pat in [
        rf"\b({COLOR_NAMES_PATTERN})\s+(?:color\s+)?background\b",
        rf"\b({COLOR_NAMES_PATTERN})\s+back(?:ground)?\b",
        rf"background\s+(?:color\s+)?(?:is\s+)?({COLOR_NAMES_PATTERN})\b",
        rf"bg\s+(?:color\s+)?({COLOR_NAMES_PATTERN})\b",
    ]:
        m = re.search(pat, lower)
        if m:
            background = NAMED_COLORS.get(m.group(1).lower())
            break
    if not background:
        if re.search(r"\bwhite\s+background\b|\bwhite\s+theme\b|light\s+theme|minimal\s+white", lower):
            background = "#ffffff"
        elif re.search(r"\bdark\b|\bblack\s+back|\bcharcoal\b|\bmidnight\b", lower):
            background = "#0f172a"
        else:
            # Tinted page bg from primary (unique per prompt)
            background = _hsl_to_hex(seed % 360, 25, 96 if not re.search(r"\bdark\b", lower) else 12)

    if background and primary == p_seed and not roles.get("primary"):
        if _is_light(background):
            primary = _hsl_to_hex((seed + 120) % 360, 68, 42)
        else:
            primary = _hsl_to_hex((seed + 60) % 360, 75, 52)

    header_bg = roles["header"] or (
        primary if re.search(r"\b(header|navbar)\b.*\b(same|match|primary)\b", lower) else None
    )
    footer_bg = roles["footer"] or (
        primary if re.search(r"\bfooter\b.*\b(same|match|primary|red|blue|green)\b", lower) else None
    )

    if not header_bg:
        hm = re.search(rf"\b({COLOR_NAMES_PATTERN})\s+header\b", lower)
        if hm:
            header_bg = NAMED_COLORS.get(hm.group(1).lower())
        elif _is_light(background):
            header_bg = primary if re.search(r"\bcolou?red\s+header\b", lower) else "#ffffff"
        else:
            header_bg = primary

    if not footer_bg:
        fm = re.search(rf"\b({COLOR_NAMES_PATTERN})\s+footer\b", lower)
        if fm:
            footer_bg = NAMED_COLORS.get(fm.group(1).lower())
        else:
            footer_bg = primary if re.search(r"\bcolou?red\s+footer\b|\bfooter\b", lower) else secondary

    text_on_bg = "#0f172a" if _is_light(background) else "#f8fafc"
    header_text = "#ffffff" if not _is_light(header_bg) else primary
    footer_text = "#ffffff" if not _is_light(footer_bg) else "#0f172a"
    surface = _hsl_to_hex((seed + 40) % 360, 30, 92 if _is_light(background) else 18)
    muted = "#64748b" if _is_light(background) else "#94a3b8"

    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "background": background,
        "header_bg": header_bg,
        "footer_bg": footer_bg,
        "text": text_on_bg,
        "header_text": header_text,
        "footer_text": footer_text,
        "muted": muted,
        "surface": surface,
        "is_dark": not _is_light(background),
        "card_bg": "#ffffff" if _is_light(background) else "#1e293b",
    }


def _detect_site_type(text: str) -> str:
    lower = text.lower()
    for pattern, site_type in SITE_TYPE_PATTERNS:
        if re.search(pattern, lower):
            return site_type
    return "default"


def _detect_sections(text: str, site_type: str) -> List[str]:
    """Only sections user asked for — no heavy preset stacking."""
    lower = text.lower()
    sections: List[str] = []

    if re.search(r"\bhero\b", lower) or re.search(
        r"website|landing|homepage|site\s+for", lower
    ):
        sections.append("hero")

    is_restaurant = site_type == "restaurant" or re.search(r"restaurant|cafe|food|dining|menu", lower)

    for section, pattern in SECTION_KEYWORDS.items():
        if section == "containers" and re.search(pattern, lower):
            sections.append("containers")
        elif section != "containers" and re.search(pattern, lower):
            if section == "products" and is_restaurant and not re.search(
                r"\bproducts?\b|shop|store|cart|merchandise|e[\-\s]?commerce", lower
            ):
                continue
            if section not in sections:
                sections.append(section)

    # Multi-page / generic site → at least hero + content
    if not sections:
        sections = ["hero", "containers", "contact"]
    elif sections == ["hero"]:
        if re.search(r"container|section|content|card", lower):
            sections.append("containers")
        else:
            sections.append("features")
    if re.search(r"contact|footer|form|reach", lower) and "contact" not in sections:
        sections.append("contact")
    if re.search(r"\bcta\b|call\s+to\s+action|get\s+started", lower) and "cta" not in sections:
        sections.append("cta")

    return sections


NAV_PAGE_TO_SECTION = {
    "home": "hero", "index": "hero", "main": "hero",
    "shop": "products", "store": "products", "products": "products",
    "menu": "menu", "gallery": "gallery", "contact": "contact", "booking": "contact",
    "about": "features", "team": "team", "work": "gallery", "portfolio": "gallery",
    "services": "features", "classes": "features", "features": "features",
    "pricing": "pricing", "plans": "pricing", "faq": "faq", "blog": "features",
    "packages": "packages", "courses": "courses", "doctors": "team",
    "articles": "features", "projects": "gallery", "listings": "products",
    "destinations": "packages", "cta": "cta",
}


def _extract_nav_items(text: str, sections: List[str]) -> List[Dict[str, str]]:
    """Build header menu as same-page anchors (not separate HTML files)."""
    lower = text.lower()
    items: List[Dict[str, str]] = []
    seen_ids: set = set()

    def add(label: str, section_id: str) -> None:
        sid = section_id if section_id in sections or section_id == "hero" else (
            "features" if "features" in sections else sections[0] if sections else "hero"
        )
        if sid not in seen_ids:
            seen_ids.add(sid)
            items.append({"label": label.strip(), "id": sid})

    m = re.search(r"pages?\s*[:=]\s*([^\n.]+)", text, re.I)
    if m:
        for part in re.split(r"[,;&|]+", m.group(1)):
            label = part.strip()
            if not label:
                continue
            key = PAGE_ALIASES.get(label.lower(), label.lower().replace(" ", "_"))
            sid = NAV_PAGE_TO_SECTION.get(key, key if key in sections else "features")
            add(label, sid)

    nav_hints = [
        (r"\bmenu\b", "Menu", "menu"),
        (r"\bgallery\b", "Gallery", "gallery"),
        (r"\bshop\b|\bstore\b", "Shop", "products"),
        (r"\babout\b", "About", "features"),
        (r"\bpricing\b|\bplans\b", "Pricing", "pricing"),
        (r"\bcontact\b|\bbooking\b", "Contact", "contact"),
        (r"\bteam\b", "Team", "team"),
        (r"\bservices\b", "Services", "features"),
        (r"\bpackages\b", "Packages", "packages"),
        (r"\bcourses\b", "Courses", "courses"),
        (r"\bfaq\b", "FAQ", "faq"),
    ]
    if not items:
        add("Home", "hero")
        for pattern, label, sid in nav_hints:
            if re.search(pattern, lower) and sid in sections:
                add(label, sid)

    if not items:
        labels = {
            "hero": "Home", "features": "Features", "products": "Shop", "menu": "Menu",
            "gallery": "Gallery", "pricing": "Pricing", "contact": "Contact",
            "team": "Team", "faq": "FAQ", "packages": "Packages", "courses": "Courses",
            "containers": "Sections", "cta": "Get Started",
        }
        for s in sections:
            if s == "cta":
                continue
            add(labels.get(s, s.replace("_", " ").title()), s)

    return items


def _extract_explicit_nav_items(text: str, sections: List[str]) -> List[Dict[str, str]]:
    """Parse exact nav labels from prompt, e.g. header options: Home, Services, Pricing, Contact."""
    patterns = [
        r"(?:header|nav|navbar|menu)\s*(?:options?|items?|links?)\s*[:=]\s*([^\n.]+)",
        r"(?:header|nav|navbar)\s*[:=]\s*([^\n.]+)",
    ]
    raw = ""
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            raw = m.group(1).strip()
            break
    if not raw:
        return []

    items: List[Dict[str, str]] = []
    seen: set = set()
    for token in re.split(r"[,;|>]+", raw):
        label = token.strip(" -")
        if not label:
            continue
        key = PAGE_ALIASES.get(label.lower(), label.lower().replace(" ", "_"))
        sid = NAV_PAGE_TO_SECTION.get(key, key if key in sections else key)
        if sid in seen:
            continue
        seen.add(sid)
        items.append({"label": label[:24], "id": sid})
    return items


def _extract_pages(text: str) -> List[str]:
    """Always single-page — one index.html only."""
    return ["home"]


def _parse_counts(text: str) -> Dict[str, int]:
    """Extract per-section counts from prompt — e.g. 8 menu items, 4 containers, 5 nav links."""
    lower = text.lower()
    counts: Dict[str, int] = {}

    patterns = [
        (r"(\d+)\s*container", "containers"),
        (r"(\d+)\s*content\s+block", "containers"),
        (r"(\d+)\s*section(?:s)?(?!\s+title)", "containers"),
        (r"(\d+)\s*menu\s*(?:item|card)?", "menu"),
        (r"(\d+)\s*product", "products"),
        (r"(\d+)\s*gallery\s*(?:photo|image)?", "gallery"),
        (r"(\d+)\s*team\s*member", "team"),
        (r"(\d+)\s*feature", "features"),
        (r"(\d+)\s*course", "courses"),
        (r"(\d+)\s*package", "packages"),
        (r"(\d+)\s*(?:nav|header|menu)\s*(?:link|option|item|tab)", "nav_links"),
        (r"(\d+)\s*page", "pages"),
    ]
    for pat, key in patterns:
        m = re.search(pat, lower)
        if m:
            counts[key] = max(2, min(int(m.group(1)), 12))

    generic = re.search(
        r"(\d+)\s*(product|item|card|menu|class|course|package|container|section|block)",
        lower,
    )
    if generic and "containers" not in counts:
        counts.setdefault("items", int(generic.group(1)))

    return counts


def _parse_layout(text: str, seed: int, site_type: str = "default") -> Dict[str, Any]:
    lower = text.lower()
    counts = _parse_counts(text)
    container_count = counts.get("containers", counts.get("items", 0))

    rich_types = {"restaurant", "portfolio", "travel", "ecommerce", "gym", "realestate", "agency"}
    use_bg_image = bool(re.search(
        r"background\w*\s+image|bg\s+image|hero\s+image|banner\s+image|"
        r"with\s+image|with\s+images|photo|full[\s-]?width\s+image|"
        r"rich|premium|visual|showcase",
        lower,
    ))
    if not use_bg_image and site_type in rich_types:
        use_bg_image = True
    if re.search(r"no\s+image|without\s+image|solid\s+color\s+only|no\s+background\s+image", lower):
        use_bg_image = False
    if re.search(r"gradient\s+only|gradient\s+background|gradient\s+theme", lower):
        use_bg_image = False

    use_gradient = bool(re.search(r"gradient", lower))
    use_images = "no image" not in lower and "without image" not in lower

    themes = ["rounded", "sharp", "glass", "minimal", "premium", "bold"]
    layout_theme = themes[seed % len(themes)]
    if re.search(r"\bglass\b|glassmorphism|frosted", lower):
        layout_theme = "glass"
    elif re.search(r"\bminimal\b|clean|simple", lower):
        layout_theme = "minimal"
    elif re.search(r"\bsharp\b|square|brutal", lower):
        layout_theme = "sharp"
    elif re.search(r"\bpremium\b|luxury|upscale|elegant", lower):
        layout_theme = "premium"
    elif re.search(r"\bbold\b|vibrant|colorful", lower):
        layout_theme = "bold"

    nav_cta = "Get Started"
    cta_m = re.search(r"(?:cta|button)\s*(?:text|label)?\s*[:=]\s*['\"]?([^'\".\n,]+)", text, re.I)
    if cta_m:
        nav_cta = cta_m.group(1).strip()[:30]
    elif re.search(r"book\s+(?:a\s+)?table", lower):
        nav_cta = "Book a Table"
    elif re.search(r"shop\s+now", lower):
        nav_cta = "Shop Now"
    elif re.search(r"contact\s+us", lower):
        nav_cta = "Contact Us"

    return {
        "container_count": max(2, min(container_count, 12)) if container_count else 0,
        "counts": counts,
        "nav_link_count": counts.get("nav_links", 0),
        "show_header": "no header" not in lower,
        "show_footer": "no footer" not in lower,
        "use_bg_image": use_bg_image,
        "use_images": use_images,
        "use_gradient": use_gradient,
        "layout_theme": layout_theme,
        "nav_style": "center" if re.search(r"center(?:ed)?\s+nav|nav\s+center", lower) else "spread",
        "hero_align": "left" if re.search(r"left[\s-]?align|text\s+left|hero\s+left", lower) else "center",
        "nav_cta": nav_cta,
    }


def _enforce_nav_count(nav_items: List[Dict[str, str]], sections: List[str], requested: int) -> List[Dict[str, str]]:
    """Ensure header has exact number of options when user specifies it."""
    if requested <= 0:
        return nav_items

    ordered_sections = [
        ("hero", "Home"),
        ("features", "Features"),
        ("products", "Shop"),
        ("menu", "Menu"),
        ("gallery", "Gallery"),
        ("pricing", "Pricing"),
        ("team", "Team"),
        ("packages", "Packages"),
        ("courses", "Courses"),
        ("faq", "FAQ"),
        ("contact", "Contact"),
        ("containers", "Sections"),
        ("cta", "Get Started"),
    ]

    out: List[Dict[str, str]] = []
    seen: set = set()
    for item in nav_items:
        sid = (item or {}).get("id", "").strip()
        label = (item or {}).get("label", "").strip() or sid.title()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        out.append({"label": label, "id": sid})

    for sid, label in ordered_sections:
        if len(out) >= requested:
            break
        if sid in seen:
            continue
        seen.add(sid)
        out.append({"label": label, "id": sid})

    return out[:requested]


def _extract_brand(prompt: str) -> str:
    text = prompt.strip()
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', text)
    if quoted:
        name = (quoted[0][0] or quoted[0][1]).strip()
        if len(name) <= 40:
            return name

    named = re.search(
        r"(?:for|called|named|brand(?:\s+name)?)\s+['\"]?([A-Z][A-Za-z0-9&'\-\s]{2,35})",
        text,
    )
    if named:
        return named.group(1).strip().strip("'\"")

    first = re.split(r"[.\n]", text)[0].strip()
    first = re.sub(r"^(create|build|make|design|generate)\s+(a|an|me)?\s*", "", first, flags=re.I)
    first = re.sub(
        r"^(modern|premium|creative|simple|beautiful|dynamic|fully|advanced|next[\s-]?level)\s+",
        "",
        first,
        flags=re.I,
    )
    first = re.sub(
        r"^(website|site|landing\s+page|web\s+page|multi[\s-]?page\s+site)\s+(for|about|with)?\s*",
        "",
        first,
        flags=re.I,
    )
    words = first.split()
    stop = {
        "with", "red", "blue", "green", "header", "footer", "hero", "section", "container",
        "background", "image", "color", "theme", "page", "pages", "and", "the", "a", "an",
    }
    brand_words = [w for w in words if w.lower() not in stop][:4]
    brand = " ".join(brand_words) if brand_words else " ".join(words[:3])
    brand = brand.strip(" ,.-")
    return (brand[:50] + "...") if len(brand) > 50 else (brand or "My Website")


def _hero_copy(prompt: str, site_type: str) -> Dict[str, str]:
    brand = _extract_brand(prompt)
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', prompt)
    title = (quoted[0][0] or quoted[0][1]).strip() if quoted else brand
    subtitle = ""
    for sep in [". ", " — ", " - ", "; "]:
        parts = prompt.split(sep, 1)
        if len(parts) > 1 and len(parts[1].strip()) > 15:
            subtitle = parts[1].strip()[:180]
            break
    explicit_title = re.search(r"(?:hero\s+title|title)\s*[:=]\s*['\"]?([^'\n\"]+)", prompt, re.I)
    explicit_subtitle = re.search(r"(?:hero\s+subtitle|subtitle|tagline)\s*[:=]\s*['\"]?([^'\n\"]+)", prompt, re.I)
    explicit_cta = re.search(r"(?:hero\s+cta|cta\s+text|button\s+text|button\s+label)\s*[:=]\s*['\"]?([^'\n\"]+)", prompt, re.I)
    if explicit_title:
        title = explicit_title.group(1).strip()[:90]
    if explicit_subtitle:
        subtitle = explicit_subtitle.group(1).strip()[:180]
    if not subtitle:
        subtitle = f"Custom {site_type.replace('_', ' ')} experience — built exactly from your prompt."
    out = {"hero_title": title, "hero_subtitle": subtitle}
    if explicit_cta:
        out["cta_text"] = explicit_cta.group(1).strip()[:34]
    return out


def _section_titles(prompt: str) -> Dict[str, str]:
    lower = prompt.lower()
    titles = {}
    m = re.search(r"section\s+title[s]?\s*[:=]\s*([^\n]+)", prompt, re.I)
    if m:
        parts = re.split(r"[,|]", m.group(1))
        for i, p in enumerate(parts[:6]):
            titles[f"block_{i}"] = p.strip()
    if re.search(r"\bproduct", lower):
        titles["products"] = "Our Products"
    if re.search(r"\bgallery", lower):
        titles["gallery"] = "Gallery"
    if re.search(r"\bfeature", lower):
        titles["features"] = "Features"
    for sid in ["hero", "menu", "gallery", "pricing", "contact", "team", "faq", "products", "containers"]:
        m2 = re.search(rf"{sid}\s+title\s*[:=]\s*([^\n,|;]+)", prompt, re.I)
        if m2:
            titles[sid] = m2.group(1).strip()[:60]
    return titles


def _parse_list_item(token: str) -> Dict[str, str]:
    """Parse 'SEO - Rank faster' or 'Ads | More leads' into title + description."""
    token = token.strip(" -•\t")
    if not token:
        return {"title": "", "desc": ""}
    for sep in (" - ", " — ", " | ", ": "):
        if sep in token:
            title, desc = token.split(sep, 1)
            return {"title": title.strip()[:80], "desc": desc.strip()[:160]}
    return {"title": token[:80], "desc": ""}


def _extract_section_items(prompt: str) -> Dict[str, List[str]]:
    """Parse custom section list content from prompt lines."""
    cards = _extract_section_cards(prompt)
    out: Dict[str, List[str]] = {}
    for key, items in cards.items():
        out[key] = [i["title"] for i in items if i.get("title")]
    return out


def _extract_section_cards(prompt: str) -> Dict[str, List[Dict[str, str]]]:
    """Parse section lines with optional title + description pairs."""
    section_map = {
        "services": "features",
        "features": "features",
        "feature": "features",
        "menu": "menu",
        "menu items": "menu",
        "products": "products",
        "product": "products",
        "gallery": "gallery",
        "team": "team",
        "faq": "faq",
        "courses": "courses",
        "packages": "packages",
        "testimonials": "testimonials",
    }
    out: Dict[str, List[Dict[str, str]]] = {}
    for line in re.split(r"[\n\r]+", prompt):
        m = re.match(r"\s*([a-zA-Z ]+)\s*:\s*(.+)\s*$", line.strip())
        if not m:
            continue
        key_raw = m.group(1).strip().lower()
        val_raw = m.group(2).strip()
        key = section_map.get(key_raw)
        if not key:
            continue
        tokens = [x.strip(" -•\t") for x in re.split(r"[,|;]+", val_raw) if x.strip(" -•\t")]
        cards = [_parse_list_item(t) for t in tokens if _parse_list_item(t)["title"]]
        if cards:
            out[key] = cards[:12]
    return out


def _extract_pricing_plans(prompt: str) -> List[Dict[str, str]]:
    """Parse pricing: Basic 499, Pro 999/mo, Enterprise Custom"""
    m = re.search(r"pricing\s*:\s*([^\n]+)", prompt, re.I)
    if not m:
        return []
    plans: List[Dict[str, str]] = []
    for part in re.split(r"[,|;]+", m.group(1)):
        part = part.strip()
        if not part:
            continue
        if " - " in part or " — " in part:
            name, price = re.split(r"\s[-—]\s", part, maxsplit=1)
            plans.append({
                "name": name.strip()[:40],
                "price": price.strip()[:24],
                "period": "",
            })
            continue
        pm = re.match(
            r"^(.+?)\s+(?:₹|rs\.?|\$)?\s*(free|custom|[\d,]+(?:\.\d+)?)\s*(?:/\s*(mo|month|yr|year|yearly))?$",
            part,
            re.I,
        )
        if pm:
            price_val = pm.group(2).replace(",", "")
            period = pm.group(3) or ""
            price_display = "Free" if price_val.lower() == "free" else (
                "Custom" if price_val.lower() == "custom" else f"₹{price_val}"
            )
            if period:
                price_display += f"/{period[:2]}"
            plans.append({
                "name": pm.group(1).strip()[:40],
                "price": price_display,
                "period": period,
            })
    return plans[:6]


def _extract_contact_info(prompt: str) -> Dict[str, str]:
    """Parse phone, email, address, whatsapp from prompt."""
    info: Dict[str, str] = {}
    patterns = [
        (r"(?:phone|mobile|call)\s*[:=]\s*([+\d\s\-()]{7,20})", "phone"),
        (r"(?:email|mail)\s*[:=]\s*([\w.+-]+@[\w.-]+\.[a-z]{2,})", "email"),
        (r"(?:whatsapp|wa)\s*[:=]\s*([+\d\s\-()]{7,20})", "whatsapp"),
        (r"(?:address|location)\s*[:=]\s*([^\n]{8,120})", "address"),
    ]
    for pat, key in patterns:
        m = re.search(pat, prompt, re.I)
        if m:
            info[key] = m.group(1).strip()
    return info


def _extract_testimonials(prompt: str) -> List[Dict[str, str]]:
    """Parse testimonials: Rahul - Great service | Neha, CEO - Loved it"""
    cards = _extract_section_cards(prompt).get("testimonials", [])
    if cards:
        out = []
        for c in cards:
            name = c["title"]
            role = ""
            if "," in name:
                name, role = [x.strip() for x in name.split(",", 1)]
            out.append({"name": name, "role": role or "Client", "text": c.get("desc") or "Excellent experience."})
        return out[:8]
    m = re.search(r"testimonials?\s*:\s*([^\n]+)", prompt, re.I)
    if not m:
        return []
    out = []
    for part in re.split(r"[|]+", m.group(1)):
        part = part.strip()
        if not part:
            continue
        if " - " in part or " — " in part:
            left, text = re.split(r"\s[-—]\s", part, maxsplit=1)
        else:
            left, text = part, "Great experience with this brand."
        role = "Client"
        if "," in left:
            left, role = [x.strip() for x in left.split(",", 1)]
        out.append({"name": left.strip()[:40], "role": role[:30], "text": text.strip()[:180]})
    return out[:8]


SECTION_ORDER_ALIASES = {
    "home": "hero", "hero": "hero", "services": "features", "service": "features",
    "features": "features", "shop": "products", "products": "products", "menu": "menu",
    "gallery": "gallery", "pricing": "pricing", "plans": "pricing", "team": "team",
    "faq": "faq", "contact": "contact", "cta": "cta", "testimonials": "testimonials",
    "packages": "packages", "courses": "courses", "containers": "containers", "stats": "stats",
}


def _reorder_sections(sections: List[str], prompt: str) -> List[str]:
    """Apply user section order: order: hero, services, pricing, contact"""
    m = re.search(r"order\s*:\s*([^\n.]+)", prompt, re.I)
    if not m:
        return sections
    ordered: List[str] = []
    seen: set = set()
    for token in re.split(r"[,;|]+", m.group(1)):
        key = token.strip().lower().replace(" ", "_")
        sid = SECTION_ORDER_ALIASES.get(key, key)
        if sid and sid not in seen:
            seen.add(sid)
            ordered.append(sid)
    for s in sections:
        if s not in seen:
            ordered.append(s)
    return ordered


def _parse_typography(prompt: str) -> Dict[str, Any]:
    lower = prompt.lower()
    body_font = "Inter"
    heading_font = ""
    bold_headings = bool(re.search(r"bold\s+head(?:ing)?s?", lower))
    fm = re.search(r"(?:body\s+)?font\s*[:=]\s*([a-zA-Z\s]+)", prompt, re.I)
    if fm:
        body_font = fm.group(1).strip().split(",")[0].strip()
    hm = re.search(r"heading\s+font\s*[:=]\s*([a-zA-Z\s]+)", prompt, re.I)
    if hm:
        heading_font = hm.group(1).strip().split(",")[0].strip()
    font_style = "serif" if re.search(r"elegant|luxury|premium|upscale|playfair|serif", lower) else "sans"
    known = {
        "poppins": "Poppins", "inter": "Inter", "roboto": "Roboto", "montserrat": "Montserrat",
        "lato": "Lato", "open sans": "Open Sans", "playfair": "Playfair Display",
        "raleway": "Raleway", "nunito": "Nunito", "system": "system-ui",
    }
    for k, v in known.items():
        if k in lower and not fm:
            body_font = v
    return {
        "body_font": body_font,
        "heading_font": heading_font or body_font,
        "bold_headings": bold_headings,
        "font_style": font_style,
    }


def _apply_theme_preset(prompt: str, layout: Dict[str, Any], colors: Dict[str, Any]) -> None:
    """Apply bundled theme presets from keywords."""
    lower = prompt.lower()
    presets = [
        (r"apple\s+style|ios\s+style", {"layout_theme": "minimal", "nav_style": "spread"}, {
            "background": "#f5f5f7", "header_bg": "#ffffff", "footer_bg": "#ffffff",
            "primary": "#0071e3", "text": "#1d1d1f",
        }),
        (r"modern\s+saas|startup\s+saas", {"layout_theme": "glass", "use_gradient": True}, {
            "primary": "#2563eb", "accent": "#06b6d4", "background": "#0f172a",
            "header_bg": "#0b1220", "is_dark": True,
        }),
        (r"luxury\s+dark|premium\s+dark", {"layout_theme": "premium", "font_style": "serif"}, {
            "background": "#0a0a0a", "primary": "#d4af37", "accent": "#fbbf24",
            "header_bg": "#111111", "footer_bg": "#111111", "is_dark": True,
        }),
        (r"minimal\s+white|clean\s+white", {"layout_theme": "minimal"}, {
            "background": "#ffffff", "header_bg": "#ffffff", "footer_bg": "#f8fafc",
            "primary": "#0f172a", "accent": "#2563eb",
        }),
    ]
    for pattern, layout_patch, color_patch in presets:
        if re.search(pattern, lower):
            layout.update(layout_patch)
            for k, v in color_patch.items():
                colors[k] = v
            if colors.get("is_dark"):
                colors["text"] = "#f8fafc"
                colors["surface"] = "#1e293b"
                colors["card_bg"] = "#1e293b"
            break


def _parse_animation(prompt: str) -> str:
    lower = prompt.lower()
    if re.search(r"no\s+animation|animation\s*:\s*none|without\s+animation", lower):
        return "none"
    if re.search(r"animation\s*:\s*premium|premium\s+animation|rich\s+animation", lower):
        return "premium"
    if re.search(r"animation\s*:\s*subtle|subtle\s+animation", lower):
        return "subtle"
    return "default"


def _parse_image_style(prompt: str) -> str:
    lower = prompt.lower()
    m = re.search(r"image\s+style\s*:\s*(\w+)", lower)
    if m:
        return m.group(1).strip().lower()
    if re.search(r"gradient\s+only|gradient\s+images?", lower):
        return "gradient"
    if re.search(r"abstract\s+image|abstract\s+style", lower):
        return "abstract"
    if re.search(r"realistic\s+image|photo\s+style", lower):
        return "realistic"
    if re.search(r"no\s+image|without\s+image", lower):
        return "none"
    return "abstract"


def parse_prompt(prompt: str) -> Dict[str, Any]:
    prompt = (prompt or "").strip()
    if not prompt:
        prompt = "Red background, background image, header, footer, 4 containers, hero section. pages: Home, About, Contact"

    seed = _prompt_hash(prompt)
    site_type = _detect_site_type(prompt)
    pages = _extract_pages(prompt)
    sections = _detect_sections(prompt, site_type)
    colors = _build_color_palette(prompt, site_type, seed)
    layout = _parse_layout(prompt, seed, site_type)
    _apply_theme_preset(prompt, layout, colors)

    hero = _hero_copy(prompt, site_type)
    section_titles = _section_titles(prompt)
    section_cards = _extract_section_cards(prompt)
    section_items = _extract_section_items(prompt)
    for key in section_cards.keys():
        if key not in sections:
            sections.append(key)

    pricing_plans = _extract_pricing_plans(prompt)
    if pricing_plans and "pricing" not in sections:
        sections.append("pricing")

    contact_info = _extract_contact_info(prompt)
    if contact_info and "contact" not in sections:
        sections.append("contact")

    testimonials_data = _extract_testimonials(prompt)
    if testimonials_data and "testimonials" not in sections:
        sections.append("testimonials")

    counts = layout.get("counts", {})

    item_count = layout["container_count"] or counts.get("containers") or counts.get("items") or 4
    item_count = max(2, min(item_count, 12))

    nav_items = _extract_explicit_nav_items(prompt, sections) or _extract_nav_items(prompt, sections)
    nav_items = _enforce_nav_count(nav_items, sections, layout.get("nav_link_count", 0))

    for item in nav_items:
        sid = item.get("id", "")
        if sid and sid not in sections and sid != "hero":
            sections.append(sid)

    sections = _reorder_sections(sections, prompt)

    typography = _parse_typography(prompt)
    animation_mode = _parse_animation(prompt)
    image_style = _parse_image_style(prompt)
    use_images = layout.get("use_images", True) and image_style != "none"

    section_counts = {
        "containers": counts.get("containers", item_count),
        "menu": counts.get("menu", item_count),
        "products": counts.get("products", item_count),
        "gallery": counts.get("gallery", min(item_count, 9)),
        "features": counts.get("features", 6),
        "team": counts.get("team", 4),
        "courses": counts.get("courses", item_count),
        "packages": counts.get("packages", item_count),
    }

    return {
        "prompt": prompt,
        "site_type": site_type,
        "brand": _extract_brand(prompt),
        "tagline": hero["hero_subtitle"],
        "pages": pages,
        "nav_items": nav_items,
        "sections": sections,
        "colors": colors,
        "layout": layout,
        "custom_content": {
            **hero,
            "item_count": item_count,
            "section_counts": section_counts,
            "section_titles": section_titles,
            "section_items": section_items,
            "section_cards": section_cards,
            "pricing_plans": pricing_plans,
            "contact_info": contact_info,
            "testimonials": testimonials_data,
            "nav_cta": layout.get("nav_cta", "Get Started"),
        },
        "style": {
            "use_gradient": layout["use_gradient"],
            "use_bg_image": layout["use_bg_image"],
            "use_images": use_images,
            "is_dark": colors.get("is_dark", False),
            "font_style": typography.get("font_style") or (
                "serif" if re.search(r"elegant|luxury|premium|upscale", prompt.lower()) else "sans"
            ),
            "layout_theme": layout["layout_theme"],
            "hero_align": layout["hero_align"],
            "nav_style": layout.get("nav_style", "spread"),
            "body_font": typography.get("body_font", "Inter"),
            "heading_font": typography.get("heading_font", typography.get("body_font", "Inter")),
            "bold_headings": typography.get("bold_headings", False),
            "animation": animation_mode,
            "image_style": image_style,
        },
        "seed": seed,
        "_parsed": True,
        "sections_detected": [s.replace("_", " ").title() for s in sections],
        "color_palette": {
            "primary": colors["primary"],
            "accent": colors["accent"],
            "background": colors["background"],
            "header": colors["header_bg"],
            "footer": colors["footer_bg"],
        },
    }


def config_from_prompt(prompt: str) -> Dict[str, Any]:
    return parse_prompt(prompt)
