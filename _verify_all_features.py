from prompt_parser import parse_prompt
from local_engine import generate_site_local
from component_exporter import export_modular_react

prompt = """
modern saas website apple style
font: Poppins
heading font: Montserrat
bold headings
animation: premium
image style: abstract
header options: Home, Services, Pricing, Contact
order: hero, features, pricing, testimonials, contact
services: SEO - Rank faster, Ads - More leads, Branding - Build trust
pricing: Basic 499, Pro 999/mo, Enterprise Custom
phone: +91 98765 43210
email: hello@brand.com
address: Mumbai, India
testimonials: Rahul, CEO - Amazing results | Neha - Loved the UI
hero title: Growth Engine
hero cta: Start Now
backgroundd image
"""

cfg = parse_prompt(prompt)
html = generate_site_local(cfg)["pages"][0]["html"]
mods = export_modular_react(cfg, html)

checks = {
    "seo_card": "Rank faster" in html,
    "pricing_pro": "Pro" in html and "999" in html,
    "phone": "98765" in html,
    "testimonial": "Amazing results" in html,
    "poppins": "Poppins" in html or "poppins" in html.lower(),
    "animation_premium": cfg["style"].get("animation") == "premium",
    "section_order": cfg["sections"].index("features") < cfg["sections"].index("pricing"),
    "modular_files": "src/components/HeroSection.tsx" in mods,
    "bg_image": cfg["style"].get("use_bg_image"),
}
print("ALL_OK", all(checks.values()))
for k, v in checks.items():
    print(k, v)
