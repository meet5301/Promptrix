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
        
        # Get content library for this site type
        content = CONTENT_LIBRARY.get(self.site_type, CONTENT_LIBRARY["default"])
        
        # Build site configuration
        brand = config.get("brand", "My Brand")
        tagline = config.get("tagline", "Your tagline here")
        pages = config.get("pages", ["home", "contact"])
        sections = config.get("sections", ["hero", "features", "cta"])
        colors = config.get("colors", COLOR_PALETTES["modern"])
        custom_content = config.get("custom_content", {})
        
        # Generate pages
        pages_out = []
        for page_name in pages:
            page_html = self._generate_page(
                page_name, brand, tagline, sections, colors, content, custom_content
            )
            pages_out.append({
                "name": page_name,
                "filename": f"{page_name}.html",
                "html": page_html,
                "title": page_name.title(),
            })
        
        return {
            "pages": pages_out,
            "site_name": brand,
            "site_type": self.site_type,
            "page_count": len(pages_out),
            "success": True,
            "metadata": {
                "brand": brand,
                "tagline": tagline,
                "colors": colors,
                "pages": pages,
            }
        }
    
    def _generate_page(self, page_name: str, brand: str, tagline: str, 
                      sections: List[str], colors: Dict, 
                      content: Dict, custom: Dict) -> str:
        """Generate a single page HTML"""
        
        nav_html = self._build_navbar(brand, colors)
        sections_html = ""
        
        for section in sections:
            if section == "hero":
                sections_html += self._build_hero(content, colors, custom)
            elif section == "features":
                sections_html += self._build_features(content, colors)
            elif section == "pricing":
                sections_html += self._build_pricing(colors)
            elif section == "testimonials":
                sections_html += self._build_testimonials(colors)
            elif section == "cta":
                sections_html += self._build_cta(content, colors)
            elif section == "faq":
                sections_html += self._build_faq(colors)
        
        footer_html = self._build_footer(brand, colors)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{brand} · {page_name.title()}</title>
<meta name="description" content="{tagline}">
<style>
{self._build_css(colors)}
</style>
</head>
<body>
{nav_html}
<main>
{sections_html}
</main>
{footer_html}
<script>{self._build_js()}</script>
</body>
</html>"""
    
    def _build_navbar(self, brand: str, colors: Dict) -> str:
        """Build navigation bar"""
        return f"""<nav style="
            display:flex; justify-content:space-between; align-items:center;
            padding:1rem 5%; background:#fff; border-bottom:1px solid #e5e7eb;
            position:sticky; top:0; z-index:100;
        ">
            <div style="font-size:1.5rem; font-weight:bold; color:{colors['primary']}">
                {_html.escape(brand)}
            </div>
            <div style="display:flex; gap:2rem; align-items:center;">
                <a href="#home" style="color:#4b5563; text-decoration:none; font-weight:500">Home</a>
                <a href="#about" style="color:#4b5563; text-decoration:none; font-weight:500">About</a>
                <a href="#services" style="color:#4b5563; text-decoration:none; font-weight:500">Services</a>
                <a href="#contact" style="color:#4b5563; text-decoration:none; font-weight:500">Contact</a>
                <button style="
                    background:{colors['primary']}; color:white;
                    border:none; padding:0.5rem 1.5rem; border-radius:0.375rem;
                    cursor:pointer; font-weight:600;
                ">Get Started</button>
            </div>
        </nav>"""
    
    def _build_hero(self, content: Dict, colors: Dict, custom: Dict) -> str:
        """Build hero section"""
        title = custom.get("hero_title") or self.random.choice(content.get("hero_titles", ["Welcome"]))
        subtitle = custom.get("hero_subtitle") or self.random.choice(content.get("hero_subs", ["Your message"]))
        cta_text = custom.get("cta_text") or self.random.choice(content.get("cta_texts", ["Get Started"]))
        
        return f"""<section id="hero" style="
            background:linear-gradient(135deg, {colors['primary']}20, {colors['secondary']}20);
            padding:6rem 5%; text-align:center; min-height:70vh;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
        ">
            <h1 style="
                font-size:3.5rem; font-weight:800; margin-bottom:1rem;
                color:#1a202c; letter-spacing:-0.02em;
            ">{_html.escape(title)}</h1>
            <p style="
                font-size:1.25rem; color:#4b5563; margin-bottom:2rem;
                max-width:600px; line-height:1.6;
            ">{_html.escape(subtitle)}</p>
            <div style="display:flex; gap:1rem; justify-content:center; flex-wrap:wrap;">
                <button style="
                    background:{colors['primary']}; color:white;
                    border:none; padding:0.75rem 2rem; border-radius:0.5rem;
                    font-weight:600; cursor:pointer; font-size:1rem;
                ">{_html.escape(cta_text)}</button>
                <button style="
                    background:transparent; color:{colors['primary']};
                    border:2px solid {colors['primary']}; padding:0.75rem 2rem; 
                    border-radius:0.5rem; font-weight:600; cursor:pointer; font-size:1rem;
                ">Learn More</button>
            </div>
        </section>"""
    
    def _build_features(self, content: Dict, colors: Dict) -> str:
        """Build features grid"""
        features = content.get("features", [])[:6]
        features_html = ""
        
        for title, desc in features:
            features_html += f"""<div style="
                padding:2rem; background:#fff; border:1px solid #e5e7eb;
                border-radius:0.5rem; text-align:center;
            ">
                <div style="font-size:2rem; margin-bottom:0.5rem; color:{colors['primary']}">✨</div>
                <h3 style="font-weight:700; margin-bottom:0.5rem; color:#1a202c;">
                    {_html.escape(title)}
                </h3>
                <p style="color:#6b7280; line-height:1.6;">{_html.escape(desc)}</p>
            </div>"""
        
        return f"""<section id="features" style="padding:4rem 5%; background:#f9fafb;">
            <h2 style="font-size:2.5rem; font-weight:800; margin-bottom:1rem; text-align:center; color:#1a202c;">
                Why Choose Us
            </h2>
            <p style="text-align:center; color:#6b7280; margin-bottom:3rem; max-width:600px; margin-left:auto; margin-right:auto;">
                Everything you need to succeed
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">
                {features_html}
            </div>
        </section>"""
    
    def _build_pricing(self, colors: Dict) -> str:
        """Build pricing section"""
        return f"""<section id="pricing" style="padding:4rem 5%; background:#fff;">
            <h2 style="font-size:2.5rem; font-weight:800; margin-bottom:3rem; text-align:center; color:#1a202c;">
                Simple Pricing
            </h2>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">
                <div style="border:2px solid {colors['primary']}; border-radius:0.5rem; padding:2rem; text-align:center;">
                    <h3 style="font-size:1.5rem; font-weight:700; margin-bottom:0.5rem;">Starter</h3>
                    <p style="font-size:2.5rem; font-weight:900; color:{colors['primary']}; margin:1rem 0;">Free</p>
                    <button style="width:100%; background:{colors['primary']}; color:white; border:none; padding:0.75rem; border-radius:0.375rem; font-weight:600; cursor:pointer;">Get Started</button>
                </div>
                <div style="border:2px solid {colors['primary']}; border-radius:0.5rem; padding:2rem; text-align:center; background:{colors['primary']}15;">
                    <h3 style="font-size:1.5rem; font-weight:700; margin-bottom:0.5rem;">Pro</h3>
                    <p style="font-size:2.5rem; font-weight:900; color:{colors['primary']}; margin:1rem 0;">₹999<span style="font-size:1rem;">/mo</span></p>
                    <button style="width:100%; background:{colors['primary']}; color:white; border:none; padding:0.75rem; border-radius:0.375rem; font-weight:600; cursor:pointer;">Choose Plan</button>
                </div>
                <div style="border:2px solid {colors['primary']}; border-radius:0.5rem; padding:2rem; text-align:center;">
                    <h3 style="font-size:1.5rem; font-weight:700; margin-bottom:0.5rem;">Enterprise</h3>
                    <p style="font-size:2.5rem; font-weight:900; color:{colors['primary']}; margin:1rem 0;">Custom</p>
                    <button style="width:100%; background:{colors['primary']}; color:white; border:none; padding:0.75rem; border-radius:0.375rem; font-weight:600; cursor:pointer;">Contact Us</button>
                </div>
            </div>
        </section>"""
    
    def _build_testimonials(self, colors: Dict) -> str:
        """Build testimonials section"""
        testimonials = [
            ("Rohan Mehta", "CEO", "Absolutely transformed how we work. Highly recommend!"),
            ("Priya Sharma", "Marketing Lead", "Incredible quality and amazing support."),
            ("Amit Singh", "Freelancer", "Best decision I made. Results speak for themselves."),
        ]
        
        testi_html = ""
        for name, role, text in testimonials:
            testi_html += f"""<div style="
                background:#fff; border:1px solid #e5e7eb; border-radius:0.5rem;
                padding:1.5rem;
            ">
                <p style="color:#6b7280; margin-bottom:1rem; font-size:1rem;">
                    "{_html.escape(text)}"
                </p>
                <div style="font-weight:700; color:#1a202c;">{_html.escape(name)}</div>
                <div style="font-size:0.875rem; color:{colors['primary']};">{_html.escape(role)}</div>
            </div>"""
        
        return f"""<section id="testimonials" style="padding:4rem 5%; background:{colors['primary']}15;">
            <h2 style="font-size:2.5rem; font-weight:800; margin-bottom:3rem; text-align:center; color:#1a202c;">
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
    
    def _build_faq(self, colors: Dict) -> str:
        """Build FAQ section"""
        faqs = [
            ("How do I get started?", "Simply sign up and follow the onboarding guide."),
            ("Is there a free trial?", "Yes, 14 days free - no credit card required."),
            ("Can I cancel anytime?", "Absolutely, cancel anytime with no questions."),
        ]
        
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
        
        return f"""<section id="faq" style="padding:4rem 5%; background:#f9fafb;">
            <h2 style="font-size:2.5rem; font-weight:800; margin-bottom:3rem; text-align:center; color:#1a202c;">
                Frequently Asked Questions
            </h2>
            <div style="max-width:600px; margin:0 auto;">
                {faq_html}
            </div>
        </section>"""
    
    def _build_footer(self, brand: str, colors: Dict) -> str:
        """Build footer"""
        return f"""<footer style="
            background:#1a202c; color:white; padding:3rem 5%;
            border-top:1px solid {colors['primary']};
        ">
            <div style="max-width:1200px; margin:0 auto; display:grid; grid-template-columns:repeat(4, 1fr); gap:2rem; margin-bottom:2rem;">
                <div>
                    <div style="font-weight:700; margin-bottom:1rem; color:{colors['primary']};">
                        {_html.escape(brand)}
                    </div>
                    <p style="color:#9ca3af; font-size:0.875rem;">Building beautiful digital products.</p>
                </div>
                <div>
                    <div style="font-weight:700; margin-bottom:1rem;">Product</div>
                    <div style="display:flex; flex-direction:column; gap:0.5rem;">
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Features</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Pricing</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Updates</a>
                    </div>
                </div>
                <div>
                    <div style="font-weight:700; margin-bottom:1rem;">Company</div>
                    <div style="display:flex; flex-direction:column; gap:0.5rem;">
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">About</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Blog</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Contact</a>
                    </div>
                </div>
                <div>
                    <div style="font-weight:700; margin-bottom:1rem;">Legal</div>
                    <div style="display:flex; flex-direction:column; gap:0.5rem;">
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Privacy</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">Terms</a>
                        <a href="#" style="color:#9ca3af; text-decoration:none; font-size:0.875rem;">License</a>
                    </div>
                </div>
            </div>
            <div style="border-top:1px solid #374151; padding-top:2rem; text-align:center; color:#9ca3af; font-size:0.875rem;">
                © 2024 {_html.escape(brand)}. All rights reserved.
            </div>
        </footer>"""
    
    def _build_css(self, colors: Dict) -> str:
        """Build base CSS"""
        return f"""
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a202c; }}
        a {{ color: {colors['primary']}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        button:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        section {{ scroll-margin-top: 80px; }}
        @media (max-width: 768px) {{
            nav {{ flex-direction: column; gap: 1rem; }}
            h1 {{ font-size: 2rem; }}
            h2 {{ font-size: 1.75rem; }}
            section {{ padding: 2rem 1rem !important; }}
        }}
        """
    
    def _build_js(self) -> str:
        """Build base JavaScript"""
        return """
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if(target) target.scrollIntoView({ behavior: 'smooth' });
            });
        });
        """


def generate_site_local(config: Dict[str, Any]) -> Dict[str, Any]:
    """Public API: Generate site locally (NO external APIs)"""
    site_type = config.get("site_type", "landing")
    seed = config.get("seed", 0)
    
    engine = LocalTemplateEngine(site_type, seed)
    result = engine.generate_site(config)
    
    # Convert pages to HTML format
    pages_html = []
    for page in result.get("pages", []):
        pages_html.append({
            "filename": page["filename"],
            "html": page["html"],
        })
    
    return {
        "pages": pages_html,
        "site_name": result.get("site_name"),
        "site_type": result.get("site_type"),
        "page_count": len(pages_html),
        "success": True,
    }
