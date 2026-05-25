"""
Database Models - SQLAlchemy ORM for PostgreSQL
Phase 2: CMS Backend
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///promptrix.db")

# Use SQLite for dev, PostgreSQL for prod
if "postgresql" not in DATABASE_URL:
    # SQLite for development
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL for production
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ──────────────────────────────────────────────────────────────────────────────
# USER MODEL
# ──────────────────────────────────────────────────────────────────────────────

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    session_token = Column(String(255), unique=True, index=True)
    
    # Profile
    company = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Settings
    language = Column(String(5), default="en")
    theme = Column(String(10), default="light")  # light, dark
    notifications_enabled = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sites = relationship("Site", back_populates="user", cascade="all, delete-orphan")
    content_items = relationship("ContentItem", back_populates="user", cascade="all, delete-orphan")
    email_campaigns = relationship("EmailCampaign", back_populates="user", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────────────────────────
# SITE MODEL
# ──────────────────────────────────────────────────────────────────────────────

class Site(Base):
    """Generated website model"""
    __tablename__ = "sites"
    
    id = Column(String(32), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Site info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    brand = Column(String(255), nullable=False)
    tagline = Column(String(500), nullable=True)
    site_type = Column(String(50), nullable=False, index=True)  # ecommerce, blog, portfolio, etc.
    
    # Content
    pages = Column(JSON, nullable=True)  # List of page configs
    sections = Column(JSON, nullable=True)  # List of sections
    custom_content = Column(JSON, nullable=True)  # User-provided content
    
    # Design
    colors = Column(JSON, nullable=True)  # Primary, secondary, accent
    fonts = Column(JSON, nullable=True)  # Typography config
    dark_mode = Column(JSON, nullable=True)  # Dark mode colors
    
    # SEO
    seo_metadata = Column(JSON, nullable=True)  # Meta tags, og:, schema
    sitemap = Column(Text, nullable=True)
    robots_txt = Column(Text, nullable=True)
    seo_score = Column(Integer, default=0)  # 0-100
    
    # Accessibility
    accessibility_score = Column(Integer, default=0)  # 0-100
    wcag_level = Column(String(5), default="AA")  # AA, AAA
    
    # Settings
    is_published = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=True)
    language = Column(String(5), default="en")
    
    # URLs
    domain = Column(String(255), nullable=True, index=True)
    preview_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sites")
    content_items = relationship("ContentItem", back_populates="site", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────────────────────────
# CONTENT ITEM MODEL
# ──────────────────────────────────────────────────────────────────────────────

class ContentItem(Base):
    """Manageable content for a site"""
    __tablename__ = "content_items"
    
    id = Column(String(32), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False, index=True)
    
    # Content type
    category = Column(String(50), nullable=False, index=True)  # hero, features, cta, etc.
    item_type = Column(String(50), nullable=False)  # title, subtitle, description, etc.
    
    # Content
    content = Column(Text, nullable=False)
    item_metadata = Column(JSON, nullable=True)  # position, styling, etc.
    
    # Translation
    language = Column(String(5), default="en")
    translations = Column(JSON, nullable=True)  # {lang: content}
    
    # State
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # A/B Testing
    variant_group = Column(String(50), nullable=True)  # Group ID for A/B tests
    variant_name = Column(String(100), nullable=True)  # e.g., "control", "variant_a"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_items")
    site = relationship("Site", back_populates="content_items")


# ──────────────────────────────────────────────────────────────────────────────
# EMAIL TEMPLATE MODEL
# ──────────────────────────────────────────────────────────────────────────────

class EmailTemplate(Base):
    """Email templates for marketing"""
    __tablename__ = "email_templates"
    
    id = Column(String(32), primary_key=True, index=True)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False, index=True)
    
    # Template info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # welcome, newsletter, promotional, etc.
    
    # Content
    subject = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    plain_text = Column(Text, nullable=True)
    
    # Design
    preheader = Column(String(255), nullable=True)
    preview_image = Column(String(500), nullable=True)
    colors = Column(JSON, nullable=True)
    
    # Settings
    is_draft = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ──────────────────────────────────────────────────────────────────────────────
# EMAIL CAMPAIGN MODEL
# ──────────────────────────────────────────────────────────────────────────────

class EmailCampaign(Base):
    """Email marketing campaigns"""
    __tablename__ = "email_campaigns"
    
    id = Column(String(32), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Campaign info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(50), nullable=False)  # newsletter, promotional, transactional
    
    # Template
    template_id = Column(String(32), nullable=True)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    
    # Recipients
    recipient_count = Column(Integer, default=0)
    segment = Column(JSON, nullable=True)  # Targeting rules
    
    # Performance
    status = Column(String(20), default="draft")  # draft, scheduled, sent, paused
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="email_campaigns")


# ──────────────────────────────────────────────────────────────────────────────
# AB TEST MODEL
# ──────────────────────────────────────────────────────────────────────────────

class ABTest(Base):
    """A/B testing data"""
    __tablename__ = "ab_tests"
    
    id = Column(String(32), primary_key=True, index=True)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False, index=True)
    
    # Test info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(String(50), nullable=False)  # headline, cta, image, etc.
    
    # Variants
    control_id = Column(String(32), nullable=False)  # Content item ID for control
    variant_ids = Column(JSON, nullable=False)  # List of variant content item IDs
    
    # Status
    status = Column(String(20), default="draft")  # draft, running, completed, paused
    
    # Results
    results = Column(JSON, nullable=True)  # {variant_id: {conversions, views, rate}}
    winner_id = Column(String(32), nullable=True)
    
    # Config
    sample_size = Column(Integer, default=1000)
    confidence_level = Column(Integer, default=95)  # 90, 95, 99
    
    # Dates
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ──────────────────────────────────────────────────────────────────────────────
# ANALYTICS MODEL
# ──────────────────────────────────────────────────────────────────────────────

class SiteAnalytics(Base):
    """Site analytics and metrics"""
    __tablename__ = "site_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(32), ForeignKey("sites.id"), nullable=False, index=True)
    
    # Traffic
    date = Column(DateTime, default=datetime.utcnow)
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    bounce_rate = Column(Integer, default=0)  # 0-100%
    avg_session_duration = Column(Integer, default=0)  # seconds
    
    # Conversions
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Integer, default=0)  # 0-100%
    goals_completed = Column(Integer, default=0)
    
    # Traffic sources
    organic = Column(Integer, default=0)
    direct = Column(Integer, default=0)
    referral = Column(Integer, default=0)
    social = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db_session():
    """Get database session"""
    return SessionLocal()


def drop_all_tables():
    """Drop all tables (USE CAREFULLY!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")
