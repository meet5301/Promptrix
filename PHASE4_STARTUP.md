# Promptrix Phase 4 Startup Guide

**Complete Setup, Configuration, and API Documentation**

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Email System](#email-system)
5. [Webhook System](#webhook-system)
6. [Advanced Analytics](#advanced-analytics)
7. [Admin Dashboard](#admin-dashboard)
8. [API Endpoints](#api-endpoints)
9. [Integration Examples](#integration-examples)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Overview

Promptrix Phase 4 extends Phases 1-3 with enterprise features:

- **Email System**: Multi-provider email delivery with queue persistence and retry logic
- **Webhook System**: Event-driven webhooks with HMAC signatures and exponential backoff
- **Advanced Analytics**: Real-time visitor tracking, funnel analysis, cohort analysis
- **Admin Dashboard**: Modern web UI for managing all features

### Architecture

```
┌─────────────────────────────────────────┐
│         Flask REST API (Phase 4)        │
├─────────────────────────────────────────┤
│  Email  │ Webhooks │ Analytics │ CMS   │
├─────────────────────────────────────────┤
│  Email  │ Webhook  │ Analytics │ SQLite│
│ Service │ Manager  │  Manager  │  DB   │
└─────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip or conda
- Git

### Step 1: Clone/Navigate to Project

```bash
cd c:\Users\Meet\OneDrive\Desktop\Promptrix
```

### Step 2: Install Dependencies

```bash
pip install flask flask-cors sqlalchemy requests
```

### Step 3: Create Virtual Environment (Recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Step 4: Initialize Databases

```bash
python -c "from app_v2_phase4 import app; app.app_context().push(); from db_models import init_db; init_db(app)"
```

### Step 5: Start the Server

```bash
python app_v2_phase4.py
```

Server runs on `http://localhost:5000`

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# API Configuration
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
DEBUG=False
PORT=5000
HOST=0.0.0.0

# Database
DATABASE_URL=sqlite:///promptrix.db

# Email Configuration
EMAIL_PROVIDER=smtp
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Gmail Configuration (if using GMAIL provider)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# SendGrid Configuration (if using SENDGRID provider)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxx

# Analytics & Webhooks Databases
WEBHOOKS_DB=webhooks.db
ANALYTICS_DB=analytics.db
```

### Email Provider Configuration

#### SMTP (Default)

```env
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Gmail app password
```

#### Gmail

```env
EMAIL_PROVIDER=gmail
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### SendGrid

```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxx
```

---

## Email System

### Overview

The email system provides:
- Multi-provider support (SMTP, Gmail, SendGrid)
- Queue-based delivery with SQLite persistence
- Exponential backoff retry logic (5 retries max)
- Template support (6 built-in templates)
- Batch sending

### Architecture

```
EmailService (high-level API)
    ↓
EmailSender (provider abstraction)
    ↓
EmailQueue (SQLite persistence)
    ↓
EmailProvider (SMTP/Gmail/SendGrid)
```

### Usage Examples

#### Send Single Email

```python
from email_service import get_email_service

service = get_email_service()

result = service.send(
    to="user@example.com",
    subject="Test Email",
    html_content="<p>Hello from Promptrix</p>",
    plain_text="Hello from Promptrix"
)

print(result)
# Output: {'email_id': 'msg_xxxx', 'status': 'pending'}
```

#### Send from Template

```python
result = service.send_from_template(
    to="user@example.com",
    template_type="welcome",
    variables={
        "brand": "MyBrand",
        "first_name": "John",
        "app_url": "https://myapp.com"
    }
)
```

#### Batch Send

```python
results = service.send_batch(
    recipients=["user1@example.com", "user2@example.com", "user3@example.com"],
    subject="Newsletter",
    html_content="<h1>Our Latest News</h1>...",
    plain_text="Our Latest News..."
)

print(results)
# Output: [
#   {'to': 'user1@...', 'email_id': 'msg_xxx', 'success': True},
#   {'to': 'user2@...', 'email_id': 'msg_yyy', 'success': True},
#   ...
# ]
```

#### Process Queue

```python
stats = service.process_queue(batch_size=10)

print(stats)
# Output: {'sent': 8, 'failed': 1, 'retried': 1}
```

### Email Templates

#### 1. Welcome Template

```
Template Type: welcome
Subject: Welcome to {brand}!
Variables: brand, first_name, app_url, domain
```

#### 2. Newsletter

```
Template Type: newsletter
Subject: Your {brand} Newsletter
Variables: brand, content, blog_url, unsubscribe_url
```

#### 3. Promotional

```
Template Type: promotional
Subject: {offer_title}
Variables: offer_title, discount, shop_url, expiry_date
```

#### 4. Order Confirmation

```
Template Type: order_confirmation
Subject: Order #{order_id}
Variables: order_id, total, shipping_address, tracking_url
```

#### 5. Abandoned Cart

```
Template Type: abandoned_cart
Subject: Don't forget your items!
Variables: item_count, cart_total, cart_url, discount_code
```

#### 6. Password Reset

```
Template Type: password_reset
Subject: Reset your {brand} password
Variables: brand, reset_url, expiry_minutes
```

### Retry Logic

- **Attempt 1**: Immediate
- **Attempt 2**: 5 seconds
- **Attempt 3**: 30 seconds
- **Attempt 4**: 5 minutes
- **Attempt 5**: 30 minutes
- **Attempt 6**: 2 hours (final)

---

## Webhook System

### Overview

The webhook system provides:
- Event-driven webhook subscriptions
- HMAC-SHA256 signature verification
- Exponential backoff retry logic
- Delivery persistence and logging
- 12 event types

### Event Types

```python
SITE_CREATED = "site.created"
SITE_UPDATED = "site.updated"
SITE_DELETED = "site.deleted"
SITE_PUBLISHED = "site.published"
CONTENT_CREATED = "content.created"
CONTENT_UPDATED = "content.updated"
CONTENT_DELETED = "content.deleted"
EMAIL_SENT = "email.sent"
EMAIL_FAILED = "email.failed"
CAMPAIGN_STARTED = "campaign.started"
CAMPAIGN_COMPLETED = "campaign.completed"
ANALYTICS_MILESTONE = "analytics.milestone"
```

### Usage Examples

#### Create Webhook

```python
from webhooks import get_webhook_manager

manager = get_webhook_manager()

webhook = manager.create_webhook(
    user_id="user_123",
    url="https://example.com/webhook",
    events=["site.created", "email.sent", "analytics.milestone"]
)

print(webhook)
# Output: {
#   "id": "wh_xxxx",
#   "user_id": "user_123",
#   "url": "https://example.com/webhook",
#   "events": ["site.created", "email.sent", "analytics.milestone"],
#   "secret": "secret_key",  # Save this securely!
#   "active": true,
#   "created_at": "2024-01-20T..."
# }
```

#### Dispatch Event

```python
result = manager.dispatch_event(
    "site.created",
    {
        "site_id": "site_123",
        "site_name": "My Blog",
        "created_by": "user_123"
    }
)

print(result)
# Output: {
#   "event_id": "evt_xxxx",
#   "event_type": "site.created",
#   "deliveries_queued": 2
# }
```

#### Process Deliveries

```python
stats = manager.process_deliveries(batch_size=10)

print(stats)
# Output: {'sent': 8, 'failed': 1, 'retried': 1}
```

#### Get Delivery Logs

```python
logs = manager.get_delivery_logs("wh_xxxx", limit=50)

for log in logs:
    print(f"{log['status']} - {log['created_at']}")
```

### Webhook Signature Verification

Your webhook receiver should verify the signature:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

# In your webhook handler
signature = request.headers.get('X-Webhook-Signature')
payload = request.get_data(as_text=True)
secret = os.getenv('WEBHOOK_SECRET')

if verify_webhook(payload, signature, secret):
    # Process webhook
    data = json.loads(payload)
    ...
```

---

## Advanced Analytics

### Overview

The analytics system provides:
- Real-time event tracking
- Visitor profiling
- Session tracking
- Conversion tracking
- Funnel analysis
- Cohort analysis

### Event Tracking

#### Track Custom Event

```python
from advanced_analytics import get_analytics_manager, AnalyticsEvent

manager = get_analytics_manager()

event = AnalyticsEvent(
    event_type="page_view",
    site_id="site_123",
    visitor_id="visitor_456",
    session_id="session_789",
    properties={
        "page": "/products",
        "referrer": "/home",
        "device": "mobile"
    }
)

manager.track_event(event)
```

#### Track Conversion

```python
manager.track_conversion(
    site_id="site_123",
    visitor_id="visitor_456",
    conversion_type="purchase",
    value=99.99,
    properties={
        "product_id": "prod_123",
        "currency": "USD"
    }
)
```

### Analytics Reports

#### Get Summary

```python
summary = manager.get_summary("site_123", days=30)

print(summary)
# Output: {
#   "metrics": {
#     "page_views": 42500,
#     "unique_visitors": 8234,
#     "sessions": 12543,
#     "bounce_rate": 28.5,
#     "conversions": 324,
#     "conversion_rate": 3.94,
#     "conversion_value": 32345.76
#   }
# }
```

#### Conversion Funnel

```python
funnel = manager.get_funnel(
    "site_123",
    event_sequence=["page_view", "add_to_cart", "checkout", "purchase"],
    days=30
)

print(funnel)
# Output: {
#   "funnel": [
#     {"step": 1, "event": "page_view", "count": 42500, "drop_off": 0},
#     {"step": 2, "event": "add_to_cart", "count": 8432, "drop_off": 34068},
#     {"step": 3, "event": "checkout", "count": 2159, "drop_off": 6273},
#     {"step": 4, "event": "purchase", "count": 1289, "drop_off": 870}
#   ],
#   "conversion_rate": 3.03
# }
```

#### Cohort Analysis

```python
cohorts = manager.get_cohort_analysis("site_123")

print(cohorts)
# Output: {
#   "cohorts": [
#     {
#       "cohort_date": "2024-01-20",
#       "cohort_size": 342,
#       "retention": [100, 45.3, 28.9, 15.2, 8.5]
#     },
#     ...
#   ]
# }
```

#### Events Report

```python
report = manager.get_events_report("site_123", days=7, limit=100)

print(report)
# Output: {
#   "event_types": [
#     {"type": "page_view", "count": 12543},
#     {"type": "click", "count": 4234},
#     {"type": "form_submit", "count": 234}
#   ],
#   "recent_events": [...]
# }
```

---

## Admin Dashboard

### Access Dashboard

Navigate to: `http://localhost:5000/dashboard`

### Dashboard Features

- **Overview Metrics**: Sites, visitors, emails, conversions
- **Sites Management**: Create, edit, delete sites
- **Content Editor**: Manage content items
- **Email Campaigns**: Send and track email campaigns
- **Webhooks**: Configure webhooks and view delivery logs
- **Analytics**: View visitor analytics and conversion funnels
- **Settings**: Configure email provider and API keys

### Dashboard Statistics API

Get dashboard statistics:

```bash
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:5000/dashboard/api/stats
```

Response:

```json
{
  "analytics": {
    "page_views": 42500,
    "unique_visitors": 8234,
    "sessions": 12543,
    "bounce_rate": 28.5,
    "conversions": 324,
    "conversion_rate": 3.94,
    "conversion_value": 32345.76
  },
  "updated_at": "2024-01-20T..."
}
```

---

## API Endpoints

### Email Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/email/send` | Send single email |
| POST | `/api/email/send-batch` | Send batch emails |
| POST | `/api/email/send-template` | Send template email |
| GET | `/api/email/status/<id>` | Get email status |
| GET | `/api/email/logs` | Get delivery logs |
| POST | `/api/email/process-queue` | Process queue |

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/webhooks` | Create webhook |
| GET | `/api/webhooks/<id>` | Get webhook |
| GET | `/api/webhooks/user/<user_id>` | List user webhooks |
| PUT | `/api/webhooks/<id>` | Update webhook |
| DELETE | `/api/webhooks/<id>` | Delete webhook |
| GET | `/api/webhooks/logs/<id>` | Get delivery logs |
| POST | `/api/webhooks/process` | Process deliveries |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analytics/track` | Track event |
| POST | `/api/analytics/conversion` | Track conversion |
| GET | `/api/analytics/summary/<site_id>` | Get summary |
| GET | `/api/analytics/funnel/<site_id>` | Get funnel |
| GET | `/api/analytics/cohorts/<site_id>` | Get cohorts |
| GET | `/api/analytics/events/<site_id>` | Get events |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/info` | API information |
| GET | `/dashboard` | Admin dashboard |

---

## Integration Examples

### Example 1: Complete Email Workflow

```python
from email_service import get_email_service
from webhooks import get_webhook_manager

# Initialize
email_service = get_email_service()
webhook_manager = get_webhook_manager()

# Create webhook for email notifications
webhook = webhook_manager.create_webhook(
    user_id="user_123",
    url="https://myapp.com/notifications",
    events=["email.sent", "email.failed"]
)

# Send welcome email
result = email_service.send_from_template(
    to="newuser@example.com",
    template_type="welcome",
    variables={
        "brand": "MyApp",
        "first_name": "John",
        "app_url": "https://myapp.com"
    }
)

# Dispatch webhook event when email is sent
webhook_manager.dispatch_event("email.sent", {
    "to": "newuser@example.com",
    "template_type": "welcome"
})

# Process any pending emails
stats = email_service.process_queue()
print(f"Processed: {stats['sent']} sent, {stats['failed']} failed")
```

### Example 2: Analytics & Funnel Analysis

```python
from advanced_analytics import get_analytics_manager, AnalyticsEvent

manager = get_analytics_manager()

# Track user journey
journey = [
    ("page_view", "/"),
    ("page_view", "/products"),
    ("add_to_cart", "product_123"),
    ("view_cart", "cart_summary"),
    ("checkout", "payment_page"),
    ("purchase", "order_confirmed")
]

for event_type, page in journey:
    event = AnalyticsEvent(
        event_type=event_type,
        site_id="store_123",
        visitor_id="visitor_456",
        session_id="session_789",
        properties={"page": page}
    )
    manager.track_event(event)

# Analyze funnel
funnel = manager.get_funnel(
    "store_123",
    event_sequence=["page_view", "add_to_cart", "checkout", "purchase"],
    days=7
)

print(f"Overall conversion: {funnel['conversion_rate']}%")
for step in funnel['funnel']:
    print(f"  {step['event']}: {step['count']} visitors")
```

### Example 3: Webhook-Triggered Analytics

```python
from webhooks import get_webhook_manager
from advanced_analytics import get_analytics_manager

webhook_manager = get_webhook_manager()
analytics_manager = get_analytics_manager()

# Create webhook to monitor conversions
webhook = webhook_manager.create_webhook(
    user_id="analytics_team",
    url="https://analytics.myapp.com/webhook",
    events=["email.sent", "analytics.milestone"]
)

# When purchase conversion milestone is reached
conversions = analytics_manager.track_conversion(
    site_id="store_123",
    visitor_id="visitor_456",
    conversion_type="purchase",
    value=299.99
)

# Dispatch milestone event if threshold reached
summary = analytics_manager.get_summary("store_123", days=1)
if summary["metrics"]["conversions"] >= 100:
    webhook_manager.dispatch_event("analytics.milestone", {
        "milestone": "100 conversions",
        "daily_conversions": 100,
        "daily_revenue": 29999.00
    })
```

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use strong `SECRET_KEY` and `API_KEY`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Use production email provider (SendGrid/Gmail)
- [ ] Enable HTTPS for webhooks
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Test email delivery thoroughly
- [ ] Test webhook signatures
- [ ] Load test analytics
- [ ] Document webhook endpoints for clients

### Deploy to Heroku

```bash
# 1. Create Heroku app
heroku create promptrix

# 2. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set API_KEY=your-api-key
heroku config:set EMAIL_PROVIDER=sendgrid
heroku config:set SENDGRID_API_KEY=SG.xxx

# 3. Deploy
git push heroku main

# 4. Create database
heroku run python -c "from app_v2_phase4 import app; app.app_context().push(); from db_models import init_db; init_db(app)"
```

### Deploy to Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app_v2_phase4.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app_v2_phase4:app"]
```

---

## Troubleshooting

### Issue: "Email provider not configured"

**Solution**: Ensure `EMAIL_PROVIDER` environment variable is set and credentials are configured.

### Issue: "Webhook signature verification failed"

**Solution**: Verify the webhook secret matches and payload isn't being modified.

### Issue: "Analytics query timeout"

**Solution**: Limit query range with `days` parameter or add database indexes on frequently queried columns.

### Issue: "Email queue stuck"

**Solution**: Run `EmailService.process_queue()` or check database for stuck messages.

### Issue: "Webhooks not delivering"

**Solution**: Check webhook URL is accessible, check logs with `manager.get_delivery_logs()`.

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

---

## Next Steps

1. **Configure Email Provider**: Set up SMTP, Gmail, or SendGrid credentials
2. **Create First Webhook**: Test webhook delivery with a public endpoint
3. **Track First Events**: Implement analytics tracking in your frontend
4. **Access Dashboard**: Navigate to `/dashboard` and explore the UI
5. **Run Tests**: Execute `test_phase4_complete.py` to verify all systems
6. **Review API**: Check `/api/info` for complete endpoint list

---

## Support & Documentation

- **Full API**: See [API Endpoints](#api-endpoints) section
- **Examples**: See [Integration Examples](#integration-examples) section
- **Email Templates**: See [Email Templates](#email-templates) section
- **Event Types**: See [Event Types](#event-types) section

---

**Last Updated**: January 2024  
**Version**: 4.0.0  
**Status**: Production Ready
