"""
Promptrix Local Template Engine v2.0 - NO EXTERNAL APIs
Pure Python rule-based HTML generation
Supports: HTML, React, Vue, TypeScript exports
"""

import re
import html as _html
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
import random

from local_images import LocalImageGenerator

# ──────────────────────────────────────────────────────────────────────────────
# CONTENT LIBRARY (Pre-built copy for all site types)
# ──────────────────────────────────────────────────────────────────────────────

CONTENT_LIBRARY = {
    "ecommerce": {
        "hero_titles": ["Shop the Best", "Discover Your Style", "Premium Shopping Experience", "Everything You Need"],
        "hero_subs": ["Curated products delivered to your doorstep", "Quality meets affordability", "Browse, compare, and save", "Shop thousands of verified sellers"],
        "cta_texts": ["Shop Now", "Browse Collection", "Explore Products", "Start Shopping"],
        "features": [
            ("Free Shipping", "On orders above ₹500"),
            ("Easy Returns", "30-day return policy"),
            ("Secure Payment", "256-bit encryption"),
            ("24/7 Support", "Chat, email, phone"),
            ("Genuine Products", "100% authentic"),
            ("Fast Delivery", "2-3 business days"),
        ],
        "product_names": ["Premium Headphones", "Smartwatch Pro", "Wireless Charger", "USB-C Cable", "Phone Case", "Screen Protector"],
    },
    "restaurant": {
        "hero_titles": ["Taste the Difference", "Culinary Excellence", "Farm to Table", "Signature Flavors"],
        "hero_subs": ["Authentic cuisine made with passion", "Fresh ingredients, time-tested recipes", "Award-winning restaurant experience", "Book your table today"],
        "cta_texts": ["Book a Table", "View Menu", "Order Online", "Reserve Now"],
        "features": [
            ("Farm Fresh Ingredients", "Sourced daily from local farms"),
            ("Expert Chefs", "20+ years of culinary experience"),
            ("Cozy Ambiance", "Perfect for any occasion"),
            ("Fast Service", "Efficient, attentive staff"),
            ("Catering Available", "Events and celebrations"),
            ("Private Dining", "Intimate gatherings"),
        ],
    },
    "portfolio": {
        "hero_titles": ["Creative Work", "Design & Development", "Digital Solutions", "My Portfolio"],
        "hero_subs": ["Crafting beautiful digital experiences", "Let's build something amazing together", "Expert in design, code, and strategy", "Your project deserves excellence"],
        "cta_texts": ["View My Work", "Let's Collaborate", "Contact Me", "Start a Project"],
        "features": [
            ("Web Design", "Beautiful, responsive interfaces"),
            ("Development", "Scalable, performant code"),
            ("UI/UX Design", "User-centered approach"),
            ("Branding", "Logo and visual identity"),
            ("Mobile Apps", "iOS and Android solutions"),
            ("Consulting", "Strategy and optimization"),
        ],
    },
    "saas": {
        "hero_titles": ["Scale Your Business", "Powerful Software", "Work Smarter", "Transform Your Workflow"],
        "hero_subs": ["The platform built for modern teams", "Automate repetitive tasks and focus on growth", "Seamless integration with your tools", "Start free, upgrade when you're ready"],
        "cta_texts": ["Start Free Trial", "Get Started", "Try Now", "Sign Up Free"],
        "features": [
            ("Real-time Collaboration", "Work together seamlessly"),
            ("Advanced Analytics", "Data-driven insights"),
            ("API Integration", "Connect to your favorite tools"),
            ("Enterprise Security", "SOC 2, GDPR compliant"),
            ("24/7 Support", "Dedicated support team"),
            ("Custom Workflows", "Tailor to your needs"),
        ],
    },
    "blog": {
        "hero_titles": ["Stories & Insights", "Latest Updates", "Expert Thoughts", "Welcome to Our Blog"],
        "hero_subs": ["Thoughts on design, tech, and business", "Expert insights delivered weekly", "Stay informed with quality content", "Join thousands of readers"],
        "cta_texts": ["Subscribe Now", "Read Latest", "Explore Articles", "Stay Updated"],
        "features": [
            ("Weekly Posts", "Fresh content every week"),
            ("Expert Writers", "Industry leaders sharing knowledge"),
            ("Newsletter", "Curated content in your inbox"),
            ("Searchable Archive", "Find exactly what you need"),
            ("Community Comments", "Join the conversation"),
            ("Categories", "Browse by topic"),
        ],
    },
    "gym": {
        "hero_titles": ["Transform Your Body", "Fitness Revolution", "Build Your Best Self", "Let's Get Strong"],
        "hero_subs": ["World-class trainers and equipment", "Personalized programs for every goal", "Join our thriving fitness community", "Your journey starts here"],
        "cta_texts": ["Join Now", "Get Free Trial", "Start Training", "Book a Tour"],
        "features": [
            ("Expert Trainers", "Certified fitness professionals"),
            ("State-of-the-Art Equipment", "Latest gym technology"),
            ("Group Classes", "Yoga, HIIT, CrossFit, and more"),
            ("Personal Training", "One-on-one guidance"),
            ("Nutrition Coaching", "Holistic fitness approach"),
            ("Community", "Supportive fitness family"),
        ],
    },
    "travel": {
        "hero_titles": ["Explore the World", "Your Next Adventure", "Travel Beyond Limits", "Discover Destinations"],
        "hero_subs": ["Curated trips and unforgettable experiences", "From beaches to mountains — we plan it all", "Premium travel packages for every explorer", "Book your dream vacation today"],
        "cta_texts": ["Book a Trip", "View Packages", "Plan Journey", "Explore Now"],
        "features": [
            ("Custom Itineraries", "Tailored to your travel style"),
            ("Best Price Guarantee", "Unbeatable value packages"),
            ("24/7 Travel Support", "Help anywhere, anytime"),
            ("Verified Partners", "Trusted hotels and guides"),
            ("Flexible Booking", "Easy rescheduling options"),
            ("Group & Solo Tours", "Trips for every traveler"),
        ],
    },
    "hospital": {
        "hero_titles": ["Care You Can Trust", "Your Health, Our Priority", "Advanced Medical Care", "Compassionate Healthcare"],
        "hero_subs": ["Expert doctors and modern facilities", "Patient-first approach with 24/7 emergency care", "Book appointments online in minutes", "Trusted by thousands of families"],
        "cta_texts": ["Book Appointment", "Find a Doctor", "Emergency Care", "Contact Us"],
        "features": [
            ("Expert Doctors", "Board-certified specialists"),
            ("Modern Equipment", "State-of-the-art diagnostics"),
            ("24/7 Emergency", "Round-the-clock care"),
            ("Online Booking", "Easy appointment scheduling"),
            ("Insurance Support", "All major plans accepted"),
            ("Patient Care", "Warm, compassionate staff"),
        ],
    },
    "education": {
        "hero_titles": ["Learn Without Limits", "Master New Skills", "Education Reimagined", "Start Learning Today"],
        "hero_subs": ["Expert-led courses for every level", "Interactive lessons and real-world projects", "Join thousands of successful learners", "Flexible learning at your pace"],
        "cta_texts": ["Enroll Now", "Browse Courses", "Start Free", "View Curriculum"],
        "features": [
            ("Expert Instructors", "Industry professionals"),
            ("Flexible Schedule", "Learn anytime, anywhere"),
            ("Certificates", "Recognized credentials"),
            ("Live Sessions", "Interactive Q&A classes"),
            ("Project Based", "Hands-on learning"),
            ("Community", "Connect with peers"),
        ],
    },
    "realestate": {
        "hero_titles": ["Find Your Dream Home", "Premium Properties", "Real Estate Excellence", "Live Where You Love"],
        "hero_subs": ["Luxury homes and smart investments", "Browse verified listings with virtual tours", "Expert agents to guide every step", "Your perfect property awaits"],
        "cta_texts": ["View Listings", "Schedule Tour", "Contact Agent", "Explore Homes"],
        "features": [
            ("Verified Listings", "100% authentic properties"),
            ("Virtual Tours", "Explore from anywhere"),
            ("Expert Agents", "Local market specialists"),
            ("Easy Financing", "Mortgage assistance"),
            ("Neighborhood Insights", "Detailed area guides"),
            ("Fast Closing", "Smooth buying process"),
        ],
    },
    "agency": {
        "hero_titles": ["Grow Your Brand", "Digital Excellence", "Results That Matter", "Creative Agency"],
        "hero_subs": ["Strategy, design, and marketing that converts", "We help brands stand out and scale", "Award-winning campaigns and creative work", "Let's build something remarkable"],
        "cta_texts": ["Start a Project", "Get a Quote", "View Work", "Contact Us"],
        "features": [
            ("Brand Strategy", "Positioning that resonates"),
            ("Web Design", "Stunning digital experiences"),
            ("SEO & Ads", "Drive qualified traffic"),
            ("Social Media", "Engaging content campaigns"),
            ("Analytics", "Data-driven decisions"),
            ("Full Service", "End-to-end solutions"),
        ],
    },
    "default": {
        "hero_titles": ["Welcome", "Discover", "Experience", "Explore"],
        "hero_subs": ["Your message here", "Tell your story", "Build connections", "Create impact"],
        "cta_texts": ["Get Started", "Learn More", "Explore", "Join Us"],
        "features": [
            ("Feature One", "Description goes here"),
            ("Feature Two", "Description goes here"),
            ("Feature Three", "Description goes here"),
            ("Feature Four", "Description goes here"),
            ("Feature Five", "Description goes here"),
            ("Feature Six", "Description goes here"),
        ],
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM RULES
# ──────────────────────────────────────────────────────────────────────────────

COLOR_PALETTES = {
    "modern": {"primary": "#2563eb", "secondary": "#1e40af", "accent": "#f59e0b"},
    "vibrant": {"primary": "#d4540a", "secondary": "#0a7070", "accent": "#f97316"},
    "minimal": {"primary": "#0f172a", "secondary": "#64748b", "accent": "#e2e8f0"},
    "premium": {"primary": "#7c3aed", "secondary": "#1e293b", "accent": "#fbbf24"},
    "eco": {"primary": "#16a34a", "secondary": "#065f46", "accent": "#f59e0b"},
    "creative": {"primary": "#ec4899", "secondary": "#7c3aed", "accent": "#06b6d4"},
}

TYPOGRAPHY_SETS = {
    "modern": {
        "heading": "Georgia",
        "body": "Segoe UI",
        "mono": "Courier New",
    },
    "minimal": {
        "heading": "Verdana",
        "body": "Helvetica Neue",
        "mono": "Monaco",
    },
    "playful": {
        "heading": "Comic Sans MS",
        "body": "Trebuchet MS",
        "mono": "Courier",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# TEMPLATE COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────

class LocalTemplateEngine:
    """Pure Python rule-based template engine - NO external APIs"""
    
    def __init__(self, site_type: str = "landing", seed: int = 0):
        self.site_type = site_type
        self.seed = seed
        self.random = random.Random(seed)
        self.style: Dict[str, Any] = {}
        self.page_names: List[str] = []
        self.nav_items: List[Dict[str, str]] = []
        self.images: Optional[LocalImageGenerator] = None
    
    def _section_href(self, section_id: str) -> str:
        return f"#{section_id}"
    
    def _count(self, custom: Dict, section: str, default: int = 4) -> int:
        counts = custom.get("section_counts") or {}
        return max(2, min(int(counts.get(section, custom.get("item_count", default))), 12))
    
    def _use_images(self) -> bool:
        return self.style.get("use_images", True) is not False
    
    def _page_href(self, page_name: str) -> str:
        return "index.html" if page_name == "home" else f"{page_name}.html"
    
    def _sections_for_page(self, page_name: str, all_sections: List[str]) -> List[str]:
        """Pick sections relevant to each page."""
        if page_name == "home":
            return all_sections
        page_map = {
            "about": ["hero", "features", "containers", "team", "testimonials", "cta"],
            "contact": ["hero", "contact", "cta"],
            "shop": ["hero", "products", "cta"],
            "menu": ["hero", "menu", "gallery", "cta"],
            "gallery": ["hero", "gallery", "cta"],
            "pricing": ["hero", "pricing", "faq", "cta"],
            "team": ["hero", "team", "cta"],
            "blog": ["hero", "features", "newsletter", "cta"],
            "work": ["hero", "gallery", "testimonials", "cta"],
            "services": ["hero", "features", "cta"],
            "faq": ["hero", "faq", "cta"],
            "packages": ["hero", "packages", "gallery", "cta"],
            "courses": ["hero", "courses", "pricing", "cta"],
            "doctors": ["hero", "team", "contact", "cta"],
            "classes": ["hero", "features", "pricing", "cta"],
        }
        allowed = page_map.get(page_name, ["hero", "features", "cta"])
        out = []
        for s in all_sections:
            if s in allowed and s not in out:
                out.append(s)
        if "hero" not in out:
            out.insert(0, "hero")
        if "cta" not in out:
            out.append("cta")
        return out
    
    def generate_site(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete website from configuration
        
        Args:
            config: {
                "brand": "Company Name",
                "tagline": "Your tagline",
                "pages": ["home", "about", "services", "contact"],
                "sections": ["hero", "features", "pricing", "testimonials"],
                "colors": {"primary": "#2563eb", ...},
                "custom_content": {"hero_title": "Custom title", ...}
            }
        
        Returns:
            {
                "pages": [{"name": "home", "html": "..."}, ...],
                "metadata": {...},
                "success": True
            }
        """
        
        content = CONTENT_LIBRARY.get(self.site_type, CONTENT_LIBRARY["default"])
        brand = config.get("brand", "My Brand")
        tagline = config.get("tagline", "Your tagline here")
        sections = config.get("sections", ["hero", "features", "cta"])
        colors = dict(config.get("colors") or COLOR_PALETTES.get("modern", {}))
        custom_content = config.get("custom_content", {})
        self.style = dict(config.get("style", {}))
        self.layout = dict(config.get("layout", {}))
        self.page_names = ["home"]
        self.nav_items = config.get("nav_items") or []
        if not self.nav_items:
            self.nav_items = [{"label": "Home", "id": "hero"}]
            for s in sections:
                if s in ("hero", "cta"):
                    continue
                self.nav_items.append({
                    "label": s.replace("_", " ").title(),
                    "id": s,
                })
        img_style = self.style.get("image_style", "abstract")
        self.images = LocalImageGenerator(self.seed, self.site_type, colors, img_style)
        if self.style.get("use_bg_image") and not self.style.get("hero_bg_image"):
            self.style["hero_bg_image"] = self.images.hero_background()
        theme_map = {
            "rounded": "1rem", "sharp": "0", "glass": "1.25rem",
            "minimal": "0.35rem", "premium": "1.5rem", "bold": "0.75rem",
        }
        self._radius = theme_map.get(self.style.get("layout_theme", "rounded"), "1rem")
        self._theme = self.style.get("layout_theme", "rounded")
        body_font = self.style.get("body_font", "Inter")
        heading_font = self.style.get("heading_font", body_font)
        if self.style.get("font_style") == "serif" and body_font == "Inter":
            body_font = heading_font = "Playfair Display"
        self._body_font = body_font
        self._heading_font = heading_font
        self._font = f"'{body_font}', 'Segoe UI', system-ui, sans-serif"
        self._font_link = self._google_fonts_link(body_font, heading_font)
        self._animation = self.style.get("animation", "default")
        self._bold_headings = bool(self.style.get("bold_headings"))

        page_html = self._generate_page(
            "home", brand, tagline, sections, colors, content, custom_content
        )
        pages_out = [{
            "name": "home",
            "filename": "index.html",
            "html": page_html,
            "title": brand,
        }]

        font = self._font
        return {
            "pages": pages_out,
            "site_name": brand,
            "site_type": self.site_type,
            "page_count": 1,
            "success": True,
            "font": font,
            "sections_detected": config.get("sections_detected", []),
            "color_palette": config.get("color_palette", {
                "primary": colors.get("primary"),
                "accent": colors.get("accent"),
                "background": colors.get("background", "#fff"),
            }),
            "metadata": {
                "brand": brand,
                "tagline": tagline,
                "colors": colors,
                "pages": ["home"],
                "nav_items": self.nav_items,
                "hero_image": self.style.get("hero_bg_image"),
            },
        }
    
    def _generate_page(self, page_name: str, brand: str, tagline: str,
                      sections: List[str], colors: Dict,
                      content: Dict, custom: Dict) -> str:
        nav_html = self._build_navbar(brand, colors, custom)
        sections_html = ""
        compact_hero = False
        for section in sections:
            sections_html += self._build_section(
                section, content, colors, custom, compact_hero=compact_hero
            )
        footer_html = self._build_footer(brand, colors, custom)
        body_bg = colors.get("background", "#fff")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{_html.escape(brand)} · {_html.escape(page_name.replace('_', ' ').title())}</title>
<meta name="description" content="{_html.escape(tagline)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{self._font_link}" rel="stylesheet">
<style>
{self._build_css(colors)}
</style>
</head>
<body style="background:{body_bg};color:{colors.get('text', '#0f172a')}">
{nav_html}
<main>
{sections_html}
</main>
{footer_html}
<script>{self._build_js()}</script>
</body>
</html>"""

    def _build_section(self, section: str, content: Dict, colors: Dict,
                       custom: Dict, compact_hero: bool = False) -> str:
        builders = {
            "hero": lambda: self._build_hero(content, colors, custom, compact=compact_hero),
            "features": lambda: self._build_features(content, colors, custom),
            "pricing": lambda: self._build_pricing(colors, custom),
            "testimonials": lambda: self._build_testimonials(colors, custom),
            "cta": lambda: self._build_cta(content, colors),
            "faq": lambda: self._build_faq(colors, custom),
            "products": lambda: self._build_products(colors, custom),
            "menu": lambda: self._build_menu(colors, custom),
            "gallery": lambda: self._build_gallery(colors, custom),
            "team": lambda: self._build_team(colors, custom),
            "contact": lambda: self._build_contact(colors, custom),
            "stats": lambda: self._build_stats(colors),
            "newsletter": lambda: self._build_newsletter(colors),
            "packages": lambda: self._build_packages(colors, custom),
            "courses": lambda: self._build_courses(colors, custom),
            "containers": lambda: self._build_containers(colors, custom),
        }
        fn = builders.get(section)
        return fn() if fn else ""

    def _title(self, custom: Dict, key: str, default: str) -> str:
        return custom.get("section_titles", {}).get(key, default)

    def _section_items(self, custom: Dict, key: str) -> List[str]:
        return list((custom.get("section_items") or {}).get(key, []) or [])

    def _section_cards(self, custom: Dict, key: str) -> List[Dict[str, str]]:
        return list((custom.get("section_cards") or {}).get(key, []) or [])

    def _google_fonts_link(self, body_font: str, heading_font: str) -> str:
        families = []
        for f in {body_font, heading_font}:
            if not f:
                continue
            name = f.strip().replace(" ", "+")
            families.append(f"family={name}:wght@400;600;700;800")
        if not families:
            return "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap"
        return "https://fonts.googleapis.com/css2?family=" + "&family=".join(families) + "&display=swap"
    
    def _build_navbar(self, brand: str, colors: Dict, custom: Dict) -> str:
        if self.layout.get("show_header") is False:
            return ""
        nav_bg = colors.get("header_bg", colors.get("primary", "#0f172a"))
        brand_color = colors.get("header_text", "#fff")
        link_color = colors.get("header_text", "#e2e8f0") if not colors.get("is_dark") else "#cbd5e1"
        nav_style = self.style.get("nav_style", "spread")
        nav_cta = custom.get("nav_cta", "Get Started")
        links = ""
        for item in self.nav_items[:10]:
            sid = item.get("id", "hero")
            label = item.get("label", sid.title())
            href = self._section_href(sid)
            link_style = f"color:{link_color};opacity:0.9;text-decoration:none;font-size:0.9rem"
            links += f'<a href="{href}" class="px-nav-link" style="{link_style}">{_html.escape(label)}</a>'
        cta_href = "#contact" if any(i.get("id") == "contact" for i in self.nav_items) else "#cta"
        glass = "backdrop-filter:blur(14px);background:rgba(255,255,255,0.08);" if self._theme == "glass" else ""
        nav_justify = "center" if nav_style == "center" else "space-between"
        nav_inner = "justify-content:center;" if nav_style == "center" else ""
        return f"""<header class="px-nav" style="
            display:flex;justify-content:{nav_justify};align-items:center;flex-wrap:wrap;gap:1rem;
            padding:1rem 5%;background:{nav_bg};border-bottom:3px solid {colors['accent']};
            position:sticky;top:0;z-index:200;{glass}
        ">
            <a href="#hero" class="px-nav-link" style="font-size:1.35rem;font-weight:800;color:{brand_color};text-decoration:none">
                {_html.escape(brand[:42])}
            </a>
            <nav style="display:flex;gap:1.25rem;align-items:center;flex-wrap:wrap;{nav_inner}">{links}</nav>
            <a href="{cta_href}" class="px-nav-cta px-nav-link" style="
                background:{colors['accent']};color:#0f172a;text-decoration:none;
                padding:0.55rem 1.35rem;border-radius:{self._radius};font-weight:700;font-size:0.9rem;
            ">{_html.escape(nav_cta)}</a>
        </header>"""

    def _build_hero(self, content: Dict, colors: Dict, custom: Dict, compact: bool = False) -> str:
        title = custom.get("hero_title") or self.random.choice(content.get("hero_titles", ["Welcome"]))
        subtitle = custom.get("hero_subtitle") or self.random.choice(content.get("hero_subs", ["Your message"]))
        cta_text = custom.get("cta_text") or self.random.choice(content.get("cta_texts", ["Get Started"]))
        bg_img = self.style.get("hero_bg_image", "") if self.style.get("use_bg_image", True) else ""
        if not bg_img and self.style.get("use_bg_image", True) and self.images:
            bg_img = self.images.hero_background()
        align = "center" if self.style.get("hero_align", "center") == "center" else "left"
        items_align = "center" if align == "center" else "flex-start"
        text_align = align
        min_h = "40vh" if compact else "82vh"
        overlay = f"linear-gradient(135deg, {colors['primary']}cc 0%, {colors.get('accent','#f59e0b')}88 100%)"
        if self.style.get("use_gradient") and not bg_img:
            bg_style = f"background:linear-gradient(135deg,{colors['primary']},{colors.get('secondary', colors['primary'])},{colors.get('accent', '#f59e0b')});"
            text_light, sub_color = "#fff", "rgba(255,255,255,0.92)"
        elif bg_img:
            bg_style = f'background-image:{overlay},url("{bg_img}");background-size:cover;background-position:center;'
            text_light, sub_color = "#fff", "rgba(255,255,255,0.92)"
        else:
            bg_style = f"background:{colors.get('primary', '#2563eb')};"
            text_light, sub_color = "#fff", "rgba(255,255,255,0.9)"
        explore_target = "#features"
        for candidate in ("features", "products", "menu", "gallery", "pricing", "packages", "courses", "contact"):
            if any((i.get("id") == candidate) for i in self.nav_items):
                explore_target = f"#{candidate}"
                break
        hero_title = self._title(custom, "hero", title)
        return f"""<section id="hero" class="px-hero" style="
            {bg_style}padding:5rem 5%;text-align:{text_align};min-height:{min_h};
            display:flex;flex-direction:column;justify-content:center;align-items:{items_align};position:relative;
        ">
            <h1 style="font-size:clamp(2rem,5vw,3.75rem);font-weight:800;margin-bottom:1rem;color:{text_light};letter-spacing:-0.03em;max-width:900px">
                {_html.escape(hero_title)}
            </h1>
            <p style="font-size:clamp(1rem,2.5vw,1.3rem);color:{sub_color};margin-bottom:2rem;max-width:640px;line-height:1.65">
                {_html.escape(subtitle)}
            </p>
            <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
                <a href="#contact" class="px-nav-link" style="
                    background:{colors['accent']};color:#0f172a;text-decoration:none;
                    padding:0.85rem 2rem;border-radius:999px;font-weight:700;font-size:1rem;
                ">{_html.escape(cta_text)}</a>
                <a href="{explore_target}" class="px-nav-link" style="
                    background:rgba(255,255,255,0.15);color:{text_light};text-decoration:none;
                    border:2px solid rgba(255,255,255,0.5);padding:0.8rem 1.75rem;border-radius:999px;font-weight:600;
                ">Explore</a>
            </div>
        </section>"""
    
    def _build_features(self, content: Dict, colors: Dict, custom: Dict) -> str:
        """Build features grid"""
        cards = self._section_cards(custom, "features")
        n = len(cards) if cards else self._count(custom, "features", 6)
        if cards:
            features = [(c["title"], c.get("desc") or "Tailored for your business.") for c in cards[:n]]
        else:
            custom_items = self._section_items(custom, "features")
            if custom_items:
                features = [(x, "Custom service from your prompt.") for x in custom_items[:n]]
            else:
                features = content.get("features", [])[:n]
        features_html = ""
        txt = colors.get("text", "#1a202c")
        use_img = self._use_images() and self.images
        for i, (title, desc) in enumerate(features):
            card_bg = colors.get("background", "#fff") if not colors.get("is_dark") else "#1e293b"
            icon_html = (
                f'<img src="{self.images.feature_icon(i)}" alt="" style="width:56px;height:56px;margin-bottom:0.75rem">'
                if use_img else
                f'<div style="font-size:2rem;margin-bottom:0.5rem;color:{colors["accent"]}">✨</div>'
            )
            features_html += f"""<div class="px-card" style="
                padding:2rem;background:{card_bg};border:1px solid {colors['primary']}22;
                border-radius:{self._radius};text-align:center;transition:transform .2s;
            ">
                {icon_html}
                <h3 style="font-weight:700;margin-bottom:0.5rem;color:{txt}">{_html.escape(title)}</h3>
                <p style="color:{colors.get('muted','#6b7280')};line-height:1.6">{_html.escape(desc)}</p>
            </div>"""
        
        surf = colors.get("surface", "#f9fafb")
        feat_title = self._title(custom, "features", "Features")
        return f"""<section id="features" style="padding:4rem 5%;background:{surf}">
            <h2 style="font-size:2.5rem;font-weight:800;margin-bottom:1rem;text-align:center;color:{txt}">
                {_html.escape(feat_title)}
            </h2>
            <p style="text-align:center;color:{colors.get('muted','#6b7280')};margin-bottom:3rem;max-width:600px;margin-left:auto;margin-right:auto">
                Everything you need to succeed
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">
                {features_html}
            </div>
        </section>"""
    
    def _build_pricing(self, colors: Dict, custom: Dict) -> str:
        """Build pricing section"""
        txt = colors.get("text", "#1a202c")
        card = colors.get("card_bg", "#fff")
        title = self._title(custom, "pricing", "Simple Pricing")
        plans = custom.get("pricing_plans") or []
        if not plans:
            plans = [
                {"name": "Starter", "price": "Free"},
                {"name": "Pro", "price": "₹999/mo"},
                {"name": "Enterprise", "price": "Custom"},
            ]
        plan_html = ""
        for i, plan in enumerate(plans):
            highlight = "background:{0}15;border:2px solid {0};".format(colors["primary"]) if i == 1 and len(plans) > 1 else f"border:2px solid {colors['primary']};background:{card};"
            plan_html += f"""<div style="{highlight}border-radius:{self._radius};padding:2rem;text-align:center;">
                <h3 style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;color:{txt}">{_html.escape(plan.get('name', 'Plan'))}</h3>
                <p style="font-size:2.5rem;font-weight:900;color:{colors['primary']};margin:1rem 0">{_html.escape(plan.get('price', '₹0'))}</p>
                <button style="width:100%;background:{colors['primary']};color:#fff;border:none;padding:0.75rem;border-radius:0.375rem;font-weight:600;cursor:pointer">Choose Plan</button>
            </div>"""
        return f"""<section id="pricing" style="padding:4rem 5%;background:{colors.get('surface', '#f9fafb')}">
            <h2 style="font-size:2.5rem;font-weight:800;margin-bottom:3rem;text-align:center;color:{txt}">
                {_html.escape(title)}
            </h2>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">
                {plan_html}
            </div>
        </section>"""
    
    def _build_testimonials(self, colors: Dict, custom: Dict) -> str:
        """Build testimonials section"""
        custom_t = custom.get("testimonials") or []
        if custom_t:
            testimonials = [(t["name"], t.get("role", "Client"), t.get("text", "")) for t in custom_t]
        else:
            testimonials = [
                ("Rohan Mehta", "CEO", "Absolutely transformed how we work. Highly recommend!"),
                ("Priya Sharma", "Marketing Lead", "Incredible quality and amazing support."),
                ("Amit Singh", "Freelancer", "Best decision I made. Results speak for themselves."),
            ]
        
        testi_html = ""
        txt = colors.get("text", "#0f172a")
        for name, role, text in testimonials:
            testi_html += f"""<div style="
                background:{colors.get('card_bg','#fff')};border:1px solid {colors['primary']}33;border-radius:{self._radius};
                padding:1.5rem;
            ">
                <p style="color:{colors.get('muted','#6b7280')};margin-bottom:1rem;font-size:1rem">
                    "{_html.escape(text)}"
                </p>
                <div style="font-weight:700;color:{txt}">{_html.escape(name)}</div>
                <div style="font-size:0.875rem;color:{colors['primary']}">{_html.escape(role)}</div>
            </div>"""
        return f"""<section id="testimonials" style="padding:4rem 5%;background:{colors.get('surface','#f9fafb')}">
            <h2 style="font-size:2.5rem;font-weight:800;margin-bottom:3rem;text-align:center;color:{txt}">
                What People Say
            </h2>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">
                {testi_html}
            </div>
        </section>"""
    
    def _build_cta(self, content: Dict, colors: Dict) -> str:
        """Build call-to-action section"""
        cta_text = self.random.choice(content.get("cta_texts", ["Get Started"]))
        
        return f"""<section id="cta" style="
            background:linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            padding:4rem 5%; text-align:center; color:white;
        ">
            <h2 style="font-size:2.5rem; font-weight:800; margin-bottom:1rem;">Ready to Get Started?</h2>
            <p style="font-size:1.25rem; margin-bottom:2rem; opacity:0.9;">
                Join thousands of happy customers today.
            </p>
            <button style="
                background:white; color:{colors['primary']}; border:none;
                padding:0.75rem 2rem; border-radius:0.5rem; font-weight:700;
                font-size:1rem; cursor:pointer;
            ">{_html.escape(cta_text)} →</button>
        </section>"""
    
    def _build_faq(self, colors: Dict, custom: Dict) -> str:
        """Build FAQ section"""
        faqs = [
            ("How do I get started?", "Simply sign up and follow the onboarding guide."),
            ("Is there a free trial?", "Yes, 14 days free - no credit card required."),
            ("Can I cancel anytime?", "Absolutely, cancel anytime with no questions."),
        ]
        faq_cards = self._section_cards(custom, "faq")
        if faq_cards:
            faqs = [(c["title"], c.get("desc") or "Details available on request.") for c in faq_cards[:8]]
        elif self._section_items(custom, "faq"):
            faqs = [(q, "Details available on request.") for q in self._section_items(custom, "faq")[:8]]
        
        faq_html = ""
        for q, a in faqs:
            faq_html += f"""<details style="
                margin-bottom:1rem; padding:1rem; border:1px solid #e5e7eb;
                border-radius:0.375rem; cursor:pointer;
            ">
                <summary style="font-weight:700; color:{colors['primary']}; cursor:pointer;">
                    {_html.escape(q)}
                </summary>
                <p style="margin-top:1rem; color:#6b7280; line-height:1.6;">
                    {_html.escape(a)}
                </p>
            </details>"""
        
        faq_title = self._title(custom, "faq", "Frequently Asked Questions")
        return f"""<section id="faq" style="padding:4rem 5%;background:{colors.get('surface','#f9fafb')}">
            <h2 style="font-size:2.5rem;font-weight:800;margin-bottom:3rem;text-align:center;color:{colors.get('text','#1a202c')}">
                {_html.escape(faq_title)}
            </h2>
            <div style="max-width:600px;margin:0 auto">{faq_html}</div>
        </section>"""

    def _img_url(self, topic: str, idx: int, label: str = "") -> str:
        if self.images and self._use_images():
            return self.images.card_image(idx, label=label or f"Image {idx + 1}")
        return self.images.hero_background() if self.images else ""

    def _build_products(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "products", 6)
        names = self._section_items(custom, "products") or CONTENT_LIBRARY.get(
            self.site_type, CONTENT_LIBRARY["default"]
        ).get("product_names", [f"Product {i+1}" for i in range(n)])
        cards = ""
        for i in range(n):
            name = names[i % len(names)] if names else f"Item {i+1}"
            price = self.random.choice([499, 799, 1299, 2499, 3999, 5999])
            img = self._img_url("product", i, name)
            cards += f"""<article class="px-card" style="background:{colors.get('background','#fff')};border-radius:1rem;overflow:hidden;border:1px solid {colors['primary']}22">
                <img src="{img}" alt="{_html.escape(name)}" style="width:100%;height:200px;object-fit:cover" loading="lazy">
                <div style="padding:1.25rem">
                    <h3 style="font-weight:700;color:{colors.get('text','#0f172a')};margin-bottom:0.35rem">{_html.escape(name)}</h3>
                    <p style="color:{colors['primary']};font-weight:800;font-size:1.25rem;margin-bottom:1rem">₹{price:,}</p>
                    <button style="width:100%;background:{colors['primary']};color:#fff;border:none;padding:0.65rem;border-radius:0.5rem;font-weight:600;cursor:pointer">Add to Cart</button>
                </div>
            </article>"""
        prod_title = self._title(custom, "products", "Our Products")
        return f"""<section id="products" style="padding:4rem 5%"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2.5rem;color:{colors.get('text','#0f172a')}">{_html.escape(prod_title)}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.75rem;max-width:1200px;margin:0 auto">{cards}</div></section>"""

    def _build_menu(self, colors: Dict, custom: Dict) -> str:
        cards = self._section_cards(custom, "menu")
        n = len(cards) if cards else self._count(custom, "menu", 8)
        dishes = self._section_items(custom, "menu") or [
            "Truffle Pasta", "Wood-Fired Pizza", "Seafood Risotto", "Tiramisu",
            "Bruschetta", "Osso Buco", "Caprese Salad", "Gelato",
        ]
        items = ""
        for i in range(n):
            if cards and i < len(cards):
                d = cards[i]["title"]
                desc = cards[i].get("desc", "")
            else:
                d = dishes[i % len(dishes)]
                desc = ""
            price = self.random.choice([299, 449, 599, 799, 999])
            img = self._img_url("food", i, d)
            img_html = f'<img src="{img}" alt="{_html.escape(d)}" style="width:100px;height:100px;object-fit:cover;border-radius:0.75rem" loading="lazy">' if img else f'<div style="width:100px;height:100px;border-radius:0.75rem;background:linear-gradient(135deg,{colors["primary"]},{colors["accent"]})"></div>'
            desc_html = f'<p style="color:{colors.get("muted","#64748b")};font-size:0.9rem">{_html.escape(desc)}</p>' if desc else ""
            items += f"""<div class="px-card" style="display:flex;gap:1rem;background:{colors.get('surface','#fff')};padding:1rem;border-radius:{self._radius};border:1px solid {colors['primary']}18">
                {img_html}
                <div><h3 style="font-weight:700;color:{colors.get('text','#0f172a')}">{_html.escape(d)}</h3>{desc_html}<p style="color:{colors['primary']};font-weight:700">₹{price}</p></div>
            </div>"""
        menu_title = self._title(custom, "menu", "Menu")
        return f"""<section id="menu" style="padding:4rem 5%;background:{colors.get('surface','#f9fafb')}"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">{_html.escape(menu_title)}</h2>
        <div style="display:grid;gap:1rem;max-width:800px;margin:0 auto">{items}</div></section>"""

    def _build_gallery(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "gallery", 6)
        custom_labels = self._section_items(custom, "gallery")
        imgs = ""
        if self.images and self._use_images():
            imgs = "".join(
                f'<div class="px-gallery-item" style="overflow:hidden;border-radius:{self._radius};box-shadow:0 8px 24px {colors["primary"]}22">'
                f'<img src="{self.images.gallery_tile(i)}" alt="{_html.escape((custom_labels[i] if i < len(custom_labels) else f"Gallery {i+1}"))}" style="width:100%;height:220px;object-fit:cover;display:block" loading="lazy"></div>'
                for i in range(n)
            )
        else:
            imgs = "".join(
                f'<div style="height:220px;border-radius:{self._radius};background:linear-gradient(135deg,{colors["primary"]},{colors["accent"]});opacity:{0.7 + (i % 3) * 0.1}"></div>'
                for i in range(n)
            )
        title = self._title(custom, "gallery", "Gallery")
        return f"""<section id="gallery" style="padding:4rem 5%"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">{_html.escape(title)}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem;max-width:1200px;margin:0 auto">{imgs}</div></section>"""

    def _build_team(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "team", 4)
        roles = ["Lead Designer", "Developer", "Marketing", "Support", "Operations", "Strategy"]
        custom_names = self._section_items(custom, "team")
        members = ""
        for i in range(n):
            role = roles[i % len(roles)]
            name = custom_names[i] if i < len(custom_names) else f"Team Member {i+1}"
            img = self.images.portrait(i + 20, name) if self.images and self._use_images() else ""
            img_html = (
                f'<img src="{img}" alt="{_html.escape(name)}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;margin:0 auto 1rem" loading="lazy">'
                if img else
                f'<div style="width:120px;height:120px;border-radius:50%;background:{colors["primary"]};margin:0 auto 1rem;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800">{name[0]}</div>'
            )
            members += f"""<div class="px-card" style="text-align:center;padding:1.5rem;background:{colors.get('surface','#fff')};border-radius:{self._radius}">
                {img_html}
                <h3 style="font-weight:700;color:{colors.get('text','#0f172a')}">{name}</h3>
                <p style="color:{colors['primary']}">{role}</p>
            </div>"""
        team_title = self._title(custom, "team", "Our Team")
        return f"""<section id="team" style="padding:4rem 5%"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">{_html.escape(team_title)}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;max-width:1000px;margin:0 auto">{members}</div></section>"""

    def _build_contact(self, colors: Dict, custom: Dict) -> str:
        contact_title = self._title(custom, "contact", "Contact Us")
        info = custom.get("contact_info") or {}
        info_html = ""
        if info:
            rows = []
            if info.get("phone"):
                rows.append(f"<div><strong>Phone:</strong> {_html.escape(info['phone'])}</div>")
            if info.get("email"):
                rows.append(f"<div><strong>Email:</strong> {_html.escape(info['email'])}</div>")
            if info.get("whatsapp"):
                rows.append(f"<div><strong>WhatsApp:</strong> {_html.escape(info['whatsapp'])}</div>")
            if info.get("address"):
                rows.append(f"<div><strong>Address:</strong> {_html.escape(info['address'])}</div>")
            info_html = f'<div style="max-width:520px;margin:0 auto 1.5rem;color:{colors.get("muted","#64748b")};display:flex;flex-direction:column;gap:0.5rem;text-align:center">{"".join(rows)}</div>'
        return f"""<section id="contact" style="padding:4rem 5%;background:{colors.get('surface','#f8fafc')}">
            <h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">{_html.escape(contact_title)}</h2>
            {info_html}
            <form style="max-width:520px;margin:0 auto;display:flex;flex-direction:column;gap:1rem" onsubmit="event.preventDefault();alert('Thanks! We will reply soon.');">
                <input type="text" placeholder="Your name" required style="padding:0.85rem;border:1px solid {colors['primary']}44;border-radius:0.5rem;font-size:1rem">
                <input type="email" placeholder="Email" required style="padding:0.85rem;border:1px solid {colors['primary']}44;border-radius:0.5rem;font-size:1rem">
                <textarea placeholder="Message" rows="4" required style="padding:0.85rem;border:1px solid {colors['primary']}44;border-radius:0.5rem;font-size:1rem"></textarea>
                <button type="submit" style="background:{colors['primary']};color:#fff;border:none;padding:0.9rem;border-radius:0.5rem;font-weight:700;cursor:pointer">Send Message</button>
            </form>
        </section>"""

    def _build_stats(self, colors: Dict) -> str:
        stats = [("10K+", "Happy Clients"), ("500+", "Projects"), ("99%", "Satisfaction"), ("24/7", "Support")]
        boxes = "".join(
            f'<div style="text-align:center;padding:2rem"><div style="font-size:2.75rem;font-weight:900;color:{colors["accent"]}">{v}</div><div style="color:{colors.get("muted","#64748b")};margin-top:0.5rem">{l}</div></div>'
            for v, l in stats
        )
        return f"""<section style="padding:3rem 5%;background:{colors['primary']};color:#fff"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;max-width:1000px;margin:0 auto">{boxes}</div></section>"""

    def _build_newsletter(self, colors: Dict) -> str:
        return f"""<section style="padding:3rem 5%;text-align:center;background:{colors.get('surface','#f1f5f9')}">
            <h2 style="font-size:1.75rem;font-weight:800;margin-bottom:1rem;color:{colors.get('text','#0f172a')}">Stay in the loop</h2>
            <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;max-width:480px;margin:0 auto">
                <input type="email" placeholder="you@email.com" style="flex:1;min-width:200px;padding:0.75rem;border-radius:0.5rem;border:1px solid #ccc">
                <button style="background:{colors['primary']};color:#fff;border:none;padding:0.75rem 1.5rem;border-radius:0.5rem;font-weight:600">Subscribe</button>
            </div>
        </section>"""

    def _build_packages(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "packages", 6)
        dests = self._section_items(custom, "packages") or [
            "Bali Escape", "Swiss Alps", "Tokyo Discovery", "Safari Kenya", "Greek Islands", "Iceland Aurora"
        ]
        cards = ""
        for i in range(n):
            d = dests[i % len(dests)]
            price = self.random.choice([45999, 68999, 89999, 129999])
            img = self._img_url("travel", i + 10, d)
            cards += f"""<article class="px-card" style="border-radius:{self._radius};overflow:hidden;background:{colors.get('background','#fff')};border:1px solid {colors['primary']}22">
                <img src="{img}" alt="{_html.escape(d)}" style="width:100%;height:180px;object-fit:cover" loading="lazy">
                <div style="padding:1.25rem"><h3 style="font-weight:700;color:{colors.get('text','#0f172a')}">{d}</h3>
                <p style="color:{colors['primary']};font-weight:800;margin:0.5rem 0">From ₹{price:,}</p>
                <button style="background:{colors['accent']};color:#0f172a;border:none;padding:0.5rem 1rem;border-radius:0.5rem;font-weight:600;width:100%">Book Now</button></div>
            </article>"""
        return f"""<section id="packages" style="padding:4rem 5%"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">Packages</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem;max-width:1200px;margin:0 auto">{cards}</div></section>"""

    def _build_courses(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "courses", 6)
        courses = self._section_items(custom, "courses") or [
            "Web Development Bootcamp", "UI/UX Masterclass", "Data Science 101",
            "Digital Marketing", "Python Pro", "Cloud AWS",
        ]
        cards = ""
        for i in range(n):
            c = courses[i % len(courses)]
            price = self.random.choice([1999, 4999, 7999])
            img_html = ""
            if self.images and self._use_images():
                img = self.images.card_image(i + 30, label=c[:20])
                img_html = f'<img src="{img}" alt="{_html.escape(c)}" style="width:100%;height:140px;object-fit:cover;border-radius:{self._radius} {self._radius} 0 0;margin:-1.5rem -1.5rem 1rem -1.5rem;width:calc(100% + 3rem)">'
            cards += f"""<div class="px-card" style="padding:1.5rem;background:{colors.get('surface','#fff')};border-radius:{self._radius};border-left:4px solid {colors['primary']};overflow:hidden">
                {img_html}
                <h3 style="font-weight:700;color:{colors.get('text','#0f172a')}">{c}</h3>
                <p style="color:{colors['primary']};font-weight:800;margin-top:0.5rem">₹{price:,}</p>
            </div>"""
        return f"""<section id="courses" style="padding:4rem 5%;background:{colors.get('surface','#f9fafb')}"><h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2rem;color:{colors.get('text','#0f172a')}">Courses</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem;max-width:1100px;margin:0 auto">{cards}</div></section>"""

    def _build_containers(self, colors: Dict, custom: Dict) -> str:
        n = self._count(custom, "containers", 4)
        titles = custom.get("section_titles", {})
        blocks = ""
        card_bg = colors.get("card_bg", "#fff")
        txt = colors.get("text", "#0f172a")
        for i in range(n):
            t = titles.get(f"block_{i}") or titles.get(f"block_{i+1}") or f"Section {i + 1}"
            img_html = ""
            if self.images and self._use_images():
                banner = self.images.container_banner(i)
                img_html = f'<img src="{banner}" alt="{_html.escape(t)}" style="width:100%;height:140px;object-fit:cover;border-radius:{self._radius};margin-bottom:1rem" loading="lazy">'
            blocks += f"""<div class="px-container px-card" style="
                padding:2rem;background:{card_bg};border-radius:{self._radius};
                border:2px solid {colors['accent']}44;box-shadow:0 8px 30px {colors['primary']}18;
            ">
                {img_html}
                <h3 style="font-size:1.35rem;font-weight:800;color:{colors['primary']};margin-bottom:0.75rem">{_html.escape(t)}</h3>
                <p style="color:{colors.get('muted','#64748b')};line-height:1.7">Premium content block {i + 1} — styled from your prompt colors, layout theme, and section count.</p>
            </div>"""
        return f"""<section id="containers" style="padding:4rem 5%;background:{colors.get('background','#fff')}">
            <h2 style="font-size:2.5rem;font-weight:800;text-align:center;margin-bottom:2.5rem;color:{txt}">Our Sections</h2>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.75rem;max-width:1200px;margin:0 auto">{blocks}</div>
        </section>"""

    def _build_footer(self, brand: str, colors: Dict, custom: Optional[Dict] = None) -> str:
        if self.layout.get("show_footer") is False:
            return ""
        custom = custom or {}
        foot_bg = colors.get("footer_bg", colors.get("primary", "#0f172a"))
        foot_text = colors.get("footer_text", "#fff")
        muted = "rgba(255,255,255,0.65)" if not colors.get("is_dark") else "rgba(255,255,255,0.55)"
        if foot_text == "#0f172a":
            muted = "#64748b"
        info = custom.get("contact_info") or {}
        contact_lines = ""
        if info.get("email"):
            contact_lines += f'<div style="color:{muted};font-size:0.875rem">{_html.escape(info["email"])}</div>'
        if info.get("phone"):
            contact_lines += f'<div style="color:{muted};font-size:0.875rem">{_html.escape(info["phone"])}</div>'
        nav_links = "".join(
            f'<a href="{self._section_href(item.get("id", "hero"))}" class="px-nav-link" '
            f'style="color:{muted};text-decoration:none;font-size:0.875rem">'
            f'{_html.escape(item.get("label", "Link"))}</a>'
            for item in self.nav_items[:8]
        )
        return f"""<footer style="background:{foot_bg};color:{foot_text};padding:3rem 5%;border-top:4px solid {colors['accent']}">
            <div style="max-width:1200px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:2rem;margin-bottom:2rem">
                <div>
                    <div style="font-weight:800;margin-bottom:1rem;font-size:1.2rem;color:{colors['accent']}">{_html.escape(brand)}</div>
                    <p style="color:{muted};font-size:0.875rem;line-height:1.6">Single-page website built from your prompt — click menu to jump to any section.</p>
                </div>
                <div>
                    <div style="font-weight:700;margin-bottom:1rem">Quick Links</div>
                    <div style="display:flex;flex-direction:column;gap:0.5rem">{nav_links}</div>
                </div>
                <div>
                    <div style="font-weight:700;margin-bottom:1rem">Contact</div>
                    {contact_lines or f'<div style="color:{muted};font-size:0.875rem">Reach us anytime</div>'}
                </div>
            </div>
            <div style="border-top:1px solid {colors['accent']}44;padding-top:1.5rem;text-align:center;color:{muted};font-size:0.875rem">
                © 2025 {_html.escape(brand)}. All rights reserved.
            </div>
        </footer>"""
    
    def _build_css(self, colors: Dict) -> str:
        """Build base CSS with design tokens from prompt."""
        theme = self._theme
        card_shadow = "0 4px 20px rgba(0,0,0,0.08)"
        if theme == "glass":
            card_shadow = "0 8px 32px rgba(0,0,0,0.12)"
        elif theme == "bold":
            card_shadow = f"0 6px 0 {colors.get('accent', '#f59e0b')}"
        elif theme == "premium":
            card_shadow = "0 20px 50px rgba(0,0,0,0.15)"
        heading_weight = "900" if self._bold_headings else "800"
        anim_css = ""
        if self._animation == "none":
            anim_css = "main > section { animation: none; }"
        elif self._animation == "premium":
            anim_css = """
        @keyframes px-fade-up { from { opacity: 0; transform: translateY(24px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
        main > section { animation: px-fade-up 0.85s cubic-bezier(.2,.8,.2,1) both; }
        main > section:nth-child(2) { animation-delay: 0.08s; }
        main > section:nth-child(3) { animation-delay: 0.16s; }
        main > section:nth-child(4) { animation-delay: 0.24s; }
            """
        elif self._animation == "subtle":
            anim_css = """
        @keyframes px-fade-up { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        main > section { animation: px-fade-up 0.45s ease both; }
            """
        else:
            anim_css = """
        @keyframes px-fade-up { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
        main > section { animation: px-fade-up 0.6s ease both; }
        main > section:nth-child(2) { animation-delay: 0.05s; }
        main > section:nth-child(3) { animation-delay: 0.1s; }
            """
        return f"""
        :root {{
            --primary: {colors['primary']};
            --accent: {colors.get('accent', '#f59e0b')};
            --surface: {colors.get('surface', '#f8fafc')};
            --text: {colors.get('text', '#0f172a')};
            --muted: {colors.get('muted', '#64748b')};
            --radius: {self._radius};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: {self._font}; line-height: 1.6; }}
        h1, h2, h3 {{ font-family: '{self._heading_font}', {self._font}; font-weight: {heading_weight}; }}
        a {{ color: var(--primary); text-decoration: none; }}
        a:hover {{ opacity: 0.85; }}
        button:hover, .px-nav-cta:hover {{ transform: translateY(-1px); filter: brightness(1.05); }}
        .px-card:hover {{ transform: translateY(-4px); box-shadow: {card_shadow}; }}
        .px-card, .px-container, .px-gallery-item {{ transition: transform 0.25s ease, box-shadow 0.25s ease; }}
        .px-hero::after {{
            content:''; position:absolute; inset:0;
            background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12), transparent 40%);
            pointer-events:none;
        }}
        section {{ scroll-margin-top: 88px; position: relative; }}
        img {{ max-width: 100%; display: block; }}
        {anim_css}
        @media (max-width: 768px) {{
            .px-nav {{ padding: 0.75rem 1rem !important; }}
            .px-hero {{ min-height: 55vh !important; padding: 3rem 1rem !important; }}
            h1 {{ font-size: 1.85rem !important; }}
            h2 {{ font-size: 1.5rem !important; }}
            section {{ padding: 2.5rem 1rem !important; }}
        }}
        """
    
    def _build_js(self) -> str:
        """Smooth scroll for all same-page anchor links."""
        return """
        document.querySelectorAll('a.px-nav-link[href^="#"], a[href^="#"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const id = this.getAttribute('href');
                if (!id || id === '#') return;
                const target = document.querySelector(id);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    history.replaceState(null, '', id);
                }
            });
        });
        """


def generate_site_local(config: Dict[str, Any]) -> Dict[str, Any]:
    """Public API: Generate site locally from prompt or config (NO external APIs)."""
    if config.get("prompt") and not config.get("_parsed"):
        try:
            from prompt_parser import parse_prompt
            config = {**parse_prompt(config["prompt"]), **config}
        except Exception:
            pass

    site_type = config.get("site_type", "default")
    seed = config.get("seed", 0)
    engine = LocalTemplateEngine(site_type, seed)
    result = engine.generate_site(config)

    pages_html = []
    for page in result.get("pages", []):
        pages_html.append({
            "filename": page["filename"],
            "name": page.get("title") or page.get("name"),
            "html": page["html"],
        })

    return {
        "pages": pages_html,
        "site_name": result.get("site_name"),
        "site_type": result.get("site_type"),
        "page_count": len(pages_html),
        "success": True,
        "font": result.get("font"),
        "sections_detected": result.get("sections_detected", config.get("sections_detected", [])),
        "color_palette": result.get("color_palette", config.get("color_palette")),
    }
