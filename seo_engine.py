"""
SEO Optimization Engine - Generate SEO-optimized HTML
Pure Python - NO external APIs
"""

import re
import json
from typing import Dict, List, Optional
from urllib.parse import quote

class SEOOptimizer:
    """Generate SEO metadata and optimize HTML for search engines"""
    
    def __init__(self):
        self.keyword_density_target = 0.02  # 2%
        self.min_title_length = 30
        self.max_title_length = 60
        self.min_description_length = 120
        self.max_description_length = 160
    
    def optimize_html(self, html: str, config: Dict) -> str:
        """Add SEO optimizations to HTML"""
        brand = config.get("brand", "Your Brand")
        tagline = config.get("tagline", "")
        site_type = config.get("site_type", "landing")
        
        # Generate metadata
        title = self._generate_title(brand, site_type)
        description = self._generate_description(brand, tagline, site_type)
        keywords = self._generate_keywords(site_type)
        
        # Create head content
        head_content = f"""
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{self._escape_html(title)}</title>
        <meta name="description" content="{self._escape_html(description)}">
        <meta name="keywords" content="{self._escape_html(keywords)}">
        <meta name="author" content="{self._escape_html(brand)}">
        <meta property="og:title" content="{self._escape_html(title)}">
        <meta property="og:description" content="{self._escape_html(description)}">
        <meta property="og:type" content="website">
        <meta property="og:site_name" content="{self._escape_html(brand)}">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{self._escape_html(title)}">
        <meta name="twitter:description" content="{self._escape_html(description)}">
        <meta name="robots" content="index, follow">
        <link rel="canonical" href="https://example.com/">
        <meta name="theme-color" content="#2563eb">
        {self._generate_schema_markup(brand, site_type)}
        """
        
        # Insert into HTML
        html = html.replace("</head>", head_content + "</head>")
        
        # Add semantic HTML improvements
        html = self._improve_semantic_html(html)
        
        # Add sitemap reference
        html = html.replace("</head>", '<link rel="sitemap" href="/sitemap.xml"></head>')
        
        return html
    
    def _generate_title(self, brand: str, site_type: str) -> str:
        """Generate SEO-optimized page title"""
        templates = {
            "ecommerce": f"{brand} - Premium Online Shopping | Best Deals & Free Shipping",
            "restaurant": f"{brand} - Book Your Table | Fine Dining & Amazing Food",
            "portfolio": f"{brand} - Web Designer & Developer | Creative Solutions",
            "saas": f"{brand} - Software Platform | Productivity & Collaboration",
            "blog": f"{brand} - Blog | Industry Insights & Updates",
            "gym": f"{brand} - Fitness Center | Professional Training & Facilities",
            "agency": f"{brand} - Creative Agency | Design & Marketing Solutions",
            "default": f"{brand} - Welcome | Discover Amazing Services"
        }
        
        title = templates.get(site_type, templates["default"])
        
        # Ensure it's within character limits
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length-3] + "..."
        
        return title
    
    def _generate_description(self, brand: str, tagline: str, site_type: str) -> str:
        """Generate SEO-optimized meta description"""
        if tagline:
            desc = tagline
        else:
            templates = {
                "ecommerce": f"Shop {brand} for premium products with free shipping and easy returns.",
                "restaurant": f"Discover {brand} - Award-winning cuisine and fine dining experience.",
                "portfolio": f"{brand} offers professional web design and development services.",
                "saas": f"Manage your business with {brand} - Powerful, easy-to-use software.",
                "blog": f"Read latest insights and articles on {brand}.",
                "gym": f"Join {brand} and transform your fitness journey with expert trainers.",
                "agency": f"{brand} - Creative solutions for modern businesses.",
                "default": f"Explore {brand} - Your destination for quality and innovation."
            }
            desc = templates.get(site_type, templates["default"])
        
        # Ensure it's within character limits
        if len(desc) > self.max_description_length:
            desc = desc[:self.max_description_length-3] + "..."
        elif len(desc) < self.min_description_length:
            desc = desc + " Contact us today for more information."
        
        return desc
    
    def _generate_keywords(self, site_type: str) -> str:
        """Generate relevant keywords based on site type"""
        keywords_map = {
            "ecommerce": "online shopping, buy online, best deals, free shipping, products",
            "restaurant": "restaurant, dining, food, reservation, menu, cuisine",
            "portfolio": "web design, development, portfolio, freelancer, services",
            "saas": "software, platform, productivity, business tools, automation",
            "blog": "blog, articles, insights, news, updates, industry",
            "gym": "gym, fitness, training, exercise, health, workout",
            "agency": "agency, creative, marketing, design, branding",
            "default": "business, services, products, solutions, quality"
        }
        
        return keywords_map.get(site_type, keywords_map["default"])
    
    def _generate_schema_markup(self, brand: str, site_type: str) -> str:
        """Generate JSON-LD structured data for rich snippets"""
        if site_type == "ecommerce":
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": brand,
                "url": "https://example.com",
                "sameAs": [
                    "https://www.facebook.com/example",
                    "https://www.instagram.com/example",
                ],
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "IN"
                }
            }
        elif site_type == "restaurant":
            schema = {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                "name": brand,
                "url": "https://example.com",
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "IN"
                },
                "priceRange": "₹₹",
                "servesCuisine": "Indian"
            }
        else:
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": brand,
                "url": "https://example.com",
            }
        
        return f'<script type="application/ld+json">{json.dumps(schema)}</script>'
    
    def _improve_semantic_html(self, html: str) -> str:
        """Improve semantic HTML structure"""
        # Ensure main content is wrapped in <main>
        if '<main' not in html:
            html = html.replace('<body>', '<body><main>', 1)
            html = html.replace('</body>', '</main></body>', 1)
        
        # Add article tags where appropriate
        html = re.sub(r'<section[^>]*>(.*?)</section>', r'<article>\1</article>', html)
        
        # Ensure images have alt text
        def add_alt_to_img(match):
            img_tag = match.group(0)
            if 'alt=' not in img_tag:
                img_tag = img_tag.replace('>', ' alt="Product image">', 1)
            return img_tag
        
        html = re.sub(r'<img[^>]*>', add_alt_to_img, html)
        
        return html
    
    def generate_sitemap_xml(self, pages: List[Dict]) -> str:
        """Generate sitemap.xml for search engines"""
        urls = []
        
        for page in pages:
            url = {
                "loc": f"https://example.com/{page.get('filename', 'index.html')}",
                "lastmod": "2024-01-15",
                "changefreq": "weekly",
                "priority": "0.8" if page.get('filename') == 'index.html' else "0.6"
            }
            urls.append(url)
        
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{url["loc"]}</loc>\n'
            sitemap += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
            sitemap += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
            sitemap += f'    <priority>{url["priority"]}</priority>\n'
            sitemap += '  </url>\n'
        
        sitemap += '</urlset>'
        
        return sitemap
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt"""
        return """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
"""
    
    def analyze_seo_score(self, html: str, config: Dict) -> Dict:
        """Analyze and score SEO optimization"""
        score = 100
        issues = []
        
        # Check title
        title_match = re.search(r'<title>([^<]*)</title>', html)
        if not title_match:
            issues.append("Missing page title")
            score -= 20
        elif len(title_match.group(1)) < self.min_title_length:
            issues.append("Page title too short")
            score -= 10
        elif len(title_match.group(1)) > self.max_title_length:
            issues.append("Page title too long")
            score -= 5
        
        # Check meta description
        desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
        if not desc_match:
            issues.append("Missing meta description")
            score -= 15
        elif len(desc_match.group(1)) < self.min_description_length:
            issues.append("Meta description too short")
            score -= 10
        elif len(desc_match.group(1)) > self.max_description_length:
            issues.append("Meta description too long")
            score -= 5
        
        # Check H1 tags
        h1_tags = re.findall(r'<h1[^>]*>[^<]*</h1>', html)
        if len(h1_tags) == 0:
            issues.append("Missing H1 heading")
            score -= 15
        elif len(h1_tags) > 1:
            issues.append("Multiple H1 tags found")
            score -= 10
        
        # Check for keywords
        brand = config.get("brand", "")
        if brand and brand.lower() in html.lower():
            score += 5  # Bonus for brand mentions
        
        # Check alt text on images
        img_without_alt = len(re.findall(r'<img(?!.*alt=)[^>]*>', html))
        if img_without_alt > 0:
            issues.append(f"{img_without_alt} images missing alt text")
            score -= img_without_alt * 2
        
        # Check canonical URL
        if '<link rel="canonical"' not in html:
            issues.append("Missing canonical URL")
            score -= 10
        
        # Check structured data
        if 'application/ld+json' not in html:
            issues.append("Missing structured data (Schema.org)")
            score -= 10
        
        # Determine SEO level
        if score >= 90:
            level = "Excellent"
        elif score >= 70:
            level = "Good"
        elif score >= 50:
            level = "Fair"
        else:
            level = "Needs Improvement"
        
        return {
            "score": max(0, score),
            "level": level,
            "issues": issues,
            "recommendations": self._get_recommendations(issues),
        }
    
    def _get_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations for SEO improvement"""
        recommendations = []
        
        if "Missing page title" in issues:
            recommendations.append("Add a descriptive title (30-60 chars)")
        if "Meta description" in " ".join(issues):
            recommendations.append("Add a meta description (120-160 chars)")
        if "Missing H1" in issues:
            recommendations.append("Add one main H1 heading per page")
        if "alt text" in " ".join(issues):
            recommendations.append("Add descriptive alt text to all images")
        if "canonical" in " ".join(issues):
            recommendations.append("Add canonical URL to prevent duplicate content")
        if "structured data" in " ".join(issues):
            recommendations.append("Add JSON-LD structured data for rich snippets")
        
        return recommendations
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        return text


def optimize_html_seo(html: str, config: Dict) -> str:
    """Public API: Optimize HTML for SEO"""
    optimizer = SEOOptimizer()
    return optimizer.optimize_html(html, config)


def analyze_seo(html: str, config: Dict) -> Dict:
    """Public API: Analyze SEO score"""
    optimizer = SEOOptimizer()
    return optimizer.analyze_seo_score(html, config)


def generate_sitemap(pages: List[Dict]) -> str:
    """Public API: Generate sitemap.xml"""
    optimizer = SEOOptimizer()
    return optimizer.generate_sitemap_xml(pages)


def generate_robots_txt_content() -> str:
    """Public API: Generate robots.txt"""
    optimizer = SEOOptimizer()
    return optimizer.generate_robots_txt()
