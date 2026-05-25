"""
Email Template Generator - Generate professional email templates
Phase 2: Email marketing templates (MJML-compatible HTML)
NO external APIs - Pure Python email generation
"""

from typing import Dict, List, Optional
import json


class EmailTemplateGenerator:
    """Generate professional email templates"""
    
    def __init__(self):
        self.templates = self._load_email_templates()
    
    def _load_email_templates(self) -> Dict[str, Dict]:
        """Pre-built email template designs"""
        return {
            # ──────────────────────────────────────────────────────
            # WELCOME EMAIL
            # ──────────────────────────────────────────────────────
            "welcome": {
                "name": "Welcome Email",
                "subject": "Welcome to {brand}!",
                "preview": "We're excited to have you here",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#2563eb",
                        "text_color": "#ffffff",
                        "title": "Welcome to {brand}!",
                        "subtitle": "We're thrilled to have you on board",
                    },
                    {
                        "type": "content",
                        "body": """
                            <h2>Hello {first_name},</h2>
                            <p>Thank you for joining {brand}. We're excited to help you {value_proposition}.</p>
                            <p>Here's what you can do next:</p>
                            <ul>
                                <li>Complete your profile to get personalized recommendations</li>
                                <li>Explore our getting started guide</li>
                                <li>Join our community forum</li>
                            </ul>
                        """,
                    },
                    {
                        "type": "cta",
                        "button_text": "Get Started",
                        "button_url": "{app_url}/welcome",
                        "button_color": "#2563eb",
                    },
                    {
                        "type": "footer",
                        "text": "Questions? Contact our support team at support@{domain}",
                    },
                ],
            },
            
            # ──────────────────────────────────────────────────────
            # NEWSLETTER
            # ──────────────────────────────────────────────────────
            "newsletter": {
                "name": "Weekly Newsletter",
                "subject": "Your weekly update from {brand}",
                "preview": "Top stories this week",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#1a202c",
                        "text_color": "#ffffff",
                        "title": "{brand} Weekly",
                        "subtitle": "Top stories and insights",
                    },
                    {
                        "type": "highlight",
                        "title": "Top Story",
                        "description": "{top_article}",
                        "image_url": "{top_image}",
                        "link_url": "{top_link}",
                    },
                    {
                        "type": "articles",
                        "title": "This Week's Articles",
                        "articles": [
                            {"title": "{article_1}", "link": "{link_1}"},
                            {"title": "{article_2}", "link": "{link_2}"},
                            {"title": "{article_3}", "link": "{link_3}"},
                        ],
                    },
                    {
                        "type": "cta",
                        "button_text": "Read More on the Blog",
                        "button_url": "{blog_url}",
                        "button_color": "#2563eb",
                    },
                    {
                        "type": "footer",
                        "text": "You're receiving this because you subscribed to {brand} newsletter. <a href='{unsubscribe_url}'>Unsubscribe</a>",
                    },
                ],
            },
            
            # ──────────────────────────────────────────────────────
            # PROMOTIONAL
            # ──────────────────────────────────────────────────────
            "promotional": {
                "name": "Promotional Offer",
                "subject": "Special Offer: {offer_title}",
                "preview": "Limited time {discount}% off",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#f59e0b",
                        "text_color": "#ffffff",
                        "title": "{offer_title}",
                        "subtitle": "Limited time only",
                    },
                    {
                        "type": "highlight",
                        "title": "Save {discount}%",
                        "description": "{offer_description}",
                        "highlight_color": "#f59e0b",
                    },
                    {
                        "type": "product_grid",
                        "products": [
                            {"name": "{product_1}", "price": "{price_1}", "image": "{image_1}"},
                            {"name": "{product_2}", "price": "{price_2}", "image": "{image_2}"},
                            {"name": "{product_3}", "price": "{price_3}", "image": "{image_3}"},
                        ],
                    },
                    {
                        "type": "cta",
                        "button_text": "Shop Now",
                        "button_url": "{shop_url}",
                        "button_color": "#f59e0b",
                    },
                    {
                        "type": "footer",
                        "text": "Offer expires on {expiry_date}. No coupon needed.",
                    },
                ],
            },
            
            # ──────────────────────────────────────────────────────
            # TRANSACTIONAL (ORDER CONFIRMATION)
            # ──────────────────────────────────────────────────────
            "order_confirmation": {
                "name": "Order Confirmation",
                "subject": "Order Confirmed: {order_id}",
                "preview": "Your order has been confirmed",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#10b981",
                        "text_color": "#ffffff",
                        "title": "Order Confirmed",
                        "subtitle": "Thank you for your purchase!",
                    },
                    {
                        "type": "order_details",
                        "order_id": "{order_id}",
                        "order_date": "{order_date}",
                        "total": "{total}",
                        "items": [
                            {"name": "{item_1}", "quantity": "{qty_1}", "price": "{price_1}"},
                            {"name": "{item_2}", "quantity": "{qty_2}", "price": "{price_2}"},
                        ],
                    },
                    {
                        "type": "shipping_info",
                        "title": "Shipping To",
                        "address": "{shipping_address}",
                        "estimated_delivery": "{delivery_date}",
                    },
                    {
                        "type": "cta",
                        "button_text": "Track Your Order",
                        "button_url": "{tracking_url}",
                        "button_color": "#2563eb",
                    },
                    {
                        "type": "footer",
                        "text": "Questions? <a href='mailto:support@{domain}'>Contact us</a>",
                    },
                ],
            },
            
            # ──────────────────────────────────────────────────────
            # ABANDONED CART
            # ──────────────────────────────────────────────────────
            "abandoned_cart": {
                "name": "Abandoned Cart",
                "subject": "You left items in your cart",
                "preview": "Complete your purchase",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#ef4444",
                        "text_color": "#ffffff",
                        "title": "Complete Your Purchase",
                        "subtitle": "Items in your cart are waiting",
                    },
                    {
                        "type": "content",
                        "body": "You left {item_count} item(s) in your cart. Complete your order to receive free shipping!",
                    },
                    {
                        "type": "cart_items",
                        "items": [
                            {"name": "{item_1}", "price": "{price_1}", "image": "{image_1}"},
                            {"name": "{item_2}", "price": "{price_2}", "image": "{image_2}"},
                        ],
                        "total": "{cart_total}",
                    },
                    {
                        "type": "cta",
                        "button_text": "Complete Purchase",
                        "button_url": "{cart_url}",
                        "button_color": "#ef4444",
                    },
                    {
                        "type": "footer",
                        "text": "Offer expires in 24 hours",
                    },
                ],
            },
            
            # ──────────────────────────────────────────────────────
            # PASSWORD RESET
            # ──────────────────────────────────────────────────────
            "password_reset": {
                "name": "Password Reset",
                "subject": "Reset your password",
                "preview": "Secure your account",
                "sections": [
                    {
                        "type": "header",
                        "background_color": "#6366f1",
                        "text_color": "#ffffff",
                        "title": "Password Reset",
                        "subtitle": "Secure your account",
                    },
                    {
                        "type": "content",
                        "body": """
                            <p>We received a request to reset your password. Click the button below to create a new password.</p>
                            <p><strong>This link expires in 24 hours.</strong></p>
                        """,
                    },
                    {
                        "type": "cta",
                        "button_text": "Reset Password",
                        "button_url": "{reset_url}",
                        "button_color": "#6366f1",
                    },
                    {
                        "type": "content",
                        "body": "<p>If you didn't request this, you can ignore this email.</p>",
                    },
                    {
                        "type": "footer",
                        "text": "Never share this link with anyone",
                    },
                ],
            },
        }
    
    def generate_email(self, template_type: str, variables: Dict) -> Optional[Dict]:
        """Generate email from template"""
        if template_type not in self.templates:
            return None
        
        template = self.templates[template_type]
        
        # Replace variables in template
        email = {
            "subject": self._replace_variables(template["subject"], variables),
            "preview": self._replace_variables(template["preview"], variables),
            "html": self._generate_html(template["sections"], variables),
            "plain_text": self._generate_plain_text(template["sections"], variables),
        }
        
        return email
    
    def _replace_variables(self, text: str, variables: Dict) -> str:
        """Replace {variable} with values"""
        for key, value in variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def _generate_html(self, sections: List[Dict], variables: Dict) -> str:
        """Generate HTML email from sections"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { padding: 40px 20px; text-align: center; }
        .content { padding: 40px 20px; }
        .cta-button { display: inline-block; padding: 12px 30px; text-decoration: none; border-radius: 4px; color: white; font-weight: bold; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="container">
"""
        
        for section in sections:
            if section["type"] == "header":
                html += self._render_header(section, variables)
            elif section["type"] == "content":
                html += self._render_content(section, variables)
            elif section["type"] == "highlight":
                html += self._render_highlight(section, variables)
            elif section["type"] == "cta":
                html += self._render_cta(section, variables)
            elif section["type"] == "footer":
                html += self._render_footer(section, variables)
            elif section["type"] == "order_details":
                html += self._render_order_details(section, variables)
            elif section["type"] == "shipping_info":
                html += self._render_shipping_info(section, variables)
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _generate_plain_text(self, sections: List[Dict], variables: Dict) -> str:
        """Generate plain text version"""
        text = ""
        for section in sections:
            if section["type"] == "header":
                text += f"\n{section['title']}\n{section['subtitle']}\n\n"
            elif section["type"] == "content":
                text += f"{self._replace_variables(section.get('body', ''), variables)}\n\n"
            elif section["type"] == "cta":
                text += f"{section['button_text']}: {section['button_url']}\n\n"
            elif section["type"] == "footer":
                text += f"\n{self._replace_variables(section['text'], variables)}\n"
        return text
    
    def _render_header(self, section: Dict, variables: Dict) -> str:
        """Render header section"""
        bg = section.get("background_color", "#2563eb")
        text_color = section.get("text_color", "#ffffff")
        title = self._replace_variables(section["title"], variables)
        subtitle = self._replace_variables(section["subtitle"], variables)
        
        return f"""
        <div class="header" style="background-color: {bg}; color: {text_color};">
            <h1 style="margin: 0 0 10px 0;">{title}</h1>
            <p style="margin: 0;">{subtitle}</p>
        </div>
        """
    
    def _render_content(self, section: Dict, variables: Dict) -> str:
        """Render content section"""
        body = self._replace_variables(section.get("body", ""), variables)
        return f'<div class="content">{body}</div>'
    
    def _render_highlight(self, section: Dict, variables: Dict) -> str:
        """Render highlight section"""
        title = self._replace_variables(section.get("title", ""), variables)
        description = self._replace_variables(section.get("description", ""), variables)
        color = section.get("highlight_color", "#f59e0b")
        
        return f"""
        <div class="content" style="border-left: 4px solid {color}; padding-left: 20px;">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """
    
    def _render_cta(self, section: Dict, variables: Dict) -> str:
        """Render CTA button"""
        text = section["button_text"]
        url = self._replace_variables(section["button_url"], variables)
        color = section.get("button_color", "#2563eb")
        
        return f"""
        <div class="content" style="text-align: center;">
            <a href="{url}" class="cta-button" style="background-color: {color};">{text}</a>
        </div>
        """
    
    def _render_footer(self, section: Dict, variables: Dict) -> str:
        """Render footer"""
        text = self._replace_variables(section["text"], variables)
        return f'<div class="footer">{text}</div>'
    
    def _render_order_details(self, section: Dict, variables: Dict) -> str:
        """Render order details"""
        order_id = self._replace_variables(section["order_id"], variables)
        order_date = self._replace_variables(section["order_date"], variables)
        total = self._replace_variables(section["total"], variables)
        
        items_html = ""
        for item in section.get("items", []):
            name = self._replace_variables(item["name"], variables)
            qty = self._replace_variables(item["quantity"], variables)
            price = self._replace_variables(item["price"], variables)
            items_html += f"<tr><td>{name}</td><td>{qty}</td><td>{price}</td></tr>"
        
        return f"""
        <div class="content">
            <h3>Order Details</h3>
            <p>Order ID: {order_id}</p>
            <p>Date: {order_date}</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <th style="text-align: left; padding: 10px 0;">Item</th>
                    <th style="text-align: center;">Qty</th>
                    <th style="text-align: right;">Price</th>
                </tr>
                {items_html}
                <tr style="font-weight: bold; border-top: 2px solid #eee;">
                    <td colspan="2" style="padding: 10px 0;">Total:</td>
                    <td style="text-align: right;">{total}</td>
                </tr>
            </table>
        </div>
        """
    
    def _render_shipping_info(self, section: Dict, variables: Dict) -> str:
        """Render shipping info"""
        title = section["title"]
        address = self._replace_variables(section["address"], variables)
        delivery = self._replace_variables(section["estimated_delivery"], variables)
        
        return f"""
        <div class="content">
            <h3>{title}</h3>
            <p>{address}</p>
            <p><strong>Estimated Delivery:</strong> {delivery}</p>
        </div>
        """
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {"id": key, "name": template["name"]}
            for key, template in self.templates.items()
        ]
    
    def export_template(self, template_type: str, format: str = "html") -> Optional[str]:
        """Export template"""
        if template_type not in self.templates:
            return None
        
        if format == "json":
            return json.dumps(self.templates[template_type], indent=2)
        
        return None


def create_generator() -> EmailTemplateGenerator:
    """Factory function"""
    return EmailTemplateGenerator()


# Singleton
generator = EmailTemplateGenerator()


def generate_email(template_type: str, variables: Dict) -> Optional[Dict]:
    """Public API: Generate email"""
    return generator.generate_email(template_type, variables)


def list_email_templates() -> List[Dict]:
    """Public API: List templates"""
    return generator.list_templates()
