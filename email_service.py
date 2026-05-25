"""Email Service Module - Phase 4"""

import uuid
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import os

from email_sender import EmailMessage, EmailSender, EmailProvider, EmailQueue


class EmailTemplateType(Enum):
    """Email template types"""
    WELCOME = "welcome"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    ORDER_CONFIRMATION = "order_confirmation"
    ABANDONED_CART = "abandoned_cart"
    PASSWORD_RESET = "password_reset"
    INVOICE = "invoice"
    SHIPMENT = "shipment"


class EmailService:
    """High-level email service"""

    def __init__(self, provider: str = "smtp", **config):
        """
        Initialize email service
        
        Args:
            provider: "smtp", "gmail", or "sendgrid"
            **config: Provider-specific configuration
        """
        if provider == "gmail":
            provider_enum = EmailProvider.GMAIL
        elif provider == "sendgrid":
            provider_enum = EmailProvider.SENDGRID
        else:
            provider_enum = EmailProvider.SMTP

        self.sender = EmailSender(provider_enum, **config)
        self.queue = self.sender.queue

    @staticmethod
    def from_env() -> "EmailService":
        """Create email service from environment variables"""
        provider = os.getenv("EMAIL_PROVIDER", "smtp").lower()

        if provider == "gmail":
            return EmailService(
                provider="gmail",
                gmail_address=os.getenv("GMAIL_ADDRESS"),
                app_password=os.getenv("GMAIL_APP_PASSWORD")
            )
        elif provider == "sendgrid":
            return EmailService(
                provider="sendgrid",
                api_key=os.getenv("SENDGRID_API_KEY")
            )
        else:
            return EmailService(
                provider="smtp",
                smtp_server=os.getenv("SMTP_SERVER", "localhost"),
                smtp_port=int(os.getenv("SMTP_PORT", "587")),
                username=os.getenv("SMTP_USERNAME", ""),
                password=os.getenv("SMTP_PASSWORD", ""),
                use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            )

    def send(self, to: str, subject: str, html_content: str, plain_text: str,
             from_email: Optional[str] = None, from_name: Optional[str] = "Promptrix",
             reply_to: Optional[str] = None, cc: Optional[List[str]] = None,
             bcc: Optional[List[str]] = None, headers: Optional[Dict[str, str]] = None,
             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an email

        Args:
            to: Recipient email
            subject: Email subject
            html_content: HTML email body
            plain_text: Plain text email body
            from_email: Sender email (optional, uses default)
            from_name: Sender name
            reply_to: Reply-to address
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            headers: Custom headers
            metadata: Custom metadata

        Returns:
            Response with message ID and status
        """
        # Generate message ID
        message_id = f"msg_{uuid.uuid4().hex[:16]}"

        # Create email message
        email = EmailMessage(
            id=message_id,
            to=to,
            subject=subject,
            html_content=html_content,
            plain_text=plain_text,
            from_email=from_email or "noreply@promptrix.com",
            from_name=from_name,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            headers=headers,
            metadata=metadata,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

        # Send
        result = self.sender.send(email)

        return {
            "success": result.success,
            "message_id": result.message_id,
            "status": result.status,
            "error": result.error,
            "timestamp": result.timestamp
        }

    def send_batch(self, recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send batch emails

        Args:
            recipients: List of recipient objects with:
                - to: email address
                - subject: email subject
                - html_content: HTML body
                - plain_text: Plain text body
                - variables: Template variables (optional)

        Returns:
            Summary of batch send
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "message_ids": []
        }

        for recipient in recipients:
            result = self.send(
                to=recipient["to"],
                subject=recipient.get("subject", ""),
                html_content=recipient.get("html_content", ""),
                plain_text=recipient.get("plain_text", ""),
                from_email=recipient.get("from_email"),
                from_name=recipient.get("from_name", "Promptrix"),
                metadata=recipient.get("metadata")
            )

            if result["success"]:
                results["sent"] += 1
            else:
                results["failed"] += 1

            results["message_ids"].append(result["message_id"])

        return results

    def send_from_template(self, to: str, template_type: str, variables: Dict[str, Any],
                           from_email: Optional[str] = None, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email using template

        Args:
            to: Recipient email
            template_type: Type of template (welcome, newsletter, etc.)
            variables: Variables to substitute in template
            from_email: Sender email
            reply_to: Reply-to address

        Returns:
            Send result
        """
        # Get template
        template = self._get_template(template_type)
        if not template:
            return {"success": False, "error": f"Template not found: {template_type}"}

        # Render template
        html = self._render_template(template["html"], variables)
        plain_text = self._render_template(template["plain_text"], variables)
        subject = self._render_template(template["subject"], variables)

        # Send
        return self.send(
            to=to,
            subject=subject,
            html_content=html,
            plain_text=plain_text,
            from_email=from_email,
            reply_to=reply_to,
            metadata={"template": template_type}
        )

    def _get_template(self, template_type: str) -> Optional[Dict[str, str]]:
        """Get email template"""
        templates = {
            "welcome": {
                "subject": "Welcome to {brand}! 🎉",
                "html": self._template_welcome_html(),
                "plain_text": self._template_welcome_text()
            },
            "newsletter": {
                "subject": "Your {brand} Newsletter",
                "html": self._template_newsletter_html(),
                "plain_text": self._template_newsletter_text()
            },
            "promotional": {
                "subject": "{offer_title}",
                "html": self._template_promotional_html(),
                "plain_text": self._template_promotional_text()
            },
            "order_confirmation": {
                "subject": "Order #{order_id} Confirmed",
                "html": self._template_order_html(),
                "plain_text": self._template_order_text()
            },
            "abandoned_cart": {
                "subject": "Don't forget your items!",
                "html": self._template_cart_html(),
                "plain_text": self._template_cart_text()
            },
            "password_reset": {
                "subject": "Reset your {brand} password",
                "html": self._template_password_html(),
                "plain_text": self._template_password_text()
            }
        }
        return templates.get(template_type)

    @staticmethod
    def _render_template(template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    @staticmethod
    def _template_welcome_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1>Welcome to {brand}!</h1>
                    <p>Hi {first_name},</p>
                    <p>{value_proposition}</p>
                    <p><a href="{app_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Get Started</a></p>
                    <hr/>
                    <p style="font-size: 12px; color: #999;">
                        © {brand} | <a href="{domain}">Visit Website</a>
                    </p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_welcome_text() -> str:
        return "Welcome to {brand}!\n\nHi {first_name},\n\n{value_proposition}\n\nVisit: {app_url}"

    @staticmethod
    def _template_newsletter_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1>{brand} Newsletter</h1>
                    <h2 style="color: #007bff;">{top_article}</h2>
                    <p>{article_1}</p>
                    <p>{article_2}</p>
                    <p>{article_3}</p>
                    <p><a href="{blog_url}" style="color: #007bff;">Read More</a></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_newsletter_text() -> str:
        return "{brand} Newsletter\n\n{top_article}\n\n{article_1}\n{article_2}\n{article_3}\n\nRead more: {blog_url}"

    @staticmethod
    def _template_promotional_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #ff6b6b;">{offer_title}</h1>
                    <p>Get {discount}% off on selected items!</p>
                    <p><a href="{shop_url}" style="background-color: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 16px;">Shop Now</a></p>
                    <p style="font-size: 12px; color: #999;">Offer expires: {expiry_date}</p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_promotional_text() -> str:
        return "{offer_title}\n\nGet {discount}% off! Shop now: {shop_url}\n\nExpires: {expiry_date}"

    @staticmethod
    def _template_order_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1>Order Confirmed</h1>
                    <p>Thank you for your order #{order_id}!</p>
                    <p><strong>Total: {total}</strong></p>
                    <p><strong>Shipping to:</strong><br/>{shipping_address}</p>
                    <p>Expected delivery: {delivery_date}</p>
                    <p><a href="{tracking_url}" style="color: #007bff;">Track Order</a></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_order_text() -> str:
        return "Order Confirmed: #{order_id}\n\nTotal: {total}\n\nShipping to: {shipping_address}\n\nDelivery: {delivery_date}\n\nTrack: {tracking_url}"

    @staticmethod
    def _template_cart_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1>Don't Forget Your Items!</h1>
                    <p>You left {item_count} items in your cart worth {cart_total}.</p>
                    <p><a href="{cart_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Complete Purchase</a></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_cart_text() -> str:
        return "Don't Forget Your Items!\n\nYou left {item_count} items in your cart worth {cart_total}.\n\nComplete purchase: {cart_url}"

    @staticmethod
    def _template_password_html() -> str:
        return """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1>Password Reset</h1>
                    <p>Hi,</p>
                    <p>Click the link below to reset your password:</p>
                    <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
                    <p style="color: #ff6b6b;"><strong>Warning:</strong> Do not share this link with anyone!</p>
                    <p style="font-size: 12px; color: #999;">This link expires in 24 hours.</p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _template_password_text() -> str:
        return "Password Reset\n\nReset your password: {reset_url}\n\nWarning: Do not share this link!\n\nLink expires in 24 hours."

    def get_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get email status"""
        return self.queue.get_status(message_id)

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get email logs"""
        return self.queue.get_logs(limit)

    def process_queue(self, batch_size: int = 10) -> Dict[str, int]:
        """Process pending emails"""
        return self.sender.process_queue(batch_size)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService.from_env()
    return _email_service


def set_email_service(service: EmailService):
    """Set email service singleton"""
    global _email_service
    _email_service = service
