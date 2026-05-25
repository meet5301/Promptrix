"""
CMS Backend - Content Management System operations
Phase 2: CRUD operations for sites, content, emails
NO external APIs - Pure Python data operations
"""

from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime
import json
from db_models import (
    get_db_session, User, Site, ContentItem, EmailTemplate, 
    EmailCampaign, ABTest, SiteAnalytics
)


class CMSBackend:
    """Content Management System operations"""
    
    def __init__(self):
        self.db = get_db_session()
    
    # ──────────────────────────────────────────────────────────────────────────────
    # SITE OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def create_site(self, user_id: int, config: Dict) -> Optional[Site]:
        """Create new site"""
        try:
            site = Site(
                id=uuid4().hex,
                user_id=user_id,
                name=config.get("brand", "Untitled"),
                brand=config.get("brand", ""),
                tagline=config.get("tagline", ""),
                site_type=config.get("site_type", "landing"),
                pages=config.get("pages", []),
                sections=config.get("sections", []),
                colors=config.get("colors", {}),
                custom_content=config.get("custom_content", {}),
                language=config.get("language", "en"),
            )
            self.db.add(site)
            self.db.commit()
            self.db.refresh(site)
            return site
        except Exception as e:
            self.db.rollback()
            print(f"Error creating site: {e}")
            return None
    
    def get_site(self, site_id: str) -> Optional[Site]:
        """Get site by ID"""
        return self.db.query(Site).filter(Site.id == site_id).first()
    
    def get_user_sites(self, user_id: int, limit: int = 50) -> List[Site]:
        """Get all sites for user"""
        return self.db.query(Site).filter(
            Site.user_id == user_id
        ).order_by(Site.created_at.desc()).limit(limit).all()
    
    def update_site(self, site_id: str, updates: Dict) -> Optional[Site]:
        """Update site"""
        try:
            site = self.get_site(site_id)
            if not site:
                return None
            
            for key, value in updates.items():
                if hasattr(site, key):
                    setattr(site, key, value)
            
            site.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(site)
            return site
        except Exception as e:
            self.db.rollback()
            print(f"Error updating site: {e}")
            return None
    
    def delete_site(self, site_id: str) -> bool:
        """Delete site"""
        try:
            site = self.get_site(site_id)
            if not site:
                return False
            
            self.db.delete(site)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting site: {e}")
            return False
    
    def publish_site(self, site_id: str) -> bool:
        """Publish site"""
        return self.update_site(site_id, {
            "is_published": True,
            "is_draft": False,
            "published_at": datetime.utcnow(),
        }) is not None
    
    def duplicate_site(self, site_id: str, user_id: int, new_name: str) -> Optional[Site]:
        """Duplicate site"""
        try:
            original = self.get_site(site_id)
            if not original:
                return None
            
            new_site = Site(
                id=uuid4().hex,
                user_id=user_id,
                name=new_name,
                brand=original.brand,
                tagline=original.tagline,
                site_type=original.site_type,
                pages=original.pages,
                sections=original.sections,
                colors=original.colors,
                fonts=original.fonts,
                custom_content=original.custom_content,
                language=original.language,
            )
            self.db.add(new_site)
            self.db.commit()
            self.db.refresh(new_site)
            return new_site
        except Exception as e:
            self.db.rollback()
            print(f"Error duplicating site: {e}")
            return None
    
    # ──────────────────────────────────────────────────────────────────────────────
    # CONTENT OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def create_content_item(self, user_id: int, site_id: str, content_data: Dict) -> Optional[ContentItem]:
        """Create content item"""
        try:
            item = ContentItem(
                id=uuid4().hex,
                user_id=user_id,
                site_id=site_id,
                category=content_data.get("category", ""),
                item_type=content_data.get("item_type", ""),
                content=content_data.get("content", ""),
                metadata=content_data.get("metadata", {}),
                language=content_data.get("language", "en"),
                translations=content_data.get("translations", {}),
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            print(f"Error creating content item: {e}")
            return None
    
    def get_content_item(self, item_id: str) -> Optional[ContentItem]:
        """Get content item by ID"""
        return self.db.query(ContentItem).filter(ContentItem.id == item_id).first()
    
    def get_site_content(self, site_id: str, category: Optional[str] = None) -> List[ContentItem]:
        """Get all content for site, optionally filtered by category"""
        query = self.db.query(ContentItem).filter(ContentItem.site_id == site_id)
        if category:
            query = query.filter(ContentItem.category == category)
        return query.order_by(ContentItem.created_at.desc()).all()
    
    def update_content_item(self, item_id: str, updates: Dict) -> Optional[ContentItem]:
        """Update content item"""
        try:
            item = self.get_content_item(item_id)
            if not item:
                return None
            
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            item.updated_at = datetime.utcnow()
            item.version += 1
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            print(f"Error updating content: {e}")
            return None
    
    def delete_content_item(self, item_id: str) -> bool:
        """Delete content item"""
        try:
            item = self.get_content_item(item_id)
            if not item:
                return False
            
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting content: {e}")
            return False
    
    def translate_content(self, item_id: str, language: str, translated_text: str) -> Optional[ContentItem]:
        """Add translation for content item"""
        try:
            item = self.get_content_item(item_id)
            if not item:
                return None
            
            if not item.translations:
                item.translations = {}
            
            item.translations[language] = translated_text
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            print(f"Error translating content: {e}")
            return None
    
    # ──────────────────────────────────────────────────────────────────────────────
    # EMAIL OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def create_email_template(self, site_id: str, template_data: Dict) -> Optional[EmailTemplate]:
        """Create email template"""
        try:
            template = EmailTemplate(
                id=uuid4().hex,
                site_id=site_id,
                name=template_data.get("name", ""),
                description=template_data.get("description", ""),
                template_type=template_data.get("template_type", "promotional"),
                subject=template_data.get("subject", ""),
                from_name=template_data.get("from_name", ""),
                from_email=template_data.get("from_email", ""),
                html_content=template_data.get("html_content", ""),
                plain_text=template_data.get("plain_text", ""),
                preheader=template_data.get("preheader", ""),
                colors=template_data.get("colors", {}),
            )
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            print(f"Error creating email template: {e}")
            return None
    
    def get_email_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get email template"""
        return self.db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    
    def get_site_email_templates(self, site_id: str) -> List[EmailTemplate]:
        """Get all email templates for site"""
        return self.db.query(EmailTemplate).filter(
            EmailTemplate.site_id == site_id
        ).order_by(EmailTemplate.created_at.desc()).all()
    
    def update_email_template(self, template_id: str, updates: Dict) -> Optional[EmailTemplate]:
        """Update email template"""
        try:
            template = self.get_email_template(template_id)
            if not template:
                return None
            
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            print(f"Error updating email template: {e}")
            return None
    
    def delete_email_template(self, template_id: str) -> bool:
        """Delete email template"""
        try:
            template = self.get_email_template(template_id)
            if not template:
                return False
            
            self.db.delete(template)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting email template: {e}")
            return False
    
    # ──────────────────────────────────────────────────────────────────────────────
    # EMAIL CAMPAIGN OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def create_email_campaign(self, user_id: int, campaign_data: Dict) -> Optional[EmailCampaign]:
        """Create email campaign"""
        try:
            campaign = EmailCampaign(
                id=uuid4().hex,
                user_id=user_id,
                name=campaign_data.get("name", ""),
                description=campaign_data.get("description", ""),
                campaign_type=campaign_data.get("campaign_type", "promotional"),
                subject=campaign_data.get("subject", ""),
                html_content=campaign_data.get("html_content", ""),
                recipient_count=campaign_data.get("recipient_count", 0),
                segment=campaign_data.get("segment", {}),
            )
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            return campaign
        except Exception as e:
            self.db.rollback()
            print(f"Error creating campaign: {e}")
            return None
    
    def get_email_campaign(self, campaign_id: str) -> Optional[EmailCampaign]:
        """Get email campaign"""
        return self.db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
    
    def get_user_campaigns(self, user_id: int, limit: int = 50) -> List[EmailCampaign]:
        """Get user's campaigns"""
        return self.db.query(EmailCampaign).filter(
            EmailCampaign.user_id == user_id
        ).order_by(EmailCampaign.created_at.desc()).limit(limit).all()
    
    def send_campaign(self, campaign_id: str) -> bool:
        """Mark campaign as sent"""
        try:
            campaign = self.get_email_campaign(campaign_id)
            if not campaign:
                return False
            
            campaign.status = "sent"
            campaign.sent_at = datetime.utcnow()
            campaign.sent_count = campaign.recipient_count
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error sending campaign: {e}")
            return False
    
    # ──────────────────────────────────────────────────────────────────────────────
    # A/B TEST OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def create_ab_test(self, site_id: str, test_data: Dict) -> Optional[ABTest]:
        """Create A/B test"""
        try:
            test = ABTest(
                id=uuid4().hex,
                site_id=site_id,
                name=test_data.get("name", ""),
                description=test_data.get("description", ""),
                test_type=test_data.get("test_type", "headline"),
                control_id=test_data.get("control_id", ""),
                variant_ids=test_data.get("variant_ids", []),
                sample_size=test_data.get("sample_size", 1000),
                confidence_level=test_data.get("confidence_level", 95),
            )
            self.db.add(test)
            self.db.commit()
            self.db.refresh(test)
            return test
        except Exception as e:
            self.db.rollback()
            print(f"Error creating A/B test: {e}")
            return None
    
    def get_ab_test(self, test_id: str) -> Optional[ABTest]:
        """Get A/B test"""
        return self.db.query(ABTest).filter(ABTest.id == test_id).first()
    
    def get_site_ab_tests(self, site_id: str) -> List[ABTest]:
        """Get all A/B tests for site"""
        return self.db.query(ABTest).filter(
            ABTest.site_id == site_id
        ).order_by(ABTest.created_at.desc()).all()
    
    def start_ab_test(self, test_id: str) -> bool:
        """Start A/B test"""
        try:
            test = self.get_ab_test(test_id)
            if not test:
                return False
            
            test.status = "running"
            test.started_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error starting test: {e}")
            return False
    
    def record_ab_result(self, test_id: str, variant_id: str, result_type: str) -> bool:
        """Record A/B test result (view, conversion, etc.)"""
        try:
            test = self.get_ab_test(test_id)
            if not test:
                return False
            
            if not test.results:
                test.results = {}
            
            if variant_id not in test.results:
                test.results[variant_id] = {"views": 0, "conversions": 0}
            
            if result_type == "view":
                test.results[variant_id]["views"] += 1
            elif result_type == "conversion":
                test.results[variant_id]["conversions"] += 1
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error recording result: {e}")
            return False
    
    # ──────────────────────────────────────────────────────────────────────────────
    # ANALYTICS OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────────
    
    def record_page_view(self, site_id: str) -> bool:
        """Record page view for analytics"""
        try:
            today = datetime.utcnow().date()
            analytics = self.db.query(SiteAnalytics).filter(
                SiteAnalytics.site_id == site_id,
                SiteAnalytics.date >= today,
            ).first()
            
            if not analytics:
                analytics = SiteAnalytics(
                    site_id=site_id,
                    date=datetime.utcnow(),
                )
                self.db.add(analytics)
            
            analytics.page_views += 1
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error recording page view: {e}")
            return False
    
    def get_site_analytics(self, site_id: str, days: int = 30) -> List[SiteAnalytics]:
        """Get site analytics"""
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - __import__('datetime').timedelta(days=days)
        
        return self.db.query(SiteAnalytics).filter(
            SiteAnalytics.site_id == site_id,
            SiteAnalytics.date >= cutoff_date,
        ).order_by(SiteAnalytics.date.desc()).all()
    
    def close(self):
        """Close database session"""
        self.db.close()


# Singleton instance
cms = None


def get_cms() -> CMSBackend:
    """Get CMS instance"""
    global cms
    if cms is None:
        cms = CMSBackend()
    return cms
