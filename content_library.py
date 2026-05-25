"""
Content Library - Pre-built content for all site types
Phase 2: Content Management System
NO external APIs - Pure Python content database
"""

from typing import Dict, List, Optional
import json
from dataclasses import dataclass, asdict

@dataclass
class ContentItem:
    """Single content item"""
    id: str
    category: str
    type: str  # hero_title, feature, cta, testimonial, etc.
    content: str
    metadata: Dict = None
    tags: List[str] = None
    
    def to_dict(self):
        return asdict(self)


class ContentLibrary:
    """Pre-built content database for all site types and industries"""
    
    def __init__(self):
        self.content = self._load_content_library()
        self.translations = self._load_translations()
    
    def _load_content_library(self) -> Dict[str, Dict]:
        """Pre-built content for all site types"""
        return {
            # ──────────────────────────────────────────────────────
            # ECOMMERCE
            # ──────────────────────────────────────────────────────
            "ecommerce": {
                "hero_titles": [
                    "Shop the Best Selection Online",
                    "Premium Products at Unbeatable Prices",
                    "Your One-Stop Shop for Everything You Need",
                    "Discover Quality Merchandise Today",
                    "Shop Smart, Save More",
                ],
                "hero_subtitles": [
                    "Fast shipping & easy returns on all orders",
                    "Trusted by millions of satisfied customers",
                    "Browse thousands of products from your favorites brands",
                    "Quality guaranteed or your money back",
                    "Shop now and save up to 50%",
                ],
                "features": [
                    "Fast & Free Shipping Over $50",
                    "Easy 30-Day Returns",
                    "Secure Payment Processing",
                    "24/7 Customer Support",
                    "Exclusive Member Discounts",
                    "Quality Guarantee",
                ],
                "cta_primary": [
                    "Shop Now",
                    "Browse Collection",
                    "Start Shopping",
                    "Explore Our Store",
                    "View All Products",
                ],
                "cta_secondary": [
                    "View Details",
                    "Learn More",
                    "Add to Cart",
                    "Check Availability",
                    "See More",
                ],
                "testimonials": [
                    "Amazing selection and fast delivery. Highly recommend!",
                    "Best prices I've found online. Great customer service.",
                    "High quality products and easy checkout process.",
                    "I'm impressed with the variety and value for money.",
                    "Fast shipping and packaging is excellent.",
                ],
                "pricing_tiers": [
                    {"name": "Basic", "price": "$9.99", "features": ["Free Shipping", "30 Days Return"]},
                    {"name": "Pro", "price": "$19.99", "features": ["Priority Shipping", "60 Days Return", "Exclusive Deals"]},
                    {"name": "Premium", "price": "$49.99", "features": ["Next Day Shipping", "1 Year Return", "VIP Support", "Early Access"]},
                ],
                "newsletter_signup": "Get exclusive deals delivered to your inbox",
            },
            
            # ──────────────────────────────────────────────────────
            # SAAS (Software as a Service)
            # ──────────────────────────────────────────────────────
            "saas": {
                "hero_titles": [
                    "Build More, Manage Less",
                    "Enterprise-Grade Software Made Simple",
                    "The Platform Built for Your Growth",
                    "Transform Your Workflow",
                    "Work Smarter with Intelligent Tools",
                ],
                "hero_subtitles": [
                    "Increase productivity by 300% with our intelligent automation",
                    "Used by 10,000+ companies worldwide",
                    "Start free, scale as you grow",
                    "Trusted by industry leaders",
                    "Everything you need to succeed in one platform",
                ],
                "features": [
                    "Real-Time Collaboration",
                    "Advanced Analytics & Reporting",
                    "AI-Powered Insights",
                    "Seamless Integrations",
                    "Enterprise Security",
                    "99.9% Uptime SLA",
                ],
                "cta_primary": [
                    "Start Free Trial",
                    "Get Started Today",
                    "Try It Now",
                    "Sign Up Free",
                    "Request Demo",
                ],
                "cta_secondary": [
                    "Schedule a Demo",
                    "View Pricing",
                    "Learn More",
                    "Contact Sales",
                    "Download Resources",
                ],
                "testimonials": [
                    "This platform transformed how our team works. ROI in first month.",
                    "Best investment we've made. Saves us 20 hours per week.",
                    "Incredible support and constant innovation.",
                    "The UI is intuitive and powerful at the same time.",
                    "Scaled from 10 to 1000 users without a hitch.",
                ],
                "pricing_tiers": [
                    {"name": "Starter", "price": "$29/month", "features": ["Up to 5 Users", "Basic Analytics", "Email Support"]},
                    {"name": "Professional", "price": "$99/month", "features": ["Unlimited Users", "Advanced Analytics", "Priority Support", "Custom Integrations"]},
                    {"name": "Enterprise", "price": "Custom", "features": ["Dedicated Support", "Custom SLA", "On-Premise Option", "Advanced Security"]},
                ],
                "newsletter_signup": "Stay updated with product news and tips",
            },
            
            # ──────────────────────────────────────────────────────
            # BLOG
            # ──────────────────────────────────────────────────────
            "blog": {
                "hero_titles": [
                    "Insights, Stories & Expertise",
                    "Discover What's Next in the Industry",
                    "Expert Perspectives on What Matters",
                    "Latest Trends & Deep Dives",
                    "Where Ideas Come to Life",
                ],
                "hero_subtitles": [
                    "Thought leadership from industry experts",
                    "Stay ahead with weekly insights",
                    "Subscribe to never miss a story",
                    "Written by professionals, for professionals",
                    "Curated content you'll actually want to read",
                ],
                "features": [
                    "Weekly Expert Articles",
                    "In-Depth Case Studies",
                    "Industry Research & Data",
                    "Podcast Series",
                    "Downloadable Resources",
                    "Community Forum",
                ],
                "cta_primary": [
                    "Read Our Blog",
                    "Explore Stories",
                    "Browse Articles",
                    "Start Reading",
                    "View Latest Posts",
                ],
                "cta_secondary": [
                    "Subscribe to Newsletter",
                    "Share This Article",
                    "Read Full Story",
                    "Add to Reading List",
                    "Follow Us",
                ],
                "testimonials": [
                    "The best content in our industry. I read every article.",
                    "Consistently valuable insights that help my work.",
                    "This blog has become my go-to source for information.",
                    "Well-researched articles with actionable advice.",
                    "The stories here truly inspire and educate.",
                ],
                "newsletter_signup": "Get new articles delivered weekly",
                "post_categories": ["Technology", "Business", "Innovation", "Trends", "How-To", "Case Studies"],
            },
            
            # ──────────────────────────────────────────────────────
            # PORTFOLIO
            # ──────────────────────────────────────────────────────
            "portfolio": {
                "hero_titles": [
                    "Creative Work. Bold Ideas. Real Results.",
                    "Bringing Visions to Life",
                    "Design & Development Excellence",
                    "Your Brand, Elevated",
                    "Where Creativity Meets Strategy",
                ],
                "hero_subtitles": [
                    "10+ years of award-winning design experience",
                    "Helping brands stand out in a crowded market",
                    "From concept to launch, we've got you covered",
                    "Trusted by leading companies worldwide",
                    "Let's create something extraordinary together",
                ],
                "features": [
                    "Brand Strategy & Design",
                    "Web & Mobile Development",
                    "Digital Marketing",
                    "UX/UI Design",
                    "Content Creation",
                    "Project Management",
                ],
                "cta_primary": [
                    "View My Work",
                    "Browse Projects",
                    "See the Portfolio",
                    "Explore My Work",
                    "Check Out Projects",
                ],
                "cta_secondary": [
                    "Get In Touch",
                    "Discuss Your Project",
                    "Schedule Consultation",
                    "Send a Message",
                    "Let's Work Together",
                ],
                "testimonials": [
                    "Outstanding work and professionalism. Highly recommended.",
                    "They understood our vision and delivered beyond expectations.",
                    "Best designer I've worked with. Incredible attention to detail.",
                    "Transformed our brand completely. Worth every penny.",
                    "Responsive, creative, and a pleasure to work with.",
                ],
                "services": ["Branding", "Web Design", "App Design", "Illustration", "Motion Graphics", "Consulting"],
            },
            
            # ──────────────────────────────────────────────────────
            # RESTAURANT
            # ──────────────────────────────────────────────────────
            "restaurant": {
                "hero_titles": [
                    "Taste the Difference",
                    "Farm to Table Excellence",
                    "Culinary Perfection in Every Bite",
                    "Where Great Food Brings People Together",
                    "Experience Authentic Flavors",
                ],
                "hero_subtitles": [
                    "Award-winning cuisine from our chef",
                    "Fresh ingredients, time-honored recipes",
                    "Join us for an unforgettable dining experience",
                    "Reservations now available for intimate gatherings",
                    "Celebrating 15 years of culinary excellence",
                ],
                "features": [
                    "Farm-Fresh Ingredients",
                    "Expert Chef Team",
                    "Cozy Ambiance",
                    "Private Event Space",
                    "Wine Selection",
                    "Seasonal Menus",
                ],
                "cta_primary": [
                    "Make a Reservation",
                    "Book Your Table",
                    "Reserve Now",
                    "Check Availability",
                    "Plan Your Visit",
                ],
                "cta_secondary": [
                    "View Menu",
                    "See Food Photos",
                    "Special Events",
                    "Delivery Info",
                    "Catering Options",
                ],
                "testimonials": [
                    "Best meal we've had in years. Absolutely delicious!",
                    "The atmosphere is perfect for a special night out.",
                    "Every dish was perfectly prepared. Exceptional service.",
                    "We've been coming here for 5 years. Never disappointed.",
                    "Worth the wait. Truly exceptional dining experience.",
                ],
                "hours": {
                    "monday_friday": "11:00 AM - 10:00 PM",
                    "saturday": "12:00 PM - 11:00 PM",
                    "sunday": "12:00 PM - 9:00 PM",
                },
                "cuisines": ["Italian", "French", "Japanese", "Mediterranean", "Modern American"],
            },
            
            # ──────────────────────────────────────────────────────
            # GYM/FITNESS
            # ──────────────────────────────────────────────────────
            "gym": {
                "hero_titles": [
                    "Transform Your Body. Transform Your Life.",
                    "Your Fitness Journey Starts Here",
                    "Build the Body You've Always Wanted",
                    "More Than Just a Gym",
                    "Achieve Your Fitness Goals",
                ],
                "hero_subtitles": [
                    "State-of-the-art equipment and expert trainers",
                    "Join 5,000+ members on their fitness journey",
                    "Personalized training programs for every goal",
                    "Community-focused fitness experience",
                    "Free consultation with our certified trainers",
                ],
                "features": [
                    "Premium Equipment",
                    "Personal Training",
                    "Group Classes",
                    "Nutritionist Consultation",
                    "Recovery Facilities",
                    "24/7 Access",
                ],
                "cta_primary": [
                    "Start Your Free Trial",
                    "Join Now",
                    "Get Started Today",
                    "Sign Up for Membership",
                    "Begin Your Transformation",
                ],
                "cta_secondary": [
                    "View Class Schedule",
                    "Meet Our Trainers",
                    "Check Pricing",
                    "Book a Session",
                    "Tour Our Facility",
                ],
                "testimonials": [
                    "Best decision I made for my health. Incredible results in 3 months!",
                    "The trainers here are knowledgeable and motivating.",
                    "Great community and world-class equipment.",
                    "Flexible schedules and a welcoming atmosphere.",
                    "Transformed my life. Highly recommended to everyone.",
                ],
                "membership_levels": ["Basic", "Premium", "VIP"],
                "class_types": ["CrossFit", "Yoga", "Spinning", "HIIT", "Boxing", "Pilates"],
            },
            
            # ──────────────────────────────────────────────────────
            # AGENCY
            # ──────────────────────────────────────────────────────
            "agency": {
                "hero_titles": [
                    "Strategy. Creativity. Results.",
                    "Your Growth Partner",
                    "We Build Brands That Matter",
                    "Let's Create Your Success Story",
                    "Digital Excellence Delivered",
                ],
                "hero_subtitles": [
                    "Award-winning creative agency specializing in growth",
                    "Trusted by Fortune 500 companies",
                    "From strategy to execution, we deliver results",
                    "Your vision, our expertise",
                    "Let's accelerate your growth together",
                ],
                "features": [
                    "Brand Strategy",
                    "Creative Direction",
                    "Digital Marketing",
                    "Web Development",
                    "Analytics & Optimization",
                    "Content Strategy",
                ],
                "cta_primary": [
                    "Let's Work Together",
                    "Start a Project",
                    "Get a Proposal",
                    "Schedule Consultation",
                    "Discuss Your Vision",
                ],
                "cta_secondary": [
                    "View Our Work",
                    "Case Studies",
                    "See Our Process",
                    "Meet the Team",
                    "Download Portfolio",
                ],
                "testimonials": [
                    "They exceeded our expectations on every level.",
                    "Brought fresh perspective and delivered amazing results.",
                    "Professional, creative, and results-driven.",
                    "This agency truly understands our business.",
                    "Transformed our brand and boosted our sales.",
                ],
                "services": ["Branding", "Digital Strategy", "Content", "Design", "Development", "Marketing"],
            },
        }
    
    def _load_translations(self) -> Dict[str, Dict]:
        """Multi-language support"""
        return {
            "en": {
                "footer_copyright": "© 2024 All rights reserved.",
                "footer_privacy": "Privacy Policy",
                "footer_terms": "Terms of Service",
                "footer_contact": "Contact Us",
                "newsletter_placeholder": "Enter your email",
                "newsletter_button": "Subscribe",
                "subscribe_success": "Thank you for subscribing!",
            },
            "es": {
                "footer_copyright": "© 2024 Todos los derechos reservados.",
                "footer_privacy": "Política de Privacidad",
                "footer_terms": "Términos de Servicio",
                "footer_contact": "Contáctenos",
                "newsletter_placeholder": "Ingresa tu correo",
                "newsletter_button": "Suscribirse",
                "subscribe_success": "¡Gracias por suscribirse!",
            },
            "fr": {
                "footer_copyright": "© 2024 Tous droits réservés.",
                "footer_privacy": "Politique de Confidentialité",
                "footer_terms": "Conditions d'Utilisation",
                "footer_contact": "Nous Contacter",
                "newsletter_placeholder": "Entrez votre email",
                "newsletter_button": "S'abonner",
                "subscribe_success": "Merci de vous être abonné!",
            },
            "de": {
                "footer_copyright": "© 2024 Alle Rechte vorbehalten.",
                "footer_privacy": "Datenschutz",
                "footer_terms": "Nutzungsbedingungen",
                "footer_contact": "Kontaktieren Sie uns",
                "newsletter_placeholder": "Geben Sie Ihre E-Mail ein",
                "newsletter_button": "Abonnieren",
                "subscribe_success": "Vielen Dank für Ihr Abonnement!",
            },
        }
    
    def get_content(self, site_type: str, content_type: str, language: str = "en") -> Optional[List[str]]:
        """Get content by site type and content type"""
        if site_type not in self.content:
            return None
        
        site_content = self.content[site_type]
        if content_type not in site_content:
            return None
        
        content_items = site_content[content_type]
        
        # Return as list if it's a list, otherwise wrap in list
        if isinstance(content_items, list):
            return content_items
        return [content_items]
    
    def get_random_content(self, site_type: str, content_type: str) -> Optional[str]:
        """Get random content item"""
        items = self.get_content(site_type, content_type)
        if not items:
            return None
        
        import random
        return random.choice(items)
    
    def get_all_content_for_site(self, site_type: str) -> Optional[Dict]:
        """Get all content for a site type"""
        return self.content.get(site_type)
    
    def search_content(self, keyword: str, site_type: Optional[str] = None) -> List[Dict]:
        """Search content by keyword"""
        results = []
        
        search_targets = [self.content.get(site_type)] if site_type else self.content.values()
        
        for site_content in search_targets:
            if not site_content:
                continue
            
            for content_type, items in site_content.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, str) and keyword.lower() in item.lower():
                            results.append({
                                "type": content_type,
                                "content": item,
                                "keyword_match": True,
                            })
                elif isinstance(items, str) and keyword.lower() in items.lower():
                    results.append({
                        "type": content_type,
                        "content": items,
                        "keyword_match": True,
                    })
        
        return results
    
    def add_custom_content(self, site_type: str, content_type: str, content: str) -> bool:
        """Add custom content (for user-provided content)"""
        if site_type not in self.content:
            self.content[site_type] = {}
        
        if content_type not in self.content[site_type]:
            self.content[site_type][content_type] = []
        
        if isinstance(self.content[site_type][content_type], list):
            self.content[site_type][content_type].append(content)
        else:
            # Convert to list if single item
            existing = self.content[site_type][content_type]
            self.content[site_type][content_type] = [existing, content]
        
        return True
    
    def export_content_json(self) -> str:
        """Export content library as JSON"""
        return json.dumps(self.content, indent=2)
    
    def export_translations_json(self) -> str:
        """Export translations as JSON"""
        return json.dumps(self.translations, indent=2)
    
    def get_translation(self, key: str, language: str = "en") -> str:
        """Get translated string"""
        if language not in self.translations:
            language = "en"
        
        return self.translations[language].get(key, key)
    
    def translate_site_content(self, content: Dict, language: str = "en") -> Dict:
        """Translate site content to specified language"""
        # For now, returns original - can be extended with full translation
        translated = content.copy()
        translated["language"] = language
        return translated


def create_library() -> ContentLibrary:
    """Factory function to create content library instance"""
    return ContentLibrary()


# Public API
library = ContentLibrary()
